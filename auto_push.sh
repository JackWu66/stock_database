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
cd /Users/jack/Desktop/GitHub/Stock || exit

# 確保 remote 是正確的
git remote set-url origin https://github.com/JackWu66/Stock.git

# 顯示狀態
git status >> "$LOG_FILE" 2>&1

# 加入變更
git add . >> "$LOG_FILE" 2>&1

# 提交（若有變更才 commit）
if ! git diff --cached --quiet; then
    git commit -m "Auto sync on $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE" 2>&1
    git push origin main >> "$LOG_FILE" 2>&1
else
    echo "No changes to commit." >> "$LOG_FILE"
fi