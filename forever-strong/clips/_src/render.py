"""Forever Strong Fitness: render branded 9:16 podcast clips.
Usage: python render.py <path-to-episode.mp4> <fonts-dir> <out-dir>
Reads clips.json (edit list), words_med.json / words.json (word timings), logo PNGs in this folder."""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
SRC, FONTS, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
HERE = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT, exist_ok=True); TMP = os.path.join(OUT, '_tmp'); os.makedirs(TMP, exist_ok=True)
cfg = json.load(open(os.path.join(HERE, 'clips.json')))
WM = {'med': json.load(open(os.path.join(HERE, 'words_med.json'))), 'small': json.load(open(os.path.join(HERE, 'words.json')))}
ORANGE = (217, 98, 32); W, H = 1080, 1920
def font(name, size):
    for f in os.listdir(FONTS):
        p = os.path.join(FONTS, f); 
        if ImageFont.truetype(p, 10).getname() == name: return ImageFont.truetype(p, size)
    raise SystemExit('font missing: %s' % (name,))
BLACK = ('Montserrat', 'Black'); XB = ('Montserrat', 'ExtraBold'); IB = ('Inter', 'Bold'); IM = ('Inter', 'Medium')

def hook_png(lines, hi, path):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); sz = 92
    while True:
        f = font(BLACK, sz); hs = [d.textbbox((0, 0), l, font=f) for l in lines]
        if max(b[2] - b[0] for b in hs) <= 880 or sz <= 50: break
        sz -= 2
    lh = int(sz * 1.17); total = lh * len(lines)
    y0 = 330; pad = 34
    bw = max(b[2] - b[0] for b in hs) + pad * 2
    d.rounded_rectangle([(W - bw) / 2, y0 - pad, (W + bw) / 2, y0 + total + pad - 14], 28, fill=(10, 10, 10, 235))
    for i, l in enumerate(lines):
        b = hs[i]; x = (W - (b[2] - b[0])) / 2 - b[0]
        d.text((x, y0 + i * lh - b[1] + 6), l, font=f, fill=ORANGE if l in hi else (255, 255, 255))
    im.save(path)

