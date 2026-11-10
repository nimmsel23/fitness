# fitness — KB-Daten-Repo (`catalog/kb`)

VitalOS Exercise Knowledge Base. **Nur YAML-Daten, kein App-Code.**

Repo: https://github.com/nimmsel23/fitness  
Lokal: `~/dev/fitness` · in `coach-dev` als Submodul `fitness/catalog/kb`

## LLM-Webapps (ChatGPT / Claude / Grok / …)

1. Repo **`nimmsel23/fitness`** öffnen (public — Lesen ohne Auth).
2. Zuerst [`llms.txt`](./llms.txt), dann [`AGENTS.md`](./AGENTS.md).
3. Inbox-Enrichment-Prompt: [`.github/prompts/enrich-inbox.md`](./.github/prompts/enrich-inbox.md).

## Inbox: GitHub/Agents vs. Coach

Siehe [`INBOX.md`](./INBOX.md). Kurz:

- **GitHub App + Agents** arbeiten Drafts als PRs unter `inbox/` (Enrich-CI, Prompt).
- **Coach-UI / Laptop** bleibt das Expert-Gate (`approve` → `exercises/`).
- vos-coach steuert Git **nicht**; optional nur read-only PR-Überblick.

## CI-Enrichment (für Agents / Cloud)

```bash
gh workflow run "Enrich Inbox" -R nimmsel23/fitness -f limit=1
# oder:
gh api repos/nimmsel23/fitness/dispatches -f event_type=enrich-inbox \
  -f client_payload='{"limit":"1"}'
```

Skript: [`scripts/enrich_inbox.py`](./scripts/enrich_inbox.py) · Workflow: `.github/workflows/enrich-inbox.yml`  
Ergebnis = PR auf `inbox/` (kein Auto-Approve nach `exercises/`).

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
| `vendor/free-exercise-db/` | gepinntes Submodul [yuhonas/free-exercise-db](https://github.com/yuhonas/free-exercise-db) (Bulk/Bilder); SHA in `yuhonas.ref` |
| `vendor/fma/` | gepinntes Submodul [uw-sig/FMA](https://github.com/uw-sig/FMA) **5.1.0**; SHA in `fma.ref` — Konzept-Ontology (`fma_id` in `muscles/`) |
| `registry/fma_kb_map.yml` | Katalog-Muskel ↔ FMA-IRI (52 Links); Voll-OWL optional via `scripts/fetch_fma_owl.sh` (Git LFS) |
| `vendor/bodyparts3d/` | BodyParts3D **4.0** Indexes (CC BY 4.0); Pin `bp3d.ref` — FMA-indexed OBJs für Learn-3D |
| `registry/bp3d_kb_map.yml` | Katalog-Muskel ↔ BP3D-Meshes (`FJ####.obj`); Rebuild `scripts/build_bp3d_kb_map.py`; Fetch `scripts/fetch_bodyparts3d_meshes.sh` |
| `exercises/unreviewed_wger.yml` | **Wger-Bulk-Quelle** in der KB — Snapshot aus lokalem wger-API-Import (kein Git-Upstream wie yuhonas) |

## Konsumenten

- `coach-dev` — Submodul unter `fitness/catalog/kb`
- Catalog-Python/CLI — `~/dev/coach-dev/fitness/catalog/` (`coach catalog`)
- Ownership: `~/dev/coach-dev/docs/OWNERSHIP-MAP.md`
