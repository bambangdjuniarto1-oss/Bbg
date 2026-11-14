// Kantor virtual 3D isometrik: gedung 3 lantai open-plan (18 kubikel per lantai, total 54 kursi).
//   Lantai 3: Ruang CEO, Ruang Rapat, Pantry   Lantai 2: Studio Produksi, Ruang Kreatif, Pantry
//   Lantai 1: Ruang Rapat Bisnis, Ruang Server, Pantry      Setiap lantai: Workspace + Lounge
// Divisi (kepala + spesialisnya) duduk berdekatan. Karakter bergerak sesuai status agent dari server.
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { CSS2DRenderer, CSS2DObject } from "three/addons/renderers/CSS2DRenderer.js";

// ---------- Denah (satuan meter) ----------
const X0 = -15, X1 = 15, Z0 = -11, Z1 = 11;
const JARAK_LANTAI = 24; // jarak vertikal antar lantai (gedung "dibuka" supaya isinya terlihat)
const JUMLAH_LANTAI = 3;
const KORIDOR_Z = -2.6;
const TINGGI_DINDING = 3.6;
const LORONG_X = [-8.4, -2.3, 3.9];
const BARIS = [
  { mejaZ: -0.3, lorongZ: 1.95 },
  { mejaZ: 3.5, lorongZ: 5.75 },
  { mejaZ: 7.3, lorongZ: 9.55 },
];
const KOLOM_KURSI = [-12.6, -10.3, -6.5, -4.2, -0.4, 1.9];
const KURSI_PER_LANTAI = BARIS.length * KOLOM_KURSI.length; // 18
const TEMA = [
  { nama: "Lantai 1 · Bisnis & Operasional", kiri: "rapat-bisnis", tengah: "server" },
  { nama: "Lantai 2 · Produksi & Audiens", kiri: "studio", tengah: "rapat-kreatif" },
  { nama: "Lantai 3 · Eksekutif & Strategi", kiri: "ceo", tengah: "rapat" },
];
const yLantai = (i) => i * JARAK_LANTAI;

// ---------- Renderer & scene ----------
const wadah = document.getElementById("scene");
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.toneMapping = THREE.NeutralToneMapping;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
wadah.appendChild(renderer.domElement);

const labelRenderer = new CSS2DRenderer();
Object.assign(labelRenderer.domElement.style, { position: "absolute", inset: "0", pointerEvents: "none" });
wadah.appendChild(labelRenderer.domElement);

const scene = new THREE.Scene();
const ISO_ARAH = new THREE.Vector3(1, 1.05, 1).normalize();
const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 600);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.minZoom = 0.3;
controls.maxZoom = 4;
controls.minPolarAngle = Math.PI * 0.18;
controls.maxPolarAngle = Math.PI * 0.36;
controls.screenSpacePanning = true;
camera.position.copy(ISO_ARAH).multiplyScalar(150);

scene.add(new THREE.HemisphereLight("#ffffff", "#b9c4d0", 1.6));
// Satu matahari dengan bayangan, ditempatkan khusus untuk lantai yang sedang dilihat
// (lantai di atasnya berada "di belakang" lampu, jadi tidak menutupi lantai ini).
const ARAH_MATAHARI = new THREE.Vector3(-14, 30, 18).normalize();
const matahari = new THREE.DirectionalLight("#fff6ea", 2.2);
matahari.castShadow = true;
matahari.shadow.mapSize.set(2048, 2048);
Object.assign(matahari.shadow.camera, { left: -24, right: 24, top: 24, bottom: -24, near: 0.5, far: 45 });
matahari.shadow.bias = -0.0004;
matahari.shadow.radius = 4;
scene.add(matahari, matahari.target);
function aturBayangan(i) {
  const pusat = new THREE.Vector3(0, yLantai(i), 0);
  matahari.target.position.copy(pusat);
  matahari.position.copy(pusat).addScaledVector(ARAH_MATAHARI, 23);
}

// ---------- Helper ----------
const mat = (color, extra = {}) => new THREE.MeshStandardMaterial({ color, roughness: 0.75, ...extra });
const glow = (color, intensity = 1.6) =>
  new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: intensity, roughness: 0.3 });
function tambah(m, parent, x, y, z) {
  m.position.set(x, y, z);
  m.castShadow = m.receiveShadow = true;
  parent.add(m);
  return m;
}
const kotak = (w, h, d, material, x = 0, y = 0, z = 0, parent = scene) =>
  tambah(new THREE.Mesh(new THREE.BoxGeometry(w, h, d), material), parent, x, y, z);
const silinder = (r, h, material, x, y, z, parent, seg = 16) =>
  tambah(new THREE.Mesh(new THREE.CylinderGeometry(r, r, h, seg), material), parent, x, y, z);
const bola = (r, material, x, y, z, parent) => tambah(new THREE.Mesh(new THREE.IcosahedronGeometry(r, 1), material), parent, x, y, z);
const v = (x, z, y = 0) => new THREE.Vector3(x, y, z);

function label(kelas, html, parent, x, y, z) {
  const el = document.createElement("div");
  el.className = kelas;
  el.innerHTML = html;
  const o = new CSS2DObject(el);
  o.position.set(x, y, z);
  parent.add(o);
  return el;
}

