# Exercise Inbox — läuft auf GitHub (Stand 2026-11-20)

**Dieses Repo ist die Quelle der Wahrheit für die Übungs-Inbox.** Alles geht im
Browser oder in der GitHub-App am Handy — kein Laptop, keine Coach-App nötig.
Laptop-Kopien (`coach-dev/backend/fitness/catalog/kb`) sind nur Spiegel.

## So arbeitest du

| Was | Wie |
|-----|-----|
| **Neue Übung** | Issue → Vorlage **„Neue Übung“** ausfüllen. Der Bot legt `inbox/inbox_<name>.yml` an, reichert mit KI an und benennt das Issue in „Übung prüfen: …“ um. |
| **Prüfen** | Jeder Draft hat genau ein offenes Issue (Label `inbox`). Oben steht die Zusammenfassung: Muskeln, Quellen, Coaching-Notizen, Fehlerbilder. |
| **Schnell korrigieren** | Im Issue auf „✏️ Datei bearbeiten“ → Commit nach `main`. Das Issue aktualisiert sich selbst. |
| **Befehle** | Als Kommentar im Issue (eine Zeile): |

| Befehl | Wirkung |
|--------|---------|
| `/approve` | Freigabe → `exercises/<id>.yml` (`source: expert`), Draft weg, Issue zu. Verweigert, wenn Name oder Primär-Muskeln fehlen. |
| `/reenrich <Feedback>` | KI überarbeitet den Draft mit deinem Feedback. |
| `/unlink wger` · `/unlink yuhonas` | Falsche Quelle dauerhaft trennen (`source_selection: null`, entfernt übernommene Rohtexte/Bilder). Überlebt jedes Re-Enrich. |
| `/link wger <id>` · `/link yuhonas <id>` | Quelle setzen. |
| `/name <Deutscher Name>` | Namen ändern. |
| `/reject` | Draft löschen, Issue zu. |

Nur Owner/Collaborators können Befehle auslösen (das Repo ist öffentlich).

## Technik

- Workflow: `.github/workflows/inbox-bot.yml` (Issue geöffnet · Kommentar · Push auf `inbox/**` · manuell)
- Logik: `scripts/inbox_bot.py` (`new`, `command`, `summary`, `list`)
- KI: `scripts/enrich_inbox.py` (Gemini, Secret `GEMINI_API_KEY`); hält
  `source_selection` und Identitätsfelder fest
- Abgleich: jeder Push auf `inbox/**` legt fehlende Issues an, aktualisiert
  bestehende und schließt Issues, deren Datei nicht mehr da ist.
  Manuell: Actions → Inbox-Bot → Run workflow.
- Agents/LLM-Webapps dürfen weiter Drafts als PR unter `inbox/` liefern
  (`enrich-inbox.yml`, Prompt `.github/prompts/enrich-inbox.md`); nach dem
  Merge bekommt der Draft automatisch sein Issue.

## Weg in die App

Die Coach-App baut ihren Katalog beim Build aus diesem Repo (`main`). Eine
Freigabe erscheint dort mit dem nächsten Coach-Deploy.

## Bulk-Rohstoff (kein Gate)

| Quelle | In der KB |
|--------|-----------|
| **yuhonas** | Submodul `vendor/free-exercise-db` (`yuhonas.ref`) → `dist/exercises.json` |
| **wger** | Dump `exercises/unreviewed_wger.yml` |

## Quellenfusion (Owner 2026-11-25)

Ein Katalogeintrag führt die passende wger- und yuhonas-Übung zusammen.
Beide Quellen-IDs, Rohdaten und Herkunft bleiben dabei nachvollziehbar erhalten.
Unterschiedliche Namen oder eine ergänzte Griffvariante sind allein kein Grund,
beide Quellen pauschal mit `source_selection: null` zu sperren.

- Passende Quellen über `wger_id`, `yuhonas_id`, `external_ids` und
  `source_selection` konsistent demselben Draft zuordnen.
- Beschreiben Quellen nur die Basisübung, die Abweichung der ausgearbeiteten
  Variante ausdrücklich unter `origin.variant_note` dokumentieren. Originale
  unter `source_snapshot` unverändert erhalten.
- Falsche Zuordnungen korrigieren; nicht beliebige Varianten als identisch behandeln.
  `/unlink` bleibt für konkret verworfene Quellen verfügbar, ist kein Standard
  beim Anlegen oder Anreichern eines Drafts.
- Nach Änderung der Quellen `source_review_required: true` setzen. Fusion allein
  ist keine Expert-Freigabe.
