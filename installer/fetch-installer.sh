#!/usr/bin/env bash
# 下载 macOS 恢复镜像（需要 Python 3）
set -e
cd "$(dirname "$0")/../scripts"
python3 macrecovery.py -b Mac-XXXXXXXX -m 0000000000000000 download
mv com.apple.recovery.boot/BaseSystem.dmg ../installer/ 2>/dev/null || true
mv com.apple.recovery.boot/BaseSystem.chunklist ../installer/ 2>/dev/null || true
echo "done -> $(pwd)/../installer"
