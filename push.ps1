# 推送脚本：先试直连，失败自动走本地代理重试
# 用法：双击 push.cmd，或
#       powershell -NoProfile -ExecutionPolicy Bypass -File push.ps1 "提交说明"
#
# 背景：国内直连 github.com 的 git 传输经常被重置。
#       本脚本会自动检测并使用本地代理（默认 127.0.0.1:7897）。

param(
    [string]$Message = ""
)

$ErrorActionPreference = 'Stop'
$Project = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Project

# 本地代理端口（Clash 默认 7897；改成你自己的）
$ProxyPort = 7897
$ProxyUrl  = "http://127.0.0.1:$ProxyPort"

Write-Host "==> 1/3 提交改动" -ForegroundColor Cyan
$status = git status --porcelain
if ($status) {
    if (-not $Message) {
        $Message = "post: 更新文章 $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    }
    git add -A
    git commit -m $Message
    Write-Host "    已提交：$Message"
} else {
    Write-Host "    没有需要提交的改动"
}

Write-Host "==> 2/3 推送" -ForegroundColor Cyan
$env:GIT_TERMINAL_PROMPT = "0"

# 先试直连
Write-Host "    尝试直连..." -NoNewline
$direct = git push 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host " 成功" -ForegroundColor Green
} else {
    Write-Host " 失败，改走代理" -ForegroundColor Yellow

    # 检测代理是否在监听
    $proxyAlive = Test-NetConnection -ComputerName 127.0.0.1 -Port $ProxyPort -InformationLevel Quiet -WarningAction SilentlyContinue
    if (-not $proxyAlive) {
        Write-Host "    代理 $ProxyUrl 未在监听。" -ForegroundColor Red
        Write-Host "    请启动你的代理软件，或把 push.ps1 里的 `$ProxyPort 改成实际端口。" -ForegroundColor Red
        exit 1
    }

    Write-Host "    经 $ProxyUrl 推送..."
    git -c "http.proxy=$ProxyUrl" -c "https.proxy=$ProxyUrl" push 2>&1 | ForEach-Object { "    $_" }
    if ($LASTEXITCODE -ne 0) {
        Write-Host "    推送仍然失败，请检查网络或代理。" -ForegroundColor Red
        exit 1
    }
    Write-Host " 成功" -ForegroundColor Green
}

Write-Host "==> 3/3 完成" -ForegroundColor Cyan
Write-Host "    GitHub Actions 会自动构建部署，约 1-2 分钟后生效"
Write-Host "    查看进度：https://github.com/TANGJIN13/tangjin-blog/actions"
Write-Host "    线上站点：https://tangjin.xyz" -ForegroundColor Green
