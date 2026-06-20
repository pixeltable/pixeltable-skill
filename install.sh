#!/usr/bin/env bash
set -euo pipefail

# Pixeltable Skill Installer
# Prefer: npx skills add pixeltable/pixeltable-skill (audited, no curl|bash)
# Usage:
#   Interactive:  ./install.sh
#   Direct:       ./install.sh --platform claude-code --target ./my-project

REPO_URL="https://raw.githubusercontent.com/pixeltable/pixeltable-skill/main"
REF_FILES="core-api cli providers workflows video-rag-agents agents-memory-mcp ml-data-pipeline agentic-patterns anti-patterns"

TARGET_DIR=""
PLATFORM=""

usage() {
  cat <<EOF
Pixeltable Skill Installer

Usage:
  ./install.sh                              Interactive mode
  ./install.sh --platform <name> [--target]  Direct mode

Platforms: claude-code, cursor-skill

Options:
  --platform  claude-code or cursor-skill
  --target    Target project directory (defaults to current directory)
  --help      Show this help message
EOF
  exit 0
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --platform) PLATFORM="$2"; shift 2 ;;
    --target)   TARGET_DIR="$2"; shift 2 ;;
    --help)     usage ;;
    *)          echo "Unknown option: $1"; usage ;;
  esac
done

TARGET_DIR="${TARGET_DIR:-.}"

install_skill() {
  local platform="$1"
  local skill_dest

  if [[ "$platform" == "cursor-skill" ]]; then
    skill_dest="$HOME/.cursor/skills/pixeltable-skill"
  elif [[ "$platform" == "claude-code" ]]; then
    skill_dest="$TARGET_DIR/.claude/skills/pixeltable-skill"
  else
    echo "Unknown platform: $platform"
    echo "Available: claude-code, cursor-skill"
    exit 1
  fi

  if [[ -d "$skill_dest" ]]; then
    echo "  Directory already exists: $skill_dest"
    read -rp "  Overwrite? [y/N] " answer < /dev/tty
    if [[ ! "$answer" =~ ^[Yy] ]]; then
      echo "  Skipped."
      return
    fi
  fi

  mkdir -p "$skill_dest/references"

  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || echo ".")"

  if [[ -f "$script_dir/skills/pixeltable-skill/SKILL.md" ]]; then
    cp "$script_dir/skills/pixeltable-skill/SKILL.md" "$skill_dest/"
    cp "$script_dir/skills/pixeltable-skill/references/"*.md "$skill_dest/references/"
  else
    curl -fsSL "$REPO_URL/skills/pixeltable-skill/SKILL.md" -o "$skill_dest/SKILL.md"
    for ref_file in $REF_FILES; do
      curl -fsSL "$REPO_URL/skills/pixeltable-skill/references/${ref_file}.md" -o "$skill_dest/references/${ref_file}.md"
    done
  fi

  echo "  Installed: $skill_dest/SKILL.md + references/ (9 files)"
}

# Direct mode
if [[ -n "$PLATFORM" ]]; then
  install_skill "$PLATFORM"
  exit 0
fi

# Detect piped stdin
if [[ ! -t 0 ]]; then
  echo "Error: Interactive mode requires a terminal."
  echo "Usage: curl -fsSL ... | bash -s -- --platform claude-code"
  exit 1
fi

# Interactive mode
echo ""
echo "Pixeltable Skill Installer"
echo "=========================="
echo ""
echo "  1) Claude Code"
echo "  2) Cursor (agent skill)"
echo ""
read -rp "Choice [1-2]: " choice < /dev/tty

case "$choice" in
  1) install_skill "claude-code" ;;
  2) install_skill "cursor-skill" ;;
  *) echo "Invalid choice."; exit 1 ;;
esac

echo ""
echo "Done. https://github.com/pixeltable/pixeltable-skill"
echo ""
