// Renders Memory Room carousel slides (1080x1350 PNG) from posts.json.
// Usage: node render.js   (run from this folder; needs Playwright + Chromium)
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const OUT = path.resolve(__dirname, '..');
const posts = JSON.parse(fs.readFileSync(path.join(__dirname, 'posts.json'), 'utf8'));
const esc = s => s.replace(/&/g,'&amp;').replace(/</g,'&lt;');
const noise = (op) => `url("data:image/svg+xml;utf8,${encodeURIComponent(`<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='3' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 ${op} 0'/></filter><rect width='100%' height='100%' filter='url(#n)'/></svg>`)}")`;
const linen = (base) => `background-color:${base};background-image:${noise(0.35)},repeating-linear-gradient(0deg,rgba(255,255,255,.035) 0 2px,transparent 2px 5px),repeating-linear-gradient(90deg,rgba(0,0,0,.08) 0 2px,transparent 2px 5px);`;
function body(s){
  if (s.t==='card') return `<div class="bg dark"><div class="card"><p class="q">${esc(s.text)}</p></div></div>`;
  if (s.t==='title') return `<div class="bg dark"><div class="card"><p class="title">${esc(s.text)}</p></div></div>`;
  if (s.t==='month') return `<div class="bg dark"><div class="card tall"><p class="label">${esc(s.label)}</p><p class="q">${esc(s.text)}</p></div></div>`;
  const tag = s.t==='end' ? `<p class="endline">${esc(s.text)}</p>` : '';
  return `<div class="bg light"><div class="book"><div class="b1">the story<br>the memory<br>the feeling</div><div class="b2">MEMORY ROOM</div></div>${tag}</div>`;
}
const css = `
*{margin:0;box-sizing:border-box}html,body{width:1080px;height:1350px}
.bg{width:1080px;height:1350px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:70px;font-family:'Inter',sans-serif}
.dark{${linen('#4b3529')}}
.light{${linen('#e9e3da')};background-image:${noise(0.25)},radial-gradient(ellipse at 30% 20%,rgba(255,255,255,.7),transparent 60%),radial-gradient(ellipse at 80% 90%,rgba(0,0,0,.10),transparent 55%)}
.card{width:800px;min-height:560px;background:#fbf9f5;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:90px 80px;transform:rotate(-.35deg);box-shadow:0 2px 3px rgba(0,0,0,.25),0 20px 40px rgba(0,0,0,.25)}
.card.tall{min-height:640px;gap:44px}
.q{text-wrap:balance;font-size:52px;line-height:1.32;font-weight:500;color:#2a2622;text-align:center;letter-spacing:-.005em}
.title{text-wrap:balance;font-size:64px;line-height:1.2;font-weight:600;color:#2a2622;text-align:center;letter-spacing:-.01em}
.label{font-size:30px;letter-spacing:.32em;text-transform:uppercase;color:#8a6a55;font-weight:500}
.book{width:600px;height:840px;background:linear-gradient(135deg,#5a3d2e,#3f2a1f);border-radius:6px 10px 10px 6px;display:flex;flex-direction:column;align-items:center;justify-content:space-between;padding:290px 40px 90px;transform:rotate(-4deg);box-shadow:inset 14px 0 18px -10px rgba(0,0,0,.6),0 30px 60px rgba(0,0,0,.35),0 4px 8px rgba(0,0,0,.3)}
.b1{color:#efe6dc;font-family:'Jost',sans-serif;font-weight:300;font-size:34px;letter-spacing:.14em;text-align:center;line-height:1.5;text-transform:uppercase}
.b2{color:#efe6dc;font-family:'Jost',sans-serif;font-weight:300;font-size:40px;letter-spacing:.2em}
.endline{text-wrap:balance;font-size:44px;font-weight:500;color:#3f2a1f;text-align:center;max-width:820px}
.light:has(.endline) .book{width:480px;height:672px;padding:220px 30px 70px}
.light:has(.endline) .b1{font-size:27px}.light:has(.endline) .b2{font-size:32px}`;
(async()=>{
  const b = await chromium.launch(); const pg = await b.newPage({viewport:{width:1080,height:1350},deviceScaleFactor:1});
  for (const p of posts){
    const d = path.join(OUT,p.dir); fs.mkdirSync(d,{recursive:true});
    for (const f of fs.readdirSync(d)) if (f.endsWith('.png')) fs.unlinkSync(path.join(d,f));
    for (let i=0;i<p.slides.length;i++){
      await pg.setContent(`<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Jost:wght@300&display=block" rel="stylesheet"><style>${css}</style></head><body>${body(p.slides[i])}</body></html>`,{waitUntil:'networkidle'});
      await pg.evaluate(()=>document.fonts.ready);
      await pg.screenshot({path:path.join(d,`${String(i+1).padStart(2,'0')}.png`)});
    }
    fs.writeFileSync(path.join(d,'caption.txt'),p.caption+'\n');
    console.log(p.dir,p.slides.length);
  }
  await b.close();
})();
