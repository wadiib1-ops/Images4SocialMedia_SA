# JOB: Saudi-Pro-League-Spielergebnisse (Design "Scoreboard Night")

Gilt zusätzlich zu `CLAUDE-Routine.md` (Konten, Queue-Format, Sofort-Veröffentlichung, Dublettenprüfung, Hashtag-Limit, nur Arabisch) und `PROMPT.md` Abschnitt 6 und 7 (Texte, Recherche, Bericht). Bei Widerspruch gilt für Design und Animation diese Datei, sonst `CLAUDE-Routine.md`. Kein Foto und keine Videosuche: Das Bild entsteht aus den Wappen.

## 1. Auftrag
Bis zu 1 neues Endergebnis pro Lauf aus der Saudi Pro League (Roshn Saudi League), Spiel nachweislich beendet in den letzten 32 Stunden, mit Torschützen und Minuten. Beide Vereine müssen in `spl-video/teams.json` stehen (18 Vereine, Schlüssel = Dateiname in `Wappen/` ohne `.png`). Fehlt ein Verein oder ein Wappen: Spiel verwerfen und im Bericht nennen. Kein neues Spiel = nichts anlegen, keine Benachrichtigung.

Quellen (WebFetch): spl.com.sa/en/news, kooora.com, arriyadiyah.com, sportksa.net, goal.com/ar-sa, saff.com.sa. Ergebnis, Torschützen und Minuten müssen in mindestens einer verlässlichen Quelle stehen. Keine erfundenen Daten. Höchstens 10 Abrufe pro Lauf.

## 2. Pro Meldung drei Einträge (kein Instagram-Feed seit 04.11.2026, keine Facebook-Story seit 13.11.2026, beides Nutzerwunsch, dauerhaft) (gleiche Zeit, gleiche `quelle_url`, gleicher `titel`)
1. Facebook-Feed (`photo`): `--kind feed` (1080 x 1350 PNG), FACEBOOK-TEXT, höchstens 3 Hashtags.
2. Instagram-Reel (`reel`): `--kind reel`, `cover_url` = `--kind cover`, INSTAGRAM-TEXT, höchstens 5 Hashtags.
3. Instagram-Story (`story`): `--kind story`, `caption` leer.
4. Entfällt dauerhaft: keine Facebook-Story (kein Eintrag `platform: facebook`, `type: story`; der Veröffentlicher lehnt ihn ab), kein Instagram-Feed, kein Facebook-Reel.

## 3. Eingabedatei `match.json` (im Arbeitsordner, nicht committen)
```json
{
  "home": "Al_Nassr", "away": "Al-Hilal", "score": [3, 2],
  "matchday": "الجولة 9",
  "title": "<Schlagzeile, eine Zeile, höchstens ca. 55 Zeichen>",
  "sections": ["<Abschnitt 1>", "<Abschnitt 2>", "<Abschnitt 3>"],
  "cta": "<Call to Action, jedes Mal neu>",
  "scorers": [ {"side": "home", "name": "<Nachname arabisch>", "minute": 12} ]
}
```
- `home` ist der Gastgeber (links im Bild), `score` = [Tore Heim, Tore Gast].
- `sections`: der arabische Teil des FACEBOOK-TEXTS ohne Hashtags, wortgetreu, je Abschnitt höchstens ca. 12 Wörter, 3 bis 6 Abschnitte, letzter Abschnitt = sachliche Frage.
- `scorers`: nur echte Tore, `side` = Mannschaft, die das Tor zählt (Eigentor: Seite der Mannschaft, der es gutgeschrieben wird). Nachspielzeit als volle Minute (90+3 = 93). Höchstens 8 Einträge, bei mehr die ersten 8. Kurze Namen (höchstens ca. 14 Zeichen). Keine Hashtags in der Datei.

