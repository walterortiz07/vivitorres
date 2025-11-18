import csv

INPUT = "data_enriquecida.csv"
OUTPUT = "faltantes.csv"

def tiene_faltantes(row):
    return (
        not row["imagen_local"] or
        not row["resumen"] or
        not row["reino"] or
        row["reino"].strip() == ""
    )

def main():
    faltantes = []

    with open(INPUT, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if tiene_faltantes(row):
                faltantes.append((row["tipo"], row["especie"]))

    with open(OUTPUT, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["tipo", "nombre_original", "nombre_corregido"])
        for tipo, nombre in faltantes:
            writer.writerow([tipo, nombre, nombre])

    print("✔ faltantes.csv generado")
    print(f"Total: {len(faltantes)} especies con datos faltantes.")


if __name__ == "__main__":
    main()
