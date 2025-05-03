#!/bin/bash

# === 設定變數 ===
TODAY=$(date '+%Y%m%d')
LOG_DIR="/Users/jack/Desktop/GitHub/logs"
LOG_FILE="$LOG_DIR/push_log_$TODAY.txt"
REPO_DIR="/Users/jack/Desktop/GitHub/stock-data-public"

# === 建立 logs 資料夾 ===
mkdir -p "$LOG_DIR"
find "$LOG_DIR" -name "push_log_*.txt" -mtime +7 -delete

# === 進入目標 repo 資料夾 ===
cd "$REPO_DIR" || exit

# === 確保 remote 設定正確 ===
git remote set-url origin https://github.com/JackWu66/stock-data-public.git

# === 顯示目前狀態 ===
echo "Checking Git status..." >> "$LOG_FILE"
git status >> "$LOG_FILE" 2>&1

# === 加入所有變更 ===
echo "Adding all changes..." >> "$LOG_FILE"
git add -A >> "$LOG_FILE" 2>&1

# === 提交變更（如果有） ===
if ! git diff --cached --quiet; then
    echo "Committing changes..." >> "$LOG_FILE"
    git commit -m "Auto sync on $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE" 2>&1

    # === 強制推送（覆蓋遠端）===
    echo "Pushing changes to GitHub..." >> "$LOG_FILE"
    git push -f origin main >> "$LOG_FILE" 2>&1
else
    echo "No changes to commit." >> "$LOG_FILE"
fi
