# start_daemon.ps1
# Script para iniciar o dashboard_daemon.py em segundo plano
# E opcionalmente registrar para iniciar junto com o Windows.

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== Iniciando Fairmont Dashboard Daemon (Robô de Automação) ===" -ForegroundColor Cyan

# 1. Verifica se já está rodando na porta 8080
$portActive = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue
if ($portActive) {
    Write-Host "Aviso: Já existe um processo escutando na porta 8080. O daemon já pode estar rodando." -ForegroundColor Yellow
} else {
    # 2. Inicia o processo python de forma invisível/segundo plano
    Write-Host "Iniciando dashboard_daemon.py em segundo plano..." -ForegroundColor Green
    Start-Process -FilePath "python" -ArgumentList "dashboard_daemon.py" -WindowStyle Hidden -WorkingDirectory $PSScriptRoot
    Write-Host "Daemon iniciado com sucesso!" -ForegroundColor Green
}

Write-Host "`nO daemon irá:" -ForegroundColor White
Write-Host "1. Ficar ativo na porta 8080 para responder aos cliques no botão do HTML." -ForegroundColor Gray
Write-Host "2. Verificar novos dumps automaticamente todos os dias às 18:00h." -ForegroundColor Gray

# Instruções para adicionar ao Inicializar do Windows
$startupFolder = [System.IO.Path]::Combine($env:APPDATA, "Microsoft\Windows\Start Menu\Programs\Startup")
$shortcutPath = [System.IO.Path]::Combine($startupFolder, "FairmontDashboardDaemon.lnk")

if (-not (Test-Path $shortcutPath)) {
    Write-Host "`nDeseja que este robô inicie automaticamente junto com o Windows? (S/N):" -ForegroundColor Cyan
    # Vamos apenas sugerir como fazer para não bloquear caso rode em ambiente automático,
    # mas se o script for executado interativamente podemos criar o atalho.
    Write-Host "Para iniciar com o Windows automaticamente, crie um atalho deste script na pasta de Inicializar do Windows:" -ForegroundColor Yellow
    Write-Host "Pasta: $startupFolder" -ForegroundColor Yellow
    
    # Criar atalho opcional
    try {
        $wshell = New-Object -ComObject Wscript.Shell
        $shortcut = $wshell.CreateShortcut($shortcutPath)
        $shortcut.TargetPath = "powershell.exe"
        $shortcut.Arguments = "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$PSScriptRoot\start_daemon.ps1`""
        $shortcut.WorkingDirectory = $PSScriptRoot
        $shortcut.Description = "Inicia o robô de automação do Fairmont Dashboard"
        $shortcut.Save()
        Write-Host "`n[Sucesso] Configurado para iniciar automaticamente com o Windows (atalho criado na pasta de Inicialização)." -ForegroundColor Green
    } catch {
        Write-Host "Não foi possível criar o atalho de inicialização automática: $_" -ForegroundColor Red
    }
} else {
    Write-Host "`nO robô já está configurado para iniciar junto com o Windows." -ForegroundColor Green
}

Write-Host "`nProcesso Concluído!" -ForegroundColor Cyan
