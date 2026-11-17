#!/usr/bin/env python3
"""Search Openverse for free sound effects, download them, and record each one's licence.

Standard library only. No API key needed (anonymous use is rate-limited; page size max 20).

  openverse.py search "coin drop" [--license cc0,by] [--max-seconds 8] [--n 10] [--source freesound] [--json]
  openverse.py fetch ID [ID ...] --out sfx/openverse
  openverse.py grab "coin drop" --out sfx/openverse [--n 4] [--license cc0] [--max-seconds 8]

Every downloaded file gets an entry in <out>/LICENSES.json and a line in <out>/CREDITS.md
(title, creator, licence, licence URL, source page, attribution text). Nothing is saved
without its licence record.
"""
import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://api.openverse.org/v1/audio/"
UA = "openverse-sfx-skill/1.0 (Claude Code skill; searches Openverse for CC-licensed audio)"
# Licences that allow use in an edited, commercial video. "by" needs a credit; cc0 / pdm need nothing.
DEFAULT_LICENSES = "cc0,pdm,by"
NEEDS_CREDIT = {"by", "by-sa", "by-nd", "by-nc", "by-nc-sa", "by-nc-nd", "sampling+"}


def get(url, binary=False, tries=3):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            return data if binary else json.loads(data.decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and attempt < tries - 1:
                time.sleep(3 * (attempt + 1))
                continue
            raise
        except urllib.error.URLError:
            if attempt < tries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            raise


def search(query, licenses, max_seconds, n, extension=None, source=None):
    params = {"q": query, "license": licenses, "page_size": 20, "mature": "false"}
    if source:
        params["source"] = source
    if extension:
        params["extension"] = extension
    if max_seconds and max_seconds <= 30:
        params["length"] = "shortest"  # Openverse bucket: under 30 s
    out, page = [], 1
    while len(out) < n and page <= 5:
        params["page"] = page
        d = get(API + "?" + urllib.parse.urlencode(params))
        for r in d.get("results", []):
            dur = (r.get("duration") or 0) / 1000.0
            if max_seconds and dur and dur > max_seconds:
                continue
            out.append(r)
            if len(out) >= n:
                break
        if page >= (d.get("page_count") or 1):
            break
        page += 1
    return out


def row(r):
    lic = (r.get("license") or "?").upper()
    ver = r.get("license_version") or ""
    dur = (r.get("duration") or 0) / 1000.0
    return (f"{r['id']}  {dur:6.1f}s  {lic + ' ' + ver:<10}  {r.get('filetype') or '?':<4}  "
            f"{(r.get('title') or '')[:48]:<48}  by {(r.get('creator') or '?')[:24]}  [{r.get('provider')}]")


def slug(text):
    s = re.sub(r"[^a-zA-Z0-9]+", "-", text or "sound").strip("-").lower()
    return s[:50] or "sound"


def record(r, filename):
    lic = r.get("license") or ""
    return {
        "file": filename,
        "openverse_id": r["id"],
        "title": r.get("title"),
        "creator": r.get("creator"),
        "creator_url": r.get("creator_url"),
        "license": lic,
        "license_version": r.get("license_version"),
        "license_url": r.get("license_url"),
        "credit_required": lic in NEEDS_CREDIT,
        "attribution": r.get("attribution"),
        "source_page": r.get("foreign_landing_url"),
        "download_url": r.get("url"),
        "provider": r.get("provider"),
        "duration_s": round((r.get("duration") or 0) / 1000.0, 3),
        "openverse_page": f"https://openverse.org/audio/{r['id']}",
        "fetched": time.strftime("%Y-%m-%d"),
    }


def fetch(results, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    ledger_path = out / "LICENSES.json"
    ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else []
    have = {e["openverse_id"] for e in ledger}
    saved, failed = [], []
    for r in results:
        if r["id"] in have:
            print(f"skip (already saved): {r.get('title')}")
            continue
        ext = (r.get("filetype") or Path(urllib.parse.urlparse(r["url"]).path).suffix.lstrip(".") or "mp3").lower()
        name = f"{slug(r.get('title'))}-{r['id'][:8]}.{ext}"
        try:
            data = get(r["url"], binary=True)
        except Exception as e:  # the file host refused; say where to get it by hand
            failed.append((r, str(e)))
            print(f"FAILED {r.get('title')}: {e}\n  get it from {r.get('foreign_landing_url')}", file=sys.stderr)
            continue
        if len(data) < 512:
            failed.append((r, "empty file"))
            print(f"FAILED {r.get('title')}: file too small ({len(data)} bytes)", file=sys.stderr)
            continue
        (out / name).write_bytes(data)
        ledger.append(record(r, name))
        saved.append(name)
        print(f"saved {out / name}  [{(r.get('license') or '').upper()}]")
    ledger_path.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n")
    lines = ["# Sound credits (Openverse)", "",
             "Generated by openverse.py. CC BY sounds must be credited wherever the video is published.", ""]
    for e in ledger:
        mark = "credit required" if e["credit_required"] else "no credit required"
        lines.append(f"- `{e['file']}`: \"{e['title']}\" by {e['creator']}, "
                     f"{e['license'].upper()} {e['license_version'] or ''} ({mark}). "
                     f"{e['source_page']} / {e['license_url']}")
    (out / "CREDITS.md").write_text("\n".join(lines) + "\n")
    print(f"\n{len(saved)} saved, {len(failed)} failed. Licence ledger: {ledger_path}")
    return 1 if failed and not saved else 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("search", "grab"):
        s = sub.add_parser(name)
        s.add_argument("query")
        s.add_argument("--license", default=DEFAULT_LICENSES,
                       help=f"comma list of Openverse licence codes (default {DEFAULT_LICENSES})")
        s.add_argument("--max-seconds", type=float, default=10.0, help="skip longer files (0 = any length)")
        s.add_argument("--n", type=int, default=10 if name == "search" else 4)
        s.add_argument("--extension", help="mp3, wav, ogg, flac")
        s.add_argument("--source", help="only these Openverse sources, e.g. freesound or wikimedia_audio")
        if name == "search":
            s.add_argument("--json", action="store_true")
        else:
            s.add_argument("--out", required=True)
    f = sub.add_parser("fetch")
    f.add_argument("ids", nargs="+")
    f.add_argument("--out", required=True)
    a = p.parse_args()

    try:
        if a.cmd == "fetch":
            return fetch([get(f"{API}{i}/") for i in a.ids], a.out)
        res = search(a.query, a.license, a.max_seconds, a.n, a.extension, a.source)
        if not res:
            print("no results: try a plainer query (two or three words) or widen --license / --max-seconds",
                  file=sys.stderr)
            return 1
        if a.cmd == "search":
            if a.json:
                print(json.dumps([record(r, None) for r in res], indent=2, ensure_ascii=False))
            else:
                for r in res:
                    print(row(r))
            return 0
        return fetch(res, a.out)
    except urllib.error.HTTPError as e:
        print(f"openverse: error: HTTP {e.code} from {e.url}", file=sys.stderr)
        return 1
    except urllib.error.URLError as e:
        print(f"openverse: error: {e.reason}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
