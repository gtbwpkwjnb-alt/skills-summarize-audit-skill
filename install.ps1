# skills-audit installer — iwr https://raw.githubusercontent.com/gtbwpkwjnb-alt/skills-audit-skill/main/install.ps1 | iex

$ErrorActionPreference = "Stop"

$RepoSSH   = "git@github.com:gtbwpkwjnb-alt/skills-audit-skill.git"
$RepoHTTPS = "https://github.com/gtbwpkwjnb-alt/skills-audit-skill.git"

function Get-InstallDir {
    if (Test-Path "$env:USERPROFILE\.zcode\skills") {
        return "$env:USERPROFILE\.zcode\skills\skills-audit"
    }
    if (Test-Path "$env:USERPROFILE\.claude\skills") {
        return "$env:USERPROFILE\.claude\skills\skills-audit"
    }
    if (Test-Path "$env:USERPROFILE\.codex\skills") {
        return "$env:USERPROFILE\.codex\skills\skills-audit"
    }
    if (Test-Path "$env:USERPROFILE\.cursor\agent-skills") {
        return "$env:USERPROFILE\.cursor\agent-skills\skills-audit"
    }
    return "$env:USERPROFILE\.agent-skills\skills-audit"
}

$InstallDir = Get-InstallDir

Write-Host "📦 skills-audit installer"
Write-Host "   Target: $InstallDir"

if (Test-Path $InstallDir) {
    Write-Host "   Already installed. Updating..."
    Push-Location $InstallDir
    try { git pull --rebase 2>$null }
    catch {
        Pop-Location
        Remove-Item -Recurse -Force $InstallDir -ErrorAction SilentlyContinue
        try { git clone $RepoSSH $InstallDir } catch { git clone $RepoHTTPS $InstallDir }
    }
    Pop-Location
} else {
    Write-Host "   Cloning..."
    New-Item -ItemType Directory -Force -Path (Split-Path $InstallDir) | Out-Null
    try { git clone $RepoSSH $InstallDir } catch { git clone $RepoHTTPS $InstallDir }
}

$ver = Get-Content "$InstallDir\VERSION" -Raw
Write-Host ""
Write-Host "✅ skills-audit installed!  v$ver"
Write-Host "   Trigger: skills-audit / 技能审查 / 审查技能"
Write-Host "   Issues:  https://github.com/gtbwpkwjnb-alt/skills-audit-skill/issues"