// ---------- Material ----------
const M = {
  putih: mat("#f7f7f5"),
  dinding: mat("#fbfbfa"),
  lantai: mat("#e4e7eb"),
  kayu: mat("#d8b48a"),
  kayuMeja: mat("#e3c39d"),
  abuMuda: mat("#ced3da"),
  kursi: mat("#8f98a5"),
  hitam: mat("#2a2d33"),
  akustik: mat("#3b3f4a"),
  daun: mat("#5aa84f"),
  daunTua: mat("#3f8a3d"),
  pot: mat("#f1f1ef"),
  kaca: new THREE.MeshPhysicalMaterial({ color: "#cfe6ff", transparent: true, opacity: 0.22, roughness: 0.05 }),
  rangka: mat("#4b5260", { metalness: 0.5, roughness: 0.4 }),
  jendela: mat("#9cc3e6", { roughness: 0.15, metalness: 0.1 }),
  buku: ["#c96b5b", "#5b8bc9", "#e0b354", "#6aa37a", "#9a7ec2"].map((c) => mat(c)),
};
const KARPET = {};
function teksturKarpet(dasar, a, b) {
  const kunci = dasar + a + b;
  if (KARPET[kunci]) return KARPET[kunci];
  const c = document.createElement("canvas");
  c.width = c.height = 256;
  const g = c.getContext("2d");
  g.fillStyle = dasar;
  g.fillRect(0, 0, 256, 256);
  let s = 3;
  const acak = () => ((s = (s * 16807) % 2147483647) / 2147483647);
  for (let i = 0; i < 900; i++) {
    g.fillStyle = acak() < 0.5 ? a : b;
    g.globalAlpha = 0.6;
    g.beginPath();
    g.arc(acak() * 256, acak() * 256, 1 + acak() * 2.4, 0, Math.PI * 2);
    g.fill();
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(3, 2);
  return (KARPET[kunci] = new THREE.MeshStandardMaterial({ map: t, roughness: 1 }));
}

// ---------- Furnitur ----------
function kursiKantor(g, x, z, rotY = 0) {
  const k = new THREE.Group();
  kotak(0.62, 0.1, 0.6, M.kursi, 0, 0.5, 0, k);
  kotak(0.62, 0.62, 0.1, M.kursi, 0, 0.84, 0.27, k);
  kotak(0.06, 0.45, 0.06, M.hitam, 0, 0.25, 0, k);
  kotak(0.55, 0.05, 0.55, M.hitam, 0, 0.04, 0, k);
  k.position.set(x, 0, z);
  k.rotation.y = rotY;
  g.add(k);
}
function rakBuku(g, x, z, w, rotY = 0) {
  const r = new THREE.Group();
  kotak(w, 2.2, 0.45, M.putih, 0, 1.1, 0, r);
  for (let i = 0; i < 4; i++) {
    let bx = -w / 2 + 0.15;
    while (bx < w / 2 - 0.3) {
      const bw = 0.08 + Math.random() * 0.1;
      const bh = 0.3 + Math.random() * 0.15;
      if (Math.random() < 0.8) kotak(bw, bh, 0.3, M.buku[Math.floor(Math.random() * 5)], bx, 0.25 + i * 0.52 + bh / 2, 0.06, r);
      bx += bw + 0.02;
    }
  }
  r.position.set(x, 0, z);
  r.rotation.y = rotY;
  g.add(r);
}
function sofaKecil(g, x, z, rotY = 0, warna = M.abuMuda) {
  const s = new THREE.Group();
  kotak(0.95, 0.45, 0.9, warna, 0, 0.3, 0, s);
  kotak(0.95, 0.6, 0.2, warna, 0, 0.75, 0.38, s);
  for (const sx of [-0.42, 0.42]) kotak(0.14, 0.35, 0.9, warna, sx, 0.62, 0, s);
  s.position.set(x, 0, z);
  s.rotation.y = rotY;
  g.add(s);
}
function tanamanPot(g, x, z, s = 1) {
  silinder(0.28 * s, 0.5 * s, M.pot, x, 0.25 * s, z, g);
  bola(0.45 * s, M.daunTua, x, 0.85 * s, z, g);
  bola(0.32 * s, M.daun, x + 0.18 * s, 1.15 * s, z - 0.1 * s, g);
}
function pohon(g, x, z, s = 1, y = 0) {
  silinder(0.08 * s, 0.9 * s, M.kayu, x, y + 0.45 * s, z, g, 8);
  bola(0.75 * s, M.daun, x, y + 1.35 * s, z, g);
}
const LAYAR_MATI = "#8fbbe8";
const LAYAR_NYALA = "#2f8cff";
function monitorGanda(g, x, z) {
  const mats = [];
  for (const dx of [-0.36, 0.36]) {
    const m = glow(LAYAR_MATI, 0.45);
    kotak(0.68, 0.44, 0.05, M.hitam, x + dx, 1.33, z, g);
    kotak(0.62, 0.38, 0.02, m, x + dx, 1.33, z + 0.03, g);
    mats.push(m);
  }
  kotak(0.06, 0.25, 0.06, M.hitam, x, 1.0, z - 0.03, g);
  kotak(0.5, 0.03, 0.12, M.abuMuda, x, 0.79, z + 0.35, g);
  return mats;
}
function pagarKaca(g, x, z, panjang, sumbuX) {
  const h = 1.1;
  const n = Math.round(panjang / 2.5);
  const [w, d] = sumbuX ? [panjang, 0.04] : [0.04, panjang];
  kotak(w, h, d, M.kaca, x, h / 2 + 0.05, z, g).castShadow = false;
  kotak(sumbuX ? panjang : 0.09, 0.06, sumbuX ? 0.09 : panjang, M.rangka, x, h + 0.05, z, g);
  for (let i = 0; i <= n; i++) {
    const t = -panjang / 2 + (i * panjang) / n;
    kotak(0.07, h, 0.07, M.rangka, sumbuX ? x + t : x, h / 2 + 0.05, sumbuX ? z : z + t, g);
  }
}
function jendela(g, x, z, w, sumbuX) {
  if (sumbuX) {
    kotak(w, 2.1, 0.06, M.jendela, x, 1.85, z + 0.2, g);
    for (let i = 0; i <= 3; i++) kotak(0.07, 2.2, 0.08, M.putih, x - w / 2 + (i * w) / 3, 1.85, z + 0.24, g);
  } else {
    kotak(0.06, 2.1, w, M.jendela, x + 0.2, 1.85, z, g);
    for (let i = 0; i <= 3; i++) kotak(0.08, 2.2, 0.07, M.putih, x + 0.24, 1.85, z - w / 2 + (i * w) / 3, g);
  }
}
function sekatKaca(g) {
  // sekat kaca ruang belakang (kiri dan tengah)
  kotak(0.08, 2.6, 6.2, M.kaca, -6.4, 1.3, -7.9, g).castShadow = false;
  kotak(5.6, 2.6, 0.08, M.kaca, -12.2, 1.3, -3.9, g).castShadow = false;
  kotak(0.1, 0.08, 6.2, M.rangka, -6.4, 2.62, -7.9, g);
  kotak(5.6, 0.08, 0.1, M.rangka, -12.2, 2.62, -3.9, g);
  kotak(0.08, 2.6, 6.2, M.kaca, 4.6, 1.3, -7.9, g).castShadow = false;
}
function mejaRapat(g, cx, cz, karpet) {
  kotak(9.6, 0.05, 6.2, karpet, cx, 0.05, cz, g);
  kotak(6.2, 0.1, 1.8, M.putih, cx, 0.78, cz - 0.1, g);
  for (const dx of [-2.6, 2.6]) kotak(0.12, 0.74, 1.4, M.putih, cx + dx, 0.38, cz - 0.1, g);
  for (const dx of [-2.2, -0.8, 0.6, 2]) {
    kursiKantor(g, cx + dx, cz - 1.4, Math.PI);
    kursiKantor(g, cx + dx, cz + 1.2);
  }
}

// Ruang-ruang khusus di sisi belakang
const RUANG = {
  ceo(g) {
    kotak(8.6, 0.05, 7.2, M.kayu, -10.7, 0.045, -7.4, g);
    kotak(3, 0.1, 1.3, M.kayuMeja, -10.8, 0.8, -8.4, g);
    kotak(3, 0.75, 0.08, M.putih, -10.8, 0.4, -8.95, g);
    const layar = monitorGanda(g, -10.8, -8.65);
    kursiKantor(g, -10.8, -7.4);
    sofaKecil(g, -14.1, -5.4, -Math.PI / 2);
    rakBuku(g, -8.2, -10.55, 3);
    tanamanPot(g, -14.2, -10.2, 1.1);
    return { nama: "Ruang CEO", layar };
  },
  rapat(g) {
    mejaRapat(g, -0.6, -7.5, teksturKarpet("#9fb9d6", "#c7d8ea", "#7f9dc0"));
    kotak(2.4, 1.4, 0.06, M.hitam, -0.6, 1.9, -10.75, g);
    kotak(2.25, 1.25, 0.02, glow("#cfe3ff", 0.6), -0.6, 1.9, -10.71, g);
    tanamanPot(g, 3.9, -10.2, 1.2);
    return { nama: "Ruang Rapat" };
  },
  "rapat-kreatif"(g) {
    mejaRapat(g, -0.6, -7.5, teksturKarpet("#e9b7a2", "#f6d5c6", "#d38f78"));
    kotak(3.2, 1.6, 0.06, M.putih, -0.6, 1.9, -10.75, g); // papan ide
    for (let i = 0; i < 12; i++) {
      const warna = ["#ffe066", "#ffadad", "#a0e7e5", "#b4f8c8"][i % 4];
      kotak(0.3, 0.3, 0.02, mat(warna), -1.9 + (i % 6) * 0.5, 2.2 - Math.floor(i / 6) * 0.5, -10.71, g);
    }
    return { nama: "Ruang Kreatif" };
  },
  "rapat-bisnis"(g) {
    kotak(8.6, 0.05, 7.2, M.kayu, -10.7, 0.045, -7.4, g);
    kotak(4.4, 0.1, 1.6, M.kayuMeja, -10.7, 0.78, -7.4, g);
    for (const dx of [-1.6, 1.6]) kotak(0.12, 0.74, 1.2, M.putih, -10.7 + dx, 0.38, -7.4, g);
    for (const dx of [-1.4, 0, 1.4]) {
      kursiKantor(g, -10.7 + dx, -8.6, Math.PI);
      kursiKantor(g, -10.7 + dx, -6.2);
    }
    kotak(2.2, 1.3, 0.06, M.hitam, -10.7, 1.9, -10.75, g);
    kotak(2.05, 1.15, 0.02, glow("#d7f5e3", 0.6), -10.7, 1.9, -10.71, g);
    tanamanPot(g, -14.2, -4.6, 1);
    return { nama: "Ruang Rapat Bisnis" };
  },
  studio(g) {
    // studio rekaman/produksi: dinding akustik gelap, meja mixer, mic, speaker, kamera
    kotak(8.6, 0.05, 7.2, mat("#55505a"), -10.7, 0.045, -7.4, g);
    for (let i = 0; i < 6; i++) kotak(1.2, 1.2, 0.08, M.akustik, -14 + i * 1.3, 1.9, -10.7, g);
    kotak(3.2, 0.12, 1.1, M.hitam, -10.8, 0.85, -8.6, g);
    for (let i = 0; i < 10; i++) kotak(0.12, 0.05, 0.6, glow(i % 3 ? "#7dd3fc" : "#fda4af", 1.2), -12.1 + i * 0.28, 0.93, -8.6, g);
    for (const dx of [-1.9, 1.9]) kotak(0.5, 0.9, 0.5, M.hitam, -10.8 + dx, 1.35, -9.4, g);
    silinder(0.03, 1.5, M.rangka, -9.2, 0.75, -6, g, 8);
    bola(0.13, M.hitam, -9.2, 1.55, -6, g);
    silinder(0.03, 1.3, M.rangka, -13, 0.65, -5.5, g, 8);
    kotak(0.5, 0.35, 0.35, M.hitam, -13, 1.45, -5.5, g);
    kursiKantor(g, -10.8, -7.6);
    return { nama: "Studio Produksi" };
  },
  server(g) {
    kotak(10.8, 0.05, 6.8, mat("#d4dae2"), -0.9, 0.045, -7.4, g);
    const lampu = [];
    for (let r = 0; r < 4; r++) {
      const x = -4.2 + r * 2.2;
      kotak(1.3, 2.4, 0.9, M.hitam, x, 1.2, -9.6, g);
      for (let i = 0; i < 8; i++) {
        const m = glow(i % 2 ? "#22c55e" : "#38bdf8", 2);
        kotak(0.08, 0.05, 0.02, m, x - 0.4 + (i % 4) * 0.25, 0.5 + Math.floor(i / 4) * 1.1 + r * 0.1, -9.14, g);
        lampu.push(m);
      }
    }
    kotak(2.4, 0.1, 1, M.putih, -0.6, 0.78, -6.2, g);
    monitorGanda(g, -0.6, -6.5);
    return { nama: "Ruang Server", lampu };
  },
};

// ---------- Bangun satu lantai ----------
const lampuServer = [];
function bangunLantai(idx) {
  const tema = TEMA[idx];
  const g = new THREE.Group();
  g.position.y = yLantai(idx);
  scene.add(g);

  kotak(X1 - X0 + 0.6, 0.8, Z1 - Z0 + 0.6, M.putih, 0, -0.4, 0, g);
  kotak(X1 - X0, 0.04, Z1 - Z0, M.lantai, 0, 0.02, 0, g);
  kotak(8.2, 0.05, 12.6, M.kayu, 10.9, 0.045, 4.4, g); // lounge

  // dinding belakang & kiri dengan jendela
  kotak(X1 - X0 + 0.35, TINGGI_DINDING, 0.35, M.dinding, 0.17, TINGGI_DINDING / 2, Z0 - 0.17, g);
  kotak(0.35, TINGGI_DINDING, Z1 - Z0, M.dinding, X0 - 0.17, TINGGI_DINDING / 2, 0, g);
  jendela(g, 1.5, Z0, 3.6, true);
  jendela(g, 10, Z0, 3.2, true);
  jendela(g, X0, 2.5, 4.5, false);
  jendela(g, X0, 8, 3.6, false);

  // pagar kaca + bedeng tanaman
  pagarKaca(g, 0, Z1, X1 - X0, true);
  pagarKaca(g, X1, 0, Z1 - Z0, false);
  kotak(X1 - X0, 0.35, 1, M.putih, 0, 0.17, Z1 + 0.85, g);
  kotak(1, 0.35, Z1 - Z0 + 2, M.putih, X1 + 0.85, 0.17, 0.5, g);
  kotak(X1 - X0 - 0.2, 0.05, 0.8, M.daunTua, 0, 0.37, Z1 + 0.85, g);
  kotak(0.8, 0.05, Z1 - Z0 + 1.8, M.daunTua, X1 + 0.85, 0.37, 0.5, g);
  for (const x of [-12, -4, 4, 12]) pohon(g, x, Z1 + 0.85, 0.9, 0.35);
  for (const z of [-7, 1, 8]) pohon(g, X1 + 0.85, z, 0.9, 0.35);

  // kubikel: urutan kursi per pod (6 kursi) supaya satu divisi duduk berdekatan
  const kursi = [];
  for (let p = 0; p < 3; p++) {
    const xa = KOLOM_KURSI[p * 2], xb = KOLOM_KURSI[p * 2 + 1];
    const cx = (xa + xb) / 2;
    for (const [bi, b] of BARIS.entries()) {
      kotak(4.9, 1.25, 0.1, M.putih, cx, 0.62, b.mejaZ - 0.55, g);
      for (const sx of [-2.45, 0, 2.45]) kotak(0.1, 1.25, 1.5, M.putih, cx + sx, 0.62, b.mejaZ + 0.2, g);
      for (const x of [xa, xb]) {
        kotak(2.15, 0.07, 1, M.kayuMeja, x, 0.76, b.mejaZ, g);
        kotak(0.06, 0.74, 0.9, M.putih, x - 1.0, 0.38, b.mejaZ, g);
        const layar = monitorGanda(g, x, b.mejaZ - 0.3);
        kursiKantor(g, x, b.mejaZ + 1.05);
        kursi.push({ x, z: b.mejaZ + 1.05, baris: bi, layar, lantai: idx });
      }
    }
  }
  tanamanPot(g, -14.2, 1.95, 0.8);
  tanamanPot(g, 5.6, 5.75, 0.9);

  // ruang belakang
  sekatKaca(g);
  const kiri = RUANG[tema.kiri](g);
  const tengah = RUANG[tema.tengah](g);
  if (kiri.lampu) lampuServer.push(...kiri.lampu);
  if (tengah.lampu) lampuServer.push(...tengah.lampu);
  label("label-lantai", kiri.nama, g, -10.6, 3.1, -7);
  label("label-lantai", tengah.nama, g, -0.6, 3.1, -7.5);

  // pantry
  kotak(5.5, 0.95, 0.8, M.putih, 9.9, 0.48, -10.4, g);
  kotak(5.5, 0.06, 0.85, M.abuMuda, 9.9, 0.98, -10.4, g);
  kotak(0.5, 0.6, 0.45, M.hitam, 8, 1.3, -10.45, g);
  kotak(0.12, 0.08, 0.02, glow("#5dffa0", 2), 8, 1.4, -10.2, g);
  kotak(1, 2.2, 0.8, M.abuMuda, 13.6, 1.1, -10.4, g);
  kotak(1.2, 0.08, 1.2, M.putih, 9.5, 0.75, -7.2, g);
  silinder(0.08, 0.72, M.putih, 9.5, 0.37, -7.2, g, 8);
  for (const [dx, dz] of [[-0.9, 0], [0.9, 0], [0, 0.9]]) silinder(0.25, 0.5, M.kursi, 9.5 + dx, 0.25, -7.2 + dz, g);

  // lounge: sofa berhadapan, meja kopi, meja bar, rak buku
  for (const [i, [x, z]] of [[8.6, 1.2], [10.6, 1.2], [12.6, 1.2], [8.6, 5.8], [10.6, 5.8], [12.6, 5.8]].entries()) {
    sofaKecil(g, x, z, i < 3 ? Math.PI : 0);
  }
  kotak(5, 0.08, 1.1, M.kayuMeja, 10.6, 0.45, 3.5, g);
  for (const dx of [-2.2, 2.2]) kotak(0.1, 0.42, 0.9, M.putih, 10.6 + dx, 0.22, 3.5, g);
  kotak(5.2, 0.08, 0.6, M.kayuMeja, 10.4, 1.05, 9.1, g);
  for (const dx of [-2.3, 0, 2.3]) silinder(0.06, 1.02, M.rangka, 10.4 + dx, 0.51, 9.1, g, 8);
  rakBuku(g, 14.6, -1.2, 2.4, -Math.PI / 2);
  tanamanPot(g, 7.4, 10.3, 0.9);

  const santai = [
    [8.6, 2.3], [10.6, 4.7], [12.6, 2.3], [8.6, 4.7], [10.6, 2.3], [12.6, 4.7],
    [8.2, 8.3], [9.7, 9.9], [11.2, 8.3], [12.7, 9.9], [12.7, 8.3], [8.2, 9.9],
    [8.2, -6.1], [10.8, -6.1], [11.6, -9.3], [12.6, -9.3], [9.5, -5.6], [6.8, -8.6],
  ].map(([x, z], i) => ({ x, z, pantry: i >= 12 }));

  const elJudul = label("label-gedung", tema.nama, g, X1 - 2, 1.2, Z1 + 2.2);
  return { g, kursi, santai, layarCeo: kiri.layar, elJudul, idx };
}

const LANTAI = Array.from({ length: JUMLAH_LANTAI }, (_, i) => bangunLantai(i));
const ATAS = JUMLAH_LANTAI - 1;

// Kolom sudut dan lift kaca yang menghubungkan lantai
const tinggiGedung = yLantai(ATAS) + TINGGI_DINDING;
// tiang sudut hanya tampil saat melihat seluruh gedung (supaya tidak menghalangi tampilan satu lantai)
const struktur = new THREE.Group();
scene.add(struktur);
for (const [x, z] of [[X0 - 0.2, Z0 - 0.2], [X1 + 0.2, Z0 - 0.2], [X0 - 0.2, Z1 + 0.2], [X1 + 0.2, Z1 + 0.2]]) {
  kotak(0.35, tinggiGedung, 0.35, M.putih, x, tinggiGedung / 2, z, struktur);
}
kotak(2.6, tinggiGedung + 1, 2.6, M.kaca, X1 + 3.2, (tinggiGedung + 1) / 2, Z0 + 2.2).castShadow = false;
for (const [dx, dz] of [[-1.3, -1.3], [1.3, -1.3], [-1.3, 1.3], [1.3, 1.3]]) {
  kotak(0.1, tinggiGedung + 1, 0.1, M.rangka, X1 + 3.2 + dx, (tinggiGedung + 1) / 2, Z0 + 2.2 + dz);
}
const lift = kotak(2.2, 2.6, 2.2, mat("#e8edf3"), X1 + 3.2, 1.3, Z0 + 2.2);

// ---------- Karakter voxel ----------
const matKulit = mat("#f0c8a4");
const matMata = mat("#1d1d1d");
const matCelana = mat("#4a5568");
const RAMBUT = ["#2b1b12", "#5a3825", "#111111", "#7b4a2a", "#3a2a20", "#a0522d"];

function buatKarakter(info, i) {
  const g = new THREE.Group();
  const baju = mat(info.warna);
  const rambut = mat(RAMBUT[i % RAMBUT.length]);
  const kaki = [];
  for (const sx of [-0.13, 0.13]) {
    const pivot = new THREE.Group();
    pivot.position.set(sx, 0.58, 0);
    kotak(0.22, 0.58, 0.26, matCelana, 0, -0.29, 0, pivot);
    g.add(pivot);
    kaki.push(pivot);
  }
  kotak(0.56, 0.66, 0.34, baju, 0, 0.91, 0, g);
  const lengan = [];
  for (const sx of [-0.37, 0.37]) {
    const pivot = new THREE.Group();
    pivot.position.set(sx, 1.18, 0);
    kotak(0.17, 0.56, 0.2, baju, 0, -0.25, 0, pivot);
    kotak(0.15, 0.11, 0.18, matKulit, 0, -0.57, 0, pivot);
    g.add(pivot);
    lengan.push(pivot);
  }
  kotak(0.5, 0.5, 0.46, matKulit, 0, 1.5, 0, g);
  kotak(0.54, 0.15, 0.5, rambut, 0, 1.8, 0, g);
  kotak(0.54, 0.36, 0.1, rambut, 0, 1.62, -0.21, g);
  for (const sx of [-0.11, 0.11]) kotak(0.07, 0.09, 0.02, matMata, sx, 1.53, 0.24, g);
  if (info.id === "bos") kotak(0.11, 0.38, 0.02, mat("#c0392b"), 0, 0.91, 0.18, g);
  else if (!info.atasan && info.punyaTim) kotak(0.4, 0.06, 0.36, mat("#f5b041"), 0, 1.9, 0, g); // penanda kepala divisi

  const el = document.createElement("div");
  el.className = "label3d";
  el.innerHTML = `<span class="bubble"></span><span class="tag"><i></i>${esc(info.nama)}</span>`;
  const lbl = new CSS2DObject(el);
  lbl.position.set(0, 2.2, 0);
  g.add(lbl);
  scene.add(g);
  return { g, kaki, lengan, el, bubble: el.querySelector(".bubble"), jalur: [], fase: Math.random() * 6, bubbleSampai: 0, spot: null };
}

// ---------- Titik tujuan & rute (selalu di lantai yang sama) ----------
const lorongTerdekat = (x) => LORONG_X.reduce((a, b) => (Math.abs(b - x) < Math.abs(a - x) ? b : a));

function spotKursi(k) {
  const y = yLantai(k.lantai);
  const lz = BARIS[k.baris].lorongZ;
  const lx = lorongTerdekat(k.x);
  return { lantai: k.lantai, pos: v(k.x, k.z, y), hadap: Math.PI, keluar: [v(k.x, lz, y), v(lx, lz, y), v(lx, KORIDOR_Z, y)] };
}
function spotSantai(s, lantai) {
  const y = yLantai(lantai);
  if (s.pantry) return { lantai, pos: v(s.x, s.z, y), hadap: s.z < -8 ? Math.PI : 0, keluar: [v(s.x, KORIDOR_Z - 1.2, y), v(s.x, KORIDOR_Z, y)] };
  const tepi = s.x > 11 ? 14 : 7.2;
  return { lantai, pos: v(s.x, s.z, y), hadap: s.z < 3.5 || (s.z > 8 && s.z < 9) ? 0 : Math.PI, keluar: [v(tepi, s.z, y), v(tepi, KORIDOR_Z, y)] };
}
const yA = yLantai(ATAS);
const SPOT_CEO_MEJA = { lantai: ATAS, pos: v(-10.8, -7.4, yA), hadap: Math.PI, keluar: [v(-8, -6, yA), v(-8, KORIDOR_Z, yA)] };
const SPOT_CEO_SANTAI = { lantai: ATAS, pos: v(-12.8, -5.4, yA), hadap: Math.PI / 2, keluar: [v(-8, -6, yA), v(-8, KORIDOR_Z, yA)] };

const kursiAgent = {};
const santaiAgent = {};
const tujuan = (id, status) =>
  id === "bos" ? (status === "idle" ? SPOT_CEO_SANTAI : SPOT_CEO_MEJA) : status === "idle" ? santaiAgent[id] : kursiAgent[id];
const rute = (dari, ke) => (dari === ke ? [] : [...dari.keluar, ...[...ke.keluar].reverse(), ke.pos].map((p) => p.clone()));

// Bagi agent ke kursi: divisi (kepala + spesialis) duduk berdekatan, lantai atas diisi lebih dulu.
function aturTempatDuduk(agents) {
  const tim = agents.filter((a) => a.id !== "bos");
  const kelompok = tim.filter((a) => !a.atasan).map((k) => [k, ...tim.filter((x) => x.atasan === k.id)]);
  const yatim = tim.filter((a) => a.atasan && !tim.some((k) => k.id === a.atasan));
  if (yatim.length) kelompok.push(yatim);
  const urutanLantai = Array.from({ length: JUMLAH_LANTAI }, (_, i) => ATAS - i);
  const terisi = urutanLantai.map(() => 0);
  const hasil = []; // { lantai, kursi, kelompok }
  let f = 0;
  for (const grup of kelompok) {
    let ditempatkan = false;
    for (; f < urutanLantai.length && !ditempatkan; ) {
      const rataPod = Math.ceil(terisi[f] / 6) * 6;
      const mulai = rataPod + grup.length <= KURSI_PER_LANTAI ? rataPod : terisi[f] + grup.length <= KURSI_PER_LANTAI ? terisi[f] : -1;
      if (mulai < 0) {
        f++;
        continue;
      }
      grup.forEach((a, j) => hasil.push({ a, lantai: urutanLantai[f], kursi: mulai + j, grup }));
      terisi[f] = mulai + grup.length;
      ditempatkan = true;
    }
    if (!ditempatkan) {
      // kelompok terlalu besar: isi kursi kosong mana saja
      for (const a of grup) {
        const fi = terisi.findIndex((n) => n < KURSI_PER_LANTAI);
        if (fi < 0) break;
        hasil.push({ a, lantai: urutanLantai[fi], kursi: terisi[fi]++, grup });
      }
    }
  }
  const santaiTerpakai = {};
  for (const { a, lantai, kursi } of hasil) {
    const L = LANTAI[lantai];
    const k = L.kursi[kursi];
    kursiAgent[a.id] = spotKursi(k);
    layar[a.id] = k.layar;
    const n = (santaiTerpakai[lantai] = (santaiTerpakai[lantai] ?? -1) + 1);
    santaiAgent[a.id] = spotSantai(L.santai[n % L.santai.length], lantai);
  }
  // label nama divisi di atas klaster kubikelnya
  for (const grup of kelompok) {
    if (grup.length < 2) continue;
    const kursiGrup = hasil.filter((h) => h.grup === grup).map((h) => LANTAI[h.lantai].kursi[h.kursi]);
    if (!kursiGrup.length) continue;
    const cx = kursiGrup.reduce((s, k) => s + k.x, 0) / kursiGrup.length;
    const cz = Math.min(...kursiGrup.map((k) => k.z)) - 1.6;
    label("label-divisi", `Divisi ${esc(grup[0].jabatan)}`, LANTAI[kursiGrup[0].lantai].g, cx, 2.7, cz);
  }
}

// ---------- Paket tugas yang terbang dari atasan ke agent ----------
const paket = [];
function kirimPaket(dariId, keId, warna) {
  const a = aktor[dariId], b = aktor[keId];
  if (!a || !b) return;
  const m = kotak(0.3, 0.4, 0.05, glow(warna, 2.5), 0, 0, 0);
  paket.push({ m, dari: a.g.position.clone().add(v(0, 0, 2)), ke: b, t: 0 });
}

// ---------- State UI ----------
const elChat = document.getElementById("chat");
const elKartu = document.getElementById("kartu-agent");
const elToken = document.getElementById("token");
const elMode = document.getElementById("mode");
const elKirim = document.getElementById("kirim");
let AGENTS = [];
const aktor = {};
const infoAgent = {};
const statusAgent = {};
const layar = {};

function esc(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
function linkify(teks, slug) {
  return esc(teks)
    .replace(/(https?:\/\/[^\s)]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>')
    .replace(/(^|\s)(\/files\/[^\s)]+)/g, '$1<a href="$2" target="_blank">$2</a>')
    .replace(/(^|[\s(])(output\/[\w./-]+)/g, (m, pre, p) =>
      slug ? `${pre}<a href="/files/${slug}/${p}" target="_blank">${p}</a>` : m);
}
let slugAktif = "";

const jam = (t) => new Date(t ?? Date.now()).toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit" });
const gulirBawah = () => (elChat.scrollTop = elChat.scrollHeight);
function tambahSistem(html) {
  const li = document.createElement("li");
  li.className = "sistem";
  li.innerHTML = html;
  elChat.appendChild(li);
  gulirBawah();
}
function tambahChat(ev) {
  const a = infoAgent[ev.from] ?? { nama: ev.from, jabatan: "", warna: "#888" };
  const li = document.createElement("li");
  li.className = "msg" + (ev.final ? " final" : "") + (ev.error ? " error" : "");
  const galeri = ev.images?.length
    ? `<div class="galeri">${ev.images.map((src) => `<a href="${esc(src)}" target="_blank"><img src="${esc(src)}" alt="" loading="lazy"></a>`).join("")}</div>`
    : "";
  li.innerHTML = `<div class="ava" style="background:${a.warna}">${esc(a.nama[0])}</div>
    <div class="isi"><div class="siapa"><span>${esc(a.nama)} <small>${esc(a.jabatan)}</small></span><small>${jam(ev.t)}</small></div>
    <div class="teks">${linkify(ev.text, ev.klien || slugAktif)}</div>${galeri}</div>`;
  elChat.appendChild(li);
  gulirBawah();
}

// Kartu status: bos + agent yang sedang bekerja (tim besar tidak muat semua di layar)
function renderKartu() {
  const aktif = AGENTS.filter((a) => a.id === "bos" || statusAgent[a.id]?.status !== "idle");
  const tampil = AGENTS.length <= 9 ? AGENTS : aktif.slice(0, 9);
  const kartu = tampil.map((a) => {
    const s = statusAgent[a.id] ?? { status: "idle", aktivitas: "" };
    const teks = s.status === "idle" ? (a.id === "bos" ? "standby di ruang CEO" : "santai di lounge") : s.aktivitas || "bekerja";
    return `<div class="kartu" data-status="${s.status}"><span class="dot" style="background:${a.warna}"></span>
      <span class="nama">${esc(a.nama)} <small>${esc(a.jabatan)}</small></span><span class="akt">${esc(teks)}</span></div>`;
  });
  const tim = AGENTS.filter((a) => a.id !== "bos");
  const kerja = tim.filter((a) => statusAgent[a.id]?.status !== "idle").length;
  if (AGENTS.length > 9) {
    const lebih = aktif.length - tampil.length;
    kartu.push(`<div class="kartu ringkas"><span class="nama">${kerja} bekerja · ${tim.length - kerja} santai${lebih > 0 ? ` · +${lebih} lainnya` : ""}</span></div>`);
  }
  elKartu.innerHTML = kartu.join("");
  for (const L of LANTAI) {
    const diLantai = tim.filter((a) => kursiAgent[a.id]?.lantai === L.idx);
    const k = diLantai.filter((a) => statusAgent[a.id]?.status !== "idle").length;
    L.elJudul.innerHTML = `${TEMA[L.idx].nama} <small>· ${diLantai.length} agent${diLantai.length ? ` · ${k} kerja` : ""}</small>`;
  }
}

function tampilkanBubble(id, teks, durasi = 4500) {
  const ak = aktor[id];
  if (!ak) return;
  ak.bubble.textContent = teks.length > 70 ? teks.slice(0, 67) + "…" : teks;
  ak.bubble.classList.add("on");
  ak.bubbleSampai = performance.now() + durasi;
}

function nyalakanLayar(id, nyala) {
  for (const m of layar[id] ?? []) {
    m.color.set(nyala ? LAYAR_NYALA : LAYAR_MATI);
    m.emissive.set(nyala ? LAYAR_NYALA : LAYAR_MATI);
    m.emissiveIntensity = nyala ? 1.8 : 0.45;
  }
}

function setStatus(id, status, aktivitas, instan = false) {
  statusAgent[id] = { status, aktivitas };
  const ak = aktor[id];
  if (!ak) return;
  ak.el.dataset.status = status;
  nyalakanLayar(id, status !== "idle");
  if (aktivitas && status !== "idle") tampilkanBubble(id, aktivitas, 6000);
  const t = tujuan(id, status);
  if (!t) return;
  if (instan || !ak.spot) {
    ak.g.position.copy(t.pos);
    ak.g.rotation.y = t.hadap;
    ak.jalur = [];
    ak.spot = t;
  } else if (ak.spot !== t) {
    ak.jalur.push(...rute(ak.spot, t));
    ak.spot = t;
  }
  jadwalRenderKartu();
}
let antreKartu = false;
function jadwalRenderKartu() {
  if (antreKartu) return;
  antreKartu = true;
  requestAnimationFrame(() => {
    antreKartu = false;
    renderKartu();
  });
}

// ---------- Event dari server ----------
function tanganiEvent(ev, replay = false) {
  switch (ev.type) {
    case "status":
      setStatus(ev.agent, ev.status, ev.aktivitas);
      break;
    case "chat":
      tambahChat(ev);
      if (!replay) tampilkanBubble(ev.from, ev.text.split("\n")[0]);
      if (ev.final || ev.error) elKirim.disabled = false;
      break;
    case "brief":
      slugAktif = ev.slug;
      elToken.textContent = "0 token";
      tambahSistem(`📝 Brief baru untuk <b>${esc(ev.klien)}</b>`);
      if (!replay) elKirim.disabled = true;
      break;
    case "delegasi": {
      const ke = infoAgent[ev.to];
      tambahSistem(`📨 ${esc(infoAgent[ev.from]?.nama ?? ev.from)} → ${esc(ke?.nama ?? ev.to)}: ${esc(ev.tugas.slice(0, 90))}${ev.tugas.length > 90 ? "…" : ""}`);
      if (!replay) kirimPaket(ev.from, ev.to, ke?.warna ?? "#fff");
      break;
    }
    case "file":
      tambahSistem(`📄 ${esc(infoAgent[ev.agent]?.nama ?? ev.agent)} menyimpan <a href="${esc(ev.url)}" target="_blank">${esc(ev.path)}</a>`);
      break;
    case "usage":
      elToken.textContent = `${(ev.input + ev.output).toLocaleString("id-ID")} token`;
      break;
    case "selesai":
      elKirim.disabled = false;
      tambahSistem(ev.error ? "⛔ Pekerjaan berhenti karena error" : "✅ Pekerjaan selesai");
      break;
  }
}

async function perbaruiMode() {
  const i = await fetch("/api/info").then((r) => r.json()).catch(() => null);
  if (!i) return;
  elMode.textContent = i.demo ? "Mode DEMO" : `LIVE · ${i.provider}`;
  elMode.className = "pill " + (i.demo ? "demo" : "live");
  document.getElementById("banner-demo").hidden = !i.demo;
}
document.getElementById("banner-hubungkan").addEventListener("click", () => document.getElementById("buka-pengaturan").click());

function sambung() {
  const ws = new WebSocket(`${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/ws`);
  ws.onmessage = (m) => {
    const ev = JSON.parse(m.data);
    if (ev.type === "tim-berubah") return location.reload();
    if (ev.type === "pengaturan-berubah") return perbaruiMode();
    if (ev.type === "init") {
      elChat.innerHTML = "";
      perbaruiMode();
      for (const r of ev.riwayat) tanganiEvent(r, true);
      for (const [id, s] of Object.entries(ev.statusAgent)) setStatus(id, s.status, s.aktivitas, true);
      elKirim.disabled = Object.values(ev.statusAgent).some((s) => s.status !== "idle");
      if (!ev.riwayat.length) tambahSistem("Kirim brief di bawah. Bos akan membagi tugas ke tim.");
      return;
    }
    tanganiEvent(ev);
  };
  ws.onclose = () => setTimeout(sambung, 1500);
}

// ---------- Form brief ----------
document.getElementById("form-brief").addEventListener("submit", async (e) => {
  e.preventDefault();
  const klien = document.getElementById("klien").value.trim();
  const brief = document.getElementById("brief").value.trim();
  if (!klien || !brief) return;
  elKirim.disabled = true;
  const res = await fetch("/api/brief", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ klien, brief }),
  }).then((r) => r.json()).catch(() => ({ ok: false, error: "Server tidak bisa dihubungi" }));
  if (!res.ok) {
    tambahSistem(`⚠️ ${esc(res.error)}`);
    elKirim.disabled = false;
  } else {
    document.getElementById("brief").value = "";
  }
});

