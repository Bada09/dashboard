import os
import sys
import time
import glob
import re
import datetime
import subprocess
import threading
import shutil
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

# Forçar stdout UTF-8 no Windows
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

PORT = 8080
DAEMON_DIR = os.path.dirname(os.path.abspath(__file__))
LAST_DUMP_FILE_PATH = os.path.join(DAEMON_DIR, 'last_processed_dump.txt')
LOG_FILE_PATH = os.path.join(DAEMON_DIR, 'daemon.log')
CHECK_INTERVAL_SECONDS = 5

# Estado global do robô
ROBOT_STATE = {
    "status": "iniciando",
    "last_processed_dump": "",
    "last_processed_time": "",
    "latest_available_dump": "",
    "last_error": "",
    "is_updating": False,
    "recent_logs": []
}

def log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {msg}"
    print(entry, flush=True)
    
    # Salvar no buffer de logs em memória (últimos 100)
    ROBOT_STATE["recent_logs"].append(entry)
    if len(ROBOT_STATE["recent_logs"]) > 100:
        ROBOT_STATE["recent_logs"].pop(0)
        
    # Salvar no arquivo daemon.log
    try:
        with open(LOG_FILE_PATH, 'a', encoding='utf-8') as f:
            f.write(entry + '\n')
    except Exception:
        pass

def get_monitored_directories():
    """Retorna a lista de diretórios a serem monitorados pelo robô."""
    dirs = [DAEMON_DIR]
    
    # Pasta Downloads do usuário
    user_home = os.path.expanduser('~')
    downloads = os.path.join(user_home, 'Downloads')
    if os.path.isdir(downloads) and downloads not in dirs:
        dirs.append(downloads)
        
    # Área de Trabalho local e OneDrive
    desktop_local = os.path.join(user_home, 'Desktop')
    if os.path.isdir(desktop_local) and desktop_local not in dirs:
        dirs.append(desktop_local)
        
    desktop_onedrive = os.path.join(user_home, 'OneDrive', 'Desktop')
    if os.path.isdir(desktop_onedrive) and desktop_onedrive not in dirs:
        dirs.append(desktop_onedrive)
        
    return dirs

def parse_dump_date(filename):
    """
    Extrai data e hora do nome do arquivo (ex: 18sept26-23h02, 21sep26-19h53, 10sep26-16h44).
    """
    m = re.search(r'(\d{1,2})([a-zA-Z]{3,4})(\d{2,4})(?:-(\d{1,2})h(\d{2}))?', filename, re.IGNORECASE)
    if m:
        day, month_str, year_str, hour, minute = m.groups()
        months_map = {
            'jan': 1, 'fev': 2, 'feb': 2, 'mar': 3, 'abr': 4, 'apr': 4,
            'mai': 5, 'may': 5, 'jun': 6, 'jul': 7, 'ago': 8, 'aug': 8,
            'set': 9, 'sep': 9, 'sept': 9, 'out': 10, 'oct': 10,
            'nov': 11, 'dez': 12, 'dec': 12
        }
        month = months_map.get(month_str.lower()[:3], 1)
        year = int(year_str)
        if year < 100:
            year += 2000
        h = int(hour) if hour else 0
        mi = int(minute) if minute else 0
        try:
            return datetime.datetime(year, month, int(day), h, mi)
        except Exception:
            return None
    return None

def is_file_ready(filepath):
    """Verifica se o arquivo está completamente baixado/escrito no disco."""
    try:
        # Se for arquivo temporário de download do navegador
        if filepath.endswith(('.crdownload', '.tmp', '.part', '.download')):
            return False
        if not os.path.exists(filepath):
            return False
        size1 = os.path.getsize(filepath)
        if size1 < 1000:  # Muito pequeno para ser um dump válido
            return False
        # Tenta abrir para leitura sem erro
        with open(filepath, 'rb') as f:
            chunk = f.read(1024)
            if not chunk.strip().startswith(b'{'):
                return False
        return True
    except Exception:
        return False

def find_all_dumps():
    """Busca todos os dumps de Fairmont em todos os diretórios monitorados."""
    found = []
    for d in get_monitored_directories():
        if not os.path.isdir(d):
            continue
        # Busca case-insensitive
        try:
            for entry in os.scandir(d):
                if entry.is_file():
                    name_lower = entry.name.lower()
                    if 'dump' in name_lower and 'fairmont' in name_lower and name_lower.endswith('.json'):
                        if is_file_ready(entry.path):
                            found.append(entry.path)
        except Exception as e:
            log(f"Aviso ao escanear pasta {d}: {e}")
            
    return found

