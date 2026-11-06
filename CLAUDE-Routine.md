# CLAUDE-Routine.md (nur für den Saudi-Fußball-Job)

Diese Datei gilt innerhalb der Routine anstelle von CLAUDE.md. Wo PROMPT.md und diese Datei sich widersprechen, gilt diese Datei.

## Grundsatz
Ich (Claude) lege die Beiträge in `publisher/queue.json` ab. Der GitHub-Workflow `.github/workflows/publish.yml` (alle 15 Minuten) veröffentlicht fällige Einträge mit `publisher/publish.py` über die Meta Graph API. Es wird kein externes Planungswerkzeug benutzt. Inhalte, Quellenregeln und Technik stehen in PROMPT.md.

## Konten
- Facebook-Seite "أخبار الكرة السعودية": 1330304383510660
- Instagram-Konto "@saudifootballfutsal": 17841451577328406
- Zugang: Das Geheimnis `META_USER_TOKEN` liegt in den Repo-Einstellungen dieses SA-Repos und wird nur vom Workflow gelesen. Das Token nie ausgeben, nie in Dateien, Logs oder Chat schreiben.

## Fünf Einträge je Meldung (Nutzerwunsch vom 04.11.2026, ergänzt am 06.11.2026 um das Facebook-Reel; gilt für alle künftigen Läufe dieser Routine; Instagram-Feed entfällt dauerhaft), gleiche Zeit, gleiche quelle_url und titel
1. Facebook-Feed: `platform: "facebook"`, `type: "photo"`, `image_url` = gerendertes Feed-PNG aus PROMPT.md Abschnitt 5 (images/feed-…png auf main). Text FACEBOOK-TEXT (Arabisch, höchstens 3 Hashtags).
2. Instagram-Reel: `platform: "instagram"`, `type: "reel"`, `video_url` = Reel-Video, `cover_url` = Reel-Cover (siehe unten). Text INSTAGRAM-TEXT (genau 5 Hashtags).
3. Facebook-Story: `platform: "facebook"`, `type: "story"`, `video_url` = Story-Video mit Text, `caption` leer.
4. Instagram-Story: `platform: "instagram"`, `type: "story"`, gleiche `video_url` wie Facebook-Story, `caption` leer.
5. Facebook-Reel (Nutzerwunsch vom 06.11.2026, dauerhaft): `platform: "facebook"`, `type: "reel"`, gleiche `video_url` wie das Instagram-Reel, `caption` = FACEBOOK-TEXT (Arabisch, höchstens 3 Hashtags). publish.py lädt es über video_reels hoch. Id-Suffix `-fb-reel`.
6. Kein Instagram-Feed (Nutzerwunsch vom 04.11.2026, dauerhaft).

## Format eines Eintrags in publisher/queue.json
```json
{
  "id": "20261101-1200-fb-feed",
  "platform": "facebook",
  "type": "photo",
  "image_url": "https://raw.githubusercontent.com/wadiib1-ops/Images4SocialMedia_SA/main/images/<Datei>.jpg",
  "caption": "Text mit höchstens 3 Hashtags",
  "status": "now",
  "titel": "<Schlagzeile>",
  "quelle_url": "<Quelle>"
}
```
- `status`: immer `now` (siehe "Sofort veröffentlichen"). Nie `published` oder `failed` selbst setzen.
- `id` eindeutig, `caption` leer lassen bei Stories.
- `titel` und `quelle_url` immer setzen (Doppelschutz 24 h).
- Medien-URLs: Bilder aus `main/images/`, Videos aus Branch `video-out` (Raw-URLs), vor dem Eintrag per curl prüfen (HTTP 200).
- Videos auf `video-out` aufräumt der Workflow `delete-videos.yml` nach über 2 Tagen. Bilder in `images/` nach über 3 Tagen.

## Sofort veröffentlichen (verbindlich, dauerhaft)
Alle Einträge bekommen `status: "now"` ohne `publish_at`, keine Slots. Direkt nach dem Push von `queue.json` den Workflow `publish.yml` per workflow_dispatch starten (GitHub-Tool `actions_run_trigger`, ref main), weil der 15-Minuten-Takt unzuverlässig ist. Danach `publisher/log.jsonl` prüfen; Fehler per PushNotification melden. Fälliger Rückstand in der Queue löst denselben Start aus.

