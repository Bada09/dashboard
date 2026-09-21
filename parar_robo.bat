@echo off
title Parar Robo Fairmont
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_daemon.ps1" -Stop
timeout /t 3