// ---------- Kamera: seluruh gedung atau satu lantai ----------
let fokus = null; // null = seluruh gedung, atau indeks lantai
const ZOOM_GEDUNG = 0.42;
function tampilkanLantai(i) {
  fokus = i;
  for (const L of LANTAI) L.g.visible = i === null || L.idx === i;
  struktur.visible = i === null;
  for (const [id, ak] of Object.entries(aktor)) ak.g.visible = i === null || (ak.spot?.lantai ?? ATAS) === i;
  aturBayangan(i ?? ATAS);
}
let terbang = null;
function terbangKe(target, zoom) {
  terbang = { tar0: controls.target.clone(), zoom0: camera.zoom, target, zoom, t: 0 };
}
document.querySelectorAll(".kamera button").forEach((b) =>
  b.addEventListener("click", () => {
    document.querySelectorAll(".kamera button").forEach((x) => x.classList.toggle("aktif", x === b));
    const cam = b.dataset.cam;
    if (cam === "gedung") {
      tampilkanLantai(null);
      terbangKe(v(0, 0, yLantai(1) + 1), ZOOM_GEDUNG);
    } else {
      const i = Number(cam);
      tampilkanLantai(i);
      terbangKe(v(-1, 0, yLantai(i)), 1);
    }
  }),
);

