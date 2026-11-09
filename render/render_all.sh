#!/bin/bash
# Render semua adegan berurutan. Pemakaian: bash render/render_all.sh OUTDIR [RES] [SAMPLES]
OUT=${1:-out/scenes}; RES=${2:-720x1280}; SMP=${3:-8}
cd "$(dirname "$0")/.."
for s in S01 S02 S03 S04 S05 S06 S07 S08 S09 S10 S11 S12 S13 S14 S15 S16; do
  echo "$(date +%T) start $s"
  python3 render/scenes.py -- --scene $s --out "$OUT/$s" --res $RES --samples $SMP 2>&1 | grep -E "DONE|Error|Traceback"
done
echo "$(date +%T) ALL DONE"
