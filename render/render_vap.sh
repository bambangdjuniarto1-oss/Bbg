#!/bin/bash
# Render semua adegan video Liquid Vape. Pemakaian: bash render/render_vap.sh OUTDIR [RES] [SAMPLES] [ADEGAN...]
OUT=${1:-out/vap}; RES=${2:-720x1280}; SMP=${3:-4}; shift 3 2>/dev/null
SC=${@:-$(seq -f "V%02g" 1 20)}
cd "$(dirname "$0")/.."
for s in $SC; do
  echo "$(date +%H:%M:%S) start $s"
  python3 render/scenes_vap.py -- --scene $s --out "$OUT/$s" --res $RES --samples $SMP 2>&1 | grep -E "DONE|Error|Traceback"
done
echo "ALL DONE"
