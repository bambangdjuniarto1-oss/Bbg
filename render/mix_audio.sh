#!/bin/bash
# Percepat VO (pitch tetap) + bikin backsound orisinal + mix (VO dominan, musik di-duck saat VO bicara).
# Pemakaian: bash render/mix_audio.sh NARASI.mp3 OUTDIR [SPEED] [BREAK_MULAI BREAK_SELESAI] [VARIAN] [BPM]
# (BREAK dalam detik timeline yang sudah dipercepat: bagian musik tanpa drum)
# Hasil: OUTDIR/mix.wav (~-14 LUFS; musik ±13-15 dB di bawah VO, mirip proporsi video referensi)
set -e
VO=$1; OUT=$2; SPD=${3:-1.28}; B0=${4:-}; B1=${5:-}; VAR=${6:-A}; BPM=${7:-128}
mkdir -p "$OUT"
cd "$(dirname "$0")/.."
lufs() { ffmpeg -hide_banner -i "$1" -af ebur128 -f null - 2>&1 | grep -E "^\s+I:" | tail -1 | awk '{print $2}'; }

ffmpeg -v error -y -i "$VO" -af "rubberband=tempo=$SPD:pitchq=quality:formant=preserved,highpass=f=70,acompressor=threshold=-24dB:ratio=3:attack=5:release=80" \
  -ar 44100 -ac 1 "$OUT/vo_fast.wav"
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT/vo_fast.wav")
if [ -z "$B0" ]; then B0=$(python3 -c "print(26.4/$SPD)"); B1=$(python3 -c "print(31.2/$SPD)"); fi
python3 render/music.py "$OUT/music.wav" "$DUR" --break $B0 $B1 --variant $VAR --bpm $BPM
GV=$(python3 -c "print(-17-($(lufs "$OUT/vo_fast.wav")))")
GM=$(python3 -c "print(-23-($(lufs "$OUT/music.wav")))")
ffmpeg -v error -y -i "$OUT/vo_fast.wav" -i "$OUT/music.wav" -filter_complex "\
[0:a]volume=${GV}dB,aresample=44100,asplit=2[vo][key];[1:a]volume=${GM}dB[mus];\
[mus][key]sidechaincompress=threshold=0.03:ratio=2:attack=30:release=400[duck];\
[vo]pan=stereo|c0=c0|c1=c0[vos];\
[vos][duck]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.89:level=false[out]" -map "[out]" "$OUT/mix.wav"
echo "mix $(lufs "$OUT/mix.wav") LUFS -> $OUT/mix.wav"
