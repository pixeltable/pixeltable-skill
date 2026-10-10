#!/usr/bin/env python3
"""Copy the shared skill and icon into plugins/pixeltable-cloud.

The directory installs only the submitted plugin folder, and rejects symbolic links,
so the Cloud plugin carries its own copy. validate_plugin.py fails when the copy drifts.
"""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLOUD = ROOT / "plugins" / "pixeltable-cloud"
SHARED = ["skills/pixeltable-skill", "assets/icon.png"]


def main():
    for rel in SHARED:
        src, dst = ROOT / rel, CLOUD / rel
        if dst.is_dir():
            shutil.rmtree(dst)
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        print(f"synced {rel}")


if __name__ == "__main__":
    main()
