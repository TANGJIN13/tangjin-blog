# 本地部署脚本：构建 -> 推送到服务器
# 用法：pwsh -File deploy.ps1
# 依赖：本机已配好 ssh 别名 tangjin（见 ~/.ssh/config）
#
# 说明：服务器上 /var/www/blog 归属 ubuntu:www-data，
#       直接以 ubuntu 身份写入即可，无需 sudo。

$ErrorActionPreference = 'Stop'
$Project   = Split-Path -Parent $MyInvocation.MyCommand.Path
$Dist      = Join-Path $Project 'dist'
$RemoteDir = '/var/www/blog'

Write-Host "==> 1/3 构建" -ForegroundColor Cyan
Push-Location $Project
pnpm build
if ($LASTEXITCODE -ne 0) { Pop-Location; throw "构建失败" }
Pop-Location

if (-not (Test-Path (Join-Path $Dist 'index.html'))) {
    throw "构建产物缺少 index.html"
}

Write-Host "==> 2/3 同步到服务器 $RemoteDir" -ForegroundColor Cyan
ssh -T tangjin "rm -rf $RemoteDir/*"
if ($LASTEXITCODE -ne 0) { throw "清空远程目录失败" }

scp -r "$Dist\*" "tangjin:$RemoteDir/"
if ($LASTEXITCODE -ne 0) { throw "上传失败" }

Write-Host "==> 3/3 验证" -ForegroundColor Cyan
$code = (ssh -T tangjin "curl -s -o /dev/null -w '%{http_code}' -H 'Host: tangjin.xyz' http://127.0.0.1/ --max-time 10" | Out-String).Trim()
Write-Host "    服务器本地探测 HTTP $code"

if ($code -eq '200') {
    Write-Host "==> 完成，站点已更新：https://tangjin.xyz" -ForegroundColor Green
} else {
    Write-Host "==> 上传完成，但探测返回 $code，请手动检查" -ForegroundColor Yellow
}
