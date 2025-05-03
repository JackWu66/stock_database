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

# 設定遠端（保險起見）
git remote set-url origin https://github.com/JackWu66/stock-data-public.git

# 顯示狀態
echo "Checking Git status..." >> "$LOG_FILE"
git status >> "$LOG_FILE" 2>&1

# 加入變更（限定在這個 repo 資料夾）
echo "Adding all changes..." >> "$LOG_FILE"
git add -A >> "$LOG_FILE" 2>&1

# 提交變更
if ! git diff --cached --quiet; then
    echo "Committing changes..." >> "$LOG_FILE"
    git commit -m "Auto sync on $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE" 2>&1
fi

# === stash 未加入的變更，避免 pull/rebase 失敗 ===
echo "Stashing unstaged changes..." >> "$LOG_FILE"
git stash push -m "auto-stash-before-rebase" >> "$LOG_FILE" 2>&1

# === pull 並 rebase 遠端更新 ===
echo "Pulling latest from remote (rebase)..." >> "$LOG_FILE"
git pull --rebase origin main >> "$LOG_FILE" 2>&1

# === 推送變更 ===
echo "Pushing changes to GitHub..." >> "$LOG_FILE"
git push origin main >> "$LOG_FILE" 2>&1

# === 還原 stash（如有）===
if git stash list | grep -q "auto-stash-before-rebase"; then
    echo "Applying stashed changes..." >> "$LOG_FILE"
    git stash pop >> "$LOG_FILE" 2>&1
fi
