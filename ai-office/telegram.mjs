// Integrasi Telegram (opsional), diatur dari Pengaturan > Telegram.
// - Kirim brief dari chat/grup:  Nama Klien: isi brief ...
// - Semua laporan agent dikirim balik ke chat yang sama.
// Hanya chat dengan ID yang ditentukan yang dilayani, supaya orang lain tidak bisa memerintah tim kamu.
import { ambil } from "./settings.mjs";

let generasi = 0;
let pasang = false;

const api = (token, method, body) =>
  fetch(`https://api.telegram.org/bot${token}/${method}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  }).then((r) => r.json());

export async function tesTelegram({ token, chatId }) {
  const me = await api(token, "getMe", {});
  if (!me.ok) throw new Error(`Token ditolak Telegram: ${me.description ?? "tidak valid"}`);
  const kirim = await api(token, "sendMessage", { chat_id: chatId, text: "✅ Kantor Virtual AI tersambung ke chat ini." });
  if (!kirim.ok) throw new Error(`Bot @${me.result.username} tidak bisa mengirim ke chat ${chatId}: ${kirim.description}`);
  return `Bot @${me.result.username} tersambung`;
}

// Panggil saat aplikasi mulai dan setiap kali pengaturan Telegram disimpan.
export function aturTelegram({ terimaBrief, bus }) {
  const gen = ++generasi; // menghentikan loop polling lama
  const { aktif, token, chatId } = ambil().telegram;

  if (!pasang) {
    pasang = true;
    bus.on("event", (ev) => {
      const t = ambil().telegram;
      if (ev.type !== "chat" || !t.aktif || !t.token || !t.chatId) return;
      const tim = ambil().tim;
      const a = [tim.orchestrator, ...tim.anggota].find((x) => x.id === ev.from);
      api(t.token, "sendMessage", { chat_id: t.chatId, text: `[${a ? `${a.nama} · ${a.jabatan}` : ev.from}]\n${ev.text}`.slice(0, 4000) })
        .catch((e) => console.error("[telegram] gagal kirim:", e.message));
    });
  }

  if (!aktif || !token || !chatId) {
    console.log("   Telegram: nonaktif (atur di Pengaturan > Telegram)");
    return;
  }
  console.log("   Telegram: aktif");

  let offset = 0;
  const poll = async () => {
    if (gen !== generasi) return;
    try {
      const res = await api(token, "getUpdates", { offset, timeout: 25, allowed_updates: ["message"] });
      if (gen !== generasi) return;
      for (const u of res.result ?? []) {
        offset = u.update_id + 1;
        const m = u.message;
        if (!m?.text || String(m.chat.id) !== String(chatId)) continue;
        const teks = m.text.replace(/^\/brief(@\w+)?\s*/i, "");
        const i = teks.indexOf(":");
        if (i < 1) {
          api(token, "sendMessage", {
            chat_id: chatId,
            text: 'Format brief: "Nama Klien: isi brief". Contoh:\nToko Kue Manis: buatkan promo paket ulang tahun.',
          });
          continue;
        }
        try {
          await terimaBrief({ klien: teks.slice(0, i), brief: teks.slice(i + 1) });
        } catch (err) {
          api(token, "sendMessage", { chat_id: chatId, text: `⚠️ ${err.message}` });
        }
      }
    } catch (err) {
      console.error("[telegram]", err.message);
      await new Promise((r) => setTimeout(r, 5000));
    }
    setImmediate(poll);
  };
  poll();
}