## Ablauf am Ende des Laufs
1. Medien wie in PROMPT.md erzeugen und pushen (Bilder auf main, Videos auf video-out).
2. Neue Einträge an `publisher/queue.json` anhängen (vorhandene Einträge nie ändern oder löschen).
3. `git add publisher/queue.json images/`, committen, `git push origin HEAD:main` (bei Ablehnung `git pull --rebase origin main` und einmal wiederholen). Der Push muss gelingen.
4. Workflow starten, `publisher/log.jsonl` lesen, fehlgeschlagene Einträge (`status: failed`, Feld `error`) im Bericht nennen. Nicht stillschweigend neu anlegen.
5. Keine Meldung = nichts anlegen.

## Befehle einzeln ausführen (verbindlich, wegen der Allow-Regeln in .claude/settings.json)
Zusammengesetzte Befehle (`&&`, `;`, Heredocs, Python-Blöcke mit anschließendem git) passen zu keinem Allow-Muster und werden abgelehnt. Deshalb jeden Schritt als eigenen Bash-Aufruf, in dieser Reihenfolge:
1. `git pull --rebase origin main`
2. Einträge als JSON-Datei in den Scratchpad schreiben (Write-Werkzeug), dann `python3 publisher/add_entries.py <datei.json>`
3. `git add publisher/queue.json` (und `git add images/<datei>` für Medien)
4. `git commit -m "<Text>"`
5. `git push origin HEAD:main`
6. `git push -u origin <Sitzungs-Branch>` (Branch-Push, den der Stop-Hook verlangt)
Videos: `git fetch origin video-out`, `git worktree add …`, `git add`, `git commit`, `git push origin video-out`, jeweils einzeln.

## Dublettenprüfung (verbindlich)
Vor dem Bauen von Medien und vor dem Anlegen von Einträgen wird jeder Kandidat per Stichwortsuche gegen die KOMPLETTE `publisher/queue.json` und `publisher/log.jsonl` geprüft: Teamnamen, Spielernamen, Gegner, Ergebnis und Wettbewerb, auf Arabisch und Englisch. Ein Treffer zum selben Spiel, Spieler im selben Kontext oder derselben Aussage in den letzten 7 Tagen macht den Kandidaten zur Dublette: verwerfen. Im Bericht die verwendeten Suchbegriffe nennen.

## Hashtag-Limit (verbindlich)
Facebook höchstens 3, Instagram höchstens 5 Hashtags pro Beitrag, im Text und im Video zusammen. Der Veröffentlicher lehnt Einträge mit zu vielen Hashtags ab.

## Nur arabische Texte (verbindlich)
FACEBOOK-TEXT und INSTAGRAM-TEXT nur auf Arabisch. Die Frage am Ende des Facebook-Texts ist sachlich, ohne Gefühlswörter, Ausrufe oder Emojis. Der Instagram-Text bleibt unter 2200 Zeichen.

## Logo und Feed-Design (verbindlich)
Facebook-Feed-Fotos werden im Design "Saudi Kora News" mit make_feed_image.py erzeugt (PROMPT.md Abschnitt 5). Das Logo steht dort oben links. Videos tragen das Logo als eingeblendetes Bild oben links, 106 px breit.

## Video-Effekt (verbindlich)
Instagram-Reel, Facebook-Story und Instagram-Story erhalten das Effekt-Video nach PROMPT.md Abschnitt 8 Schritt 5. Das Foto gleitet ein und zoomt danach sanft rein und raus, das Logo wächst oben links, goldener Fortschrittsbalken unten.

## Text im Video (verbindlich)
- Reel und Stories zeigen im Video den arabischen Teil des FACEBOOK-TEXTS, ohne Hashtags, wortgetreu.
- Jeder Abschnitt steht 3,0 Sekunden. Abschnitte höchstens ca. 12 Wörter. Der erste Abschnitt beginnt ab 0,5 s, jeder weitere direkt nach dem vorigen.
- Videolänge D = Anzahl Abschnitte x 3,0 s, mindestens 12 s, keine Obergrenze.
- In den ffmpeg-Aufrufen überall D statt fester Werte verwenden (`-t D`, Farbbalken `d=D`, Fortschrittsbalken `t/D`, `atrim=0:D`, Ausblendung `st=D-2`). Startpunkt im Track: höchstens Tracklänge minus D minus 8 Sekunden.
- Die Stories bekommen am Ende einen Call to Action von 4,5 s, falls D es erlaubt; er wird jedes Mal neu formuliert.
- Reel, Facebook-Story und Instagram-Story nutzen pro Meldung dieselbe Musik und denselben Textablauf.

