#!/bin/bash
# Render semua adegan video CTD (Close The Door). Pemakaian: bash render/render_ctd.sh OUTDIR [RES] [SAMPLES]
OUT=${1:-out/ctd}; RES=${2:-720x1280}; SMP=${3:-4}
cd "$(dirname "$0")/.."
for s in C01 C02 C03 C04 C05 C06 C07 C08 C09 C10 C11 C12 C13 C14 C15 C16 C17 C18 C19 C20 C21 C22 C23 C24 C25; do
  echo "$(date +%T) start $s"
  python3 render/scenes_ctd.py -- --scene $s --out "$OUT/$s" --res $RES --samples $SMP 2>&1 | grep -E "DONE|Error|Traceback"
done
echo "$(date +%T) ALL DONE"
