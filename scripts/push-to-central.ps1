#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Push improved scripts from current repo to mcp-central-docs
    
.DESCRIPTION
    Copies improved/updated scripts from the current repository back to the
    central documentation repository (mcp-central-docs), making them the new
    standard for all repos.
    
    This is the REVERSE of propagate-backup-script.ps1 which pushes FROM
    central TO individual repos.
    
.PARAMETER ScriptName
    Name of the script to push (e.g., "backup-repo.ps1")
    
.PARAMETER WhatIf
    Preview what would be copied without actually copying
    
.EXAMPLE
    .\scripts\push-to-central.ps1 -ScriptName "backup-repo.ps1"
    # Copies backup-repo.ps1 to mcp-central-docs
    
.EXAMPLE
    .\scripts\push-to-central.ps1 -ScriptName "backup-repo.ps1" -WhatIf
    # Preview what would be copied
#>

[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory = $true)]
    [string]$ScriptName,
    
    [switch]$Force = $false
)

$WhatIf = $WhatIfPreference

Write-Host "`nâ•"â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•-" -ForegroundColor Cyan
Write-Host "â•'     ðŸ"¤ Push Script to Central Docs Repository ðŸ"¤       â•'" -ForegroundColor Cyan
Write-Host "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•`n" -ForegroundColor Cyan

# Paths
$centralRepo = "D:\Dev\repos\mcp-central-docs"
$centralScriptsDir = Join-Path $centralRepo "scripts"
$currentRepo = Get-Location
$currentRepoName = (Get-Item $currentRepo).Name
$sourceScript = Join-Path $currentRepo "scripts" $ScriptName
$destScript = Join-Path $centralScriptsDir $ScriptName

# Validate source exists
if (-not (Test-Path $sourceScript)) {
    Write-Host "âŒ Error: Script not found: $sourceScript" -ForegroundColor Red
    exit 1
}

# Validate central repo exists
if (-not (Test-Path $centralRepo)) {
    Write-Host "âŒ Error: Central docs repo not found: $centralRepo" -ForegroundColor Red
    exit 1
}

Write-Host "ðŸ"‹ Push Configuration:" -ForegroundColor Cyan
Write-Host "  Source repo:   $currentRepoName" -ForegroundColor White
Write-Host "  Script:        $ScriptName" -ForegroundColor White
Write-Host "  Source:        $sourceScript" -ForegroundColor Gray
Write-Host "  Destination:   $destScript" -ForegroundColor Gray
Write-Host ""

# Check if destination exists
$destExists = Test-Path $destScript
if ($destExists) {
    Write-Host "âš ï¸  Destination file already exists" -ForegroundColor Yellow
    
    # Compare files
    $sourceHash = (Get-FileHash $sourceScript -Algorithm SHA256).Hash
    $destHash = (Get-FileHash $destScript -Algorithm SHA256).Hash
    
    if ($sourceHash -eq $destHash) {
        Write-Host "âœ... Files are identical - no update needed" -ForegroundColor Green
        exit 0
    }
    
    Write-Host "ðŸ"Š File comparison:" -ForegroundColor Cyan
    $sourceSize = (Get-Item $sourceScript).Length
    $destSize = (Get-Item $destScript).Length
    $sourceModified = (Get-Item $sourceScript).LastWriteTime
    $destModified = (Get-Item $destScript).LastWriteTime
    
    Write-Host "  Source:        $([math]::Round($sourceSize/1KB, 2)) KB (modified: $($sourceModified.ToString('yyyy-MM-dd HH:mm:ss')))" -ForegroundColor White
    Write-Host "  Destination:   $([math]::Round($destSize/1KB, 2)) KB (modified: $($destModified.ToString('yyyy-MM-dd HH:mm:ss')))" -ForegroundColor White
    Write-Host ""
    
    if (-not $Force -and -not $WhatIf) {
        $response = Read-Host "Overwrite central repo version? (y/N)"
        if ($response -ne 'y' -and $response -ne 'Y') {
            Write-Host "âŒ Cancelled by user" -ForegroundColor Yellow
            exit 0
        }
    }
}

# Perform copy
if ($WhatIf) {
    Write-Host "`nâš ï¸  DRY-RUN MODE: No files will be copied`n" -ForegroundColor Yellow
    Write-Host "Would copy:" -ForegroundColor Cyan
    Write-Host "  FROM: $sourceScript" -ForegroundColor White
    Write-Host "  TO:   $destScript" -ForegroundColor White
    Write-Host "`nâœ... Dry-run complete - no files copied`n" -ForegroundColor Green
    exit 0
}

try {
    Copy-Item -Path $sourceScript -Destination $destScript -Force
    Write-Host "âœ... Successfully copied to central repo!" -ForegroundColor Green
    
    # Show next steps
    Write-Host "`nðŸ"‹ Next steps:" -ForegroundColor Cyan
    Write-Host "  1. cd $centralRepo" -ForegroundColor Gray
    Write-Host "  2. git status" -ForegroundColor Gray
    Write-Host "  3. git add scripts/$ScriptName" -ForegroundColor Gray
    Write-Host "  4. git commit -m `"Update $ScriptName from $currentRepoName`"" -ForegroundColor Gray
    Write-Host "  5. Run propagate-backup-script.ps1 to push to other repos" -ForegroundColor Gray
    Write-Host ""
    
}
catch {
    Write-Host "âŒ Error copying file: $_" -ForegroundColor Red
    exit 1
}

Write-Host "âœ... Done!`n" -ForegroundColor Green
