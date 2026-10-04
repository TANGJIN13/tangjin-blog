@echo off
REM 一键推送 —— 双击本文件即可
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0push.ps1" %*
echo.
echo 按任意键关闭窗口...
pause >nul
endlocal
