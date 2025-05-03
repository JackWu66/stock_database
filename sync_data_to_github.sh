#!/bin/bash

# === 設定變數 ===
TODAY=$(date '+%Y%m%d')
REPO_DIR="/Users/jack/Desktop/GitHub/stock-data-public"
LOG_DIR="$REPO_DIR/logs"
LOG_FILE="$LOG_DIR/push_log_$TODAY.txt"

# === 建立 logs 資料夾 ===
mkdir -p "$LOG_DIR"

# === 自動清除 7 天前的 log 檔 ===
find "$LOG_DIR" -name "push_log_*.txt" -mtime +7 -delete

# === 進入正確的 repo 資料夾 ===
cd "$REPO_DIR" || exit

# 確保 remote 設定正確
git remote set-url origin https://github.com/JackWu66/stock-data-public.git

# 顯示 Git 狀態
echo "Checking Git status..." >> "$LOG_FILE"
git status >> "$LOG_FILE" 2>&1

# 加入變更
echo "Adding all changes..." >> "$LOG_FILE"
git add -A >> "$LOG_FILE" 2>&1

# 如果有暫存變更才 commit
if ! git diff --cached --quiet; then
    echo "Committing changes..." >> "$LOG_FILE"
    git commit -m "Auto sync on $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE" 2>&1
fi

# 暫存未加入的變更，避免 rebase 失敗
echo "Stashing unstaged changes..." >> "$LOG_FILE"
git stash push -m "auto-stash-before-push" >> "$LOG_FILE" 2>&1

# 拉取最新遠端（避免 push 被拒）
echo "Pulling latest from origin..." >> "$LOG_FILE"
git pull --rebase origin main >> "$LOG_FILE" 2>&1

# 推送
echo "Pushing changes to GitHub..." >> "$LOG_FILE"
git push origin main >> "$LOG_FILE" 2>&1

# 恢復 stash（如有）
if git stash list | grep -q "auto-stash-before-push"; then
    echo "Restoring stashed changes..." >> "$LOG_FILE"
    git stash pop >> "$LOG_FILE" 2>&1
fi
