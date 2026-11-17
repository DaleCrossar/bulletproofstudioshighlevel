# Sound effects for video edits: three free tools

Source: Instagram reel by @jaytonburnett, posted 16 Nov 2026
(https://www.instagram.com/reel/DfzwscexBOa/).

## What the video says

Claude cannot hear, so the sound effects it added to edits were poor. Three free tools fix that:

1. **real-sfx** finds the moments in an edit that need a sound and lands one on the exact frame.
2. **Openverse** is where Claude searches for free sounds when the library lacks the right one, and it records a
   licence for every sound it finds.
3. **earshot** gives Claude ears: it listens to every sound Claude picked and throws out any that sound fake or do
   not fit.

In the test shown, Claude pulled four sounds from Openverse (Coins, Chain and lock on fence, Coins dropping,
coinSounds.wav). All four passed the earshot check, so all four went into the edit.

## What is installed here

| tool | where | from |
|---|---|---|
| real-sfx | `.claude/skills/real-sfx` | [Clipwing/skills](https://github.com/Clipwing/skills), scripts MIT, bundled UI sounds CC0 |
| openverse-sfx | `.claude/skills/openverse-sfx` | written for this repo; uses the public [Openverse API](https://api.openverse.org) |
| earshot | `.claude/skills/earshot` | [Leonxlnx/earshot](https://github.com/Leonxlnx/earshot), MIT |

Claude Code loads all three as skills in this repo. Ask for "add sound effects to this video" and they chain:
real-sfx finds the cue points, openverse-sfx fills gaps in the library, earshot checks each pick.

## One-time setup on your computer

Needs Python 3.10+, ffmpeg and [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
# earshot: the program behind the earshot skill (downloads two models, about 1.1 GB, runs on CPU)
uv tool install "earshot[mcp] @ git+https://github.com/Leonxlnx/earshot"
earshot doctor --fetch

# optional: keep earshot's models loaded between calls (much faster than one CLI call at a time)
claude mcp add earshot --scope user -e EARSHOT_THREADS=3 -- earshot mcp

# real-sfx: check its tools, and point it at your own sound library if you have one
python .claude/skills/real-sfx/scripts/setup.py check
python .claude/skills/real-sfx/scripts/setup.py init --library main="/path/to/your/SFX" --uisfx --index
```

Without a library of your own, real-sfx still has its 78 bundled UI cues, and openverse-sfx supplies the rest.

openverse-sfx needs no setup and no account.
