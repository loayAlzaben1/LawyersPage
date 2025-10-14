param(
    [string]$LogDir = '..\logs'
)
$outLog = Join-Path $PSScriptRoot $LogDir | Resolve-Path -ErrorAction SilentlyContinue
if (-not $outLog) { Write-Host "No logs directory found"; exit }
$outLog = Join-Path $outLog.Path 'celery.out.log'
if (-not (Test-Path $outLog)) { Write-Host "Log file not found: $outLog"; exit }

Get-Content -Path $outLog -Wait -Tail 200
