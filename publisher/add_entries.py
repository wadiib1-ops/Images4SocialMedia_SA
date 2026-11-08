#!/usr/bin/env python3
"""Hängt neue Einträge an publisher/queue.json an (vorhandene bleiben unverändert).

Aufruf: python3 publisher/add_entries.py <eintraege.json>
Die JSON-Datei enthält eine Liste von Einträgen (Format siehe CLAUDE-Routine.md).
Bricht ab, wenn eine id schon existiert.
"""
import json, os, sys

queue_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "queue.json")
new = json.load(open(sys.argv[1], encoding="utf-8"))
queue = json.load(open(queue_path, encoding="utf-8"))
ids = {e["id"] for e in queue}
dup = [e["id"] for e in new if e["id"] in ids]
if dup:
    sys.exit(f"id bereits vorhanden: {dup}")
queue += new
json.dump(queue, open(queue_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print(f"{len(new)} Einträge angehängt, gesamt {len(queue)}")
