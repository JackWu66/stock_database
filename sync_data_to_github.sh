#!/bin/bash

# === 設定變數 ===
TODAY=$(date '+%Y%m%d')
REPO_DIR="/Users/jack/Desktop/GitHub/stock-data-public"
LOG_DIR="/Users/jack/Desktop/GitHub/logs"
LOG_FILE="$LOG_DIR/push_log_$TODAY.txt"

# === 建立 logs 資料夾 ===
mkdir -p "$LOG_DIR"

# === 自動清除 7 天前的 log 檔 ===
find "$LOG_DIR" -name "push_log_*.txt" -mtime +7 -delete

# === 進入 repo ===
cd "$REPO_DIR" || exit

# 確保 remote 正確
git remote set-url origin https://github.com/JackWu66/stock-data-public.git

# 顯示狀態
echo "Checking Git status..." >> "$LOG_FILE"
git status >> "$LOG_FILE" 2>&1

# 加入變更
echo "Adding all changes..." >> "$LOG_FILE"
git add -A >> "$LOG_FILE" 2>&1

# 若有變更再提交
if ! git diff --cached --quiet; then
    echo "Committing changes..." >> "$LOG_FILE"
    git commit -m "Auto sync on $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE" 2>&1

    echo "Pulling latest from remote (rebase)..." >> "$LOG_FILE"
    git pull --rebase origin main >> "$LOG_FILE" 2>&1

    echo "Pushing changes to GitHub..." >> "$LOG_FILE"
    git push origin main >> "$LOG_FILE" 2>&1

else
    echo "No changes to commit." >> "$LOG_FILE"
fi
