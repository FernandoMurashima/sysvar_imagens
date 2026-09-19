import argparse
import base64
import csv
import io
import os
import re
import time
from pathlib import Path

from openai import OpenAI
from PIL import Image

OUT = Path("imagens")
MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-2")

def nome_arquivo(ref: str) -> str:
    return re.sub(r"[^A-Za-z0-9]", "", ref) + ".png"

def prompt(ref: str, descricao: str) -> str:
    return f"""Fotografia de catálogo profissional de um único produto: {descricao}.
Referência interna: {ref} (não mostrar a referência na imagem).
Mostrar somente o produto, inteiro, centralizado, vista frontal, sem modelo, sem manequim,
sem cabide, sem acessórios extras, sem texto, sem letras, sem números, sem marca e sem logotipo.
Fundo branco ou neutro muito claro, iluminação uniforme de estúdio, sombra discreta e realista,
cores e materiais coerentes com a descrição. Composição vertical com bastante margem ao redor,
adequada a recorte final 1:2. Estética consistente de e-commerce de moda/ERP."""

def ajustar_1x2(raw: bytes) -> Image.Image:
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    w, h = img.size
    target_ratio = 0.5
    if w / h > target_ratio:
        nw = int(h * target_ratio)
        left = (w - nw) // 2
        img = img.crop((left, 0, left + nw, h))
    else:
        nh = int(w / target_ratio)
        top = max(0, (h - nh) // 2)
        img = img.crop((0, top, w, top + nh))
    return img.resize((600, 1200), Image.Resampling.LANCZOS)

def carregar_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            ref = (row.get("referencia") or "").strip()
            desc = (row.get("descricao") or "").strip()
            if ref and desc:
                yield ref, desc

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, type=Path)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--delay", type=float, default=1.0)
    args = ap.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("Defina OPENAI_API_KEY antes de executar.")

    OUT.mkdir(parents=True, exist_ok=True)
    client = OpenAI()
    itens = list(carregar_csv(args.csv))
    print(f"{len(itens)} item(ns) carregado(s). Modelo: {MODEL}")

    ok = falhas = pulados = 0
    for i, (ref, desc) in enumerate(itens, 1):
        destino = OUT / nome_arquivo(ref)
        if destino.exists() and not args.force:
            pulados += 1
            print(f"[{i}/{len(itens)}] PULADO {ref} -> {destino.name}")
            continue
        try:
            print(f"[{i}/{len(itens)}] GERANDO {ref} - {desc}")
            r = client.images.generate(
                model=MODEL,
                prompt=prompt(ref, desc),
                size="1024x1536",
                quality="high",
                n=1,
            )
            raw = base64.b64decode(r.data[0].b64_json)
            ajustar_1x2(raw).save(destino, "PNG", optimize=True)
            ok += 1
            print(f"  OK -> {destino}")
        except Exception as exc:
            falhas += 1
            print(f"  ERRO: {exc}")
        time.sleep(args.delay)

    print(f"Concluído: {ok} geradas, {pulados} puladas, {falhas} falhas.")

if __name__ == "__main__":
    main()
