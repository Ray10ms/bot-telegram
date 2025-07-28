import json
import random
import threading
import os
from datetime import datetime
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import google.generativeai as genai

# === TOKEN BOT TELEGRAM ===
TOKEN = "8198954294:AAEakuVdkMDANq9PRb6VvcDqZjV6UQzZcmo"

# === API KEY GEMINI ===
genai.configure(api_key="AIzaSyCGTgebEDjSgzPtzas-MmzNyYq1W678iOo")

# === FLASK SERVER UNTUK UPTIMEROBOT ===
app_flask = Flask('')

@app_flask.route('/')
def home():
    return "Bot Telegram is Alive!"

def run_flask():
    app_flask.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = threading.Thread(target=run_flask)
    t.start()

# === FLAG ON/OFF BOT ===
bot_active = True

# === FILES ===
STATUS_FILE = "status.json"
WEEKLY_FILE = "weekly_stats.json"
PENDINGAN_FILE = "pendingan.json"

# === VARIABEL PENDINGAN ===
last_pendingan = None

# === VARIABEL CHAT HISTORY (UNTUK NGOBROL NYAMBUNG) ===
chat_history = {}  # Menyimpan percakapan per user_id

def add_to_history(user_id, role, content):
    """Tambahkan percakapan ke riwayat per user."""
    if user_id not in chat_history:
        chat_history[user_id] = []
    chat_history[user_id].append({"role": role, "content": content})
    if len(chat_history[user_id]) > 10:  # simpan max 10 percakapan
        chat_history[user_id].pop(0)

# === LOAD & SAVE STATUS ===
def load_status():
    today = datetime.now().strftime("%Y-%m-%d")
    default = {
        "date": today,
        "Emray": {"win": False, "lose": False, "mc": False},
        "Billy": {"win": False, "lose": False, "mc": False},
        "Eza": {"win": False, "lose": False, "mc": False},
    }
    try:
        with open(STATUS_FILE, "r") as f:
            data = json.load(f)
        for name in ["Emray", "Billy", "Eza"]:
            if "mc" not in data.get(name, {}):
                data[name]["mc"] = False
        if data.get("date") != today:
            return default
        return data
    except FileNotFoundError:
        return default

def save_status(data):
    with open(STATUS_FILE, "w") as f:
        json.dump(data, f, indent=4)

# === LOAD & SAVE WEEKLY ===
def load_weekly():
    try:
        with open(WEEKLY_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "Emray": {"win": 0, "lose": 0, "mc": 0},
            "Billy": {"win": 0, "lose": 0, "mc": 0},
            "Eza": {"win": 0, "lose": 0, "mc": 0},
        }

def save_weekly():
    with open(WEEKLY_FILE, "w") as f:
        json.dump(weekly_stats, f, indent=4)

# === LOAD & SAVE PENDINGAN ===
def save_pendingan(teks):
    with open(PENDINGAN_FILE, "w", encoding="utf-8") as f:
        json.dump({"pendingan": teks}, f, ensure_ascii=False)

