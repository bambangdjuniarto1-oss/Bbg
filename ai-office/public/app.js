// Kantor virtual 3D isometrik: satu lantai open-plan (Ruang CEO, Ruang Rapat, Workspace kubikel,
// Lounge & Pantry) dengan karakter voxel yang bergerak sesuai status agent dari server (WebSocket).
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { CSS2DRenderer, CSS2DObject } from "three/addons/renderers/CSS2DRenderer.js";

// ---------- Denah (satuan meter) ----------
const X0 = -15, X1 = 15, Z0 = -11, Z1 = 11; // batas lantai; dinding di X0 (kiri) dan Z0 (belakang)
const KORIDOR_Z = -2.6; // koridor utama yang menghubungkan semua area
const TINGGI_DINDING = 3.6;
const LORONG_X = [-8.3, -2.3, 3.9]; // lorong vertikal antar-pod kubikel
const BARIS = [
  { mejaZ: 1.4, lorongZ: 4.1 },
  { mejaZ: 6.6, lorongZ: 9.3 },
];
const KOLOM_KURSI = [-12.6, -10.3, -6.5, -4.2, -0.4, 1.9];

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

// Kamera ortografis dengan sudut isometrik klasik
const ISO_ARAH = new THREE.Vector3(1, 1.05, 1).normalize();
const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 400);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.minZoom = 0.7;
controls.maxZoom = 4;
controls.minPolarAngle = Math.PI * 0.18;
controls.maxPolarAngle = Math.PI * 0.36;
controls.screenSpacePanning = true;
function aturKamera(target, zoom) {
  controls.target.copy(target);
  camera.position.copy(target).addScaledVector(ISO_ARAH, 80);
  camera.zoom = zoom;
  camera.updateProjectionMatrix();
}
aturKamera(new THREE.Vector3(0, 0, 0), 1);

scene.add(new THREE.HemisphereLight("#ffffff", "#b9c4d0", 1.6));
const matahari = new THREE.DirectionalLight("#fff6ea", 2.2);
matahari.position.set(-14, 30, 18);
matahari.castShadow = true;
matahari.shadow.mapSize.set(2048, 2048);
Object.assign(matahari.shadow.camera, { left: -24, right: 24, top: 24, bottom: -24, near: 1, far: 80 });
matahari.shadow.bias = -0.0004;
matahari.shadow.radius = 4;
scene.add(matahari);

// ---------- Helper ----------
const mat = (color, extra = {}) => new THREE.MeshStandardMaterial({ color, roughness: 0.75, ...extra });
const glow = (color, intensity = 1.6) =>
  new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: intensity, roughness: 0.3 });
function kotak(w, h, d, material, x = 0, y = 0, z = 0, parent = scene) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), material);
  m.position.set(x, y, z);
  m.castShadow = m.receiveShadow = true;
  parent.add(m);
  return m;
}
function silinder(r, h, material, x, y, z, seg = 16) {
  const m = new THREE.Mesh(new THREE.CylinderGeometry(r, r, h, seg), material);
  m.position.set(x, y, z);
  m.castShadow = m.receiveShadow = true;
  scene.add(m);
  return m;
}
function bola(r, material, x, y, z) {
  const m = new THREE.Mesh(new THREE.IcosahedronGeometry(r, 1), material);
  m.position.set(x, y, z);
  m.castShadow = m.receiveShadow = true;
  scene.add(m);
  return m;
}

// ---------- Material ----------
const M = {
  putih: mat("#f7f7f5"),
  dinding: mat("#fbfbfa"),
  lantai: mat("#e4e7eb"),
  kayu: mat("#d8b48a"),
  kayuMeja: mat("#e3c39d"),
  abu: mat("#a9b0ba"),
  abuMuda: mat("#ced3da"),
  kursi: mat("#8f98a5"),
  hitam: mat("#2a2d33"),
  daun: mat("#5aa84f"),
  daunTua: mat("#3f8a3d"),
  pot: mat("#f1f1ef"),
  kaca: new THREE.MeshPhysicalMaterial({ color: "#cfe6ff", transparent: true, opacity: 0.22, roughness: 0.05 }),
  rangka: mat("#4b5260", { metalness: 0.5, roughness: 0.4 }),
  jendela: mat("#9cc3e6", { roughness: 0.15, metalness: 0.1 }),
  buku: ["#c96b5b", "#5b8bc9", "#e0b354", "#6aa37a", "#9a7ec2"].map((c) => mat(c)),
};

