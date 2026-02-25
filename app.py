from flask import Flask
from openpyxl import Workbook
from reportlab.pdfgen import canvas

app = Flask(__name__)

@app.route("/")
def home():
    # --- Excel ---
    wb = Workbook()
    ws = wb.active
    ws.append(["Placa", "Tipo", "Empresa"])
    ws.append(["ABC1234", "Carro", "Empresa X"])
    wb.save("dados.xlsx")
    
    # --- PDF ---
    c = canvas.Canvas("dados.pdf")
    c.drawString(100, 750, "Placa: ABC1234")
    c.drawString(100, 730, "Tipo: Carro")
    c.drawString(100, 710, "Empresa: Empresa X")
    c.save()
    
    return "Arquivos Excel e PDF criados com sucesso!"

if __name__ == "__main__":
    app.run()
