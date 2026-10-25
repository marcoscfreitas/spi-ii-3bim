"""Prepare the mapped public datasets for import into the application schema."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


HEADERS = ("origem", "arquivo_origem", "linha_origem", "nome", "cargo", "orgao", "uf")
SOURCE_COLUMNS = {
    "aposentados": (18, 0, 6, 3, None),
    "carreiras": (8, 0, 3, 5, 4),
}


def clean(value: str) -> str:
    return " ".join(value.strip("\x00 \t\r\n").split())


def prepare_file(path: Path, origem: str, writer: csv.writer) -> dict[str, int]:
    expected, nome_col, cargo_col, orgao_col, uf_col = SOURCE_COLUMNS[origem]
    counts = {
        "registros_origem": 0,
        "estrutura_invalida": 0,
        "nulos_obrigatorios": 0,
        "uf_invalida": 0,
        "duplicados": 0,
        "tratados": 0,
    }
    seen: set[bytes] = set()

    with path.open("r", encoding="latin-1", newline="") as source:
        for line_number, raw in enumerate(source, start=1):
            row = next(csv.reader([raw], delimiter=";"))
            if not row or not any(value.strip() for value in row):
                continue
            if origem == "carreiras" and (row[0].startswith("CARREIRA.") or row[0].casefold() == "nome"):
                continue
            if origem == "carreiras" and len(row) == expected + 1 and not clean(row[-1]):
                row.pop()

            counts["registros_origem"] += 1
            if len(row) != expected:
                counts["estrutura_invalida"] += 1
                continue

            nome, cargo, orgao = (clean(row[index]) for index in (nome_col, cargo_col, orgao_col))
            uf = clean(row[uf_col]).upper() if uf_col is not None else ""
            if not nome or not cargo or not orgao:
                counts["nulos_obrigatorios"] += 1
                continue
            if uf and (len(uf) != 2 or not uf.isalpha()):
                counts["uf_invalida"] += 1
                continue

            fingerprint = hashlib.blake2b(
                "\0".join((nome, cargo, orgao, uf)).encode("utf-8"), digest_size=16
            ).digest()
            if fingerprint in seen:
                counts["duplicados"] += 1
                continue
            seen.add(fingerprint)

            writer.writerow((origem, path.name, line_number, nome, cargo, orgao, uf))
            counts["tratados"] += 1

    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--aposentados", type=Path, required=True)
    parser.add_argument("--carreiras", type=Path, required=True)
    parser.add_argument("--saida", type=Path, required=True)
    args = parser.parse_args()

    months = []
    for path, pattern in (
        (args.aposentados, r"APOSENTADOS_(\d{6})\.csv"),
        (args.carreiras, r"CARREIRA_(\d{6})\.txt"),
    ):
        match = re.fullmatch(pattern, path.name, re.IGNORECASE)
        if not match or not path.is_file():
            parser.error(f"arquivo de origem ausente ou nome inesperado: {path}")
        months.append(match.group(1))
    if months[0] != months[1]:
        parser.error("os dois arquivos devem pertencer a mesma competencia")

    args.saida.parent.mkdir(parents=True, exist_ok=True)
    with args.saida.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.writer(destination)
        writer.writerow(HEADERS)
        results = {
            origem: prepare_file(path, origem, writer)
            for origem, path in (("aposentados", args.aposentados), ("carreiras", args.carreiras))
        }
    print(json.dumps({"competencia": months[0], "arquivos": results}, ensure_ascii=False))


if __name__ == "__main__":
    main()
