"""buat render/scenes/prk.json dari waktu absolut (detik timeline) -> detik lokal adegan."""
import json, re
src = open("render/scenes_prk.py").read()
TL = dict((a, float(b)) for a, b in re.findall(r'\("(Q\d\d)", ([\d.]+)\)', src))
HUD = dict(pos=[56, 1430], prefix="Rp ")

def lb(anchor, title, t, color="blue", sub="", lift=90, until=None):
    d = dict(anchor=anchor, title=title, sub=sub, color=color, t=t, lift=lift)
    if until is not None:
        d["until"] = until
    return d

S = [
 ("Q01", "Modal **rompi & peluit**", [lb("ROMPI", "ROMPI", .45, "orange", "", 120), lb("PELUIT", "PELUIT", .95, "blue", "", 40)], None, None),
 ("Q02", "Sebulan **Rp12 juta**?", [lb("STACK", "Rp12 JUTA / BULAN?", 2.95, "green", "", 70)], None, None),
 ("Q03", "Lebih **cuan** dari karyawan?", [lb("JUKIR", "JURU PARKIR", 5.0, "orange", "", 60),
                                         lb("KASIR", "KARYAWAN MINIMARKET", 6.85, "blue", "", 60)], None, None),
 ("Q04", "Kita **hitung**", [lb("CALC", "HITUNG", 7.9, "orange", "simulasi sederhana", 60),
                             lb("STORE", "1 MINIMARKET RAMAI", 9.0, "green", "", 60)], None, None),
 ("Q05", "**150 motor** + **20 mobil**", [lb("MOTOR", "150 MOTOR / HARI", 11.7, "blue", "", 70),
                                          lb("MOBIL", "20 MOBIL / HARI", 13.8, "orange", "", 70)],
  dict(title="KENDARAAN PER HARI", start=0, keys=[[11.65, 150], [13.8, 170]], max=170, unit="kendaraan", t=11.5,
       dur=1.0, prefix="", target_text="motor + mobil"), None),
 ("Q06", "Motor **Rp2.000**, mobil **Rp5.000**", [lb("MOTOR", "MOTOR Rp2.000", 15.55, "blue", "", 60),
                                                  lb("MOBIL", "MOBIL Rp5.000", 16.55, "orange", "", 60)], None, None),
 ("Q07", "Sebulan **Rp12 juta**", [lb("DAY", "Rp400 RB / HARI", 18.25, "blue", "", 50),
                                   lb("CAL", "× 30 HARI", 19.65, "orange", "", 50),
                                   lb("STACK", "Rp12 JUTA / BULAN", 20.9, "green", "", 60)], None,
  [dict(type="table", title="PEMASUKAN PARKIR (SIMULASI)", cols=["HITUNGAN", "NILAI"], widths=[460, 280],
        rows=[["150 motor × Rp2.000", "Rp300 rb"], ["20 mobil × Rp5.000", "Rp100 rb"], ["Sehari", "Rp400 rb"],
              ["Sebulan (30 hari)", "Rp12 jt"]],
        row_t=[17.8, 18.0, 18.3, 20.3], red_col=-1, y=600)]),
 ("Q08", "Tapi **nggak semua** masuk kantong", [lb("POUCH", "KANTONG JUKIR", 23.9, "orange", "", 50),
                                                lb("TOP", "BUKAN MILIK JUKIR", 24.45, "red", "", 60)], None, None),
 ("Q09", "Ada **setoran** ke pengelola", [lb("PIN", "BANYAK TITIK PARKIR", 25.5, "green", "", 60),
                                          lb("HQ", "PENGELOLA", 27.8, "purple", "", 60),
                                          lb("SETOR", "SETORAN Rp150 RB / HARI", 29.2, "red", "contoh", 50)], None, None),
 ("Q10", "Setoran **Rp4,5 juta**/bulan", [lb("SETOR", "SETORAN Rp4,5 JT", 32.1, "red", "Rp150 rb × 30 hari", 60),
                                          lb("LAYAR", "PENGELOLA", 33.9, "purple", "", 60)],
  dict(title="SETORAN SEBULAN", start=0, to=4.5, max=12, unit="juta", t=31.9, dur=1.0, decimals=1, trim_zero=True,
       target_text="Rp150 rb × 30 hari", bar="red"), None),
 ("Q11", "Sisa **±Rp7,5 juta**", [lb("SISA", "SISA ±Rp7,5 JUTA", 35.5, "green", "Rp12 jt − Rp4,5 jt", 60)],
  dict(title="DIPEGANG JUKIR (SIMULASI)", start=12, keys=[[35.3, 7.5]], max=12, unit="juta", t=35.2, dur=.8,
       decimals=1, trim_zero=True, target_text="Rp12 jt − Rp4,5 jt"), None),
 ("Q12", "Kerja **pagi** sampai **malam**", [lb("JUKIR", "DARI PAGI", 37.45, "orange", "", 60, 1.3),
                                             lb("JUKIR", "SAMPAI MALAM", 38.0, "purple", "", 60)], None, None),
 ("Q13", "Panas, hujan, **tanpa BPJS**", [lb("PANAS", "PANAS", 38.65, "orange", "", 40),
                                          lb("HUJAN", "HUJAN", 38.95, "blue", "", 40),
                                          lb("BPJS", "TANPA BPJS", 39.55, "red", "", 50),
                                          lb("Q", "TANPA KEPASTIAN", 40.4, "red", "", 50)], None, None),
 ("Q14", "Yang mahal: **lokasinya**", [lb("JASA", "BUKAN JASANYA", 42.95, "red", "", 60, 2.7),
                                       lb("LOKASI", "LOKASINYA", 44.3, "green", "titik ramai", 60)], None, None),
 ("Q15", "Kuasai **titik ramai**", [lb("RAMAI", "TITIK RAMAI", 45.9, "orange", "", 60),
                                    lb("UANG", "KUASAI UANGNYA", 47.7, "green", "", 60)], None, None),
 ("Q16", "Ini **simulasi**", [lb("DOC", "ANGKA SIMULASI", 49.5, "red", "bukan data resmi", 60)], None, None),
 ("Q17", "Tiap lokasi **beda jauh**", [lb("RAMAI", "RAMAI", 50.9, "green", "", 50), lb("SEDANG", "SEDANG", 51.3, "orange", "", 50),
                                       lb("SEPI", "SEPI", 51.7, "red", "", 50)], None, None),
 ("Q18", "Siapa **paling untung**?", [lb("JUKIR", "JURU PARKIR?", 56.4, "orange", "", 60),
                                      lb("LAYAR", "ORANG DI BALIK LAYAR?", 58.1, "purple", "", 60)], None, None),
 ("Q19", "Tulis di **komentar**", [lb("STORE", "TULIS PENDAPATMU", 59.2, "orange", "di kolom komentar", 80)], None, None),
]
out = {"keywords": ["rompi", "peluit", "12", "cuan", "karyawannya", "hitung", "150", "20", "rp2.000", "rp5.000", "400",
                    "setoran", "pengelola", "4,5", "7,5", "pagi", "malam", "panas", "hujan", "bpjs", "kepastian",
                    "lokasinya", "titik", "uangnya", "simulasi", "beda", "jauh", "parkirnya", "layarnya", "komentar",
                    "follow", "bukan", "nggak"],
       "scenes": []}
for sid, bub, labels, hud, panels in S:
    t0 = TL[sid]
    sc = {"id": sid, "bubble": bub}
    if labels:
        sc["labels"] = [dict(l, t=round(l["t"] - t0, 2)) for l in labels]
    if hud:
        h = dict(HUD, **hud)
        h["t"] = round(h["t"] - t0, 2)
        if "keys" in h:
            h["keys"] = [[round(a - t0, 2), b] for a, b in h["keys"]]
        sc["hud"] = h
    if panels:
        for p in panels:
            p["row_t"] = [round(x - t0, 2) for x in p["row_t"]]
        sc["panels"] = panels
    if sid == "Q19":
        sc["cta"] = 0.2
    out["scenes"].append(sc)
json.dump(out, open("render/scenes/prk.json", "w"), ensure_ascii=False, indent=1)
print("ok", len(out["scenes"]))
