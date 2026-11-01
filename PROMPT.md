Anleitung für den Saudi-Fußball-Job (أخبار الكرة السعودية)

0. VORRANG
Lies zuerst vollständig die Datei CLAUDE-Routine.md im selben Repo (Branch main). Sie ersetzt CLAUDE.md für diese Routine. Bei Widerspruch gilt CLAUDE-Routine.md vor dieser Datei. Beiträge werden ausschließlich über publisher/queue.json und den GitHub-Workflow publish.yml veröffentlicht, es gibt kein externes Planungswerkzeug. Hashtag-Limit (Abschnitt 10) und Zeitangaben in Berliner Zeit gelten immer.

1. AUFTRAG UND ABLAUF
Veröffentliche bis zu 1 neue Meldung pro Lauf. Gesucht wird nur nach EINER Meldung, auf Arabisch, über AKTUELLE Nachrichten zu Fußball oder Futsal mit klarem Saudi-Bezug. Zulässig: Saudi Pro League, Saudi-Nationalteam (Green Falcons) und Nationalteams der Frauen und der Jugend, saudische Klubs und Trainer, saudische Spieler im In- und Ausland, saudische Klubs in der AFC Champions League und in anderen AFC-Wettbewerben, Futsal (Nationalteam und Klubs), Verband und Ligabetrieb (SAFF, SPL). Kein anderes Thema.

Pro Meldung entstehen VIER Einträge in publisher/queue.json, immer in dieser Reihenfolge und mit derselben Veröffentlichungszeit:
 1. Facebook-Feed: Foto mit Seitenlogo und FACEBOOK-TEXT.
 2. Instagram-Reel: dasselbe Musik-Video mit INSTAGRAM-TEXT.
 3. Facebook-Story: Story-Video mit eingeblendetem Text, ohne Begleittext.
 4. Instagram-Story: dasselbe Story-Video, ohne Begleittext.
(Kein Instagram-Feed, kein Facebook-Reel.)

Ablauf eines Laufs:
 1. Dublettenprüfung (Abschnitt 7).
 2. Recherche, Video- und Fotosuche (Abschnitt 7 und 3).
 3. Foto laden und prüfen, Videos bauen (Abschnitt 8), Texte schreiben (Abschnitt 6).
 4. Medien hosten und prüfen (Abschnitt 5 und 8).
 5. Einträge an publisher/queue.json anhängen, pushen, Workflow starten (CLAUDE-Routine.md).
 6. Abschlussbericht auf Deutsch (Abschnitt 7).

2. KONTEN UND TECHNIK
 - Facebook-Seite "أخبار الكرة السعودية", Seiten-ID 1098115996402021, Seiten-URL https://facebook.com/1098115996402021
 - Instagram-Konto "@saudifootballfutsal" (Professional), ID 17841451577328406
 - Veröffentlichung: Workflow publish.yml (alle 15 Minuten) mit publisher/publish.py über die Meta Graph API. Das Geheimnis META_USER_TOKEN liegt in den Repo-Einstellungen dieses SA-Repos; nie ausgeben oder speichern.
 - Uhrzeit: Shell: TZ=Europe/Berlin date -Iseconds
 - Eintragsformat: siehe CLAUDE-Routine.md.

