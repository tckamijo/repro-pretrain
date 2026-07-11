#!/bin/bash
# Fully-detached (nohup) size-ladder finalizer — survives harness task-kills.
# 1) finish Mac run (resumable, niced)  2) wait honmaru run_ladder exit
# 3) pull honmaru JSONs  4) run analyzer  5) iMessage.
# Progress -> runs/finalize.log (read anytime).
set -u
REPO="$HOME/projects/repro-pretrain"
cd "$REPO" || exit 1
PY="$REPO/.venv/bin/python"
PYWIN='C:\Users\chuyo\repro-pretrain\.venv\Scripts\python.exe'
POLL="$(dirname "$0")/pollcheck.py"
LOG="$REPO/runs/finalize.log"
log(){ echo "[finalize $(date '+%m-%d %H:%M:%S')] $*" >> "$LOG"; }

log "START pid=$$"

# 1) Mac run to completion (resumable — skips the 6 done 10m jobs)
nice -n 10 "$PY" -u harness/run_ladder.py --machine mac >> runs/ladder_mac.log 2>&1
log "mac run finished (JSON=$(ls runs/ladder_mac_*.json 2>/dev/null | wc -l | tr -d ' ')/11)"

# 2) wait for honmaru run_ladder to exit (independent process)
while true; do
  S=$(ssh -o ConnectTimeout=10 honmaru "$PYWIN -" < "$POLL" 2>/dev/null)
  log "honmaru $S"
  echo "$S" | grep -q "ALIVE False" && break
  [ -z "$S" ] && log "  (poll failed; retry)"
  sleep 300
done

# 3) pull honmaru JSONs to Mac
scp -q honmaru:C:/Users/chuyo/repro-pretrain/runs/ladder_honmaru_*.json "$REPO/runs/" 2>>"$LOG"
log "pulled honmaru JSON=$(ls runs/ladder_honmaru_*.json 2>/dev/null | wc -l | tr -d ' ')/16"

# 4) analyze
"$PY" analysis/analyze_ladder.py >> "$LOG" 2>&1
log "analysis written to analysis/ladder_report.md"

# 5) iMessage (UTF-8 safe)
MACN=$(ls runs/ladder_mac_*.json 2>/dev/null | wc -l | tr -d ' ')
HMN=$(ls runs/ladder_honmaru_*.json 2>/dev/null | wc -l | tr -d ' ')
BODY="size-ladder 完了: Mac ${MACN}/11 + honmaru ${HMN}/16、解析レポート ladder_report.md 生成済"
tmpfile=$(/usr/bin/mktemp -t fin-notify) || tmpfile="/tmp/fin-notify-$$"
printf '%s' "$BODY" > "$tmpfile"
/usr/bin/osascript <<APPLESCRIPT 2>/dev/null
set bodyText to (do shell script "/bin/cat " & quoted form of "$tmpfile")
tell application "Messages"
    set targetService to 1st service whose service type = iMessage
    set targetBuddy to buddy "chuyo.km@gmail.com" of targetService
    send bodyText to targetBuddy
end tell
APPLESCRIPT
/bin/rm -f "$tmpfile"
log "DONE mac=$MACN honmaru=$HMN"
