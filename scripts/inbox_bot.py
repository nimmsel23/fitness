#!/usr/bin/env python3
"""Inbox-Bot: GitHub-Issues als Übungs-Inbox (Cloud, ohne Laptop).

Jeder Draft `inbox/*.yml` hat genau ein Issue mit Label `inbox`. Das Issue zeigt
den Draft lesbar an; Befehle laufen als Kommentar (siehe HELP). Der Workflow
`.github/workflows/inbox-bot.yml` ruft dieses Skript auf und committet nach main.

Subcommands (Ausgabe = JSON auf stdout, für den Workflow):
  new      --title T --body B       Draft aus Issue-Formular anlegen (+ Enrichment, wenn Key da)
  command  --file F --text TEXT     Kommentar-Befehl auf einen Draft anwenden
  summary  --file F                 Markdown-Body fürs Issue
  list                              alle Drafts als JSON (path, name)
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
INBOX = ROOT / "inbox"
EXERCISES = ROOT / "exercises"
REPO = os.environ.get("GITHUB_REPOSITORY", "nimmsel23/fitness")
MARKER = "<!-- inbox-file:{} -->"

HELP = """**Befehle** (als Kommentar, eine Zeile):
- `/approve` — freigeben → `exercises/`, Issue wird geschlossen
- `/reenrich <was besser werden soll>` — KI überarbeitet den Draft mit deinem Feedback
- `/unlink wger` · `/unlink yuhonas` — falsche Quell-Verknüpfung dauerhaft trennen
- `/link wger <id>` · `/link yuhonas <id>` — Quelle setzen
- `/name <Deutscher Name>` — Namen ändern
- `/reject` — Draft verwerfen, Issue wird geschlossen

