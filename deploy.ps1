# 部署脚本：本地构建 -> scp 推送到服务器 Nginx 站点目录
# 用法：在项目根目录执行  pwsh -File deploy.ps1
# 依赖：本机已配好 ssh 别名 tangjin（见 ~/.ssh/config）

$ErrorActionPreference = 'Stop'
$Project = Split-Path -Parent $MyInvocation.MyCommand.Path
$Dist = Join-Path $Project 'dist'
$RemoteDir = '/var/www/blog'

Write-Host "==> 1/3 构建" -ForegroundColor Cyan
Push-Location $Project
pnpm build
if ($LASTEXITCODE -ne 0) { throw "构建失败" }
Pop-Location

Write-Host "==> 2/3 同步到服务器 $RemoteDir" -ForegroundColor Cyan
# 先清空远程目录再上传，保证无残留
ssh -T tangjin "sudo rm -rf $RemoteDir && sudo mkdir -p $RemoteDir && sudo chown -R ubuntu:www-data $RemoteDir"
if ($LASTEXITCODE -ne 0) { throw "远程目录准备失败" }

# scp 递归上传 dist 内容
scp -r "$Dist\*" "tangjin:$RemoteDir/"
if ($LASTEXITCODE -ne 0) { throw "scp 上传失败" }

Write-Host "==> 3/3 修正权限并重载 nginx" -ForegroundColor Cyan
ssh -T tangjin "sudo chown -R www-data:www-data $RemoteDir && sudo find $RemoteDir -type d -exec chmod 755 {} + && sudo find $RemoteDir -type f -exec chmod 644 {} + && sudo nginx -t && sudo systemctl reload nginx"
if ($LASTEXITCODE -ne 0) { throw "nginx 重载失败" }

Write-Host "==> 完成。站点已部署。" -ForegroundColor Green
