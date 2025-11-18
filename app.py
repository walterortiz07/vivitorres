from flask import Flask, render_template, request, send_file, abort, url_for
import sqlite3
import io
import qrcode
from offline_data import get_offline_info

DB_PATH = "datos.db"

app = Flask(__name__)


# ==========================
#  CONEXIÓN A SQLITE
# ==========================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ==========================
#  PÁGINA INICIAL
# ==========================
@app.route("/")
def index():
    return render_template("index.html")


# ==========================
#  LISTA DE AVES
# ==========================
@app.route("/aves")
def listar_aves():
    q = request.args.get("q", "").strip()
    conn = get_db()
    cur = conn.cursor()

    if q:
        like = f"%{q}%"
        cur.execute("""
            SELECT * FROM aves
            WHERE especie LIKE ? OR nombre_comun LIKE ? OR familia LIKE ? OR orden LIKE ?
            ORDER BY n
        """, (like, like, like, like))
    else:
        cur.execute("SELECT * FROM aves ORDER BY n")

    aves = cur.fetchall()
    conn.close()

    return render_template("lista_aves.html", aves=aves, q=q)


# ==========================
#  LISTA DE PLANTAS
# ==========================
@app.route("/plantas")
def listar_plantas():
    q = request.args.get("q", "").strip()
    conn = get_db()
    cur = conn.cursor()

    if q:
        like = f"%{q}%"
        cur.execute("""
            SELECT * FROM plantas
            WHERE especie LIKE ? OR nombre_comun LIKE ? OR familia LIKE ?
            ORDER BY especie
        """, (like, like, like))
    else:
        cur.execute("SELECT * FROM plantas ORDER BY especie")

    plantas = cur.fetchall()
    conn.close()

    return render_template("lista_plantas.html", plantas=plantas, q=q)


# ==========================
#  DETALLE AVE
# ==========================
@app.route("/aves/<int:item_id>")
def detalle_ave(item_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM aves WHERE id = ?", (item_id,))
    ave = cur.fetchone()
    conn.close()

    if not ave:
        abort(404)

    especie = ave["especie"]
    info = get_offline_info(especie, "ave") if especie else {}

    return render_template("detalle_ave.html", ave=ave, info=info)


# ==========================
#  DETALLE PLANTA
# ==========================
@app.route("/plantas/<int:item_id>")
def detalle_planta(item_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM plantas WHERE id = ?", (item_id,))
    planta = cur.fetchone()
    conn.close()

    if not planta:
        abort(404)

    especie = planta["especie"]
    info = get_offline_info(especie, "planta") if especie else {}

    return render_template("detalle_planta.html", planta=planta, info=info)


# ==========================
#  GALERÍA AVES
# ==========================
@app.route("/galeria/aves")
def galeria_aves():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM aves ORDER BY nombre_comun")
    aves = cur.fetchall()
    conn.close()

    data = []
    for ave in aves:
        info = get_offline_info(ave["especie"], "ave")
        data.append({
            "id": ave["id"],
            "nombre_comun": ave["nombre_comun"],
            "especie": ave["especie"],
            "imagen_local": info.get("imagen_local")
        })

    return render_template("galeria_aves.html", aves=data)


# ==========================
#  GALERIA PLANTAS
# ==========================
@app.route("/galeria/plantas")
def galeria_plantas():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM plantas ORDER BY nombre_comun")
    plantas = cur.fetchall()
    conn.close()

    data = []
    for p in plantas:
        info = get_offline_info(p["especie"], "planta")
        data.append({
            "id": p["id"],
            "nombre_comun": p["nombre_comun"],
            "especie": p["especie"],
            "imagen_local": info.get("imagen_local")
        })

    return render_template("galeria_plantas.html", plantas=data)


# ==========================
#  GENERAR QR
# ==========================
@app.route("/qr/aves/<int:item_id>.png")
def qr_ave(item_id):
    url = url_for("detalle_ave", item_id=item_id, _external=True)
    return generar_qr(url)


@app.route("/qr/plantas/<int:item_id>.png")
def qr_planta(item_id):
    url = url_for("detalle_planta", item_id=item_id, _external=True)
    return generar_qr(url)


def generar_qr(data: str):
    img = qrcode.make(data)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")


# ==========================
#  MAIN
# ==========================
if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