3. HARTE REGELN (HABEN VORRANG)
A. Nur Nachrichten der letzten 32 Stunden. Eine Meldung wird nie ein zweites Mal veröffentlicht (Dublettenprüfung, Abschnitt 7). Ein Beitrag berichtet nur über ein Ereignis, das nachweislich in den letzten 32 Stunden passiert oder veröffentlicht wurde. Datum und Uhrzeit der Quelle prüfen. Ist das Datum nicht eindeutig oder älter, ist die Meldung unbrauchbar. Keine Evergreen-Themen, keine Geschichte, keine Rückblicke. Gibt es keine frische Meldung, wird nichts veröffentlicht.
B. Keine URL im Text der Beiträge, kein Link zur Quelle. Bilder und Videos immer als Medien, nie als Link-Vorschau.
C. Keine Quellenangabe in den Beiträgen, auch nicht im Video. Die Quelle wird nur im Abschlussbericht und im Feld quelle_url der Warteschlange genannt.
D. Video vor Foto. Gibt es zur Meldung ein direktes Video (.mp4 oder .mov, zum Beispiel aus og:video), das nutzbar ist, bleibt es unverändert (Originalton, keine Musik) und wird für Feed-Video, Reels und Stories verwendet. Nicht verwendbar: YouTube-, Facebook-, Instagram-, X-Einbettungen, .m3u8-Playlists, Seiten-URLs, Videos mit fremden Wasserzeichen oder Senderlogos. Ohne plausible Datei-URL gilt die Fotosuche.
E. Foto ist Pflicht-Suche (ohne verwendbares Video). Kandidat 1 ist das Artikelfoto der Quellseite (og:image oder großes Artikelfoto), per WebFetch ermittelt. Einen zweiten Kandidaten erst suchen, wenn Kandidat 1 in der Shell nicht ladbar ist: das Artikelfoto einer zweiten Quelle zur selben Meldung, sonst ein frei lizenziertes Bild (Wikimedia Commons, Pixabay, Pexels). Höchstens 2 Kandidaten pro Meldung.
F. Kein Video und kein Foto: die Meldung wird nicht veröffentlicht, es wird kein Eintrag angelegt. Im Bericht nennen.
G. Schlägt der Facebook-Feed-Eintrag nach der Prüfung endgültig fehl, werden die übrigen drei Einträge dieser Meldung nicht angelegt.
H. Musik-Tracks im Ordner Video/ werden nie gelöscht oder verändert.

4. EINTRÄGE JE MELDUNG
 - Die vier Einträge mit Typen und Texten stehen in CLAUDE-Routine.md. FACEBOOK-TEXT: Arabisch, höchstens 3 Hashtags. INSTAGRAM-TEXT: Arabisch, genau 5 Hashtags, unter 2200 Zeichen. Stories ohne Begleittext (Text im Video, Abschnitt 8). Keine Quellenzeile.
Rückfälle (je Eintrag, nur wenn der Eintrag nicht anlegbar ist; das Scheitern von Reel oder Story stoppt den Facebook-Eintrag nicht):
 - Facebook-Foto: erst LOGO-URL, bei Fehler die Original-Foto-Adresse ohne Logo, dann Kandidat 2 mit Logo und ohne Logo (höchstens 4 Versuche). Alles fehlgeschlagen: Regel F.
 - Reel und Story: Video nicht baubar oder nicht hostbar: Eintrag weglassen und im Bericht melden.
Musste der Facebook-Eintrag ohne Logo auskommen, trägt das Video trotzdem das Logo (Abschnitt 8). Das Logo wird nie doppelt aufgesetzt.

5. BILD-URLS (CLOUDINARY, NUR FACEBOOK-FOTO)
Jedes Foto aus einer externen Quelle bekommt oben einen Streifen in der Randfarbe des Fotos (Cloudinary b_auto:border), dessen Höhe 15,4 % der Bildbreite beträgt; darin sitzt das runde Seitenlogo links oben (90 % der Streifenhöhe). Das Logo verdeckt dadurch nie einen Teil des Fotos; das Foto wird nie beschnitten. Den Streifen und das Logo setzt Cloudinary (Cloud-Name gc0qxb3y). Die URL wird nur gebaut und per curl -sIL auf HTTP 200 und image/jpeg geprüft.
Foto-URL kodieren (nur Sonderzeichen wie ? & = # und Leerzeichen; "https://", Host und Pfad bleiben lesbar):
 python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1], safe=':/%'))" "<Foto-URL>"
