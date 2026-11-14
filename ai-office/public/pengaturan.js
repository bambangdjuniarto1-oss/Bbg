// Halaman Pengaturan: Koneksi AI, Tim & Persona, Telegram. Semua disimpan lewat aplikasi,
// pengguna tidak perlu mengubah file apa pun.
const $ = (s, el = document) => el.querySelector(s);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const dialog = $("#pengaturan");
let data = null;

async function api(path, body) {
  const res = await fetch(path, body === undefined ? {} : {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });
  const j = await res.json().catch(() => ({ ok: false, error: `HTTP ${res.status}` }));
  if (j.ok === false) throw new Error(j.error || "Gagal");
  return j;
}

function pesan(el, teks, jenis = "") {
  el.textContent = teks;
  el.className = `status-msg ${jenis}`;
}

// ---------- Tab ----------
function bukaTab(nama) {
  dialog.querySelectorAll("[data-tab]").forEach((b) => b.classList.toggle("aktif", b.dataset.tab === nama));
  dialog.querySelectorAll("[data-panel]").forEach((p) => (p.hidden = p.dataset.panel !== nama));
}
dialog.querySelectorAll("[data-tab]").forEach((b) => b.addEventListener("click", () => bukaTab(b.dataset.tab)));
$("#tutup-pengaturan").addEventListener("click", () => dialog.close());

export async function bukaPengaturan(tab = "koneksi") {
  data = await api("/api/pengaturan");
  renderKoneksi();
  renderTim();
  renderTelegram();
  bukaTab(tab);
  if (!dialog.open) dialog.showModal();
}

// ---------- Koneksi AI ----------
const PENJELASAN = {
  demo: "Coba tampilan dan alur kerja tanpa AI. Hasilnya hanya contoh.",
  anthropic: 'Tempel API key dari <a href="https://platform.claude.com/settings/keys" target="_blank" rel="noopener">platform.claude.com → API Keys</a>.',
  "anthropic-login": "Tanpa API key: login dengan akun <b>Claude Console</b> di browser. Butuh Anthropic CLI (<code>ant</code>) di komputer ini. Pemakaian ditagih ke akun Console, bukan langganan Claude Pro/Max.",
  openrouter: "Satu akun untuk banyak model (Claude, GPT, Gemini, Llama, dll). Klik <b>Login dengan OpenRouter</b>, tidak perlu menyalin key. Atau tempel API key dari openrouter.ai.",
  openai: 'Tempel API key dari <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener">platform.openai.com</a>.',
  gemini: 'Tempel API key dari <a href="https://aistudio.google.com/apikey" target="_blank" rel="noopener">Google AI Studio</a>.',
  ollama: 'AI gratis yang berjalan di komputer sendiri, tanpa key. Pasang dari <a href="https://ollama.com" target="_blank" rel="noopener">ollama.com</a>, lalu unduh model yang mendukung <i>tool calling</i>, contoh: <code>ollama pull llama3.1</code>.',
  custom: "Layanan lain yang kompatibel dengan format OpenAI (Groq, DeepSeek, LM Studio, dll). Isi base URL dan API key bila perlu.",
};

function renderKoneksi() {
  const k = data.koneksi;
  const pilihan = Object.entries(data.provider)
    .map(([id, p]) => `<label class="opsi-provider"><input type="radio" name="provider" value="${id}" ${id === k.provider ? "checked" : ""}><span>${esc(p.label)}</span></label>`)
    .join("");
  $("#daftar-provider").innerHTML = pilihan;
  $("#f-model").value = k.model;
  $("#f-model-tim").value = k.modelTim;
  $("#f-base-url").value = k.baseUrl;
  $("#f-api-key").value = "";
  pesan($("#status-koneksi"), data.status.siap ? `Terhubung: ${data.provider[k.provider].label}` : `Belum siap: ${data.status.alasan}`, data.status.siap ? "ok" : "");
  $("#daftar-provider").onchange = sesuaikanForm;
  sesuaikanForm();
}

