# 推送脚本：自动提交 -> 拉取远程 -> 推送（网络不通时自动走本地代理）
# 用法：双击 push.cmd，或
#       powershell -NoProfile -ExecutionPolicy Bypass -File push.ps1 "提交说明"
#
# 为什么要自动 pull：
#   你在 /admin/ 后台发的文章会直接提交到 GitHub，
#   本地如果不同步就推送会被拒绝（non-fast-forward）。

param(
    [string]$Message = ""
)

$Project = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Project

# 本地代理端口（Clash 默认 7897；改成你自己的）
$ProxyPort = 7897
$ProxyUrl  = "http://127.0.0.1:$ProxyPort"

# 关键：不能让 PowerShell 把 git 的 stderr 当终止错误，否则重试逻辑不会执行
function Invoke-Git {
    param([string[]]$GitArgs)
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $output = & git @GitArgs 2>&1 | Out-String
    $code = $LASTEXITCODE
    $ErrorActionPreference = $prev
    return @{ Output = $output; Code = $code }
}

# ---------- 1. 决定走不走代理 ----------
Write-Host "==> 1/4 检测网络" -ForegroundColor Cyan
$netArgs = @()
$probe = Invoke-Git @('ls-remote', '--exit-code', 'origin', 'HEAD')
if ($probe.Code -eq 0) {
    Write-Host "    直连 GitHub 可用" -ForegroundColor Green
} else {
    $proxyAlive = Test-NetConnection -ComputerName 127.0.0.1 -Port $ProxyPort -InformationLevel Quiet -WarningAction SilentlyContinue
    if (-not $proxyAlive) {
        Write-Host "    直连失败，且本地代理 $ProxyUrl 未在监听" -ForegroundColor Red
        Write-Host "    请启动代理软件，或修改本脚本里的 ProxyPort" -ForegroundColor Red
        exit 1
    }
    $netArgs = @('-c', "http.proxy=$ProxyUrl", '-c', "https.proxy=$ProxyUrl")
    Write-Host "    直连失败，改用代理 $ProxyUrl" -ForegroundColor Yellow
}

# ---------- 2. 提交本地改动 ----------
Write-Host "==> 2/4 提交本地改动" -ForegroundColor Cyan
$status = (& git status --porcelain 2>&1 | Out-String).Trim()
if ($status) {
    if (-not $Message) {
        $Message = "post: 更新文章 $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    }
    & git add -A 2>&1 | Out-Null
    & git commit -m $Message 2>&1 | Out-Null
    Write-Host "    已提交：$Message"
} else {
    Write-Host "    没有需要提交的改动"
}

# ---------- 3. 拉取远程 ----------
Write-Host "==> 3/4 拉取远程改动" -ForegroundColor Cyan
$pull = Invoke-Git ($netArgs + @('pull', '--rebase', '--autostash', 'origin', 'main'))
if ($pull.Code -eq 0) {
    Write-Host "    已同步"
} else {
    Write-Host "    拉取失败（可能有冲突），输出如下：" -ForegroundColor Yellow
    Write-Host $pull.Output
    Write-Host "    请手动处理后重试" -ForegroundColor Red
    exit 1
}

# ---------- 4. 推送 ----------
Write-Host "==> 4/4 推送到 GitHub" -ForegroundColor Cyan
$push = Invoke-Git ($netArgs + @('push'))
if ($push.Code -ne 0) {
    Write-Host "    推送失败：" -ForegroundColor Red
    Write-Host $push.Output
    exit 1
}
Write-Host "    推送成功" -ForegroundColor Green

Write-Host ""
Write-Host "Actions 会自动构建部署，约 1-2 分钟后生效" -ForegroundColor Cyan
Write-Host "  进度：https://github.com/TANGJIN13/tangjin-blog/actions"
Write-Host "  站点：https://tangjin.xyz" -ForegroundColor Green