LOGO-URL (Saudi-Logo aus diesem Repo, Datei images/logo-saudi.png):
 https://res.cloudinary.com/gc0qxb3y/image/fetch/$b_iw_mul_0.154/c_pad,w_iw,h_ih_add_$b,g_south,b_auto:border/l_fetch:aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL3dhZGlpYjEtb3BzL0ltYWdlczRTb2NpYWxNZWRpYV9TQS9tYWluL2ltYWdlcy9sb2dvLXNhdWRpLnBuZw/c_scale,h_$b_mul_0.9/fl_layer_apply,g_north_west,x_$b_mul_0.05,y_$b_mul_0.05/f_jpg,q_90/<kodierte Foto-URL>
Vor dem ersten Lauf diese Basis-URL per curl -sIL prüfen (HTTP 200, image/jpeg). Schlägt sie fehl, im Bericht melden und nichts veröffentlichen.
Es ist immer dieselbe Foto-Adresse für alle URLs einer Meldung.

6. TEXTE (NUR ARABISCH)
Texte umformulieren (Pflicht, vor dem Anlegen der Einträge): Aus den Fakten der Quelle einen arabischen Rohentwurf mit Titel und Body in eigenen Worten schreiben, dann umformulieren. Modern Standard Arabic, leicht verständlich.
 - FACEBOOK-TEXT | Facebook-Feed | Informativ, einladend, kurze Absätze mit Leerzeile, am Ende eine sachliche Frage an die Leser (keine Gefühlswörter, keine Ausrufe, keine Emojis in der Frage), danach 2 bis 3 Hashtags.
 - INSTAGRAM-TEXT | Instagram-Reel | Hook als erste Zeile, bildhafte Sprache, 3 bis 5 Emojis, am Ende genau 5 relevante Hashtags; anders formuliert als FACEBOOK-TEXT.
 - Die Schlagzeile und der Text im Video sind der arabische Teil des FACEBOOK-TEXTS (Abschnitt 8), ohne Hashtags.
Für alle gilt: keine Textübernahme aus Artikeln (nur eigene Formulierungen, Zitate unter 15 Wörtern und selten), keine erfundenen oder veränderten Fakten, Zahlen oder Zitate, keine politischen Aussagen, keine Beleidigungen von Spielern, Teams oder Fans, keine URLs, keine Quellenangaben, keine Länderflaggen-Emojis.

7. DUBLETTENPRÜFUNG, RECHERCHE UND ABSCHLUSSBERICHT
Dublettenprüfung (vollständig, nicht nur ein Ausschnitt): Durchsuche publisher/queue.json (alle Einträge) und publisher/log.jsonl nach Teamnamen, Spielernamen, Gegnern, Ergebnis und Wettbewerb, auf Arabisch, Französisch und Englisch, zum Beispiel per Python über titel und caption. Ein Treffer zu demselben Spiel, Spieler im selben Kontext oder derselben Aussage in den letzten 7 Tagen (auch mit anderer Quelle oder anderem Wortlaut) macht den Kandidaten zur Dublette: verwerfen, nächste Meldung suchen. Der Veröffentlicher prüft zusätzlich: gleiche quelle_url oder gleicher titel bei gleicher Plattform und gleichem Typ innerhalb von 24 Stunden wird abgelehnt. Die Prüfung muss ausgewertet sein, bevor ein Eintrag angelegt wird.

Recherche: WebSearch und WebFetch auf Arabisch und Englisch. Jede Suchanfrage enthält mindestens einen Saudi-Begriff (السعودية, Saudi, Saudi Arabia, SAFF, SPL) und bei Tagesnachrichten das heutige Datum oder "heute". Zuerst die Seiten der Quellenliste per WebFetch abrufen, weil dort die neuesten Meldungen mit Uhrzeit oben stehen. Nur Fakten, die in mindestens einer verlässlichen Quelle bestätigt sind und Regel A erfüllen; keine Gerüchte, keine unbestätigten Transfers. Pro Meldung Namen und URL der Quelle merken, danach Videosuche (Regel D), dann Fotosuche (Regel E). Soziale Netzwerke (X, Facebook, Instagram) werden nicht abgerufen.

