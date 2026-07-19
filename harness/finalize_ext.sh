#!/bin/bash
# Ladder-extension finalizer (nohup, self-healing). Mac MPS run is ALREADY running
# (do not restart it); this waits for it, keeps honmaru's CUDA run alive until done,
# then pulls + re-analyzes. Targets: honmaru 22 jsons (16 + 6 ext), mac 17 (11 + 6 ext).
set -u
REPO="$HOME/projects/repro-pretrain"
cd "$REPO" || exit 1
PY="$REPO/.venv/bin/python"
PYWIN='C:\Users\chuyo\repro-pretrain\.venv\Scripts\python.exe'
POLL="$REPO/harness/pollcheck.py"
LOG="$REPO/runs/finalize_ext.log"
DONE="$REPO/runs/FINALIZE_EXT_DONE.txt"
HON_TARGET=22
MAC_TARGET=17
log(){ echo "[ext $(date '+%m-%d %H:%M:%S')] $*" >> "$LOG"; }
poll(){ ssh -o ConnectTimeout=10 honmaru "$PYWIN -" < "$POLL" 2>/dev/null; }

log "START pid=$$ (honmaru->$HON_TARGET, mac->$MAC_TARGET)"

# honmaru keeper (launches run_ladder on first poll since it's not running; relaunches on death)
(
  while true; do
    S=$(poll)
    alive=$(echo "$S" | awk '/ALIVE/{print $2}')
    count=$(echo "$S" | awk '/COUNT/{print $NF}' | tr -d '\r')
    log "keeper honmaru: $S"
    [ -n "$count" ] && [ "$count" -ge "$HON_TARGET" ] && { log "keeper: honmaru $count/$HON_TARGET done"; break; }
    if [ "$alive" = "False" ]; then
      log "keeper: (re)launch honmaru (${count:-?}/$HON_TARGET)"
      nohup ssh -o ServerAliveInterval=60 -o ConnectTimeout=10 honmaru \
        "& '$PYWIN' -u C:/Users/chuyo/repro-pretrain/harness/run_ladder.py --machine honmaru" \
        >> "$REPO/runs/ladder_honmaru_ext_stream.log" 2>&1 &
    fi
    sleep 180
  done
) &
KEEPER=$!

# wait for Mac (already running) to reach target
while true; do
  n=$(ls runs/ladder_mac_*.json 2>/dev/null | wc -l | tr -d ' ')
  log "mac json=$n/$MAC_TARGET"
  [ "$n" -ge "$MAC_TARGET" ] && break
  sleep 180
done
log "mac done"

wait "$KEEPER"
log "honmaru keeper finished"

scp -q "honmaru:C:/Users/chuyo/repro-pretrain/runs/ladder_honmaru_*.json" "$REPO/runs/" 2>>"$LOG"
log "pulled honmaru json=$(ls runs/ladder_honmaru_*.json 2>/dev/null | wc -l | tr -d ' ')"

"$PY" analysis/analyze_ladder.py >> "$LOG" 2>&1
log "analysis -> analysis/ladder_report.md"

MACN=$(ls runs/ladder_mac_*.json 2>/dev/null | wc -l | tr -d ' ')
HMN=$(ls runs/ladder_honmaru_*.json 2>/dev/null | wc -l | tr -d ' ')
{ echo "EXTENSION FINALIZE DONE $(date '+%Y-%m-%d %H:%M:%S')"
  echo "mac ${MACN} + honmaru ${HMN} jsons; 30m/75m ladder extension"; } > "$DONE"
log "DONE mac=$MACN honmaru=$HMN"