function providerDipilih() {
  return $('input[name="provider"]:checked')?.value ?? "demo";
}

function sesuaikanForm() {
  const p = providerDipilih();
  const info = data.provider[p];
  $("#penjelasan-provider").innerHTML = PENJELASAN[p] ?? "";
  const slot = p.startsWith("anthropic") ? "anthropic" : p;
  $("#baris-key").hidden = !(info.butuhKey || p === "custom");
  $("#f-api-key").placeholder = data.koneksi.keyTersimpan[slot] ? `Tersimpan: ${data.koneksi.keyTersimpan[slot]} (kosongkan bila tidak diganti)` : "Tempel API key di sini";
  $("#hapus-key").hidden = !data.koneksi.keyTersimpan[slot];
  $("#baris-url").hidden = !(p === "custom" || p === "ollama");
  $("#f-base-url").placeholder = p === "ollama" ? "http://localhost:11434/v1" : "https://.../v1";
  $("#baris-model").hidden = p === "demo";
  $("#blok-login-claude").hidden = p !== "anthropic-login";
  $("#blok-login-openrouter").hidden = p !== "openrouter";
  if (p === "anthropic-login") cekLoginClaude();
  if (p.startsWith("anthropic") && !$("#f-model").value) $("#f-model").placeholder = "claude-opus-5-5 (bawaan)";
  else $("#f-model").placeholder = "Pilih atau ketik nama model";
}

async function simpanKoneksi(hapusKey = false) {
  const body = {
    provider: providerDipilih(),
    apiKey: $("#f-api-key").value,
    hapusKey,
    baseUrl: $("#f-base-url").value,
    model: $("#f-model").value,
    modelTim: $("#f-model-tim").value,
  };
  const r = await api("/api/pengaturan/koneksi", body);
  data = await api("/api/pengaturan");
  renderKoneksi();
  return r;
}

$("#simpan-koneksi").addEventListener("click", async () => {
  const el = $("#status-koneksi");
  try {
    pesan(el, "Menyimpan…");
    const r = await simpanKoneksi();
    pesan(el, r.status.siap ? "Tersimpan ✅ Klik “Tes koneksi” untuk memastikan." : `Tersimpan, tapi belum siap: ${r.status.alasan}`, r.status.siap ? "ok" : "");
    if (providerDipilih() !== "demo") muatModel(true);
  } catch (e) {
    pesan(el, e.message, "error");
  }
});
$("#hapus-key").addEventListener("click", async () => {
  if (!confirm("Hapus API key yang tersimpan untuk provider ini?")) return;
  await simpanKoneksi(true).catch((e) => pesan($("#status-koneksi"), e.message, "error"));
});

$("#tes-koneksi").addEventListener("click", async () => {
  const el = $("#status-koneksi");
  try {
    pesan(el, "Menyimpan & mengetes… (bisa beberapa detik)");
    await simpanKoneksi();
    const r = await api("/api/tes-koneksi", {});
    pesan(el, `Berhasil ✅ Model ${r.model} menjawab: “${r.jawaban}”`, "ok");
  } catch (e) {
    pesan(el, `Gagal: ${e.message}`, "error");
  }
});

async function muatModel(diam = false) {
  const el = $("#status-koneksi");
  try {
    if (!diam) pesan(el, "Memuat daftar model…");
    const r = await api("/api/model");
    $("#daftar-model").innerHTML = r.model.map((m) => `<option value="${esc(m.id)}">${esc(m.nama)}</option>`).join("");
    if (!diam) pesan(el, `${r.model.length} model tersedia. Klik kolom model untuk memilih.`, "ok");
  } catch (e) {
    if (!diam) pesan(el, `Tidak bisa memuat model: ${e.message}`, "error");
  }
}
$("#muat-model").addEventListener("click", async () => {
  await simpanKoneksi().catch(() => {});
  muatModel();
});