// ---------- Lantai, dinding, pagar ----------
// alas bangunan (tebal, putih) supaya terlihat seperti potongan maket
kotak(X1 - X0 + 0.6, 0.8, Z1 - Z0 + 0.6, M.putih, 0, -0.4, 0);
kotak(X1 - X0, 0.04, Z1 - Z0, M.lantai, 0, 0.02, 0);
// zona lantai kayu (Ruang CEO dan Lounge)
kotak(8.6, 0.05, 7.2, M.kayu, -10.7, 0.045, -7.4);
kotak(8.2, 0.05, 12.6, M.kayu, 10.9, 0.045, 4.4);

function teksturKarpet() {
  const c = document.createElement("canvas");
  c.width = c.height = 256;
  const g = c.getContext("2d");
  g.fillStyle = "#9fb9d6";
  g.fillRect(0, 0, 256, 256);
  let s = 3;
  const acak = () => ((s = (s * 16807) % 2147483647) / 2147483647);
  for (let i = 0; i < 900; i++) {
    g.fillStyle = acak() < 0.5 ? "#c7d8ea" : "#7f9dc0";
    g.globalAlpha = 0.6;
    g.beginPath();
    g.arc(acak() * 256, acak() * 256, 1 + acak() * 2.4, 0, Math.PI * 2);
    g.fill();
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(3, 2);
  return t;
}
kotak(9.6, 0.05, 6.2, new THREE.MeshStandardMaterial({ map: teksturKarpet(), roughness: 1 }), -0.6, 0.05, -7.5);

// dinding belakang & kiri (dengan jendela)
const tebal = 0.35;
kotak(X1 - X0 + tebal, TINGGI_DINDING, tebal, M.dinding, (X0 + X1) / 2 + tebal / 2, TINGGI_DINDING / 2, Z0 - tebal / 2);
kotak(tebal, TINGGI_DINDING, Z1 - Z0, M.dinding, X0 - tebal / 2, TINGGI_DINDING / 2, 0);
function jendela(x, z, w, sumbuX) {
  const tebalJ = 0.06;
  if (sumbuX) {
    kotak(w, 2.1, tebalJ, M.jendela, x, 1.85, z + 0.2);
    for (let i = 0; i <= 3; i++) kotak(0.07, 2.2, 0.08, M.putih, x - w / 2 + (i * w) / 3, 1.85, z + 0.24);
  } else {
    kotak(tebalJ, 2.1, w, M.jendela, x + 0.2, 1.85, z);
    for (let i = 0; i <= 3; i++) kotak(0.08, 2.2, 0.07, M.putih, x + 0.24, 1.85, z - w / 2 + (i * w) / 3);
  }
}
jendela(-11, Z0, 4.5, true);
jendela(1.5, Z0, 3.6, true);
jendela(X0, 2.5, 4.5, false);
jendela(X0, 8, 3.6, false);

// pagar kaca di sisi depan & kanan + pot tanaman di luar
function pagarKaca(x, z, panjang, sumbuX) {
  const h = 1.1;
  if (sumbuX) {
    kotak(panjang, h, 0.04, M.kaca, x, h / 2 + 0.05, z).castShadow = false;
    kotak(panjang, 0.06, 0.09, M.rangka, x, h + 0.05, z);
    for (let i = 0; i <= Math.round(panjang / 2.5); i++) kotak(0.07, h, 0.07, M.rangka, x - panjang / 2 + (i * panjang) / Math.round(panjang / 2.5), h / 2 + 0.05, z);
  } else {
    kotak(0.04, h, panjang, M.kaca, x, h / 2 + 0.05, z).castShadow = false;
    kotak(0.09, 0.06, panjang, M.rangka, x, h + 0.05, z);
    for (let i = 0; i <= Math.round(panjang / 2.5); i++) kotak(0.07, h, 0.07, M.rangka, x, h / 2 + 0.05, z - panjang / 2 + (i * panjang) / Math.round(panjang / 2.5));
  }
}
pagarKaca(0, Z1, X1 - X0, true);
pagarKaca(X1, 0, Z1 - Z0, false);

function pohon(x, z, s = 1, y = 0) {
  silinder(0.08 * s, 0.9 * s, M.kayu, x, y + 0.45 * s, z, 8);
  bola(0.75 * s, M.daun, x, y + 1.35 * s, z);
}
function tanamanPot(x, z, s = 1) {
  silinder(0.28 * s, 0.5 * s, M.pot, x, 0.25 * s, z);
  bola(0.45 * s, M.daunTua, x, 0.85 * s, z);
  bola(0.32 * s, M.daun, x + 0.18 * s, 1.15 * s, z - 0.1 * s);
}
// bedeng tanaman di luar pagar
kotak(X1 - X0, 0.35, 1, M.putih, 0, 0.17, Z1 + 0.85);
kotak(1, 0.35, Z1 - Z0 + 2, M.putih, X1 + 0.85, 0.17, 0.5);
kotak(X1 - X0 - 0.2, 0.05, 0.8, M.daunTua, 0, 0.37, Z1 + 0.85);
kotak(0.8, 0.05, Z1 - Z0 + 1.8, M.daunTua, X1 + 0.85, 0.37, 0.5);
for (const x of [-12, -4, 4, 12]) pohon(x, Z1 + 0.85, 1, 0.35);
for (const z of [-7, 1, 8]) pohon(X1 + 0.85, z, 1, 0.35);

// ---------- Furnitur ----------
function kursiKantor(x, z, rotY = 0) {
  const g = new THREE.Group();
  kotak(0.62, 0.1, 0.6, M.kursi, 0, 0.5, 0, g);
  kotak(0.62, 0.62, 0.1, M.kursi, 0, 0.84, 0.27, g);
  kotak(0.06, 0.45, 0.06, M.hitam, 0, 0.25, 0, g);
  kotak(0.55, 0.05, 0.55, M.hitam, 0, 0.04, 0, g);
  g.position.set(x, 0, z);
  g.rotation.y = rotY;
  scene.add(g);
  return g;
}
function rakBuku(x, z, w, rotY = 0) {
  const g = new THREE.Group();
  kotak(w, 2.2, 0.45, M.putih, 0, 1.1, 0, g);
  for (let i = 0; i < 4; i++) {
    let bx = -w / 2 + 0.15;
    while (bx < w / 2 - 0.3) {
      const bw = 0.08 + Math.random() * 0.1;
      const bh = 0.3 + Math.random() * 0.15;
      if (Math.random() < 0.8) kotak(bw, bh, 0.3, M.buku[Math.floor(Math.random() * 5)], bx, 0.25 + i * 0.52 + bh / 2, 0.06, g);
      bx += bw + 0.02;
    }
  }
  g.position.set(x, 0, z);
  g.rotation.y = rotY;
  scene.add(g);
}
function sofaKecil(x, z, rotY = 0, warna = M.abuMuda) {
  const g = new THREE.Group();
  kotak(0.95, 0.45, 0.9, warna, 0, 0.3, 0, g);
  kotak(0.95, 0.6, 0.2, warna, 0, 0.75, 0.38, g);
  for (const sx of [-0.42, 0.42]) kotak(0.14, 0.35, 0.9, warna, sx, 0.62, 0, g);
  g.position.set(x, 0, z);
  g.rotation.y = rotY;
  scene.add(g);
}

// Monitor: id agent -> material layar
const layar = {};
const LAYAR_MATI = "#8fbbe8";
const LAYAR_NYALA = "#2f8cff";
function monitorGanda(x, z) {
  const mats = [];
  for (const dx of [-0.36, 0.36]) {
    const m = glow(LAYAR_MATI, 0.45);
    kotak(0.68, 0.44, 0.05, M.hitam, x + dx, 1.33, z);
    kotak(0.62, 0.38, 0.02, m, x + dx, 1.33, z + 0.03);
    mats.push(m);
  }
  kotak(0.06, 0.25, 0.06, M.hitam, x, 1.0, z - 0.03);
  kotak(0.5, 0.03, 0.12, M.abuMuda, x, 0.79, z + 0.35); // keyboard
  return mats;
}

// Kubikel: 2 baris x 6 kursi, partisi putih rendah, meja kayu, monitor ganda
const KURSI = []; // {x, z, baris, layar}
for (const [bi, b] of BARIS.entries()) {
  // partisi belakang memanjang per pod
  for (let p = 0; p < 3; p++) {
    const xa = KOLOM_KURSI[p * 2], xb = KOLOM_KURSI[p * 2 + 1];
    const cx = (xa + xb) / 2;
    kotak(4.9, 1.25, 0.1, M.putih, cx, 0.62, b.mejaZ - 0.55);
    for (const sx of [-2.45, 0, 2.45]) kotak(0.1, 1.25, 1.5, M.putih, cx + sx, 0.62, b.mejaZ + 0.2);
  }
  for (const x of KOLOM_KURSI) {
    kotak(2.15, 0.07, 1, M.kayuMeja, x, 0.76, b.mejaZ);
    kotak(0.06, 0.74, 0.9, M.putih, x - 1.0, 0.38, b.mejaZ);
    const m = monitorGanda(x, b.mejaZ - 0.3);
    kursiKantor(x, b.mejaZ + 1.05);
    KURSI.push({ x, z: b.mejaZ + 1.05, baris: bi, layar: m });
  }
}
tanamanPot(-14.2, 4.1, 0.9);
tanamanPot(5.5, 4.1, 0.9);
tanamanPot(-14.2, 9.6, 0.9);

// Ruang CEO (kiri belakang): sekat kaca, meja eksekutif, rak buku, tanaman
kotak(0.08, 2.6, 6.2, M.kaca, -6.4, 1.3, -7.9).castShadow = false;
kotak(5.6, 2.6, 0.08, M.kaca, -12.2, 1.3, -3.9).castShadow = false;
kotak(0.1, 0.08, 6.2, M.rangka, -6.4, 2.62, -7.9);
kotak(5.6, 0.08, 0.1, M.rangka, -12.2, 2.62, -3.9);
kotak(3, 0.1, 1.3, M.kayuMeja, -10.8, 0.8, -8.4);
kotak(3, 0.75, 0.08, M.putih, -10.8, 0.4, -8.95);
const layarCeo = monitorGanda(-10.8, -8.65);
kursiKantor(-10.8, -7.4);
sofaKecil(-14.1, -5.4, -Math.PI / 2);
rakBuku(-8.2, -10.55, 3);
tanamanPot(-14.2, -10.2, 1.1);

// Ruang Rapat (tengah belakang): karpet biru, meja panjang, kursi
kotak(6.2, 0.1, 1.8, M.putih, -0.6, 0.78, -7.6);
for (const dx of [-2.6, 2.6]) kotak(0.12, 0.74, 1.4, M.putih, -0.6 + dx, 0.38, -7.6);
for (const dx of [-2.2, -0.8, 0.6, 2]) {
  kursiKantor(-0.6 + dx, -8.9, Math.PI);
  kursiKantor(-0.6 + dx, -6.3);
}
kotak(2.4, 1.4, 0.06, M.hitam, -0.6, 1.9, -10.75); // layar presentasi
kotak(2.25, 1.25, 0.02, glow("#cfe3ff", 0.6), -0.6, 1.9, -10.71);
kotak(0.08, 2.6, 6.2, M.kaca, 4.6, 1.3, -7.9).castShadow = false;
tanamanPot(3.9, -10.2, 1.2);

// Pantry (kanan belakang): meja dapur, mesin kopi, kulkas
kotak(5.5, 0.95, 0.8, M.putih, 9.9, 0.48, -10.4);
kotak(5.5, 0.06, 0.85, M.abuMuda, 9.9, 0.98, -10.4);
kotak(0.5, 0.6, 0.45, M.hitam, 8, 1.3, -10.45);
kotak(0.12, 0.08, 0.02, glow("#5dffa0", 2), 8, 1.4, -10.2);
kotak(1, 2.2, 0.8, M.abuMuda, 13.6, 1.1, -10.4);
kotak(1.2, 0.08, 1.2, M.putih, 9.5, 0.75, -7.2);
silinder(0.08, 0.72, M.putih, 9.5, 0.37, -7.2, 8);
for (const [dx, dz] of [[-0.9, 0], [0.9, 0], [0, 0.9]]) silinder(0.25, 0.5, M.kursi, 9.5 + dx, 0.25, -7.2 + dz);

// Lounge (kanan depan): kursi santai, meja kopi, rak buku
const SANTAI = [];
for (const [i, [x, z]] of [[8.6, 1.2], [10.6, 1.2], [12.6, 1.2], [8.6, 5.8], [10.6, 5.8], [12.6, 5.8]].entries()) {
  sofaKecil(x, z, i < 3 ? Math.PI : 0); // sandaran membelakangi meja kopi
}
for (const [x, z] of [[8.6, 2.3], [10.6, 4.7], [12.6, 2.3], [8.6, 4.7], [10.6, 2.3], [12.6, 4.7]]) SANTAI.push({ x, z });
kotak(5, 0.08, 1.1, M.kayuMeja, 10.6, 0.45, 3.5);
for (const dx of [-2.2, 2.2]) kotak(0.1, 0.42, 0.9, M.putih, 10.6 + dx, 0.22, 3.5);
rakBuku(14.6, 8.6, 3.2, -Math.PI / 2);
tanamanPot(7.6, 9.6, 1);
tanamanPot(14.3, -1, 1);

// ---------- Label zona ----------
function labelZona(teks, x, z) {
  const el = document.createElement("div");
  el.className = "label-lantai";
  el.innerHTML = teks;
  const o = new CSS2DObject(el);
  o.position.set(x, 3.2, z);
  scene.add(o);
  return el;
}
const elZona = {
  bos: labelZona("Ruang CEO", -10.6, -7),
  rapat: labelZona("Ruang Rapat", -0.6, -7.5),
  workspace: labelZona("Workspace", -5.3, 4.2),
  lounge: labelZona("Lounge & Pantry", 10.8, -4),
};

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

  const el = document.createElement("div");
  el.className = "label3d";
  el.innerHTML = `<span class="bubble"></span><span class="tag"><i></i>${info.nama}</span>`;
  const label = new CSS2DObject(el);
  label.position.set(0, 2.2, 0);
  g.add(label);
  scene.add(g);
  return { g, kaki, lengan, el, bubble: el.querySelector(".bubble"), jalur: [], fase: Math.random() * 6, bubbleSampai: 0, spot: null };
}

