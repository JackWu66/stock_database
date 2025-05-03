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

# 確保 remote 是正確的
git remote set-url origin https://github.com/JackWu66/stock-data-public.git

# 顯示狀態
echo "Checking Git status..." >> "$LOG_FILE"
git status >> "$LOG_FILE" 2>&1

# 檢查遠端儲存庫配置，確保指向正確的儲存庫
REMOTE_URL=$(git remote get-url origin)
EXPECTED_URL="https://github.com/JackWu66/stock-data-public.git"  # 替換成你的正確儲存庫URL

if [ "$REMOTE_URL" != "$EXPECTED_URL" ]; then
    echo "Error: The remote repository URL is incorrect. Expected $EXPECTED_URL but got $REMOTE_URL" >> "$LOG_FILE"
    exit 1
fi

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
