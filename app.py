import os
import sqlite3
import pandas as pd
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters

TOKEN = os.getenv("TOKEN")

# Criar banco
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
    cursor.execute("INSERT INTO gastos (data, categoria, valor) VALUES (?, ?, ?)", (data, categoria, valor))
    conn.commit()
    conn.close()

    await update.message.reply_text(f"Gasto salvo: {categoria} - R${valor}")

async def relatorio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect("gastos.db")
    df = pd.read_sql_query("SELECT * FROM gastos", conn)
    conn.close()

    if df.empty:
        await update.message.reply_text("Nenhum gasto registrado.")
        return

    arquivo = "relatorio.xlsx"
    df.to_excel(arquivo, index=False)

    await update.message.reply_document(open(arquivo, "rb"))

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, salvar_gasto))
app.add_handler(CommandHandler("relatorio", relatorio))

app.run_polling()
