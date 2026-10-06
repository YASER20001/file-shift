// Motion graphics renderer: HTML/CSS cards -> PNG sequences (opaque) and alpha PNG overlays.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const path = require('path');

const HERE = __dirname;
const OUT = path.join(HERE, 'mg');
fs.mkdirSync(OUT, { recursive: true });
const FPS = 30;
const durs = JSON.parse(fs.readFileSync(path.join(HERE, 'vo', 'durations.json')));

const CSS = `
@import url('');
:root{--bg:#070b16;--bg2:#101a33;--acc:#22d3c5;--acc2:#4f7cff;--txt:#eef2ff;--mut:#8b96b8;}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1920px;height:1080px;overflow:hidden;background:transparent;font-family:"Inter Display","Inter",system-ui,sans-serif;color:var(--txt)}
.stage{position:relative;width:1920px;height:1080px;overflow:hidden}
.bg{position:absolute;inset:0;background:radial-gradient(1200px 800px at 30% 20%,#13204a 0%,transparent 60%),radial-gradient(900px 700px at 80% 90%,#0c2a33 0%,transparent 60%),linear-gradient(160deg,#0a1024 0%,#070b16 60%,#05070f 100%)}
.grid{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);background-size:96px 96px;mask-image:radial-gradient(ellipse at center,#000 30%,transparent 80%);-webkit-mask-image:radial-gradient(ellipse at center,#000 30%,transparent 80%)}
.glow{position:absolute;border-radius:50%;opacity:.7;animation:drift 14s ease-in-out infinite alternate}
.g1{width:1300px;height:1300px;left:-400px;top:-500px;background:radial-gradient(circle,#1b3a8a 0%,rgba(27,58,138,0) 65%)}
.g2{width:1200px;height:1200px;right:-450px;bottom:-550px;background:radial-gradient(circle,#0f5f66 0%,rgba(15,95,102,0) 65%);animation-delay:-6s}
.g3{width:900px;height:900px;left:45%;top:-10%;background:radial-gradient(circle,#3b2a86 0%,rgba(59,42,134,0) 65%);opacity:.4;animation-delay:-3s}
@keyframes drift{from{transform:translate(0,0) scale(1)}to{transform:translate(120px,80px) scale(1.12)}}
.vignette{position:absolute;inset:0;background:radial-gradient(ellipse at center,transparent 55%,rgba(0,0,0,.55) 100%)}
.center{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 160px}
.h1{font-size:92px;font-weight:600;letter-spacing:-.02em;line-height:1.1}
.h1 .w{display:inline-block;opacity:0;filter:blur(14px);transform:translateY(30px);animation:wIn .9s cubic-bezier(.2,.8,.2,1) forwards}
@keyframes wIn{to{opacity:1;filter:blur(0);transform:none}}
.chips{display:flex;gap:22px;margin-top:54px}
.chip{padding:16px 30px;border:1px solid rgba(255,255,255,.14);border-radius:999px;font-size:30px;font-weight:500;color:var(--txt);background:rgba(255,255,255,.05);opacity:0;transform:translateY(24px) scale(.96);animation:cIn .7s cubic-bezier(.2,.8,.2,1) forwards}
.chip::before{content:"";display:inline-block;width:12px;height:12px;border-radius:50%;background:var(--acc);margin-right:14px;vertical-align:middle;box-shadow:0 0 18px var(--acc)}
@keyframes cIn{to{opacity:1;transform:none}}
.eyebrow{font-size:26px;letter-spacing:.42em;text-transform:uppercase;color:var(--acc);font-weight:600;opacity:0;animation:fadeUp 1s .1s forwards}
@keyframes fadeUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:none}}
.logo{font-size:260px;font-weight:700;letter-spacing:-.04em;line-height:1;background:linear-gradient(135deg,#fff 0%,#cfe6ff 45%,#22d3c5 100%);-webkit-background-clip:text;background-clip:text;color:transparent;opacity:0;transform:scale(.86);filter:blur(20px);animation:logoIn 1.4s .2s cubic-bezier(.2,.8,.2,1) forwards}
@keyframes logoIn{to{opacity:1;transform:none;filter:blur(0)}}
.logoGlow{position:absolute;width:1100px;height:520px;left:410px;top:280px;background:radial-gradient(ellipse,rgba(34,211,197,.3),transparent 65%);opacity:0;animation:fadeUp 1.6s .4s forwards}
.sub{font-size:40px;font-weight:400;color:var(--mut);letter-spacing:.18em;text-transform:uppercase;margin-top:28px;opacity:0;animation:trackIn 1.3s .9s cubic-bezier(.2,.8,.2,1) forwards}
@keyframes trackIn{from{opacity:0;letter-spacing:.5em;transform:translateY(14px)}to{opacity:1;letter-spacing:.18em;transform:none}}
.line{width:0;height:3px;background:linear-gradient(90deg,var(--acc),var(--acc2));margin:38px auto 0;animation:lineIn 1s 1.1s cubic-bezier(.2,.8,.2,1) forwards;border-radius:2px}
@keyframes lineIn{to{width:260px}}
/* chapter */
.chap{position:absolute;left:200px;top:0;height:1080px;display:flex;flex-direction:column;justify-content:center}
.chapNum{position:absolute;right:120px;top:50%;transform:translateY(-50%);font-size:720px;font-weight:700;color:rgba(255,255,255,.035);letter-spacing:-.06em;line-height:1;opacity:0;animation:numIn 1.6s .1s cubic-bezier(.2,.8,.2,1) forwards}
@keyframes numIn{from{opacity:0;transform:translateY(-50%) translateX(120px)}to{opacity:1;transform:translateY(-50%)}}
.chapT{font-size:120px;font-weight:600;letter-spacing:-.025em;line-height:1.05;margin-top:26px;overflow:hidden}
.chapT span{display:block;transform:translateY(110%);animation:rise 1s .35s cubic-bezier(.2,.8,.2,1) forwards}
@keyframes rise{to{transform:none}}
.chapS{font-size:40px;color:var(--mut);margin-top:30px;opacity:0;animation:fadeUp 1s .9s forwards;font-weight:400}
.chapLine{width:0;height:4px;background:linear-gradient(90deg,var(--acc),var(--acc2));margin-top:44px;border-radius:2px;animation:lineIn2 1.1s .6s cubic-bezier(.2,.8,.2,1) forwards}
@keyframes lineIn2{to{width:420px}}
/* recap */
.tiles{display:flex;gap:40px;margin-top:70px}
.tile{width:480px;padding:48px 44px;border-radius:28px;background:linear-gradient(180deg,rgba(255,255,255,.08),rgba(255,255,255,.03));border:1px solid rgba(255,255,255,.12);text-align:left;opacity:0;transform:translateY(60px);animation:cIn .9s cubic-bezier(.2,.8,.2,1) forwards;box-shadow:0 30px 80px rgba(0,0,0,.45)}
.tile .ic{width:84px;height:84px;border-radius:22px;display:flex;align-items:center;justify-content:center;margin-bottom:34px;background:linear-gradient(135deg,var(--acc),var(--acc2));box-shadow:0 10px 40px rgba(34,211,197,.35)}
.tile .ic svg{width:44px;height:44px;stroke:#071018;fill:none;stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round}
.tile h3{font-size:44px;font-weight:600;letter-spacing:-.01em}
.tile p{font-size:28px;color:var(--mut);margin-top:14px;line-height:1.35;font-weight:400}
.tag{font-size:54px;font-weight:500;color:var(--txt);margin-top:40px;opacity:0;animation:fadeUp 1s 1.4s forwards;letter-spacing:-.01em}
.tag b{color:var(--acc);font-weight:600}
/* overlays */
.lower{position:absolute;left:120px;bottom:110px;display:flex;align-items:stretch;gap:0;border-radius:18px;overflow:hidden;background:rgba(8,12,24,.78);border:1px solid rgba(255,255,255,.14);box-shadow:0 20px 60px rgba(0,0,0,.5)}
.lower .bar{width:10px;background:linear-gradient(180deg,var(--acc),var(--acc2))}
.lower .tx{padding:22px 40px 24px 30px}
.lower h4{font-size:44px;font-weight:600;letter-spacing:-.01em;line-height:1.1}
.lower p{font-size:26px;color:var(--mut);margin-top:6px;font-weight:400}
.callout{position:absolute;display:inline-flex;align-items:center;gap:16px;padding:18px 30px 18px 24px;border-radius:999px;background:rgba(8,12,24,.86);border:1px solid rgba(34,211,197,.45);box-shadow:0 14px 50px rgba(0,0,0,.5),0 0 0 6px rgba(34,211,197,.08);font-size:34px;font-weight:600;letter-spacing:-.005em;white-space:nowrap}
.callout .dot{width:16px;height:16px;border-radius:50%;background:var(--acc);box-shadow:0 0 22px var(--acc)}
.frameShadow{position:absolute;left:120px;top:98px;width:1680px;height:884px;border-radius:20px;box-shadow:0 50px 140px rgba(0,0,0,.75),0 0 0 1px rgba(255,255,255,.08)}
.watermark{position:absolute;right:70px;top:38px;font-size:30px;font-weight:700;letter-spacing:.08em;color:rgba(255,255,255,.5)}
.watermark small{display:block;font-size:14px;letter-spacing:.3em;font-weight:500;color:rgba(255,255,255,.35);margin-top:2px}
`;

