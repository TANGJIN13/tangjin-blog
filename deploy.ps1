$ErrorActionPreference = 'Stop'
$Project   = Split-Path -Parent $MyInvocation.MyCommand.Path
$Dist      = Join-Path $Project 'dist'
$RemoteDir = '/var/www/blog'

Write-Host "==> 1/4 Build" -ForegroundColor Cyan
Push-Location $Project
pnpm build
if ($LASTEXITCODE -ne 0) { Pop-Location; throw "Build failed" }
Pop-Location

if (-not (Test-Path (Join-Path $Dist 'index.html'))) { throw "Missing index.html" }

Write-Host "==> 2/4 Sync to $RemoteDir" -ForegroundColor Cyan
ssh -T tangjin "sudo rm -rf $RemoteDir/* $RemoteDir/.* 2>/dev/null; sudo mkdir -p $RemoteDir; sudo chown -R ubuntu:www-data $RemoteDir; echo ready"
scp -r "$Dist\*" "tangjin:$RemoteDir/"
ssh -T tangjin "sudo chown -R www-data:www-data $RemoteDir; echo done"

Write-Host "==> 3/4 Verify" -ForegroundColor Cyan
$code = (ssh -T tangjin "curl -s -o /dev/null -w '%{http_code}' -H 'Host: tangjin.xyz' http://127.0.0.1/ --max-time 10" | Out-String).Trim()
Write-Host "  Server HTTP $code"

if ($code -eq '200') {
    Write-Host "==> Done: https://tangjin.xyz" -ForegroundColor Green
} else {
    Write-Host "==> Uploaded but HTTP $code, check manually" -ForegroundColor Yellow
}
