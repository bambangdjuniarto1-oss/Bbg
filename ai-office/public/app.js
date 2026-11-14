// Kantor virtual 3D: gedung 3 lantai (Pantry, Workspace, Ruang Bos) dengan karakter voxel
// yang bergerak sesuai status agent yang dikirim server lewat WebSocket.
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { CSS2DRenderer, CSS2DObject } from "three/addons/renderers/CSS2DRenderer.js";

const H = 4.5; // tinggi satu lantai
const LANTAI = { pantry: 0, workspace: 1, bos: 2 };
const KORIDOR_Z = 2.4;
const TANGGA_Z = 2.4;
const X_TANGGA_KIRI = 8.2;
const X_TANGGA_KANAN = 11.6;

// ---------- Renderer & scene ----------
const wadah = document.getElementById("scene");
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
wadah.appendChild(renderer.domElement);

const labelRenderer = new CSS2DRenderer();
labelRenderer.domElement.style.position = "absolute";
labelRenderer.domElement.style.inset = "0";
labelRenderer.domElement.style.pointerEvents = "none";
wadah.appendChild(labelRenderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color("#0a0c1c");
scene.fog = new THREE.Fog("#0a0c1c", 40, 90);

const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 200);
camera.position.set(-1, 9, 27);
const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(-1, 5.5, 0);
controls.enableDamping = true;
controls.minDistance = 6;
controls.maxDistance = 45;
controls.maxPolarAngle = Math.PI * 0.55;
controls.minAzimuthAngle = -Math.PI * 0.4;
controls.maxAzimuthAngle = Math.PI * 0.4;

scene.add(new THREE.HemisphereLight("#9fb4ff", "#2a1d10", 0.9));
const bulan = new THREE.DirectionalLight("#c9d6ff", 0.6);
bulan.position.set(-10, 20, 15);
scene.add(bulan);

// ---------- Helper bangun ----------
const mat = (color, extra = {}) => new THREE.MeshStandardMaterial({ color, roughness: 0.8, ...extra });
const glow = (color, intensity = 2) =>
  new THREE.MeshStandardMaterial({ color, emissive: color, emissiveIntensity: intensity });
function kotak(w, h, d, material, x = 0, y = 0, z = 0, parent = scene) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), material);
  m.position.set(x, y, z);
  parent.add(m);
  return m;
}

