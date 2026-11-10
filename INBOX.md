# Exercise Inbox — wer macht was (Stand 2026-11-10)

Zwei getrennte Flächen. **Nicht vermischen.**

| Fläche | Für wen | Rolle |
|--------|---------|--------|
| **GitHub** (`nimmsel23/fitness`) | GitHub App, LLM-Webapps, Coding-Agents | Drafts anlegen/anreichern/reviewen als PRs unter `inbox/` |
| **Coach (Laptop)** | Daniel / Coach-UI / `coach-sync` / `coach catalog` | Menschliches Expert-Gate → Freigabe nach `exercises/` |

Git ist **nicht** die Steuerfläche der Coach-UI. vos-coach steuert keine
`repository_dispatch`-Calls und kein PR-Merge als Freigabe-Workflow.

## GitHub / Agents (Draft-Arbeit)

| Aktion | Auf GitHub |
|--------|------------|
| Neuer Draft | Branch + PR: `inbox/<id>.yml` (noch nicht in `exercises/`) |
| Anreichern | CI `Enrich Inbox`, Prompt `.github/prompts/enrich-inbox.md`, oder Agent-Commit auf dem PR-Branch |
| Review | PR Conversation / Checks |
| Verwerfen | PR schließen |
| Nach Merge von Inbox-PRs | Datei liegt weiter in `inbox/` — **Merge ≠ Expert-Approve** |

Hilfen im Repo:

- Workflow: `.github/workflows/enrich-inbox.yml`
- Prompt: `.github/prompts/enrich-inbox.md`
- Skript: `scripts/enrich_inbox.py`
- Offene Inbox-PRs listen: `scripts/list_inbox_prs.py`

## Coach (Expert-Gate)

| Aktion | Auf dem Laptop |
|--------|----------------|
| Inbox lesen / reviewen | Coach-UI, Catalog-UI, `coach catalog` / `fitness-catalog inbox …` |
| Anreichern (primär) | `coach-sync` + lokale Pipeline (Gemini/CLI) |
| Freigabe | `approve` → Datei nach `exercises/<id>.yml` (+ Build zieht Expert-JS) |
| Firestore `coachInbox` / `fitness/*/inbox` | Cache / Offline-Spiegel, **nicht** Gate und **nicht** Agent-SOT |

Optional: vos-coach darf offene GitHub-Inbox-PRs **read-only** einblenden
(`listGithubInboxPrs`) — nur Überblick. Approve/Reenrich/Delete für PR-Items
öffnen GitHub bzw. verweisen dorthin; sie ersetzen das Laptop-Gate nicht.

## Nahtstelle

1. Agent/GitHub App liefert oder verbessert `inbox/*.yml` per PR.
2. Nach Merge (oder parallelem Sync) liegt der Draft in der KB / im Submodul.
3. Coach approved lokal → `exercises/`.
4. Konsumenten (`coach-dev` / `fitness-dev`) bumpen den Submodul-Pointer und bauen.

## Bulk-Rohstoff (nicht Gate)

| Quelle | In der KB |
|--------|-----------|
| **yuhonas** | Submodul `vendor/free-exercise-db` (`yuhonas.ref`) → `dist/exercises.json` |
| **wger** | Dump `exercises/unreviewed_wger.yml` |

Inbox-Drafts tragen `wger_id` / `yuhonas_id`. Expert-Truth erst nach Coach-Gate
in `exercises/<id>.yml`.
