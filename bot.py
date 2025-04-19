
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram.dispatcher.filters import Command
import os
from dotenv import load_dotenv

load_dotenv()
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(bot)
admin_id = int(os.getenv("ADMIN_ID"))

# Créer base si elle n'existe pas
conn = sqlite3.connect("db.sqlite3")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS produits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT,
    description TEXT,
    prix TEXT,
    media TEXT
)''')
conn.commit()

@dp.message_handler(commands=["start"])
async def start_cmd(msg: types.Message):
    cursor.execute("SELECT id, nom FROM produits")
    produits = cursor.fetchall()
    text = "Bienvenue sur *BROLY69* !\nVoici nos produits :\n\n"
    for pid, nom in produits:
        text += f"• {nom} - /product_{pid}\n"
    await msg.answer(text, parse_mode=ParseMode.MARKDOWN)

@dp.message_handler(lambda m: m.text and m.text.startswith("/product_"))
async def product_details(msg: types.Message):
    pid = msg.text.split("_")[1]
    cursor.execute("SELECT nom, description, prix, media FROM produits WHERE id=?", (pid,))
    data = cursor.fetchone()
    if data:
        nom, desc, prix, media = data
        caption = f"*{nom}*\n\n{desc}\n\n{prix}"
        if media.endswith(".mp4"):
            await msg.answer_video(video=media, caption=caption, parse_mode=ParseMode.MARKDOWN)
        else:
            await msg.answer_photo(photo=media, caption=caption, parse_mode=ParseMode.MARKDOWN)

@dp.message_handler(commands=["add"])
async def add_product(msg: types.Message):
    if msg.from_user.id != admin_id:
        return await msg.reply("Accès refusé.")
    await msg.reply("Envoie les infos du produit comme ceci :\nnom | description | prix | lien_media")

@dp.message_handler(lambda m: m.from_user.id == admin_id and "|" in m.text)
async def save_product(msg: types.Message):
    parts = msg.text.split("|")
    if len(parts) == 4:
        nom, desc, prix, media = [p.strip() for p in parts]
        cursor.execute("INSERT INTO produits (nom, description, prix, media) VALUES (?, ?, ?, ?)",
                       (nom, desc, prix, media))
        conn.commit()
        await msg.reply("Produit ajouté !")
    else:
        await msg.reply("Format incorrect.")

@dp.message_handler(commands=["list"])
async def list_products(msg: types.Message):
    if msg.from_user.id != admin_id:
        return await msg.reply("Accès refusé.")
    cursor.execute("SELECT id, nom FROM produits")
    produits = cursor.fetchall()
    text = "Produits enregistrés :\n"
    for pid, nom in produits:
        text += f"{pid}: {nom}\n"
    await msg.reply(text)

@dp.message_handler(commands=["delete"])
async def delete_product(msg: types.Message):
    if msg.from_user.id != admin_id:
        return await msg.reply("Accès refusé.")
    await msg.reply("Envoie l'ID du produit à supprimer.")

@dp.message_handler(lambda m: m.from_user.id == admin_id and m.text.isdigit())
async def confirm_delete(msg: types.Message):
    pid = int(msg.text)
    cursor.execute("DELETE FROM produits WHERE id=?", (pid,))
    conn.commit()
    await msg.reply("Produit supprimé.")


@dp.message_handler(commands=["edit"])
async def edit_product(msg: types.Message):
    if msg.from_user.id != admin_id:
        return await msg.reply("Accès refusé.")
    await msg.reply("Envoie les nouvelles infos comme ceci :\nid | nom | description | prix | media")

@dp.message_handler(lambda m: m.from_user.id == admin_id and "|" in m.text and m.text.split("|")[0].strip().isdigit())
async def update_product(msg: types.Message):
    parts = msg.text.split("|")
    if len(parts) == 5:
        pid, nom, desc, prix, media = [p.strip() for p in parts]
        cursor.execute("UPDATE produits SET nom=?, description=?, prix=?, media=? WHERE id=?",
                       (nom, desc, prix, media, int(pid)))
        conn.commit()
        await msg.reply("Produit mis à jour !")
    else:
        await msg.reply("Format incorrect. Utilise : id | nom | description | prix | media")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
