@echo off
title Iniciar Robo Fairmont
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_daemon.ps1"
if %ERRORLEVEL% NEQ 0 pause