## 4. Rendern
Werkzeuge einmalig: `python3 -m venv /tmp/venv && /tmp/venv/bin/pip install -q pillow` (ffmpeg ist vorhanden). Immer im Repo-Hauptordner starten:
```
/tmp/venv/bin/python spl-video/spl_render.py --data match.json --kind feed  --out images/feed-<JJJJMMTT-HHMM>-1.png
/tmp/venv/bin/python spl-video/spl_render.py --data match.json --kind cover --out images/cover-<JJJJMMTT-HHMM>-1.jpg
/tmp/venv/bin/python spl-video/spl_render.py --data match.json --kind reel  --out musik-<JJJJMMTT-HHMM>-1-reel-text.mp4
/tmp/venv/bin/python spl-video/spl_render.py --data match.json --kind story --out musik-<JJJJMMTT-HHMM>-1-story-text.mp4
```
- Das Skript wählt den Musik-Track aus `Video/*.mp3` zufällig und gibt Track und Startpunkt aus (im Bericht nennen). Tracks nie verändern.
- Videolänge: Abschnitte x 3,0 s + 0,5 s, mindestens 12 s. Die Story hängt den Call to Action (4,5 s) an. Rendern dauert ca. 2 s je Videosekunde.
- Danach mit ffprobe prüfen: 1080x1920, Dauer wie ausgegeben, Audio vorhanden. Feed 1080x1350, Cover 1080x1920. Fehler: einmal wiederholen, danach Reel und Instagram-Story weglassen und melden. Die Bilddateien vorher ansehen (Read), z. B. auf abgeschnittene Namen.
- Hosting, Queue, Workflow-Start, Prüfung: wie in `CLAUDE-Routine.md` und `PROMPT.md` Abschnitt 8 Schritt 8 (Bilder auf main in `images/`, Videos auf Branch `video-out`, Raw-URLs per curl auf HTTP 200 prüfen).

## 5. Design (verbindlich, bewusst anders als "Saudi Kora News" und Botola)
- Farben: Nachtblau #0A1230 bis #101E4E, Cyan #19D3F3, Magenta #FF2E88, Weiß. Kein Grün, kein Gold.
- Layout: geteiltes Scoreboard mit diagonaler Trennung (Heim links in Blau mit Cyan-Kante, Gast rechts in Violett mit Magenta-Kante), runde Wappen-Scheiben, "FT"-Ring in der Mitte, große Ergebniszahlen, Torschützen-Zeitleiste (Heim cyan oberhalb, Gast magenta unterhalb der Leiste), unten Textfeld, Seitenname und Handle. Liga-Logo oben links, Liganame und Spieltag oben rechts.
- Animation (Video): Hintergrundraster läuft diagonal. Liga-Logo poppt auf. Die Blau- und Violett-Fläche fahren von den Seiten ein. Die Wappen fliegen von außen zur Mitte, kollidieren mit Lichtblitz und rasten mit Überschwingen an ihre Plätze. Der Ring wächst auf und füllt sich bis zum Videoende. Die Tore zählen hoch, danach Zahlenschlag. Ein Cyan-Strich läuft über die Zeitleiste, die Tor-Marker poppen in der jeweiligen Minute auf. Textabschnitte fahren per Wipe von rechts ein, bei jedem Wechsel läuft eine Scan-Linie über das Bild mit kurzem Glitch. Die Story-CTA steht im Magenta-Feld.
- Wappen: Die Dateien in `Wappen/` haben einen weißen Hintergrund. Das Skript löst ihn automatisch heraus. Neue Wappen bitte ohne Änderung des Dateinamens ersetzen. Die Wappen sind klein (ca. 150 px) und werden auf 250 px hochgerechnet; größere Originale verbessern die Schärfe.
- Logo und Handle stehen je einmal, nie doppelt. Im Bild keine Quelle, keine URL, keine Hashtags.

## 6. Abschlussbericht (deutsch, knapp)
Spiel und Ergebnis in einer Zeile, Quelle (nur im Bericht), Suchbegriffe der Dublettenprüfung, Track und Startpunkt, ffprobe-Werte, Status der drei Einträge aus `publisher/log.jsonl`, Fehler, "Texte arabisch fertig".
