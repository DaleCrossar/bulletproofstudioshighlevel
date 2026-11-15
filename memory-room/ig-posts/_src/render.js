// The Memory Room carousels, v2 ("website" look). Photo slides use the session photos from the
// website design, with a warm dark fade and cream type; question slides use the brand paper.
// Fonts: Fraunces SOFT 700 (headline match), Jost (kickers / UI). Colours: #7a4e3a brown,
// #cba98c tan, #f5efe7 cream, #37291f CTA.   Usage: node render.js
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const OUT = path.resolve(__dirname, '..'), BR = path.join(__dirname, 'brand');
const posts = JSON.parse(fs.readFileSync(path.join(__dirname, 'posts.json'), 'utf8'));
const crops = JSON.parse(fs.readFileSync(path.join(BR, 'photos', 'crops.json'), 'utf8'));
const uri = (f, t='png') => `data:image/${t};base64,` + fs.readFileSync(f).toString('base64');
const PAPER = uri(path.join(BR,'paper.png')), LOGO = uri(path.join(BR,'logo.png')), LOGOB = uri(path.join(BR,'logo-brown.png'));
const photo = k => { const x = crops[k]*2400; const l = Math.min(Math.max(x-540,0),1320); return `background-image:url(${uri(path.join(BR,'photos',k+'.jpg'),'jpeg')});background-size:2400px 1350px;background-position:-${Math.round(l)}px 0`; };
const esc = s => s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/'/g,'’');
const bubble = c => `<svg width="46" height="47" viewBox="0 0 56 57"><path d="M28 4C14.2 4 4 13.3 4 25s10.2 21 24 21c2.6 0 5-.3 7.3-.9L46 52l-2.4-11.2C49.4 37 52 31.4 52 25 52 13.3 41.8 4 28 4z" fill="none" stroke="${c}" stroke-width="5" stroke-linejoin="round"/></svg>`;
const fs1 = t => { const n=t.length; return n<40?92:n<70?82:n<95?74:68; };
const bar = (i,n,dark) => `<div class="bar">${Array.from({length:n},(_,k)=>`<i class="${k<=i?'on':''} ${dark?'d':''}"></i>`).join('')}</div>`;
function body(s,i,n){
  const B = bar(i,n,s.t!=='photo'&&s.t!=='pause');
  if (s.t==='photo') return `<div class="pg ph" style="${photo(s.img)}"><div class="shade"></div>${B}<img class="toplogo" src="${LOGO}"><div class="low"><p class="kick">${esc(s.kicker)}</p><h1 class="cream" style="font-size:${fs1(s.text)}px">${esc(s.text)}</h1>${s.swipe?`<p class="swipe">Swipe <span>→</span></p>`:''}</div></div>`;
  if (s.t==='pause') return `<div class="pg ph" style="${photo(s.img)}"><div class="shade soft"></div>${B}<img class="pauselogo" src="${LOGO}"></div>`;
  if (s.t==='q') return `<div class="pg" style="background-image:url(${PAPER})">${B}<img class="toplogo" src="${LOGO}"><div class="mid"><p class="kick">${esc(s.kicker)}</p><h1 style="font-size:${s.big?170:fs1(s.text)}px">${esc(s.text)}</h1>${s.comment?`<p class="sub">${bubble('#7a4e3a')}<span>Comment your answer below</span></p>`:''}</div></div>`;
  return `<div class="pg" style="background-image:url(${PAPER})">${B}<div class="mid end"><img class="endlogo" src="${LOGOB}"><h2>${esc(s.text)}</h2><div class="pill">CAPTURE THEIR STORY</div><p class="small">${esc(s.sub)}</p></div></div>`;
}
const css = `*{margin:0;box-sizing:border-box}html,body{width:1080px;height:1350px}
.pg{width:1080px;height:1350px;background-size:cover;position:relative;overflow:hidden}
.ph{background-repeat:no-repeat}
.shade{position:absolute;inset:0;background:linear-gradient(to top,rgba(24,17,13,.92) 0%,rgba(24,17,13,.78) 30%,rgba(24,17,13,.25) 62%,rgba(24,17,13,.35) 100%),rgba(122,78,58,.10)}
.shade.soft{background:linear-gradient(to top,rgba(24,17,13,.55) 0%,rgba(24,17,13,0) 45%,rgba(24,17,13,.30) 100%)}
.bar{position:absolute;top:44px;left:60px;right:60px;display:flex;gap:10px;z-index:3}
.bar i{flex:1;height:4px;border-radius:4px;background:rgba(245,239,231,.35)}.bar i.on{background:#f5efe7}
.bar i.d{background:rgba(122,78,58,.22)}.bar i.d.on{background:#7a4e3a}
.toplogo{position:absolute;top:84px;left:50%;transform:translateX(-50%);width:150px;z-index:3}
.pauselogo{position:absolute;bottom:80px;left:50%;transform:translateX(-50%);width:260px;z-index:3}
.low{position:absolute;left:80px;right:80px;bottom:120px;display:flex;flex-direction:column;align-items:center;gap:30px;z-index:3}
.mid{position:absolute;left:70px;right:70px;top:60px;bottom:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:40px}
.kick{font-family:'Jost';font-weight:600;font-size:28px;letter-spacing:.32em;text-transform:uppercase;color:#cba98c;text-align:center}
h1{font-family:'Fraunces';font-variation-settings:'SOFT' 100,'WONK' 0;font-weight:700;color:#7a4e3a;line-height:1;text-align:center;text-wrap:balance}
h1.cream{color:#f5efe7;text-shadow:0 2px 24px rgba(0,0,0,.35)}
.swipe{font-family:'Jost';font-weight:500;font-size:28px;letter-spacing:.2em;text-transform:uppercase;color:rgba(245,239,231,.8);margin-top:24px}.swipe span{font-size:34px;margin-left:8px}
.sub{display:flex;align-items:center;gap:14px;font-family:'Jost';font-weight:700;font-size:40px;color:#7a4e3a;margin-top:10px}
.end{gap:0;top:0}.endlogo{width:330px;margin-bottom:90px}
h2{font-family:'Fraunces';font-variation-settings:'SOFT' 100,'WONK' 0;font-weight:700;color:#7a4e3a;font-size:76px;line-height:1;text-align:center;text-wrap:balance;max-width:900px;margin-bottom:80px}
.pill{background:#37291f;color:#fff;font-family:'Jost';font-weight:500;font-size:36px;letter-spacing:.06em;padding:30px 64px;border-radius:999px;margin-bottom:44px}
.small{font-family:'Jost';font-weight:500;font-size:31px;color:#5a3d31;text-align:center;max-width:900px;text-wrap:balance}`;
(async()=>{
  const b = await chromium.launch(); const pg = await b.newPage({viewport:{width:1080,height:1350},deviceScaleFactor:1});
  for (const p of posts){
    const d = path.join(OUT,p.dir); fs.mkdirSync(d,{recursive:true});
    for (const f of fs.readdirSync(d)) if (f.endsWith('.png')) fs.unlinkSync(path.join(d,f));
    for (let i=0;i<p.slides.length;i++){
      await pg.setContent(`<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght,SOFT,WONK@9..144,700,100,0&family=Jost:wght@500;600;700&display=block" rel="stylesheet"><style>${css}</style></head><body>${body(p.slides[i],i,p.slides.length)}</body></html>`,{waitUntil:'networkidle'});
      await pg.evaluate(()=>document.fonts.ready);
      await pg.screenshot({path:path.join(d,`${String(i+1).padStart(2,'0')}.png`)});
    }
    fs.writeFileSync(path.join(d,'caption.txt'),p.caption+'\n');
    console.log(p.dir,p.slides.length);
  }
  await b.close();
})();
