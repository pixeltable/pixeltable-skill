#!/usr/bin/env bash
set -euo pipefail

# Pixeltable Skill — Multi-Platform Installer
# Usage:
#   Interactive:  ./install.sh
#   Direct:       ./install.sh --platform cursor-rule --target ./my-project
#   Curl:         curl -fsSL https://raw.githubusercontent.com/pixeltable/pixeltable-skill/main/install.sh | bash

REPO_URL="https://raw.githubusercontent.com/pixeltable/pixeltable-skill/main"

platform_src() {
  case "$1" in
    cursor-rule)       echo "platforms/cursor-rule/pixeltable.mdc" ;;
    cursor-skill)      echo "SKILL_DIR" ;;
    claude-code)       echo "SKILL_DIR" ;;
    github-copilot)    echo "platforms/github-copilot/copilot-instructions.md" ;;
    windsurf)          echo "platforms/windsurf/.windsurfrules" ;;
    cline)             echo "platforms/cline/.clinerules" ;;
    agents-md)         echo "platforms/agents-md/AGENTS.md" ;;
    system-prompt)     echo "platforms/system-prompt/system-prompt.md" ;;
    openai-custom-gpt) echo "platforms/openai-custom-gpt/instructions.md" ;;
    *) return 1 ;;
  esac
}

platform_dest() {
  case "$1" in
    cursor-rule)       echo ".cursor/rules/pixeltable.mdc" ;;
    cursor-skill)      echo "SKILL_DIR" ;;
    claude-code)       echo "SKILL_DIR" ;;
    github-copilot)    echo ".github/copilot-instructions.md" ;;
    windsurf)          echo ".windsurfrules" ;;
    cline)             echo ".clinerules" ;;
    agents-md)         echo "AGENTS.md" ;;
    system-prompt)     echo "" ;;
    openai-custom-gpt) echo "" ;;
    *) return 1 ;;
  esac
}

platform_label() {
  case "$1" in
    cursor-rule)       echo "Cursor (always-on rule)" ;;
    cursor-skill)      echo "Cursor (agent skill)" ;;
    claude-code)       echo "Claude Code (skill)" ;;
    github-copilot)    echo "GitHub Copilot" ;;
    windsurf)          echo "Windsurf" ;;
    cline)             echo "Cline" ;;
    agents-md)         echo "AGENTS.md (multi-agent convention)" ;;
    system-prompt)     echo "System prompt (raw LLM API)" ;;
    openai-custom-gpt) echo "OpenAI Custom GPT" ;;
    *) return 1 ;;
  esac
}

PLATFORMS="cursor-rule cursor-skill claude-code github-copilot windsurf cline agents-md"

TARGET_DIR=""
PLATFORM=""

usage() {
  cat <<EOF
Pixeltable Skill Installer

Usage:
  ./install.sh                              Interactive mode
  ./install.sh --platform <name> [--target]  Direct mode

Platforms: $PLATFORMS system-prompt openai-custom-gpt

Options:
  --platform  Platform to install for (required in direct mode)
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

fetch_file() {
  local src="$1"
  local dest="$2"
  local dest_dir
  dest_dir="$(dirname "$dest")"
  mkdir -p "$dest_dir"

  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || echo ".")"

  if [[ -f "$script_dir/$src" ]]; then
    cp "$script_dir/$src" "$dest"
  else
    curl -fsSL "$REPO_URL/$src" -o "$dest"
  fi
}

install_skill_dir() {
  local platform="$1"
  local skill_dest

  if [[ "$platform" == "cursor-skill" ]]; then
    skill_dest="$HOME/.cursor/skills/pixeltable-skill"
  elif [[ "$platform" == "claude-code" ]]; then
    skill_dest="$TARGET_DIR/.claude/skills/pixeltable-skill"
  else
    return 1
  fi

  if [[ -d "$skill_dest" ]]; then
    echo ""
    echo "  Directory already exists: $skill_dest"
    read -rp "  Overwrite? [y/N] " answer
    if [[ ! "$answer" =~ ^[Yy] ]]; then
      echo "  Skipped."
      return
    fi
  fi

  mkdir -p "$skill_dest/reference"

  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || echo ".")"

  if [[ -f "$script_dir/skills/pixeltable-skill/SKILL.md" ]]; then
    cp "$script_dir/skills/pixeltable-skill/SKILL.md" "$skill_dest/"
    cp "$script_dir/skills/pixeltable-skill/reference/"*.md "$skill_dest/reference/"
  else
    curl -fsSL "$REPO_URL/skills/pixeltable-skill/SKILL.md" -o "$skill_dest/SKILL.md"
    for ref_file in core-api providers workflows; do
      curl -fsSL "$REPO_URL/skills/pixeltable-skill/reference/${ref_file}.md" -o "$skill_dest/reference/${ref_file}.md"
    done
  fi

  echo "  Installed: $skill_dest/SKILL.md"
  echo "  Installed: $skill_dest/reference/ (core-api.md, providers.md, workflows.md)"
}

install_platform() {
  local p="$1"
  local src dest

  src="$(platform_src "$p")"

  if [[ "$src" == "SKILL_DIR" ]]; then
    install_skill_dir "$p"
    return
  fi

  dest_rel="$(platform_dest "$p")"

  if [[ -z "$dest_rel" ]]; then
    echo ""
    echo "  This platform file is meant to be pasted manually."
    echo "  Printing contents to stdout:"
    echo ""
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || echo ".")"
    if [[ -f "$script_dir/$src" ]]; then
      cat "$script_dir/$src"
    else
      curl -fsSL "$REPO_URL/$src"
    fi
    return
  fi

  local dest="$TARGET_DIR/$dest_rel"

  if [[ -f "$dest" ]]; then
    echo ""
    echo "  File already exists: $dest"
    read -rp "  Overwrite? [y/N] " answer
    if [[ ! "$answer" =~ ^[Yy] ]]; then
      echo "  Skipped."
      return
    fi
  fi

  fetch_file "$src" "$dest"
  echo "  Installed: $dest"
}

if [[ -n "$PLATFORM" ]]; then
  if ! platform_src "$PLATFORM" > /dev/null 2>&1; then
    echo "Unknown platform: $PLATFORM"
    echo "Available: $PLATFORMS system-prompt openai-custom-gpt"
    exit 1
  fi
  install_platform "$PLATFORM"
  exit 0
fi

echo ""
echo "Pixeltable Skill Installer"
echo "=========================="
echo ""
echo "Select a platform to install:"
echo ""

i=1
ALL_PLATFORMS="cursor-rule cursor-skill claude-code github-copilot windsurf cline agents-md system-prompt openai-custom-gpt"
for p in $ALL_PLATFORMS; do
  echo "  $i) $(platform_label "$p")"
  i=$((i + 1))
done

count=$((i - 1))
echo ""
read -rp "Choice [1-$count]: " choice

if [[ -z "$choice" ]] || ! [[ "$choice" =~ ^[0-9]+$ ]] || (( choice < 1 || choice > count )); then
  echo "Invalid choice."
  exit 1
fi

i=1
selected=""
for p in $ALL_PLATFORMS; do
  if [[ $i -eq $choice ]]; then
    selected="$p"
    break
  fi
  i=$((i + 1))
done

echo ""
echo "Installing for: $(platform_label "$selected")"

install_platform "$selected"

echo ""
echo "Done. For the full skill with API reference, install as 'cursor-skill' or 'claude-code'."
echo "  https://github.com/pixeltable/pixeltable-skill"
echo ""
