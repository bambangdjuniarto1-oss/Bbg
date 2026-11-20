#!/bin/bash
# Render semua adegan video FOOM (fatwa vape). Pemakaian: bash render/render_fom.sh OUTDIR [RES] [SAMPLES] [ADEGAN...]
export FOM_TEX=${FOM_TEX:-/tmp/claude-0/-home-user-Bbg/e4570b9b-8bb7-5f4c-a29b-693bb3cf9daa/scratchpad/fom/tex}
OUT=${1:-out/fom}; RES=${2:-720x1280}; SMP=${3:-4}; shift 3 2>/dev/null
SC=${@:-$(seq -f "F%02g" 1 19)}
cd "$(dirname "$0")/.."
for s in $SC; do
  echo "$(date +%H:%M:%S) start $s"
  python3 render/scenes_fom.py -- --scene $s --out "$OUT/$s" --res $RES --samples $SMP 2>&1 | grep -E "DONE|Error|Traceback"
done
echo "ALL DONE"
