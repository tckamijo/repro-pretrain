#!/bin/bash
# Self-healing, fully-detached (nohup) size-ladder finalizer.
# Survives harness task-kills AND honmaru run_ladder death (SSH reaping).
#  - honmaru_keeper (bg): whenever honmaru run_ladder is NOT alive and <16 done,
#    relaunch it (resumable, skips done). Loops until 16 honmaru JSONs.
#  - Mac run (fg): resumable to 11.
#  - then: pull honmaru JSONs, run analyzer, write DONE marker (iMessage best-effort).
# Progress + completion -> runs/finalize.log (read anytime; iMessage is unreliable).
set -u
REPO="$HOME/projects/repro-pretrain"
cd "$REPO" || exit 1
PY="$REPO/.venv/bin/python"
PYWIN='C:\Users\chuyo\repro-pretrain\.venv\Scripts\python.exe'
POLL="$REPO/harness/pollcheck.py"
LOG="$REPO/runs/finalize.log"
DONE="$REPO/runs/FINALIZE_DONE.txt"
log(){ echo "[finalize $(date '+%m-%d %H:%M:%S')] $*" >> "$LOG"; }

poll(){ ssh -o ConnectTimeout=10 honmaru "$PYWIN -" < "$POLL" 2>/dev/null; }  # -> "ALIVE <b> COUNT <n>"

honmaru_keeper(){
  while true; do
    S=$(poll)
    local alive count
    alive=$(echo "$S" | awk '/ALIVE/{print $2}')
    count=$(echo "$S" | awk '/COUNT/{print $NF}' | tr -d '\r')  # strip Windows CR (else -ge breaks)
    log "keeper honmaru: $S"
    [ -n "$count" ] && [ "$count" -ge 16 ] && { log "keeper: honmaru complete 16/16"; break; }
    if [ "$alive" = "False" ]; then
      log "keeper: honmaru not running (${count:-?}/16) -> relaunch resumable"
      nohup ssh -o ServerAliveInterval=60 -o ConnectTimeout=10 honmaru \
        "& '$PYWIN' -u C:/Users/chuyo/repro-pretrain/harness/run_ladder.py --machine honmaru" \
        >> "$REPO/runs/ladder_honmaru_stream.log" 2>&1 &
    fi
    sleep 180
  done
}

log "START pid=$$ (self-healing)"
honmaru_keeper &
KEEPER=$!

# Mac run to completion (resumable, niced) — concurrent with honmaru keeper
nice -n 10 "$PY" -u harness/run_ladder.py --machine mac >> runs/ladder_mac.log 2>&1
log "mac run finished (JSON=$(ls runs/ladder_mac_*.json 2>/dev/null | wc -l | tr -d ' ')/11)"

wait "$KEEPER"
log "honmaru keeper finished"

# pull honmaru JSONs to Mac
scp -q honmaru:C:/Users/chuyo/repro-pretrain/runs/ladder_honmaru_*.json "$REPO/runs/" 2>>"$LOG"
log "pulled honmaru JSON=$(ls runs/ladder_honmaru_*.json 2>/dev/null | wc -l | tr -d ' ')/16"

# analyze
"$PY" analysis/analyze_ladder.py >> "$LOG" 2>&1
log "analysis -> analysis/ladder_report.md"

# on-disk completion marker (primary signal; iMessage is unreliable per user)
MACN=$(ls runs/ladder_mac_*.json 2>/dev/null | wc -l | tr -d ' ')
HMN=$(ls runs/ladder_honmaru_*.json 2>/dev/null | wc -l | tr -d ' ')
{
  echo "SIZE-LADDER FINALIZE DONE $(date '+%Y-%m-%d %H:%M:%S')"
  echo "Mac ${MACN}/11 + honmaru ${HMN}/16 jobs"
  echo "report: $REPO/analysis/ladder_report.md"
} > "$DONE"
log "DONE mac=$MACN honmaru=$HMN -> $DONE"

# best-effort iMessage — opt-in only; set CC_NOTIFY_IMESSAGE to your own iMessage
# handle to enable. Disk marker (FINALIZE_DONE.txt) above is the authoritative signal.
if [ -n "${CC_NOTIFY_IMESSAGE:-}" ]; then
  tmpfile=$(/usr/bin/mktemp -t fin-notify) || tmpfile="/tmp/fin-notify-$$"
  printf '%s' "size-ladder done Mac${MACN}/11 honmaru${HMN}/16 -> analysis/ladder_report.md" > "$tmpfile"
  /usr/bin/osascript >/dev/null 2>&1 <<APPLESCRIPT
set bodyText to (do shell script "/bin/cat " & quoted form of "$tmpfile")
tell application "Messages"
    set targetService to 1st service whose service type = iMessage
    set targetBuddy to buddy "$CC_NOTIFY_IMESSAGE" of targetService
    send bodyText to targetBuddy
end tell
APPLESCRIPT
  /bin/rm -f "$tmpfile"
fi