// ---------- Latar kota malam ----------
function teksturKota() {
  const c = document.createElement("canvas");
  c.width = 2048; c.height = 768;
  const g = c.getContext("2d");
  const langit = g.createLinearGradient(0, 0, 0, c.height);
  langit.addColorStop(0, "#0b0a24");
  langit.addColorStop(0.6, "#2a1747");
  langit.addColorStop(1, "#4a2350");
  g.fillStyle = langit;
  g.fillRect(0, 0, c.width, c.height);
  let seed = 7;
  const acak = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  for (const [lapis, gelap, peluang] of [[0, "#16122e", 0.18], [1, "#0d0b1f", 0.32]]) {
    let x = 0;
    while (x < c.width) {
      const w = 40 + acak() * 110;
      const h = (lapis ? 180 : 320) + acak() * (lapis ? 320 : 260);
      const y = c.height - h;
      g.fillStyle = gelap;
      g.fillRect(x, y, w, h);
      for (let wy = y + 10; wy < c.height - 8; wy += 14) {
        for (let wx = x + 6; wx < x + w - 6; wx += 10) {
          if (acak() < peluang) {
            g.fillStyle = acak() < 0.8 ? "#ffd27a" : "#9ad7ff";
            g.globalAlpha = 0.5 + acak() * 0.5;
            g.fillRect(wx, wy, 5, 7);
          }
        }
      }
      g.globalAlpha = 1;
      x += w + acak() * 12;
    }
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}
const kota = new THREE.Mesh(
  new THREE.PlaneGeometry(110, 42),
  new THREE.MeshBasicMaterial({ map: teksturKota(), fog: false }),
);
kota.position.set(0, 12, -18);
scene.add(kota);

// ---------- Gedung ----------
const LEBAR_KIRI = -12.5;
const LEBAR_KANAN = 7.2;
const LEBAR = LEBAR_KANAN - LEBAR_KIRI;
const TENGAH_X = (LEBAR_KIRI + LEBAR_KANAN) / 2;
const matLantai = mat("#2b2f45");
const matLantaiKayu = mat("#5b4636");
const matDinding = mat("#1d2133");
const matKaca = new THREE.MeshStandardMaterial({ color: "#7aa7ff", transparent: true, opacity: 0.08, roughness: 0.1 });
const matRangka = mat("#11131f", { metalness: 0.4 });
const matLampu = glow("#ffb45c", 2.4);

for (let f = 0; f <= 3; f++) {
  const y = f * H;
  kotak(LEBAR + 5.4, 0.35, 8.4, f === 2 ? matLantaiKayu : matLantai, TENGAH_X + 2.7, y - 0.175, 0);
  if (f > 0) {
    // lis lampu hangat di tepi depan plafon
    kotak(LEBAR + 5.4, 0.08, 0.12, matLampu, TENGAH_X + 2.7, y - 0.4, 4.1);
  }
  if (f < 3) {
    const lampu = new THREE.PointLight("#ffbf73", 18, 16, 1.6);
    lampu.position.set(TENGAH_X - 3, y + H - 0.8, 1.5);
    scene.add(lampu);
    const lampu2 = lampu.clone();
    lampu2.position.x = TENGAH_X + 6;
    scene.add(lampu2);
    // kaca belakang + rangka
    kotak(LEBAR + 5.4, H - 0.35, 0.05, matKaca, TENGAH_X + 2.7, y + H / 2, -4.15);
    for (let x = LEBAR_KIRI; x <= LEBAR_KANAN + 5.4; x += 2.6) kotak(0.08, H, 0.08, matRangka, x, y + H / 2, -4.1);
  }
}
// dinding samping
kotak(0.3, 3 * H, 8.4, matDinding, LEBAR_KIRI - 0.15, 1.5 * H, 0);
kotak(0.3, 3 * H, 8.4, matDinding, LEBAR_KANAN + 5.55, 1.5 * H, 0);
// sekat antara ruang kerja dan tangga
for (let f = 0; f < 3; f++) kotak(0.12, H * 0.55, 3.2, matRangka, LEBAR_KANAN + 0.3, f * H + H * 0.275, -2.3);

// tangga zig-zag di sisi kanan
const matTangga = mat("#3a3f5a");
for (let f = 0; f < 2; f++) {
  const naikKeKanan = f % 2 === 0;
  const anak = 12;
  for (let i = 0; i < anak; i++) {
    const t = (i + 0.5) / anak;
    const x = naikKeKanan
      ? X_TANGGA_KIRI + t * (X_TANGGA_KANAN - X_TANGGA_KIRI)
      : X_TANGGA_KANAN - t * (X_TANGGA_KANAN - X_TANGGA_KIRI);
    kotak(0.32, 0.18, 1.4, matTangga, x, f * H + t * H, TANGGA_Z + (naikKeKanan ? 1 : -1) * 0.75);
  }
}

// ---------- Furnitur ----------
const matMeja = mat("#d9d4c7");
const matKursi = mat("#262a3d");
const matTanaman = mat("#3fae5a");
const matPot = mat("#8a5a3b");
function tanaman(x, y, z, s = 1) {
  kotak(0.5 * s, 0.5 * s, 0.5 * s, matPot, x, y + 0.25 * s, z);
  kotak(0.8 * s, 0.9 * s, 0.8 * s, matTanaman, x, y + 0.95 * s, z);
  kotak(0.5 * s, 0.5 * s, 0.5 * s, matTanaman, x + 0.1, y + 1.6 * s, z - 0.1);
}

const monitor = {}; // id agent -> material layar
function mejaKerja(id, x, y) {
  kotak(2.4, 0.12, 1.1, matMeja, x, y + 0.85, -1.3);
  for (const dx of [-1.05, 1.05]) kotak(0.1, 0.85, 1, matMeja, x + dx, y + 0.42, -1.3);
  kotak(0.9, 0.1, 0.9, matKursi, x, y + 0.5, -0.35); // kursi di depan meja (menghadap kamera)
  kotak(0.9, 0.5, 0.1, matKursi, x, y + 0.8, 0.1);
  kotak(0.1, 0.5, 0.1, matKursi, x, y + 0.25, -0.35);
  const layar = glow("#1c2238", 0.4);
  kotak(1.2, 0.72, 0.06, matRangka, x, y + 1.45, -1.62);
  kotak(1.1, 0.62, 0.02, layar, x, y + 1.45, -1.58);
  kotak(0.08, 0.35, 0.08, matRangka, x, y + 1.05, -1.65);
  monitor[id] = layar;
}

// Lantai 0: Pantry
const yP = 0;
kotak(4.5, 1, 1, mat("#e7e2d6"), -10, yP + 0.5, -3.3);
kotak(4.5, 0.08, 1.05, mat("#3b3f55"), -10, yP + 1.04, -3.3);
kotak(0.6, 0.8, 0.5, mat("#c0392b"), -11.2, yP + 1.48, -3.4); // mesin kopi
kotak(0.2, 0.2, 0.05, glow("#7dffb2", 3), -11.2, yP + 1.6, -3.14);
kotak(1, 2.2, 0.9, mat("#cfd6e0"), -6.8, yP + 1.1, -3.35); // kulkas
kotak(2.6, 0.12, 1.4, matMeja, -3.5, yP + 0.8, 0.2); // meja makan
kotak(0.15, 0.8, 0.15, matMeja, -3.5, yP + 0.4, 0.2);
for (const [dx, dz] of [[-1.7, 0.2], [1.7, 0.2]]) kotak(0.6, 0.5, 0.6, mat("#f5a623"), -3.5 + dx, yP + 0.25, 0.2 + dz);
kotak(3, 0.6, 1, mat("#46507a"), 2.5, yP + 0.3, -2.9); // sofa
kotak(3, 0.8, 0.3, mat("#46507a"), 2.5, yP + 0.7, -3.35);
tanaman(5.8, yP, -3.2);
tanaman(-12, yP, 3.2, 0.8);

// Lantai 1: Workspace
const yW = H;
const POSISI_MEJA = { riset: -9.5, copywriter: -5.3, builder: -1.1, content: 3.1 };
for (const [id, x] of Object.entries(POSISI_MEJA)) mejaKerja(id, x, yW);
tanaman(6, yW, -3.3);
tanaman(-12, yW, -3.3, 0.8);
kotak(3, 1.6, 0.06, mat("#f2f2f2"), -3, yW + 2.4, -4.05); // papan tulis

// Lantai 2: Ruang Bos
const yB = 2 * H;
kotak(3.4, 0.14, 1.5, mat("#6e4a33"), -6, yB + 0.88, -1.4);
kotak(3.2, 0.8, 0.1, mat("#5a3b28"), -6, yB + 0.45, -2.1);
kotak(1.1, 1.3, 0.2, mat("#7a1f2b"), -6, yB + 1.2, 0.15); // kursi bos
kotak(1, 0.1, 1, mat("#7a1f2b"), -6, yB + 0.55, -0.3);
const layarBos = glow("#1c2238", 0.4);
kotak(1.6, 0.9, 0.06, matRangka, -6, yB + 1.55, -1.85);
kotak(1.5, 0.8, 0.02, layarBos, -6, yB + 1.55, -1.81);
monitor.bos = layarBos;
kotak(3.6, 0.6, 1.2, mat("#2f3654"), 1.5, yB + 0.3, -2.9);
kotak(3.6, 0.9, 0.3, mat("#2f3654"), 1.5, yB + 0.75, -3.4);
kotak(1.4, 0.4, 0.8, mat("#6e4a33"), 1.5, yB + 0.2, -1.4);
tanaman(-10.8, yB, -3.2, 1.1);
tanaman(5.5, yB, -3.2);
kotak(0.12, H * 0.8, 6, matKaca, -2.2, yB + H * 0.4, -1); // sekat kaca ruang bos

// Label lantai
function labelLantai(teks, x, y) {
  const el = document.createElement("div");
  el.className = "label-lantai";
  el.innerHTML = teks;
  const o = new CSS2DObject(el);
  o.position.set(x, y, 4.2);
  scene.add(o);
  return el;
}
const elLantai = {
  bos: labelLantai("Ruang Bos", 4.5, yB + 3.7),
  workspace: labelLantai("Workspace", 4.5, yW + 3.7),
  pantry: labelLantai("Pantry", 4.5, yP + 3.7),
};

// ---------- Karakter voxel ----------
const matKulit = mat("#f1c9a5");
const matHitam = mat("#111111");
const matCelana = mat("#2c3e50");
const RAMBUT = ["#2b1b12", "#5a3825", "#111111", "#7b4a2a", "#3a2a20"];

function buatKarakter(info, i) {
  const g = new THREE.Group();
  const baju = mat(info.warna);
  const rambut = mat(RAMBUT[i % RAMBUT.length]);
  const kaki = [];
  for (const sx of [-0.15, 0.15]) {
    const pivot = new THREE.Group();
    pivot.position.set(sx, 0.62, 0);
    kotak(0.24, 0.62, 0.28, matCelana, 0, -0.31, 0, pivot);
    g.add(pivot);
    kaki.push(pivot);
  }
  kotak(0.62, 0.72, 0.36, baju, 0, 0.98, 0, g);
  const lengan = [];
  for (const sx of [-0.41, 0.41]) {
    const pivot = new THREE.Group();
    pivot.position.set(sx, 1.28, 0);
    kotak(0.19, 0.62, 0.22, baju, 0, -0.28, 0, pivot);
    kotak(0.17, 0.12, 0.2, matKulit, 0, -0.62, 0, pivot);
    g.add(pivot);
    lengan.push(pivot);
  }
  kotak(0.54, 0.54, 0.5, matKulit, 0, 1.62, 0, g);
  kotak(0.58, 0.16, 0.54, rambut, 0, 1.94, 0, g);
  kotak(0.58, 0.4, 0.12, rambut, 0, 1.74, -0.22, g);
  for (const sx of [-0.12, 0.12]) kotak(0.08, 0.1, 0.02, matHitam, sx, 1.65, 0.26, g);
  if (info.id === "bos") kotak(0.12, 0.42, 0.02, mat("#c0392b"), 0, 0.98, 0.19, g); // dasi bos

  const el = document.createElement("div");
  el.className = "label3d";
  el.innerHTML = `<span class="bubble"></span><span class="tag"><i></i>${info.nama}</span>`;
  const label = new CSS2DObject(el);
  label.position.set(0, 2.35, 0);
  g.add(label);
  scene.add(g);
  return { g, kaki, lengan, el, bubble: el.querySelector(".bubble"), jalur: [], fase: Math.random() * 6, bubbleSampai: 0 };
}

// Posisi tujuan setiap agent per status
function tujuan(id, status) {
  if (id === "bos") {
    return status === "idle" ? new THREE.Vector3(1.5, yB, -0.6) : new THREE.Vector3(-6, yB, -0.3);
  }
  if (status === "idle") {
    const santai = { riset: [-10.5, -2.4], copywriter: [-5.2, 0.2], builder: [-1.8, 0.2], content: [2.5, -1.8] };
    const [x, z] = santai[id];
    return new THREE.Vector3(x, yP, z);
  }
  return new THREE.Vector3(POSISI_MEJA[id], yW, -0.35);
}

const lantaiDari = (v) => Math.round(v.y / H);

// Rute: ke koridor depan -> tangga (zig-zag) -> koridor lantai tujuan -> tujuan
function rencanaJalur(dari, ke) {
  const f0 = lantaiDari(dari);
  const f1 = lantaiDari(ke);
  const titik = [];
  if (f0 !== f1) {
    titik.push(new THREE.Vector3(dari.x, dari.y, KORIDOR_Z));
    const arah = Math.sign(f1 - f0);
    for (let f = f0; f !== f1; f += arah) {
      const ramp = arah > 0 ? f : f - 1; // tangga antara lantai ramp dan ramp+1
      const kanan = ramp % 2 === 0; // tangga genap naik ke kanan
      const zRamp = TANGGA_Z + (kanan ? 0.75 : -0.75);
      const bawah = new THREE.Vector3(kanan ? X_TANGGA_KIRI : X_TANGGA_KANAN, ramp * H, zRamp);
      const atas = new THREE.Vector3(kanan ? X_TANGGA_KANAN : X_TANGGA_KIRI, (ramp + 1) * H, zRamp);
      if (arah > 0) titik.push(bawah, atas);
      else titik.push(atas, bawah);
    }
    titik.push(new THREE.Vector3(ke.x, ke.y, KORIDOR_Z));
  } else if (Math.abs(dari.x - ke.x) > 1.5) {
    titik.push(new THREE.Vector3(dari.x, dari.y, KORIDOR_Z), new THREE.Vector3(ke.x, ke.y, KORIDOR_Z));
  }
  titik.push(ke.clone());
  return titik;
}

// ---------- Paket tugas yang "terbang" dari bos ke agent ----------
const paket = [];
function kirimPaket(dariId, keId, warna) {
  const a = aktor[dariId], b = aktor[keId];
  if (!a || !b) return;
  const m = kotak(0.35, 0.45, 0.06, glow(warna, 3), 0, 0, 0);
  paket.push({ m, dari: a.g.position.clone().add(new THREE.Vector3(0, 2, 0)), ke: b, t: 0 });
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

function jam(t) {
  return new Date(t ?? Date.now()).toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit" });
}
function gulirBawah() {
  elChat.scrollTop = elChat.scrollHeight;
}
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
    const teks = s.status === "idle" ? (a.id === "bos" ? "standby di ruang bos" : "santai di pantry") : s.aktivitas || "bekerja";
    return `<div class="kartu" data-status="${s.status}"><span class="dot" style="background:${a.warna}"></span>
      <span class="nama">${esc(a.nama)} <small>${esc(a.jabatan)}</small></span><span class="akt">${esc(teks)}</span></div>`;
  }).join("");
  const kerja = AGENTS.filter((a) => a.id !== "bos" && statusAgent[a.id]?.status !== "idle").length;
  const santai = AGENTS.filter((a) => a.id !== "bos").length - kerja;
  elLantai.workspace.innerHTML = `Workspace · <b>${kerja}</b> kerja`;
  elLantai.pantry.innerHTML = `Pantry · <b>${santai}</b> santai`;
  elLantai.bos.innerHTML = `Ruang Bos · ${statusAgent.bos?.status === "idle" ? "standby" : "<b>sibuk</b>"}`;
}