// ---------- Loop animasi ----------
const jamAnim = new THREE.Clock();
function animasi() {
  const dt = Math.min(jamAnim.getDelta(), 0.2);
  const now = performance.now();

  for (const [id, ak] of Object.entries(aktor)) {
    ak.fase += dt * 9;
    const titik = ak.jalur[0];
    if (titik) {
      const arah = titik.clone().sub(ak.g.position);
      const jarak = arah.length();
      const langkah = 4.2 * dt;
      if (jarak <= langkah) {
        ak.g.position.copy(titik);
        ak.jalur.shift();
      } else {
        ak.g.position.addScaledVector(arah.normalize(), langkah);
        ak.g.rotation.y = Math.atan2(arah.x, arah.z);
      }
      const ayun = Math.sin(ak.fase) * 0.6;
      ak.kaki[0].rotation.x = ayun;
      ak.kaki[1].rotation.x = -ayun;
      ak.lengan[0].rotation.x = -ayun;
      ak.lengan[1].rotation.x = ayun;
    } else {
      const hadap = ak.spot?.hadap ?? 0;
      const selisih = Math.atan2(Math.sin(hadap - ak.g.rotation.y), Math.cos(hadap - ak.g.rotation.y));
      ak.g.rotation.y += selisih * Math.min(1, dt * 6);
      ak.kaki[0].rotation.x = ak.kaki[1].rotation.x = 0;
      if (statusAgent[id]?.status === "working") {
        ak.lengan[0].rotation.x = -1.1 + Math.sin(ak.fase * 2.2) * 0.12;
        ak.lengan[1].rotation.x = -1.1 + Math.cos(ak.fase * 2.4) * 0.12;
      } else {
        ak.lengan[0].rotation.x = ak.lengan[1].rotation.x = Math.sin(ak.fase * 0.25) * 0.05;
      }
    }
    if (ak.bubbleSampai && now > ak.bubbleSampai) {
      ak.bubble.classList.remove("on");
      ak.bubbleSampai = 0;
    }
  }

  for (let i = paket.length - 1; i >= 0; i--) {
    const p = paket[i];
    p.t += dt / 1.4;
    const ke = p.ke.g.position.clone().add(v(0, 0, 2));
    const pos = p.dari.clone().lerp(ke, Math.min(p.t, 1));
    pos.y += Math.sin(Math.min(p.t, 1) * Math.PI) * 3;
    p.m.position.copy(pos);
    p.m.rotation.y += dt * 6;
    if (p.t >= 1) {
      scene.remove(p.m);
      paket.splice(i, 1);
    }
  }

  // lift naik-turun pelan antar lantai
  const siklus = (now / 1000 / 6) % (2 * ATAS);
  const posLift = siklus < ATAS ? siklus : 2 * ATAS - siklus;
  lift.position.y = 1.3 + posLift * JARAK_LANTAI;
  for (const [i, m] of lampuServer.entries()) m.emissiveIntensity = Math.sin(now / 180 + i * 1.7) > 0.2 ? 2.4 : 0.4;

  if (terbang) {
    terbang.t = Math.min(1, terbang.t + dt / 0.9);
    const e = 1 - Math.pow(1 - terbang.t, 3);
    const offset = camera.position.clone().sub(controls.target);
    controls.target.lerpVectors(terbang.tar0, terbang.target, e);
    camera.position.copy(controls.target).add(offset);
    camera.zoom = terbang.zoom0 + (terbang.zoom - terbang.zoom0) * e;
    camera.updateProjectionMatrix();
    if (terbang.t >= 1) terbang = null;
  }
  document.body.classList.toggle("jauh", camera.zoom < 0.75);

  controls.update();
  renderer.render(scene, camera);
  labelRenderer.render(scene, camera);
  requestAnimationFrame(animasi);
}

