import sqlite3
import csv
from pathlib import Path

DB_PATH = "datos.db"

def crear_tablas(conn):
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS aves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            n INTEGER,
            orden TEXT,
            familia TEXT,
            especie TEXT,
            nombre_comun TEXT,
            s INTEGER,
            b INTEGER,
            migratoria INTEGER
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS plantas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            familia TEXT,
            especie TEXT,
            nombre_comun TEXT,
            uso TEXT,
            fisionomia TEXT,
            estado_agosto TEXT,
            estado_octubre TEXT
        );
    """)

    conn.commit()

def cargar_aves(conn, csv_path):
    cur = conn.cursor()
    cur.execute("DELETE FROM aves;")
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cur.execute("""
                INSERT INTO aves (n, orden, familia, especie, nombre_comun, s, b, migratoria)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                int(row["n"]),
                row["orden"],
                row["familia"],
                row["especie"],
                row["nombre_comun"],
                int(row["s"] or 0),
                int(row["b"] or 0),
                int(row.get("migratoria", 0) or 0)
            ))
    conn.commit()

def cargar_plantas(conn, csv_path):
    cur = conn.cursor()
    cur.execute("DELETE FROM plantas;")
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cur.execute("""
                INSERT INTO plantas (familia, especie, nombre_comun, uso, fisionomia,
                                     estado_agosto, estado_octubre)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                row["familia"],
                row["especie"],
                row["nombre_comun"],
                row["uso"],
                row["fisionomia"],
                row["estado_agosto"],
                row["estado_octubre"],
            ))
    conn.commit()

if __name__ == "__main__":
    if not Path("aves.csv").exists() or not Path("plantas.csv").exists():
        raise SystemExit("Faltan aves.csv o plantas.csv en la carpeta actual")

    conn = sqlite3.connect(DB_PATH)
    crear_tablas(conn)
    cargar_aves(conn, "aves.csv")
    cargar_plantas(conn, "plantas.csv")
    conn.close()
    print("Base de datos creada y cargada en datos.db")
