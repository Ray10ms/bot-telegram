import json
import os
import random
import sys
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8198954294:AAEakuVdkMDANq9PRb6VvcDqZjV6UQzZcmo"
STATUS_FILE = "status.json"
WEEKLY_FILE = "weekly_stats.json"

# === Fungsi Load & Save Daily ===
def load_status():
    today = datetime.now().strftime("%Y-%m-%d")
    default = {
        "date": today,
        "Emray": {"win": False, "lose": False, "mc": False},
        "Billy": {"win": False, "lose": False, "mc": False},
        "Eza": {"win": False, "lose": False, "mc": False},
    }
    if not os.path.exists(STATUS_FILE):
        return default

    with open(STATUS_FILE, "r") as f:
        data = json.load(f)

        # Tambahkan key 'mc' jika belum ada
        for name in ["Emray", "Billy", "Eza"]:
            if "mc" not in data.get(name, {}):
                data[name]["mc"] = False

        # Reset otomatis jika tanggal berbeda
        if data.get("date") != today:
            return default

        return data

def save_status(data):
    with open(STATUS_FILE, "w") as f:
        json.dump(data, f, indent=4)

# === Fungsi Load & Save Weekly ===
def load_weekly():
    if not os.path.exists(WEEKLY_FILE):
        return {
            "Emray": {"win": 0, "lose": 0, "mc": 0},
            "Billy": {"win": 0, "lose": 0, "mc": 0},
            "Eza": {"win": 0, "lose": 0, "mc": 0},
        }
    with open(WEEKLY_FILE, "r") as f:
        return json.load(f)

def save_weekly():
    with open(WEEKLY_FILE, "w") as f:
        json.dump(weekly_stats, f, indent=4)

data_status = load_status()
weekly_stats = load_weekly()

# === Pesan Harian ===
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

# === START & STATUS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Halo geyzz siapp trading hari ini? semoga profit ya Aamiin\n\n"
        "kalo sampe MC berarti kalian yg tolol"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global data_status
    data_status = load_status()
    await update.message.reply_text(generate_message(), parse_mode='Markdown')

# === Helper untuk Win/Lose/MC ===
async def set_win(name, update):
    global data_status
    data_status = load_status()
    data_status[name]["win"] = True
    save_status(data_status)

    weekly_stats[name]["win"] += 1
    save_weekly()

    await update.message.reply_text(generate_message(), parse_mode='Markdown')
    win_msgs = [
        f"Mantap {name}, profit cukup untuk hari ini. Jangan serakah!",
        f"{name}, profit udah cukup, jangan tamak, kalo entry lagi tolol!",
        f"{name}, syukuri profit ini sebelum jadi LOSE.",
        f"Udah profit, {name}, jangan hancurin dengan entry tolol!",
        f"Mantap {name}! Hargai profitmu, jangan greedy!",
        f"Bagus {name}, trader waras tuh tau kapan berhenti.",
        f"{name}, profit secukupnya, jangan kayak orang tolol!",
        f"Good job {name}, tinggal tarik duit, jangan tamak."
    ]
    await update.message.reply_text(random.choice(win_msgs))

async def set_lose(name, update):
    global data_status
    data_status = load_status()
    data_status[name]["lose"] = True
    save_status(data_status)

    weekly_stats[name]["lose"] += 1
    save_weekly()

    await update.message.reply_text(generate_message(), parse_mode='Markdown')
    lose_msgs = [
        f"{name}, LOSE gara-gara gasabaran entry. Tolol amat!",
        f"{name}, lot gede modal tipis, mau kaya instan ya?",
        f"{name}, TP ditunda mulu. Gak puas, ujungnya LOSE!",
        f"{name}, serakah itu penyakit. Makanya LOSE!",
        f"KURANG SABAR {name}, KURANG RAPI, KURANG NGOPI NIH!",
        f"{name}, WIN lu kalah sama emosi, belajar lagi!",
        f"{name}, entry lo random, ya wajar LOSE!",
        f"{name}, LOSE itu tanda otak lu butuh upgrade!"
    ]
    await update.message.reply_text(random.choice(lose_msgs))

async def set_mc(name, update):
    global data_status
    data_status = load_status()
    data_status[name]["mc"] = True
    save_status(data_status)

    weekly_stats[name]["mc"] += 1
    save_weekly()

    mc_msgs = [
        f"DASAR {name.upper()} TOLOLLL!!!! MASIH AJAA SERAKAHH MISKIN",
        f"{name.upper()} MC? OTAK LU DIPAKE GAK?",
        f"MC LAGI YA {name.upper()}? BELAJAR MONEY MANAGEMENT GAK?",
        f"HAHA {name.upper()}!!! MC KAYAK GINI SIH BEBAN MARKET!",
        f"LOT jumbo, skill mikro. Wajar aja MC, {name.upper()}!",
        f"{name.upper()}! MC itu pilihan tolol lu!",
        f"MC karna serakah, {name.upper()} emang hobi miskin!",
        f"Bakar duit tuh kerjaan {name.upper()}!"
    ]
    await update.message.reply_text(random.choice(mc_msgs))

