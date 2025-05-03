#!/bin/bash

# === 設定變數 ===
TODAY=$(date '+%Y%m%d')
LOG_DIR="/Users/jack/Desktop/GitHub/logs"
LOG_FILE="$LOG_DIR/push_log_$TODAY.txt"

# === 建立 logs 資料夾 ===
mkdir -p "$LOG_DIR"

# === 自動清除 7 天前的 log 檔 ===
find "$LOG_DIR" -name "push_log_*.txt" -mtime +7 -delete

# === Git 自動同步 ===
cd /Users/jack/Desktop/GitHub/stock-data-public || exit

# 顯示狀態
echo "Checking Git status..." >> "$LOG_FILE"
git status >> "$LOG_FILE" 2>&1

# 加入變更
echo "Adding all changes..." >> "$LOG_FILE"
git add -A >> "$LOG_FILE" 2>&1

# 提交（若有變更才 commit）
if ! git diff --cached --quiet; then
    echo "Committing changes..." >> "$LOG_FILE"
    git commit -m "Auto sync on $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE" 2>&1
    if [ $? -ne 0 ]; then
        echo "Commit failed" >> "$LOG_FILE"
        exit 1
    fi

    echo "Pushing changes to GitHub..." >> "$LOG_FILE"
    git push origin main >> "$LOG_FILE" 2>&1
    if [ $? -ne 0 ]; then
        echo "Push failed" >> "$LOG_FILE"
        exit 1
    fi
else
    echo "No changes to commit." >> "$LOG_FILE"
fi