function ukuran() {
  const w = wadah.clientWidth, h = wadah.clientHeight;
  renderer.setSize(w, h);
  labelRenderer.setSize(w, h);
  const aspek = w / h;
  const tinggi = aspek < 1.1 ? 44 / aspek : 34;
  const geser = w > 860 ? (120 / w) * tinggi * aspek : 0;
  camera.left = (-tinggi * aspek) / 2 - geser;
  camera.right = (tinggi * aspek) / 2 - geser;
  camera.top = tinggi / 2;
  camera.bottom = -tinggi / 2;
  camera.updateProjectionMatrix();
}
new ResizeObserver(ukuran).observe(wadah);

// ---------- Mulai ----------
const info = await fetch("/api/info").then((r) => r.json());
AGENTS = info.agents;
for (const a of AGENTS) a.punyaTim = AGENTS.some((x) => x.atasan === a.id);
layar.bos = LANTAI[ATAS].layarCeo;
aturTempatDuduk(AGENTS);
AGENTS.forEach((a, i) => {
  infoAgent[a.id] = a;
  aktor[a.id] = buatKarakter(a, i);
  statusAgent[a.id] = { status: "idle", aktivitas: "" };
});
document.getElementById("subjudul").textContent =
  AGENTS.length > 10
    ? `${AGENTS[0].nama} (bos) + ${AGENTS.length - 1} agent di ${new Set(Object.values(kursiAgent).map((s) => s.lantai)).size} lantai`
    : `${AGENTS[0].nama} (bos) + ${AGENTS.slice(1).map((a) => a.nama).join(", ")}`;
for (const a of AGENTS) setStatus(a.id, "idle", "", true);
// lantai awal: seluruh gedung bila timnya besar, lantai 3 bila kecil
const awalGedung = AGENTS.length > 18;
tampilkanLantai(awalGedung ? null : ATAS);
document.querySelectorAll(".kamera button").forEach((x) => x.classList.toggle("aktif", x.dataset.cam === (awalGedung ? "gedung" : String(ATAS))));
controls.target.copy(awalGedung ? v(0, 0, yLantai(1) + 1) : v(-1, 0, yLantai(ATAS)));
camera.position.copy(controls.target).addScaledVector(ISO_ARAH, 150);
camera.zoom = awalGedung ? ZOOM_GEDUNG : 1;
ukuran();
animasi();
sambung();