function tampilkanBubble(id, teks, durasi = 4500) {
  const ak = aktor[id];
  if (!ak) return;
  ak.bubble.textContent = teks.length > 70 ? teks.slice(0, 67) + "…" : teks;
  ak.bubble.classList.add("on");
  ak.bubbleSampai = performance.now() + durasi;
}

function setStatus(id, status, aktivitas, instan = false) {
  const lama = statusAgent[id]?.status;
  statusAgent[id] = { status, aktivitas };
  const ak = aktor[id];
  if (!ak) return;
  ak.el.dataset.status = status;
  if (monitor[id]) {
    const nyala = status !== "idle";
    monitor[id].color.set(nyala ? "#3d7bff" : "#1c2238");
    monitor[id].emissive.set(nyala ? "#3d7bff" : "#1c2238");
    monitor[id].emissiveIntensity = nyala ? 2.2 : 0.4;
  }
  if (aktivitas && status !== "idle") tampilkanBubble(id, aktivitas, 6000);
  const t = tujuan(id, status);
  if (instan) {
    ak.g.position.copy(t);
    ak.jalur = [];
  } else if (lama !== status || ak.jalur.length === 0) {
    if (ak.g.position.distanceTo(t) > 0.05) ak.jalur = rencanaJalur(ak.g.position.clone(), t);
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

// ---------- Kamera per ruangan ----------
const PRESET = {
  semua: [new THREE.Vector3(-1, 9, 27), new THREE.Vector3(-1, 5.5, 0)],
  bos: [new THREE.Vector3(-2, yB + 4.5, 16), new THREE.Vector3(-2, yB + 1.6, -1)],
  workspace: [new THREE.Vector3(-3, yW + 4.5, 16), new THREE.Vector3(-3, yW + 1.6, -1)],
  pantry: [new THREE.Vector3(-4, yP + 4.5, 16), new THREE.Vector3(-4, yP + 1.6, -1)],
};
let terbang = null;
document.querySelectorAll(".kamera button").forEach((b) =>
  b.addEventListener("click", () => {
    document.querySelectorAll(".kamera button").forEach((x) => x.classList.toggle("aktif", x === b));
    const [pos, target] = PRESET[b.dataset.cam];
    terbang = { pos0: camera.position.clone(), tar0: controls.target.clone(), pos, target, t: 0 };
  }),
);

// ---------- Loop animasi ----------
const jamAnim = new THREE.Clock();
function animasi() {
  const dt = Math.min(jamAnim.getDelta(), 0.2);
  const now = performance.now();

  for (const [id, ak] of Object.entries(aktor)) {
    ak.fase += dt * 9;
    const tujuanSaatIni = ak.jalur[0];
    if (tujuanSaatIni) {
      const arah = tujuanSaatIni.clone().sub(ak.g.position);
      const jarak = arah.length();
      const langkah = 5 * dt;
      if (jarak <= langkah) {
        ak.g.position.copy(tujuanSaatIni);
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
      // di meja/jendela: menghadap ke belakang (monitor/kota); di pantry: menghadap kamera
      const st = statusAgent[id]?.status ?? "idle";
      const hadap = st === "idle" && id !== "bos" ? 0 : Math.PI;
      const selisih = Math.atan2(Math.sin(hadap - ak.g.rotation.y), Math.cos(hadap - ak.g.rotation.y));
      ak.g.rotation.y += selisih * Math.min(1, dt * 6);
      ak.kaki[0].rotation.x = ak.kaki[1].rotation.x = 0;
      const kerja = statusAgent[id]?.status === "working" && id !== "bos";
      if (kerja) {
        // mengetik: lengan ke depan bergetar kecil
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
    p.t += dt / 1.3;
    const ke = p.ke.g.position.clone().add(new THREE.Vector3(0, 2, 0));
    const pos = p.dari.clone().lerp(ke, Math.min(p.t, 1));
    pos.y += Math.sin(Math.min(p.t, 1) * Math.PI) * 2.5;
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
    camera.position.lerpVectors(terbang.pos0, terbang.pos, e);
    controls.target.lerpVectors(terbang.tar0, terbang.target, e);
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
  camera.aspect = w / h;
  camera.fov = camera.aspect < 1 ? 62 : 42; // layar sempit (HP): pandangan lebih lebar
  camera.updateProjectionMatrix();
}
new ResizeObserver(ukuran).observe(wadah);

// ---------- Mulai ----------
const info = await fetch("/api/info").then((r) => r.json());
AGENTS = info.agents;
AGENTS.forEach((a, i) => {
  infoAgent[a.id] = a;
  aktor[a.id] = buatKarakter(a, i);
  statusAgent[a.id] = { status: "idle", aktivitas: "" };
  aktor[a.id].g.position.copy(tujuan(a.id, "idle"));
});
document.getElementById("subjudul").textContent =
  `${AGENTS[0].nama} (bos) + ${AGENTS.slice(1).map((a) => a.nama).join(", ")}`;
renderKartu();
ukuran();
animasi();
sambung();
