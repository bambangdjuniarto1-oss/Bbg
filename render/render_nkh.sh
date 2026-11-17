#!/bin/bash
# Render semua adegan video Nikahan. Pemakaian: bash render/render_nkh.sh OUTDIR [RES] [SAMPLES] [ADEGAN...]
OUT=${1:-out/nkh}; RES=${2:-720x1280}; SMP=${3:-4}; shift 3 2>/dev/null
SC=${@:-$(seq -f "N%02g" 1 18)}
cd "$(dirname "$0")/.."
for s in $SC; do
  echo "$(date +%H:%M:%S) start $s"
  python3 render/scenes_nkh.py -- --scene $s --out "$OUT/$s" --res $RES --samples $SMP 2>&1 | grep -E "DONE|Error|Traceback"
done
echo "ALL DONE"
