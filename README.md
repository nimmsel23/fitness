# fitness — Daten-Repo (KB)

Die Fitness-Wissensbasis (Übungen, Anatomie-Lehre, Muskeln, Coaching-Notes, Regeln, Registry) als YAML.
**Nur Daten, kein Code.** Das ist die **KB-Daten-SOT**.

Python-Code (CLI, API, Katalog-Tools): `~/dev/coach-dev/fitness/` — Einstieg
`coach catalog` (Alias `coach agent`). Altpfad `~/dev/fitness-cli` ist archiviert.

Konsumenten lesen diese KB:
- `coach-dev` — Git-Submodul unter `fitness/catalog/kb` (dieser Commit)
- `fitness-dev`, `plan-dev` (Build-Skripte / Overlay; Override ggf. `FITNESS_AGENT_KB`)

Historie: per `git subtree split` aus `coach-dev/fitness/catalog/kb` (Stand 2026-11-06).

Ownership-Karte: `~/dev/coach-dev/docs/OWNERSHIP-MAP.md`.
