# start_daemon.ps1
# Script para iniciar, monitorar e registrar o robô autônomo do Fairmont Dashboard

param(
    [switch]$Hidden = $false,
    [switch]$Stop = $false,
    [switch]$Status = $false
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if ($Stop) {
    Write-Host "=== Encerrando Fairmont Dashboard Daemon ===" -ForegroundColor Yellow
    $conns = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue
    if ($conns) {
        foreach ($c in $conns) {
            $proc = Get-Process -Id $c.OwningProcess -ErrorAction SilentlyContinue
            if ($proc) {
                Write-Host "Encerrando PID $($proc.Id) ($($proc.ProcessName))..." -ForegroundColor Yellow
                Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
            }
        }
        Write-Host "Robô encerrado." -ForegroundColor Green
    } else {
        Write-Host "Nenhum processo escutando na porta 8080." -ForegroundColor Gray
    }
    return
}

if ($Status) {
    Write-Host "=== Status do Fairmont Dashboard Daemon ===" -ForegroundColor Cyan
    $conns = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue
    if ($conns) {
        Write-Host "[ONLINE] Robô em execução na porta 8080 (PID: $($conns[0].OwningProcess))" -ForegroundColor Green
        try {
            $res = Invoke-RestMethod -Uri "http://127.0.0.1:8080/status" -TimeoutSec 3
            Write-Host "Último Dump Processado : $($res.last_processed_dump)" -ForegroundColor Cyan
            Write-Host "Horário de Atualização : $($res.last_processed_time)" -ForegroundColor Yellow
            Write-Host "Dump Mais Recente      : $($res.latest_available_dump)" -ForegroundColor Cyan
        } catch {
            Write-Host "Aviso ao consultar endpoint /status: $_" -ForegroundColor Yellow
        }
    } else {
        Write-Host "[OFFLINE] O robô não está ativo." -ForegroundColor Red
    }
    return
}

Write-Host "=== Iniciando Fairmont Dashboard Daemon (Robô de Automação) ===" -ForegroundColor Cyan

# 1. Verifica se já está rodando na porta 8080
$portActive = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue
if ($portActive) {
    Write-Host "Aviso: Já existe um processo escutando na porta 8080 (PID: $($portActive.OwningProcess)). O robô já está ativo." -ForegroundColor Yellow
} else {
    $windowStyle = if ($Hidden) { "Hidden" } else { "Normal" }
    Write-Host "Iniciando dashboard_daemon.py (WindowStyle: $windowStyle)..." -ForegroundColor Green
    Start-Process -FilePath "python" -ArgumentList "dashboard_daemon.py" -WindowStyle $windowStyle -WorkingDirectory $PSScriptRoot
    
    Start-Sleep -Seconds 2
    $check = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue
    if ($check) {
        Write-Host "Robô iniciado com sucesso na porta 8080!" -ForegroundColor Green
    } else {
        Write-Host "Iniciando processo..." -ForegroundColor Gray
    }
}

Write-Host "`nO robô irá:" -ForegroundColor White
Write-Host "1. Monitorar continuamente (a cada 5s) por novos dumps na pasta do projeto, Downloads e Desktop." -ForegroundColor Gray
Write-Host "2. Detectar automaticamente o arquivo mais recente, atualizar o HTML e publicar no GitHub." -ForegroundColor Gray
Write-Host "3. Responder em tempo real aos pedidos do dashboard via API local (127.0.0.1:8080)." -ForegroundColor Gray

# Configuração de Inicializar do Windows
$startupFolder = [System.IO.Path]::Combine($env:APPDATA, "Microsoft\Windows\Start Menu\Programs\Startup")
$shortcutPath = [System.IO.Path]::Combine($startupFolder, "FairmontDashboardDaemon.lnk")

if (-not (Test-Path $shortcutPath)) {
    try {
        $wshell = New-Object -ComObject Wscript.Shell
        $shortcut = $wshell.CreateShortcut($shortcutPath)
        $shortcut.TargetPath = "powershell.exe"
        $shortcut.Arguments = "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$PSScriptRoot\start_daemon.ps1`" -Hidden"
        $shortcut.WorkingDirectory = $PSScriptRoot
        $shortcut.Description = "Inicia o robô de automação do Fairmont Dashboard com o Windows"
        $shortcut.Save()
        Write-Host "`n[Sucesso] Configurado para iniciar automaticamente com o Windows (atalho criado na pasta Inicializar)." -ForegroundColor Green
    } catch {
        Write-Host "Nota sobre inicialização automática com Windows: $_" -ForegroundColor Gray
    }
} else {
    Write-Host "`nO robô já está configurado para iniciar junto com o Windows." -ForegroundColor Green
}

Write-Host "`nProcesso Concluído!" -ForegroundColor Cyan
