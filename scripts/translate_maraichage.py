#!/usr/bin/env python3
"""
Translate all Maraîchage course modules (src/data/maraichage/*.json)
into English (en), German (de), Bambara Latin (bm-latn), and N'Ko (bm-nko).

Model routing:
- en, de       -> anthropic/claude-sonnet-5.5 (best European localization & nuance)
- bm-latn      -> google/gemini-3.1-pro-preview (best Google multilingual/Manding model)
- bm-nko       -> google/gemini-3.1-pro-preview (with manual N'Ko agronomic glossary from commit a82338e)
"""

import argparse
import concurrent.futures
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE_DIR = Path("src/data/maraichage")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

MODELS = {
    "en": "anthropic/claude-sonnet-5.5",
    "de": "anthropic/claude-sonnet-5.5",
    "bm-latn": "google/gemini-3.1-pro-preview",
    "bm-nko": "google/gemini-3.1-pro-preview",
}

LANG_NAMES = {
    "en": "English",
    "de": "German (Deutsch)",
    "bm-latn": "Bambara / Bamanankan written in official Malian Latin orthography (with ɛ, ɔ, ɲ, ŋ where appropriate)",
    "bm-nko": "N'Ko (ߒߞߏ, standardized Manding literary language written strictly in Unicode N'Ko script U+07C0-U+07FF, RTL)",
}

# Curated agronomic terminology extracted from manual N'Ko translations (commit a82338e)
NKO_GLOSSARY = """
Référence terminologique N'Ko (issues des traductions manuelles validées de l'équipe Nakôbio sur les modules 101 et 201 — respecte ces termes autant que possible) :
- maraîchage bio-intensif en sol vivant : ߛߣߍ߬ߞߍ ߓߌ߬ߟߊ߬ߢߐ߲߰ߡߊ ߘߎ߰ߞߟߏ ߓߊߟߏߣߍ߲ ߡߊ߬
- sol vivant : ߘߎ߰ߞߟߏ ߓߊߟߏߣߍ߲
- planche permanente / planche de culture : ߛߣߍ߬ ߜߊ߲ߜߊ߲ ߘߎ߲ߡߊ / ߛߣߍ߬ ߜߊ߲ߜߊ߲
- compost : ߞߐ߲ߔߐߛߌ / ߣߐ߰ ߟߊߘߊ߲ߣߍ߲
- irrigation : ߖߌ ߟߊߕߊ߬ߡߌ߲߬ߠߌ߲ / ߛߣߍ߬ ߖߌ߫ ߛߐ
- paillage / paillis : ߓߌ߲߫ ߓߌߙߌ / ߘߎ߰ߞߟߏ ߘߊߕߎ߲߯ߠߌ߲
- humus : ߘߎ߰ߞߟߏ ߣߐ߰ / ߤߎߡߎߛߌ
- semence / graine : ߞߌ߬ߛߍ / ߛߣߍ߬ ߞߌ߬ߛߍ
- récolte : ߛߎ߬ߡߊ߲߬ ߟߊߘߊ߲ / ߛߎ߬ߡߊ߲߬ ߞߊ߲ߠߌ߲
- environnement : ߟߊ߬ߡߌߣߌ߲
- santé : ߞߍ߲ߘߍߦߊ
- eau : ߖߌ
- plante : ߝߍߘߍ߲ߝߋ߲
- racine : ߟߌ߬ߟߌ
- micro-ferme : ߛߣߍ߬ߘߊ߫ ߡߌߛߍ߲
"""


def load_api_key() -> str:
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("OPENROUTER_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY not found in .env or environment")
    return key


def load_manual_nko_context(slug: str) -> str:
    """For modules 101 and 201, load the manual N'Ko translations from commit a82338e as reference."""
    if slug not in ("101_fondamentaux_maraichage_sol_vivant", "201_sols_vivants"):
        return ""
    try:
        raw = subprocess.check_output(
            ["git", "show", f"a82338e:src/data/maraichage/{slug}.bm-nko.json"],
            stderr=subprocess.DEVNULL,
        )
        data = json.loads(raw.decode("utf-8"))
        samples = []
        for p in data.get("pages", []):
            t = p.get("title", "").strip()
            x = p.get("text", "").strip()
            if t or x:
                samples.append(f"p.{p.get('page_number')}: {t} | {x[:140]}")
        return (
            "\nTraductions manuelles N'Ko précédentes pour ce module (à réutiliser/adapter "
            "fidèlement au nouveau texte français corrigé) :\n"
            + "\n".join(samples)
        )
    except Exception:
        return ""


