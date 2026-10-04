@echo off
REM 一键部署 —— 双击本文件即可
REM 内部用 -ExecutionPolicy Bypass 绕过脚本签名限制

setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0deploy.ps1" %*
echo.
echo 按任意键关闭窗口...
pause >nul
endlocal
