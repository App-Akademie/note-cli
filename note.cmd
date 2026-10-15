@echo off
setlocal DisableDelayedExpansion
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "%~dp0note.ps1" %*
exit /b %errorlevel%
