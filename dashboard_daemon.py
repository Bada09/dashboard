import os
import sys
import time
import glob
import datetime
import subprocess
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8080
DAEMON_DIR = os.path.dirname(os.path.abspath(__file__))
LAST_DUMP_FILE_PATH = os.path.join(DAEMON_DIR, 'last_processed_dump.txt')

def log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)

def get_latest_dump():
    dumps = glob.glob(os.path.join(DAEMON_DIR, '[dD]ump-[fF]airmont-*.json'))
    if not dumps:
        return None
    # Sort by modification time
    dumps.sort(key=os.path.getmtime, reverse=True)
    return os.path.basename(dumps[0])

def run_update_script(dump_name=None):
    script_path = os.path.join(DAEMON_DIR, 'update_fairmont.py')
    cmd = [sys.executable, script_path]
    if dump_name:
        cmd.append(os.path.join(DAEMON_DIR, dump_name))
    
    log(f"Executando script de atualização: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', cwd=DAEMON_DIR)
    
    if result.returncode == 0:
        log("Atualização concluída com sucesso!")
        if dump_name:
            with open(LAST_DUMP_FILE_PATH, 'w', encoding='utf-8') as f:
                f.write(dump_name)
        return True, result.stdout
    else:
        log(f"Erro na atualização! Código de saída: {result.returncode}")
        log(result.stderr)
        return False, result.stderr

class DashboardHTTPHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path == '/update':
            log("Requisição manual de atualização recebida via GET /update")
            latest = get_latest_dump()
            success, output = run_update_script(latest)
            
            if success:
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.end_headers()
                response = f'{{"status": "success", "message": "Dashboard atualizado com sucesso!", "dump": "{latest}"}}'
                self.wfile.write(response.encode('utf-8'))
            else:
                self.send_response(500)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.end_headers()
                # Clean output to be JSON-safe
                safe_output = output.replace('"', '\\"').replace('\n', '\\n').replace('\r', '')
                response = f'{{"status": "error", "message": "Erro ao atualizar", "detail": "{safe_output}"}}'
                self.wfile.write(response.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    server = HTTPServer(('127.0.0.1', PORT), DashboardHTTPHandler)
    log(f"Servidor HTTP iniciado em http://127.0.0.1:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        log("Servidor HTTP finalizado.")

def scheduler_loop():
    log("Thread de agendamento diário iniciada (Verificação às 18:00h).")
    last_run_date = ""
    
    while True:
        try:
            now = datetime.datetime.now()
            # Verifica se é 18:00h e ainda não rodou hoje
            if now.hour == 18 and now.strftime("%Y-%m-%d") != last_run_date:
                log("Horário de verificação atingido (18:00). Verificando novos dumps...")
                latest = get_latest_dump()
                
                if latest:
                    # Ler o último dump processado
                    last_processed = ""
                    if os.path.exists(LAST_DUMP_FILE_PATH):
                        with open(LAST_DUMP_FILE_PATH, 'r', encoding='utf-8') as f:
                            last_processed = f.read().strip()
                    
                    if latest != last_processed:
                        log(f"Novo dump encontrado: {latest}. Iniciando atualização...")
                        success, _ = run_update_script(latest)
                        if success:
                            last_run_date = now.strftime("%Y-%m-%d")
                    else:
                        log(f"Sem dumps novos. O último dump '{latest}' já foi processado.")
                        last_run_date = now.strftime("%Y-%m-%d")
                else:
                    log("Nenhum dump encontrado no diretório.")
                    last_run_date = now.strftime("%Y-%m-%d")
            
            # Dorme por 30 segundos
            time.sleep(30)
        except Exception as e:
            log(f"Erro no loop do agendador: {e}")
            time.sleep(10)

if __name__ == '__main__':
    # Criar arquivo de registro inicial se não existir
    initial_dump = get_latest_dump()
    if initial_dump and not os.path.exists(LAST_DUMP_FILE_PATH):
        with open(LAST_DUMP_FILE_PATH, 'w', encoding='utf-8') as f:
            f.write(initial_dump)
        log(f"Registrado dump inicial como já processado: {initial_dump}")

    # Iniciar thread do agendador
    t = threading.Thread(target=scheduler_loop, daemon=True)
    t.start()

    # Iniciar servidor HTTP no thread principal
    run_server()