def endcard_png(path):
    im = Image.new('RGB', (W, H), (11, 11, 11)); d = ImageDraw.Draw(im)
    lg = Image.open(os.path.join(HERE, 'logo_tag_cut.png')); lw = 760; lg = lg.resize((lw, int(lg.height * lw / lg.width)), Image.LANCZOS)
    im.paste(lg, ((W - lw) // 2, 520), lg)
    c = cfg['cta']; f = font(BLACK, 58); b = d.textbbox((0, 0), c['pill'], font=f); tw = b[2] - b[0]
    py = 1180; d.rounded_rectangle([(W - tw) / 2 - 60, py, (W + tw) / 2 + 60, py + 128], 64, fill=ORANGE)
    d.text(((W - tw) / 2 - b[0], py + 64 - (b[1] + b[3]) / 2), c['pill'], font=f, fill=(255, 255, 255))
    for txt, fn, sz, y, col in [(c['line'], IB, 44, 1370, (255, 255, 255)), (c['small'], IM, 36, 1440, (170, 170, 170))]:
        ff = font(fn, sz); b = d.textbbox((0, 0), txt, font=ff); d.text(((W - (b[2] - b[0])) / 2 - b[0], y), txt, font=ff, fill=col)
    im.save(path)

def segments(words, keep, drop, fixes):
    kept = []
    for i, w in enumerate(words):
        if any(a <= w['s'] < b for a, b in keep) and w['w'].strip('.,?!').lower() not in drop:
            ww = dict(w); ww['i'] = i; ww['w'] = fixes.get('%.1f' % w['s'], w['w']); kept.append(ww)
    # merge '-y' style fragments into previous word for captions
    out = []
    for w in kept:
        if w['w'].startswith('-') and out: out[-1]['w'] += w['w'][1:]; out[-1]['e'] = w['e']
        else: out.append(w)
    segs = []
    for j, w in enumerate(out):
        nxt = words[w['i'] + 1]['s'] if w['i'] + 1 < len(words) else w['e'] + 0.5
        prv = words[w['i'] - 1]['e'] if w['i'] > 0 else w['s'] - 0.5
        s = max(w['s'] - 0.07, prv + 0.01) if not (segs and out[j - 1]['i'] == w['i'] - 1 and w['s'] - out[j - 1]['e'] < 0.32) else None
        e = min(w['e'] + 0.14, nxt - 0.02) if w['e'] + 0.14 < nxt else w['e'] + 0.02
        if s is None: segs[-1][1] = max(segs[-1][1], e); segs[-1][2].append(w)
        else: segs.append([s, e, [w]])
    return segs

def ass_time(t): h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60; return '%d:%02d:%05.2f' % (h, m, s)

def captions(segs, path):
    t = 0; items = []
    for s, e, ws in segs:
        for w in ws: items.append((t + w['s'] - s, t + w['e'] - s, w['w']))
        t += e - s
    groups = []; cur = []
    for it in items:
        cur.append(it)
        if len(cur) == 3 or it[2][-1:] in '.,?!': groups.append(cur); cur = []
    if cur: groups.append(cur)
    hdr = ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 2\n\n[V4+ Styles]\n"
           "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
           "Style: C,Montserrat Black,84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,7,3,2,80,80,560,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    ev = []
    for gi, g in enumerate(groups):
        nxt = groups[gi + 1][0][0] if gi + 1 < len(groups) else 1e9
        for k, (s, e, w) in enumerate(g):
            end = g[k + 1][0] if k + 1 < len(g) else min(e + 0.25, nxt)
            txt = ' '.join(('{\\c&H2062D9&}%s{\\c&HFFFFFF&}' % x[2].upper()) if j == k else x[2].upper() for j, x in enumerate(g))
            ev.append('Dialogue: 0,%s,%s,C,,0,0,0,,%s' % (ass_time(s), ass_time(end), txt))
    open(path, 'w').write(hdr + '\n'.join(ev) + '\n'); return t

def run(cmd): print(' '.join(cmd[:6]), '...'); subprocess.run(cmd, check=True)

endcard = os.path.join(TMP, 'endcard.png'); endcard_png(endcard)
cx = cfg['crop_center']; cw = int(2160 * 9 / 16); x0 = int(3840 * cx - cw / 2)
only = sys.argv[4:] 
for c in cfg['clips']:
    if only and c['id'] not in only: continue
    src, key = c['words'].split(':'); words = WM[src][key]
    segs = segments(words, c['keep'], set(c.get('drop_words', [])), c.get('fix_at', {}))
    ass = os.path.join(TMP, c['id'] + '.ass'); dur = captions(segs, ass)
    hook = os.path.join(TMP, c['id'] + '_hook.png'); hook_png(c['hook'], c['hook_hi'], hook)
    t0 = segs[0][0] - 1.0; n = len(segs); cat = ''
    fc = ['[0:v]crop=%d:2160:%d:0,scale=1080:1920:flags=lanczos,fps=25,split=%d%s' % (cw, x0, n, ''.join('[s%d]' % i for i in range(n))),
          '[0:a]asplit=%d%s' % (n, ''.join('[t%d]' % i for i in range(n)))]
    for i, (s, e, _) in enumerate(segs):
        a, b = s - t0, e - t0; L = e - s; fd = min(0.02, L / 4)
        fc.append('[s%d]trim=%.3f:%.3f,setpts=PTS-STARTPTS[v%d]' % (i, a, b, i))
        fc.append('[t%d]atrim=' % i + '%.3f:%.3f,asetpts=PTS-STARTPTS,afade=t=in:d=%.3f,afade=t=out:st=%.3f:d=%.3f[a%d]' % (a, b, fd, L - fd, fd, i))
        cat += '[v%d][a%d]' % (i, i)
    fc.append(cat + 'concat=n=%d:v=1:a=1[cv][ca]' % len(segs))
    fc.append("[cv]subtitles='%s':fontsdir='%s'[sv]" % (ass, FONTS))
    fc.append('[2:v]scale=300:-1[lg];[sv][lg]overlay=(W-w)/2:110[lv]')
    fc.append("[lv][1:v]overlay=0:0:enable='lt(t,3.2)'[hv]")
    fc.append('[3:v]loop=loop=-1:size=1,trim=duration=3.5,fps=25,setsar=1,format=yuv420p,settb=1/25[ec]')
    fc.append('[hv]fps=25,format=yuv420p,setsar=1,settb=1/25[hv2];[hv2][ec]xfade=transition=fade:duration=0.35:offset=%.3f[vout]' % (dur - 0.35))
    fc.append('[ca]afade=t=out:st=%.3f:d=0.35,apad=pad_dur=3.2,loudnorm=I=-14:TP=-1.5:LRA=11[aout]' % (dur - 0.35))
    out = os.path.join(OUT, c['id'] + '.mp4')
    run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', '%.3f' % t0, '-t', '%.3f' % (segs[-1][1] - t0 + 0.5), '-i', SRC,
         '-loop', '1', '-i', hook, '-i', os.path.join(HERE, 'logo_cut.png'), '-i', endcard,
         '-filter_complex', ';'.join(fc), '-map', '[vout]', '-map', '[aout]', '-c:v', 'libx264', '-preset', 'medium', '-crf', '19',
         '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', '-shortest', out])
    print(c['id'], 'segments', len(segs), 'speech %.1fs' % dur, '-> total %.1fs' % (dur + 3.15))