// ---------- Titik tujuan & rute ----------
// Setiap "spot" punya posisi, arah hadap, dan titik keluar menuju koridor utama.
const lorongTerdekat = (x) => LORONG_X.reduce((a, b) => (Math.abs(b - x) < Math.abs(a - x) ? b : a));
const v = (x, z) => new THREE.Vector3(x, 0, z);

function spotKursi(k) {
  const lz = BARIS[k.baris].lorongZ;
  const lx = lorongTerdekat(k.x);
  return { pos: v(k.x, k.z), hadap: Math.PI, keluar: [v(k.x, lz), v(lx, lz), v(lx, KORIDOR_Z)] };
}
const SPOT_CEO_MEJA = { pos: v(-10.8, -7.4), hadap: Math.PI, keluar: [v(-9, -6), v(-5.6, -4.6), v(-5.6, KORIDOR_Z)] };
const SPOT_CEO_SANTAI = { pos: v(-12.8, -5.4), hadap: Math.PI / 2, keluar: [v(-9, -6), v(-5.6, -4.6), v(-5.6, KORIDOR_Z)] };
const spotSantai = (i) => {
  const s = SANTAI[i % SANTAI.length];
  return { pos: v(s.x, s.z), hadap: s.z < 3.5 ? 0 : Math.PI, keluar: [v(s.x > 11 ? 14 : 7.2, s.z), v(s.x > 11 ? 14 : 7.2, KORIDOR_Z)] };
};

