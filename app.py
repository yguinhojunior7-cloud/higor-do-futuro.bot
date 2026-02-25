import os
import sqlite3
import csv
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

TOKEN = os.getenv("TOKEN")

# Criar banco
def init_db():
    conn = sqlite3.connect("gastos.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            categoria TEXT,
            valor REAL
        )
    """)
    conn.commit()
    conn.close()

async def salvar_gasto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text.lower().split()

    if len(texto) < 2:
        await update.message.reply_text("Formato: categoria valor\nEx: gasolina 120")
        return

    categoria = texto[0]

    try:
        valor = float(texto[1])
    except:
        await update.message.reply_text("Valor inválido.")
        return

    data = datetime.now().strftime("%d/%m/%Y")

    conn = sqlite3.connect("gastos.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO gastos (data, categoria, valor) VALUES (?, ?, ?)",
                   (data, categoria, valor))
    conn.commit()
    conn.close()

    await update.message.reply_text(f"✅ Gasto salvo: {categoria} - R${valor}")

async def relatorio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect("gastos.db")
    cursor = conn.cursor()
    cursor.execute("SELECT data, categoria, valor FROM gastos")
    dados = cursor.fetchall()
    conn.close()

    if not dados:
        await update.message.reply_text("Nenhum gasto registrado.")
        return

    arquivo = "relatorio.csv"

    with open(arquivo, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Data", "Categoria", "Valor"])
        writer.writerows(dados)

    await update.message.reply_document(open(arquivo, "rb"))

def main():
    init_db()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, salvar_gasto))
    app.add_handler(CommandHandler("relatorio", relatorio))
    print("Bot rodando...")
    app.run_polling()

if __name__ == "__main__":
    main()