function page(body, opaque = true) {
  const bg = opaque ? `<div class="bg"></div><div class="glow g1"></div><div class="glow g2"></div><div class="glow g3"></div><div class="grid"></div><div class="vignette"></div>` : '';
  return `<!doctype html><html><head><meta charset="utf-8"><style>${CSS}</style></head><body><div class="stage">${bg}${body}</div>
<script>window.__seek=(s)=>{document.getAnimations().forEach(a=>{a.pause();a.currentTime=s*1000;});};</script></body></html>`;
}

const words = (txt, start = 0.15, step = 0.12) => txt.split(' ').map((w, i) => `<span class="w" style="animation-delay:${(start + i * step).toFixed(2)}s">${w}&nbsp;</span>`).join('');
const chips = (arr, start) => `<div class="chips">${arr.map((c, i) => `<div class="chip" style="animation-delay:${(start + i * 0.22).toFixed(2)}s">${c}</div>`).join('')}</div>`;

const ICONS = {
  chart: '<svg viewBox="0 0 24 24"><path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/></svg>',
  track: '<svg viewBox="0 0 24 24"><path d="M3 12h4l3-8 4 16 3-8h4"/></svg>',
  send: '<svg viewBox="0 0 24 24"><path d="M22 2 11 13M22 2l-7 20-4-9-9-4 20-7z"/></svg>',
};

