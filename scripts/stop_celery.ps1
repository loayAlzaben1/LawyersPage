# Stop a running Celery worker started by start_celery.ps1
$logDir = Join-Path $PSScriptRoot '..\logs'
$pidFile = Join-Path $logDir 'celery.pid'
if (Test-Path $pidFile) {
    $pid = Get-Content $pidFile | Select-Object -First 1
    if ($pid) {
        try {
            Stop-Process -Id $pid -Force -ErrorAction Stop
            Remove-Item $pidFile -ErrorAction SilentlyContinue
            Write-Host "Stopped Celery (PID=$pid)"
        } catch {
            Write-Host "Failed to stop process $pid: $_"
        }
    } else {
        Write-Host "PID file empty"
    }
} else {
    Write-Host "PID file not found at $pidFile"
}
