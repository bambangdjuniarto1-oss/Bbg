#!/bin/bash
# Render semua adegan Persib Part 2 (mesin uang). Pemakaian: bash render/render_ps2.sh OUTDIR [RES] [SAMPLES] [ADEGAN...]
export PSB_TEX=${PSB_TEX:-/tmp/claude-0/-home-user-Bbg/e4570b9b-8bb7-5f4c-a29b-693bb3cf9daa/scratchpad/ps2/tex}
OUT=${1:-out/ps2}; RES=${2:-864x1536}; SMP=${3:-4}; shift 3 2>/dev/null
SC=${@:-$(seq -f "Q%02g" 1 19)}
cd "$(dirname "$0")/.."
for s in $SC; do
  echo "$(date +%H:%M:%S) start $s"
  python3 render/scenes_ps2.py -- --scene $s --out "$OUT/$s" --res $RES --samples $SMP 2>&1 | grep -E "DONE|Error|Traceback"
done
echo "ALL DONE"