def call_openrouter(api_key: str, model: str, system_prompt: str, user_prompt: str, max_retries: int = 4) -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
    }
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://campus.nakobio.org",
        "X-Title": "Nakobio Campus Translation Pipeline",
    }

    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(OPENROUTER_URL, data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=240) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                return body["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")[:300]
            if attempt == max_retries:
                raise RuntimeError(f"HTTP {e.code} from OpenRouter ({model}): {err_body}")
            time.sleep(3 * attempt)
        except Exception as e:
            if attempt == max_retries:
                raise
            time.sleep(3 * attempt)
    raise RuntimeError("Unreachable")


def extract_json(raw_text: str) -> dict:
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON object found in response: {text[:200]}")
    return json.loads(text[start : end + 1])


def has_nko_chars(s: str) -> bool:
    return any("\u07c0" <= ch <= "\u07ff" for ch in s)


def translate_module(api_key: str, fr_path: Path, lang: str, force: bool = True) -> tuple[str, str, str]:
    slug = fr_path.stem
    out_path = BASE_DIR / f"{slug}.{lang}.json"
    if out_path.exists() and not force:
        return (slug, lang, "SKIPPED")

    fr_data = json.loads(fr_path.read_text(encoding="utf-8"))
    model = MODELS[lang]

    # Build minimal payload of translatable fields only
    to_translate = {
        "title": fr_data.get("title", ""),
        "category": fr_data.get("category", ""),
        "summary": fr_data.get("summary", ""),
        "pages": [
            {
                "page_number": p.get("page_number"),
                "title": p.get("title", ""),
                "text": p.get("text", ""),
            }
            for p in fr_data.get("pages", [])
        ],
    }

    extra_rules = ""
    if lang == "bm-nko":
        extra_rules = (
            "\nRÈGLES SPÉCIFIQUES N'KO :\n"
            "- Écris TOUT le texte traduit exclusivement en alphabet N'Ko Unicode (ߒߞߏ, U+07C0-U+07FF).\n"
            "- Ne laisse aucun mot français non traduit sauf les symboles d'unités/chiffres si nécessaire (ou utilise les chiffres N'Ko/arabes de façon cohérente).\n"
            "- Conserve la mise en forme Markdown (**gras**, listes `- `, retours à la ligne `\\n\\n`).\n"
            + NKO_GLOSSARY
            + load_manual_nko_context(slug)
        )
    elif lang == "bm-latn":
        extra_rules = (
            "\nRÈGLES SPÉCIFIQUES BAMBARA (BAMANANKAN) :\n"
            "- Écris un bamanankan naturel, clair et pédagogique, compréhensible par des maraîchers au Mali.\n"
            "- Utilise l'orthographe officielle malienne (ɛ, ɔ, ɲ, ŋ) de façon cohérente.\n"
            "- Ne répète jamais de phrases ou de mots en boucle.\n"
            "- Conserve la mise en forme Markdown (**gras**, listes `- `, retours à la ligne `\\n\\n`).\n"
        )
    else:
        extra_rules = (
            "\nRÈGLES SPÉCIFIQUES :\n"
            "- Utilise un vocabulaire agronomique précis, naturel et pédagogique (maraîchage bio-intensif sur sol vivant).\n"
            "- Conserve strictement la mise en forme Markdown (**gras**, listes `- `, retours à la ligne `\\n\\n`).\n"
            "- Ne mets pas les titres en MAJUSCULES ; respecte la casse naturelle de la langue cible.\n"
        )

    system_prompt = (
        f"Tu es un traducteur professionnel spécialisé en agronomie et agroécologie.\n"
        f"Traduis le JSON fourni du français vers : {LANG_NAMES[lang]}.\n"
        f"Contraintes impératives :\n"
        f"1. Retourne UNIQUEMENT un objet JSON valide avec exactement la même structure : "
        f"`title`, `category`, `summary`, et `pages` (liste d'objets avec `page_number`, `title`, `text`).\n"
        f"2. Le nombre d'éléments dans `pages` et chaque `page_number` doivent correspondre exactement à l'entrée.\n"
        f"3. Aucun commentaire hors du JSON.\n"
        f"{extra_rules}"
    )

    user_prompt = json.dumps(to_translate, ensure_ascii=False, indent=2)

    for attempt in range(1, 4):
        try:
            raw = call_openrouter(api_key, model, system_prompt, user_prompt)
            tr = extract_json(raw)

            tr_pages = tr.get("pages", [])
            fr_pages = fr_data.get("pages", [])
            if len(tr_pages) != len(fr_pages):
                raise ValueError(f"Page count mismatch: got {len(tr_pages)}, expected {len(fr_pages)}")

            # Sanity check: char ratio & script check
            fr_chars = sum(len(p.get("title", "")) + len(p.get("text", "")) for p in fr_pages)
            tr_chars = sum(len(p.get("title", "")) + len(p.get("text", "")) for p in tr_pages)
            if fr_chars > 0 and (tr_chars < fr_chars * 0.25 or tr_chars > fr_chars * 2.8):
                raise ValueError(f"Suspicious char ratio: tr={tr_chars} vs fr={fr_chars}")

            if lang == "bm-nko":
                sample_text = tr.get("title", "") + "".join(p.get("text", "") for p in tr_pages[:3])
                if not has_nko_chars(sample_text):
                    raise ValueError("N'Ko translation does not contain N'Ko Unicode characters!")

            # Merge back into full FR structure preserving all non-translatable fields
            merged = dict(fr_data)
            merged["title"] = tr.get("title", fr_data.get("title", ""))
            merged["category"] = tr.get("category", fr_data.get("category", ""))
            merged["summary"] = tr.get("summary", fr_data.get("summary", ""))

            merged_pages = []
            for fp, tp in zip(fr_pages, tr_pages):
                mp = dict(fp)
                mp["title"] = tp.get("title", fp.get("title", ""))
                mp["text"] = tp.get("text", fp.get("text", ""))
                merged_pages.append(mp)
            merged["pages"] = merged_pages

            out_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            return (slug, lang, f"OK ({len(merged_pages)}p, {tr_chars}c)")
        except Exception as e:
            if attempt == 3:
                return (slug, lang, f"ERROR: {e}")
            time.sleep(2 * attempt)

    return (slug, lang, "ERROR: unknown")