const kursiAgent = {}; // id -> spot meja
const santaiAgent = {}; // id -> spot santai

function tujuan(id, status) {
  if (id === "bos") return status === "idle" ? SPOT_CEO_SANTAI : SPOT_CEO_MEJA;
  return status === "idle" ? santaiAgent[id] : kursiAgent[id];
}

// Rute: keluar dari spot asal ke koridor -> sepanjang koridor -> masuk ke spot tujuan
function rute(dari, ke) {
  if (dari === ke) return [];
  return [...dari.keluar, ...[...ke.keluar].reverse(), ke.pos.clone()].map((p) => p.clone());
}

// ---------- Paket tugas yang terbang dari bos ke agent ----------
const paket = [];
function kirimPaket(dariId, keId, warna) {
  const a = aktor[dariId], b = aktor[keId];
  if (!a || !b) return;
  const m = kotak(0.3, 0.4, 0.05, glow(warna, 2.5), 0, 0, 0);
  paket.push({ m, dari: a.g.position.clone().add(v(0, 2, 0)), ke: b, t: 0 });
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

const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
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

function renderKartu() {
  elKartu.innerHTML = AGENTS.map((a) => {
    const s = statusAgent[a.id] ?? { status: "idle", aktivitas: "" };
    const teks = s.status === "idle" ? (a.id === "bos" ? "standby di ruang CEO" : "santai di lounge") : s.aktivitas || "bekerja";
    return `<div class="kartu" data-status="${s.status}"><span class="dot" style="background:${a.warna}"></span>
      <span class="nama">${esc(a.nama)} <small>${esc(a.jabatan)}</small></span><span class="akt">${esc(teks)}</span></div>`;
  }).join("");
  const tim = AGENTS.filter((a) => a.id !== "bos");
  const kerja = tim.filter((a) => statusAgent[a.id]?.status !== "idle").length;
  elZona.workspace.innerHTML = `Workspace · <b>${kerja}</b> kerja`;
  elZona.lounge.innerHTML = `Lounge & Pantry · <b>${tim.length - kerja}</b> santai`;
  elZona.bos.innerHTML = `Ruang CEO · ${statusAgent.bos?.status === "idle" ? "standby" : "<b>sibuk</b>"}`;
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
  if (instan || !ak.spot) {
    ak.g.position.copy(t.pos);
    ak.g.rotation.y = t.hadap;
    ak.jalur = [];
    ak.spot = t;
  } else if (ak.spot !== t) {
    // lanjutkan jalur yang sedang ditempuh, lalu menuju spot baru
    ak.jalur.push(...rute(ak.spot, t));
    ak.spot = t;
  }
  renderKartu();
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

function sambung() {
  const ws = new WebSocket(`${location.protocol === "https:" ? "wss" : "ws"}://${location.host}/ws`);
  ws.onmessage = (m) => {
    const ev = JSON.parse(m.data);
    if (ev.type === "init") {
      elChat.innerHTML = "";
      elMode.textContent = ev.demo ? "Mode DEMO" : "LIVE · Claude";
      elMode.className = "pill " + (ev.demo ? "demo" : "live");
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

// ---------- Kamera per area ----------
const PRESET = {
  semua: [v(0, 0), 1],
  bos: [v(-9, -6), 2.4],
  workspace: [v(-5, 4.5), 1.9],
  pantry: [v(9.5, -1.5), 2.1],
};
let terbang = null;
document.querySelectorAll(".kamera button").forEach((b) =>
  b.addEventListener("click", () => {
    document.querySelectorAll(".kamera button").forEach((x) => x.classList.toggle("aktif", x === b));
    const [target, zoom] = PRESET[b.dataset.cam];
    terbang = { tar0: controls.target.clone(), zoom0: camera.zoom, target, zoom, t: 0 };
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
        // mengetik di depan monitor
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
    const ke = p.ke.g.position.clone().add(v(0, 2, 0));
    const pos = p.dari.clone().lerp(ke, Math.min(p.t, 1));
    pos.y += Math.sin(Math.min(p.t, 1) * Math.PI) * 3;
    p.m.position.copy(pos);
    p.m.rotation.y += dt * 6;
    if (p.t >= 1) {
      scene.remove(p.m);
      paket.splice(i, 1);
    }
  }

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
  // tinggi pandangan: cukup untuk seluruh lantai; di layar sempit diperbesar agar lebarnya muat
  const tinggi = aspek < 1.1 ? 44 / aspek : 34;
  // geser pandangan ke kanan di layar lebar supaya gedung tidak tertutup kartu status
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
let idxKursi = 0;
// sebar agent ke kubikel yang berselang-seling supaya kantor terlihat terisi merata
const URUTAN_KURSI = [1, 3, 5, 6, 8, 10, 0, 2, 4, 7, 9, 11];
AGENTS.forEach((a, i) => {
  infoAgent[a.id] = a;
  aktor[a.id] = buatKarakter(a, i);
  statusAgent[a.id] = { status: "idle", aktivitas: "" };
  if (a.id === "bos") {
    layar.bos = layarCeo;
  } else {
    const k = KURSI[URUTAN_KURSI[idxKursi % KURSI.length]];
    kursiAgent[a.id] = spotKursi(k);
    santaiAgent[a.id] = spotSantai(idxKursi);
    layar[a.id] = k.layar;
    idxKursi++;
  }
});
document.getElementById("subjudul").textContent =
  `${AGENTS[0].nama} (bos) + ${AGENTS.slice(1).map((a) => a.nama).join(", ")}`;
for (const a of AGENTS) setStatus(a.id, "idle", "", true);
ukuran();
animasi();
sambung();
