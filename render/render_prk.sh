#!/bin/bash
# Render semua adegan video Juru Parkir. Pemakaian: bash render/render_prk.sh OUTDIR [RES] [SAMPLES]
OUT=${1:-out/prk}; RES=${2:-720x1280}; SMP=${3:-4}
cd "$(dirname "$0")/.."
for s in Q01 Q02 Q03 Q04 Q05 Q06 Q07 Q08 Q09 Q10 Q11 Q12 Q13 Q14 Q15 Q16 Q17 Q18 Q19; do
  echo "$(date +%T) start $s"
  python3 render/scenes_prk.py -- --scene $s --out "$OUT/$s" --res $RES --samples $SMP 2>&1 | grep -E "DONE|Error|Traceback"
done
echo "$(date +%T) ALL DONE"