def get_latest_dump_info():
    """
    Identifica o dump mais recente com base na data do nome do arquivo
    e data de modificação no disco. Se estiver fora da pasta do projeto, copia para ela.
    """
    all_dumps = find_all_dumps()
    if not all_dumps:
        return None, None
        
    def dump_sort_key(path):
        fn = os.path.basename(path)
        dt = parse_dump_date(fn)
        mtime = os.path.getmtime(path)
        # Se encontrou data no nome, usa como critério primário
        if dt:
            dt_ts = dt.timestamp()
        else:
            dt_ts = mtime
        return (dt_ts, mtime, os.path.getsize(path))
        
    all_dumps.sort(key=dump_sort_key, reverse=True)
    best_path = all_dumps[0]
    best_filename = os.path.basename(best_path)
    
    # Se o melhor dump estiver fora do diretório do projeto, copiar para cá
    dest_path = os.path.join(DAEMON_DIR, best_filename)
    if os.path.abspath(best_path) != os.path.abspath(dest_path):
        try:
            log(f"Novo dump detectado fora da pasta do projeto: {best_path}")
            log(f"Copiando para {dest_path}...")
            shutil.copy2(best_path, dest_path)
            log("Cópia concluída com sucesso!")
            best_path = dest_path
        except Exception as ex:
            log(f"Erro ao copiar dump para a pasta do projeto: {ex}")
            
    return best_path, best_filename

def get_last_processed_dump():
    if os.path.exists(LAST_DUMP_FILE_PATH):
        try:
            with open(LAST_DUMP_FILE_PATH, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception:
            return ""
    return ""

def set_last_processed_dump(dump_name):
    try:
        with open(LAST_DUMP_FILE_PATH, 'w', encoding='utf-8') as f:
            f.write(dump_name)
    except Exception as e:
        log(f"Erro ao salvar last_processed_dump.txt: {e}")

def run_update_script(dump_path=None):
    """Executa update_fairmont.py apontando para o dump especificado."""
    if ROBOT_STATE["is_updating"]:
        log("Aviso: Uma atualização já está em andamento. Aguardando...")
        return False, "Atualização em andamento"

    ROBOT_STATE["is_updating"] = True
    ROBOT_STATE["status"] = "atualizando"
    
    script_path = os.path.join(DAEMON_DIR, 'update_fairmont.py')
    cmd = [sys.executable, script_path]
    if dump_path:
        cmd.append(dump_path)
        dump_name = os.path.basename(dump_path)
    else:
        dump_name = "latest"

    log(f"=== DISPARANDO ATUALIZAÇÃO AUTOMÁTICA DO DASHBOARD ===")
    log(f"Dump selecionado: {dump_name}")
    log(f"Comando: {' '.join(cmd)}")
    
    start_t = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            cwd=DAEMON_DIR,
            timeout=180
        )
        
        elapsed = round(time.time() - start_t, 2)
        if result.returncode == 0:
            log(f"Atualização concluída com sucesso em {elapsed}s!")
            if dump_path:
                set_last_processed_dump(dump_name)
            
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ROBOT_STATE["last_processed_dump"] = dump_name
            ROBOT_STATE["last_processed_time"] = now_str
            ROBOT_STATE["status"] = "ativo"
            ROBOT_STATE["last_error"] = ""
            return True, result.stdout
        else:
            err_msg = result.stderr or result.stdout or f"Exit code {result.returncode}"
            log(f"Erro na execução do script ({elapsed}s)! Código: {result.returncode}")
            log(err_msg)
            ROBOT_STATE["status"] = "erro"
            ROBOT_STATE["last_error"] = err_msg
            return False, err_msg
    except Exception as ex:
        log(f"Exceção ao rodar update_fairmont.py: {ex}")
        ROBOT_STATE["status"] = "erro"
        ROBOT_STATE["last_error"] = str(ex)
        return False, str(ex)
    finally:
        ROBOT_STATE["is_updating"] = False

# ─── Servidor HTTP Local (Porta 8080) ─────────────────────────────────────────

class DashboardHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suprimir logs padrão do BaseHTTPRequestHandler para manter o terminal limpo
        pass

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        path = self.path.split('?')[0]
        
        if path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            
            _, latest_fn = get_latest_dump_info()
            last_p = get_last_processed_dump()
            
            payload = {
                "status": ROBOT_STATE["status"],
                "last_processed_dump": last_p,
                "last_processed_time": ROBOT_STATE["last_processed_time"],
                "latest_available_dump": latest_fn,
                "needs_update": (latest_fn is not None and latest_fn != last_p),
                "is_updating": ROBOT_STATE["is_updating"],
                "last_error": ROBOT_STATE["last_error"],
                "monitored_dirs": get_monitored_directories(),
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.wfile.write(json.dumps(payload, ensure_ascii=False).encode('utf-8'))
            
        elif path == '/update':
            log("Requisição manual de atualização recebida via GET /update")
            latest_path, latest_fn = get_latest_dump_info()
            if not latest_path:
                self.send_response(404)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.end_headers()
                resp = {"status": "error", "message": "Nenhum dump do Fairmont encontrado."}
                self.wfile.write(json.dumps(resp, ensure_ascii=False).encode('utf-8'))
                return
                
            success, output = run_update_script(latest_path)
            if success:
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.end_headers()
                resp = {
                    "status": "success",
                    "message": "Dashboard atualizado com sucesso!",
                    "dump": latest_fn,
                    "time": ROBOT_STATE["last_processed_time"]
                }
                self.wfile.write(json.dumps(resp, ensure_ascii=False).encode('utf-8'))
            else:
                self.send_response(500)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.end_headers()
                resp = {
                    "status": "error",
                    "message": "Erro ao atualizar o dashboard",
                    "detail": output
                }
                self.wfile.write(json.dumps(resp, ensure_ascii=False).encode('utf-8'))
                
        elif path == '/log':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            log_text = "\n".join(ROBOT_STATE["recent_logs"])
            self.wfile.write(log_text.encode('utf-8'))
            
        else:
            self.send_response(404)
            self.end_headers()

def run_http_server():
    try:
        server = HTTPServer(('127.0.0.1', PORT), DashboardHTTPHandler)
        log(f"Servidor HTTP da API do Robô iniciado em http://127.0.0.1:{PORT}")
        server.serve_forever()
    except Exception as e:
        log(f"Erro no servidor HTTP: {e}")

# ─── Loop Principal do Robô Vigilante ────────────────────────────────────────

def watcher_loop():
    log("=" * 65)
    log("ROBÔ DE ATUALIZAÇÃO CONTÍNUA DO FAIRMONT INICIADO")
    log("=" * 65)
    log(f"Intervalo de verificação: a cada {CHECK_INTERVAL_SECONDS} segundos")
    log("Pastas monitoradas:")
    for p in get_monitored_directories():
        log(f"  📁 {p}")
        
    last_processed = get_last_processed_dump()
    ROBOT_STATE["last_processed_dump"] = last_processed
    ROBOT_STATE["status"] = "ativo"
    log(f"Último dump registrado como processado: '{last_processed}'")

    # Primeira verificação imediata na inicialização
    initial_path, initial_fn = get_latest_dump_info()
    if initial_fn:
        ROBOT_STATE["latest_available_dump"] = initial_fn
        log(f"Dump mais recente detectado no sistema: '{initial_fn}'")
        if initial_fn != last_processed:
            log(f"⚡ NOVO DUMP DETECTADO NA INICIALIZAÇÃO: {initial_fn}")
            run_update_script(initial_path)
        else:
            log("O dashboard já está sincronizado com o dump mais recente.")
    else:
        log("Aviso: Nenhum dump do Fairmont encontrado no momento.")

    while True:
        try:
            time.sleep(CHECK_INTERVAL_SECONDS)
            
            # Buscar dump mais recente atualizado
            best_path, best_fn = get_latest_dump_info()
            if not best_fn:
                continue
                
            ROBOT_STATE["latest_available_dump"] = best_fn
            current_processed = get_last_processed_dump()
            
            if best_fn != current_processed:
                log("-" * 65)
                log(f"🔔 NOVO DUMP DETECTADO: {best_fn}")
                log(f"Dump anterior era: {current_processed}")
                log("Iniciando processo automático de atualização...")
                success, _ = run_update_script(best_path)
                if success:
                    log(f"🎉 Dashboard atualizado e publicado no GitHub com sucesso!")
                else:
                    log(f"⚠️ Falha ao processar novo dump {best_fn}. Tentará novamente no próximo ciclo.")
                log("-" * 65)
                
        except Exception as e:
            log(f"Erro no loop do robô: {e}")
            time.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == '__main__':
    # Iniciar thread do servidor HTTP
    http_thread = threading.Thread(target=run_http_server, daemon=True)
    http_thread.start()

    # Executar o loop do vigilante na thread principal
    try:
        watcher_loop()
    except KeyboardInterrupt:
        log("Robô finalizado pelo usuário (Ctrl+C).")
