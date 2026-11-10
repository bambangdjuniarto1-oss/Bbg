"""Timestamp per kata dari VO (untuk subtitle), sudah disesuaikan dengan tempo VO yang dipercepat.

  python3 render/transcribe.py VO.wav render/scenes/NAMA_words.json [--speed 1.4] [--model small]

Hasil: list [mulai, selesai, kata] dalam detik timeline video. Setelah itu cek & rapikan
salah dengar (mis. "tau" -> "tahu") dan gabungkan angka ("7,5", "Rp6.000") langsung di JSON.
Butuh: pip install faster-whisper
"""
import argparse
import json

from faster_whisper import WhisperModel


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vo")
    ap.add_argument("out")
    ap.add_argument("--speed", type=float, default=1.0, help="tempo VO di video (mis. 1.4)")
    ap.add_argument("--model", default="small")
    ap.add_argument("--lang", default="id")
    a = ap.parse_args()
    model = WhisperModel(a.model, device="cpu", compute_type="int8")
    segs, _ = model.transcribe(a.vo, language=a.lang, word_timestamps=True, vad_filter=True)
    words = []
    for s in segs:
        for w in s.words:
            words.append([round(w.start / a.speed, 3), round(w.end / a.speed, 3), w.word.strip()])
    json.dump(words, open(a.out, "w"), ensure_ascii=False)
    print(len(words), "kata ->", a.out)


if __name__ == "__main__":
    main()
