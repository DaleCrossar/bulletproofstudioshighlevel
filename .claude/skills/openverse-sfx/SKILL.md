---
name: openverse-sfx
description: Find free, openly licensed sound effects on Openverse (CC0 / public domain / CC BY recordings, mostly from Freesound) when the local sound library has nothing that fits, download them, and record a licence for every file. Use when a video edit needs a sound that real-sfx could not supply, or when the user asks to find, search or download a free sound effect, foley, ambience or "a sound of X", or asks where a sound came from and whether it can be used. Pairs with real-sfx (places sounds on the frame) and earshot (listens to each pick and rejects fakes and misfits).
---

# openverse-sfx: free sounds, each with a licence

Openverse (openverse.org) indexes over 800 million openly licensed works, including audio. This skill searches its
audio API, downloads the picks, and writes a licence record for each file. No API key is needed.

All commands use `scripts/openverse.py` in this skill's folder (Python standard library only).

## When to use it

1. real-sfx reports a moment with no fitting sound in the library ("stays quiet" in its cue report), or the user asks
   for a sound the library does not have.
2. Search here, download a few candidates, and let earshot listen to them before anything goes in the edit.

Never put a downloaded sound in an edit unheard. You cannot hear; a title like "coin drop" says nothing about what the
file holds.

## Steps

1. **Search** with a plain two- or three-word description of the sound itself, not of the scene:

   ```
   python scripts/openverse.py search "coin drop" --n 10
   ```

   Each row: id, length, licence, file type, title, creator, source. Defaults: licences `cc0,pdm,by`, files of 10 s or
   less. `--license cc0` when the user wants nothing to credit. `--max-seconds 0` for ambiences and long recordings.
   `--json` for the full records.

2. **Download** three to five candidates, not one:

   ```
   python scripts/openverse.py grab "coin drop" --n 4 --out sfx/openverse
   python scripts/openverse.py fetch <id> <id> --out sfx/openverse      # or pick ids from a search
   ```

   Each saved file gets an entry in `sfx/openverse/LICENSES.json` and a line in `sfx/openverse/CREDITS.md`: title,
   creator, licence and its URL, source page, attribution text, and whether a credit is required.

3. **Listen with earshot** and keep only what passes (see the earshot skill):

   ```
   earshot rank "a single coin dropping on a hard table" sfx/openverse --top 4
   earshot realness sfx/openverse/<file>
   earshot find sfx/openverse/<file> "a single coin hit" --top 3      # the cleanest moment in a longer file
   ```

   Throw out a pick when the description match is weak or no match, or when it reads as code-synthesized and the user
   wants real recordings. Delete the rejected file and remove its entry from `LICENSES.json` and `CREDITS.md`.

4. **Hand the keepers to real-sfx** as a fallback library, then re-run its mix:

   ```
   python ../real-sfx/scripts/setup.py add-library openverse sfx/openverse --tier extra --index
   ```

5. **Report** to the user: which sounds went in and at what time, each one's earshot numbers, its licence, and the
   credit lines the video needs.

## Licences

| code | meaning | in a video |
|---|---|---|
| `cc0`, `pdm` | public domain | use freely, no credit |
| `by` | CC BY | use freely, credit the creator (the `attribution` text in the ledger) |
| `by-sa` | CC BY-ShareAlike | credit required; ask the user first, the share-alike term can reach the video |
| `by-nc*` | non-commercial | not for client or monetised work; never download without the user saying so |
| `by-nd*` | no derivatives | editing or mixing the sound may not be allowed; avoid |

The default search leaves out everything below `by`. When any `by` sound is in the final edit, give the user the
lines from `CREDITS.md` to paste into the video description. Openverse reports the licence the source site lists; for
paid client work, open the `source_page` and confirm it before delivery.

## When a download fails

`FAILED ... HTTP Error 403` or `429` means the file host (usually `cdn.freesound.org`) refused the request, which
happens from cloud machines and data-centre addresses. The search still works. Options: run the same command on the
user's own computer, pick a result from another source (`--source wikimedia_audio`), or give the user the source page
link the script printed so they can download it by hand into the same folder (then add its entry to the ledger from
`search --json`). Do not retry in a loop.