def load_pendingan():
    if os.path.exists(PENDINGAN_FILE):
        with open(PENDINGAN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("pendingan")
    return None

data_status = load_status()
weekly_stats = load_weekly()
last_pendingan = load_pendingan()

# === GENERATE MESSAGE ===
def generate_message():
    return f"""
*Daily Wins :*\n
Emray (200k) {'✅' if data_status['Emray']['win'] else ''}
Billy (200k) {'✅' if data_status['Billy']['win'] else ''}
Eza (50k naik jika 3hari berturut" profit) {'✅' if data_status['Eza']['win'] else ''}

*Daily Lose :*\n
Emray (100k) {'💀' if data_status['Emray']['lose'] else ''}
Billy (100k) {'💀' if data_status['Billy']['lose'] else ''}
Eza (30k) {'💀' if data_status['Eza']['lose'] else ''}

*Daily MC :*\n
Emray (MC) {'🧠❌' if data_status['Emray']['mc'] else ''}
Billy (MC) {'🧠❌' if data_status['Billy']['mc'] else ''}
Eza (MC) {'🧠❌' if data_status['Eza']['mc'] else ''}
"""

# === COMMANDS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global bot_active
    bot_active = True
    await update.message.reply_text(
        "Bot sudah AKTIF kembali!\n\nHalo geyzz siapp trading hari ini? semoga profit ya Aamiin\n"
        "kalo sampe MC berarti kalian yg tolol"
    )

async def paeh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global bot_active
    bot_active = False
    await update.message.reply_text(
        "ARGHHH AKU DIAM!! BOT NONAKTIF. Ketik /start untuk hidupkan lagi!"
    )

async def resetchat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_history[user_id] = []
    await update.message.reply_text("Riwayat percakapan sudah di-reset. Mulai ngobrol dari awal!")

async def tamparan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not bot_active:
        return
    pesan = random.choice([
        "namanya orang berilmu, itu makin kalem hidupnya, ga buru - buru ambil keputusan",
        "makin ringan tangan kamu pencet, makin Tolol kamu"
    ])
    await update.message.reply_text(pesan)

async def pendingan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_pendingan
    if not bot_active:
        return

    if update.message.reply_to_message:
        pesan = update.message.reply_to_message.text or update.message.reply_to_message.caption
        if pesan:
            last_pendingan = pesan
            save_pendingan(pesan)
            await update.message.reply_text(f"Pendingan ditandai:\n\n{pesan}")
        else:
            await update.message.reply_text(
                "Pesan reply kosong atau tidak bisa dibaca.\n"
                "Coba kirim pesan murni teks tanpa format aneh."
            )
    else:
        pending = last_pendingan or load_pendingan()
        if pending:
            await update.message.reply_text(f"Pendingan terakhir:\n\n{pending}")
        else:
            await update.message.reply_text("Belum ada pendingan yang ditandai.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not bot_active:
        return
    global data_status
    data_status = load_status()
    await update.message.reply_text(generate_message(), parse_mode="Markdown")

# === FUNGSI GEMINI AI ===
async def tanya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not bot_active:
        return

    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text("Tulis pertanyaan setelah /tanya atau reply pesan bot.")
        return

    prompt = " ".join(context.args)
    add_to_history(user_id, "user", prompt)
    await update.message.reply_text("Tunggu sebentar, lagi mikir...")

    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content(
            [{"role": msg["role"], "parts": [msg["content"]]} for msg in chat_history[user_id]]
        )
        jawaban = response.text
        add_to_history(user_id, "model", jawaban)

        await update.message.reply_text(jawaban)
    except Exception as e:
        await update.message.reply_text(f"Terjadi error: {str(e)}")

# === AUTO REPLY KE PESAN BOT ===
async def auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not bot_active:
        return

    if update.message.reply_to_message and update.message.reply_to_message.from_user.is_bot:
        user_id = update.effective_user.id
        prompt = update.message.text
        add_to_history(user_id, "user", prompt)
        await update.message.reply_text("Sebentar ya, aku mikir dulu...")

        try:
            model = genai.GenerativeModel("models/gemini-1.5-flash")
            response = model.generate_content(
                [{"role": msg["role"], "parts": [msg["content"]]} for msg in chat_history[user_id]]
            )
            jawaban = response.text
            add_to_history(user_id, "model", jawaban)
            await update.message.reply_text(jawaban)
        except Exception as e:
            await update.message.reply_text(f"Terjadi error: {str(e)}")

# === SET WIN/LOSE/MC ===
async def set_win(name, update):
    global data_status
    data_status = load_status()
    data_status[name]["win"] = True
    save_status(data_status)
    weekly_stats[name]["win"] += 1
    save_weekly()
    await update.message.reply_text(generate_message(), parse_mode="Markdown")
    await update.message.reply_text(random.choice([
        f"Mantap {name}, profit cukup untuk hari ini. Jangan serakah!",
        f"{name}, profit udah cukup, jangan tamak, kalo entry lagi tolol!",
        f"{name}, syukuri profit ini sebelum jadi LOSE.",
        f"Udah profit, {name}, jangan hancurin dengan entry tolol!",
        f"Mantap {name}! Hargai profitmu, jangan greedy!",
        f"Bagus {name}, trader waras tuh tau kapan berhenti.",
        f"{name}, profit secukupnya, jangan kayak orang tolol!",
        f"Good job {name}, tinggal tarik duit, jangan tamak."
    ]))

async def set_lose(name, update):
    global data_status
    data_status = load_status()
    data_status[name]["lose"] = True
    save_status(data_status)
    weekly_stats[name]["lose"] += 1
    save_weekly()
    await update.message.reply_text(generate_message(), parse_mode="Markdown")
    await update.message.reply_text(random.choice([
        f"{name}, LOSE gara-gara gasabaran entry. Tolol amat!",
        f"{name}, lot gede modal tipis, mau kaya instan ya?",
        f"{name}, TP ditunda mulu. Gak puas, ujungnya LOSE!",
        f"{name}, serakah itu penyakit. Makanya LOSE!",
        f"KURANG SABAR {name}, KURANG RAPI, KURANG NGOPI NIH!",
        f"{name}, WIN lu kalah sama emosi, belajar lagi!",
        f"{name}, entry lo random, ya wajar LOSE!",
        f"{name}, LOSE itu tanda otak lu butuh upgrade!"
    ]))

async def set_mc(name, update):
    global data_status
    data_status[name]["mc"] = True
    save_status(data_status)
    weekly_stats[name]["mc"] += 1
    save_weekly()
    await update.message.reply_text(random.choice([
        f"DASAR {name.upper()} TOLOLLL!!!! MASIH AJAA SERAKAHH MISKIN",
        f"{name.upper()} MC? OTAK LU DIPAKE GAK?",
        f"MC LAGI YA {name.upper()}? BELAJAR MONEY MANAGEMENT GAK?",
        f"HAHA {name.upper()}!!! MC KAYAK GINI SIH BEBAN MARKET!",
        f"LOT jumbo, skill mikro. Wajar aja MC, {name.upper()}!",
        f"{name.upper()}! MC itu pilihan tolol lu!",
        f"MC karna serakah, {name.upper()} emang hobi miskin!",
        f"Bakar duit tuh kerjaan {name.upper()}!"
    ]))

# === RESET STATUS ===
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now().strftime("%Y-%m-%d")
    global data_status
    data_status = {
        "date": today,
        "Emray": {"win": False, "lose": False, "mc": False},
        "Billy": {"win": False, "lose": False, "mc": False},
        "Eza": {"win": False, "lose": False, "mc": False},
    }
    save_status(data_status)
    await update.message.reply_text("Status harian sudah di-reset untuk hari ini!")

async def resetmingguan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global weekly_stats
    weekly_stats = {
        "Emray": {"win": 0, "lose": 0, "mc": 0},
        "Billy": {"win": 0, "lose": 0, "mc": 0},
        "Eza": {"win": 0, "lose": 0, "mc": 0},
    }
    save_weekly()
    await update.message.reply_text("Statistik mingguan sudah di-reset ke 0.")

async def hasilmingguan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "*Hasil Mingguan (Senin - Jumat)*\n\n"
    for name in weekly_stats:
        stats = weekly_stats[name]
        text += f"{name} :\nWin {stats['win']}x\nLose {stats['lose']}x\nMC {stats['mc']}x\n\n"
        max_key = max(stats, key=stats.get)
        if stats[max_key] == 0:
            text += "(Belum ada data minggu ini)\n\n"
            continue
        messages = {
            "win": [
                f"Keren {name}, trader panutan!",
                f"{name}, terusin cara trading lo!",
                f"{name}, profit konsisten gini dong!",
                f"Wih {name}, win win win terus!",
                f"Good job {name}, lanjut gas minggu depan!",
                f"Win terbanyak, {name} makin pro!",
                f"{name}, tradingnya mantap parah!",
                f"Keren banget {name}, top trader minggu ini!"
            ],
            "lose": [
                f"{name}, kurang fokus nih!",
                f"{name}, belajar lagi biar gak lose mulu!",
                f"Next week jangan ngulang lose, {name}!",
                f"{name}, tradingnya kayak judi ya?",
                f"Improve lagi {name}, jangan jadi beban!",
                f"{name}, belajar sabar!",
                f"Win tipis, lose numpuk {name}!",
                f"{name}, kurang ngopi kali?"
            ],
            "mc": [
                f"TOLOL {name.upper()}!!! MC TERUSSS!",
                f"{name.upper()} MISKIN KARENA MC!",
                f"{name.upper()} MC LAGI?! OTAK KOSONG!",
                f"MC itu hobi ya {name.upper()}?",
                f"HAHA {name.upper()}! BURN DUIT LAGI!",
                f"{name.upper()} NGAPAIN TRADING KALO MC MLU?",
                f"MC MC MC!!! {name.upper()} GG JUGA!",
                f"{name.upper()}! STOP JADI BEBAN PASAR!"
            ]
        }
        text += random.choice(messages[max_key]) + "\n\n"
    await update.message.reply_text(text, parse_mode="Markdown")

# === MAIN ===
def main():
    keep_alive()
    app = ApplicationBuilder().token(TOKEN).build()

    # COMMANDS
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("paeh", paeh))
    app.add_handler(CommandHandler("tamparan", tamparan))
    app.add_handler(CommandHandler("pendingan", pendingan))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("tanya", tanya))
    app.add_handler(CommandHandler("resetchat", resetchat))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("resetmingguan", resetmingguan))
    app.add_handler(CommandHandler("hasilmingguan", hasilmingguan))

    # COMMANDS WIN/LOSE/MC
    app.add_handler(CommandHandler("emraywin", lambda u, c: set_win("Emray", u)))
    app.add_handler(CommandHandler("billywin", lambda u, c: set_win("Billy", u)))
    app.add_handler(CommandHandler("ezawin", lambda u, c: set_win("Eza", u)))
    app.add_handler(CommandHandler("emraylose", lambda u, c: set_lose("Emray", u)))
    app.add_handler(CommandHandler("billylose", lambda u, c: set_lose("Billy", u)))
    app.add_handler(CommandHandler("ezalose", lambda u, c: set_lose("Eza", u)))
    app.add_handler(CommandHandler("emraymc", lambda u, c: set_mc("Emray", u)))
    app.add_handler(CommandHandler("billymc", lambda u, c: set_mc("Billy", u)))
    app.add_handler(CommandHandler("ezamc", lambda u, c: set_mc("Eza", u)))

    # AUTO REPLY HANDLER
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_reply))

    print("Bot berjalan...")
    app.run_polling()

if __name__ == "__main__":
    main()
