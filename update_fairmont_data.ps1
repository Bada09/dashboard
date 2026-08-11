# update_fairmont_data.ps1
# Executa a atualizacao completa do fairmont.html e users_data.js com o dump mais recente

param(
    [string]$DumpFile = "dump-Fairmont-10aug26-10h28.json",
    [string]$HtmlFile = "fairmont.html"
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=== Atualizando Fairmont Dashboard com dump: $DumpFile ===" -ForegroundColor Cyan

# Executar script python para garantir 100% de integridade de encoding UTF-8 e escape de JSON
python update_fairmont.py

Write-Host "`nProcesso concluido com sucesso!" -ForegroundColor Green
