from flask import Flask, request, jsonify, render_template
import qrcode
import uuid
import os
from datetime import datetime

app = Flask(__name__)

# Pasta onde os QR Codes serão salvos
QR_CODES_DIR = os.path.join("static", "qr_codes")
os.makedirs(QR_CODES_DIR, exist_ok=True)

# Banco de dados temporário em memória
bilhetes_db = {}


@app.route("/")
@app.route("/geradordebilhetescptm")
def index():
    return render_template("index.html")


@app.route("/gerar_qr", methods=["POST"])
def gerar_qr():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Dados não enviados"}), 400

    num_qrs = int(data.get("num_qrs", 1))

    if num_qrs < 1 or num_qrs > 1000:
        return jsonify({"error": "Quantidade deve ser entre 1 e 1000"}), 400

    qr_codes = []

    for _ in range(num_qrs):
        id_bilhete = str(uuid.uuid4())

        bilhetes_db[id_bilhete] = {
            "valido": True,
            "data_criacao": datetime.now().isoformat()
        }

        qr_data = f"APP:{id_bilhete}"

        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=5
        )

        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(
            fill_color="black",
            back_color="white"
        )

        filename = f"{id_bilhete}.png"
        filepath = os.path.join(QR_CODES_DIR, filename)

        img.save(filepath)

        qr_codes.append({
            "id": id_bilhete,
            "url": f"/static/qr_codes/{filename}",
            "data": qr_data
        })

    return jsonify({"qr_codes": qr_codes})


@app.route("/validar_qr", methods=["GET"])
def validar_qr():
    qr_data = request.args.get("data")

    if not qr_data:
        return jsonify({"valido": False})

    try:
        partes = qr_data.split(":")
        id_bilhete = partes[1]

        valido = (
            id_bilhete in bilhetes_db and
            bilhetes_db[id_bilhete]["valido"]
        )

        return jsonify({"valido": valido})

    except Exception:
        return jsonify({"valido": False})


if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=porta)
