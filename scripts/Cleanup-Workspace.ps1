param(
    [switch]$Delete,
    [switch]$Force
)

Write-Host "Workspace cleanup - UnityCatalog-ChatBot" -ForegroundColor Cyan
Write-Host "Mode: " -NoNewline; if($Delete){ Write-Host "DELETE" -ForegroundColor Red } else { Write-Host "DRY-RUN" -ForegroundColor Yellow }

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
Push-Location $Root

$patterns = @(
    # Python caches and temp
    "**/__pycache__/*",
    "**/.pytest_cache/*",
    "**/.ipynb_checkpoints/*",
    
    # Virtual environments
    ".venv/*",
    "venv/*",
    "env/*",

    # Coverage and reports
    ".coverage",
    "htmlcov/*",

    # Node outputs if any
    "node_modules/*",

    # Logs
    "*.log"
)

function Get-Matches([string]$pattern){
    try { Get-ChildItem -Path $pattern -Recurse -Force -ErrorAction SilentlyContinue } catch { @() }
}

$toRemove = New-Object System.Collections.Generic.List[System.IO.FileSystemInfo]
foreach($p in $patterns){ foreach($item in (Get-Matches $p)){ if($item){ $toRemove.Add($item) } } }

if($toRemove.Count -eq 0){ Write-Host "No matching files found for cleanup patterns." -ForegroundColor Green; Pop-Location; return }

Write-Host ("Found {0} items:" -f $toRemove.Count) -ForegroundColor Yellow
foreach($i in $toRemove){ Write-Host " - " $i.FullName }

if(-not $Delete){ Write-Host "Dry-run complete. Rerun with -Delete to remove these items." -ForegroundColor Yellow; Pop-Location; return }

Write-Host "Deleting files..." -ForegroundColor Red
foreach($i in $toRemove){
    try {
        if($i.PSIsContainer){ Remove-Item -LiteralPath $i.FullName -Recurse -Force:$Force -ErrorAction Stop }
        else { Remove-Item -LiteralPath $i.FullName -Force:$Force -ErrorAction Stop }
    } catch { Write-Host ("Failed to delete: {0} -> {1}" -f $i.FullName, $_.Exception.Message) -ForegroundColor DarkRed }
}

Write-Host "Cleanup complete." -ForegroundColor Green
Pop-Location
