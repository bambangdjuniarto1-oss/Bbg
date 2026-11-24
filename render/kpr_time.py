"""Peta waktu video KPR: semua waktu di scenes_kpr/gen_kpr_cfg ditulis pada timeline VO versi 1 (tempo 1,05);
VO versi 2 (tempo asli 1,0) lebih panjang. tm(t) memetakan waktu v1 -> v2 secara linear per kata (awal kata v1
-> awal kata v2), sehingga semua efek/label/kamera tetap jatuh tepat di kata yang sama."""
import json
import os

_D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scenes")
_A = [w[0] for w in json.load(open(os.path.join(_D, "kpr_words_v1.json")))]
_B = [w[0] for w in json.load(open(os.path.join(_D, "kpr_words.json")))]
END_V1, END_V2 = 82.6, _B[-1] + 1.75


def tm(t):
    if t <= _A[0]:
        return t
    if t >= _A[-1]:
        return _B[-1] + (t - _A[-1]) * (END_V2 - _B[-1]) / (END_V1 - _A[-1])
    i = 0
    while _A[i + 1] < t:
        i += 1
    a0, a1, b0, b1 = _A[i], _A[i + 1], _B[i], _B[i + 1]
    if a1 - a0 < 1e-6:
        return b0
    return b0 + (t - a0) * (b1 - b0) / (a1 - a0)
