# Forever Strong Fitness: Episode 1 social clips

Three branded 9:16 clips cut from `Episode 1 David Founder story.mp4`. The finished files are in Dropbox at `/Forever Strong Fitness/Podcast 1/Social clips`, with `Captions.txt` alongside.

| Clip | Source | Length | Hook |
|---|---|---:|---|
| 1. Why I came back | 07:23 to 08:24 | 52s | What my mum's pain taught me about lifting weights |
| 2. Not a gym person | 11:14 to 12:35 | 58s | Not a "gym person"? Watch this. |
| 3. The card | 17:36 to 18:27 | 41s | The card that nearly made me cry |

**Format:** each clip has:
- a 4K source center-cropped to 1080×1920
- jump cuts at word boundaries, removing pauses, filler and the swear word in clip 3, with 20ms audio fades at every cut
- burned-in captions in Montserrat Black, with the active word in the brand orange (`#D96220`)
- a hook card for the first 3 seconds
- the logo at the top
- a 3.5s end card: logo with the tagline, **JOIN THE WAITLIST**, "Free trial sessions from December", and "Link in bio"
- loudness normalised to −14 LUFS

**To re-render:** edit `_src/clips.json` (keep ranges, hooks and CTA), then run:

`python _src/render.py <episode.mp4> <fonts-dir> <out-dir> [clip-id …]`

It needs ffmpeg with libass, Pillow, and the Montserrat Black/ExtraBold and Inter Bold/Medium TTFs from Google Fonts.
