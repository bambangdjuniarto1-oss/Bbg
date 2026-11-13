#!/bin/bash
# Render semua adegan video sawit. Pemakaian: bash render/render_sawit.sh OUTDIR [RES] [SAMPLES]
OUT=${1:-out/sawit}; RES=${2:-720x1280}; SMP=${3:-4}
cd "$(dirname "$0")/.."
for s in K01 K02 K03 K04 K05 K06 K07 K08 K09 K10 K11 K12 K13 K14 K15 K16 K17 K18 K19 K20; do
  echo "$(date +%T) start $s"
  python3 render/scenes_sawit.py -- --scene $s --out "$OUT/$s" --res $RES --samples $SMP 2>&1 | grep -E "DONE|Error|Traceback"
done
echo "$(date +%T) ALL DONE"
