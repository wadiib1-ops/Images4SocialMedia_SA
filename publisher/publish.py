#!/usr/bin/env python3
"""Veröffentlicher für Facebook-Seite und Instagram, läuft in GitHub Actions.

Liest publisher/queue.json, veröffentlicht fällige Beiträge und schreibt jede
Aktion in publisher/log.jsonl (nur anhängen, nie überschreiben).

Das Token kommt aus der Umgebungsvariable META_USER_TOKEN (GitHub-Geheimnis).
Es wird nirgends ausgegeben oder gespeichert.
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

GRAPH = "https://graph.facebook.com/v21.0"
PAGE_ID = "1330304383510660"
IG_ID = "17841451577328406"
BASE = os.path.dirname(os.path.abspath(__file__))
QUEUE = os.path.join(BASE, "queue.json")
LOG = os.path.join(BASE, "log.jsonl")
BERLIN = ZoneInfo("Europe/Berlin")
HASHTAG_LIMIT = {"facebook": 3, "instagram": 5}


def now_utc():
    return datetime.now(timezone.utc)


def log(action, entry_id="", platform="", result="", detail=""):
    """Eine Zeile an das Protokoll anhängen. Enthält nie das Token."""
    record = {
        "zeit": now_utc().astimezone(BERLIN).strftime("%d.%m.%Y %H:%M:%S"),
        "aktion": action,
        "beitrag": entry_id,
        "plattform": platform,
        "ergebnis": result,
        "details": detail,
    }
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(json.dumps(record, ensure_ascii=False))


def call(method, path, token, **params):
    params["access_token"] = token
    url = f"{GRAPH}/{path}"
    data = None
    if method == "POST":
        data = urllib.parse.urlencode(params).encode()
    else:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, data=data, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        # Token aus Fehlertexten entfernen, falls Meta es echoed
        body = body.replace(token, "***")
        raise RuntimeError(f"Meta-Fehler HTTP {e.code}: {body[:500]}")


def count_hashtags(text):
    return len(re.findall(r"(?<!\S)#\S+", text or ""))


def wait_for_container(container_id, token):
    for _ in range(60):
        res = call("GET", container_id, token, fields="status_code,status")
        code = res.get("status_code")
        if code == "FINISHED":
            return
        if code in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Instagram-Verarbeitung: {code} ({res.get('status', '')[:300]})")
        time.sleep(5)
    raise RuntimeError("Instagram-Verarbeitung dauert zu lange")


def publish_instagram(entry, token):
    kind = entry["type"]  # "feed", "reel", "story"
    if kind == "story":
        params = {"media_type": "STORIES"}
        if entry.get("video_url"):
            params["video_url"] = entry["video_url"]
        else:
            params["image_url"] = entry["image_url"]
    elif kind == "photo":
        params = {"image_url": entry["image_url"], "caption": entry.get("caption", "")}
    elif kind in ("feed", "reel"):
        params = {
            "media_type": "REELS",
            "video_url": entry["video_url"],
            "caption": entry.get("caption", ""),
            "share_to_feed": "true" if kind == "feed" else "false",
        }
        if entry.get("cover_url"):
            params["cover_url"] = entry["cover_url"]
    else:
        raise RuntimeError(f"Unbekannter Instagram-Typ: {kind}")

    container = call("POST", f"{IG_ID}/media", token, **params)["id"]
    wait_for_container(container, token)
    return call("POST", f"{IG_ID}/media_publish", token, creation_id=container)["id"]


def page_token(token):
    return call("GET", PAGE_ID, token, fields="access_token")["access_token"]


def publish_facebook_video_upload(entry, token, edge, **finish):
    """Reel (video_reels) oder Video-Story (video_stories) per file_url hochladen."""
    ptoken = page_token(token)
    start = call("POST", f"{PAGE_ID}/{edge}", ptoken, upload_phase="start")
    video_id = start["video_id"]
    req = urllib.request.Request(
        start["upload_url"], method="POST",
        headers={"Authorization": f"OAuth {ptoken}", "file_url": entry["video_url"]})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            r.read()
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace").replace(ptoken, "***")
        raise RuntimeError(f"Meta-Upload HTTP {e.code}: {body[:500]}")
    call("POST", f"{PAGE_ID}/{edge}", ptoken, upload_phase="finish", video_id=video_id, **finish)
    return video_id


def set_facebook_thumbnail(video_id, cover_url, ptoken):
    """Cover als bevorzugtes Vorschaubild (Thumbnail) des Facebook-Reels setzen (Fehler brechen nicht ab)."""
    try:
        with urllib.request.urlopen(cover_url, timeout=60) as r:
            img = r.read()
        b = "----thumb" + str(int(time.time()))
        body = (f"--{b}\r\nContent-Disposition: form-data; name=\"is_preferred\"\r\n\r\ntrue\r\n"
                f"--{b}\r\nContent-Disposition: form-data; name=\"source\"; filename=\"cover.jpg\"\r\n"
                f"Content-Type: image/jpeg\r\n\r\n").encode() + img + f"\r\n--{b}--\r\n".encode()
        req = urllib.request.Request(
            f"{GRAPH}/{video_id}/thumbnails", data=body, method="POST",
            headers={"Content-Type": f"multipart/form-data; boundary={b}",
                     "Authorization": f"OAuth {ptoken}"})
        urllib.request.urlopen(req, timeout=120).read()
    except Exception as e:
        print(f"Thumbnail-Hinweis: {str(e).replace(ptoken, '***')[:200]}")


def publish_facebook(entry, token):
    if entry["type"] == "reel":
        vid = publish_facebook_video_upload(
            entry, token, "video_reels", video_state="PUBLISHED",
            description=entry.get("caption", ""))
        if entry.get("cover_url"):
            time.sleep(20)
            set_facebook_thumbnail(vid, entry["cover_url"], page_token(token))
        return vid
    if entry["type"] == "story":
        return publish_facebook_video_upload(entry, token, "video_stories")
    if entry["type"] == "video":
        res = call("POST", f"{PAGE_ID}/videos", token,
                   file_url=entry["video_url"], description=entry.get("caption", ""))
    else:
        res = call("POST", f"{PAGE_ID}/photos", token,
                   url=entry["image_url"], message=entry.get("caption", ""))
    return res["id"]


def load_queue():
    if not os.path.exists(QUEUE):
        return []
    with open(QUEUE, encoding="utf-8") as f:
        return json.load(f)


def save_queue(queue):
    with open(QUEUE, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)
        f.write("\n")


def is_due(entry, now):
    status = entry.get("status")
    if status == "now":
        return True
    if status == "scheduled":
        return datetime.fromisoformat(entry["publish_at"]) <= now
    return False  # paused, published, failed, ...


SPERRE_STUNDEN = 24


def bereits_verwendet(entry, queue, now):
    """Quelle oder Titel in den letzten 24 Stunden schon veröffentlicht?
    Zusätzlich 'runde' für Botola-Beiträge: dieselbe Runde nur einmal.
    Gibt den Grund zurück oder None."""
    fenster = SPERRE_STUNDEN * 3600
    for e in queue:
        if e is entry or e.get("status") != "published":
            continue
        # Geschwister-Einträge derselben Meldung (anderer Kanal/Typ) sind keine Dubletten
        if (e.get("platform"), e.get("type")) != (entry.get("platform"), entry.get("type")):
            continue
        zeit_str = e.get("published_at")
        if not zeit_str:
            continue
        if (now - datetime.fromisoformat(zeit_str)).total_seconds() >= fenster:
            continue
        if entry.get("quelle_url") and entry.get("quelle_url") == e.get("quelle_url"):
            return f"Quelle bereits am {zeit_str} veröffentlicht"
        if entry.get("titel") and entry.get("titel") == e.get("titel"):
            return f"Titel bereits am {zeit_str} veröffentlicht"
        if entry.get("runde") and entry.get("runde") == e.get("runde"):
            return f"Runde '{entry['runde']}' bereits veröffentlicht"
    return None


def run(token):
    queue = load_queue()
    now = now_utc()
    changed = False

    for entry in queue:
        eid = entry.get("id", "?")
        platform = entry.get("platform", "")
        if entry.get("status") == "paused":
            continue
        if not is_due(entry, now):
            continue

        limit = HASHTAG_LIMIT.get(platform)
        if limit is None:
            entry["status"] = "failed"
            entry["error"] = f"Unbekannte Plattform: {platform}"
            log("fehlgeschlagen", eid, platform, "fehler", entry["error"])
            changed = True
            continue

        grund = bereits_verwendet(entry, queue, now)
        if grund:
            entry["status"] = "failed"
            entry["error"] = grund
            log("übersprungen", eid, platform, "fehler", grund)
            changed = True
            continue

        n = count_hashtags(entry.get("caption", ""))
        if n > limit:
            entry["status"] = "failed"
            entry["error"] = f"{n} Hashtags, erlaubt sind {limit}"
            log("fehlgeschlagen", eid, platform, "fehler", entry["error"])
            changed = True
            continue

        try:
            if platform == "instagram":
                meta_id = publish_instagram(entry, token)
            else:
                meta_id = publish_facebook(entry, token)
            entry["status"] = "published"
            entry["meta_id"] = meta_id
            entry["published_at"] = now.isoformat()
            entry.pop("error", None)
            log("veröffentlicht", eid, platform, "erfolg", f"Meta-ID {meta_id}")
        except RuntimeError as e:
            entry["status"] = "failed"
            entry["error"] = str(e)
            log("fehlgeschlagen", eid, platform, "fehler", str(e))
        changed = True

    if changed:
        save_queue(queue)
    log("lauf", detail=f"{len(queue)} Einträge geprüft")


def main():
    user_token = os.environ.get("META_USER_TOKEN", "").strip()
    if not user_token:
        sys.exit("Fehler: Geheimnis META_USER_TOKEN ist nicht gesetzt.")
    try:
        page = call("GET", PAGE_ID, user_token, fields="access_token")
        token = page["access_token"]
    except RuntimeError as e:
        log("lauf", result="fehler", detail=f"Seiten-Token nicht abrufbar: {e}")
        sys.exit(1)
    run(token)


if __name__ == "__main__":
    main()