const cards = {
  intro1: { d: durs.intro1 + 0.9, html: `<div class="center"><div class="h1">${words('Every engineering project runs on documents.', 0.2, 0.13)}</div>${chips(['Drawings', 'Transmittals', 'Reviews', 'Approvals'], 2.1)}</div>` },
  intro2: { d: durs.intro2 + 0.9, html: `<div class="center"><div class="h1" style="font-size:104px">${words('Keeping track of all of it', 0.1, 0.12)}<br>${words('shouldn’t be the hard part.', 1.6, 0.13)}</div></div>` },
  title: { d: Math.max(4.2, durs.title + 2.6), html: `<div class="logoGlow"></div><div class="center"><div class="eyebrow">KBR-AMCDE · Digital Engineering</div><div class="logo">PIMX</div><div class="sub">Integrated Digital Project Management Suite</div><div class="line"></div></div>` },
  ch1: { d: 3.4, html: `<div class="chapNum">01</div><div class="chap"><div class="eyebrow">Chapter 01</div><div class="chapT"><span>Power BI Dashboard</span></div><div class="chapLine"></div><div class="chapS">Live project data, embedded inside PIMX.</div></div>` },
  ch2: { d: 3.4, html: `<div class="chapNum">02</div><div class="chap"><div class="eyebrow">Chapter 02</div><div class="chapT"><span>SDC &amp; IDC Tracker</span></div><div class="chapLine"></div><div class="chapS">Where every document stands. Right now.</div></div>` },
  ch3: { d: 3.4, html: `<div class="chapNum">03</div><div class="chap"><div class="eyebrow">Chapter 03</div><div class="chapT"><span>PIMX Transmittals</span></div><div class="chapLine"></div><div class="chapS">From draft to delivery. One workflow.</div></div>` },
  recap: { d: durs.recap + 1.0, html: `<div class="center"><div class="eyebrow">One platform</div><div class="tiles">
    <div class="tile" style="animation-delay:.3s"><div class="ic">${ICONS.chart}</div><h3>Dashboards</h3><p>Live Power BI reports, inside PIMX. Export to Excel in one click.</p></div>
    <div class="tile" style="animation-delay:.55s"><div class="ic">${ICONS.track}</div><h3>Trackers</h3><p>SDC &amp; IDC status for every document, every project, every stage.</p></div>
    <div class="tile" style="animation-delay:.8s"><div class="ic">${ICONS.send}</div><h3>Transmittals</h3><p>ProjectWise documents, PM approval, cover sheets and client issue.</p></div>
  </div><div class="tag">One platform. One login. <b>Zero</b> documents lost in email.</div></div>` },
  end: { d: durs.end + 2.4, html: `<div class="logoGlow"></div><div class="center"><div class="logo" style="font-size:220px">PIMX</div><div class="sub">Built for the way engineers actually work</div><div class="line"></div><div class="eyebrow" style="margin-top:70px;animation-delay:1.6s;color:var(--mut);letter-spacing:.3em">KBR-AMCDE · Digital Engineering</div></div>` },
};