// Login akun Claude Console lewat Anthropic CLI
async function cekLoginClaude() {
  const el = $("#status-login-claude");
  try {
    const s = await api("/api/claude-login");
    $("#instal-ant").hidden = s.terpasang;
    $("#login-claude").disabled = !s.terpasang || s.berjalan;
    pesan(el, !s.terpasang ? "Anthropic CLI belum terpasang di komputer ini." : s.masuk ? "Sudah login ✅" : "Belum login.", s.masuk ? "ok" : "");
  } catch (e) {
    pesan(el, e.message, "error");
  }
}
$("#login-claude").addEventListener("click", async () => {
  const el = $("#status-login-claude");
  await api("/api/claude-login", {});
  pesan(el, "Jendela login dibuka di browser. Selesaikan login di sana, lalu kembali ke sini…");
  $("#login-claude").disabled = true;
  const cek = setInterval(async () => {
    const r = await api("/api/claude-login/hasil").catch(() => null);
    if (!r || r.berjalan) return;
    clearInterval(cek);
    if (r.hasil?.ok) {
      pesan(el, "Login berhasil ✅ Klik Simpan, lalu Tes koneksi.", "ok");
    } else {
      pesan(el, `Login belum berhasil: ${r.hasil?.pesan || "dibatalkan"}`, "error");
    }
    $("#login-claude").disabled = false;
  }, 2000);
});
$("#login-openrouter").addEventListener("click", async () => {
  // simpan pilihan dulu, lalu pindah ke halaman login OpenRouter
  await simpanKoneksi().catch(() => {});
  location.href = "/auth/openrouter/mulai";
});

// ---------- Tim & Persona ----------
let draftTim = null;

function renderTim() {
  draftTim = structuredClone(data.tim);
  $("#pilih-preset").innerHTML = Object.entries(data.preset)
    .map(([id, p]) => `<option value="${id}">${esc(p.nama)}</option>`)
    .join("");
  $("#info-preset").textContent = data.preset[$("#pilih-preset").value]?.deskripsi ?? "";
  $("#catatan-web").hidden = data.webSearch;
  gambarTim();
}
$("#pilih-preset").addEventListener("change", () => ($("#info-preset").textContent = data.preset[$("#pilih-preset").value]?.deskripsi ?? ""));

function kartuPersona(a, i) {
  const bos = i === -1;
  return `<div class="persona" data-i="${i}">
    <div class="persona-head">
      <input type="color" data-f="warna" value="${esc(a.warna)}" title="Warna baju">
      <input data-f="nama" value="${esc(a.nama)}" placeholder="Nama" maxlength="30">
      <input data-f="jabatan" value="${esc(a.jabatan)}" placeholder="Jabatan / peran" maxlength="40">
      ${bos ? '<span class="badge">Bos</span>' : `<button type="button" class="hapus" data-hapus="${i}" title="Hapus anggota">✕</button>`}
    </div>
    <textarea data-f="instruksi" rows="${bos ? 5 : 4}" placeholder="${bos ? "Gaya memimpin, urutan kerja, isi laporan akhir…" : "Peran, keahlian, apa yang harus dihasilkan, dan nama file output (contoh: output/riset.md)"}">${esc(a.instruksi)}</textarea>
    ${bos ? "" : `<label class="cek"><input type="checkbox" data-f="webSearch" ${a.webSearch ? "checked" : ""}> Boleh mencari di internet</label>`}
  </div>`;
}

function gambarTim() {
  $("#persona-bos").innerHTML = kartuPersona(draftTim.orchestrator, -1);
  $("#persona-anggota").innerHTML = draftTim.anggota.map(kartuPersona).join("");
  $("#jumlah-anggota").textContent = `${draftTim.anggota.length} / ${data.maksAnggota}`;
  $("#tambah-anggota").disabled = draftTim.anggota.length >= data.maksAnggota;
}

