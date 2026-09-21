@echo off
title Status do Robo Fairmont
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_daemon.ps1" -Status
echo.
pause