QUELLENLISTE (jeweils per WebFetch auf genau diese Adresse):
 1. https://www.arriyadiyah.com/
 2. https://www.kooora.com/
 3. https://www.sportksa.net/
 4. https://www.goal.com/ar-sa
 5. https://www.spl.com.sa/en/news
 6. https://www.arabnews.com/
 7. https://www.spa.gov.sa/
 8. https://www.saff.com.sa/
 9. https://www.saff.com.sa/en/newscenter.php
10. https://www.the-afc.com/
11. https://www.arabnews.com/tags/futsal
12. https://feeds.footballco.com/kooora/feed/6p5bsxot7te8yick
13. https://ajel.sa/rss.xml
14. https://english.ajel.sa/rss.xml
Hinweis: Startseiten und Feeds sind unterschiedlich ergiebig. Nicht erreichbare Seiten werden übersprungen und im Bericht genannt.

Suchreihenfolge mit Abbruch: Es wird der Reihe nach gesucht und nur so lange, bis 1 brauchbare Meldung gefunden ist; dann sofort aufhören. Brauchbar ist eine Meldung, wenn sie Regel A erfüllt, keine Dublette ist und eine Bildquelle hat (Video oder Artikelfoto). Obergrenze: höchstens 10 erfolgreiche Recherche-Abrufe pro Lauf. Nicht erreichbare Seiten (DNS-Fehler, Timeout, 403, robots.txt-Sperre) zählen als Fehler; nicht umgehen (keine Archive), sofort die nächste Seite nehmen. Sind 10 Seiten nacheinander fehlgeschlagen, per PushNotification melden: "Quellenseiten nicht erreichbar (Netzwerkfreigabe prüfen)". Eine frische Meldung ohne Bildquelle zählt nicht als gefunden.

Findet sich nichts Neues, wird nichts angelegt, und es gibt keine Benachrichtigung.

Abschlussbericht (deutsch, kurz, Zeiten in Berliner Zeit):
 - Die Meldung in einer Zeile: Datum und Uhrzeit der Quelle, Quellenname (nur im Bericht), Themenbereich.
 - Video oder Foto (URL, Maße), Logo ja oder nein, Musik-Track (Dateiname) und Startpunkt, ob der Push nach video-out klappte.
 - Nach dem Lauf des Workflows: Status der vier Einträge aus publisher/log.jsonl (veröffentlicht oder Fehlertext).
 - Fehlgeschlagene oder nicht angelegte Einträge mit Grund; oder dass mangels frischer Meldungen nichts angelegt wurde.
 - Bestätigung "Texte arabisch fertig".
 - Verbrauch: Anzahl Recherche-Abrufe, Fehlschläge, Liste der abgerufenen Seiten mit Ergebnis.

