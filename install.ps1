# skills-summarize-audit installer — 手动安装，见 README.md

$ErrorActionPreference = "Stop"

$RepoSSH   = "git@github.com:gtbwpkwjnb-alt/skills-summarize-audit-skill.git"
$RepoHTTPS = "https://github.com/gtbwpkwjnb-alt/skills-summarize-audit-skill.git"

function Get-InstallDir {
    if (Test-Path "$env:USERPROFILE\.zcode\skills") {
        return "$env:USERPROFILE\.zcode\skills\skills-summarize-audit"
    }
    if (Test-Path "$env:USERPROFILE\.claude\skills") {
        return "$env:USERPROFILE\.claude\skills\skills-summarize-audit"
    }
    if (Test-Path "$env:USERPROFILE\.codex\skills") {
        return "$env:USERPROFILE\.codex\skills\skills-summarize-audit"
    }
    if (Test-Path "$env:USERPROFILE\.cursor\agent-skills") {
        return "$env:USERPROFILE\.cursor\agent-skills\skills-summarize-audit"
    }
    return "$env:USERPROFILE\.agent-skills\skills-summarize-audit"
}

$InstallDir = Get-InstallDir

Write-Host "📦 skills-summarize-audit installer"
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
Write-Host "✅ skills-summarize-audit installed!  v$ver"
Write-Host "   Trigger: skills-summarize-audit / 技能审查 / 技能总结"
Write-Host "   Issues:  https://github.com/gtbwpkwjnb-alt/skills-summarize-audit-skill/issues"
