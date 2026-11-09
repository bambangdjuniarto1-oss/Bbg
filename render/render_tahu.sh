#!/bin/bash
# Render semua adegan video tahu. Pemakaian: bash render/render_tahu.sh OUTDIR [RES] [SAMPLES]
OUT=${1:-out/tahu}; RES=${2:-720x1280}; SMP=${3:-4}
cd "$(dirname "$0")/.."
for s in T01 T02 T03 T04 T05 T06 T07 T08 T09 T10 T11 T12 T13 T14 T15 T16 T17 T18 T19 T20; do
  echo "$(date +%T) start $s"
  python3 render/scenes_tahu.py -- --scene $s --out "$OUT/$s" --res $RES --samples $SMP 2>&1 | grep -E "DONE|Error|Traceback"
done
echo "$(date +%T) ALL DONE"
