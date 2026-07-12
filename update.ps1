# Auto-update from GitHub (no git client required).
# Never blocks startup: any failure simply starts the currently installed version.
$ErrorActionPreference = 'Stop'
$repo    = 'chunhuan-lu/advance-pdf-report-local'
$branch  = 'master'
$root    = $PSScriptRoot
$shaFile = Join-Path $root '.app_version'

try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 } catch {}

$remote = $null
try {
    $r = Invoke-RestMethod -Uri "https://api.github.com/repos/$repo/commits/$branch" `
        -TimeoutSec 10 -Headers @{ 'User-Agent' = 'advance-report-launcher' }
    $remote = $r.sha
} catch {
    Write-Host '[update] Cannot reach GitHub - starting the current version.'
    exit 0
}

$local = ''
if (Test-Path $shaFile) { $local = (Get-Content $shaFile -Raw).Trim() }
if ($remote -and ($local -eq $remote)) {
    Write-Host '[update] Already up to date.'
    exit 0
}

Write-Host '[update] New version available - downloading ...'
$zip = Join-Path $env:TEMP 'advance_report_update.zip'
$tmp = Join-Path $env:TEMP 'advance_report_update'
try {
    Invoke-WebRequest -Uri "https://github.com/$repo/archive/refs/heads/$branch.zip" `
        -OutFile $zip -TimeoutSec 180
    if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
    Expand-Archive -Path $zip -DestinationPath $tmp -Force
    $src = (Get-ChildItem $tmp -Directory | Select-Object -First 1).FullName

    # start.bat is executing right now and must not be overwritten in place:
    # stage it as start.bat.new; the launcher swaps and relaunches itself.
    $oldBat = Join-Path $root 'start.bat'
    $newBat = Join-Path $src 'start.bat'
    if ((Test-Path $newBat) -and (Test-Path $oldBat)) {
        if ((Get-FileHash $newBat).Hash -ne (Get-FileHash $oldBat).Hash) {
            Copy-Item $newBat (Join-Path $root 'start.bat.new') -Force
        }
    }

    # Copy everything else over; keep runtime data, the venv and local templates untouched.
    robocopy $src $root /E /XD .venv local_store data .git /XF start.bat /NFL /NDL /NJH /NJS /NP | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "robocopy failed with code $LASTEXITCODE" }

    Set-Content -Path $shaFile -Value $remote -Encoding Ascii
    Write-Host '[update] Updated to the latest version.'
} catch {
    Write-Host ('[update] Update failed (' + $_.Exception.Message + ') - starting the current version.')
} finally {
    Remove-Item $zip -Force -ErrorAction SilentlyContinue
    Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue
}
exit 0
