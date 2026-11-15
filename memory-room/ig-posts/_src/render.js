// Renders The Memory Room carousel slides (1080x1350 PNG) from posts.json, in the brand system
// taken from the brand's own Canva posts: real paper background + logo (brand/), headline
// colour #7a4e3a, Fraunces SOFT 700 (match for the Canva headline font), Jost 700 sublines,
// logo tan #cba98c, CTA pill #37291f.   Usage: node render.js
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const OUT = path.resolve(__dirname, '..');
const posts = JSON.parse(fs.readFileSync(path.join(__dirname, 'posts.json'), 'utf8'));
const b64 = f => 'data:image/png;base64,' + fs.readFileSync(path.join(__dirname, 'brand', f)).toString('base64');
const PLATE = b64('plate.png'), PAPER = b64('paper.png'), LOGO = b64('logo.png'), LOGOB = b64('logo-brown.png');
const esc = s => s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/'/g,'’');
const bubble = `<svg width="56" height="57" viewBox="0 0 56 57"><path d="M28 4C14.2 4 4 13.3 4 25s10.2 21 24 21c2.6 0 5-.3 7.3-.9L46 52l-2.4-11.2C49.4 37 52 31.4 52 25 52 13.3 41.8 4 28 4z" fill="none" stroke="#7a4e3a" stroke-width="5" stroke-linejoin="round"/></svg>`;
function size(t){ const n=t.length; return n<40?96:n<70?88:n<95?80:72; }
function body(s){
  if (s.t==='q') return `<div class="pg" style="background-image:url(${PLATE})"><div class="mid"><h1 style="font-size:${s.big?150:size(s.text)}px">${esc(s.text)}</h1>${s.comment?`<p class="sub">${bubble}<span>Comment your answer below</span></p>`:''}</div></div>`;
  if (s.t==='month') return `<div class="pg" style="background-image:url(${PLATE})"><div class="mid"><p class="label">${esc(s.label)}</p><h1 style="font-size:${size(s.text)}px">${esc(s.text)}</h1></div></div>`;
  if (s.t==='logo') return `<div class="pg" style="background-image:url(${PAPER})"><div class="mid"><img class="biglogo" src="${LOGO}"></div></div>`;
  return `<div class="pg" style="background-image:url(${PAPER})"><div class="mid end"><img class="endlogo" src="${LOGOB}"><h2>${esc(s.text)}</h2><div class="pill">CAPTURE THEIR STORY</div><p class="small">${esc(s.sub)}</p></div></div>`;
}
const css = `*{margin:0;box-sizing:border-box}html,body{width:1080px;height:1350px}
.pg{width:1080px;height:1350px;background-size:cover;position:relative}
.mid{position:absolute;left:52px;right:52px;top:30px;bottom:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:56px}
h1{font-family:'Fraunces';font-variation-settings:'SOFT' 100,'WONK' 0;font-weight:700;color:#7a4e3a;line-height:.95;text-align:center;text-wrap:balance}
.sub{display:flex;align-items:center;gap:14px;font-family:'Jost';font-weight:700;font-size:45px;color:#7a4e3a}
.label{font-family:'Jost';font-weight:700;font-size:40px;letter-spacing:.28em;text-transform:uppercase;color:#cba98c;margin-bottom:-14px}
.biglogo{width:620px}
.end{bottom:0;gap:0}.endlogo{width:330px;margin-bottom:90px}
h2{font-family:'Fraunces';font-variation-settings:'SOFT' 100,'WONK' 0;font-weight:700;color:#7a4e3a;font-size:76px;line-height:1;text-align:center;text-wrap:balance;max-width:900px;margin-bottom:80px}
.pill{background:#37291f;color:#fff;font-family:'Jost';font-weight:500;font-size:36px;letter-spacing:.04em;padding:30px 64px;border-radius:999px;margin-bottom:44px}
.small{text-wrap:balance;font-family:'Jost';font-weight:500;font-size:31px;color:#5a3d31;text-align:center;max-width:900px}`;
(async()=>{
  const b = await chromium.launch(); const pg = await b.newPage({viewport:{width:1080,height:1350},deviceScaleFactor:1});
  for (const p of posts){
    const d = path.join(OUT,p.dir); fs.mkdirSync(d,{recursive:true});
    for (const f of fs.readdirSync(d)) if (f.endsWith('.png')) fs.unlinkSync(path.join(d,f));
    for (let i=0;i<p.slides.length;i++){
      await pg.setContent(`<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght,SOFT,WONK@9..144,700,100,0&family=Jost:wght@500;700&display=block" rel="stylesheet"><style>${css}</style></head><body>${body(p.slides[i])}</body></html>`,{waitUntil:'networkidle'});
      await pg.evaluate(()=>document.fonts.ready);
      await pg.screenshot({path:path.join(d,`${String(i+1).padStart(2,'0')}.png`)});
    }
    fs.writeFileSync(path.join(d,'caption.txt'),p.caption+'\n');
    console.log(p.dir,p.slides.length);
  }
  await b.close();
})();
