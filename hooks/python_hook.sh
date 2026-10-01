#!/bin/sh
# Run a Pixeltable hook with a Python 3.9+ that can read the script.
#
# Windows app-execution aliases (Python Install Manager, Store python.exe) pass a
# version check and then fail to open the hook file. Claude Code treats that
# exit 2 as a blocking error. Prefer the Install Manager's plain launcher, then
# each python on PATH, then `py -3`. Skip an interpreter that cannot see the
# script. If none qualify, exit 0 so the edit is not blocked (#23, #30).
export PYTHONUTF8=1

script=$1
if [ -z "$script" ]; then
  exit 0
fi

try() {
  "$@" -c "import os, sys; sys.exit(sys.version_info < (3, 9) or not os.path.isfile(sys.argv[1]))" "$script" >/dev/null 2>&1 \
    && exec "$@" "$script"
}

# Plain launcher, not the WindowsApps alias. Tried even when it is absent: a
# missing executable fails the probe and the search continues. Do not gate this
# on `[ -x ]`; Git Bash often reports Windows-style LOCALAPPDATA paths as
# non-executable even when CreateProcess can run them.
if [ -n "${LOCALAPPDATA:-}" ]; then
  try "$LOCALAPPDATA/Python/bin/python.exe"
fi

# Git Bash rewrites PATH with ':'. A raw Windows PATH uses ';' and contains
# drive-letter colons, so split on ';' when one is present.
old_ifs=$IFS
set -f
case "$PATH" in
  *';'*) IFS=';' ;;
  *) IFS=':' ;;
esac
# shellcheck disable=SC2086
set -- $PATH
set +f
IFS=$old_ifs

for dir in "$@"; do
  if [ -z "$dir" ]; then
    continue
  fi
  for name in python python3 python.exe python3.exe; do
    if [ -x "$dir/$name" ]; then
      try "$dir/$name"
    fi
  done
done

try py -3
exit 0