## Reel-Cover (verbindlich, Design "Saudi Kora News")
Das Cover des Instagram-Reels wird im Design erzeugt, 1080 x 1920 (Story-Layout): python3 make_feed_image.py --kind story --photo <foto.jpg> --title "<Schlagzeile>" --category "<Kategorie>" --out images/cover-<JJJJMMTT-HHMM>-<n>.png. Danach als JPG speichern (Pillow, Qualität 92) und die JPG-Datei als images/cover-<JJJJMMTT-HHMM>-<n>.jpg auf main pushen; per curl auf HTTP 200 prüfen. Der Eintrag bekommt cover_url mit dieser Adresse. publish.py reicht es an die Meta-API weiter.

## Formate je Plattform (verbindlich)
- Facebook-Feed: Hochformat 4:5 (1080 x 1350, Empfehlung), quadratisch 1:1 (1080 x 1080) oder 1,91:1 (1200 x 630). Bilder JPG/PNG, Videos MP4/MOV, empfohlen 15 bis 30 s.
- Facebook-Story und Facebook-Reel: 9:16 (Pflicht), 1080 x 1920 (bis 1440 x 2560), MP4 (H.264 + AAC), 24 bis 60 fps. Story max. 60 s, Facebook-Reel 15 bis 90 s: ist D unter 15 s, die Videolänge für das Reel auf 15 s anheben (Hinweis: Reel-Datei dann mit D = 15 bauen). Beschreibung höchstens 3 Hashtags. Bei Reels ist ein Link in der Beschreibung unzulässig. Wichtige Texte und Logos nicht ganz am oberen und unteren Rand.
- Instagram-Story: 9:16, 1080 x 1920, bis 60 s insgesamt, Abschnitte je max. 15 s.
- Instagram-Reel: 9:16, 1080 x 1920, 15 bis 90 s. Cover 9:16.
- Format und Länge jedes Mediums mit ffprobe prüfen, bevor es in die Queue geht.

## Zufällige Musikwahl (verbindlich)
Der Musik-Track wird in jedem Lauf zufällig aus allen Dateien `Video/*.mp3` gewählt.

## Umgang mit dem Token
Das Token `META_USER_TOKEN` muss in den Repo-Einstellungen dieses SA-Repos hinterlegt sein. Schlägt das Veröffentlichen mit einem Token-Fehler fehl, melde den Fehler per PushNotification. Eine eigene Erinnerungsroutine gibt es für dieses Repo nicht.

## Benachrichtigung
Meldungen an den Besitzer gehen per PushNotification, keine E-Mails und keine Gmail-Werkzeuge. In Dateien dieses Repos stehen keine E-Mail-Adressen.

## Zeitangaben
Uhrzeiten gegenüber dem Nutzer immer in Berliner Zeit (Europe/Berlin) nennen, nie in UTC.

## Arbeitsweise
Antworten auf Deutsch, knapp. Keine Zusatzaktionen außer den oben genannten Schritten.

## Vorlagen (verbindlich, Nutzerwunsch vom 02.11.2026, dauerhaft für alle Läufe)
Es gelten genau zwei Vorlagen: `images/vorlage-feed-1080x1080.png` (Feed) und `images/vorlage-story-1080x1920.png` (Reel-Cover). Layout: dunkelgrüner Grund, Seitenlogo `images/logo-saudi.png` oben rechts an der Stelle des Logo-Platzhalters, Foto im Bildfeld, Kategorie in Gold, Schlagzeile, in der Story-Vorlage ein Untertitel, `@saudifootballfutsal` unten links, goldene Leiste unten. Die Quellenzeile der Vorlagen entfällt (PROMPT.md Regel C). `make_feed_image.py` setzt das um (`--kind feed`, `--kind story` mit `--subtitle`). Ergebniszahlen wie 6-2 im Bild und im Video als Worte schreiben (Rechts-nach-links-Darstellung kehrt Ziffern um).

