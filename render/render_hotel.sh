#!/bin/bash
# Render semua adegan video hotel. Pemakaian: bash render/render_hotel.sh OUTDIR [RES] [SAMPLES]
OUT=${1:-out/hotel}; RES=${2:-720x1280}; SMP=${3:-4}
cd "$(dirname "$0")/.."
for s in H01 H02 H03 H04 H05 H06 H07 H08 H09 H10 H11 H12 H13 H14 H15 H16 H17 H18 H19 H20; do
  echo "$(date +%T) start $s"
  python3 render/scenes_hotel.py -- --scene $s --out "$OUT/$s" --res $RES --samples $SMP 2>&1 | grep -E "DONE|Error|Traceback"
done
echo "$(date +%T) ALL DONE"
