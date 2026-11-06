# fitness — Daten-Repo (KB)

Die Fitness-Wissensbasis (Übungen, Anatomie-Lehre, Muskeln, Coaching-Notes, Regeln, Registry) als YAML.
**Nur Daten, kein Code.** Der Python-Code (CLI `fitness`, API, Katalog-Tools) liegt in `~/dev/fitness-cli`.

Konsumenten lesen diese KB:
- `coach-dev` (Submodul unter `fitness/catalog/kb`, dort liegt auch der Live-Stand)
- `fitness-dev`, `plan-dev` (Build-Skripte über `scripts/lib/kb-dir.mjs`)
- `fitness-cli` (Python, Override per `FITNESS_AGENT_KB`)

Historie: per `git subtree split` aus `coach-dev/fitness/catalog/kb` (Stand 2026-11-06).
