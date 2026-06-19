#!/bin/bash
# skills-audit installer — curl -sL https://raw.githubusercontent.com/gtbwpkwjnb-alt/skills-audit-skill/main/install.sh | bash

set -e

REPO_SSH="git@github.com:gtbwpkwjnb-alt/skills-audit-skill.git"
REPO_HTTPS="https://github.com/gtbwpkwjnb-alt/skills-audit-skill.git"

detect_platform() {
    if [ -d "$HOME/.zcode/skills" ] || [ -n "$ZCODE_CLI_VERSION" ]; then
        echo "$HOME/.zcode/skills/skills-audit"
        return
    fi
    if [ -d "$HOME/.claude/skills" ]; then
        echo "$HOME/.claude/skills/skills-audit"
        return
    fi
    if [ -d "$HOME/.codex/skills" ]; then
        echo "$HOME/.codex/skills/skills-audit"
        return
    fi
    if [ -d "$HOME/.cursor/agent-skills" ]; then
        echo "$HOME/.cursor/agent-skills/skills-audit"
        return
    fi
    echo "$HOME/.agent-skills/skills-audit"
}

INSTALL_DIR=$(detect_platform)

echo "📦 skills-audit installer"
echo "   Target: $INSTALL_DIR"

if [ -d "$INSTALL_DIR" ]; then
    echo "   Already installed. Updating..."
    cd "$INSTALL_DIR"
    git pull --rebase 2>/dev/null || { cd "$HOME" && rm -rf "$INSTALL_DIR" && git clone "$REPO_SSH" "$INSTALL_DIR" 2>/dev/null || git clone "$REPO_HTTPS" "$INSTALL_DIR"; }
else
    echo "   Cloning..."
    mkdir -p "$(dirname "$INSTALL_DIR")"
    git clone "$REPO_SSH" "$INSTALL_DIR" 2>/dev/null || git clone "$REPO_HTTPS" "$INSTALL_DIR"
fi

echo ""
echo "✅ skills-audit installed!  v$(cat "$INSTALL_DIR/VERSION")"
echo "   Trigger: skills-audit / 技能审查 / 审查技能"
echo "   Issues:  https://github.com/gtbwpkwjnb-alt/skills-audit-skill/issues"