Kleine Korrekturen: Datei direkt bearbeiten (Link oben)."""


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def dump(path: Path, doc: dict) -> None:
    path.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=88), encoding="utf-8")


def exercise(doc: dict) -> dict:
    if isinstance(doc.get("exercises"), list) and doc["exercises"]:
        return doc["exercises"][0]
    return doc


def name_of(ex: dict, fallback: str = "") -> str:
    return str(ex.get("german") or ex.get("display_name") or ex.get("name") or ex.get("english") or fallback)


def slugify(text: str) -> str:
    table = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "Ä": "ae", "Ö": "oe", "Ü": "ue"})
    slug = re.sub(r"[^a-z0-9]+", "_", text.translate(table).lower()).strip("_")
    return slug[:60] or "uebung"


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


# ── Quellen ──────────────────────────────────────────────────────────────────
def set_source(ex: dict, source: str, value) -> dict:
    """Coach-Entscheidung zu einer Quelle; None = bewusst getrennt (überlebt Re-Enrich)."""
    ex = copy.deepcopy(ex)
    ex.setdefault("source_selection", {})[source] = value
    external = dict(ex.get("external_ids") or {})
    origin = dict(ex.get("origin") or {})
    refs = dict(origin.get("source_refs") or {})
    external.pop(source, None)
    ex.pop(f"{source}_id", None)
    origin.pop(source, None)
    refs.pop(source, None)
    if source == "wger":
        ex.pop("wger_muscle_ids", None)
    if isinstance(ex.get("source_snapshot"), dict):
        ex["source_snapshot"].pop(source, None)
    if value is not None:
        val = int(value) if source == "wger" and str(value).isdigit() else str(value)
        ex[f"{source}_id"] = val
        external[source] = [val]
        refs[source] = [str(val)]
    else:
        # vom Fremd-Eintrag übernommene Rohtexte/Bilder hängen an der Quelle
        if source == "yuhonas":
            ex.pop("images", None)
        for key in ("instructions", "original_description"):
            if not (external or refs):
                ex.pop(key, None)
    ex["external_ids"] = external
    origin["source_refs"] = refs
    origin["type"] = "merged_external" if len(refs) > 1 else "external" if refs else "manual"
    ex["origin"] = origin
    tags = [t for t in (ex.get("tags") or []) if t != source or value is not None]
    ex["tags"] = tags
    return ex


# ── Anzeige ──────────────────────────────────────────────────────────────────
def source_line(ex: dict, source: str) -> str:
    selection = ex.get("source_selection") or {}
    if source in selection and selection[source] is None:
        return f"- **{source}:** bewusst getrennt"
    ids = (ex.get("external_ids") or {}).get(source) or ([ex[f"{source}_id"]] if ex.get(f"{source}_id") else [])
    if not ids:
        return f"- **{source}:** —"
    links = []
    for i in ids:
        if source == "wger":
            links.append(f"[{i}](https://wger.de/en/exercise/{i}/view/)")
        else:
            links.append(f"[{i}](https://github.com/yuhonas/free-exercise-db/blob/main/exercises/{i}.json)")
    return f"- **{source}:** " + ", ".join(links)


def bullets(items, limit: int = 12) -> str:
    out = [f"- {str(i).strip()}" for i in (items or [])[:limit] if str(i).strip()]
    return "\n".join(out) if out else "- —"


def summary(path: Path) -> str:
    ex = exercise(load(path))
    file = rel(path)
    edit = f"https://github.com/{REPO}/edit/main/{file}"
    view = f"https://github.com/{REPO}/blob/main/{file}"
    review = (ex.get("review_state") or {}).get("status") or ex.get("source") or "draft"
    errors = []
    for e in ex.get("common_errors") or []:
        errors.append(e.get("error") if isinstance(e, dict) else e)
    parts = [
        MARKER.format(file),
        f"## {name_of(ex, path.stem)}",
        f"*{ex.get('english') or '—'}* · Kategorie **{ex.get('category') or '—'}** · "
        f"Equipment: {', '.join(ex.get('equipment') or []) or '—'} · Status: `{review}`",
        "",
        f"[✏️ Datei bearbeiten]({edit}) · [📄 ansehen]({view})",
        "",
        "### Muskeln",
        f"- **Primär:** {', '.join(ex.get('primary_muscles') or []) or '—'}",
        f"- **Sekundär:** {', '.join(ex.get('secondary_muscles') or []) or '—'}",
        f"- **Stabilisatoren:** {', '.join(ex.get('stabilizers') or []) or '—'}",
        "",
        "### Quellen",
        source_line(ex, "wger"),
        source_line(ex, "yuhonas"),
        "",
        "### Coaching-Notizen",
        bullets(ex.get("coaching_notes")),
        "",
        "### Fehlerbilder",
        bullets(errors),
        "",
        "---",
        HELP,
    ]
    return "\n".join(parts)


# ── Aktionen ─────────────────────────────────────────────────────────────────
def enrich(path: Path, feedback: str | None) -> str:
    key = (os.environ.get("GEMINI_API_KEY") or "").strip().strip("'\"")
    if not key:
        return "Kein GEMINI_API_KEY — Draft ohne KI-Anreicherung angelegt."
    sys.path.insert(0, str(ROOT / "scripts"))
    import enrich_inbox  # noqa: E402

    before = exercise(load(path))
    enrich_inbox.enrich_file(path, api_key=key, model=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
                             feedback=feedback, dry_run=False)
    # Coach-Entscheidungen zu Quellen und Namen gegen die KI verteidigen
    doc = load(path)
    ex = exercise(doc)
    for source, value in (before.get("source_selection") or {}).items():
        ex = set_source(ex, source, value)
    if isinstance(doc.get("exercises"), list):
        doc["exercises"][0] = ex
    else:
        doc = ex
    dump(path, doc)
    return "KI-Anreicherung erledigt."


def parse_form(body: str) -> dict:
    """GitHub-Issue-Formular: '### Label\\n\\nWert' Blöcke."""
    fields = {}
    for block in re.split(r"^### ", body or "", flags=re.M)[1:]:
        label, _, value = block.partition("\n")
        value = value.strip()
        if value in ("_No response_", ""):
            continue
        fields[label.strip().lower()] = value
    return fields


def cmd_new(title: str, body: str) -> dict:
    form = parse_form(body)
    german = form.get("name (deutsch)") or re.sub(r"^\s*(neue übung|übung)\s*:\s*", "", title, flags=re.I).strip()
    if not german:
        return {"ok": False, "message": "Kein Name gefunden — bitte Titel `Neue Übung: <Name>` verwenden."}
    slug = slugify(german)
    path = INBOX / f"inbox_{slug}.yml"
    if path.exists():
        return {"ok": True, "file": rel(path), "existing": True,
                "message": f"Draft existiert schon: `{rel(path)}` — dieses Issue übernimmt ihn."}
    ex = {
        "exercise_id": slug, "id": slug,
        "display_name": german, "german": german, "name": german,
        "english": form.get("name (englisch)", ""),
        "category": "", "equipment": [], "primary_muscles": [], "secondary_muscles": [],
        "stabilizers": [], "movements": [], "coaching_notes": [], "common_errors": [],
        "tags": ["unreviewed", "github_issue"], "source": "unreviewed",
        "review_state": {"status": "draft", "ai_reviewed": False},
    }
    if form.get("notizen"):
        ex["coach_input"] = form["notizen"]
    for source in ("wger", "yuhonas"):
        value = form.get(f"{source}-id")
        if value:
            ex = set_source(ex, source, value)
    doc = {"name": f"inbox_{slug}", "description": f"Inbox-Draft aus GitHub-Issue: {german}",
           "generated_at": now(), "exercises": [ex]}
    INBOX.mkdir(exist_ok=True)
    dump(path, doc)
    note = enrich(path, form.get("notizen"))
    return {"ok": True, "file": rel(path), "message": f"Draft `{rel(path)}` angelegt. {note}"}


def approve(path: Path) -> dict:
    doc = load(path)
    ex = copy.deepcopy(exercise(doc))
    ex_id = str(ex.get("exercise_id") or ex.get("id") or path.stem.removeprefix("inbox_"))
    target = EXERCISES / f"{ex_id}.yml"
    if target.exists():
        return {"ok": False, "message": f"`{rel(target)}` existiert schon — erst klären (anderer Name / ID)."}
    if not ex.get("primary_muscles") or not (ex.get("german") or ex.get("display_name")):
        return {"ok": False, "message": "Freigabe abgelehnt: Name oder Primär-Muskeln fehlen. Erst `/reenrich` oder Datei bearbeiten."}
    stamp = now()
    ex["source"] = "expert"
    ex["approved_at"] = stamp
    ex["tags"] = [t for t in (ex.get("tags") or []) if t not in ("unreviewed", "bulk_import", "ci_enrichment")]
    ex["review_state"] = {**(ex.get("review_state") or {}), "status": "approved", "approved_at": stamp}
    dump(target, {
        "exercise_id": ex_id,
        "description": f"Expert details for {name_of(ex, ex_id)}",
        "approved_at": stamp,
        "exercises": [ex],
    })
    path.unlink()
    return {"ok": True, "close": True, "file": rel(target),
            "message": f"✅ Freigegeben → `{rel(target)}`. Erscheint in der Coach-App mit dem nächsten Deploy."}


def cmd_command(file: str, text: str) -> dict:
    path = ROOT / file
    if not path.exists():
        return {"ok": False, "message": f"Datei `{file}` gibt es nicht (mehr)."}
    line = (text or "").strip().splitlines()[0] if text and text.strip() else ""
    verb, _, arg = line.partition(" ")
    verb, arg = verb.lower(), arg.strip()

    if verb == "/approve":
        return approve(path)
    if verb == "/reject":
        path.unlink()
        return {"ok": True, "close": True, "message": "🗑️ Draft verworfen."}
    if verb == "/reenrich":
        note = enrich(path, arg or None)
        return {"ok": True, "message": f"🔁 {note}" + (f" Feedback: „{arg}“" if arg else "")}

    doc = load(path)
    ex = exercise(doc)
    if verb in ("/unlink", "/link"):
        parts = arg.split()
        source = parts[0].lower() if parts else ""
        if source not in ("wger", "yuhonas"):
            return {"ok": False, "message": "Quelle muss `wger` oder `yuhonas` sein."}
        value = None
        if verb == "/link":
            if len(parts) < 2:
                return {"ok": False, "message": f"ID fehlt: `/link {source} <id>`"}
            value = parts[1]
        ex = set_source(ex, source, value)
        msg = f"🔗 {source} → `{value}`" if value else f"✂️ {source} bewusst getrennt (bleibt auch bei Re-Enrich getrennt)."
    elif verb == "/name":
        if not arg:
            return {"ok": False, "message": "Name fehlt: `/name <Deutscher Name>`"}
        ex["german"] = ex["display_name"] = ex["name"] = arg
        msg = f"✏️ Name → „{arg}“"
    else:
        return {"ok": False, "message": f"Unbekannter Befehl `{verb}`.\n\n{HELP}"}

    if isinstance(doc.get("exercises"), list):
        doc["exercises"][0] = ex
    else:
        doc = ex
    dump(path, doc)
    return {"ok": True, "message": msg}


def cmd_list() -> list[dict]:
    out = []
    for path in sorted(INBOX.glob("*.yml")):
        try:
            out.append({"file": rel(path), "name": name_of(exercise(load(path)), path.stem)})
        except Exception as exc:  # kaputtes YAML soll die Liste nicht blockieren
            out.append({"file": rel(path), "name": path.stem, "error": str(exc)})
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("new"); p.add_argument("--title", default=""); p.add_argument("--body", default="")
    p = sub.add_parser("command"); p.add_argument("--file", required=True); p.add_argument("--text", required=True)
    p = sub.add_parser("summary"); p.add_argument("--file", required=True)
    sub.add_parser("list")
    args = ap.parse_args()

    if args.cmd == "summary":
        print(summary(ROOT / args.file))
        return 0
    if args.cmd == "list":
        result = cmd_list()
    elif args.cmd == "new":
        result = cmd_new(args.title, args.body)
    else:
        result = cmd_command(args.file, args.text)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