# === Command untuk Win/Lose/MC ===
async def emraywin(update: Update, context: ContextTypes.DEFAULT_TYPE): await set_win("Emray", update)
async def billywin(update: Update, context: ContextTypes.DEFAULT_TYPE): await set_win("Billy", update)
async def ezawin(update: Update, context: ContextTypes.DEFAULT_TYPE): await set_win("Eza", update)

async def emraylose(update: Update, context: ContextTypes.DEFAULT_TYPE): await set_lose("Emray", update)
async def billylose(update: Update, context: ContextTypes.DEFAULT_TYPE): await set_lose("Billy", update)
async def ezalose(update: Update, context: ContextTypes.DEFAULT_TYPE): await set_lose("Eza", update)

async def emraymc(update: Update, context: ContextTypes.DEFAULT_TYPE): await set_mc("Emray", update)
async def billymc(update: Update, context: ContextTypes.DEFAULT_TYPE): await set_mc("Billy", update)
async def ezamc(update: Update, context: ContextTypes.DEFAULT_TYPE): await set_mc("Eza", update)

# === HASIL MINGGUAN ===
async def hasilmingguan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "*Hasil Mingguan (Senin - Jumat)*\n\n"
    for name in weekly_stats:
        stats = weekly_stats[name]
        text += f"{name} :\nWin {stats['win']}x\nLose {stats['lose']}x\nMC {stats['mc']}x\n\n"

        max_key = max(stats, key=stats.get)
        if stats[max_key] == 0:
            text += "(Belum ada data minggu ini)\n\n"
            continue

        if max_key == "win":
            messages = [
                f"Keren {name}, trader panutan!",
                f"{name}, terusin cara trading lo!",
                f"{name}, profit konsisten gini dong!",
                f"Wih {name}, win win win terus!",
                f"Good job {name}, lanjut gas minggu depan!",
                f"Win terbanyak, {name} makin pro!",
                f"{name}, tradingnya mantap parah!",
                f"Keren banget {name}, top trader minggu ini!"
            ]
        elif max_key == "lose":
            messages = [
                f"{name}, kurang fokus nih!",
                f"{name}, belajar lagi biar gak lose mulu!",
                f"Next week jangan ngulang lose, {name}!",
                f"{name}, tradingnya kayak judi ya?",
                f"Improve lagi {name}, jangan jadi beban!",
                f"{name}, belajar sabar!",
                f"Win tipis, lose numpuk {name}!",
                f"{name}, kurang ngopi kali?"
            ]
        else:  # mc
            messages = [
                f"TOLOL {name.upper()}!!! MC TERUSSS!",
                f"{name.upper()} MISKIN KARENA MC!",
                f"{name.upper()} MC LAGI?! OTAK KOSONG!",
                f"MC itu hobi ya {name.upper()}?",
                f"HAHA {name.upper()}! BURN DUIT LAGI!",
                f"{name.upper()} NGAPAIN TRADING KALO MC MLU?",
                f"MC MC MC!!! {name.upper()} GG JUGA!",
                f"{name.upper()}! STOP JADI BEBAN PASAR!"
            ]
        text += random.choice(messages) + "\n\n"

    await update.message.reply_text(text, parse_mode="Markdown")

# === RESET DAILY ===
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

# === RESET MINGGUAN ===
async def resetmingguan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global weekly_stats
    weekly_stats = {
        "Emray": {"win": 0, "lose": 0, "mc": 0},
        "Billy": {"win": 0, "lose": 0, "mc": 0},
        "Eza": {"win": 0, "lose": 0, "mc": 0},
    }
    save_weekly()
    await update.message.reply_text("Statistik mingguan sudah di-reset ke 0.")

# === PAEH (MATIKAN BOT) ===
async def paeh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ARGHHH AKU MATII, TOLONG BERITAHU KELUARGA KU KALO AKU SAYANG MEREKA, ARGHHH!!"
    )
    context.application.stop()
    sys.exit(0)

# === MAIN ===
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("hasilmingguan", hasilmingguan))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("resetmingguan", resetmingguan))
    app.add_handler(CommandHandler("paeh", paeh))
    app.add_handler(CommandHandler("emraywin", emraywin))
    app.add_handler(CommandHandler("emraylose", emraylose))
    app.add_handler(CommandHandler("emraymc", emraymc))
    app.add_handler(CommandHandler("billywin", billywin))
    app.add_handler(CommandHandler("billylose", billylose))
    app.add_handler(CommandHandler("billymc", billymc))
    app.add_handler(CommandHandler("ezawin", ezawin))
    app.add_handler(CommandHandler("ezalose", ezalose))
    app.add_handler(CommandHandler("ezamc", ezamc))

    print("Bot berjalan...")
    app.run_polling()

if __name__ == "__main__":
    main()