// sinkronkan input ke draft
$("#panel-tim").addEventListener("input", (e) => {
  const kartu = e.target.closest(".persona");
  const f = e.target.dataset.f;
  if (!kartu || !f) return;
  const i = Number(kartu.dataset.i);
  const target = i === -1 ? draftTim.orchestrator : draftTim.anggota[i];
  target[f] = e.target.type === "checkbox" ? e.target.checked : e.target.value;
});
$("#panel-tim").addEventListener("click", (e) => {
  const i = e.target.dataset.hapus;
  if (i === undefined) return;
  const a = draftTim.anggota[Number(i)];
  if (!confirm(`Hapus ${a.nama || "anggota ini"} dari tim?`)) return;
  draftTim.anggota.splice(Number(i), 1);
  gambarTim();
});
const WARNA = ["#5dade2", "#c39bd3", "#58d68d", "#f1948a", "#f7dc6f", "#85c1e9", "#a3e4d7", "#f0b27a", "#bb8fce", "#76d7c4", "#f5b7b1", "#aed6f1"];
$("#tambah-anggota").addEventListener("click", () => {
  draftTim.anggota.push({ nama: "", jabatan: "", warna: WARNA[draftTim.anggota.length % WARNA.length], instruksi: "", webSearch: false });
  gambarTim();
  $("#persona-anggota").lastElementChild?.querySelector('[data-f="nama"]').focus();
});

$("#simpan-tim").addEventListener("click", async () => {
  const el = $("#status-tim");
  const kosong = draftTim.anggota.find((a) => !a.nama.trim() || !a.instruksi.trim());
  if (kosong) return pesan(el, "Setiap anggota wajib punya nama dan instruksi.", "error");
  try {
    pesan(el, "Menyimpan…");
    await api("/api/pengaturan/tim", { tim: draftTim });
    pesan(el, "Tersimpan ✅ Kantor dimuat ulang…", "ok");
  } catch (e) {
    pesan(el, e.message, "error");
  }
});
$("#pakai-preset").addEventListener("click", async () => {
  const el = $("#status-tim");
  if (!confirm("Ganti seluruh tim dengan template ini? Tim saat ini akan ditimpa.")) return;
  try {
    await api("/api/pengaturan/tim", { preset: $("#pilih-preset").value });
    pesan(el, "Template dipasang ✅ Kantor dimuat ulang…", "ok");
  } catch (e) {
    pesan(el, e.message, "error");
  }
});

// ---------- Telegram ----------
function renderTelegram() {
  const t = data.telegram;
  $("#tg-aktif").checked = t.aktif;
  $("#tg-chat").value = t.chatId;
  $("#tg-token").value = "";
  $("#tg-token").placeholder = t.tokenTersimpan ? `Tersimpan: ${t.tokenTersimpan} (kosongkan bila tidak diganti)` : "Token dari @BotFather";
}
async function simpanTelegram() {
  await api("/api/pengaturan/telegram", { aktif: $("#tg-aktif").checked, token: $("#tg-token").value, chatId: $("#tg-chat").value });
  data = await api("/api/pengaturan");
  renderTelegram();
}
$("#simpan-telegram").addEventListener("click", async () => {
  try {
    await simpanTelegram();
    pesan($("#status-telegram"), "Tersimpan ✅", "ok");
  } catch (e) {
    pesan($("#status-telegram"), e.message, "error");
  }
});
$("#tes-telegram").addEventListener("click", async () => {
  try {
    await simpanTelegram();
    const r = await api("/api/tes-telegram", {});
    pesan($("#status-telegram"), `${r.pesan} ✅ Cek pesan di Telegram.`, "ok");
  } catch (e) {
    pesan($("#status-telegram"), e.message, "error");
  }
});

// Tombol ⚙️ dan pembukaan otomatis (misalnya setelah login OpenRouter)
$("#buka-pengaturan").addEventListener("click", () => bukaPengaturan());
const q = new URLSearchParams(location.search);
if (q.get("pengaturan")) {
  bukaPengaturan(q.get("pengaturan")).then(() => {
    if (q.get("login") === "openrouter") pesan($("#status-koneksi"), "Login OpenRouter berhasil ✅ Pilih model, klik Simpan, lalu Tes koneksi.", "ok");
  });
  history.replaceState(null, "", "/");
}
