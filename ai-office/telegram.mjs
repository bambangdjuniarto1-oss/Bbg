// Integrasi Telegram (opsional). Aktif kalau TELEGRAM_BOT_TOKEN dan TELEGRAM_CHAT_ID diisi.
// - Kirim brief dari grup/chat Telegram:  Nama Klien: isi brief ...
// - Semua laporan agent dikirim balik ke chat yang sama.
// Hanya chat dengan ID = TELEGRAM_CHAT_ID yang dilayani, supaya orang lain tidak bisa memerintah tim kamu.

export function mulaiTelegram({ terimaBrief, bus, agents }) {
  const token = process.env.TELEGRAM_BOT_TOKEN;
  const chatId = process.env.TELEGRAM_CHAT_ID;
  if (!token || !chatId) {
    console.log("   Telegram: nonaktif (isi TELEGRAM_BOT_TOKEN dan TELEGRAM_CHAT_ID untuk mengaktifkan)");
    return;
  }
  const api = (method, body) =>
    fetch(`https://api.telegram.org/bot${token}/${method}`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body),
    }).then((r) => r.json());

  const kirim = (text) =>
    api("sendMessage", { chat_id: chatId, text: text.slice(0, 4000) }).catch((e) =>
      console.error("[telegram] gagal kirim:", e.message),
    );

  const nama = Object.fromEntries(agents.map((a) => [a.id, `${a.nama} · ${a.jabatan}`]));
  bus.on("event", (ev) => {
    if (ev.type === "chat") kirim(`[${nama[ev.from] ?? ev.from}]\n${ev.text}`);
  });

  let offset = 0;
  const poll = async () => {
    try {
      const res = await api("getUpdates", { offset, timeout: 30, allowed_updates: ["message"] });
      for (const u of res.result ?? []) {
        offset = u.update_id + 1;
        const m = u.message;
        if (!m?.text || String(m.chat.id) !== String(chatId)) continue;
        const teks = m.text.replace(/^\/brief(@\w+)?\s*/i, "");
        const i = teks.indexOf(":");
        if (i < 1) {
          kirim('Format brief: "Nama Klien: isi brief". Contoh:\nToko Kue Manis: buatkan promo paket ulang tahun, riset kompetitor, copy iklan, website, dan carousel IG.');
          continue;
        }
        try {
          await terimaBrief({ klien: teks.slice(0, i), brief: teks.slice(i + 1) });
        } catch (err) {
          kirim(`⚠️ ${err.message}`);
        }
      }
    } catch (err) {
      console.error("[telegram]", err.message);
      await new Promise((r) => setTimeout(r, 5000));
    }
    setImmediate(poll);
  };
  poll();
  console.log("   Telegram: aktif");
}
