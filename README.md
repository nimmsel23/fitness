# fitness — KB-Daten-Repo (`catalog/kb`)

VitalOS Exercise Knowledge Base. **Nur YAML-Daten, kein App-Code.**

Repo: https://github.com/nimmsel23/fitness  
Lokal: `~/dev/fitness` · in `coach-dev` als Submodul `fitness/catalog/kb`

## LLM-Webapps (ChatGPT / Claude / Grok / …)

1. In der Webapp **GitHub verbinden** (Account `nimmsel23` bzw. Zugriff auf dieses Repo).
2. Repo **`nimmsel23/fitness`** öffnen / anbinden.
3. Zuerst [`llms.txt`](./llms.txt) lesen, dann [`AGENTS.md`](./AGENTS.md).
4. Dateien über den GitHub-Connector lesen/schreiben (PRs oder direkte Edits je nach Tool).

Einstieg für Maschinen: [`llms.txt`](./llms.txt) · Inventar: [`MANIFEST.yml`](./MANIFEST.yml)

Repo ist **privat** — Zugriff nur mit verbundenem GitHub-Account, der Leserecht hat.

## Layout

| Pfad | Inhalt |
|------|--------|
| `exercises/` | freigegebene Expert-Übungen |
| `inbox/` | Drafts vor Coach-Freigabe |
| `muscles/` | Muskeln + Regions-Buckets |
| `anatomy_teaching/` | Teaching-Layer |
| `coaching_notes/` | kurze Coaching-Notes |
| `rules/` | Katalog-Regeln |
| `registry/` | wger/yuhonas-Lookups |

## Konsumenten

- `coach-dev` — Submodul unter `fitness/catalog/kb`
- Catalog-Python/CLI — `~/dev/coach-dev/fitness/catalog/` (`coach catalog`)
- Ownership: `~/dev/coach-dev/docs/OWNERSHIP-MAP.md`
