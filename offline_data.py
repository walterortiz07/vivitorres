import sqlite3
import json
from pathlib import Path
from external_data import slugify

DB_PATH = "datos.db"
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static" / "especies"


def get_offline_info(especie: str, tipo: str):
    """
    tipo = 'ave' o 'planta'
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    tabla = "aves_info" if tipo == "ave" else "plantas_info"

    cur.execute(f"SELECT * FROM {tabla} WHERE especie = ?", (especie,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return {}

    # Leer JSON raw almacenado
    raw = {}
    try:
        raw = json.loads(row["raw_json"])
    except:
        pass

    # Imagen local (ya descargada)
    imagen = row["imagen_local"]

    return {
        "scientific_name": especie,
        "nombre_comun": row["nombre_comun"],
        "resumen": row["resumen"],
        "taxonomia": {
            "reino": row["reino"],
            "filo": row["filo"],
            "clase": row["clase"],
            "orden": row["orden"],
            "familia": row["familia"],
            "genero": row["genero"],
        },
        "paises": row["paises"].split(", ") if row["paises"] else [],
        "imagen_local": imagen,
        "raw": raw
    }
