#!/bin/bash
# Render semua adegan video laundry koin. Pemakaian: bash render/render_laundry.sh OUTDIR [RES] [SAMPLES]
OUT=${1:-out/laundry}; RES=${2:-720x1280}; SMP=${3:-4}
cd "$(dirname "$0")/.."
for s in L01 L02 L03 L04 L05 L06 L07 L08 L09 L10 L11 L12 L13 L14 L15 L16 L17 L18 L19 L20; do
  echo "$(date +%T) start $s"
  python3 render/scenes_laundry.py -- --scene $s --out "$OUT/$s" --res $RES --samples $SMP 2>&1 | grep -E "DONE|Error|Traceback"
done
echo "$(date +%T) ALL DONE"
