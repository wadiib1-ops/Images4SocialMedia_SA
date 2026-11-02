# ROUNDUP-Notizen: Saudi Pro League, Sammelmeldung je Spieltag

Stand der Notizen: 02.11.2026 (Berliner Zeit). Gilt zusätzlich zu `CLAUDE-Routine.md` und `PROMPT.md`. Das Ziel des Nutzers ist, dass die Feeds tatsächlich erstellt und veröffentlicht werden.

## 1. Regeln (vom Nutzer festgelegt)
- Der reguläre Spieltag der SPL läuft immer von Donnerstag bis Samstag. Runde 12 war 29.10. bis 31.10.2026, Runde 13 ist 05.11. bis 07.11.2026.
- Die Sammelmeldung ist eine eigene Routine neben dem Einzelspiel-Job (`JOB.md`): alle Ergebnisse der Runde auf einmal plus die Tabelle nach der Runde.
- Einzelposts zu einzelnen Spielen derselben Runde zählen nicht als Dublette. Dieselbe Runde wird als Sammelmeldung nur einmal veröffentlicht (Feld `runde` in `publisher/publish.py`).
- Auslöser: nach dem letzten Spiel am Samstag (ab Samstagabend oder Sonntag). Das Fenster ist der ganze Spieltag, nicht 32 Stunden.
- Pro Meldung vier Einträge: Facebook-Feed (höchstens 3 Hashtags), Instagram-Reel (höchstens 5), Facebook-Story und Instagram-Story (Text im Video, Begleittext leer). Kein Instagram-Feed, kein Facebook-Reel.
- Nur arabische Texte, keine Quelle im Bild, Zeiten in Berliner Zeit.

## 2. Datenquellen
Funktioniert:
- Eurosport: https://www.eurosport.de/fussball/saudi-arabien-premier-league/zeitplan-kalender-ergebnisse.shtml (alle Ergebnisse der Runde, ohne Torschützen und Minuten; im Abruf ausdrücklich nach dem ganzen Spieltag Do bis Sa fragen, nicht nur nach dem letzten Tag).
- 365scores: https://www.365scores.com/ar/football/league/saudi-league-649/standings (Tabelle und Ergebnisse; die Tabelle war nach Runde 12 nicht stimmig).

Funktioniert nicht:
- spl.com.sa/ar/standings (Tabelle lädt per JavaScript, Abruf leer; die interne Schnittstelle api-sdp.spl.com.sa wurde nicht freigegeben).
- Sofascore (HTTP 403), Fotmob (Abruf ohne Spieldaten).

## 3. Runde 12 (Eurosport, abgerufen 02.11.2026)
| Datum | Heim | Ergebnis | Gast |
|---|---|---|---|
| Do 29.10. | Al-Khaleej | 4:2 | Al-Hazm |
| Do 29.10. | Al-Nassr | 5:3 | Al-Kholood |
| Do 29.10. | Al-Riyadh | 0:6 | Al-Qadsiah |
| Fr 30.10. | Abha | 1:1 | Al-Ittihad |
| Fr 30.10. | Diriyah | 1:2 | Neom |
| Fr 30.10. | Al-Shabab | 6:1 | Al-Ahli |
| Sa 31.10. | Al-Taawoun | 1:1 | Al-Ettifaq |
| Sa 31.10. | Al-Fayha | 4:1 | Al-Faisaly |
| Sa 31.10. | Al-Hilal | 2:0 | Al-Fateh |

Alle 18 Vereine haben gespielt. Bereits als Einzelpost veröffentlicht (kein Hindernis für die Sammelmeldung): Hilal–Fateh, Fayha–Faisaly, Taawoun–Ettifaq (alle am 01.11.2026).

## 4. Tabelle
Die Tabelle von 365scores nach Runde 12 passt nicht zu den Ergebnissen (Abha und Al-Hilal mit 11 Spielen, Abha–Al-Khlood ist verschoben). Vor dem Veröffentlichen die offizielle Tabelle nach der Runde aus einer zweiten Quelle bestätigen oder aus den Ergebnissen aller Runden nachrechnen. Stand laut 365scores (nicht bestätigt): 1 Al-Hilal 30 Punkte, 2 Al-Qadsiah 28, 3 Al-Nassr 28, 4 Al-Ittihad 24, 5 Neom 22, 6 Al-Ahli 21, 7 Al-Ettifaq 19, 8 Diriyah 15, 9 Al-Khaleej 15, 10 Al-Shabab 14, 11 Al-Khlood 12, 12 Al-Riyadh 12, 13 Al-Fayha 11, 14 Al-Hazm 10, 15 Al-Faisaly 10, 16 Al-Fateh 6, 17 Al-Taawoun 5, 18 Abha 3. Dieser Stand enthält Ergebnisse vom 29. bis 31.10. wohl nur teilweise.

## 5. Technik
- Vereinsnamen arabisch und Wappen: `spl-video/teams.json` und `Wappen/`.
- Renderer für Einzelspiele: `spl-video/spl_render.py`. Ein Layout für Ergebnis-Raster und Tabelle gibt es noch nicht und muss gebaut werden (Design "Scoreboard Night": Nachtblau, Cyan #19D3F3, Magenta #FF2E88, Weiß, kein Grün, kein Gold).
- Hosting und Queue wie in `CLAUDE-Routine.md`: Bilder auf main in `images/`, Videos auf Branch `video-out`, Einträge an `publisher/queue.json` anhängen, danach Workflow `publish.yml` starten und `publisher/log.jsonl` prüfen.
