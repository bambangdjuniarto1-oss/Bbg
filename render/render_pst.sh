#!/bin/bash
# Render semua adegan video Pestapora. Pemakaian: bash render/render_pst.sh OUTDIR [RES] [SAMPLES]
OUT=${1:-out/pst}; RES=${2:-720x1280}; SMP=${3:-4}
cd "$(dirname "$0")/.."
for s in P01 P02 P03 P04 P05 P06 P07 P08 P09 P10 P11 P12 P13 P14 P15 P16 P17 P18 P19 P20 P21 P22 P23; do
  echo "$(date +%T) start $s"
  python3 render/scenes_pst.py -- --scene $s --out "$OUT/$s" --res $RES --samples $SMP 2>&1 | grep -E "DONE|Error|Traceback"
done
echo "$(date +%T) ALL DONE"