8. MUSIK-VIDEO
Ziel: Reel und Story einer Meldung sind kurze Videos mit Hintergrundmusik aus dem Ordner Video/ dieses Repos. Das Foto der Meldung ist die Bildquelle.
 1. Gilt nur für Meldungen mit Foto. Bei einem direkten Quell-Video (Regel D) bleibt es unverändert, im Bericht "Quell-Video, keine Musik".
 2. Foto laden: curl -sL -m 30 -A "Mozilla/5.0" -o /tmp/foto.img -w "%{http_code}" "<ORIGINAL-Foto-URL>" und mit Pillow prüfen. Gelingt das nicht, zuerst den zweiten Kandidaten, sonst Regel F.
 3. Werkzeuge: python3 -m venv /tmp/venv && /tmp/venv/bin/pip install -q pillow arabic-reshaper python-bidi. story_text.py mit /tmp/venv/bin/python starten. ffmpeg ist vorhanden. Das Logo liegt unter images/logo-saudi.png.
 4. Musik zufällig wählen: Liste = sortierte Dateien Video/*.mp3. INDEX=$((RANDOM % Anzahl der Dateien)). Startpunkt im Track: ein Vielfaches von 8 Sekunden zwischen 0 und (Tracklänge minus 20 Sekunden), Länge per ffprobe.
 5. EFFEKT-VIDEO (Instagram-Reel sowie Facebook- und Instagram-Story): 1080x1920, Dauer D (siehe Schritt 7), 25 fps, H.264 + AAC, yuv420p. Unscharfer, abgedunkelter Hintergrund aus demselben Foto. Foto (Breite 1000 px) gleitet in 0,9 s von links ins Bild und zoomt danach sanft rein und raus (zoompan, Zoom 1,00 bis 1,12, 8 s Zyklus; der Bildrahmen bleibt gleich groß, der Zoom verschiebt nur den Ausschnitt). Logo oben links wächst in 0,5 s auf 106 px. Goldener Fortschrittsbalken unten (0xC9A227), füllt sich bis zum Ende. Ton mit Ein- und Ausblendung. Umsetzung: python3 make_story_video.py <Arbeitsordner> <Repo> <TAG> (der Arbeitsordner braucht foto.jpg, siehe Skript-Kopf). Diese Animation gilt für alle künftigen Läufe dieser Routine.
 6. Ist das Foto hochkant, Höhe auf höchstens 1400 px begrenzen (scale=-2:1400), damit es vollständig sichtbar bleibt. Ausgabe mit ffprobe prüfen (1080x1920, Dauer D, Audio vorhanden). Fehler: einmal wiederholen, danach Reel und Story der Meldung weglassen und melden.
 7. TEXT IM VIDEO (Reel, Facebook-Story, Instagram-Story): Der arabische Teil des FACEBOOK-TEXTS, ohne Hashtags und ohne Französisch, wird wortgetreu in Abschnitte geteilt (je Satz oder Satzgruppe, höchstens ca. 12 Wörter). Jeder Abschnitt steht 3,0 s lang, der erste beginnt ab 0,5 s, die Abschnitte folgen direkt aufeinander. D = Anzahl Abschnitte x 3,0 s, mindestens 12 s, Ende des letzten Abschnitts = D. Keine Obergrenze. Je Abschnitt ein transparentes PNG: /tmp/venv/bin/python story_text.py --out /tmp/rp<k>.png --title "<Abschnitt>" (ohne --cta und --tags). Einblendung je Abschnitt: fade=t=in:st=<Start>:d=0.4:alpha=1, enable='between(t,<Start>,<Ende>)'. Die Story bekommt nach den Textabschnitten einen Call to Action von 4,5 s am Ende, sofern Platz ist; er wird jedes Mal neu formuliert.
 8. Hosting: Branch video-out dieses Repos (öffentliche Raw-URLs): git fetch origin video-out (ist der Branch noch nicht da: anlegen); rm -rf /tmp/vo && git worktree add /tmp/vo FETCH_HEAD -B video-out; Dateien als musik-<JJJJMMTT-HHMM>-<n>-story-text.mp4 und musik-<JJJJMMTT-HHMM>-<n>-reel-text.mp4 hineinkopieren; add, commit, git push origin video-out (bei Ablehnung neu holen, rebasen, einmal wiederholen; der Push muss gelingen); Worktree entfernen. URL: https://raw.githubusercontent.com/wadiib1-ops/Images4SocialMedia_SA/video-out/<Dateiname>. Vorher per curl -sIL prüfen, dass HTTP 200 kommt (bis zu 30 Sekunden warten, einmal wiederholen). Videos nie sofort löschen; das Aufräumen übernimmt der Workflow delete-videos.yml.
 9. Reel und Story erhalten pro Meldung dieselbe Musik. Im Bericht je Meldung Track und Startpunkt nennen.

9. SPRACHE
Alle Beitragstexte sind ausschließlich auf Arabisch. Keine französische oder englische Fassung.

10. HASHTAG-LIMIT
Facebook (Feed, Reel, Story) höchstens 3 Hashtags, Instagram (Feed, Reel, Story) höchstens 5 Hashtags, pro Beitrag insgesamt, auch im Video eingeblendete. Das Limit gilt vor allen anderen Hashtag-Angaben. Der Veröffentlicher lehnt Einträge mit zu vielen Hashtags in der caption ab.
