import sqlite3
import csv
import json
from pathlib import Path
from external_data import get_species_info, slugify

DB_PATH = "datos.db"
OUTPUT_CSV = "data_enriquecida.csv"
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static" / "especies"


# --------------------------------------
# Crear tablas nuevas si no existen
# --------------------------------------
def crear_tablas_info():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS aves_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            especie TEXT,
            nombre_comun TEXT,
            resumen TEXT,
            reino TEXT,
            filo TEXT,
            clase TEXT,
            orden TEXT,
            familia TEXT,
            genero TEXT,
            paises TEXT,
            imagen_local TEXT,
            raw_json TEXT
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS plantas_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            especie TEXT,
            nombre_comun TEXT,
            resumen TEXT,
            reino TEXT,
            filo TEXT,
            clase TEXT,
            orden TEXT,
            familia TEXT,
            genero TEXT,
            paises TEXT,
            imagen_local TEXT,
            raw_json TEXT
        );
    """)

    conn.commit()
    conn.close()


# --------------------------------------
# Guardar datos en la tabla correspondiente
# --------------------------------------
def guardar_info(tabla, especie, nombre_comun, info):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    inat = info.get("inat", {})
    gbif = info.get("gbif", {})

    resumen = inat.get("summary")
    paises = ", ".join(gbif.get("countries", []))
    imagen = inat.get("image_local")

    cur.execute(f"""
        INSERT INTO {tabla} (
            especie, nombre_comun, resumen,
            reino, filo, clase, orden, familia, genero,
            paises, imagen_local, raw_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        especie,
        nombre_comun,
        resumen,
        gbif.get("kingdom"),
        gbif.get("phylum"),
        gbif.get("class"),
        gbif.get("order"),
        gbif.get("family"),
        gbif.get("genus"),
        paises,
        imagen,
        json.dumps(info, ensure_ascii=False)
    ))

    conn.commit()
    conn.close()


# --------------------------------------
# Proceso general
# --------------------------------------
def procesar_todos():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Abrimos CSV final
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "tipo", "especie", "nombre_comun", "resumen",
            "reino", "filo", "clase", "orden", "familia", "genero",
            "paises", "imagen_local"
        ])

        # -----------------------
        # AVES
        # -----------------------
        cur.execute("SELECT * FROM aves")
        aves = cur.fetchall()

        for ave in aves:
            especie = ave["especie"]
            nombre_comun = ave["nombre_comun"]

            if not especie:
                continue

            print(f"Procesando AVE → {especie}...")

            info = get_species_info(especie)
            guardar_info("aves_info", especie, nombre_comun, info)

            inat = info.get("inat", {})
            gbif = info.get("gbif", {})

            writer.writerow([
                "ave",
                especie,
                nombre_comun,
                inat.get("summary"),
                gbif.get("kingdom"),
                gbif.get("phylum"),
                gbif.get("class"),
                gbif.get("order"),
                gbif.get("family"),
                gbif.get("genus"),
                ", ".join(gbif.get("countries", [])),
                inat.get("image_local")
            ])

        # -----------------------
        # PLANTAS
        # -----------------------
        cur.execute("SELECT * FROM plantas")
        plantas = cur.fetchall()

        for planta in plantas:
            especie = planta["especie"]
            nombre_comun = planta["nombre_comun"]

            if not especie:
                continue

            print(f"Procesando PLANTA → {especie}...")

            info = get_species_info(especie)
            guardar_info("plantas_info", especie, nombre_comun, info)

            inat = info.get("inat", {})
            gbif = info.get("gbif", {})

            writer.writerow([
                "planta",
                especie,
                nombre_comun,
                inat.get("summary"),
                gbif.get("kingdom"),
                gbif.get("phylum"),
                gbif.get("class"),
                gbif.get("order"),
                gbif.get("family"),
                gbif.get("genus"),
                ", ".join(gbif.get("countries", [])),
                inat.get("image_local")
            ])


    conn.close()
    print("\n✔ PROCESO COMPLETO")
    print(f"✔ Archivo CSV generado: {OUTPUT_CSV}")
    print("✔ Datos enriquecidos almacenados en tablas:")
    print("   - aves_info")
    print("   - plantas_info")
    print("✔ Imágenes guardadas en: static/especies/")


if __name__ == "__main__":
    crear_tablas_info()
    procesar_todos()
