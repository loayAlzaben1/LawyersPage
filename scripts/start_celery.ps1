param(
    [string]$BrokerUrl = 'memory://',
    [string]$VenvActivate = '.\.venv\Scripts\Activate.ps1'
)

# Ensure logs directory exists
$logDir = Join-Path $PSScriptRoot '..\logs' | Resolve-Path -ErrorAction SilentlyContinue
if (-not $logDir) {
    New-Item -ItemType Directory -Path (Join-Path $PSScriptRoot '..\logs') | Out-Null
    $logDir = (Join-Path $PSScriptRoot '..\logs')
} else {
    $logDir = $logDir.Path
}

$outLog = Join-Path $logDir 'celery.out.log'
$errLog = Join-Path $logDir 'celery.err.log'
$pidFile = Join-Path $logDir 'celery.pid'

Write-Host "Starting Celery worker (broker=$BrokerUrl). Logs: $outLog"

# Load environment variables from .env if present
$envFile = Join-Path $PSScriptRoot '..\.env'
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -and -not ($_.Trim().StartsWith('#'))) {
            $parts = $_ -split '='
            if ($parts.Count -ge 2) {
                $name = $parts[0].Trim()
                $value = ($parts[1..($parts.Count-1)] -join '=').Trim()
                Set-Item -Path Env:\$name -Value $value
            }
        }
    }
}

Set-Item -Path Env:CELERY_BROKER_URL -Value $BrokerUrl

# Activate venv (for interactive shells)
if (Test-Path (Join-Path $PSScriptRoot $VenvActivate)) {
    try { & $VenvActivate } catch { }
}

# Start celery as background process with redirected logs
$celeryExe = Join-Path $PSScriptRoot '..\.venv\Scripts\celery.exe'
if (-not (Test-Path $celeryExe)) { $celeryExe = 'celery' }

$args = '-A', 'lawyer_site', 'worker', '--loglevel=info', '--pool=solo'

$startInfo = Start-Process -FilePath $celeryExe -ArgumentList $args -RedirectStandardOutput $outLog -RedirectStandardError $errLog -PassThru -WindowStyle Hidden

if ($startInfo) {
    $startInfo.Id | Out-File -FilePath $pidFile -Encoding ascii
    Write-Host "Celery started (PID=$($startInfo.Id))."
} else {
    Write-Host "Failed to start Celery. Check $errLog"
}