def main():
    parser = argparse.ArgumentParser(description="Translate Maraîchage modules")
    parser.add_argument("--langs", nargs="+", default=["en", "de", "bm-latn", "bm-nko"])
    parser.add_argument("--modules", nargs="*", help="Optional subset of module slugs")
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--skip-existing", action="store_true")
    args = parser.parse_args()

    api_key = load_api_key()
    fr_files = sorted(
        p for p in BASE_DIR.glob("*.json")
        if p.name != "catalog.json"
        and not any(p.name.endswith(f".{ext}.json") for ext in ("en", "de", "bm-latn", "bm-nko"))
    )

    if args.modules:
        fr_files = [p for p in fr_files if p.stem in args.modules]

    tasks = [(p, lang) for p in fr_files for lang in args.langs]
    print(f"Starting {len(tasks)} translation tasks ({len(fr_files)} modules x {len(args.langs)} langs) with {args.workers} workers...")

    ok = 0
    errors = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {
            ex.submit(translate_module, api_key, p, lang, not args.skip_existing): (p.stem, lang)
            for p, lang in tasks
        }
        for fut in concurrent.futures.as_completed(futs):
            slug, lang, status = fut.result()
            print(f"[{lang:7s}] {slug:42s} -> {status}", flush=True)
            if status.startswith("OK") or status == "SKIPPED":
                ok += 1
            else:
                errors.append((slug, lang, status))

    print(f"\nDone: {ok}/{len(tasks)} succeeded, {len(errors)} errors.")
    if errors:
        for slug, lang, status in errors:
            print(f"  FAILED [{lang}] {slug}: {status}")
        sys.exit(1)


if __name__ == "__main__":
    main()
