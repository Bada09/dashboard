# update_fairmont_data.ps1
# Executa a atualizacao completa do fairmont.html e users_data.js e publica no GitHub

param(
    [string]$DumpFile = "",
    [string]$HtmlFile = "fairmont.html"
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== Atualizando Fairmont Dashboard e Publicando no GitHub ===" -ForegroundColor Cyan

# Executar script python que atualiza os dados e faz git add / commit / push automaticamente
if ($DumpFile -and (Test-Path $DumpFile)) {
    python update_fairmont.py "$DumpFile"
} else {
    python update_fairmont.py
}

Write-Host "`nProcesso concluido com sucesso!" -ForegroundColor Green
Write-Host "Link Online: https://bada09.github.io/dashboard/fairmont.html" -ForegroundColor Yellow
