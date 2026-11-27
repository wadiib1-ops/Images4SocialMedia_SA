#!/usr/bin/env python3
"""Holt die Follower-Zahlen und schreibt sie nach publisher/followers.json.
Veröffentlicht nichts, ändert queue.json und log.jsonl nie. Das Token wird nie ausgegeben."""
import json, os, sys, urllib.request, urllib.parse, urllib.error
from datetime import datetime
from zoneinfo import ZoneInfo

GRAPH = "https://graph.facebook.com/v21.0"
PAGE_ID = "1330304383510660"
IG_ID = "17841451577328406"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT, LOG = os.path.join(HERE, "followers.json"), os.path.join(HERE, "followers_log.jsonl")

def get(path, token, **params):
    params["access_token"] = token
    try:
        with urllib.request.urlopen(f"{GRAPH}/{path}?{urllib.parse.urlencode(params)}", timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        try: err = json.load(e).get("error", {})
        except Exception: err = {}
        raise RuntimeError(f"Meta HTTP {e.code}: {str(err.get('message',''))[:160]} (Code {err.get('code','?')})")
    except Exception as e:
        raise RuntimeError(f"{type(e).__name__}: {str(e)[:120]}")

def main():
    token = os.environ.get("META_USER_TOKEN", "").strip()
    if not token: sys.exit("Fehler: Geheimnis META_USER_TOKEN ist nicht gesetzt.")
    try: old = json.load(open(OUT, encoding="utf-8"))
    except Exception: old = {}
    now = datetime.now(ZoneInfo("Europe/Berlin")); iso = now.isoformat(timespec="seconds")
    new = {"updated_at": iso, "facebook": old.get("facebook", {}), "instagram": old.get("instagram", {}), "errors": {}}
    scrub = lambda e: str(e).replace(token, "***")
    try: ptoken = get(PAGE_ID, token, fields="access_token")["access_token"]
    except Exception as e: ptoken = None; new["errors"]["token"] = scrub(e)
    if ptoken:
        try:
            p = get(PAGE_ID, ptoken, fields="followers_count,fan_count")
            new["facebook"] = {"followers": p.get("followers_count"), "likes": p.get("fan_count"), "at": iso}
        except Exception as e: new["errors"]["facebook"] = scrub(e)
        try:
            i = get(IG_ID, ptoken, fields="followers_count,username")
            new["instagram"] = {"followers": i.get("followers_count"), "username": i.get("username"), "at": iso}
        except Exception as e: new["errors"]["instagram"] = scrub(e)
    json.dump(new, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    if not new["errors"]:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps({"zeit": now.strftime("%d.%m.%Y %H:%M:%S"), "facebook": new["facebook"].get("followers"), "instagram": new["instagram"].get("followers")}, ensure_ascii=False) + "\n")
    print("Follower:", {k: v for k, v in new.items() if k != "updated_at"})

main()
