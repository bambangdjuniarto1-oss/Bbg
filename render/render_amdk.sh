#!/bin/bash
# Render semua adegan video AMDK. Pemakaian: bash render/render_amdk.sh OUTDIR [RES] [SAMPLES]
OUT=${1:-out/amdk}; RES=${2:-720x1280}; SMP=${3:-4}
cd "$(dirname "$0")/.."
for s in A01 A02 A03 A04 A05 A06 A07 A08 A09 A10 A11 A12 A13 A14 A15 A16 A17 A18 A19 A20 A21 A22; do
  echo "$(date +%T) start $s"
  python3 render/scenes_amdk.py -- --scene $s --out "$OUT/$s" --res $RES --samples $SMP 2>&1 | grep -E "DONE|Error|Traceback"
done
echo "$(date +%T) ALL DONE"