const overlays = {
  bg_frame: { opaque: true, html: `<div class="frameShadow"></div><div class="watermark">PIMX<small>DIGITAL ENGINEERING</small></div>` },
  lt_hub: { html: `<div class="lower"><div class="bar"></div><div class="tx"><h4>PIMX Home</h4><p>Integrated Digital Project Management Suite</p></div></div>` },
  lt_eth: { html: `<div class="lower"><div class="bar"></div><div class="tx"><h4>Engineering Tools Hub</h4><p>Workflows · Tags · Materials · Analytics · SDC/IDC</p></div></div>` },
  lt_dash: { html: `<div class="lower"><div class="bar"></div><div class="tx"><h4>Power BI Dashboard</h4><p>KBR iPlant Status Report · live</p></div></div>` },
  lt_reg: { html: `<div class="lower"><div class="bar"></div><div class="tx"><h4>Drawing Register</h4><p>Requested · Used · Unused — per project</p></div></div>` },
  lt_trk: { html: `<div class="lower"><div class="bar"></div><div class="tx"><h4>SDC &amp; IDC Tracker</h4><p>Connected to KBR-AMCDE-PROD</p></div></div>` },
  lt_tx: { html: `<div class="lower"><div class="bar"></div><div class="tx"><h4>Transmittals</h4><p>Draft, issue and track — ProjectWise style</p></div></div>` },
  lt_wf: { html: `<div class="lower"><div class="bar"></div><div class="tx"><h4>Transmittal Workflow</h4><p>Draft → PM approval → Client response</p></div></div>` },
  lt_regtx: { html: `<div class="lower"><div class="bar"></div><div class="tx"><h4>Transmittals Register</h4><p>Every transmittal, every status</p></div></div>` },
  co_wells: { html: `<div class="callout" style="left:0;top:0"><span class="dot"></span>256 wells · live</div>` },
  co_excel: { html: `<div class="callout" style="left:0;top:0"><span class="dot"></span>One-click Excel export</div>` },
  co_live: { html: `<div class="callout" style="left:0;top:0"><span class="dot"></span>Live Snapshot · Full Audit History</div>` },
  co_pw: { html: `<div class="callout" style="left:0;top:0"><span class="dot"></span>Direct ProjectWise integration</div>` },
  co_ai: { html: `<div class="callout" style="left:0;top:0"><span class="dot"></span>Built-in PIMX Assistant</div>` },
  co_email: { html: `<div class="callout" style="left:0;top:0"><span class="dot"></span>Auto-drafted Outlook email</div>` },
  co_issue: { html: `<div class="callout" style="left:0;top:0"><span class="dot"></span>Issue TRN to Client</div>` },
  co_sign: { html: `<div class="callout" style="left:0;top:0"><span class="dot"></span>Accept &amp; Sign (PM)</div>` },
};

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  const pg = await ctx.newPage();
  const only = process.argv[2]; const names = process.argv.slice(2);

  // overlays
  for (const [name, o] of Object.entries(overlays)) {
    if (only && only !== 'overlays') continue;
    await pg.setContent(page(o.html, !!o.opaque), { waitUntil: 'load' });
    await pg.evaluate(() => document.fonts.ready);
    await pg.evaluate(() => window.__seek(30));
    if (name.startsWith('co_') || name.startsWith('lt_')) {
      const el = await pg.$(name.startsWith('co_') ? '.callout' : '.lower');
      await el.screenshot({ path: path.join(OUT, name + '.png'), omitBackground: true });
    } else {
      await pg.screenshot({ path: path.join(OUT, name + '.png'), omitBackground: !o.opaque });
    }
    console.log('overlay', name);
  }

  const meta = {};
  for (const [name, c] of Object.entries(cards)) {
    if (names.length && !names.includes(name)) continue;
    const dir = path.join(OUT, name);
    fs.mkdirSync(dir, { recursive: true });
    await pg.setContent(page(c.html, true), { waitUntil: 'load' });
    await pg.evaluate(() => document.fonts.ready);
    const n = Math.round(c.d * FPS);
    for (let i = 0; i < n; i++) {
      await pg.evaluate((t) => window.__seek(t), i / FPS);
      await pg.screenshot({ path: path.join(dir, `f${String(i).padStart(4, '0')}.png`) });
    }
    meta[name] = { d: n / FPS, frames: n };
    console.log('card', name, n, 'frames');
  }
  if (false) fs.writeFileSync(path.join(OUT, 'cards.json'), JSON.stringify(meta, null, 1));
  await browser.close();
})();