## Großes Foto randlos (verbindlich, Nutzerwunsch vom 02.11.2026, dauerhaft für alle Läufe)
Das Foto der Spieler soll deutlich größer sein. In `make_feed_image.py` steht es randlos über die volle Breite ganz oben: Feed 1080 x 700 px, Story/Reel-Cover 1080 x 1150 px, object-fit: cover (Ränder dürfen beschnitten werden). Das Logo liegt oben rechts auf dem Foto (Feed 150 px, Story 240 px). Darunter Kategorie, Schlagzeile, Handle. Nicht zurücksetzen.

## Story-/Reel-Video-Layout (verbindlich, Nutzerwunsch vom 04.11.2026, dauerhaft für alle Läufe)
- Der laufende Text im Video steht im Feed-Textband: dunkelgrün #0B3D26, volle Breite, bis ganz zum unteren Rand, immer gleiche Höhe (540 px, unten bündig), goldene Leiste (14 px) am unteren Rand, Text rechtsbündig. Schrift und Größe wie im Feed: Noto Sans Arabic 800, Titel 60 px, weiß; CTA 34 px Gold.
- Footer `@saudifootballfutsal` (28 px) steht rechts im Textband über dem unteren Rand (bottom 44 px, ganz unten, Nutzerwunsch vom 05.11.2026); Text beginnt 92 px unter dem Bandrand, Abstand zum Fortschrittsbalken.
- Foto: 1080 x 1200 px (cover), Unterkante fest bei y=1380 direkt über dem Textband, wächst nach oben; Logo (106 px) oben links.
- Umsetzung: `story_text.py` (rendert per Playwright/Chromium) und `make_story_video.py`. Nicht zurücksetzen.
- Werkzeug-Hinweis: `python3 -m venv /tmp/venv && /tmp/venv/bin/pip install -q playwright pillow`; das vorinstallierte Chromium (/opt/pw-browsers/chromium) wird automatisch genutzt.

## Festes Textband im Video (verbindlich, Nutzerwunsch vom 04.11.2026, dauerhaft für alle Läufe)
Das grüne Band mit goldener Leiste und Footer `@saudifootballfutsal` ist im Video immer sichtbar (eigene Dauer-Ebene, `story_text.py --mode band`). Nur der Text wechselt: transparente Text-PNGs (`--mode text`) blenden aus und ein, das Band verschwindet nie. Umgesetzt in `make_story_video.py`. Nicht zurücksetzen.

## Text-Fortschritt im Video (verbindlich, Nutzerwunsch vom 05.11.2026, dauerhaft für alle Läufe)
Reel und Stories zeigen im Textband oben einen Fortschrittsbalken mit einem Segment je Text-Teil (Anzahl = Gesamtzahl der Teile, auch der Call to Action) und rechts-nach-links gefüllt: das aktuelle Segment ist Gold, die übrigen blass. Links daneben steht die Zählung "k/n" in Gold. Umgesetzt in `story_text.py` (`--mode text --index k --total n`) und `make_story_video.py`. Nicht zurücksetzen.

## Einladendes Thumbnail für alle Reels (verbindlich, Nutzerwunsch vom 06.11.2026, dauerhaft für alle Läufe)
Instagram-Reel und Facebook-Reel brauchen immer ein einladendes Vorschaubild, nie eine leere oder dunkle Seite. Umsetzung: (1) Das Reel-Cover (images/cover-….jpg, 1080 x 1920) wird vor dem Videobau als `<Arbeitsordner>/cover.jpg` abgelegt; `make_story_video.py` blendet es in den ersten 0,12 s ein, damit auch das automatische Vorschaubild das Cover zeigt. (2) Beide Reel-Einträge (Instagram und Facebook) bekommen `cover_url`; publish.py setzt es beim Instagram-Reel als Cover und beim Facebook-Reel als bevorzugtes Thumbnail (`/{video_id}/thumbnails`). Reihenfolge im Lauf: Cover erzeugen, dann Video bauen. Nicht zurücksetzen.
