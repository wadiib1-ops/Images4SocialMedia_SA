# CLAUDE-Routine.md (nur für den Saudi-Fußball-Job)

Diese Datei gilt innerhalb der Routine anstelle von CLAUDE.md. Wo PROMPT.md und diese Datei sich widersprechen, gilt diese Datei.

## Grundsatz
Ich (Claude) lege die Beiträge in `publisher/queue.json` ab. Der GitHub-Workflow `.github/workflows/publish.yml` (alle 15 Minuten) veröffentlicht fällige Einträge mit `publisher/publish.py` über die Meta Graph API. Es wird kein externes Planungswerkzeug benutzt. Inhalte, Quellenregeln und Technik stehen in PROMPT.md.

## Konten
- Facebook-Seite "أخبار الكرة السعودية": 1330304383510660
- Instagram-Konto "@saudifootballfutsal": 17841451577328406
- Zugang: Das Geheimnis `META_USER_TOKEN` liegt in den Repo-Einstellungen dieses SA-Repos und wird nur vom Workflow gelesen. Das Token nie ausgeben, nie in Dateien, Logs oder Chat schreiben.

## Vier Einträge je Meldung, gleiche Zeit, gleiche quelle_url und titel
1. Facebook-Feed: `platform: "facebook"`, `type: "photo"`, `image_url` = LOGO-URL aus PROMPT.md Abschnitt 5. Text FACEBOOK-TEXT (Arabisch, höchstens 3 Hashtags).
2. Instagram-Reel: `platform: "instagram"`, `type: "reel"`, `video_url` = Reel-Video, `cover_url` = Reel-Cover (siehe unten). Text INSTAGRAM-TEXT (genau 5 Hashtags).
3. Facebook-Story: `platform: "facebook"`, `type: "story"`, `video_url` = Story-Video mit Text, `caption` leer.
4. Instagram-Story: `platform: "instagram"`, `type: "story"`, gleiche `video_url` wie Facebook-Story, `caption` leer.
Es gibt keinen Instagram-Feed und kein Facebook-Reel.

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

## Reel-Cover (verbindlich)
Der Instagram-Reel-Eintrag bekommt das Feld `cover_url`: Standbild aus dem fertigen Reel bei Sekunde 4, 1080x1920: `ffmpeg -y -loglevel error -ss 4 -i reel-text.mp4 -frames:v 1 -q:v 2 /tmp/cover.jpg`. Als `images/cover-<JJJJMMTT-HHMM>-<n>.jpg` auf `main` pushen und per curl auf HTTP 200 prüfen. `publish.py` reicht es an die Meta-API weiter.

## Formate je Plattform (verbindlich)
- Facebook-Feed: Hochformat 4:5 (1080 x 1350, Empfehlung), quadratisch 1:1 (1080 x 1080) oder 1,91:1 (1200 x 630). Bilder JPG/PNG, Videos MP4/MOV, empfohlen 15 bis 30 s.
- Facebook-Story und Reel: 9:16, 1080 x 1920 (bis 1440 x 2560). Story max. 60 s, Reel 15 bis 90 s. Wichtige Texte und Logos nicht ganz am oberen und unteren Rand.
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
