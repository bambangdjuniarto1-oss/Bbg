#!/bin/bash
# Mix akhir: VO (sudah dirapikan) + musik (di-duck saat VO bicara) + SFX -> -14 LUFS.
# Tanpa ubah tempo lagi (VO sudah final), kompresi VO lembut supaya tidak "memompa".
# Pemakaian: bash render/mix_final.sh VO.wav MUSIC.wav SFX_EVENTS.json DURASI OUTDIR [SFX_DB=-7]
set -e
VO=$1; MUS=$2; EV=$3; DUR=$4; OUT=$5; SDB=${6:--7}
mkdir -p "$OUT"
cd "$(dirname "$0")/.."
lufs() { ffmpeg -hide_banner -i "$1" -af ebur128 -f null - 2>&1 | grep -E "^\s+I:" | tail -1 | awk '{print $2}'; }
python3 render/sfx.py "$EV" "$DUR" "$OUT/sfx.wav"
ffmpeg -v error -y -i "$VO" -af "acompressor=threshold=-22dB:ratio=2:attack=12:release=160:makeup=1" -ar 44100 -ac 1 "$OUT/vo_c.wav"
GV=$(python3 -c "print(-17-($(lufs "$OUT/vo_c.wav")))")
GM=$(python3 -c "print(${MUS_LUFS:--24}-($(lufs "$MUS")))")      # MUS_LUFS=-21.5 -> musik lebih keras
ffmpeg -v error -y -i "$OUT/vo_c.wav" -i "$MUS" -i "$OUT/sfx.wav" -filter_complex "\
[0:a]volume=${GV}dB,apad=whole_dur=${DUR},asplit=3[vo][key][key2];[1:a]volume=${GM}dB,atrim=0:${DUR}[mus];\
[mus][key]sidechaincompress=threshold=0.03:ratio=2.2:attack=40:release=450[duck];\
[vo]pan=stereo|c0=c0|c1=c0[vos];[2:a]volume=${SDB}dB[sfxr];\
[sfxr][key2]sidechaincompress=threshold=0.02:ratio=${SFX_DUCK:-1}:attack=8:release=260[sfxd];\
[vos][duck][sfxd]amix=inputs=3:duration=first:normalize=0,afade=t=out:st=$(python3 -c "print($DUR-0.6)"):d=0.6[m]" \
  -map "[m]" -ar 44100 "$OUT/premix.wav"
ffmpeg -v error -y -i "$OUT/premix.wav" -af "loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.89:level=false" -ar 44100 \
  "$OUT/final.wav"
echo "final $(lufs "$OUT/final.wav") LUFS -> $OUT/final.wav"
