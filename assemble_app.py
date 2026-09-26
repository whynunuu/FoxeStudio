import json

with open("foxe_full_state.json", "r", encoding="utf-8") as f:
    full_state = json.load(f)

# Read the base HTML provided by the user
# We'll create a script to inject full_state into index.html
state_json_str = json.dumps(full_state, ensure_ascii=False)

html_template = """<!doctype html>
<html lang="id" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Foxe Studio Keuangan</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">
<script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
<style>
/* ============================================================
   Foxe Studio — sistem visual mengikuti DESIGNclaude.md
   Kanvas krem, serif editorial untuk angka & judul, koral sebagai
   satu-satunya voltase warna, permukaan gelap hangat untuk rail.
   ============================================================ */
:root{
  /* permukaan krem */
  --canvas:#faf9f5; --surface:#fffefb; --surface2:#f5f0e8; --surface3:#efe9de;
  --surface4:#e8e0d2;
  --hairline:#e6dfd8; --hairline-soft:#ebe6df; --hairline-strong:#d9d1c6;
  /* tinta */
  --ink:#141413; --ink2:#3d3d3a; --ink-strong:#252523;
  --muted:#6c6a64; --muted-soft:#8e8b82;
  /* voltase */
  --accent:#cc785c; --accent-ink:#a9583e; --accent-soft:#f6e9e2;
  --on-accent:#ffffff;
  /* permukaan gelap — dipakai untuk rail, bukan latar halaman */
  --rail:#181715; --rail2:#1f1e1b; --rail3:#252320;
  --on-rail:#faf9f5; --on-rail-soft:#a09d96; --rail-line:#2e2b27;
  /* seri data */
  --cash:#1f7a68; --transfer:#b3603f; --lead:#96702a; --dp:#7d4a5f; --omzet:#3d3d3a;
  /* semantik */
  --good:#2f7d4f; --warn:#8a6408; --crit:#a83b2e;
  --good-bg:#e6efe7; --warn-bg:#f5ecd9; --crit-bg:#f7e7e1;
  --grid:#ece6dd;
  --shadow:0 1px 3px rgba(20,20,19,.06);
  --ff-display:"Cormorant Garamond",Tiempos Headline,Garamond,"Times New Roman",serif;
  --ff-body:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
  --ff-mono:"JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
}

:root[data-theme="dark"], html[data-theme="dark"]{
  --canvas:#141413; --surface:#1b1a18; --surface2:#22211e; --surface3:#292724;
  --surface4:#32302b;
  --hairline:#2a2926; --hairline-soft:#242320; --hairline-strong:#3a3834;
  --ink:#faf9f5; --ink2:#d3cfc7; --ink-strong:#ebe7df;
  --muted:#a09d96; --muted-soft:#87847d;
  --accent:#d97757; --accent-ink:#e99072; --accent-soft:#2e211b;
  --on-accent:#ffffff;
  --rail:#100f0e; --rail2:#181715; --rail3:#22201d;
  --on-rail:#faf9f5; --on-rail-soft:#a09d96; --rail-line:#24221f;
  --cash:#3eb89b; --transfer:#d97757; --lead:#e8a55a; --dp:#cf93a8; --omzet:#cfcbc3;
  --good:#5db872; --warn:#d4a017; --crit:#e07a68;
  --good-bg:#19271f; --warn-bg:#2a2414; --crit-bg:#2d1e1a;
  --grid:#242320;
  --shadow:0 1px 3px rgba(0,0,0,.5);
}

*{box-sizing:border-box}
[hidden]{display:none!important}
body{background:var(--canvas);color:var(--ink2);font-family:var(--ff-body);
  font-size:14.5px;line-height:1.55;-webkit-font-smoothing:antialiased;
  font-feature-settings:"cv05","ss01";margin:0;padding:0}
h1,h2,h3,h4{margin:0;text-wrap:balance;color:var(--ink)}
h3,h4{font-family:var(--ff-body);font-weight:500;letter-spacing:0}
p{margin:0}
button,input,select,textarea{font:inherit;color:inherit}
a{color:var(--accent)}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:4px}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}

/* ---------- shell ---------- */
.app{display:grid;grid-template-columns:230px minmax(0,1fr);min-height:100vh}
.rail{background:var(--rail);border-right:1px solid var(--rail-line);padding:22px 0 30px;
  position:sticky;top:0;height:100vh;overflow-y:auto;display:flex;flex-direction:column;gap:18px}
.brand{padding:0 20px;display:flex;align-items:center;gap:10px}
.brand svg{flex:0 0 auto}
.brand .mark{font-family:var(--ff-display);font-size:25px;font-weight:600;line-height:1.05;
  letter-spacing:-.5px;color:var(--on-rail);display:block}
.brand .sub{font-family:var(--ff-body);font-size:11px;font-weight:500;letter-spacing:1.5px;
  text-transform:uppercase;color:var(--on-rail-soft);display:block;margin-top:2px}
.nav{display:flex;flex-direction:column;gap:1px;padding:0 12px}
.nav .grp{font-family:var(--ff-body);font-size:11px;font-weight:500;letter-spacing:1.5px;
  text-transform:uppercase;color:var(--on-rail-soft);padding:16px 10px 6px}
.nav button{display:flex;align-items:center;justify-content:space-between;gap:8px;width:100%;
  text-align:left;background:none;border:0;padding:8px 12px;border-radius:8px;
  color:var(--on-rail-soft);cursor:pointer;font-size:13.5px;font-weight:500;
  transition:background .12s,color .12s}
.nav button:hover{background:var(--rail3);color:var(--on-rail)}
.nav button[aria-current="true"]{background:var(--accent);color:var(--on-accent);font-weight:600}
.nav button[aria-current="true"] .cnt{color:rgba(255,255,255,0.85)}
.nav .cnt{font-family:var(--ff-mono);font-size:11px;color:var(--on-rail-soft);
  font-variant-numeric:tabular-nums}
.main{min-width:0;display:flex;flex-direction:column;background:var(--canvas)}

.topbar{position:sticky;top:0;z-index:20;background:color-mix(in srgb,var(--canvas) 92%,transparent);
  backdrop-filter:blur(10px);border-bottom:1px solid var(--hairline);padding:13px 28px;
  display:flex;align-items:center;gap:14px;flex-wrap:wrap}
.period{display:flex;align-items:baseline;gap:10px}
.period b{font-family:var(--ff-display);font-size:22px;font-weight:600;letter-spacing:-.3px;
  color:var(--ink)}
.period .co{font-family:var(--ff-mono);font-size:11.5px;color:var(--muted);
  font-variant-numeric:tabular-nums}
.spacer{flex:1}
.pill{display:inline-flex;align-items:center;gap:5px;padding:3px 11px;border-radius:9999px;
  font-size:12px;font-weight:500;border:1px solid transparent;white-space:nowrap;letter-spacing:.1px}
.pill.prog{background:var(--warn-bg);color:var(--warn);border-color:color-mix(in srgb,var(--warn) 24%,transparent)}
.pill.final{background:var(--good-bg);color:var(--good);border-color:color-mix(in srgb,var(--good) 24%,transparent)}
.pill.bad{background:var(--crit-bg);color:var(--crit);border-color:color-mix(in srgb,var(--crit) 24%,transparent)}
.pill.neutral{background:var(--surface3);color:var(--ink2);border-color:var(--hairline)}
.btn{background:var(--surface);border:1px solid var(--hairline-strong);border-radius:8px;
  padding:8px 16px;font-size:13.5px;font-weight:500;cursor:pointer;color:var(--ink);white-space:nowrap;
  transition:background .12s,border-color .12s}
.btn:hover{background:var(--surface2)}
.btn.pri{background:var(--accent);border-color:var(--accent);color:var(--on-accent)}
.btn.pri:hover{background:var(--accent-ink);border-color:var(--accent-ink);color:var(--on-accent)}
.btn.sm{padding:4px 11px;font-size:12px}
.btn:disabled{opacity:.5;cursor:not-allowed}
.presence{display:flex;align-items:center}
.dot{width:9px;height:9px;border-radius:50%;background:var(--good)}

.view{padding:28px 32px 80px;max-width:1600px;width:100%;margin:0 auto;box-sizing:border-box}
.view[hidden]{display:none}
.vhead{display:flex;align-items:flex-end;gap:16px;margin-bottom:22px;flex-wrap:wrap}
.vhead h2{font-family:var(--ff-display);font-size:38px;font-weight:600;letter-spacing:-.8px;
  line-height:1.08;color:var(--ink)}
.vhead p{color:var(--muted);font-size:14px;max-width:64ch;line-height:1.55}
.eyebrow{font-family:var(--ff-body);font-size:11px;font-weight:500;letter-spacing:1.5px;
  text-transform:uppercase;color:var(--muted-soft)}

/* ---------- blok ---------- */
.card{background:var(--surface);border:1px solid var(--hairline);border-radius:12px;padding:22px}
.card > h3{font-size:16px;font-weight:500;margin-bottom:14px;display:flex;align-items:center;
  gap:10px;justify-content:space-between;color:var(--ink)}
.grid{display:grid;gap:16px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:0;
  background:var(--surface);border:1px solid var(--hairline);border-radius:12px;overflow:hidden}
.stat{padding:16px 20px;border-right:1px solid var(--hairline);display:flex;flex-direction:column;
  gap:4px;min-width:0}
.stat:last-child{border-right:0}
.stat .k{font-family:var(--ff-body);font-size:11px;font-weight:500;letter-spacing:1.4px;
  text-transform:uppercase;color:var(--muted-soft)}
.stat .v{font-family:var(--ff-display);font-size:clamp(20px,1.9vw,31px);font-weight:600;line-height:1.1;
  letter-spacing:-.6px;font-variant-numeric:tabular-nums;color:var(--ink);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.stat .v.sm{font-size:clamp(17px,1.6vw,25px);letter-spacing:-.4px}
.stat .m{font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums}
.stat .bar{height:3px;border-radius:2px;background:var(--surface4);overflow:hidden;margin-top:5px}
.stat .bar i{display:block;height:100%;background:var(--accent)}

table{width:100%;border-collapse:collapse;font-size:13.5px}
.tw{overflow-x:auto;-webkit-overflow-scrolling:touch;border:1px solid var(--hairline);border-radius:12px;background:var(--surface);width:100%;max-width:100%;scrollbar-width:thin;scrollbar-color:var(--hairline-strong) var(--surface)}
.tw::-webkit-scrollbar{height:6px}
.tw::-webkit-scrollbar-track{background:var(--surface)}
.tw::-webkit-scrollbar-thumb{background:var(--hairline-strong);border-radius:3px}
th{text-align:left;font-family:var(--ff-body);font-size:11px;letter-spacing:1.2px;
  text-transform:uppercase;color:var(--muted-soft);font-weight:500;padding:11px 14px;
  border-bottom:1px solid var(--hairline);white-space:nowrap;background:var(--surface2);
  position:sticky;top:0;z-index:2}
td{padding:9px 14px;border-bottom:1px solid var(--hairline-soft);color:var(--ink2);word-break:normal}
tbody tr:last-child td{border-bottom:0}
tbody tr:hover td{background:var(--surface2)}
td.n,th.n{text-align:right;font-family:var(--ff-mono);font-variant-numeric:tabular-nums;
  font-size:12.5px;white-space:nowrap}
td.mono,th.mono{white-space:nowrap}
tr.future td{color:var(--muted-soft);background:var(--surface)}
tr.total td{font-weight:600;background:var(--surface2);border-top:1px solid var(--hairline-strong);
  color:var(--ink)}
.heat{position:relative;isolation:isolate}
.heat i{position:absolute;left:0;top:3px;bottom:3px;border-radius:3px;z-index:-1;opacity:.22}
.muted{color:var(--muted)}
.tiny{font-size:12px}
.mono{font-family:var(--ff-mono);font-variant-numeric:tabular-nums;font-size:12.5px}

/* ---------- form ---------- */
.form{display:grid;grid-template-columns:repeat(auto-fit,minmax(148px,1fr));gap:12px;align-items:end}
.f{display:flex;flex-direction:column;gap:5px;min-width:0}
.f label{font-family:var(--ff-body);font-size:11px;font-weight:500;letter-spacing:1.2px;
  text-transform:uppercase;color:var(--muted-soft)}
.f input,.f select{background:var(--canvas);border:1px solid var(--hairline-strong);border-radius:8px;
  padding:9px 12px;font-size:14px;width:100%;height:40px;color:var(--ink)}
.f input:focus,.f select:focus{border-color:var(--accent);outline:none;
  box-shadow:0 0 0 3px color-mix(in srgb,var(--accent) 15%,transparent)}
.f.wide{grid-column:span 2}
.rowact{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.del{background:none;border:0;color:var(--muted-soft);cursor:pointer;padding:3px 6px;
  border-radius:6px;font-size:14px;line-height:1}
.del:hover{background:var(--crit-bg);color:var(--crit)}
.note{font-size:13px;color:var(--ink2);background:var(--surface3);border:1px solid var(--hairline);
  border-left:3px solid var(--hairline-strong);padding:12px 16px;border-radius:0 8px 8px 0;
  line-height:1.55}
.note.warn{background:var(--warn-bg);border-color:color-mix(in srgb,var(--warn) 20%,transparent);
  border-left-color:var(--warn)}
.note.crit{background:var(--crit-bg);border-color:color-mix(in srgb,var(--crit) 20%,transparent);
  border-left-color:var(--crit)}
.note.ok{background:var(--good-bg);border-color:color-mix(in srgb,var(--good) 20%,transparent);
  border-left-color:var(--good)}

/* ---------- grafik ---------- */
.chart{width:100%;display:block;overflow:visible}
.legend{display:flex;gap:16px;flex-wrap:wrap;font-size:12.5px;color:var(--muted);margin-bottom:12px}
.legend span{display:inline-flex;align-items:center;gap:6px}
.swatch{width:10px;height:10px;border-radius:2px;display:inline-block}
.tip{position:fixed;pointer-events:none;background:var(--rail);border:1px solid var(--rail-line);
  border-radius:8px;padding:10px 13px;font-size:12.5px;color:var(--on-rail);z-index:60;opacity:0;
  transition:opacity .1s}
.tip b{display:block;margin-bottom:5px;font-size:13px;color:#fff}
.tip .r{display:flex;justify-content:space-between;gap:18px;font-family:var(--ff-mono);
  font-size:11.5px;color:var(--on-rail-soft);font-variant-numeric:tabular-nums}

.screen{display:grid;gap:6px}
.chk{display:flex;align-items:flex-start;gap:10px;font-size:13px;padding:8px 11px;border-radius:8px;
  background:var(--surface2);line-height:1.5}
.chk b{color:var(--ink);font-weight:500}
.chk .badge{font-family:var(--ff-body);font-size:10px;font-weight:500;letter-spacing:1.2px;
  padding:2px 8px;border-radius:9999px;flex-shrink:0;margin-top:2px}
.chk.ok .badge{background:var(--good-bg);color:var(--good)}
.chk.bad .badge{background:var(--crit-bg);color:var(--crit)}
.chk.warn .badge{background:var(--warn-bg);color:var(--warn)}

/* ---------- kalender bulanan ---------- */
.calwrap{overflow-x:auto}
.cal{display:grid;grid-template-columns:repeat(7,minmax(76px,1fr)) 104px;gap:1px;
  background:var(--hairline);border:1px solid var(--hairline);border-radius:12px;overflow:hidden;
  min-width:680px;--hc:var(--accent)}
.cal .hd{background:var(--surface2);padding:9px 11px;font-family:var(--ff-body);font-size:11px;
  font-weight:500;letter-spacing:1.3px;text-transform:uppercase;color:var(--muted-soft)}
.cel{background:var(--surface);min-height:82px;padding:8px 11px;display:flex;flex-direction:column;
  position:relative}
.cel.void{background:var(--surface2)}
.cel .dn{font-family:var(--ff-mono);font-size:11px;color:var(--muted-soft);
  font-variant-numeric:tabular-nums}
.cel .ab{display:inline-block;margin-left:6px;font-family:var(--ff-body);font-size:9px;
  font-weight:500;letter-spacing:.8px;font-style:normal;padding:1px 6px;border-radius:9999px;
  background:var(--warn-bg);color:var(--warn);vertical-align:1px}
.cel .dv{font-family:var(--ff-display);font-size:17px;font-weight:600;letter-spacing:-.3px;
  font-variant-numeric:tabular-nums;margin-top:4px;color:var(--ink)}
.cel .dm{font-size:11px;color:var(--muted);font-variant-numeric:tabular-nums;margin-top:1px}
.cel.on::after{content:"";position:absolute;left:0;top:0;bottom:0;pointer-events:none;z-index:0;
  width:calc(7% + var(--h) * 93%);
  background:linear-gradient(90deg,
    color-mix(in srgb,var(--hc) 34%,transparent) 0%,
    color-mix(in srgb,var(--hc) 19%,transparent) 62%,
    color-mix(in srgb,var(--hc) 4%,transparent) 100%)}
.cel.on::before{content:"";position:absolute;left:0;top:0;bottom:0;width:2px;z-index:1;
  background:var(--hc);opacity:calc(.35 + var(--h) * .65)}
.cel.on .dn{color:var(--ink2)}
.cel > span{position:relative;z-index:2}
.cel.today{box-shadow:inset 0 0 0 1.5px var(--accent);z-index:3}
.cel.wk{background:var(--surface2)}
.cel.wk .wl{font-family:var(--ff-body);font-size:10px;font-weight:500;letter-spacing:1.2px;
  text-transform:uppercase;color:var(--muted-soft)}
.seg{display:inline-flex;border:1px solid var(--hairline-strong);border-radius:8px;overflow:hidden}
.seg button{background:var(--surface);border:0;padding:6px 14px;font-size:13px;cursor:pointer;
  color:var(--muted);border-right:1px solid var(--hairline);font-weight:500}
.seg button:last-child{border-right:0}
.seg button:hover{background:var(--surface2)}
.seg button[aria-pressed="true"]{background:var(--surface4);color:var(--ink)}
.calhead{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;flex-wrap:wrap;
  margin-bottom:16px}
.calhead .mo{font-family:var(--ff-display);font-size:26px;font-weight:600;letter-spacing:-.5px;
  line-height:1.1;color:var(--ink)}

/* ---------- riwayat pembaruan ---------- */
.dashmid{display:grid;grid-template-columns:minmax(0,1fr) 288px;gap:16px;
  align-items:start;margin-bottom:16px}
@media (max-width:1120px){.dashmid{grid-template-columns:1fr}
  .updwrap{max-width:420px}}
.updwrap .card{padding:18px}
.updwrap h3{font-size:15px;margin-bottom:12px}
.upd{display:grid;gap:4px}
.urow{display:grid;grid-template-columns:1fr auto;gap:12px;align-items:center;
  padding:9px 13px;border-radius:8px;background:var(--surface2);border:1px solid transparent}
.urow.now{border-color:color-mix(in srgb,var(--accent) 50%,transparent);background:var(--accent-soft)}
.urow.bad.now{border-color:color-mix(in srgb,var(--crit) 50%,transparent);background:var(--crit-bg)}
.urow .ut{font-family:var(--ff-mono);font-size:13px;font-variant-numeric:tabular-nums;
  white-space:nowrap;color:var(--muted)}
.urow.now .ut{color:var(--ink)}
.urow .ut b{font-weight:500;color:var(--ink)}
.urow .us{font-size:12px;font-weight:500;white-space:nowrap}
.urow .us.ok{color:var(--good)} .urow .us.no{color:var(--crit)}
.urow .us.wait{color:var(--warn)} .urow .us.skip{color:var(--muted-soft)}

.empty{padding:34px 18px;text-align:center;color:var(--muted-soft);font-size:13.5px}
.two{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:16px;align-items:start}
.three{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;align-items:start}
.tabsm{display:none;gap:6px;overflow-x:auto;padding:10px 16px;border-bottom:1px solid var(--hairline);
  background:var(--surface)}
.tabsm button{white-space:nowrap;background:var(--surface2);border:1px solid var(--hairline);
  border-radius:9999px;padding:6px 14px;font-size:13px;cursor:pointer;color:var(--muted);
  font-weight:500}
.tabsm button[aria-current="true"]{background:var(--accent);border-color:var(--accent);color:var(--on-accent)}
.chartscroll{overflow-x:auto}
@media (max-width:1080px){
  .two,.three{grid-template-columns:1fr}
}
@media (max-width:900px){
  .chartscroll .chart{min-width:720px}
  .app{grid-template-columns:1fr}
  .rail{display:none}
  .tabsm{display:flex}
  .view{padding:20px 16px 64px}
  .vhead h2{font-size:31px}
  .topbar{padding:11px 16px}
  .f.wide{grid-column:span 1}
}

/* ---------- lock screen (autentikasi studio) ---------- */
.lock-screen{position:fixed;inset:0;z-index:99999;
  background:radial-gradient(circle at 50% 35%, #22201d 0%, #100f0e 100%);
  display:flex;align-items:center;justify-content:center;padding:20px;
  backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px)}
.lock-card{width:100%;max-width:360px;background:rgba(27,26,24,0.94);
  border:1px solid rgba(217,119,87,0.3);
  box-shadow:0 24px 48px rgba(0,0,0,0.7),0 0 32px rgba(217,119,87,0.12);
  border-radius:24px;padding:32px 24px;text-align:center;color:#faf9f5;
  animation:lockFadeIn .35s cubic-bezier(0.16,1,0.3,1)}
@keyframes lockFadeIn{from{opacity:0;transform:scale(0.95) translateY(10px)}to{opacity:1;transform:scale(1) translateY(0)}}
.lock-logo{margin-bottom:14px;display:inline-flex;filter:drop-shadow(0 2px 8px rgba(217,119,87,0.4))}
.lock-title{font-family:var(--ff-display,serif);font-size:29px;font-weight:700;letter-spacing:-.5px;color:#faf9f5;margin-bottom:3px}
.lock-subtitle{font-size:13px;color:#a09d96;margin-bottom:12px}
.lock-badge{display:inline-block;font-size:11px;font-weight:600;letter-spacing:.8px;text-transform:uppercase;
  padding:3px 12px;border-radius:9999px;background:rgba(217,119,87,0.15);color:#d97757;
  border:1px solid rgba(217,119,87,0.3);margin-bottom:22px}
.pin-display{display:flex;justify-content:center;gap:12px;margin-bottom:20px}
.pin-display .dot{width:14px;height:14px;border-radius:50%;border:2px solid rgba(160,157,150,0.4);
  background:transparent;transition:all .18s cubic-bezier(0.16,1,0.3,1)}
.pin-display .dot.filled{background:#d97757;border-color:#d97757;box-shadow:0 0 12px rgba(217,119,87,0.6);transform:scale(1.15)}
.pin-display.shake{animation:pinShake .45s cubic-bezier(0.36,0.07,0.19,0.97)}
@keyframes pinShake{10%,90%{transform:translate3d(-3px,0,0)}20%,80%{transform:translate3d(5px,0,0)}30%,50%,70%{transform:translate3d(-6px,0,0)}40%,60%{transform:translate3d(6px,0,0)}}
.pin-hidden-input{position:absolute;opacity:0;pointer-events:none}
.lock-error{color:#e07a68;font-size:12.5px;font-weight:500;margin-top:-8px;margin-bottom:14px;min-height:18px}
.keypad{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:18px}
.key-btn{background:rgba(37,35,32,0.85);border:1px solid rgba(255,255,255,0.08);border-radius:12px;
  padding:13px 0;font-size:19px;font-weight:600;color:#faf9f5;cursor:pointer;
  transition:all .12s ease;user-select:none;-webkit-user-select:none}
.key-btn:hover{background:rgba(52,50,45,0.95);border-color:rgba(217,119,87,0.35)}
.key-btn:active{transform:scale(0.92);background:#d97757;color:#fff}
.key-btn.action-btn{font-size:16px;color:#a09d96}
.key-btn.ok-btn{background:rgba(217,119,87,0.25);color:#d97757;border-color:rgba(217,119,87,0.4)}
.key-btn.ok-btn:active{background:#d97757;color:#fff}
.remember-wrap{display:inline-flex;align-items:center;gap:8px;font-size:12.5px;color:#a09d96;
  cursor:pointer;margin-bottom:14px;user-select:none}
.remember-wrap input{accent-color:#d97757;cursor:pointer}
.lock-footer{font-size:11.5px;color:#6c6a64}

/* ---------- toast notification ---------- */
.toast{position:fixed;bottom:24px;right:24px;z-index:9999;background:var(--rail);
  border:1px solid var(--rail-line);color:var(--on-rail);padding:12px 18px;border-radius:10px;
  font-size:13.5px;box-shadow:0 10px 25px rgba(0,0,0,0.3);display:flex;align-items:center;
  gap:10px;transform:translateY(80px);opacity:0;transition:all .25s cubic-bezier(0.16,1,0.3,1);
  pointer-events:none;max-width:420px}
.toast.show{transform:translateY(0);opacity:1;pointer-events:auto}
.toast.ok{border-color:var(--good);background:var(--rail)}
.toast.err{border-color:var(--crit);background:var(--rail)}

/* ---------- sync modal & components ---------- */
.btn-group{display:inline-flex;align-items:stretch}
.btn-group .btn:first-child{border-top-right-radius:0;border-bottom-right-radius:0}
.btn-group .btn:last-child{border-top-left-radius:0;border-bottom-left-radius:0;border-left:0}

.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.7);backdrop-filter:blur(6px);
  z-index:1000;display:flex;align-items:center;justify-content:center;padding:20px;
  opacity:0;pointer-events:none;transition:opacity .2s ease}
.modal-overlay.open{opacity:1;pointer-events:auto}
.modal-box{background:var(--surface);border:1px solid var(--hairline-strong);border-radius:16px;
  width:100%;max-width:480px;box-shadow:0 20px 40px rgba(0,0,0,0.4);overflow:hidden;
  transform:scale(0.96);transition:transform .2s cubic-bezier(0.16,1,0.3,1)}
.modal-overlay.open .modal-box{transform:scale(1)}
.modal-head{padding:18px 22px;border-bottom:1px solid var(--hairline);display:flex;align-items:center;
  justify-content:space-between}
.modal-head h3{font-family:var(--ff-display);font-size:22px;font-weight:600;margin:0;color:var(--ink)}
.modal-close{background:none;border:0;color:var(--muted);cursor:pointer;font-size:18px;padding:4px}
.modal-close:hover{color:var(--crit)}
.modal-body{padding:22px;display:flex;flex-direction:column;gap:16px}
.sync-option{background:var(--surface2);border:1px solid var(--hairline);border-radius:12px;
  padding:14px 16px;cursor:pointer;transition:all .15s;text-align:left;display:flex;flex-direction:column;gap:4px}
.sync-option:hover{border-color:var(--accent);background:var(--surface3)}
.sync-option b{color:var(--ink);font-size:14px;display:flex;align-items:center;gap:8px}
.sync-option span{font-size:12px;color:var(--muted);line-height:1.4}
.sync-status-box{background:var(--surface3);border:1px solid var(--hairline);border-radius:10px;
  padding:14px;font-size:12.5px;color:var(--ink2);display:flex;flex-direction:column;gap:6px}
.sync-spinner{width:16px;height:16px;border:2px solid var(--accent);border-top-color:transparent;border-radius:50%;animation:spin .6s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}

/* ---------- Section Tahunan (Annual Dashboard & 12 Month Tiles) ---------- */
.mgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;margin-bottom:24px}
.month-card{background:var(--surface);border:1px solid var(--hairline);border-radius:14px;
  padding:20px;display:flex;flex-direction:column;gap:13px;transition:all .18s cubic-bezier(0.16,1,0.3,1);
  position:relative;cursor:pointer}
.month-card:hover{border-color:var(--hairline-strong);transform:translateY(-3px);
  box-shadow:0 8px 24px rgba(0,0,0,0.12)}
.month-card.active-month{border:1.5px solid var(--accent);
  background:color-mix(in srgb,var(--accent) 4%,var(--surface));
  box-shadow:0 0 24px rgba(217,119,87,0.15)}
.month-card .mhead{display:flex;justify-content:space-between;align-items:flex-start;gap:8px}
.month-card .mname{font-family:var(--ff-display);font-size:22px;font-weight:700;letter-spacing:-.4px;
  color:var(--ink);display:flex;align-items:center;gap:7px}
.month-card .live-dot{width:8px;height:8px;border-radius:50%;background:var(--accent);display:inline-block;
  box-shadow:0 0 8px var(--accent);animation:pulseDot 1.6s infinite}
@keyframes pulseDot{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.4;transform:scale(1.25)}}
.month-card .mmomentum{font-size:11.5px;color:var(--muted);margin-top:2px;font-weight:500;line-height:1.35}
.month-card .mbody{display:flex;flex-direction:column;gap:11px;padding:11px 0;border-top:1px solid var(--hairline-soft);
  border-bottom:1px solid var(--hairline-soft)}
.month-card .mstat{display:flex;flex-direction:column;gap:2px}
.month-card .mk{font-family:var(--ff-body);font-size:10.5px;font-weight:500;letter-spacing:1.2px;
  text-transform:uppercase;color:var(--muted-soft)}
.month-card .mv{font-family:var(--ff-display);font-size:clamp(22px,2vw,28px);font-weight:700;
  letter-spacing:-.5px;color:var(--ink);line-height:1.15}
.month-card .mv.active{color:var(--accent)}
.month-card .msub{font-size:11.5px;color:var(--muted);font-family:var(--ff-mono);margin-top:2px}
.month-card .mseason{display:flex;flex-direction:column;gap:5px}
.month-card .mseason-label{font-size:11px;color:var(--muted);font-weight:500}
.month-card .mseason-bar{height:5px;background:var(--surface3);border-radius:3px;overflow:hidden}
.month-card .mseason-bar i{display:block;height:100%;border-radius:3px}
.month-card .myoy{display:flex;justify-content:space-between;align-items:center;font-size:12px}
.month-card .myoy-label{color:var(--muted)}
.month-card .myoy-val{font-family:var(--ff-mono);font-weight:600}
.month-card .mfoot{margin-top:auto}
tr.active-row td{background:color-mix(in srgb,var(--accent) 5%,var(--surface));font-weight:500}
</style>
</head>
<body>

<div id="lockScreen" class="lock-screen">
  <div class="lock-card">
    <div class="lock-logo">
      <svg width="42" height="42" viewBox="0 0 22 22" aria-hidden="true">
        <circle cx="11" cy="11" r="9.25" fill="none" stroke="#d97757" stroke-width="1.4"/>
        <path d="M11 1.75 L11 11 L19.01 15.62" fill="none" stroke="#d97757" stroke-width="1.4" stroke-linecap="round"/>
        <path d="M19.01 6.38 L11 11 L2.99 15.62" fill="none" stroke="#d97757" stroke-width="1.4" stroke-linecap="round"/>
        <path d="M2.99 6.38 L11 11 L11 20.25" fill="none" stroke="#d97757" stroke-width="1.4" stroke-linecap="round"/>
        <circle cx="11" cy="11" r="2.1" fill="#d97757"/>
      </svg>
    </div>
    <h2 class="lock-title">Foxe Studio</h2>
    <p class="lock-subtitle">Portal Keuangan &amp; Operasional</p>
    <div class="lock-badge">🔒 Akses Terbatas</div>
    
    <div class="pin-display" id="pinDots">
      <span class="dot"></span>
      <span class="dot"></span>
      <span class="dot"></span>
      <span class="dot"></span>
      <span class="dot"></span>
      <span class="dot"></span>
    </div>

    <input type="password" id="pinInput" maxlength="6" inputmode="numeric" pattern="[0-9]*" autocomplete="one-time-code" class="pin-hidden-input" autofocus>

    <div class="lock-error" id="lockError" hidden>PIN Salah. Silakan coba lagi.</div>

    <div class="keypad" id="pinKeypad">
      <button class="key-btn" type="button" data-val="1">1</button>
      <button class="key-btn" type="button" data-val="2">2</button>
      <button class="key-btn" type="button" data-val="3">3</button>
      <button class="key-btn" type="button" data-val="4">4</button>
      <button class="key-btn" type="button" data-val="5">5</button>
      <button class="key-btn" type="button" data-val="6">6</button>
      <button class="key-btn" type="button" data-val="7">7</button>
      <button class="key-btn" type="button" data-val="8">8</button>
      <button class="key-btn" type="button" data-val="9">9</button>
      <button class="key-btn action-btn" type="button" id="keyClear">⌫</button>
      <button class="key-btn" type="button" data-val="0">0</button>
      <button class="key-btn action-btn ok-btn" type="button" id="keySubmit">➔</button>
    </div>

    <label class="remember-wrap">
      <input type="checkbox" id="chkRemember" checked>
      <span>Ingat perangkat ini (30 hari)</span>
    </label>

    <p class="lock-footer">Akses internal khusus Owner &amp; Manajemen Foxe Studio</p>
  </div>
</div>

<div class="app">
  <aside class="rail">
    <div class="brand">
      <svg width="24" height="24" viewBox="0 0 22 22" aria-hidden="true">
        <circle cx="11" cy="11" r="9.25" fill="none" stroke="#d97757" stroke-width="1.4"/>
        <path d="M11 1.75 L11 11 L19.01 15.62" fill="none" stroke="#d97757" stroke-width="1.4" stroke-linecap="round"/>
        <path d="M19.01 6.38 L11 11 L2.99 15.62" fill="none" stroke="#d97757" stroke-width="1.4" stroke-linecap="round"/>
        <path d="M2.99 6.38 L11 11 L11 20.25" fill="none" stroke="#d97757" stroke-width="1.4" stroke-linecap="round"/>
        <circle cx="11" cy="11" r="2.1" fill="#d97757"/>
      </svg>
      <span>
        <span class="mark">Foxe Studio</span>
        <span class="sub">Laporan Keuangan</span>
      </span>
    </div>
    <nav class="nav" id="nav"></nav>
  </aside>

  <div class="main">
    <div class="topbar">
      <div class="period"><b id="tbPeriod">September 2026</b><span class="co" id="tbCut">memuat…</span></div>
      <span class="pill prog" id="tbStatus">Progressive</span>
      <span class="spacer"></span>
      <button class="btn sm" id="btnTheme" title="Ganti Tema">🌓 Tema</button>
      <button class="btn sm" id="btnLock" title="Kunci Dashboard">🔒 Kunci</button>
      <span class="pill neutral" id="tbLive" hidden></span>
      <span class="pill neutral" id="tbUpd" hidden></span>
      <span class="pill final" id="tbSync">aktif</span>
      <div class="btn-group" id="btnGroupUpdate">
        <button class="btn sm" id="btnUpdateData" style="display:inline-flex;align-items:center;gap:5px;font-weight:600;border-color:var(--accent);color:var(--accent);background:var(--surface);" title="Perbarui data terbaru ke website">🔄 Update</button>
        <button class="btn sm" id="btnSyncSettings" style="padding:4px 7px;border-left:0;border-color:var(--accent);color:var(--accent);background:var(--surface);" title="Pilihan &amp; Pengaturan Sinkronisasi">▾</button>
      </div>
      <button class="btn sm" id="btnReset" title="Kembalikan ke data awal file">Reset Data</button>
      <button class="btn pri" id="btnExport">Export Excel</button>
    </div>
    <div class="tabsm" id="tabsm"></div>
    <main id="views"></main>
  </div>
</div>
<div class="tip" id="tip"></div>

<div class="toast" id="toast"></div>

<!-- Modal Sinkronisasi Data -->
<div class="modal-overlay" id="syncModal">
  <div class="modal-box">
    <div class="modal-head">
      <h3>🔄 Perbarui Data Website</h3>
      <button class="modal-close" id="btnCloseSyncModal" title="Tutup">✕</button>
    </div>
    <div class="modal-body">
      <div style="font-size:12.5px;color:var(--muted);display:flex;justify-content:space-between;padding:0 2px;">
        <span id="modalCutoff">Cut-off: memuat…</span>
        <span id="modalLastSync">Terakhir: memuat…</span>
      </div>

      <div class="sync-actions" id="syncActions" style="display:flex;flex-direction:column;gap:10px;">
        <button class="sync-option" id="btnOptFast">
          <b>⚡ Refresh Cepat (Instan)</b>
          <span>Tarik pembaruan data yang sudah tersimpan di cloud ke layar ini (&lt; 1 detik, tanpa delay).</span>
        </button>

        <button class="sync-option" id="btnOptDrive" style="border-color:var(--accent);background:color-mix(in srgb,var(--accent) 8%,transparent);">
          <b style="color:var(--accent);">🌐 Tarik Data Baru dari Google Drive (Full Sync)</b>
          <span>Jalankan sinkronisasi File 1 Log Order, File 2 Schedule, dan File Neraca dari Google Drive via cloud (~20-25 detik).</span>
        </button>
      </div>

      <!-- Kotak Progress saat sync berjalan -->
      <div class="sync-status-box" id="syncStatusBox" hidden>
        <div style="display:flex;align-items:center;gap:10px;">
          <div class="sync-spinner"></div>
          <b id="syncStatusTitle">Menjalankan sinkronisasi cloud...</b>
        </div>
        <p id="syncStatusDesc" style="font-size:12px;color:var(--muted);margin:4px 0 0 0;">Menghubungkan ke GitHub Actions &amp; Google Drive...</p>
      </div>

      <!-- Bagian Pengaturan Token (Aman di LocalStorage) -->
      <div class="sync-token-sec" style="margin-top:6px;border-top:1px solid var(--hairline);padding-top:14px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
          <span style="font-size:11.5px;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:var(--muted-soft);">Otorisasi Google Drive Sync</span>
          <span id="tokenStatusBadge" class="pill neutral" style="font-size:10px;padding:1px 6px;">Belum Terhubung</span>
        </div>

        <div id="tokenInputSec">
          <p style="font-size:11.5px;color:var(--muted);line-height:1.45;margin-bottom:8px;">
            Token GitHub disimpan <b>hanya di browser HP/Laptop Anda</b> (localStorage) dan aman dari publik. Cukup masukkan sekali.
          </p>
          <div style="display:flex;gap:8px;">
            <input type="password" id="txtGithubToken" placeholder="ghp_xxxxxxxxxxxxxxxxxxxx" style="flex:1;background:var(--canvas);border:1px solid var(--hairline-strong);border-radius:8px;padding:6px 10px;font-size:12px;color:var(--ink);" autocomplete="off">
            <button class="btn sm pri" id="btnSaveToken">Simpan</button>
          </div>
        </div>

        <div id="tokenSavedSec" hidden style="display:flex;align-items:center;justify-content:space-between;background:var(--surface2);padding:8px 12px;border-radius:8px;border:1px solid var(--hairline);">
          <div style="font-size:12px;color:var(--ink2);">
            <span style="color:var(--good);margin-right:4px;">●</span> Token aktif tersimpan di perangkat ini
          </div>
          <button class="btn sm" id="btnRemoveToken" style="font-size:11px;padding:2px 8px;color:var(--crit);" title="Hapus token dari browser">Hapus</button>
        </div>

        <label style="display:flex;align-items:center;gap:8px;font-size:12px;color:var(--muted);margin-top:12px;cursor:pointer;">
          <input type="checkbox" id="chkAutoFullSync" style="accent-color:var(--accent);">
          <span>Otomatis Full Sync Google Drive setiap tombol 🔄 Update diklik</span>
        </label>
      </div>
    </div>
  </div>
</div>

<script>
"use strict";
/* ============================ konstanta & util ============================ */
const HARI=["Minggu","Senin","Selasa","Rabu","Kamis","Jumat","Sabtu"];
const BULAN=["Januari","Februari","Maret","April","Mei","Juni","Juli","Agustus","September","Oktober","November","Desember"];
const KAT_COGS=["Cetak Foto & Photo Paper","Tinta / Consumable Printing","Frame / Album / Packaging","Properti / Consumable Sesi","Outsource / Freelancer Produksi","Transport Produksi Langsung","Fee Payment / MDR","COGS Lainnya"];
const KAT_OPEX=["Gaji Admin","Gaji Fotografer","Gaji Editor","Overtime / Insentif","Sewa Studio","Listrik & Air","Internet & Telekomunikasi","Software / Subscription","Maintenance Studio & Equipment","Marketing / Ads / KOL","Office & Cleaning Supplies","Konsumsi Crew","Transport Operasional","Bank / Admin Fee","Pajak & Perizinan","OPEX Lainnya"];
const KAT_LAIN=["Pendapatan Lainnya","Biaya Lainnya"];
const KAT_NONPL=["Asset / CAPEX","Prive / Owner Draw","Pembayaran Hutang"];

const rp=n=>(n==null||isNaN(n))?"—":"Rp "+Math.round(n).toLocaleString("en-US");
const rpc=n=>(n==null||isNaN(n))?"—":"Rp "+Math.round(n).toLocaleString("en-US");
const num=n=>(n==null||isNaN(n))?"—":Math.round(n).toLocaleString("en-US");
const pct=n=>(n==null||isNaN(n)||!isFinite(n))?"—":(n*100).toFixed(1)+"%";
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\\"":"&quot;","'":"&#39;"}[c]));
const uid=()=>Date.now().toString(36)+Math.random().toString(36).slice(2,7);
const dnum=v=>{const n=parseFloat(String(v??"").replace(/[^0-9.-]/g,""));return isNaN(n)?0:n};
const iso=d=>d.toISOString().slice(0,10);
const npak=p=>{const s=String(p??"").trim();return s.toLowerCase()==="photo fox"?"Photofox":s};

/* ============================ DATA AWAL DARI FILE 1, 2, 3 ============================ */
const INITIAL_STATE = """ + state_json_str + """;

/* Load from LocalStorage if version matches, otherwise refresh with INITIAL_STATE */
let S = (() => {
  try {
    const syncId = (INITIAL_STATE.sync && INITIAL_STATE.sync[0] && INITIAL_STATE.sync[0].id) || "sync_init";
    const savedSync = localStorage.getItem("foxe_studio_keuangan_sync_id");
    const saved = localStorage.getItem("foxe_studio_keuangan_state");
    if (saved && savedSync === syncId) {
      const parsed = JSON.parse(saved);
      if (parsed && parsed.orders && parsed.orders.length > 0 && parsed.config && parsed.config.cutoff === INITIAL_STATE.config.cutoff && (parsed.expenses || []).length === (INITIAL_STATE.expenses || []).length && (parsed.neracaDetail || []).length === (INITIAL_STATE.neracaDetail || []).length) {
        return parsed;
      }

    }
  } catch (e) {
    console.warn("Gagal load localStorage, menggunakan initial state:", e);
  }
  try {
    const syncId = (INITIAL_STATE.sync && INITIAL_STATE.sync[0] && INITIAL_STATE.sync[0].id) || "sync_init";
    localStorage.setItem("foxe_studio_keuangan_sync_id", syncId);
    localStorage.setItem("foxe_studio_keuangan_state", JSON.stringify(INITIAL_STATE));
  } catch(e){}
  return JSON.parse(JSON.stringify(INITIAL_STATE));
})();

function saveLocal() {
  try {
    localStorage.setItem("foxe_studio_keuangan_state", JSON.stringify(S));
  } catch (e) {
    console.error("Gagal simpan ke localStorage:", e);
  }
}

let db=null,downloads=null,room=null,view="tahunan";

function nkey(s){
  return String(s||"").normalize("NFKD").replace(/[̀-ͯ]/g,"")
    .toLowerCase().replace(/[^a-z0-9]/g,"");
}

/* ============================ perhitungan inti ============================ */
function compute(){
  const c=S.config, [y,m]=c.bulan.split("-").map(Number);
  const dim=new Date(y,m,0).getDate();
  const cut=new Date(c.cutoff+"T00:00:00");
  const cutDay=cut.getDate();
  const hariBerjalan=c.status==="Final"?dim:cutDay;
  const inRange=d=>d && d<=c.cutoff && d>=`${c.bulan}-01`;

  const ord=S.orders.filter(o=>inRange(o.tanggal));
  const omzet=ord.reduce((s,o)=>s+dnum(o.total),0);
  const cash=ord.reduce((s,o)=>s+dnum(o.cash),0);
  const transfer=ord.reduce((s,o)=>s+dnum(o.transfer),0);
  const paid=ord.filter(o=>dnum(o.total)>0);
  const rp0=ord.length-paid.length;

  const pkMap=new Map();
  paid.forEach(o=>{
    const k=nkey(o.client)+"|"+(o.tanggalFoto||"");
    if(!pkMap.has(k)) pkMap.set(k,{key:k,client:o.client,tglFoto:o.tanggalFoto||"",
      paket:o.paket,bayar:[],nilai:0});
    const p=pkMap.get(k); p.bayar.push(o); p.nilai+=dnum(o.total);
  });
  const pkAll=[...pkMap.values()];
  pkAll.forEach(p=>{p.bayar.sort((a,b)=>String(a.tanggal).localeCompare(String(b.tanggal)));
    p.pecah=p.bayar.length>1;});
  const inBulan=d=>d&&d>=`${c.bulan}-01`&&d<=`${c.bulan}-${String(dim).padStart(2,"0")}`;
  const pkLewat=pkAll.filter(p=>inBulan(p.tglFoto)&&p.tglFoto<=c.cutoff);
  const pkDepan=pkAll.filter(p=>inBulan(p.tglFoto)&&p.tglFoto>c.cutoff);
  const pkTanpa=pkAll.filter(p=>!p.tglFoto);
  const pkLuar =pkAll.filter(p=>p.tglFoto&&!inBulan(p.tglFoto));
  const sumP=a=>a.reduce((s,p)=>s+p.nilai,0);
  const nilaiLewat=sumP(pkLewat), nilaiDepan=sumP(pkDepan);
  const avgPaket=pkLewat.length?nilaiLewat/pkLewat.length:0;
  const paketTerlayani=pkLewat.length;
  const paketPecah=pkLewat.filter(p=>p.pecah).length;
  
  const peranBayar=new Map();
  pkAll.forEach(p=>p.bayar.forEach((o,i)=>
    peranBayar.set(o,p.bayar.length===1?"lunas":(i===0?"dp":"pelunasan"))));
  const peran=o=>peranBayar.get(o)||"lunas";

  // harian
  const days=[];
  for(let d=1;d<=dim;d++){
    const ds=`${c.bulan}-${String(d).padStart(2,"0")}`;
    const berjalan=d<=hariBerjalan;
    const oo=ord.filter(o=>o.tanggal===ds);
    const op=oo.filter(o=>dnum(o.total)>0);
    const om=oo.reduce((s,o)=>s+dnum(o.total),0);
    days.push({d,ds,hari:HARI[new Date(ds+"T00:00:00").getDay()],berjalan,
      tx:berjalan?oo.length:null, txPaid:berjalan?op.length:null,
      cash:berjalan?oo.reduce((s,o)=>s+dnum(o.cash),0):null,
      transfer:berjalan?oo.reduce((s,o)=>s+dnum(o.transfer),0):null,
      omzet:berjalan?om:null, avg:berjalan?(op.length?om/op.length:0):null,
      nLunas:berjalan?op.filter(o=>peran(o)==="lunas").length:null,
      nDP:berjalan?op.filter(o=>peran(o)==="dp").length:null,
      nPelunasan:berjalan?op.filter(o=>peran(o)==="pelunasan").length:null,
      nilaiDP:berjalan?op.filter(o=>peran(o)==="dp").reduce((s,o)=>s+dnum(o.total),0):null});
  }
  
  const sesi=[];
  for(let d=1;d<=dim;d++){
    const ds=`${c.bulan}-${String(d).padStart(2,"0")}`;
    const g=pkAll.filter(p=>p.tglFoto===ds);
    if(!g.length) continue;
    const nilai=sumP(g);
    sesi.push({d,ds,hari:HARI[new Date(ds+"T00:00:00").getDay()],lewat:ds<=c.cutoff,
      paket:g.length,nilai,avg:nilai/g.length,pecah:g.filter(p=>p.pecah).length});
  }
  let cum=0;
  days.forEach((r,i)=>{ if(r.berjalan){const prev=cum;cum+=r.omzet;r.cum=cum;r.growth=i===0?null:(prev?(r.omzet-days[i-1].omzet)/(days[i-1].omzet||1):null);}
    else {r.cum=null;r.growth=null;} });

  const runRate=hariBerjalan?omzet/hariBerjalan:0;
  const proyeksi=runRate*dim;

  // paket
  const pm=new Map();
  ord.forEach(o=>{const p=npak(o.paket); if(!p)return;
    const e=pm.get(p)||{paket:p,tx:0,nilai:0}; e.tx++; e.nilai+=dnum(o.total); pm.set(p,e);});
  const paket=[...pm.values()].sort((a,b)=>b.tx-a.tx||b.nilai-a.nilai);

  // crew
  const agg=key=>{const M=new Map();let kosong=0;
    ord.forEach(o=>{const v=String(o[key]||"").trim().toUpperCase();
      if(!v){kosong++;return}
      const e=M.get(v)||{nama:v,n:0,nilai:0}; e.n++; e.nilai+=dnum(o.total); M.set(v,e);});
    const arr=[...M.values()].sort((a,b)=>b.n-a.n);
    const tot=arr.reduce((s,x)=>s+x.n,0);
    arr.forEach(x=>x.porsi=tot?x.n/tot:0);
    return {arr,kosong,tot}};
  const admin=agg("admin"), fotografer=agg("fotografer");

  // shift
  const sh=S.shifts.filter(s=>inRange(s.tanggal));
  const sm=new Map();
  sh.forEach(s=>{const n=String(s.nama||"").toUpperCase(); if(!n)return;
    sm.set(n,(sm.get(n)||0)+Math.max(0,dnum(s.slot)));});
  const shiftTot=[...sm.values()].reduce((a,b)=>a+b,0);
  const shift=[...sm.entries()].map(([nama,total])=>({nama,total,porsi:shiftTot?total/shiftTot:0}))
    .sort((a,b)=>b.total-a.total);
  const roster=new Set(shift.filter(s=>s.total>0).map(s=>s.nama));
  const offRoster={admin:admin.arr.filter(a=>!roster.has(a.nama)),fotografer:fotografer.arr.filter(f=>!roster.has(f.nama))};

  // biaya
  const ex=S.expenses.filter(e=>e.tanggal?inRange(e.tanggal):e.bulan===c.bulan);
  const sumJ=j=>ex.filter(e=>e.jenis===j).reduce((s,e)=>s+dnum(e.nilai),0);

  const bonDoc=S.bon.filter(b=>b.bulan===c.bulan)
    .sort((a,b)=>String(b.dibaca||"").localeCompare(String(a.dibaca||"")))[0]||null;
  const bonT=(bonDoc&&bonDoc.total)||{};
  const kasbon=dnum(bonT.kasbon), bonAizio=dnum(bonT.aizio), bonLain=dnum(bonT.lain);
  const bonOwner=dnum(bonT.owner);
  const bonOrang=(bonDoc&&bonDoc.perOrang)||{};
  const bonNeracaTakBerkategori=ex.filter(e=>!e.kategori&&/^bon$/i.test((e.deskripsi||"").trim()))
    .reduce((s,e)=>s+dnum(e.nilai),0);
  const cogs=sumJ("COGS"), opexNeraca=sumJ("OPEX");
  const pendLain=ex.filter(e=>e.kategori==="Pendapatan Lainnya").reduce((s,e)=>s+dnum(e.nilai),0);
  const biayaLain=ex.filter(e=>e.kategori==="Biaya Lainnya").reduce((s,e)=>s+dnum(e.nilai),0);
  const nonPL=sumJ("NON-P&L");
  const belumKategori=ex.filter(e=>!e.jenis||!e.kategori).length;
  const opex=opexNeraca+kasbon;

  const gajiNeraca=ex.filter(e=>/^gaji/i.test(e.kategori||"")).reduce((s,e)=>s+dnum(e.nilai),0);
  const prAll=[...S.payroll].sort((a,b)=>String(b.bulan||"").localeCompare(String(a.bulan||"")));
  const acuan=prAll.find(p=>p.terisi&&p.bulan!==c.bulan)||prAll.find(p=>p.terisi)||null;
  const TETAP=/manager|editor|marketing|tetap/i;
  const shiftOf=n=>{const f=shift.find(x=>x.nama===String(n).toUpperCase());return f?f.total:0};
  let gRoster=[];
  if(acuan){
    gRoster=(acuan.rows||[]).filter(r=>dnum(r.cost)>0).map(r=>{
      const tetap=TETAP.test(r.job||"")||!r.job;
      const q=tetap?(dnum(r.cost)>0?1:0):shiftOf(r.nama);
      return {nama:r.nama,job:r.job||"—",tetap,cost:dnum(r.cost),q,total:q*dnum(r.cost),
        adaShift:!tetap&&q>0};
    });
  }
  const dikenal=new Set(gRoster.map(r=>String(r.nama).toUpperCase()));
  const luarKartu=shift.filter(x=>x.total>0&&!dikenal.has(x.nama));
  const gajiShiftJalan=gRoster.filter(r=>!r.tetap).reduce((s,r)=>s+r.total,0);
  const gajiTetapJalan=gRoster.filter(r=>r.tetap).reduce((s,r)=>s+r.total,0);
  const gajiBlok=gRoster.length?gajiShiftJalan+gajiTetapJalan:null;
  const gajiSelisih=gajiBlok==null?null:gajiBlok-gajiNeraca;
  const grossProfit=omzet-cogs, operatingProfit=grossProfit-opex;
  const nettProfit=operatingProfit+pendLain-biayaLain;
  const cashOut=cogs+opex+biayaLain;
  const adaBiaya=(cogs+opex+pendLain+biayaLain)>0;

  // rekonsiliasi kas
  const rekon=days.filter(d=>d.berjalan).map(d=>{
    const ctrl=S.cashControl.filter(x=>x.tanggal===d.ds).reduce((s,x)=>s+dnum(x.nilai),0);
    const has=S.cashControl.some(x=>x.tanggal===d.ds);
    return {ds:d.ds,d:d.d,cash:d.cash,ctrl:has?ctrl:null,selisih:has?d.cash-ctrl:null};});
  const rekonBeda=rekon.filter(r=>r.selisih!==null&&r.selisih!==0);
  const rekonAda=rekon.filter(r=>r.ctrl!==null).length;

  // target & bonus
  const tiers=[...c.targets].sort((a,b)=>a.omzet-b.omzet).map(t=>({...t,pool:t.omzet*t.persen}));
  let tierAktif=null; tiers.forEach(t=>{if(omzet>=t.omzet)tierAktif=t});
  const tierBerikut=tiers.find(t=>omzet<t.omzet)||null;
  const pool=tierAktif?tierAktif.pool:0;

  // KPI
  const posisi=S.kpi.length?S.kpi:[];
  const bobot=posisi.length?1/posisi.length:0;
  const kpi=posisi.map(k=>{
    const dinilai=[k.akurasi,k.sop,k.client,k.produktivitas].every(v=>v!==null&&v!==undefined&&v!=="")&&(k.disiplin!==null&&k.disiplin!=="");
    if(!dinilai) return {...k,dinilai:false,basic:null,inJob:null,operasional:null,opPersen:null,totalKPI:null,bonusMax:pool*bobot,bonusCair:0,bobot};
    const basic=dnum(k.disiplin);
    const inJob=((dnum(k.akurasi)+dnum(k.sop)+dnum(k.client)+dnum(k.produktivitas))/4)*3;
    const operasional=basic+inJob;
    const referral=dnum(k.referral);
    const totalKPI=operasional+referral;
    const bonusMax=pool*bobot;
    return {...k,dinilai:true,basic,inJob,operasional,opPersen:operasional/20,referral,totalKPI,
      totalPersen:totalKPI/100,bonusMax,bonusCair:bonusMax*(totalKPI/100),bobot};});
  const kpiDinilai=kpi.filter(k=>k.dinilai);
  const avgOp=kpiDinilai.length?kpiDinilai.reduce((s,k)=>s+k.opPersen,0)/kpiDinilai.length:null;
  const bonusCair=kpi.reduce((s,k)=>s+(k.bonusCair||0),0);

  // lead
  const ld=S.leads.filter(l=>inRange(l.tanggal)).sort((a,b)=>a.tanggal<b.tanggal?-1:1);
  const lTot=k=>ld.reduce((s,l)=>s+dnum(l[k]),0);
  const totLeads=lTot("leads"), totDP=lTot("dp"), totSesi=lTot("sesiFoto"), totTx=lTot("transaksi");
  const leadKosong=ld.filter(l=>(!l.leads||dnum(l.leads)===0)&&dnum(l.dp)>0);
  const leadTerakhir=[...ld].reverse().find(l=>dnum(l.leads)>0);
  const conv=totLeads?totDP/totLeads:null;

  return {c,dim,cutDay,hariBerjalan,omzet,cash,transfer,tx:ord.length,txPaid:paid.length,rp0,
    avgTx:paid.length?omzet/paid.length:0,days,runRate,proyeksi,paket,admin,fotografer,
    pkAll,pkLewat,pkDepan,pkTanpa,pkLuar,nilaiLewat,nilaiDepan,avgPaket,paketTerlayani,
    paketPecah,sesi,peran,
    shift,shiftTot,shiftDetail:sh,roster,offRoster,
    ex,cogs,opex,pendLain,biayaLain,nonPL,belumKategori,
    bonDoc,kasbon,bonAizio,bonLain,bonOwner,bonOrang,bonNeracaTakBerkategori,opexNeraca,
    gajiAcuan:acuan,gajiRoster:gRoster,gajiLuarKartu:luarKartu,gajiShiftJalan,gajiTetapJalan,
    gajiNeraca,gajiBlok,gajiSelisih,grossProfit,operatingProfit,nettProfit,cashOut,adaBiaya,
    nettMargin:omzet?nettProfit/omzet:null,
    rekon,rekonBeda,rekonAda,tiers,tierAktif,tierBerikut,pool,kpi,kpiDinilai,avgOp,bonusCair,
    ld,totLeads,totDP,totSesi,totTx,conv,leadKosong,leadTerakhir,baseline:S.baseline,
    neracaDetail:S.neracaDetail||[],neracaSummary:S.neracaSummary||{}};
}


/* ============================ final screening ============================ */
function screening(R){
  const out=[];
  const add=(st,t,d)=>out.push({st,t,d});
  add("ok","Angka omzet tunggal",`Semua bagian membaca satu nilai: ${rp(R.omzet)}. Tidak ada perhitungan omzet terpisah per bagian.`);
  add("ok","Cut-off tunggal",`Seluruh halaman memakai ${new Date(R.c.cutoff+"T00:00:00").getDate()} ${BULAN[+R.c.bulan.split("-")[1]-1]} — ${R.hariBerjalan} hari berjalan.`);
  add(R.cash+R.transfer===R.omzet?"ok":"bad","Cash + Transfer = Omzet",
    `${rp(R.cash)} + ${rp(R.transfer)} = ${rp(R.cash+R.transfer)}${R.cash+R.transfer===R.omzet?"":" — tidak sama dengan omzet "+rp(R.omzet)}`);
  const futureIsi=R.days.some(d=>!d.berjalan&&(d.tx!==null||d.omzet!==null));
  add(futureIsi?"bad":"ok","Tanggal belum berjalan kosong",
    futureIsi?"Ada tanggal future yang terisi angka.":`${R.dim-R.hariBerjalan} tanggal setelah cut-off tampil tanpa angka, termasuk kolom jumlah transaksi.`);
  const proyOk=R.hariBerjalan>=R.dim||Math.abs(R.proyeksi-R.omzet)>1;
  add(proyOk?"ok":"bad","Proyeksi ≠ omzet progresif",
    `Run-rate ${rp(R.runRate)}/hari × ${R.dim} hari = ${rp(R.proyeksi)}.`);
  add(R.rekonBeda.length?"bad":(R.rekonAda?"ok":"warn"),"Rekonsiliasi kas harian",
    R.rekonBeda.length?`${R.rekonBeda.length} hari selisih antara kolom Cash dan baris kontrol.`
    :(R.rekonAda?`${R.rekonAda} hari cocok persis dengan baris kontrol kas.`:"Belum ada baris kontrol kas untuk dicocokkan."));
  add(R.belumKategori?"warn":(R.adaBiaya?"ok":"warn"),"Klasifikasi biaya",
    R.belumKategori?`${R.belumKategori} biaya belum punya jenis/kategori — belum masuk COGS atau OPEX.`
    :(R.adaBiaya?`${R.ex.length} biaya sudah terklasifikasi.`:"Belum ada biaya tercatat. P&L berhenti di Gross Profit."));
  const off=R.offRoster.admin.length+R.offRoster.fotografer.length;
  add(off?"warn":"ok","Roster shift vs order",
    off?`${off} nama menangani order tapi tidak ada di slot shift — tetap dihitung, ditandai.`:"Semua nama di order ada di slot shift.");
  add(R.leadKosong.length?"warn":(R.ld.length?"ok":"warn"),"Kelengkapan lead",
    R.leadKosong.length?`${R.leadKosong.length} hari punya DP tapi Leads kosong — conversion provisional.`
    :(R.ld.length?`Lead terisi ${R.ld.length} dari ${R.hariBerjalan} hari berjalan.`:"Belum ada input lead."));
  const belumKPI=R.kpi.filter(k=>!k.dinilai).length;
  add(belumKPI?"warn":(R.kpi.length?"ok":"warn"),"Kelengkapan KPI",
    R.kpi.length?(belumKPI?`${belumKPI} dari ${R.kpi.length} posisi belum dinilai.`:`${R.kpi.length} posisi sudah dinilai.`):"Belum ada posisi KPI.");
  add(R.baseline?"ok":"warn","Baseline YoY",
    R.baseline?`Baseline ${R.baseline.label} tersedia.`:"Baseline tahun lalu belum ada — YoY berstatus PENDING, tidak diisi bulan lain.");
  add(!R.bonDoc?"warn":R.bonNeracaTakBerkategori?"warn":"ok","Kasbon karyawan",
    !R.bonDoc?"Blok Bon bulan ini belum terbaca."
    :R.bonNeracaTakBerkategori?`Kasbon ${rp(R.kasbon)} dihitung dari blok Bon. Ada baris "Bon" ${rp(R.bonNeracaTakBerkategori)} di neraca yang sengaja dibiarkan tanpa kategori supaya tidak terhitung dua kali.`
    :`Kasbon ${rp(R.kasbon)} masuk OPEX. Di luar itu ${rp(R.bonAizio)} lewat Aiz untuk usaha lain dan ${rp(R.bonOwner)} tarikan pemilik — keduanya tidak dihitung sebagai biaya.`);
  add(!R.gajiRoster.length?"warn":R.gajiLuarKartu.length?"warn":"ok","Gaji berjalan",
    !R.gajiRoster.length?"Kartu tarif belum ada — perlu satu bulan lengkap di blok Gaji Karyawan."
    :R.gajiLuarKartu.length?`${R.gajiLuarKartu.length} nama punya shift di Log Order tapi tidak ada di kartu tarif: ${R.gajiLuarKartu.map(x=>x.nama).join(", ")}.`
    :`${R.gajiRoster.filter(r=>!r.tetap).length} orang shift + ${R.gajiRoster.filter(r=>r.tetap).length} gaji tetap, akrual ${rp(R.gajiBlok)}.`);
  const sy=syncUrut()[0], syOk=syncSukses();
  const syBuruk=sy&&(sy.status==="gagal"||sy.status==="berjalan");
  add(!sy?"warn":syBuruk?"bad":"ok","Kesegaran data",
    !sy?"Belum ada catatan pembaruan."
    :syBuruk?`Percobaan ${tgljam(sy.mulai)} tidak tuntas. Angka yang tampil berasal dari pembaruan berhasil terakhir, ${tgljam(syOk&&syOk.mulai)}.`
    :sy.status==="dilewati"?`Sinkron ${tgljam(sy.mulai)} dilewati karena ketiga file sumber tidak berubah sejak ${tgljam(syOk&&syOk.mulai)}. Data sudah yang terbaru.`
    :`Data masuk terakhir ${tgljam(sy.mulai)} — ${lalu(sy.mulai)}.`);
  add(R.rp0?"warn":"ok","Transaksi Rp0",
    R.rp0?`${R.rp0} order tercatat tanpa uang masuk — ikut jumlah transaksi, tidak menambah omzet.`:"Tidak ada order Rp0.");
  return out;
}

/* ============================ chart helpers ============================ */
const TIP=document.getElementById("tip");
function tipShow(e,html){TIP.innerHTML=html;TIP.style.opacity="1";
  const r=TIP.getBoundingClientRect();
  let x=e.clientX+14,y=e.clientY-10;
  if(x+r.width>innerWidth-8)x=e.clientX-r.width-14;
  if(y+r.height>innerHeight-8)y=innerHeight-r.height-8;
  TIP.style.left=x+"px";TIP.style.top=Math.max(8,y)+"px";}
function tipHide(){TIP.style.opacity="0"}
function niceMax(v){if(v<=0)return 1;const p=Math.pow(10,Math.floor(Math.log10(v)));const n=v/p;
  return (n<=1?1:n<=2?2:n<=2.5?2.5:n<=5?5:10)*p;}

function chartGabung(R){
  const rows=R.days.filter(d=>d.berjalan);
  if(!rows.length)return `<div class="empty">Belum ada hari berjalan.</div>`;
  const W=1100,H=250,PL=58,PR=62,PT=26,PB=30;
  const maxD=niceMax(Math.max(...rows.map(r=>r.omzet)));
  const t1=R.tiers[0]?R.tiers[0].omzet:0;
  const maxC=niceMax(Math.max(t1||0,rows[rows.length-1].cum*1.25));
  const iw=W-PL-PR, ih=H-PT-PB;
  const step=iw/R.dim, bw=Math.min(26,step*.56);
  const xx=d=>PL+step*(d-1)+step/2;
  const yC=v=>PT+ih-(v/maxC)*ih;
  const jt=v=>v>=1e6?(v/1e6).toFixed(v%1e6?1:0)+"jt":num(v);
  let g="";
  for(let i=0;i<=4;i++){const y=PT+ih-ih*i/4;
    g+=`<line x1="${PL}" y1="${y.toFixed(1)}" x2="${W-PR}" y2="${y.toFixed(1)}" stroke="var(--grid)" stroke-width="1"/>`
     +`<text x="${PL-8}" y="${(y+3.5).toFixed(1)}" text-anchor="end" font-size="9.5" font-family="JetBrains Mono,monospace" fill="var(--muted)">${jt(maxD*i/4)}</text>`
     +`<text x="${W-PR+8}" y="${(y+3.5).toFixed(1)}" font-size="9.5" font-family="JetBrains Mono,monospace" fill="var(--accent-ink)">${jt(maxC*i/4)}</text>`;}
  let bars="";
  rows.forEach(r=>{const x=xx(r.d)-bw/2;
    const hT=(r.transfer/maxD)*ih, hC=(r.cash/maxD)*ih;
    const yT=PT+ih-hT, yCa=yT-hC-1.5;
    if(hT>0)bars+=`<rect x="${x.toFixed(1)}" y="${yT.toFixed(1)}" width="${bw.toFixed(1)}" height="${Math.max(1,hT).toFixed(1)}" fill="var(--transfer)" opacity=".85"/>`;
    if(hC>0)bars+=`<rect x="${x.toFixed(1)}" y="${Math.max(PT,yCa).toFixed(1)}" width="${bw.toFixed(1)}" height="${Math.max(1,hC).toFixed(1)}" rx="3" fill="var(--cash)" opacity=".85"/>`;});
  for(let d=1;d<=R.dim;d+=2)
    bars+=`<text x="${xx(d).toFixed(1)}" y="${H-PB+14}" text-anchor="middle" font-size="9.5" font-family="JetBrains Mono,monospace" fill="var(--muted)">${d}</text>`;
  let tl="";
  if(t1&&t1<=maxC) tl=`<line x1="${PL}" y1="${yC(t1).toFixed(1)}" x2="${W-PR}" y2="${yC(t1).toFixed(1)}" stroke="var(--omzet)" stroke-width="1.5" stroke-dasharray="6 3"/>`
    +`<text x="${PL+4}" y="${(yC(t1)-6).toFixed(1)}" font-size="10" font-family="JetBrains Mono,monospace" fill="var(--omzet)">Target 1 · ${rp(t1)}</text>`;
  const pts=rows.map(r=>`${xx(r.d).toFixed(1)},${yC(r.cum).toFixed(1)}`).join(" ");
  const last=rows[rows.length-1];
  let proy="";
  if(R.hariBerjalan<R.dim){
    const over=R.proyeksi>maxC;
    let ex=xx(R.dim), ey=yC(R.proyeksi);
    if(over){const t=(maxC-last.cum)/(R.proyeksi-last.cum);
      ex=xx(last.d)+t*(xx(R.dim)-xx(last.d)); ey=PT;}
    proy=`<line x1="${xx(last.d).toFixed(1)}" y1="${yC(last.cum).toFixed(1)}" x2="${ex.toFixed(1)}" y2="${ey.toFixed(1)}" stroke="var(--muted)" stroke-width="2" stroke-dasharray="4 4"/>`
     +`<text x="${(ex+6).toFixed(1)}" y="${(over?PT-8:ey+3.5).toFixed(1)}" font-size="9.5" font-family="JetBrains Mono,monospace" fill="var(--muted)">proyeksi ${(R.proyeksi/1e6).toFixed(0)}jt ${over?"↗":""}</text>`;}
  let hits="";
  rows.forEach((r,i)=>{hits+=`<rect class="hitg" data-i="${i}" x="${(xx(r.d)-step/2).toFixed(1)}" y="${PT}" width="${step.toFixed(1)}" height="${ih}" fill="transparent"/>`});
  return `<div class="legend">
    <span><i class="swatch" style="background:var(--cash)"></i>Cash harian</span>
    <span><i class="swatch" style="background:var(--transfer)"></i>Transfer harian</span>
    <span><i class="swatch" style="background:var(--accent)"></i>Omzet progresif <span class="muted">— sumbu kanan</span></span>
    <span class="muted">garis putus abu = proyeksi run-rate</span></div>
  <div class="chartscroll"><svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="Omzet harian dan omzet progresif terhadap target">
    ${g}${bars}${tl}
    <polyline points="${pts}" fill="none" stroke="var(--accent)" stroke-width="2.5" stroke-linejoin="round"/>
    ${proy}
    <circle cx="${xx(last.d).toFixed(1)}" cy="${yC(last.cum).toFixed(1)}" r="4.5" fill="var(--accent)" stroke="var(--surface)" stroke-width="2"/>
    <text x="${xx(last.d).toFixed(1)}" y="${(yC(last.cum)-11).toFixed(1)}" text-anchor="middle" font-size="11" font-weight="600" font-family="JetBrains Mono,monospace" fill="var(--accent-ink)">${rp(last.cum)}</text>
    ${hits}</svg></div>`;
}

function indeksHari(R){
  const PEKAN=["Senin","Selasa","Rabu","Kamis","Jumat","Sabtu","Minggu"];
  const byDs=new Map(R.ld.map(l=>[l.tanggal,l]));
  const rows=R.days.map(d=>{const l=byDs.get(d.ds);
    const leads=l?dnum(l.leads):null, sesi=l?dnum(l.sesiFoto):null;
    return {...d,leads,sesi,terisi:!!(l&&leads>0)};});
  const isi=rows.filter(r=>r.terisi);
  if(isi.length<3) return null;
  const avgL=isi.reduce((s,r)=>s+r.leads,0)/isi.length;
  const avgS=isi.reduce((s,r)=>s+r.sesi,0)/isi.length;
  rows.forEach(r=>{r.iL=r.terisi?r.leads/avgL:null; r.iS=(r.terisi&&avgS)?r.sesi/avgS:null});
  const wk=PEKAN.map(h=>{const g=isi.filter(r=>r.hari===h);
    if(!g.length)return {hari:h,n:0};
    const mL=g.reduce((s,r)=>s+r.leads,0)/g.length, mS=g.reduce((s,r)=>s+r.sesi,0)/g.length;
    return {hari:h,n:g.length,leads:mL,sesi:mS,iL:mL/avgL,iS:avgS?mS/avgS:null};});
  const ada=wk.filter(w=>w.n);
  return {rows,isi,avgL,avgS,wk,ada,
    ramai:ada.reduce((a,b)=>b.iL>a.iL?b:a),
    sepi:ada.reduce((a,b)=>b.iL<a.iL?b:a),
    minN:Math.min(...ada.map(w=>w.n)), maxN:Math.max(...ada.map(w=>w.n)),
    belum:R.days.filter(d=>d.berjalan).length-isi.length};
}
const IDX=i=>i==null?"—":i.toFixed(2)+"×";
const LBL=i=>i==null?["","neutral"]:i>=1.15?["RAMAI","final"]:i<=0.85?["SEPI","prog"]:["NORMAL","neutral"];

function chartIndeksHari(X){
  const W=560,H=190,PL=42,PR=14,PT=26,PB=40;
  const top=niceMax(Math.max(...X.ada.map(w=>Math.max(w.iL,w.iS||0)),1.2));
  const iw=W-PL-PR, ih=H-PT-PB;
  const yy=v=>PT+ih-(v/top)*ih;
  const step=iw/X.ada.length, bw=Math.min(30,step*.44);
  const base=yy(1);
  let g="";
  for(let i=0;i<=2;i++){const v=top*i/2;
    g+=`<line x1="${PL}" y1="${yy(v).toFixed(1)}" x2="${W-PR}" y2="${yy(v).toFixed(1)}" stroke="var(--grid)"/>`
     +`<text x="${PL-7}" y="${(yy(v)+3.5).toFixed(1)}" text-anchor="end" font-size="9.5" font-family="JetBrains Mono,monospace" fill="var(--muted)">${v.toFixed(1)}×</text>`;}
  let b="";
  X.ada.forEach((w,i)=>{
    const cx=PL+step*i+step/2;
    const y=yy(w.iL), atas=w.iL>=1;
    const h=Math.max(1.5,Math.abs(base-y));
    b+=`<rect x="${(cx-bw/2).toFixed(1)}" y="${(atas?y:base).toFixed(1)}" width="${bw.toFixed(1)}" height="${h.toFixed(1)}" rx="2"
        fill="var(--lead)" opacity="${atas?.9:.42}"${w.n<2?' stroke="var(--lead)" stroke-width="1" stroke-dasharray="2 2"':''}/>`;
    b+=`<text x="${cx.toFixed(1)}" y="${(atas?y-7:base+Math.abs(base-y)+13).toFixed(1)}" text-anchor="middle" font-size="10.5" font-weight="600"
        font-family="JetBrains Mono,monospace" fill="var(--ink)">${w.iL.toFixed(2)}×</text>`;
    if(w.iS!=null) b+=`<circle cx="${cx.toFixed(1)}" cy="${yy(w.iS).toFixed(1)}" r="3.6" fill="var(--dp)" stroke="var(--surface)" stroke-width="1.5"/>`;
    b+=`<text x="${cx.toFixed(1)}" y="${H-PB+16}" text-anchor="middle" font-size="10.5" fill="var(--ink2)">${w.hari.slice(0,3)}</text>`;
    if(w.n<2) b+=`<text x="${cx.toFixed(1)}" y="${H-PB+28}" text-anchor="middle" font-size="9" fill="var(--muted-soft)">1 pekan</text>`;
  });
  const sp=X.ada.filter(w=>w.iS!=null).map((w,i)=>`${(PL+step*X.ada.indexOf(w)+step/2).toFixed(1)},${yy(w.iS).toFixed(1)}`).join(" ");
  return `<div class="legend">
    <span><i class="swatch" style="background:var(--lead)"></i>Indeks lead</span>
    <span><i class="swatch" style="background:var(--dp);border-radius:50%"></i>Indeks sesi foto</span>
    <span class="muted">garis 1,00× = hari biasa</span></div>
  <svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="Indeks hari ramai per hari dalam pekan">
    ${g}
    <polyline points="${sp}" fill="none" stroke="var(--dp)" stroke-width="1.5" opacity=".5"/>
    ${b}
    <line x1="${PL}" y1="${base.toFixed(1)}" x2="${W-PR}" y2="${base.toFixed(1)}" stroke="var(--ink2)" stroke-width="1.5"/>
  </svg>`;
}

function kartuPolaHari(R){
  const X=indeksHari(R);
  if(!X) return "";
  const bedaSesi=X.ada.filter(w=>w.iL>=.95&&w.iS!=null&&w.iS<=.8).map(w=>w.hari);
  const daftar=a=>a.length<2?a.join(""):a.slice(0,-1).join(", ")+" dan "+a[a.length-1];
  return `
  <div class="card" style="margin-bottom:14px">
    <h3>Pola hari ramai <span class="eyebrow">indeks lead · ${X.isi.length} hari terisi</span></h3>
    <div class="two">
      <div>${chartIndeksHari(X)}</div>
      <div>
        <div class="tw"><table><tbody>
          <tr><td>Paling ramai</td><td class="n"><b>${X.ramai.hari}</b> ${IDX(X.ramai.iL)}</td>
            <td class="n muted">rata ${num(X.ramai.leads)} lead</td></tr>
          <tr><td>Paling sepi</td><td class="n"><b>${X.sepi.hari}</b> ${IDX(X.sepi.iL)}</td>
            <td class="n muted">rata ${num(X.sepi.leads)} lead</td></tr>
          <tr><td>Rata-rata lead / hari</td><td class="n">${num(X.avgL)}</td>
            <td class="n muted">sesi ${num(X.avgS)}/hari</td></tr>
          <tr><td>Sampel</td><td class="n">${X.isi.length} hari</td>
            <td class="n muted">${X.minN}–${X.maxN} pekan per hari</td></tr>
        </tbody></table></div>
        ${bedaSesi.length?`<p class="tiny muted" style="margin-top:10px"><b>${daftar(bedaSesi)}</b>
          ramai bertanya tapi sepi memotret — indeks lead normal, indeks sesi di bawah 0,8×.</p>`:""}
        <p class="tiny muted" style="margin-top:6px">Sampel masih ${X.minN}–${X.maxN} pekan per hari dan
          Selasa–Rabu terangkat wisuda 8–9 September, jadi ini indikasi awal.
          Rincian per tanggal ada di bagian <b>Lead</b>.</p>
      </div>
    </div>
  </div>`;
}

function blokIndeksHari(R){
  const X=indeksHari(R);
  if(!X) return `<div class="card" style="margin-bottom:14px"><h3>Indeks hari ramai</h3>
    <div class="empty">Butuh minimal 3 hari input lead untuk menghitung indeks.</div></div>`;
  const mx=k=>Math.max(...X.ada.map(w=>w[k]||0),...X.isi.map(r=>r[k]||0),1);
  const maxL=mx("iL"), maxS=mx("iS");
  const bar=(i,c,m)=>i==null?'<span class="muted">—</span>'
    :`<i style="background:var(--${c});width:${Math.min(100,i/m*100).toFixed(1)}%"></i>${i.toFixed(2)}×`;
  return `
  <div class="card" style="margin-bottom:14px">
    <h3>Indeks hari ramai <span class="eyebrow">rincian</span></h3>
    <p class="tiny muted" style="margin:-6px 0 14px">Indeks = leads hari itu ÷ rata-rata leads per hari (${num(X.avgL)}).
      1,00× berarti hari biasa. Dihitung dari lead, bukan omzet.
      ${X.belum?`${X.belum} hari berjalan belum diisi leadnya dan <b>tidak</b> ikut rata-rata.`:""}
      Ambang: ≥1,15× ramai, ≤0,85× sepi.</p>
    <div class="two" style="margin-bottom:14px">
      <div>
        <h4 class="eyebrow" style="margin:0 0 7px">Pola hari dalam pekan</h4>
        <div class="tw"><table><thead><tr><th>Hari</th><th class="n">Lead rata</th>
          <th class="n">Indeks lead</th><th class="n">Sesi rata</th><th class="n">Indeks sesi</th>
          <th class="n">Sampel</th></tr></thead><tbody>
          ${X.wk.map(w=>w.n?`<tr><td>${w.hari}</td><td class="n">${num(w.leads)}</td>
            <td class="n heat">${bar(w.iL,"lead",maxL)}</td><td class="n">${num(w.sesi)}</td>
            <td class="n heat">${bar(w.iS,"dp",maxS)}</td><td class="n muted">${w.n} pekan</td></tr>`
            :`<tr><td>${w.hari}</td><td colspan="5" class="muted tiny">belum ada hari terisi</td></tr>`).join("")}
        </tbody></table></div>
      </div>
      <div class="note warn"><b>Baca ini dulu sebelum memakai angkanya.</b>
        Sampel baru ${X.isi.length} hari — tiap hari dalam pekan cuma terwakili ${X.minN}–${X.maxN} kali.
        Selasa dan Rabu juga terangkat oleh wisuda 8–9 September, satu event, bukan pola mingguan.
        Jadi ini <b>indikasi awal</b>, belum pola yang bisa dipakai mengunci jadwal ads.</div>
    </div>
    <h4 class="eyebrow" style="margin:0 0 7px">Per tanggal</h4>
    <div class="tw"><table><thead><tr><th>Tgl</th><th>Hari</th><th class="n">Leads</th>
      <th class="n">Indeks lead</th><th class="n">Sesi foto</th><th class="n">Indeks sesi</th>
      <th>Status</th></tr></thead><tbody>
      ${X.rows.map(r=>{const [t,c]=LBL(r.iL);
        return `<tr class="${r.berjalan?"":"future"}"><td class="mono">${r.d}</td><td>${r.hari}</td>
        ${!r.berjalan?`<td class="n"></td><td class="n"></td><td class="n"></td><td class="n"></td><td></td>`
        :r.terisi?`<td class="n">${num(r.leads)}</td><td class="n heat">${bar(r.iL,"lead",maxL)}</td>
          <td class="n">${num(r.sesi)}</td><td class="n heat">${bar(r.iS,"dp",maxS)}</td>
          <td><span class="pill ${c}">${t}</span></td>`
        :`<td colspan="4" class="muted tiny">lead belum diinput</td>
          <td><span class="pill neutral">tidak dihitung</span></td>`}</tr>`}).join("")}
      <tr class="total"><td colspan="2">Rata-rata ${X.isi.length} hari terisi</td>
        <td class="n">${num(X.avgL)}</td><td class="n">1.00×</td>
        <td class="n">${num(X.avgS)}</td><td class="n">1.00×</td><td></td></tr>
    </tbody></table></div>
  </div>`;
}

/* ---------- kalender bulanan ---------- */
let calMetric="omzet";
function rpk(n){
  if(n==null||isNaN(n))return "—";
  if(n>=1e9)return "Rp "+(n/1e9).toFixed(2).replace(".",",")+" M";
  if(n>=1e6)return "Rp "+(n/1e6).toFixed(2).replace(".",",")+" jt";
  if(n>=1e3)return "Rp "+Math.round(n/1e3)+" rb";
  return "Rp "+Math.round(n);
}

function calendar(R){
  const [y,m]=R.c.bulan.split("-").map(Number);
  const off=(new Date(y,m-1,1).getDay()+6)%7;
  const cells=[]; for(let i=0;i<off;i++)cells.push(null);
  R.days.forEach(d=>cells.push(d));
  while(cells.length%7)cells.push(null);
  const rows=[]; for(let i=0;i<cells.length;i+=7)rows.push(cells.slice(i,i+7));

  const key=calMetric==="order"?"tx":calMetric==="avg"?"avg":"omzet";
  const run=R.days.filter(d=>d.berjalan);
  const maxV=Math.max(1,...run.map(d=>d[key]||0));
  const now=new Date();
  const todayD=(now.getFullYear()===y&&now.getMonth()===m-1)?now.getDate():0;

  const AM=(S.ads&&S.ads.bulan===R.c.bulan&&S.ads.marks)||[];
  const mark=day=>{const m=AM.find(x=>+x.d===day);
    return m?`<i class="ab" title="${esc(m.label)}">${esc(m.label.split(" ")[0])}</i>`:""};

  const val=d=>calMetric==="order"?num(d.tx)+" order":calMetric==="avg"?rpk(d.avg):rpk(d.omzet);
  const meta=d=>calMetric==="order"?rpk(d.omzet)
    :calMetric==="avg"?`${num(d.txPaid)} tx masuk`:`${num(d.tx)} order`;

  const wsum=rows.map(row=>{
    const ds=row.filter(d=>d&&d.berjalan);
    const so=ds.reduce((s,d)=>s+d.omzet,0);
    const st=ds.reduce((s,d)=>s+d.tx,0);
    const sp=ds.reduce((s,d)=>s+d.txPaid,0);
    return {ds,so,st,sp,v:calMetric==="order"?st:calMetric==="avg"?(sp?so/sp:0):so};
  });
  const maxW=Math.max(1,...wsum.map(w=>w.v));

  let html=["Sen","Sel","Rab","Kam","Jum","Sab","Min"]
    .map(h=>`<div class="hd">${h}</div>`).join("")+`<div class="hd">Pekan</div>`;

  rows.forEach((row,wi)=>{
    row.forEach(d=>{
      if(!d){html+=`<div class="cel void"></div>`;return}
      const t=d.d===todayD?" today":"";
      if(!d.berjalan){html+=`<div class="cel${t}"><span class="dn">${d.d}${mark(d.d)}</span></div>`;return}
      html+=`<div class="cel on${t}" style="--h:${Math.min(1,(d[key]||0)/maxV).toFixed(3)}">
        <span class="dn">${d.d}${mark(d.d)}</span><span class="dv">${val(d)}</span>
        <span class="dm">${meta(d)}</span></div>`;
    });
    const {ds,so,st,sp,v}=wsum[wi];
    html+=`<div class="cel wk${ds.length?" on":""}"${ds.length
        ? ` style="--h:${Math.min(1,v/maxW).toFixed(3)}"`:""}>
      <span class="wl">Pekan ${wi+1}</span>`+
      (ds.length
        ? `<span class="dv">${calMetric==="order"?num(st)+" order"
            :calMetric==="avg"?rpk(sp?so/sp:0):rpk(so)}</span>
           <span class="dm">${calMetric==="order"?rpk(so):num(st)+" order"}</span>`
        : `<span class="dv muted">—</span>`)+`</div>`;
  });
  return `<div class="calwrap"><div class="cal">${html}</div></div>`;
}

function barlist(items,colorVar,valFmt){
  if(!items.length)return `<div class="empty">Belum ada data.</div>`;
  const max=Math.max(...items.map(i=>i.v))||1;
  return `<div class="grid" style="gap:7px">`+items.map(i=>`
    <div style="display:grid;grid-template-columns:1fr auto;gap:8px;align-items:center">
      <div style="min-width:0">
        <div style="display:flex;justify-content:space-between;gap:8px;font-size:12.5px;margin-bottom:3px">
          <span style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${esc(i.k)}</span>
          <span class="mono muted">${esc(i.sub||"")}</span></div>
        <div style="height:7px;background:var(--surface3);border-radius:4px;overflow:hidden">
          <i style="display:block;height:100%;width:${(i.v/max*100).toFixed(1)}%;background:var(--${colorVar});border-radius:0 4px 4px 0"></i></div>
      </div>
      <span class="mono" style="font-size:12.5px;min-width:96px;text-align:right">${valFmt(i.v)}</span>
    </div>`).join("")+`</div>`;
}

/* ============================ views ============================ */
const VIEWS=[
  {id:"tahunan",grp:"Ringkasan",label:"Laporan Tahunan"},
  {id:"dash",grp:"Ringkasan",label:"Dashboard (Bulanan)"},
  {id:"omzet",grp:"Ringkasan",label:"Omzet Harian"},
  {id:"target",grp:"Ringkasan",label:"Target & Skenario"},
  {id:"est",grp:"Ringkasan",label:"Estimasi Omzet"},
  {id:"trx",grp:"Input",label:"Transaksi"},
  {id:"biaya",grp:"Input",label:"Neraca (COGS & OPEX)"},
  {id:"gaji",grp:"Input",label:"Gaji Karyawan"},
  {id:"shift",grp:"Input",label:"Shift"},
  {id:"lead",grp:"Input",label:"Lead"},
  {id:"kpi",grp:"Input",label:"KPI & Bonus"},
  {id:"crew",grp:"Analisis",label:"Paket & Crew"},
  {id:"yoy",grp:"Analisis",label:"Perbandingan YoY"},
  {id:"ads",grp:"Analisis",label:"Jadwal Ads"},
  {id:"set",grp:"Analisis",label:"Pengaturan"},
];

function render(){
  const R=compute();
  document.getElementById("tbPeriod").textContent=BULAN[+R.c.bulan.split("-")[1]-1]+" "+R.c.bulan.split("-")[0];
  document.getElementById("tbCut").textContent=`s.d. ${R.cutDay} ${BULAN[+R.c.bulan.split("-")[1]-1]} · ${R.hariBerjalan}/${R.dim} hari`;
  const st=document.getElementById("tbStatus");
  st.textContent=R.c.status; st.className="pill "+(R.c.status==="Final"?"final":"prog");

  const up=document.getElementById("tbUpd"), ok=syncSukses(), akhir=syncUrut()[0];
  if(up){
    if(ok){ const w=wibParts(ok.mulai);
      up.hidden=false;
      up.textContent=`Diperbarui ${w.tgl.split(" ").slice(0,2).join(" ")} ${w.jam}`;
      up.title=`Terakhir berhasil ${tgljam(ok.mulai)} — ${lalu(ok.mulai)}`;
      up.className="pill "+(akhir&&akhir.status==="gagal"?"bad":"neutral");
    } else up.hidden=true;
  }

  // nav
  const nav=document.getElementById("nav"); const tabs=document.getElementById("tabsm");
  const counts={trx:R.tx,biaya:R.ex.length,gaji:R.gajiRoster.filter(r=>r.total).length,shift:R.shiftTot,lead:R.ld.length,kpi:R.kpi.length,tahunan:"12 bln"};
  let html="",lastGrp="";
  VIEWS.forEach(v=>{ if(v.grp!==lastGrp){html+=`<div class="grp">${v.grp}</div>`;lastGrp=v.grp}
    html+=`<button data-v="${v.id}" aria-current="${view===v.id}">${v.label}${counts[v.id]!=null?`<span class="cnt">${counts[v.id]}</span>`:""}</button>`;});
  nav.innerHTML=html;
  tabs.innerHTML=VIEWS.map(v=>`<button data-v="${v.id}" aria-current="${view===v.id}">${v.label}</button>`).join("");
  [...nav.querySelectorAll("button"),...tabs.querySelectorAll("button")].forEach(b=>
    b.onclick=()=>{view=b.dataset.v;render();document.querySelector(".main").scrollIntoView({block:"start"})});

  document.getElementById("views").innerHTML=`<section class="view">${({
    dash:vDash,tahunan:vTahunan,omzet:vOmzet,target:vTarget,trx:vTrx,biaya:vBiaya,
    shift:vShift,lead:vLead,kpi:vKpi,gaji:vGaji,crew:vCrew,yoy:vYoy,ads:vAds,est:vEst,set:vSet})[view](R)}</section>`;
  wire(R);
}

function wibParts(iso){
  const d=new Date(iso);
  if(!iso||isNaN(d))return null;
  const w=new Date(d.getTime()+7*3600000);
  const p=n=>String(n).padStart(2,"0");
  return {tgl:`${w.getUTCDate()} ${BULAN[w.getUTCMonth()].slice(0,3)} ${w.getUTCFullYear()}`,
    jam:`${p(w.getUTCHours())}.${p(w.getUTCMinutes())}`, ms:d.getTime()};
}
function tgljam(iso){const w=wibParts(iso);return w?`${w.tgl}, ${w.jam} WIB`:"—"}
function lalu(iso){
  const w=wibParts(iso); if(!w)return "";
  const m=Math.round((Date.now()-w.ms)/60000);
  if(m<0)return "terjadwal";
  if(m<2)return "baru saja";
  if(m<60)return `${m} menit lalu`;
  const j=Math.floor(m/60); if(j<24)return `${j} jam lalu`;
  const h=Math.floor(j/24); return h===1?"kemarin":`${h} hari lalu`;
}
function durasi(a,b){
  const x=wibParts(a),y=wibParts(b); if(!x||!y)return "";
  const s=Math.round((y.ms-x.ms)/1000); if(s<0)return "";
  return s<90?`${s} detik`:`${Math.floor(s/60)} menit ${s%60} detik`;
}
const syncUrut=()=>[...S.sync].sort((a,b)=>String(b.mulai||"").localeCompare(String(a.mulai||"")));
const syncSukses=()=>syncUrut().find(s=>s.status==="sukses"||s.status==="manual")||null;

function kartuPembaruan(){
  const list=syncUrut(), ok=syncSukses(), akhir=list[0];
  if(!list.length) return "";
  const belumTuntas=akhir&&(akhir.status==="gagal"||akhir.status==="berjalan");
  const LBL={sukses:["berhasil","ok"],manual:["manual","skip"],gagal:["gagal","no"],
             berjalan:["berjalan","wait"],sebagian:["sebagian","wait"],dilewati:["dilewati","skip"]};
  return `
  <div class="updwrap"><div class="card">
    <h3>Pembaruan Data</h3>
    ${belumTuntas&&ok?`<p class="tiny muted" style="margin:-6px 0 12px">Angka di halaman ini
      dari ${tgljam(ok.mulai)}.</p>`:""}
    <div class="upd">
      ${list.slice(0,6).map((s,i)=>{
        const [lbl,cls]=LBL[s.status]||["berhasil","ok"];
        const w=wibParts(s.mulai);
        return `<div class="urow${i===0?" now":""}${s.status==="gagal"?" bad":""}"
          title="${esc(s.ringkas||"")}">
          <span class="ut">${w?w.tgl:"—"} <b>${w?w.jam:""}</b></span>
          <span class="us ${cls}">${lbl}</span></div>`}).join("")}
    </div>
  </div></div>`;
}

function vDash(R){
  const t1=R.tiers[0];
  const scr=screening(R);
  const bad=scr.filter(s=>s.st==="bad").length, warn=scr.filter(s=>s.st==="warn").length;
  return `
  <div class="vhead"><div><div class="eyebrow">Progressive report</div>
    <h2>Dashboard</h2></div>
    <p>Semua angka di halaman ini diturunkan dari satu perhitungan, jadi omzet di sini sama persis dengan omzet di setiap bagian lain.</p></div>

  <div class="stats" style="margin-bottom:16px">
    <div class="stat"><span class="k">Omzet aktual</span><span class="v">${rp(R.omzet)}</span>
      <span class="m">${num(R.txPaid)} transaksi uang masuk</span></div>
    <div class="stat"><span class="k">Cash</span><span class="v sm">${rp(R.cash)}</span>
      <span class="m">${pct(R.omzet?R.cash/R.omzet:0)} dari omzet</span></div>
    <div class="stat"><span class="k">Transfer</span><span class="v sm">${rp(R.transfer)}</span>
      <span class="m">${pct(R.omzet?R.transfer/R.omzet:0)} dari omzet</span></div>
    <div class="stat"><span class="k">Run-rate / hari</span><span class="v sm">${rp(R.runRate)}</span>
      <span class="m">${R.hariBerjalan} hari berjalan</span></div>
    <div class="stat"><span class="k">Proyeksi ${R.dim} hari</span><span class="v sm">${rp(R.proyeksi)}</span>
      <span class="m">pace saat ini, bukan omzet final</span></div>
  </div>

  <div class="dashmid">
  <div class="card">
    <div class="calhead">
      <div><div class="mo">${BULAN[+R.c.bulan.split("-")[1]-1]} ${R.c.bulan.split("-")[0]}</div>
        <span class="tiny muted">${R.hariBerjalan} hari berjalan · ${num(R.tx)} order · ${rp(R.omzet)}</span></div>
      <div class="seg" id="segCal">
        <button data-cm="omzet" aria-pressed="${calMetric==="omzet"}">Omzet</button>
        <button data-cm="order" aria-pressed="${calMetric==="order"}">Order</button>
        <button data-cm="avg" aria-pressed="${calMetric==="avg"}">Rata-rata</button>
      </div>
    </div>
    ${calendar(R)}
    <p class="tiny muted" style="margin-top:9px">Warna mengikuti besarnya angka. Tanggal setelah cut-off tampil tanpa angka; kolom kanan menjumlah tiap pekan.</p>
  </div>
  ${kartuPembaruan()}
  </div>

  <div class="card" style="margin-bottom:14px"><h3>Omzet harian &amp; progresif <span class="eyebrow">cash + transfer · menuju target</span></h3>${chartGabung(R)}</div>
  ${kartuPolaHari(R)}

  <div class="two" style="margin-bottom:14px">
    <div class="card"><h3>Ringkasan laba rugi</h3>
      ${R.adaBiaya?"":`<div class="note warn" style="margin-bottom:10px">${R.ex.length?`${R.ex.length} biaya sudah tercatat tapi belum dikategorikan, jadi laporan berhenti di Gross Profit. Beri jenis dan kategori di bagian <b>Biaya COGS/OPEX</b>`:`Belum ada biaya tercatat, jadi laporan berhenti di Gross Profit. Isi di bagian <b>Biaya COGS/OPEX</b>`} — angka di bawah ikut terisi otomatis.</div>`}
      <div class="tw"><table><tbody>
        ${[["Omzet",R.omzet,1],["Total COGS",R.cogs?-R.cogs:(R.adaBiaya?0:null),R.omzet?R.cogs/R.omzet:null],
           ["Gross Profit",R.adaBiaya?R.grossProfit:null,R.omzet&&R.adaBiaya?R.grossProfit/R.omzet:null],
           ["Total OPEX",R.opex?-R.opex:(R.adaBiaya?0:null),R.omzet?R.opex/R.omzet:null],
           ["Operating Profit",R.adaBiaya?R.operatingProfit:null,R.omzet&&R.adaBiaya?R.operatingProfit/R.omzet:null],
           ["Pendapatan Lainnya",R.pendLain||null,null],["Biaya Lainnya",R.biayaLain?-R.biayaLain:null,null],
           ["Nett Profit",R.adaBiaya?R.nettProfit:null,R.adaBiaya?R.nettMargin:null]].map(([k,v,p])=>`
          <tr${k==="Nett Profit"?' class="total"':""}><td>${k}</td>
          <td class="n">${v===null?'<span class="muted">pending</span>':rp(v)}</td>
          <td class="n muted">${p==null?"":pct(Math.abs(p))}</td></tr>`).join("")}
      </tbody></table></div>
      <p class="tiny muted" style="margin-top:8px">Nett Profit = Omzet − COGS − OPEX + Pendapatan Lainnya − Biaya Lainnya. Non-P&L (${rp(R.nonPL)}) tidak ikut.</p>
    </div>
    <div class="card"><h3>Final screening <span class="pill ${bad?"bad":warn?"prog":"final"}">${bad?bad+" gagal":warn?warn+" perlu dilengkapi":"semua lolos"}</span></h3>
      <div class="screen">${scr.map(s=>`<div class="chk ${s.st}">
        <span class="badge">${s.st==="ok"?"LOLOS":s.st==="bad"?"GAGAL":"ISI"}</span>
        <span><b>${esc(s.t)}</b> — <span class="muted">${esc(s.d)}</span></span></div>`).join("")}</div>
    </div>
  </div>

  <div class="two">
    <div class="card"><h3>Rekonsiliasi kas harian</h3>
      <p class="tiny muted" style="margin-bottom:10px">Kolom Cash pada transaksi dibandingkan baris kontrol “Pendapatan Tunai” yang dicatat admin tiap hari.</p>
      <div class="tw"><table><thead><tr><th>Tgl</th><th class="n">Cash transaksi</th><th class="n">Kontrol kas</th><th class="n">Selisih</th></tr></thead><tbody>
      ${R.rekon.map(r=>`<tr><td class="mono">${r.d}</td><td class="n">${rp(r.cash)}</td>
        <td class="n">${r.ctrl===null?'<span class="muted">—</span>':rp(r.ctrl)}</td>
        <td class="n" style="color:${r.selisih?'var(--crit)':'var(--muted)'}">${r.selisih===null?"—":(r.selisih?rp(r.selisih):"cocok")}</td></tr>`).join("")}
      <tr class="total"><td>Total</td><td class="n">${rp(R.cash)}</td>
        <td class="n">${rp(R.rekon.reduce((s,r)=>s+(r.ctrl||0),0))}</td>
        <td class="n">${R.rekonBeda.length?R.rekonBeda.length+" hari beda":"cocok"}</td></tr>
      </tbody></table></div></div>
    <div class="card"><h3>Metrik monitoring</h3>
      <div class="tw"><table><tbody>
        ${[["Jumlah transaksi",num(R.tx)],["Transaksi uang masuk",num(R.txPaid)],["Transaksi Rp0",num(R.rp0)],
           ["Rata-rata per pembayaran",rp(R.avgTx)],
           ["Paket terlayani",num(R.paketTerlayani)],
           ["Rata-rata nilai paket",rp(R.avgPaket)],
           ["Paket pakai DP",`${num(R.paketPecah)}${R.paketTerlayani?` · ${pct(R.paketPecah/R.paketTerlayani)}`:""}`],
           ["Hari berjalan",`${R.hariBerjalan} / ${R.dim}`],
           ["Total shift tercatat",num(R.shiftTot)],["Total leads",R.totLeads?num(R.totLeads):"—"],
           ["Conversion lead → DP",R.conv==null?"—":pct(R.conv)],
           ["Progress "+(R.tierBerikut?`Target ${R.tierBerikut.tier}`:"target"),R.tierBerikut?pct(R.omzet/R.tierBerikut.omzet):"tercapai"],
           ["Sisa ke target",R.tierBerikut?rp(R.tierBerikut.omzet-R.omzet):"—"],
           ["Bonus pool aktual",rp(R.pool)]
        ].map(([k,v])=>`<tr><td>${k}</td><td class="n">${v}</td></tr>`).join("")}
      </tbody></table></div></div>
  </div>`;
}

function chartTahunanSeasonality(months, yr, avg25) {
  const W = 860, H2 = 250, PL = 64, PR = 60, PT = 24, PB = 38;
  const maxO = niceMax(Math.max(...months.flatMap(m => [dnum(m.omzet25), dnum(m.proyeksi26)])) * 1.08);
  const iw = W - PL - PR, ih = H2 - PT - PB, step = iw / 12, bw = Math.min(13, step * 0.35);
  const yy = v => PT + ih - (v / maxO) * ih;

  // Grid lines
  let g = "";
  for (let i = 0; i <= 4; i++) {
    const v = maxO * i / 4, y = yy(v);
    g += `<line x1="${PL}" y1="${y.toFixed(1)}" x2="${W - PR}" y2="${y.toFixed(1)}" stroke="var(--grid)"/>
    <text x="${PL - 8}" y="${(y + 3.5).toFixed(1)}" text-anchor="end" font-size="9.5" font-family="JetBrains Mono,monospace" fill="var(--muted)">${v >= 1e6 ? (v / 1e6).toFixed(0) + "jt" : num(v)}</text>`;
  }

  // Baseline 1.00x horizontal dashed line
  const yAvg = yy(avg25);
  g += `<line x1="${PL}" y1="${yAvg.toFixed(1)}" x2="${W - PR}" y2="${yAvg.toFixed(1)}" stroke="var(--warn)" stroke-dasharray="3 3" stroke-width="1.2"/>
  <text x="${W - PR + 6}" y="${(yAvg + 3.5).toFixed(1)}" font-size="9" font-family="JetBrains Mono,monospace" fill="var(--warn)">1.00× (Rata-rata Musiman)</text>`;

  // Bars and points
  let bars = "", curvePoints = [];
  months.forEach((m, i) => {
    const cx = PL + step * i + step / 2;
    // Bar 2025 (Acuan Seasonality)
    if (m.omzet25 > 0) {
      const h = (m.omzet25 / maxO) * ih;
      bars += `<rect x="${(cx - bw - 1).toFixed(1)}" y="${yy(m.omzet25).toFixed(1)}" width="${bw.toFixed(1)}" height="${h.toFixed(1)}" rx="2" fill="var(--hairline-strong)"/>`;
    }
    // Bar 2026: HANYA dirender jika terverifikasi (September 2026)
    if (m.isCurrent && m.proyeksi26 > 0) {
      const h = (m.proyeksi26 / maxO) * ih;
      bars += `<rect x="${(cx + 1).toFixed(1)}" y="${yy(m.proyeksi26).toFixed(1)}" width="${bw.toFixed(1)}" height="${h.toFixed(1)}" rx="2" fill="var(--accent)" stroke="var(--accent-ink)" stroke-width="1.5"/>`;
    }

    // X Axis Month Label
    bars += `<text x="${cx.toFixed(1)}" y="${H2 - PB + 14}" text-anchor="middle" font-size="10" font-family="JetBrains Mono,monospace" font-weight="${m.isCurrent ? '700' : '500'}" fill="${m.isCurrent ? 'var(--accent)' : 'var(--muted)'}">${m.short}</text>`;

    // Seasonality Index Dot (berdasarkan acuan musiman)
    const dotY = yy(m.omzet25);
    curvePoints.push({ x: cx, y: dotY, sIndex: m.sIndex, pill: m.seasonPill });
  });

  // Polyline for seasonality
  let poly = `<polyline fill="none" stroke="var(--accent)" stroke-width="2" opacity=".4" points="${curvePoints.map(p => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(" ")}"/>`;
  let dots = curvePoints.map(p => {
    const col = p.pill === 'crit' ? 'var(--crit)' : (p.pill === 'final' ? 'var(--good)' : 'var(--warn)');
    return `<circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="3.5" fill="${col}" stroke="var(--surface)" stroke-width="1.5"/>
    <text x="${p.x.toFixed(1)}" y="${(p.y - 7).toFixed(1)}" text-anchor="middle" font-size="8.5" font-family="JetBrains Mono,monospace" font-weight="600" fill="${col}">${p.sIndex.toFixed(2)}×</text>`;
  }).join("");

  return `
  <div class="legend">
    <span><i class="swatch" style="background:var(--hairline-strong)"></i>${yr-1} Benchmark Musiman</span>
    <span><i class="swatch" style="background:var(--accent)"></i>${yr} Terverifikasi (September)</span>
    <span><i class="swatch" style="background:var(--crit)"></i>Super Peak (&gt;1.50×)</span>
    <span><i class="swatch" style="background:var(--good)"></i>High Season (1.10–1.49×)</span>
    <span class="muted" style="margin-left:auto;">Garis putus-putus kuning = 1.00× Rata-rata Musiman</span>
  </div>
  <svg class="chart" viewBox="0 0 ${W} ${H2}" role="img" aria-label="Siklus Seasonality dan Omzet 12 Bulan">${g}${bars}${poly}${dots}</svg>`;
}

function vTahunan(R) {
  const yr = +R.c.bulan.split("-")[0];
  const curM = +R.c.bulan.split("-")[1]; // 9 (September)
  const H = (S.history && S.history.months) || [];
  
  // Data acuan musiman 2025
  const data25 = H.filter(m => m.tahun === yr - 1);
  const tot25 = data25.reduce((s, m) => s + dnum(m.omzet), 0) || 720036150;
  const avg25 = tot25 / 12;

  const SEASON_INFO = [
    { no: 1, label: "Januari", momentum: "Pasca Liburan & Tahun Baru", note: "Low season awal tahun, fokus pada couple & self-photo" },
    { no: 2, label: "Februari", momentum: "Couple & Valentine Session", note: "Permintaan foto pasangan & sahabat meningkat" },
    { no: 3, label: "Maret", momentum: "Pra-Ramadhan & Personal Portrait", note: "Normal season, persiapan promo sesi keluarga Idul Fitri" },
    { no: 4, label: "April", momentum: "Hari Raya Idul Fitri & Keluarga", note: "Lonjakan foto keluarga besar pasca mudik lebaran" },
    { no: 5, label: "Mei", momentum: "Wisuda Gelombang 1 & Grup", note: "Wisuda awal tahun beberapa perguruan tinggi" },
    { no: 6, label: "Juni", momentum: "Liburan Sekolah & Wisuda Tengah Tahun", note: "High season liburan anak sekolah & graduation SMA" },
    { no: 7, label: "Juli", momentum: "Tahun Ajaran Baru & Mahasiswa Baru", note: "Foto grup organisasi, OSIS, dan personal portfolio" },
    { no: 8, label: "Agustus", momentum: "Wisuda Periode 2 & Pra-Wisuda Akbar", note: "High season wisuda & awal gelombang booking September" },
    { no: 9, label: "September", momentum: "SUPER PEAK: Wisuda Akbar", note: "Puncak omzet tahunan, wisuda serentak UNTIDAR & universitas sekitar" },
    { no: 10, label: "Oktober", momentum: "Wisuda Lanjutan & Prewedding", note: "Wisuda periode susulan, sesi maternity & prewedding" },
    { no: 11, label: "November", momentum: "Low Season & Persiapan Akhir Tahun", note: "Waktu ideal maintenance studio & push booking Desember" },
    { no: 12, label: "Desember", momentum: "Liburan Akhir Tahun & Natal", note: "High season sesi keluarga, annual review, dan foto akhir tahun" }
  ];

  const months = SEASON_INFO.map(info => {
    const m25 = data25.find(m => m.no === info.no) || {};
    const o25 = dnum(m25.omzet) || (info.no === 9 ? 151036150 : 50000000);
    const sIndex = o25 / avg25;

    let seasonTag = "NORMAL";
    let seasonPill = "neutral";
    if (sIndex >= 1.50) { seasonTag = "SUPER PEAK"; seasonPill = "crit"; }
    else if (sIndex >= 1.10) { seasonTag = "HIGH"; seasonPill = "final"; }
    else if (sIndex < 0.90) { seasonTag = "LOW"; seasonPill = "prog"; }

    const isCurrent = (info.no === curM);
    const isPast = (info.no < curM);
    const isFuture = (info.no > curM);

    // USER REQUIREMENT:
    // Bulan sebelum & sesudah September dikosongkan karena belum dicocokkan (belum lulus untuk laporan real).
    let o26 = null;
    let proyeksi26 = null;
    let status = "Belum Dicocokkan";
    let statusPill = "neutral";
    let yoy = null;

    if (isCurrent) {
      o26 = R.omzet;
      proyeksi26 = R.proyeksi;
      status = "Berjalan (Terverifikasi)";
      statusPill = "crit";
      yoy = o25 ? (((R.proyeksi || R.omzet) - o25) / o25) : null;
    }

    return {
      ...info,
      short: info.label.slice(0, 3),
      omzet25: o25,
      omzet26: o26,
      proyeksi26: proyeksi26,
      sIndex: sIndex,
      seasonTag: seasonTag,
      seasonPill: seasonPill,
      status: status,
      statusPill: statusPill,
      isCurrent: isCurrent,
      isPast: isPast,
      isFuture: isFuture,
      yoy: yoy
    };
  });

  // Komparasi September 2026 vs September 2025
  const sep25 = months.find(m => m.no === 9)?.omzet25 || 151036150;
  const growthSepYoY = sep25 ? ((R.proyeksi - sep25) / sep25) : null;
  const peakMonth = months.reduce((max, m) => m.sIndex > max.sIndex ? m : max, months[0]);

  return `
  <div class="vhead"><div><div class="eyebrow">Tahun Fiskal ${yr} · Multi-Bulan &amp; Siklus Musiman</div>
    <h2>Laporan Tahunan &amp; Seasonality</h2></div>
    <p>Tinjauan performa 12 bulan eksplisit dari Januari hingga Desember ${yr}, matriks indeks musiman (Seasonality Index), dan integrasi menuju laporan bulanan.</p></div>

  <!-- Top KPI Cards -->
  <div class="stats" style="margin-bottom:16px">
    <div class="stat">
      <span class="k">Omzet Terverifikasi ${yr}</span>
      <span class="v" style="color:var(--accent);">${rp(R.omzet)}</span>
      <span class="m">September MTD (s.d. ${R.cutDay} Sep · Live Log Order)</span>
    </div>
    <div class="stat">
      <span class="k">Proyeksi September ${yr}</span>
      <span class="v sm">${rp(R.proyeksi)}</span>
      <span class="m">Run-rate akhir bulan Super Peak</span>
      <div class="bar"><i style="width:${Math.min(100, (R.omzet/R.proyeksi)*100).toFixed(0)}%"></i></div>
    </div>
    <div class="stat">
      <span class="k">Pertumbuhan Sep YoY vs ${yr-1}</span>
      <span class="v sm" style="color:${growthSepYoY>=0?"var(--good)":"var(--crit)"};">${(growthSepYoY>=0?"+":"")+pct(growthSepYoY)}</span>
      <span class="m">Realisasi Sep ${yr-1}: ${rp(sep25)}</span>
    </div>
    <div class="stat">
      <span class="k">Status Rekonsiliasi Tahunan</span>
      <span class="v sm" style="font-size:21px;">1 / 12 Terverifikasi</span>
      <span class="m">Sep ${yr} aktif · 11 bln menunggu pencocokan</span>
    </div>
  </div>

  <!-- Banner Penjelasan Seasonality Studio -->
  <div class="note ok" style="margin-bottom:16px">
    <b>Pola Musiman Studio Foto (Seasonality Index):</b>
    Indeks <b>1.00×</b> adalah garis tengah rata-rata bulanan studio.
    Bulan <b>September (1.85× – 2.50×)</b> adalah puncak tahunan tertinggi (Super Peak) berkat wisuda akbar universitas di Magelang dan sekitarnya.
    Bulan <b>Juni &amp; Agustus</b> menjadi High Season kedua, sementara <b>Januari, Februari &amp; November</b> merupakan Low Season alami.
    <div style="margin-top:6px;font-size:12px;opacity:.9;border-top:1px dashed currentColor;padding-top:6px;">
      🔒 <b>Status Data Real:</b> Sesuai standarisasi audit, data tahun ${yr} untuk bulan <b>Januari–Agustus</b> dan <b>Oktober–Desember</b> saat ini <b>dikosongkan</b> karena belum dicocokkan dengan data pembukuan riil. Hanya <b>September ${yr}</b> yang terverifikasi aktif &amp; live.
    </div>
  </div>

  <!-- Chart Seasonality & Omzet 12 Bulan -->
  <div class="card" style="margin-bottom:20px">
    <h3>Siklus Seasonality &amp; Tren Omzet 12 Bulan (${yr-1} vs ${yr})</h3>
    ${chartTahunanSeasonality(months, yr, avg25)}
  </div>

  <!-- Section 12 Kotak Bulan (Grid of 12 Month Cards) -->
  <div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:12px;flex-wrap:wrap;gap:8px;">
    <div>
      <h3 style="font-size:18px;font-weight:600;color:var(--ink);margin:0;">Ringkasan 12 Bulan Eksplisit (${yr})</h3>
      <p class="tiny muted" style="margin-top:2px;">Klik pada kotak bulan mana saja untuk menuju ke laporan operasional bulanan.</p>
    </div>
    <span class="eyebrow">12 Kotak Interaktif</span>
  </div>

  <div class="mgrid">
    ${months.map(m => `
      <div class="month-card ${m.isCurrent ? 'active-month' : ''}" data-month="${m.no}">
        <div class="mhead">
          <div>
            <span class="mname">${m.label} ${yr} ${m.isCurrent ? '<i class="live-dot" title="Bulan Berjalan Live"></i>' : ''}</span>
            <div class="mmomentum">${esc(m.momentum)}</div>
          </div>
          <span class="pill ${m.statusPill}" style="font-size:10.5px;">${m.status}</span>
        </div>

        <div class="mbody">
          <div class="mstat">
            <span class="mk">${m.isCurrent ? 'Omzet Masuk (Live)' : 'Omzet Realisasi'}</span>
            <span class="mv ${m.isCurrent ? 'active' : ''}" style="${!m.isCurrent ? 'color:var(--muted-soft);font-weight:500;' : ''}">${m.omzet26 != null ? rp(m.omzet26) : '—'}</span>
            ${m.isCurrent 
              ? `<span class="msub" style="color:var(--accent);">Proyeksi run-rate: ${rp(R.proyeksi)} · Acuan ${yr-1}: ${rp(m.omzet25)}</span>` 
              : `<span class="msub muted">Belum dicocokkan · Acuan ${yr-1}: ${rp(m.omzet25)}</span>`}
          </div>

          <div class="mseason">
            <div style="display:flex;justify-content:space-between;align-items:center;">
              <span class="mseason-label">Seasonality Index</span>
              <span class="pill ${m.seasonPill}" style="font-size:10px;padding:1px 7px;">${m.sIndex.toFixed(2)}× · ${m.seasonTag}</span>
            </div>
            <div class="mseason-bar"><i style="width:${Math.min(100, (m.sIndex / 2.2) * 100).toFixed(0)}%;background:var(--${m.seasonPill==='crit'?'crit':(m.seasonPill==='final'?'good':'warn')});"></i></div>
          </div>

          <div class="myoy">
            <span class="myoy-label">YoY vs ${yr-1}</span>
            <span class="myoy-val" style="${m.yoy != null ? (m.yoy >= 0 ? 'color:var(--good);' : 'color:var(--crit);') : 'color:var(--muted-soft);'}">
              ${m.yoy == null ? '—' : (m.yoy >= 0 ? '+' : '') + pct(m.yoy)}
            </span>
          </div>
        </div>

        <div class="mfoot">
          <button class="btn sm ${m.isCurrent ? 'pri' : ''} btn-go-month" data-month="${m.no}" style="width:100%;display:flex;justify-content:center;align-items:center;gap:6px;">
            ${m.isCurrent ? '👉 Buka Laporan September (Live)' : 'Lihat Laporan Bulanan ➔'}
          </button>
        </div>
      </div>
    `).join("")}
  </div>

  <!-- Tabel Lengkap Komparasi 12 Bulan -->
  <div class="card" style="margin-bottom:20px;">
    <h3>Matriks Komparasi 12 Bulan &amp; Momentum Permintaan</h3>
    <div class="tw"><table>
      <thead>
        <tr>
          <th>Bulan</th>
          <th>Status Verifikasi</th>
          <th class="n">Acuan ${yr-1}</th>
          <th class="n">Omzet ${yr}</th>
          <th class="n">YoY Growth</th>
          <th class="n">Seasonality</th>
          <th>Kategori Musim</th>
          <th>Momentum Bisnis &amp; Rekomendasi Aksi</th>
          <th>Aksi</th>
        </tr>
      </thead>
      <tbody>
        ${months.map(m => `
          <tr class="${m.isCurrent ? 'active-row' : ''}">
            <td><b>${m.label} ${yr}</b></td>
            <td><span class="pill ${m.statusPill}" style="font-size:10.5px;">${m.status}</span></td>
            <td class="n mono">${rp(m.omzet25)}</td>
            <td class="n mono" style="${m.isCurrent ? 'font-weight:700;color:var(--accent);' : 'color:var(--muted-soft);'}">${m.omzet26 != null ? rp(m.omzet26) : "—"}</td>
            <td class="n mono" style="${m.yoy != null ? (m.yoy >= 0 ? 'color:var(--good);' : 'color:var(--crit);') : 'color:var(--muted-soft);'}">${m.yoy == null ? '—' : (m.yoy >= 0 ? '+' : '') + pct(m.yoy)}</td>
            <td class="n mono"><b>${m.sIndex.toFixed(2)}×</b></td>
            <td><span class="pill ${m.seasonPill}" style="font-size:10px;">${m.seasonTag}</span></td>
            <td class="tiny"><b>${esc(m.momentum)}</b> — ${esc(m.note)}</td>
            <td><button class="btn sm btn-go-month" data-month="${m.no}" style="padding:2px 8px;font-size:11px;">Buka ➔</button></td>
          </tr>
        `).join("")}
        <tr class="total">
          <td colspan="2">TOTAL TAHUNAN</td>
          <td class="n mono">${rp(tot25)}</td>
          <td class="n mono" style="font-weight:700;color:var(--accent);">${rp(R.omzet)}*</td>
          <td class="n mono">—</td>
          <td class="n mono">1.00× avg</td>
          <td colspan="3" class="tiny">*Hanya September ${yr} yang telah terverifikasi live. 11 bulan lainnya dikosongkan karena menunggu pencocokan laporan riil.</td>
        </tr>
      </tbody>
    </table></div>
  </div>
  `;
}

function vOmzet(R){
  const run=R.days.filter(d=>d.berjalan);
  const maxO=Math.max(...run.map(d=>d.omzet||0))||1;
  const t1=R.tiers[0]?R.tiers[0].omzet:0;
  return `
  <div class="vhead"><div><div class="eyebrow">Sheet 2</div><h2>Omzet Harian &amp; Progresif</h2></div>
    <p>Batang menjawab hari mana yang ramai, kurva menjawab sudah sampai mana terhadap target — sumbu tanggalnya sama, jadi dibaca sekali. Tanggal setelah cut-off tetap tampil tanpa angka apa pun.</p></div>
  <div class="stats" style="margin-bottom:14px">
    <div class="stat"><span class="k">Total omzet</span><span class="v">${rp(R.omzet)}</span>
      <span class="m">${num(R.txPaid)} transaksi masuk dari ${num(R.tx)} order</span></div>
    <div class="stat"><span class="k">Cash</span><span class="v sm">${rp(R.cash)}</span>
      <span class="m">${R.omzet?pct(R.cash/R.omzet):"—"} dari omzet</span></div>
    <div class="stat"><span class="k">Transfer</span><span class="v sm">${rp(R.transfer)}</span>
      <span class="m">${R.omzet?pct(R.transfer/R.omzet):"—"} dari omzet</span></div>
    <div class="stat"><span class="k">Rata-rata / hari</span><span class="v sm">${rp(R.runRate)}</span>
      <span class="m">${R.hariBerjalan} hari berjalan</span></div>
    <div class="stat"><span class="k">Proyeksi ${R.dim} hari</span><span class="v sm">${rp(R.proyeksi)}</span>
      <span class="m">sisa ${R.dim-R.hariBerjalan} hari · run-rate, bukan jaminan</span></div>
    <div class="stat"><span class="k">Target 1</span><span class="v sm">${t1?pct(R.omzet/t1):"—"}</span>
      <span class="m">${rp(t1)}</span>
      ${t1?`<span class="bar"><i style="width:${Math.min(100,R.omzet/t1*100).toFixed(1)}%"></i></span>`:""}</div>
  </div>
  <div class="card" style="margin-bottom:14px">${chartGabung(R)}</div>
  <div class="tw"><table><thead><tr><th>Tgl</th><th>Hari</th><th class="n">Transaksi</th>
    <th class="n">Cash</th><th class="n">Transfer</th><th class="n">Omzet harian</th>
    <th class="n">Omzet progresif</th><th class="n">Growth vs hari lalu</th></tr></thead><tbody>
    ${R.days.map(d=>`<tr class="${d.berjalan?"":"future"}"><td class="mono">${d.d}</td><td>${d.hari}</td>
      ${d.berjalan?`<td class="n">${num(d.tx)}</td><td class="n">${rp(d.cash)}</td><td class="n">${rp(d.transfer)}</td>
        <td class="n heat"><i style="background:var(--accent);width:${((d.omzet||0)/maxO*100).toFixed(1)}%"></i>${rp(d.omzet)}</td>
        <td class="n" style="color:var(--accent-ink)">${rp(d.cum)}</td>
        <td class="n" style="color:${d.growth==null?"var(--muted)":d.growth>=0?"var(--good)":"var(--crit)"}">${d.growth==null?"—":(d.growth>=0?"+":"")+pct(d.growth)}</td>`
      :`<td class="n"></td><td class="n"></td><td class="n"></td><td class="n"></td><td class="n"></td><td class="n"></td>`}</tr>`).join("")}
    <tr class="total"><td colspan="2">Total s.d. ${R.cutDay} ${BULAN[+R.c.bulan.split("-")[1]-1]}</td>
      <td class="n">${num(R.tx)}</td><td class="n">${rp(R.cash)}</td><td class="n">${rp(R.transfer)}</td>
      <td class="n">${rp(R.omzet)}</td><td class="n">${rp(R.omzet)}</td>
      <td class="n muted">rata-rata ${rp(R.avgTx)}/tx</td></tr>
  </tbody></table></div>`;
}

function vTarget(R){
  const rows=R.tiers.map(t=>({...t,gap:Math.max(0,t.omzet-R.omzet),prog:R.omzet/t.omzet,
    pace:t.omzet/R.dim*R.hariBerjalan}));
  return `
  <div class="vhead"><div><div class="eyebrow">Sheet 12</div><h2>Target & Skenario</h2></div>
    <p>Aktual dibandingkan tiap tier, plus pace yang seharusnya sudah tercapai di hari ke-${R.hariBerjalan}.</p></div>
  <div class="stats" style="margin-bottom:14px">
    <div class="stat"><span class="k">Omzet aktual</span><span class="v">${rp(R.omzet)}</span></div>
    <div class="stat"><span class="k">Tier aktif</span><span class="v sm">${R.tierAktif?"Target "+R.tierAktif.tier:"Belum tercapai"}</span></div>
    <div class="stat"><span class="k">Bonus pool aktual</span><span class="v sm">${rp(R.pool)}</span></div>
    <div class="stat"><span class="k">Proyeksi ${R.dim} hari</span><span class="v sm">${rp(R.proyeksi)}</span>
      <span class="m">${R.tiers.filter(t=>R.proyeksi>=t.omzet).length?"lolos Target "+Math.max(...R.tiers.filter(t=>R.proyeksi>=t.omzet).map(t=>t.tier)):"belum lolos tier mana pun"}</span></div>
  </div>
  <div class="tw" style="margin-bottom:14px"><table><thead><tr><th>Tier</th><th class="n">Target omzet</th>
    <th class="n">Progress</th><th class="n">Gap</th><th class="n">Pace seharusnya</th><th class="n">vs pace</th>
    <th class="n">Bonus %</th><th class="n">Pool</th><th>Status</th></tr></thead><tbody>
    ${rows.map(t=>{const sel=R.omzet-t.pace;return `<tr>
      <td>Target ${t.tier}</td><td class="n">${rp(t.omzet)}</td>
      <td class="n"><div style="display:flex;align-items:center;gap:7px;justify-content:flex-end">
        <div style="width:56px;height:5px;background:var(--surface3);border-radius:3px;overflow:hidden">
          <i style="display:block;height:100%;width:${Math.min(100,t.prog*100).toFixed(1)}%;background:var(--accent)"></i></div>${pct(t.prog)}</div></td>
      <td class="n">${t.gap?rp(t.gap):"—"}</td><td class="n">${rp(t.pace)}</td>
      <td class="n" style="color:${sel>=0?"var(--good)":"var(--crit)"}">${(sel>=0?"+":"")+rp(sel)}</td>
      <td class="n">${pct(t.persen)}</td><td class="n">${rp(t.pool)}</td>
      <td>${R.omzet>=t.omzet?'<span class="pill final">tercapai</span>':`<span class="pill ${sel>=0?"neutral":"prog"}">${sel>=0?"di atas pace":"di bawah pace"}</span>`}</td></tr>`}).join("")}
  </tbody></table></div>
  <div class="card"><h3>Simulasi bonus per tier</h3>
    <p class="tiny muted" style="margin-bottom:10px">Memakai KPI operasional yang sudah dinilai. Referral dan posisi yang belum dinilai tetap 0.</p>
    <div class="tw"><table><thead><tr><th>Posisi</th><th>Nama</th><th class="n">Total KPI</th>
      ${R.tiers.map(t=>`<th class="n">Cair di T${t.tier}</th>`).join("")}</tr></thead><tbody>
      ${R.kpi.map(k=>`<tr><td>${esc(k.role||"—")}</td><td>${esc(k.nama)}</td>
        <td class="n">${k.dinilai?k.totalKPI.toFixed(1):'<span class="muted">belum dinilai</span>'}</td>
        ${R.tiers.map(t=>`<td class="n">${k.dinilai?rp(t.pool*k.bobot*(k.totalKPI/100)):rp(0)}</td>`).join("")}</tr>`).join("")}
      <tr class="total"><td colspan="3">Total cair</td>
        ${R.tiers.map(t=>`<td class="n">${rp(R.kpi.reduce((s,k)=>s+(k.dinilai?t.pool*k.bobot*(k.totalKPI/100):0),0))}</td>`).join("")}</tr>
    </tbody></table></div></div>`;
}

function vTrx(R){
  const pakets=[...new Set(S.orders.map(o=>npak(o.paket)).filter(Boolean))].sort();
  const admins=[...new Set(S.orders.map(o=>String(o.admin||"").toUpperCase()).filter(Boolean))].sort();
  const fgs=[...new Set(S.orders.map(o=>String(o.fotografer||"").toUpperCase()).filter(Boolean))].sort();
  const list=[...S.orders].sort((a,b)=>a.tanggal<b.tanggal?1:a.tanggal>b.tanggal?-1:0).slice(0,400);
  return `
  <div class="vhead"><div><div class="eyebrow">Sheet 1</div><h2>Log Transaksi</h2></div>
    <p>Cash dan transfer dipisah, total terisi otomatis. Order tanpa pembayaran tetap dicatat Rp0 dan ikut jumlah transaksi.</p></div>
  <div class="card" style="margin-bottom:14px"><h3>Tambah transaksi</h3>
    <form class="form" id="fTrx">
      <div class="f"><label>Tanggal setoran</label><input name="tanggal" type="date" value="${R.c.cutoff}" required></div>
      <div class="f wide"><label>Nama client</label><input name="client" required placeholder="Nama"></div>
      <div class="f"><label>Paket</label><input name="paket" list="dlPaket" placeholder="Graduation"></div>
      <div class="f"><label>Tanggal foto</label><input name="tanggalFoto" type="date"></div>
      <div class="f"><label>Cash</label><input name="cash" inputmode="numeric" placeholder="0"></div>
      <div class="f"><label>Transfer</label><input name="transfer" inputmode="numeric" placeholder="0"></div>
      <div class="f"><label>Admin</label><input name="admin" list="dlAdmin" placeholder="AMEL"></div>
      <div class="f"><label>Fotografer</label><input name="fotografer" list="dlFg" placeholder="SAKA"></div>
      <div class="f"><label>&nbsp;</label><button class="btn pri" type="submit">Simpan</button></div>
    </form>
    <datalist id="dlPaket">${pakets.map(p=>`<option value="${esc(p)}">`).join("")}</datalist>
    <datalist id="dlAdmin">${admins.map(p=>`<option value="${esc(p)}">`).join("")}</datalist>
    <datalist id="dlFg">${fgs.map(p=>`<option value="${esc(p)}">`).join("")}</datalist>
  </div>
  ${kartuPaket(R)}
  <div class="tw"><table><thead><tr><th>Tgl setoran</th><th>Client</th><th>Paket</th><th>Tgl foto</th>
    <th class="n">Cash</th><th class="n">Transfer</th><th class="n">Total</th><th>Metode</th><th>Admin</th><th>Fotografer</th><th></th></tr></thead><tbody>
    ${list.length?list.map(o=>{const c=dnum(o.cash),t=dnum(o.transfer);
      return `<tr><td class="mono">${esc(o.tanggal)}</td><td>${esc(o.client)}</td><td>${esc(npak(o.paket))||'<span class="muted">—</span>'}</td>
      <td class="mono muted">${esc(o.tanggalFoto||"—")}</td><td class="n">${c?rp(c):'<span class="muted">—</span>'}</td>
      <td class="n">${t?rp(t):'<span class="muted">—</span>'}</td>
      <td class="n"${c+t===0?' style="color:var(--warn)"':""}>${rp(c+t)}</td>
      <td class="muted tiny">${c&&t?"Cash + Transfer":c?"Cash":t?"Transfer":"—"}</td>
      <td>${esc(o.admin)||'<span class="muted">—</span>'}</td><td>${esc(o.fotografer)||'<span class="muted">—</span>'}</td>
      <td class="n"><button class="del" data-del="orders" data-id="${o.id}" aria-label="Hapus">✕</button></td></tr>`}).join("")
      :`<tr><td colspan="11"><div class="empty">Belum ada transaksi.</div></td></tr>`}
  </tbody></table></div>
  ${S.orders.length>400?`<p class="tiny muted" style="margin-top:8px">Menampilkan 400 transaksi terbaru dari ${num(S.orders.length)}.</p>`:""}`;
}

function kartuPaket(R){
  const sel=R.avgTx?(R.avgPaket-R.avgTx)/R.avgTx:0;
  const lain=R.pkTanpa.length+R.pkLuar.length;
  const nilaiLain=[...R.pkTanpa,...R.pkLuar].reduce((s,p)=>s+p.nilai,0);
  return `
  <div class="card" style="margin-bottom:14px">
    <h3>Paket vs pembayaran <span class="eyebrow">DP dipisah</span></h3>
    <p class="tiny muted" style="margin-bottom:12px">Log Order mencatat per pembayaran, bukan per paket.
      Paket yang di-DP lalu dilunasi muncul dua baris, jadi rata-rata per pembayaran
      selalu lebih rendah dari harga jual sebenarnya. Di bawah keduanya dipisah.</p>
    <div class="stats" style="margin-bottom:14px">
      <div class="stat"><span class="k">Rata-rata per pembayaran</span><span class="v sm">${rp(R.avgTx)}</span>
        <span class="m">${num(R.txPaid)} baris uang masuk</span></div>
      <div class="stat"><span class="k">Rata-rata nilai paket</span><span class="v sm">${rp(R.avgPaket)}</span>
        <span class="m">${num(R.paketTerlayani)} paket, sesi sudah jalan</span></div>
      <div class="stat"><span class="k">Selisih</span><span class="v sm">${sel>0?"+":""}${pct(sel)}</span>
        <span class="m">seberapa jauh angka lama meleset</span></div>
      <div class="stat"><span class="k">Paket pakai DP</span><span class="v sm">${num(R.paketPecah)}</span>
        <span class="m">${R.paketTerlayani?pct(R.paketPecah/R.paketTerlayani):"—"} dari paket terlayani</span></div>
    </div>

    <h4 class="eyebrow" style="margin:16px 0 7px">A · Per tanggal bayar — uang masuk</h4>
    <div class="tw"><table><thead><tr><th>Tgl</th><th class="n">Uang masuk</th><th class="n">Baris</th>
      <th class="n">Rata-rata</th><th class="n">Lunas</th><th class="n">DP</th><th class="n">Pelunasan</th>
      <th class="n">Nilai DP</th></tr></thead><tbody>
      ${R.days.filter(d=>d.berjalan).map(d=>`<tr>
        <td class="mono">${d.d} <span class="muted tiny">${d.hari}</span></td>
        <td class="n">${d.omzet?rp(d.omzet):'<span class="muted">—</span>'}</td>
        <td class="n">${num(d.txPaid)}</td>
        <td class="n">${d.txPaid?rp(d.avg):'<span class="muted">—</span>'}</td>
        <td class="n">${d.nLunas||'<span class="muted">—</span>'}</td>
        <td class="n">${d.nDP||'<span class="muted">—</span>'}</td>
        <td class="n">${d.nPelunasan||'<span class="muted">—</span>'}</td>
        <td class="n muted">${d.nilaiDP?rp(d.nilaiDP):"—"}</td></tr>`).join("")}
      <tr class="total"><td>Total</td><td class="n">${rp(R.omzet)}</td><td class="n">${num(R.txPaid)}</td>
        <td class="n">${rp(R.avgTx)}</td>
        <td class="n">${R.days.filter(d=>d.berjalan).reduce((s,d)=>s+d.nLunas,0)}</td>
        <td class="n">${R.days.filter(d=>d.berjalan).reduce((s,d)=>s+d.nDP,0)}</td>
        <td class="n">${R.days.filter(d=>d.berjalan).reduce((s,d)=>s+d.nPelunasan,0)}</td>
        <td class="n">${rp(R.days.filter(d=>d.berjalan).reduce((s,d)=>s+d.nilaiDP,0))}</td></tr>
    </tbody></table></div>

    <h4 class="eyebrow" style="margin:20px 0 7px">B · Per tanggal foto — nilai paket utuh</h4>
    <div class="tw"><table><thead><tr><th>Tgl foto</th><th class="n">Nilai paket</th><th class="n">Paket</th>
      <th class="n">Rata-rata</th><th class="n">Pakai DP</th><th>Status</th></tr></thead><tbody>
      ${R.sesi.length?R.sesi.map(s=>`<tr${s.lewat?"":' style="opacity:.6"'}>
        <td class="mono">${s.d} <span class="muted tiny">${s.hari}</span></td>
        <td class="n">${rp(s.nilai)}</td><td class="n">${num(s.paket)}</td>
        <td class="n">${rp(s.avg)}</td><td class="n">${s.pecah||'<span class="muted">—</span>'}</td>
        <td class="tiny ${s.lewat?"":"muted"}">${s.lewat?"sudah jalan":"belum jalan · baru DP"}</td></tr>`).join("")
        :`<tr><td colspan="6"><div class="empty">Belum ada paket.</div></td></tr>`}
      <tr class="total"><td>Sudah jalan</td><td class="n">${rp(R.nilaiLewat)}</td>
        <td class="n">${num(R.paketTerlayani)}</td><td class="n">${rp(R.avgPaket)}</td>
        <td class="n">${num(R.paketPecah)}</td><td></td></tr>
    </tbody></table></div>
  </div>`;
}

function vBiaya(R){
  const grup=(j,kats,extra)=>{const rows=kats.map(k=>({k,v:R.ex.filter(e=>e.kategori===k).reduce((s,e)=>s+dnum(e.nilai),0)}));
    if(extra)extra.forEach(x=>rows.push(x));
    const tot=rows.reduce((s,r)=>s+r.v,0);
    return `<div class="tw"><table><thead><tr><th>Kategori ${j}</th><th class="n">Total</th><th class="n">% omzet</th></tr></thead><tbody>
      ${rows.map(r=>`<tr><td>${r.k}</td><td class="n">${r.v?rp(r.v):'<span class="muted">—</span>'}</td>
        <td class="n muted">${r.v&&R.omzet?pct(r.v/R.omzet):""}</td></tr>`).join("")}
      <tr class="total"><td>Total ${j}</td><td class="n">${rp(tot)}</td><td class="n">${R.omzet?pct(tot/R.omzet):""}</td></tr>
    </tbody></table></div>`};
  return `
  <div class="vhead"><div><div class="eyebrow">Buku Neraca Keuangan · September 2026</div><h2>Neraca (COGS &amp; OPEX)</h2></div>
    <p>Laporan terpadu neraca Foxe Studio: klasifikasi otomatis COGS (beban produksi langsung) &amp; OPEX (operasional studio), mutasi kas &amp; bank harian, serta estimasi laba rugi.</p></div>

  <div class="stats" style="margin-bottom:14px">
    <div class="stat"><span class="k">Total COGS</span><span class="v sm">${rp(R.cogs)}</span><span class="m">${R.omzet?pct(R.cogs/R.omzet):""} dari omzet</span></div>
    <div class="stat"><span class="k">Gross profit</span><span class="v sm">${rp(R.grossProfit)}</span></div>
    <div class="stat"><span class="k">Total OPEX</span><span class="v sm">${rp(R.opex)}</span><span class="m">${R.omzet?pct(R.opex/R.omzet):""} dari omzet</span></div>
    <div class="stat"><span class="k">Nett profit</span><span class="v sm">${R.adaBiaya?rp(R.nettProfit):"—"}</span><span class="m">margin ${R.nettMargin==null?"—":pct(R.nettMargin)}</span></div>
  </div>
  ${R.belumKategori?`<div class="note warn" style="margin-bottom:14px">${R.belumKategori} biaya belum punya jenis dan kategori — belum ikut dihitung ke COGS atau OPEX. Baris kuning di tabel bawah.</div>`:""}
  <div class="card" style="margin-bottom:14px"><h3>Catat biaya</h3>
    <form class="form" id="fBiaya">
      <div class="f"><label>Tanggal</label><input name="tanggal" type="date" value="${R.c.cutoff}" required></div>
      <div class="f wide"><label>Deskripsi</label><input name="deskripsi" required placeholder="Sarapan crew wisuda"></div>
      <div class="f"><label>Jenis</label><select name="jenis" id="selJenis">
        <option value="">— pilih —</option><option>COGS</option><option>OPEX</option><option>LAINNYA</option><option>NON-P&L</option></select></div>
      <div class="f"><label>Kategori</label><select name="kategori" id="selKat"><option value="">— pilih jenis dulu —</option></select></div>
      <div class="f"><label>Vendor / penerima</label><input name="vendor" placeholder="opsional"></div>
      <div class="f"><label>Nilai</label><input name="nilai" inputmode="numeric" required placeholder="0"></div>
      <div class="f"><label>Skema</label><select name="skema"><option>Lunas</option><option>Termin</option></select></div>
      <div class="f"><label>Termin ke</label><input name="terminKe" inputmode="numeric" placeholder="—"></div>
      <div class="f"><label>Jatuh tempo</label><input name="jatuhTempo" type="date"></div>
      <div class="f"><label>Sudah dibayar</label><input name="nominalDibayar" inputmode="numeric" placeholder="0"></div>
      <div class="f"><label>&nbsp;</label><button class="btn pri" type="submit">Simpan</button></div>
    </form>
  </div>
  <div class="two" style="margin-bottom:14px">${grup("COGS",KAT_COGS)}${
      grup("OPEX",KAT_OPEX,R.kasbon?[{k:"Kasbon Karyawan",v:R.kasbon}]:null)}</div>
  <div class="tw"><table><thead><tr><th>Tgl</th><th>Deskripsi</th><th>Jenis</th><th>Kategori</th>
    <th class="n">Nilai</th><th>Status</th><th style="width:40px;text-align:center"></th></tr></thead><tbody>
    ${R.ex.length?[...R.ex].sort((a,b)=>(b.tanggal||"")<(a.tanggal||"")?-1:(b.tanggal||"")>(a.tanggal||"")?1:dnum(a.urutan)-dnum(b.urutan)).map(e=>{
      const n=dnum(e.nilai),b=dnum(e.nominalDibayar),sisa=n-b;
      const belum=!e.jenis||!e.kategori;
      return `<tr${belum?' style="background:var(--warn-bg)"':""}><td class="mono">${e.tanggal?esc(e.tanggal):'<span class="muted">—</span>'}</td>
      <td><div style="font-weight:500">${esc(e.deskripsi)}</div>${e.vendor?`<div class="tiny muted">Vendor: ${esc(e.vendor)}</div>`:""}${e.metode?`<span class="tiny muted" style="margin-top:2px;display:inline-block">${esc(e.metode)}</span>`:""}</td>
      <td>${e.jenis?`<span class="pill ${e.jenis==='COGS'?'neutral':e.jenis==='OPEX'?'neutral':'prog'}" style="font-weight:600;font-size:11px">${esc(e.jenis)}</span>`:'<span class="pill bad">belum</span>'}</td>
      <td class="tiny" style="color:var(--ink2)">${e.kategori?esc(e.kategori):'<span class="muted">belum</span>'}</td>
      <td class="n"><div style="font-weight:600">${rp(n)}</div>${sisa>0?`<div class="tiny" style="color:var(--warn)">Sisa ${rp(sisa)} (Dibayar ${rp(b)})</div>`:(e.skema==='Termin'?`<div class="tiny muted">Termin lunas</div>`:"")}</td>
      <td>${sisa<=0?'<span class="pill final">Lunas</span>':`<span class="pill prog">Sisa termin${e.terminKe?` #${esc(e.terminKe)}`:''}</span>`}</td>
      <td class="n" style="text-align:center"><button class="del" data-del="expenses" data-id="${e.id}" aria-label="Hapus">✕</button></td></tr>`}).join("")
      :`<tr><td colspan="7"><div class="empty">Belum ada biaya tercatat.</div></td></tr>`}
  </tbody></table></div>

  <!-- SECTION NERACA DEBIT KREDIT MENURUN SESUAI LOG TANGGAL -->
  <div class="vhead" style="margin-top:36px">
    <div>
      <div class="eyebrow">Section Detail · File Neraca Keuangan</div>
      <h2>Buku Detail Neraca (Debit &amp; Kredit)</h2>
    </div>
    <p>Rincian mutasi kas masuk (transfer/cash), pengeluaran riil per pos, dan running balance menurun per tanggal transaksi sesuai buku neraca resmi Foxe Studio.</p>
  </div>
  <div class="stats" style="margin-bottom:14px">
    <div class="stat">
      <span class="k">Total Saldo Masuk</span>
      <span class="v sm" style="color:var(--cash)">${rp(R.neracaSummary&&R.neracaSummary.total_masuk!=null?R.neracaSummary.total_masuk:R.neracaDetail.reduce((s,x)=>s+dnum(x.masuk),0))}</span>
      <span class="m">Debit Kas &amp; Bank</span>
    </div>
    <div class="stat">
      <span class="k">Total Saldo Keluar</span>
      <span class="v sm" style="color:var(--crit)">${rp(R.neracaSummary&&R.neracaSummary.total_keluar!=null?R.neracaSummary.total_keluar:R.neracaDetail.reduce((s,x)=>s+dnum(x.keluar),0))}</span>
      <span class="m">Kredit Beban Riil</span>
    </div>
    <div class="stat">
      <span class="k">Ending Balance</span>
      <span class="v sm" style="color:var(--accent)">${rp(R.neracaSummary&&R.neracaSummary.ending_balance!=null?R.neracaSummary.ending_balance:(R.neracaDetail.length?dnum(R.neracaDetail[R.neracaDetail.length-1].balance):0))}</span>
      <span class="m">Saldo Berjalan Terakhir</span>
    </div>
  </div>
  <div class="tw">
    <table>
      <thead>
        <tr style="background:var(--surface2)">
          <th style="width:65px;text-align:center">Tgl</th>
          <th class="n" style="color:var(--cash)">Saldo Masuk</th>
          <th class="n" style="color:var(--crit)">Saldo Keluar</th>
          <th class="n">Balance</th>
          <th>Ket. Masuk</th>
          <th>Ket. Keluar</th>
        </tr>
      </thead>
      <tbody>
        ${(R.neracaDetail||[]).length ? R.neracaDetail.map((d, i) => {
          const isNewDate = d.first_of_day;
          const borderStyle = (isNewDate && i > 0) ? 'style="border-top:1.5px solid var(--hairline-strong)"' : '';
          const dateCell = isNewDate 
            ? `<span class="pill neutral" style="font-weight:700;font-size:12px;min-width:32px;justify-content:center;background:var(--surface3)">${d.tgl}</span>`
            : `<span class="muted" style="font-size:11px;opacity:0.35">·</span>`;
          
          const masukFmt = d.masuk > 0 ? `<b style="color:var(--cash)">${rpc(d.masuk)}</b>` : `<span class="muted">—</span>`;
          const keluarFmt = d.keluar > 0 ? `<b style="color:var(--crit)">${rpc(d.keluar)}</b>` : `<span class="muted">—</span>`;
          const balFmt = d.balance > 0 ? `<span class="mono" style="font-weight:600">${rpc(d.balance)}</span>` : `<span class="muted">—</span>`;
          const badgeMasuk = d.ket_masuk ? `<span class="pill ${d.ket_masuk.toLowerCase().includes('cash')?'final':'neutral'}" style="font-size:11px">${esc(d.ket_masuk)}</span>` : `<span class="muted">—</span>`;
          const ketKeluar = d.ket_keluar ? `<span style="font-weight:500">${esc(d.ket_keluar)}</span>` : `<span class="muted">—</span>`;

          return `<tr ${borderStyle}>
            <td style="text-align:center">${dateCell}</td>
            <td class="n">${masukFmt}</td>
            <td class="n">${keluarFmt}</td>
            <td class="n">${balFmt}</td>
            <td>${badgeMasuk}</td>
            <td>${ketKeluar}</td>
          </tr>`;
        }).join("") : `<tr><td colspan="6"><div class="empty">Belum ada data detail neraca.</div></td></tr>`}
      </tbody>
      <tfoot>
        <tr class="total">
          <td style="text-align:center">Total</td>
          <td class="n" style="color:var(--cash)">${rp(R.neracaSummary&&R.neracaSummary.total_masuk!=null?R.neracaSummary.total_masuk:R.neracaDetail.reduce((s,x)=>s+dnum(x.masuk),0))}</td>
          <td class="n" style="color:var(--crit)">${rp(R.neracaSummary&&R.neracaSummary.total_keluar!=null?R.neracaSummary.total_keluar:R.neracaDetail.reduce((s,x)=>s+dnum(x.keluar),0))}</td>
          <td class="n" style="color:var(--accent)">${rp(R.neracaSummary&&R.neracaSummary.ending_balance!=null?R.neracaSummary.ending_balance:(R.neracaDetail.length?dnum(R.neracaDetail[R.neracaDetail.length-1].balance):0))}</td>
          <td>MTD Saldo Masuk</td>
          <td>MTD Saldo Keluar</td>
        </tr>
      </tfoot>
    </table>
  </div>`;
}


function vShift(R){
  const nama=[...new Set([...S.shifts.map(s=>String(s.nama).toUpperCase()),...R.admin.arr.map(a=>a.nama),...R.fotografer.arr.map(f=>f.nama)])].sort();
  const byDate=new Map();
  R.shiftDetail.forEach(s=>{const k=s.tanggal;if(!byDate.has(k))byDate.set(k,new Map());
    const m=byDate.get(k);const n=String(s.nama).toUpperCase();m.set(n,(m.get(n)||0)+dnum(s.slot))});
  const orang=R.shift.filter(s=>s.total>0).map(s=>s.nama);
  return `
  <div class="vhead"><div><div class="eyebrow">Sheet 5</div><h2>Rekap Shift</h2></div>
    <p>Satu slot tercatat sama dengan satu shift. Nama yang sama mengisi dua slot di hari yang sama dihitung dua shift, bukan satu.</p></div>
  <div class="two" style="margin-bottom:14px">
    <div class="card"><h3>Total shift per karyawan <span class="eyebrow">${num(R.shiftTot)} shift</span></h3>
      ${barlist(R.shift.filter(s=>s.total>0).map(s=>({k:s.nama,v:s.total,sub:pct(s.porsi)})),"accent",num)}</div>
    <div class="card"><h3>Tambah slot shift</h3>
      <form class="form" id="fShift">
        <div class="f"><label>Tanggal</label><input name="tanggal" type="date" value="${R.c.cutoff}" required></div>
        <div class="f"><label>Nama</label><input name="nama" list="dlNama" required placeholder="INDAH"></div>
        <div class="f"><label>Jumlah slot</label><input name="slot" inputmode="numeric" value="1" required></div>
        <div class="f"><label>&nbsp;</label><button class="btn pri" type="submit">Simpan</button></div>
      </form>
      <datalist id="dlNama">${nama.map(n=>`<option value="${esc(n)}">`).join("")}</datalist>
      ${R.offRoster.admin.length+R.offRoster.fotografer.length?`<div class="note warn" style="margin-top:11px">
        Menangani order tapi belum ada di slot shift: ${[...R.offRoster.admin,...R.offRoster.fotografer].map(x=>`<b>${esc(x.nama)}</b> (${x.n})`).join(", ")}. Tetap dihitung di analisis crew.</div>`:""}
    </div>
  </div>
  <div class="tw"><table><thead><tr><th>Tanggal</th><th>Hari</th>${orang.map(n=>`<th class="n">${esc(n)}</th>`).join("")}<th class="n">Total</th></tr></thead><tbody>
    ${R.days.map(d=>{const m=byDate.get(d.ds);
      if(!d.berjalan)return `<tr class="future"><td class="mono">${d.d}</td><td>${d.hari}</td>${orang.map(()=>`<td class="n"></td>`).join("")}<td class="n"></td></tr>`;
      const tot=orang.reduce((s,n)=>s+((m&&m.get(n))||0),0);
      return `<tr><td class="mono">${d.d}</td><td>${d.hari}</td>
        ${orang.map(n=>{const v=(m&&m.get(n))||0;
          return `<td class="n${v?"":" muted"}"${v>1?' style="font-weight:700;color:var(--accent)"':""}>${v||"—"}</td>`}).join("")}
        <td class="n">${tot||"—"}</td></tr>`}).join("")}
    <tr class="total"><td colspan="2">Total shift</td>
      ${orang.map(n=>`<td class="n">${num(R.shift.find(s=>s.nama===n).total)}</td>`).join("")}
      <td class="n">${num(R.shiftTot)}</td></tr>
  </tbody></table></div>`;
}

function vLead(R){
  const W=560,H=150,PL=44,PR=14,PT=12,PB=26;
  const rows=R.ld;
  let chart=`<div class="empty">Belum ada input lead.</div>`;
  if(rows.length){
    const max=niceMax(Math.max(...rows.map(r=>Math.max(dnum(r.leads),dnum(r.dp)))));
    const iw=W-PL-PR,ih=H-PT-PB,step=rows.length>1?iw/(rows.length-1):0;
    const xx=i=>PL+step*i, yy=v=>PT+ih-(v/max)*ih;
    let g="";for(let i=0;i<=3;i++){const v=max*i/3,y=yy(v);
      g+=`<line x1="${PL}" y1="${y.toFixed(1)}" x2="${W-PR}" y2="${y.toFixed(1)}" stroke="var(--grid)"/>
      <text x="${PL-7}" y="${(y+3.5).toFixed(1)}" text-anchor="end" font-size="9.5" font-family="JetBrains Mono,monospace" fill="var(--muted)">${num(v)}</text>`}
    const mk=(k,c)=>{const pts=rows.filter(r=>dnum(r[k])>0).map(r=>`${xx(rows.indexOf(r)).toFixed(1)},${yy(dnum(r[k])).toFixed(1)}`);
      return pts.length?`<polyline points="${pts.join(" ")}" fill="none" stroke="var(--${c})" stroke-width="2" stroke-linejoin="round"/>`
        +pts.map(p=>`<circle cx="${p.split(",")[0]}" cy="${p.split(",")[1]}" r="4" fill="var(--${c})" stroke="var(--surface)" stroke-width="2"/>`).join(""):""};
    const xl=rows.map((r,i)=>`<text x="${xx(i).toFixed(1)}" y="${H-PB+14}" text-anchor="middle" font-size="10" font-family="JetBrains Mono,monospace" fill="var(--muted)">${+r.tanggal.slice(8)}</text>`).join("");
    chart=`<div class="legend"><span><i class="swatch" style="background:var(--lead)"></i>Leads</span><span><i class="swatch" style="background:var(--dp)"></i>DP masuk</span></div>
      <svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="Leads dan DP harian">${g}${mk("leads","lead")}${mk("dp","dp")}${xl}</svg>`;
  }
  return `
  <div class="vhead"><div><div class="eyebrow">Sheet 10</div><h2>Lead Progresif</h2></div>
    <p>Hari yang punya DP tapi Leads kosong ditandai provisional — angka conversion tidak diisi dengan asumsi.</p></div>
  <div class="stats" style="margin-bottom:14px">
    <div class="stat"><span class="k">Total leads</span><span class="v">${R.totLeads?num(R.totLeads):"—"}</span></div>
    <div class="stat"><span class="k">Total DP</span><span class="v sm">${num(R.totDP)}</span></div>
    <div class="stat"><span class="k">Sesi foto</span><span class="v sm">${num(R.totSesi)}</span></div>
    <div class="stat"><span class="k">Conversion lead → DP</span><span class="v sm">${R.conv==null?"—":pct(R.conv)}</span>
      <span class="m">${R.leadKosong.length?"provisional":"lengkap"}</span></div>
  </div>
  ${R.leadKosong.length?`<div class="note warn" style="margin-bottom:14px">${R.leadKosong.length} hari punya DP masuk tapi Leads belum diisi (${R.leadKosong.map(l=>l.tanggal.slice(8)).join(", ")} ${BULAN[+R.c.bulan.split("-")[1]-1]}). Conversion di atas provisional sampai angka lead dilengkapi.</div>`:""}
  <div class="two" style="margin-bottom:14px">
    <div class="card">${chart}</div>
    <div class="card"><h3>Input lead harian</h3>
      <form class="form" id="fLead">
        <div class="f"><label>Tanggal</label><input name="tanggal" type="date" value="${R.c.cutoff}" required></div>
        <div class="f"><label>Leads</label><input name="leads" inputmode="numeric" placeholder="0"></div>
        <div class="f"><label>Total DP</label><input name="dp" inputmode="numeric" placeholder="0"></div>
        <div class="f"><label>Sesi foto</label><input name="sesiFoto" inputmode="numeric" placeholder="0"></div>
        <div class="f"><label>Transaksi</label><input name="transaksi" inputmode="numeric" placeholder="0"></div>
        <div class="f"><label>&nbsp;</label><button class="btn pri" type="submit">Simpan</button></div>
      </form>
      <p class="tiny muted" style="margin-top:9px">Input dengan tanggal yang sama akan menimpa data hari itu.</p>
      ${R.leadTerakhir?`<p class="tiny muted">Lead terakhir terisi: ${R.leadTerakhir.tanggal.slice(8)} ${BULAN[+R.c.bulan.split("-")[1]-1]} · coverage ${R.ld.filter(l=>dnum(l.leads)>0).length}/${R.hariBerjalan} hari.</p>`:""}
    </div>
  </div>
  ${blokIndeksHari(R)}
  <div class="tw"><table><thead><tr><th>Tanggal</th><th>Hari</th><th class="n">Leads</th><th class="n">DP</th>
    <th class="n">Sesi foto</th><th class="n">Transaksi</th><th class="n">Conversion</th><th class="n">Leads progresif</th><th>Status</th><th></th></tr></thead><tbody>
    ${R.days.map(d=>{const l=R.ld.find(x=>x.tanggal===d.ds);
      if(!d.berjalan)return `<tr class="future"><td class="mono">${d.d}</td><td>${d.hari}</td><td class="n"></td><td class="n"></td><td class="n"></td><td class="n"></td><td class="n"></td><td class="n"></td><td></td><td></td></tr>`;
      if(!l)return `<tr><td class="mono">${d.d}</td><td>${d.hari}</td><td colspan="6" class="muted tiny">belum diinput</td><td><span class="pill neutral">kosong</span></td><td></td></tr>`;
      const cum=R.ld.filter(x=>x.tanggal<=d.ds).reduce((s,x)=>s+dnum(x.leads),0);
      const lv=dnum(l.leads),dv=dnum(l.dp);
      return `<tr><td class="mono">${d.d}</td><td>${d.hari}</td>
        <td class="n">${lv||'<span class="muted">—</span>'}</td><td class="n">${num(dv)}</td>
        <td class="n">${num(dnum(l.sesiFoto))}</td><td class="n">${num(dnum(l.transaksi))}</td>
        <td class="n">${lv?pct(dv/lv):'<span class="muted">—</span>'}</td><td class="n">${num(cum)}</td>
        <td>${!lv&&dv?'<span class="pill prog">provisional</span>':'<span class="pill final">lengkap</span>'}</td>
        <td class="n"><button class="del" data-del="leads" data-id="${l.id}" aria-label="Hapus">✕</button></td></tr>`}).join("")}
  </tbody></table></div>`;
}

function vKpi(R){
  return `
  <div class="vhead"><div><div class="eyebrow">Sheet 9</div><h2>KPI & Bonus</h2></div>
    <p>Basic Point maksimal 5, In Jobdesk maksimal 15, KPI Operasional maksimal 20. Referral maksimal 80 sehingga Total KPI maksimal 100.</p></div>
  <div class="stats" style="margin-bottom:14px">
    <div class="stat"><span class="k">Rata-rata KPI operasional</span><span class="v sm">${R.avgOp==null?"—":pct(R.avgOp)}</span>
      <span class="m">${R.kpiDinilai.length} dari ${R.kpi.length} posisi dinilai</span></div>
    <div class="stat"><span class="k">Tier aktif</span><span class="v sm">${R.tierAktif?"Target "+R.tierAktif.tier:"Belum tercapai"}</span></div>
    <div class="stat"><span class="k">Bonus pool</span><span class="v sm">${rp(R.pool)}</span></div>
    <div class="stat"><span class="k">Bonus cair</span><span class="v sm">${rp(R.bonusCair)}</span>
      <span class="m">belum cair ${rp(R.pool-R.bonusCair)}</span></div>
  </div>
  <div class="card" style="margin-bottom:14px"><h3>Nilai KPI</h3>
    <p class="tiny muted" style="margin-bottom:9px">Skala 1–5 untuk tiap komponen. Nama yang sama akan menimpa penilaian sebelumnya.</p>
    <form class="form" id="fKpi">
      <div class="f"><label>Nama</label><input name="nama" required placeholder="INDAH"></div>
      <div class="f"><label>Posisi</label><input name="role" placeholder="Admin 2"></div>
      <div class="f"><label>Hari dinilai</label><input name="hariDinilai" inputmode="numeric" placeholder="4"></div>
      <div class="f"><label>Disiplin</label><input name="disiplin" inputmode="decimal" placeholder="5"></div>
      <div class="f"><label>Akurasi</label><input name="akurasi" inputmode="decimal" placeholder="5"></div>
      <div class="f"><label>SOP</label><input name="sop" inputmode="decimal" placeholder="5"></div>
      <div class="f"><label>Client</label><input name="client" inputmode="decimal" placeholder="5"></div>
      <div class="f"><label>Produktivitas</label><input name="produktivitas" inputmode="decimal" placeholder="5"></div>
      <div class="f"><label>Referral (max 80)</label><input name="referral" inputmode="decimal" placeholder="0"></div>
      <div class="f"><label>&nbsp;</label><button class="btn pri" type="submit">Simpan</button></div>
    </form>
  </div>
  <div class="tw" style="margin-bottom:14px"><table><thead><tr><th>Nama</th><th>Posisi</th><th class="n">Hari</th>
    <th class="n">Basic<br>max 5</th><th class="n">In Jobdesk<br>max 15</th><th class="n">Operasional<br>max 20</th>
    <th class="n">Op %</th><th class="n">Referral</th><th class="n">Total KPI</th><th class="n">Bonus max</th>
    <th class="n">Bonus cair</th><th></th></tr></thead><tbody>
    ${R.kpi.length?R.kpi.map(k=>k.dinilai?`<tr><td><b>${esc(k.nama)}</b></td><td class="tiny">${esc(k.role||"—")}</td>
      <td class="n">${num(dnum(k.hariDinilai))}</td><td class="n">${k.basic.toFixed(2)}</td><td class="n">${k.inJob.toFixed(2)}</td>
      <td class="n">${k.operasional.toFixed(2)}</td><td class="n">${pct(k.opPersen)}</td><td class="n">${num(k.referral)}</td>
      <td class="n">${k.totalKPI.toFixed(1)}</td><td class="n">${rp(k.bonusMax)}</td>
      <td class="n">${rp(k.bonusCair)}</td>
      <td class="n"><button class="del" data-del="kpi" data-id="${k.id}" aria-label="Hapus">✕</button></td></tr>`
      :`<tr><td><b>${esc(k.nama)}</b></td><td class="tiny">${esc(k.role||"—")}</td>
      <td colspan="7" class="muted tiny">Belum dinilai — bobot tetap dihitung di pool, bonus 0.</td>
      <td class="n">${rp(k.bonusMax)}</td><td class="n">${rp(0)}</td>
      <td class="n"><button class="del" data-del="kpi" data-id="${k.id}" aria-label="Hapus">✕</button></td></tr>`).join("")
      :`<tr><td colspan="12"><div class="empty">Belum ada posisi KPI.</div></td></tr>`}
    ${R.kpi.length?`<tr class="total"><td colspan="9">Total</td><td class="n">${rp(R.pool)}</td><td class="n">${rp(R.bonusCair)}</td><td></td></tr>`:""}
  </tbody></table></div>
  <div class="note">Basic Point = rata-rata Disiplin. In Jobdesk = rata-rata (Akurasi + SOP + Client + Produktivitas) × 3. KPI Operasional = Basic + In Jobdesk. Bonus cair = pool × bobot posisi × (Total KPI ÷ 100).</div>`;
}

function vCrew(R){
  return `
  <div class="vhead"><div><div class="eyebrow">Sheet 4</div><h2>Paket & Crew</h2></div>
    <p>Photo Fox dinormalisasi jadi Photofox. Nama yang menangani order tapi tidak ada di slot shift tetap dihitung, dan ditandai di catatan mutu data.</p></div>
  <div class="card" style="margin-bottom:14px"><h3>Urutan paket terlaris <span class="eyebrow">${num(R.paket.reduce((s,p)=>s+p.tx,0))} transaksi</span></h3>
    <div class="tw"><table><thead><tr><th>#</th><th>Paket</th><th class="n">Transaksi</th><th class="n">Porsi</th><th class="n">Total nilai</th><th class="n">Rata-rata</th></tr></thead><tbody>
      ${R.paket.map((p,i)=>{const tot=R.paket.reduce((s,x)=>s+x.tx,0);
        return `<tr><td class="mono muted">${i+1}</td><td>${esc(p.paket)}</td>
        <td class="n heat"><i style="background:var(--lead);width:${(p.tx/R.paket[0].tx*100).toFixed(1)}%"></i>${num(p.tx)}</td>
        <td class="n muted">${pct(p.tx/tot)}</td><td class="n">${rp(p.nilai)}</td>
        <td class="n muted">${rp(p.nilai/p.tx)}</td></tr>`}).join("")}
      <tr class="total"><td></td><td>Total</td><td class="n">${num(R.paket.reduce((s,p)=>s+p.tx,0))}</td><td class="n"></td>
        <td class="n">${rp(R.paket.reduce((s,p)=>s+p.nilai,0))}</td><td class="n"></td></tr>
    </tbody></table></div></div>
  <div class="two" style="margin-bottom:14px">
    <div class="card"><h3>Order per admin</h3>
      ${barlist(R.admin.arr.map(a=>({k:a.nama+(R.roster.has(a.nama)?"":" ·"),v:a.n,sub:pct(a.porsi)})),"accent",num)}
      ${R.admin.kosong?`<p class="tiny muted" style="margin-top:10px">${R.admin.kosong} order belum ada admin.</p>`:""}
      ${R.offRoster.admin.length?`<p class="tiny" style="margin-top:6px;color:var(--warn)">· tidak muncul di slot shift</p>`:""}
      <div class="tw" style="margin-top:11px"><table><thead><tr><th>Admin</th><th class="n">Order</th><th class="n">Porsi</th><th class="n">Nilai</th></tr></thead><tbody>
        ${R.admin.arr.map(a=>`<tr><td>${esc(a.nama)}</td><td class="n">${num(a.n)}</td><td class="n muted">${pct(a.porsi)}</td><td class="n">${rp(a.nilai)}</td></tr>`).join("")}
      </tbody></table></div></div>
    <div class="card"><h3>Assignment per fotografer</h3>
      ${barlist(R.fotografer.arr.map(f=>({k:f.nama+(R.roster.has(f.nama)?"":" ·"),v:f.n,sub:pct(f.porsi)})),"cash",num)}
      ${R.fotografer.kosong?`<p class="tiny muted" style="margin-top:10px">${R.fotografer.kosong} order tanpa fotografer — umumnya DP yang sesinya belum dijadwalkan.</p>`:""}
      <div class="tw" style="margin-top:11px"><table><thead><tr><th>Fotografer</th><th class="n">Assignment</th><th class="n">Porsi</th><th class="n">Nilai</th></tr></thead><tbody>
        ${R.fotografer.arr.map(f=>`<tr><td>${esc(f.nama)}</td><td class="n">${num(f.n)}</td><td class="n muted">${pct(f.porsi)}</td><td class="n">${rp(f.nilai)}</td></tr>`).join("")}
      </tbody></table></div></div>
  </div>
  <div class="card"><h3>Catatan mutu data</h3>
    <div class="tw"><table><thead><tr><th>Jenis</th><th class="n">Jumlah</th><th>Detail</th><th>Perlakuan</th></tr></thead><tbody>
      <tr><td>Admin belum diisi</td><td class="n">${num(R.admin.kosong)}</td><td class="tiny muted">order tanpa nama admin</td><td class="tiny">Tetap di log, belum dialokasikan.</td></tr>
      <tr><td>Fotografer belum diisi</td><td class="n">${num(R.fotografer.kosong)}</td><td class="tiny muted">umumnya DP tanpa jadwal sesi</td><td class="tiny">Tetap di log, belum dialokasikan.</td></tr>
      <tr><td>Admin di luar roster shift</td><td class="n">${num(R.offRoster.admin.reduce((s,x)=>s+x.n,0))}</td>
        <td class="tiny muted">${R.offRoster.admin.map(x=>esc(x.nama)+": "+x.n).join(", ")||"—"}</td><td class="tiny">Tetap dihitung sebagai handler order.</td></tr>
      <tr><td>Fotografer di luar roster shift</td><td class="n">${num(R.offRoster.fotografer.reduce((s,x)=>s+x.n,0))}</td>
        <td class="tiny muted">${R.offRoster.fotografer.map(x=>esc(x.nama)+": "+x.n).join(", ")||"—"}</td><td class="tiny">Tetap dihitung sebagai assignment.</td></tr>
      <tr><td>Transaksi Rp0</td><td class="n">${num(R.rp0)}</td><td class="tiny muted">order tercatat tanpa uang masuk</td><td class="tiny">Ikut jumlah transaksi, tidak menambah omzet.</td></tr>
    </tbody></table></div></div>`;
}

function vYoy(R){
  const b=R.baseline;
  const mn=BULAN[+R.c.bulan.split("-")[1]-1], yr=+R.c.bulan.split("-")[0];
  const H=(S.history&&S.history.months)||[];
  const bulanNo=+R.c.bulan.split("-")[1];

  if(!b) return `
  <div class="vhead"><div><div class="eyebrow">Sheet 11</div><h2>Perbandingan YoY</h2></div>
    <p>${mn} ${yr} dibandingkan ${mn} ${yr-1} saja. Bulan lain tidak boleh dipakai sebagai pengganti baseline.</p></div>
  <div class="note warn" style="margin-bottom:14px"><b>PENDING BASELINE.</b> Data ${mn} ${yr-1} belum dimuat, jadi YoY belum dihitung.</div>
  ${formBaseline(b,mn,yr)}`;

  const ytd=t=>H.filter(m=>m.tahun===t&&m.no<bulanNo).reduce((s,m)=>s+dnum(m.omzet),0);
  const y25=ytd(yr-1), y26=ytd(yr);
  const ytdG=y25?(y26-y25)/y25:null;
  const proy=R.proyeksi, bo=dnum(b.omzet);
  const proyG=bo?(proy-bo)/bo:null;
  const harapan=ytdG!=null?bo*(1+ytdG):null;

  const pend=(k,then)=>`<tr><td>${k}</td><td class="n">${rp(then)}</td>
    <td class="n"><span class="muted">belum dikategorikan</span></td><td class="n muted">—</td></tr>`;
  const cmp=(k,now,then,fmt)=>{const g=(then&&then!==0)?(now-then)/then:null;
    return `<tr><td>${k}</td><td class="n">${then==null?'<span class="muted">pending</span>':fmt(then)}</td>
      <td class="n">${fmt(now)}</td>
      <td class="n" style="color:${g==null?"var(--muted)":g>=0?"var(--good)":"var(--crit)"}">${
        g==null?"—":(g>=0?"+":"")+pct(g)}</td></tr>`};

  return `
  <div class="vhead"><div><div class="eyebrow">Sheet 11</div><h2>Perbandingan YoY</h2></div>
    <p>${mn} ${yr} dibandingkan ${mn} ${yr-1} saja. Bulan lain tidak boleh dipakai sebagai pengganti baseline.</p></div>

  <div class="note warn" style="margin-bottom:14px"><b>${mn} ${yr} baru berjalan ${R.hariBerjalan} dari ${R.dim} hari.</b>
    Membandingkan ${rp(R.omzet)} dengan ${rp(bo)} sebulan penuh akan menyesatkan. Yang setara saat ini ada dua:
    <b>YTD Januari–${BULAN[bulanNo-2]}</b> (bulan penuh di kedua tahun) dan <b>proyeksi run-rate</b> terhadap aktual tahun lalu.</div>

  <div class="stats" style="margin-bottom:14px">
    <div class="stat"><span class="k">${mn} ${yr-1} aktual</span><span class="v">${rp(bo)}</span>
      <span class="m">${num(dnum(b.txPaid))} transaksi · ${rp(bo/R.dim)}/hari</span></div>
    <div class="stat"><span class="k">${mn} ${yr} s.d. ${R.cutDay}</span><span class="v sm">${rp(R.omzet)}</span>
      <span class="m">${rp(R.runRate)}/hari</span></div>
    <div class="stat"><span class="k">Proyeksi vs tahun lalu</span>
      <span class="v sm" style="color:${proyG>=0?"var(--good)":"var(--crit)"}">${(proyG>=0?"+":"")+pct(proyG)}</span>
      <span class="m">proyeksi ${rp(proy)}</span></div>
    <div class="stat"><span class="k">YTD Jan–${BULAN[bulanNo-2]}</span>
      <span class="v sm" style="color:${ytdG>=0?"var(--good)":"var(--crit)"}">${ytdG==null?"—":(ytdG>=0?"+":"")+pct(ytdG)}</span>
      <span class="m">${rp(y26)} vs ${rp(y25)}</span></div>
  </div>

  ${b.seasonalityStatus?`<div class="note ok" style="margin-bottom:14px">
    <b>${mn} adalah bulan puncak.</b> Tahun ${yr-1} bulan ini mencatat indeks musiman ${(+b.seasonalityIndex).toFixed(2)}×
    rata-rata (${esc(b.seasonalityStatus)}, peringkat ${b.seasonalityRank} dari 12) — didorong musim wisuda.
    Jadi angka ${mn} memang wajar jauh di atas bulan lain, dan target bulan ini pantas lebih tinggi.</div>`:""}

  ${(()=>{const t3=R.tiers[R.tiers.length-1];
    if(!t3||t3.omzet>=bo)return "";
    return `<div class="note crit" style="margin-bottom:14px">
      <b>Target bulan ini di bawah realisasi tahun lalu.</b> Target ${t3.tier} sebesar ${rp(t3.omzet)}
      hanya ${pct(t3.omzet/bo)} dari ${mn} ${yr-1} yang mencapai ${rp(bo)}.
      Kalau target ini yang dipakai menghitung bonus, tier tertinggi bisa tercapai
      sambil omzet tetap turun ${pct(1-t3.omzet/bo)} dibanding tahun lalu. Perlu ditinjau di Pengaturan.</div>`})()}

  ${H.length?`<div class="card" style="margin-bottom:14px">
    <h3>Omzet bulanan ${yr-1} vs ${yr}</h3>${chartYoY(R,H,yr)}</div>`:""}

  <div class="tw" style="margin-bottom:14px"><table><thead><tr><th>Metrik</th>
    <th class="n">${mn} ${yr-1}<br><span class="muted">${R.dim} hari</span></th>
    <th class="n">${mn} ${yr}<br><span class="muted">s.d. ${R.cutDay}</span></th>
    <th class="n">Selisih</th></tr></thead><tbody>
    ${cmp("Omzet",R.omzet,bo,rp)}
    ${cmp("Transaksi",R.txPaid,dnum(b.txPaid),num)}
    ${cmp("Average transaction",R.avgTx,dnum(b.txPaid)?bo/dnum(b.txPaid):null,rp)}
    ${cmp("Cash",R.cash,dnum(b.cash),rp)}
    ${cmp("Transfer",R.transfer,dnum(b.transfer),rp)}
    ${b.cogs?(R.adaBiaya?cmp("COGS",R.cogs,dnum(b.cogs),rp):pend("COGS",dnum(b.cogs))):""}
    ${b.opex?(R.adaBiaya?cmp("OPEX",R.opex,dnum(b.opex),rp):pend("OPEX",dnum(b.opex))):""}
    ${b.nettProfit?(R.adaBiaya?cmp("Nett profit",R.nettProfit,dnum(b.nettProfit),rp)
      :pend("Nett profit",dnum(b.nettProfit))):""}
    <tr class="total"><td>Proyeksi ${R.dim} hari</td><td class="n">${rp(bo)}</td>
      <td class="n">${rp(proy)}</td>
      <td class="n" style="color:${proyG>=0?"var(--good)":"var(--crit)"}">${(proyG>=0?"+":"")+pct(proyG)}</td></tr>
  </tbody></table></div>

  ${harapan?`<div class="note" style="margin-bottom:14px">Kalau ${mn} mengikuti tren YTD (${(ytdG>=0?"+":"")+pct(ytdG)}),
    omzet bulan ini kira-kira mendarat di <b>${rp(harapan)}</b>. Pace sekarang mengarah ke ${rp(proy)} —
    ${proy>=harapan?"di atas":"sekitar "+pct(1-proy/harapan)+" di bawah"} perkiraan itu.</div>`:""}

  ${formBaseline(b,mn,yr)}

  <div class="card"><h3>Status kelengkapan baseline</h3>
    <div class="tw"><table><thead><tr><th>Kebutuhan</th><th>Periode</th><th>Dipakai untuk</th><th>Status</th></tr></thead><tbody>
      <tr><td>Omzet &amp; transaksi ${mn} ${yr-1}</td><td class="tiny muted">1–${R.dim} ${mn} ${yr-1}</td>
        <td class="tiny">YoY omzet</td><td><span class="pill final">Ada</span></td></tr>
      <tr><td>COGS/OPEX ${mn} ${yr-1}</td><td class="tiny muted">${mn} ${yr-1}</td>
        <td class="tiny">Profitability YoY</td><td>${b.cogs?'<span class="pill final">Ada</span>':'<span class="pill prog">Pending</span>'}</td></tr>
      <tr><td>Riwayat bulanan</td><td class="tiny muted">Jan ${yr-1} – ${BULAN[bulanNo-2]} ${yr}</td>
        <td class="tiny">YTD &amp; grafik bulanan</td><td>${H.length?`<span class="pill final">${H.length} bulan</span>`:'<span class="pill prog">Pending</span>'}</td></tr>
      <tr><td>Paket ${mn} ${yr-1}</td><td class="tiny muted">${mn} ${yr-1}</td>
        <td class="tiny">Portfolio YoY</td><td><span class="pill prog">Pending</span></td></tr>
    </tbody></table></div>
  </div>`;
}

function formBaseline(b,mn,yr){
  return `<div class="card" style="margin-bottom:14px"><h3>Baseline ${mn} ${yr-1}</h3>
    <form class="form" id="fBase">
      <div class="f"><label>Omzet</label><input name="omzet" inputmode="numeric" value="${b?dnum(b.omzet):""}"></div>
      <div class="f"><label>Transaksi</label><input name="txPaid" inputmode="numeric" value="${b?dnum(b.txPaid):""}"></div>
      <div class="f"><label>Cash</label><input name="cash" inputmode="numeric" value="${b?dnum(b.cash):""}"></div>
      <div class="f"><label>Transfer</label><input name="transfer" inputmode="numeric" value="${b?dnum(b.transfer):""}"></div>
      <div class="f"><label>COGS</label><input name="cogs" inputmode="numeric" value="${b?dnum(b.cogs):""}"></div>
      <div class="f"><label>OPEX</label><input name="opex" inputmode="numeric" value="${b?dnum(b.opex):""}"></div>
      <div class="f"><label>&nbsp;</label><button class="btn pri" type="submit">Simpan baseline</button></div>
    </form>
    ${b&&b.sumber?`<p class="tiny muted" style="margin-top:9px">Sumber: ${esc(b.sumber)}</p>`:""}
  </div>`;
}

function chartYoY(R,H,yr){
  const W=760,H2=220,PL=64,PR=14,PT=16,PB=34;
  const prev=yr-1;
  const rows=BULAN.map((nm,i)=>({no:i+1,nm,
    a:(H.find(m=>m.tahun===prev&&m.no===i+1)||{}).omzet,
    b:(H.find(m=>m.tahun===yr&&m.no===i+1)||{}).omzet}));
  const cur=+R.c.bulan.split("-")[1];
  rows.forEach(r=>{if(r.no===cur)r.b=R.proyeksi});
  const max=niceMax(Math.max(...rows.flatMap(r=>[dnum(r.a),dnum(r.b)])));
  const iw=W-PL-PR, ih=H2-PT-PB, step=iw/12, bw=Math.min(11,step*.34);
  const yy=v=>PT+ih-(v/max)*ih;
  let g="";
  for(let i=0;i<=4;i++){const v=max*i/4,y=yy(v);
    g+=`<line x1="${PL}" y1="${y.toFixed(1)}" x2="${W-PR}" y2="${y.toFixed(1)}" stroke="var(--grid)"/>
    <text x="${PL-8}" y="${(y+3.5).toFixed(1)}" text-anchor="end" font-size="9.5" font-family="JetBrains Mono,monospace" fill="var(--muted)">${v>=1e6?(v/1e6).toFixed(0)+"jt":num(v)}</text>`}
  let bars="";
  rows.forEach((r,i)=>{
    const cx=PL+step*i+step/2;
    if(dnum(r.a)>0){const h=(dnum(r.a)/max)*ih;
      bars+=`<rect x="${(cx-bw-1).toFixed(1)}" y="${yy(dnum(r.a)).toFixed(1)}" width="${bw.toFixed(1)}" height="${h.toFixed(1)}" rx="2" fill="var(--hairline-strong)"/>`}
    if(dnum(r.b)>0){const h=(dnum(r.b)/max)*ih;
      bars+=`<rect x="${(cx+1).toFixed(1)}" y="${yy(dnum(r.b)).toFixed(1)}" width="${bw.toFixed(1)}" height="${h.toFixed(1)}" rx="2" fill="var(--accent)"${r.no===cur?' opacity=".55" stroke="var(--accent)" stroke-width="1" stroke-dasharray="2 2"':''}/>`}
    bars+=`<text x="${cx.toFixed(1)}" y="${H2-PB+14}" text-anchor="middle" font-size="9.5" font-family="JetBrains Mono,monospace" fill="${r.no===cur?"var(--ink)":"var(--muted)"}">${r.nm.slice(0,3)}</text>`;
  });
  const s=rows[cur-1];
  if(s&&dnum(s.a)>0)bars+=`<text x="${(PL+step*(cur-1)+step/2).toFixed(1)}" y="${(yy(dnum(s.a))-6).toFixed(1)}" text-anchor="middle" font-size="10" font-weight="600" font-family="JetBrains Mono,monospace" fill="var(--ink)">${(dnum(s.a)/1e6).toFixed(0)}jt</text>`;
  return `<div class="legend"><span><i class="swatch" style="background:var(--hairline-strong)"></i>${prev} aktual</span>
    <span><i class="swatch" style="background:var(--accent)"></i>${yr} aktual</span>
    <span class="muted">batang ${BULAN[cur-1]} ${yr} = proyeksi run-rate</span></div>
  <svg class="chart" viewBox="0 0 ${W} ${H2}" role="img" aria-label="Omzet bulanan ${prev} dibanding ${yr}">${g}${bars}</svg>`;
}

function vAds(R){
  const A=S.ads&&S.ads.bulan===R.c.bulan?S.ads:null;
  const mn=BULAN[+R.c.bulan.split("-")[1]-1], yr=R.c.bulan.split("-")[0];
  if(!A) return `
  <div class="vhead"><div><div class="eyebrow">Marketing</div><h2>Jadwal Ads</h2></div>
    <p>Rencana ads untuk bulan berjalan.</p></div>
  <div class="card"><div class="empty">Belum ada rencana ads untuk ${mn} ${yr}.<br>
    <span class="tiny">Sistem hanya menampilkan bulan yang sedang berjalan.</span></div></div>`;

  const now=new Date(), todayIso=iso(now);
  const terpakai=A.schedule.filter(s=>s.tanggal<=todayIso).reduce((t,s)=>t+dnum(s.term),0);
  const sisa=dnum(A.termPlan)-terpakai;
  const ceiling=dnum(A.budgetCeiling), plan=dnum(A.termPlan)*dnum(A.termSize);

  const status=s=>{
    const akhir=s.akhir||s.tanggal2||s.tanggal;
    if(todayIso>akhir)return {t:"Sudah lewat",c:"neutral"};
    if(todayIso>=s.tanggal)return {t:"Sedang berjalan",c:"prog"};
    return {t:"Akan datang",c:"final"};
  };
  const sisaJadwal=A.schedule.filter(s=>todayIso<=(s.akhir||s.tanggal2||s.tanggal));

  return `
  <div class="vhead"><div><div class="eyebrow">Marketing · ${mn} ${yr}</div><h2>Jadwal Ads</h2></div>
    <p>Rencana pelepasan budget dan langkah yang harus dijalankan tim. Hanya bulan berjalan yang ditampilkan.</p></div>

  <div class="note ok" style="margin-bottom:14px"><b>Budget bulan ini bukan untuk bulan ini.</b>
    Menurut rencanamu sendiri, ads ${mn} dipakai membangun demand <b>${esc(A.adsUntukDemand)}</b> —
    ${esc(A.momentum)}. Jadi ukuran keberhasilannya bukan omzet ${mn}, melainkan lead dan DP yang masuk untuk bulan depan.</div>

  <div class="stats" style="margin-bottom:14px">
    <div class="stat"><span class="k">Ceiling bulan ini</span><span class="v sm">${rp(ceiling)}</span>
      <span class="m">rencana ${rp(plan)} · reserve ${rp(ceiling-plan)}</span></div>
    <div class="stat"><span class="k">Term terpakai</span><span class="v sm">${terpakai} / ${A.termPlan}</span>
      <span class="m">${rp(terpakai*dnum(A.termSize))} dari ${rp(plan)}</span>
      <div class="bar"><i style="width:${(terpakai/dnum(A.termPlan)*100).toFixed(0)}%"></i></div></div>
    <div class="stat"><span class="k">Sisa term</span><span class="v sm">${sisa}</span>
      <span class="m">${rp(sisa*dnum(A.termSize))} belum dilepas</span></div>
    <div class="stat"><span class="k">Seasonality</span><span class="v sm">${esc(A.seasonality)}</span>
      <span class="m">1 term = ${rp(A.termSize)}</span></div>
  </div>

  ${sisaJadwal.length?`<div class="card" style="margin-bottom:14px">
    <h3>Yang belum dikerjakan <span class="eyebrow">${sisaJadwal.length} jadwal tersisa</span></h3>
    <div class="grid" style="gap:9px">
    ${sisaJadwal.map(s=>{const st=status(s);
      return `<div style="display:flex;gap:11px;align-items:flex-start;padding:10px 12px;background:var(--surface2);border-radius:7px;border-left:2px solid var(--${st.c==="prog"?"warn":"accent"})">
        <div style="min-width:96px"><div style="font-weight:600;font-size:13.5px">${esc(s.label)}</div>
          <span class="pill ${st.c}" style="margin-top:3px">${st.t}</span></div>
        <div style="flex:1;min-width:0">
          <div style="font-weight:600;font-size:13px">${s.action?esc(s.action):'<span style="color:var(--warn)">Action belum ditentukan</span>'}</div>
          <div class="tiny muted">${dnum(s.term)} term · ${rp(dnum(s.term)*dnum(A.termSize))}${
            s.catatan?" · "+esc(s.catatan):""}</div>
        </div></div>`}).join("")}
    </div></div>`:`<div class="note" style="margin-bottom:14px">Seluruh jadwal ads ${mn} sudah lewat.</div>`}

  <div class="tw" style="margin-bottom:14px"><table><thead><tr><th>Tanggal</th><th>Action</th>
    <th class="n">Term</th><th class="n">Budget</th><th>Status</th><th>Catatan</th></tr></thead><tbody>
    ${A.schedule.map(s=>{const st=status(s);
      return `<tr><td class="mono">${esc(s.label)}</td>
      <td>${s.action?esc(s.action):'<span class="pill bad">belum diisi</span>'}</td>
      <td class="n">${dnum(s.term)}</td><td class="n">${rp(dnum(s.term)*dnum(A.termSize))}</td>
      <td><span class="pill ${st.c}">${st.t}</span></td>
      <td class="tiny muted">${s.turunan?"angka turunan":""}</td></tr>`}).join("")}
    <tr class="total"><td colspan="2">Total rencana</td><td class="n">${A.termPlan}</td>
      <td class="n">${rp(plan)}</td><td colspan="2" class="tiny">ceiling ${rp(ceiling)}</td></tr>
  </tbody></table></div>

  <div class="card" style="margin-bottom:14px"><h3>Langkah tiap jenis action</h3>
    <div class="two">
    ${A.playbook.map(p=>`<div style="background:var(--surface2);border-radius:8px;padding:13px 15px">
      <div style="display:flex;justify-content:space-between;align-items:baseline;gap:8px;margin-bottom:3px">
        <b style="font-size:13.5px">${esc(p.action)}</b>
        <span class="eyebrow">${esc(p.kapan)}</span></div>
      <ol style="margin:9px 0 0;padding-left:17px;font-size:12.5px;line-height:1.65;color:var(--ink2)">
        ${p.langkah.map(l=>`<li>${esc(l)}</li>`).join("")}</ol>
      <p class="tiny muted" style="margin-top:9px"><b>Ukur:</b> ${esc(p.ukur)}</p>
    </div>`).join("")}
    </div>
  </div>`;
}

function hitungBooking(R){
  const S1=S.schedule&&S.schedule.bulan===R.c.bulan?S.schedule:null;
  if(!S1)return null;
  const byND={},byN={};
  S.orders.forEach(o=>{const k=nkey(o.client);if(!k)return;
    if(o.tanggalFoto) byND[k+"|"+o.tanggalFoto]=(byND[k+"|"+o.tanggalFoto]||0)+dnum(o.total);
    else byN[k]=(byN[k]||0)+dnum(o.total);});
  const bk=(S1.bookings||[]).map(b=>{
    const k=nkey(b.nama), bayar=(byND[k+"|"+b.tgl]||0)+(byN[k]||0);
    const dp=Math.min(dnum(b.harga),bayar);
    return {...b,dp,sisa:Math.max(0,dnum(b.harga)-dp),cocok:bayar>0,
      lewat:b.tgl<=R.c.cutoff};
  });
  const fut=bk.filter(b=>!b.lewat), sudah=bk.filter(b=>b.lewat);
  const estimasi=fut.reduce((s,b)=>s+b.sisa,0);
  const kotor=fut.reduce((s,b)=>s+dnum(b.harga),0);
  const dpTot=fut.reduce((s,b)=>s+b.dp,0);

  const perTgl=R.days.map(d=>{
    const bs=bk.filter(b=>b.tgl===d.ds);
    return {...d, booking:bs.length,
      nilai:d.berjalan?d.omzet:bs.reduce((s,b)=>s+b.sisa,0),
      future:d.berjalan?0:bs.reduce((s,b)=>s+b.sisa,0),
      sumber:d.berjalan?"Log Order":(bs.length?"Schedule":"—"),
      status:d.berjalan?"REALIZED":"ESTIMATE"};
  });
  let cum=0; perTgl.forEach(t=>{cum+=t.nilai;t.cum=cum;});

  const pm={};
  fut.forEach(b=>{const p=b.paket||"(tanpa paket)";
    (pm[p]=pm[p]||{paket:p,n:0,est:0,kotor:0}); pm[p].n++; pm[p].est+=b.sisa; pm[p].kotor+=dnum(b.harga);});
  const paket=Object.values(pm).sort((a,b)=>b.est-a.est||b.n-a.n);

  return {sumber:S1.sumber,bk,fut,sudah,estimasi,kotor,dpTot,perTgl,paket,
    total:R.omzet+estimasi, cocok:fut.filter(b=>b.cocok).length};
}

function vEst(R){
  const B=hitungBooking(R);
  const mn=BULAN[+R.c.bulan.split("-")[1]-1], yr=R.c.bulan.split("-")[0];
  if(!B) return `
  <div class="vhead"><div><div class="eyebrow">Forward-looking</div><h2>Estimasi Omzet</h2></div>
    <p>Nilai booking yang sudah terjadwal tapi belum masuk kas.</p></div>
  <div class="card"><div class="empty">Belum ada data schedule untuk ${mn} ${yr}.</div></div>`;

  const maxN=Math.max(1,...B.perTgl.map(t=>t.nilai||0));
  const selisih=R.proyeksi-B.total;

  return `
  <div class="vhead"><div><div class="eyebrow">Forward-looking · ${mn} ${yr}</div><h2>Estimasi Omzet</h2></div>
    <p>Berapa yang sudah terkunci di jadwal tapi belum masuk kas. Harga paket dikurangi DP yang sudah dibayar.</p></div>

  <div class="stats" style="margin-bottom:14px">
    <div class="stat"><span class="k">Realized s.d. ${R.cutDay} ${mn}</span><span class="v">${rp(R.omzet)}</span>
      <span class="m">dari Log Order</span></div>
    <div class="stat"><span class="k">Belum masuk</span><span class="v sm">${rp(B.estimasi)}</span>
      <span class="m">${B.fut.length} booking terjadwal</span></div>
    <div class="stat"><span class="k">Cash in updated</span><span class="v sm">${rp(B.total)}</span>
      <span class="m">realized + booking</span>
      <div class="bar"><i style="width:${(R.omzet/B.total*100).toFixed(0)}%"></i></div></div>
    <div class="stat"><span class="k">Porsi sudah masuk</span><span class="v sm">${pct(R.omzet/B.total)}</span>
      <span class="m">sisanya ${pct(B.estimasi/B.total)} masih di jadwal</span></div>
  </div>

  <div class="note ok" style="margin-bottom:14px"><b>Ini lantai, bukan ramalan.</b>
    ${rp(B.total)} adalah yang <b>sudah pasti</b> — uang yang sudah masuk plus sesi yang sudah dibooking.
    Booking baru akan terus datang sepanjang bulan, jadi angka akhir hampir pasti di atas ini.
    Bandingkan dengan proyeksi run-rate ${rp(R.proyeksi)}: selisih <b>${rp(Math.abs(selisih))}</b>
    itulah yang masih harus dijual dalam ${R.dim-R.hariBerjalan} hari tersisa untuk mengejar pace.</div>

  <div class="two" style="margin-bottom:14px">
    <div class="card"><h3>Nilai booking belum masuk</h3>
      <div class="tw"><table><tbody>
        <tr><td>Harga paket penuh</td><td class="n">${rp(B.kotor)}</td></tr>
        <tr><td>Dikurangi DP yang sudah dibayar</td><td class="n" style="color:var(--crit)">− ${rp(B.dpTot)}</td></tr>
        <tr class="total"><td>Estimasi masuk</td><td class="n">${rp(B.estimasi)}</td></tr>
      </tbody></table></div>
      <p class="tiny muted" style="margin-top:9px">${B.cocok} dari ${B.fut.length} booking ketemu padanannya
        di Log Order lewat nama client.</p></div>
    <div class="card"><h3>Per paket <span class="eyebrow">booking belum masuk</span></h3>
      <div class="tw"><table><thead><tr><th>Paket</th><th class="n">Booking</th>
        <th class="n">Estimasi</th><th class="n">Porsi</th></tr></thead><tbody>
        ${B.paket.map(p=>`<tr><td>${esc(p.paket)}</td><td class="n">${num(p.n)}</td>
          <td class="n heat"><i style="background:var(--accent);width:${(p.est/(B.paket[0].est||1)*100).toFixed(1)}%"></i>${rp(p.est)}</td>
          <td class="n muted">${pct(B.estimasi?p.est/B.estimasi:0)}</td></tr>`).join("")}
        <tr class="total"><td>Total</td><td class="n">${num(B.fut.length)}</td>
          <td class="n">${rp(B.estimasi)}</td><td class="n"></td></tr>
      </tbody></table></div></div>
  </div>

  <div class="tw" style="margin-bottom:14px"><table><thead><tr><th>Tanggal</th><th>Hari</th>
    <th class="n">Booking</th><th class="n">Cash in</th><th class="n">Kumulatif</th>
    <th>Sumber</th><th>Status</th><th class="n">Belum masuk</th></tr></thead><tbody>
    ${B.perTgl.map(t=>`<tr class="${t.berjalan?"":"future"}">
      <td class="mono">${t.d}</td><td>${t.hari}</td>
      <td class="n">${t.booking||'<span class="muted">—</span>'}</td>
      <td class="n heat">${t.nilai?`<i style="background:var(--${t.berjalan?"cash":"accent"});width:${(t.nilai/maxN*100).toFixed(1)}%"></i>${rp(t.nilai)}`:'<span class="muted">—</span>'}</td>
      <td class="n">${rp(t.cum)}</td>
      <td class="tiny muted">${t.sumber}</td>
      <td><span class="pill ${t.berjalan?"final":(t.booking?"prog":"neutral")}">${t.booking||t.berjalan?t.status:"—"}</span></td>
      <td class="n">${t.future?rp(t.future):'<span class="muted">—</span>'}</td></tr>`).join("")}
    <tr class="total"><td colspan="2">Total</td><td class="n">${num(B.bk.length)}</td>
      <td class="n">${rp(B.total)}</td><td class="n">${rp(B.total)}</td>
      <td colspan="2" class="tiny">Log Order + Schedule</td><td class="n">${rp(B.estimasi)}</td></tr>
  </tbody></table></div>

  <div class="card"><h3>Daftar booking belum masuk <span class="eyebrow">${B.fut.length} sesi</span></h3>
    <div class="tw"><table><thead><tr><th>Tgl</th><th>Waktu</th><th>Client</th><th>Paket</th>
      <th class="n">Harga</th><th class="n">Sudah dibayar</th><th class="n">Sisa</th><th>Studio</th></tr></thead><tbody>
      ${B.fut.sort((a,b)=>a.tgl<b.tgl?-1:a.tgl>b.tgl?1:(a.waktu||"")<(b.waktu||"")?-1:1).map(b=>`
        <tr><td class="mono">${b.tgl.slice(8)}</td><td class="mono muted">${esc(b.waktu||"—")}</td>
        <td>${esc(b.nama)}</td><td class="tiny">${esc(b.paketRaw)||'<span class="muted">—</span>'}</td>
        <td class="n">${b.harga?rp(b.harga):'<span class="muted">—</span>'}</td>
        <td class="n">${b.dp?rp(b.dp):'<span class="muted">—</span>'}</td>
        <td class="n"${b.sisa?'':' style="color:var(--muted)"'}>${rp(b.sisa)}</td>
        <td class="tiny muted">${esc(b.studioNama||String(b.studio))}${b.manual?' <span class="pill neutral" style="font-size:9px;padding:1px 5px">manual</span>':""}</td></tr>`).join("")}
    </tbody></table></div>
  </div>`;
}

function vGaji(R){
  const mn=BULAN[+R.c.bulan.split("-")[1]-1], yr=R.c.bulan.split("-")[0];
  const head=`
  <div class="vhead"><div><div class="eyebrow">Akrual berjalan</div><h2>Gaji Karyawan</h2></div>
    <p>Berapa gaji yang sudah terpakai sejauh bulan ini, dihitung dari shift yang tercatat
      di Log Order dikali tarif tiap orang.</p></div>`;
  if(!R.gajiRoster.length) return head+`<div class="card"><div class="empty">
    Kartu tarif belum tersedia.</div></div>`;

  const A=R.gajiAcuan, mnA=A?BULAN[+String(A.bulan).split("-")[1]-1]+" "+String(A.bulan).split("-")[0]:"—";
  const shiftOrang=R.gajiRoster.filter(r=>!r.tetap).sort((x,y)=>y.total-x.total);
  const tetapOrang=R.gajiRoster.filter(r=>r.tetap).sort((x,y)=>y.total-x.total);
  const totShift=shiftOrang.reduce((s,r)=>s+r.q,0);
  const proy=R.hariBerjalan?R.gajiShiftJalan/R.hariBerjalan*R.dim+R.gajiTetapJalan:null;
  const maxT=Math.max(1,...R.gajiRoster.map(r=>r.total));
  const baris=r=>`<tr>
    <td><b>${esc(r.nama)}</b></td><td class="tiny">${esc(r.job)}</td>
    <td class="n">${r.tetap?'<span class="muted">tetap</span>':(r.q?num(r.q):'<span class="muted">0</span>')}</td>
    <td class="n muted">${rp(r.cost)}</td>
    <td class="n heat"><i style="background:var(--accent);width:${(r.total/maxT*100).toFixed(1)}%"></i>${
      r.total?rp(r.total):'<span class="muted">—</span>'}</td></tr>`;

  return head+`
  <div class="stats" style="margin-bottom:16px">
    <div class="stat"><span class="k">Gaji shift berjalan</span><span class="v sm">${rp(R.gajiShiftJalan)}</span>
      <span class="m">${num(totShift)} shift, ${R.hariBerjalan} hari</span></div>
    <div class="stat"><span class="k">Gaji tetap</span><span class="v sm">${rp(R.gajiTetapJalan)}</span>
      <span class="m">${tetapOrang.length} posisi bulanan</span></div>
    <div class="stat"><span class="k">Total akrual</span><span class="v">${rp(R.gajiBlok)}</span>
      <span class="m">sudah terpakai s.d. ${R.cutDay} ${mn}</span></div>
    <div class="stat"><span class="k">Sudah dibayar</span><span class="v sm">${rp(R.gajiNeraca)}</span>
      <span class="m">tercatat di neraca</span></div>
    <div class="stat"><span class="k">Belum dibayar</span><span class="v sm">${rp(Math.max(0,R.gajiSelisih||0))}</span>
      <span class="m">jatuh tempo akhir bulan</span></div>
  </div>

  ${proy?`<div class="note" style="margin-bottom:16px">Kalau shift berjalan dengan pace yang sama
    sampai tanggal ${R.dim}, gaji bulan ini mendarat sekitar <b>${rp(proy)}</b>.</div>`:""}

  <div class="tw" style="margin-bottom:16px"><table><thead><tr>
    <th>Nama</th><th>Posisi</th><th class="n">Shift</th><th class="n">Tarif</th>
    <th class="n">Berjalan</th></tr></thead><tbody>
    ${shiftOrang.map(baris).join("")}
    ${shiftOrang.length&&tetapOrang.length?`<tr><td colspan="4" class="tiny muted"
      style="background:var(--surface2)">Gaji tetap bulanan</td>
      <td class="n" style="background:var(--surface2)"></td></tr>`:""}
    ${tetapOrang.map(baris).join("")}
    <tr class="total"><td colspan="2">Total akrual</td><td class="n">${num(totShift)}</td>
      <td class="n"></td><td class="n">${rp(R.gajiBlok)}</td></tr>
  </tbody></table></div>

  ${R.bonDoc?`
  <div class="two" style="margin-bottom:16px">
    <div class="card"><h3>Kasbon karyawan
        <span class="pill neutral">${rp(R.kasbon)} masuk OPEX</span></h3>
      <p class="tiny muted" style="margin:-6px 0 12px">Uang yang diambil sebelum gajian.
        Nanti dipotong dari gaji akhir bulan.</p>
      ${Object.entries(R.bonOrang).filter(([,d])=>d.kasbon>0).length?`
      <div class="tw"><table><thead><tr><th>Nama</th><th class="n">Kasbon</th>
        <th class="n">Gaji berjalan</th><th class="n">Sisa kalau digaji sekarang</th>
        </tr></thead><tbody>
        ${Object.entries(R.bonOrang).filter(([,d])=>d.kasbon>0).map(([nm,d])=>{
          const rs=R.gajiRoster.filter(r=>String(r.nama).toLowerCase()===nm.toLowerCase());
          const gj=rs.reduce((s,r)=>s+r.total,0);
          const sisa=gj-d.kasbon;
          return `<tr><td><b>${esc(nm)}</b></td>
            <td class="n" style="color:var(--crit)">${rp(d.kasbon)}</td>
            <td class="n">${rs.length?rp(gj):'<span class="muted">tidak di kartu tarif</span>'}</td>
            <td class="n"${rs.length&&sisa<0?' style="color:var(--crit)"':""}>${
              rs.length?rp(sisa):'<span class="muted">—</span>'}</td></tr>`}).join("")}
        <tr class="total"><td>Total</td><td class="n">${rp(R.kasbon)}</td>
          <td class="n">${rp(R.gajiBlok)}</td><td class="n">${rp(R.gajiBlok-R.kasbon)}</td></tr>
      </tbody></table></div>`:`<div class="empty">Belum ada kasbon bulan ini.</div>`}
    </div>
    <div class="card"><h3>Di luar Foxe
        <span class="pill neutral">tidak masuk OPEX</span></h3>
      <div class="stats" style="margin-bottom:12px">
        <div class="stat"><span class="k">Atas nama Aiz</span><span class="v sm">${rp(R.bonAizio)}</span>
          <span class="m">dikelompokkan Aizio</span></div>
        <div class="stat"><span class="k">Nama lain</span><span class="v sm">${rp(R.bonLain)}</span>
          <span class="m">${R.bonLain?"perlu diputuskan":"belum ada"}</span></div>
        <div class="stat"><span class="k">Tarikan pemilik</span><span class="v sm">${rp(R.bonOwner)}</span>
          <span class="m">prive, bukan biaya</span></div>
      </div>
    </div>
  </div>`:""}

  <div class="two">
    <div class="card"><h3>Yang belum masuk hitungan</h3>
      <div class="screen">
        ${[["Bonus","Ditentukan saat tutup bulan berdasarkan tier target dan KPI."],
           ["Kasbon","Potongan gaji atas uang yang sudah diambil duluan."],
           ["Hukuman","Potongan disiplin, diisi manual saat tutup bulan."]
          ].map(([a,b])=>`<div class="chk warn"><span class="badge">NANTI</span>
            <span><b>${a}</b> — <span class="muted">${b}</span></span></div>`).join("")}
      </div>
    </div>
    <div class="card"><h3>Dari mana angkanya</h3>
      <div class="tw"><table><tbody>
        <tr><td>Jumlah shift</td><td class="tiny">Log Order ${mn} ${yr}, blok Shift</td></tr>
        <tr><td>Tarif &amp; posisi</td><td class="tiny">Blok Gaji Karyawan ${mnA}</td></tr>
        <tr><td>Sudah dibayar</td><td class="tiny">Baris berkategori Gaji di neraca ${mn}</td></tr>
      </tbody></table></div>
    </div>
  </div>`;
}

function vSet(R){
  return `
  <div class="vhead"><div><div class="eyebrow">Base Model v2</div><h2>Pengaturan Periode</h2></div>
    <p>Cut-off yang diisi di sini dipakai seluruh halaman. Tidak ada bagian yang punya tanggal sendiri.</p></div>
  <div class="two" style="margin-bottom:14px">
    <div class="card"><h3>Periode</h3>
      <form class="form" id="fCfg">
        <div class="f"><label>Bulan</label><input name="bulan" type="month" value="${R.c.bulan}" required></div>
        <div class="f"><label>Cut-off</label><input name="cutoff" type="date" value="${R.c.cutoff}" required></div>
        <div class="f"><label>Status</label><select name="status">
          <option${R.c.status==="Progressive"?" selected":""}>Progressive</option>
          <option${R.c.status==="Final"?" selected":""}>Final</option></select></div>
        <div class="f"><label>&nbsp;</label><button class="btn pri" type="submit">Terapkan</button></div>
      </form>
      <div class="note" style="margin-top:11px">Status <b>Final</b> membuat seluruh ${R.dim} hari dianggap berjalan dan menghentikan proyeksi run-rate.</div>
    </div>
    <div class="card"><h3>Target & bonus</h3>
      <form class="form" id="fTarget" style="grid-template-columns:repeat(3,1fr)">
        ${R.tiers.map((t,i)=>`<div class="f"><label>Target ${t.tier} omzet</label><input name="t${i}o" inputmode="numeric" value="${t.omzet}"></div>`).join("")}
        ${R.tiers.map((t,i)=>`<div class="f"><label>Target ${t.tier} bonus %</label><input name="t${i}p" inputmode="decimal" value="${(t.persen*100).toFixed(1)}"></div>`).join("")}
        <div class="f" style="grid-column:1/-1"><button class="btn pri" type="submit">Simpan target</button></div>
      </form>
      <div class="tw" style="margin-top:11px"><table><thead><tr><th>Tier</th><th class="n">Target</th><th class="n">%</th><th class="n">Pool</th></tr></thead><tbody>
        ${R.tiers.map(t=>`<tr><td>Target ${t.tier}</td><td class="n">${rp(t.omzet)}</td><td class="n">${pct(t.persen)}</td><td class="n">${rp(t.pool)}</td></tr>`).join("")}
      </tbody></table></div>
    </div>
  </div>
  <div class="card"><h3>Aturan yang dijaga otomatis</h3>
    <div class="screen">${[
      "Omzet, jumlah transaksi, dan payment mix dihitung satu kali lalu dipakai semua bagian.",
      "Tanggal setelah cut-off tampil tanpa angka, termasuk kolom jumlah transaksi.",
      "Proyeksi = run-rate hari berjalan × jumlah hari bulan, tidak pernah sama dengan omzet progresif.",
      "Satu slot tercatat = satu shift; nama sama dua slot di hari yang sama = dua shift.",
      "Photo Fox dinormalisasi jadi Photofox.",
      "Nama di order yang tidak ada di roster shift tetap dihitung dan ditandai.",
      "COGS/OPEX yang belum dikategorikan tidak diam-diam masuk laba rugi.",
      "Baseline YoY kosong tetap PENDING, tidak diganti bulan lain.",
      "Semua nominal diformat Rupiah; tidak ada teks label di kolom angka."
    ].map(t=>`<div class="chk ok"><span class="badge">AKTIF</span><span>${esc(t)}</span></div>`).join("")}</div>
  </div>`;
}

/* ============================ interaksi ============================ */
function wire(R){
  document.querySelectorAll("[data-del]").forEach(b=>b.onclick=()=>{
    const col=b.dataset.del,id=b.dataset.id;
    S[col]=S[col].filter(x=>x.id!==id);
    saveLocal();
    render();});

  const F=(id,fn)=>{const f=document.getElementById(id);if(f)f.onsubmit=e=>{e.preventDefault();
    const d=Object.fromEntries(new FormData(f).entries());fn(d,f);};};

  F("fTrx",(d,f)=>{const rec={id:uid(),tanggal:d.tanggal,client:d.client.trim(),paket:npak(d.paket),
    tanggalFoto:d.tanggalFoto||null,cash:dnum(d.cash),transfer:dnum(d.transfer),
    total:dnum(d.cash)+dnum(d.transfer),admin:d.admin.trim().toUpperCase(),fotografer:d.fotografer.trim().toUpperCase()};
    S.orders.push(rec);saveLocal();f.reset();f.tanggal.value=d.tanggal;render();});

  F("fBiaya",(d,f)=>{const rec={id:uid(),tanggal:d.tanggal,deskripsi:d.deskripsi.trim(),jenis:d.jenis||null,
    kategori:d.kategori||null,vendor:d.vendor.trim(),nilai:dnum(d.nilai),skema:d.skema,
    terminKe:d.terminKe||null,jatuhTempo:d.jatuhTempo||null,nominalDibayar:dnum(d.nominalDibayar)};
    S.expenses.push(rec);saveLocal();f.reset();f.tanggal.value=d.tanggal;render();});

  F("fShift",(d,f)=>{const rec={id:uid(),tanggal:d.tanggal,nama:d.nama.trim().toUpperCase(),slot:dnum(d.slot)||1};
    S.shifts.push(rec);saveLocal();f.reset();f.tanggal.value=d.tanggal;render();});

  F("fLead",(d,f)=>{const ex=S.leads.find(l=>l.tanggal===d.tanggal);
    const rec={id:ex?ex.id:uid(),tanggal:d.tanggal,leads:d.leads===""?null:dnum(d.leads),dp:dnum(d.dp),
      sesiFoto:dnum(d.sesiFoto),transaksi:dnum(d.transaksi)};
    if(ex)Object.assign(ex,rec);else S.leads.push(rec);
    saveLocal();f.reset();f.tanggal.value=d.tanggal;render();});

  F("fKpi",(d,f)=>{const nm=d.nama.trim().toUpperCase();
    const ex=S.kpi.find(k=>String(k.nama).toUpperCase()===nm);
    const rec={id:ex?ex.id:uid(),nama:nm,role:d.role.trim(),hariDinilai:dnum(d.hariDinilai),
      disiplin:d.disiplin===""?null:dnum(d.disiplin),akurasi:d.akurasi===""?null:dnum(d.akurasi),
      sop:d.sop===""?null:dnum(d.sop),client:d.client===""?null:dnum(d.client),
      produktivitas:d.produktivitas===""?null:dnum(d.produktivitas),referral:dnum(d.referral)};
    if(ex)Object.assign(ex,rec);else S.kpi.push(rec);
    saveLocal();f.reset();render();});

  F("fBase",d=>{S.baseline={...(S.baseline||{}),omzet:dnum(d.omzet),txPaid:dnum(d.txPaid),
    cash:dnum(d.cash),transfer:dnum(d.transfer),cogs:dnum(d.cogs),opex:dnum(d.opex)};
    saveLocal();render();});

  F("fCfg",d=>{S.config={...S.config,bulan:d.bulan,cutoff:d.cutoff,status:d.status};
    saveLocal();render();});

  F("fTarget",d=>{S.config.targets=S.config.targets.map((t,i)=>({...t,
    omzet:dnum(d["t"+i+"o"]),persen:dnum(d["t"+i+"p"])/100}));
    saveLocal();render();});

  const sc=document.getElementById("segCal");
  if(sc)sc.querySelectorAll("button").forEach(b=>
    b.onclick=()=>{calMetric=b.dataset.cm;render()});

  const sj=document.getElementById("selJenis"),sk=document.getElementById("selKat");
  if(sj)sj.onchange=()=>{const m={COGS:KAT_COGS,OPEX:KAT_OPEX,LAINNYA:KAT_LAIN,"NON-P&L":KAT_NONPL}[sj.value]||[];
    sk.innerHTML=m.length?m.map(k=>`<option>${esc(k)}</option>`).join(""):`<option value="">— pilih jenis dulu —</option>`;};

  // Theme toggle
  const bt=document.getElementById("btnTheme");
  if(bt) bt.onclick=()=>{
    const cur=document.documentElement.getAttribute("data-theme")||"dark";
    const next=cur==="dark"?"light":"dark";
    document.documentElement.setAttribute("data-theme",next);
    localStorage.setItem("foxe_studio_theme", next);
  };

  // Reset button
  const br=document.getElementById("btnReset");
  if(br) br.onclick=()=>{
    if(confirm("Kembalikan seluruh data ke nilai awal dari Google Drive / Excel? Perubahan manual lokal akan direset.")) {
      localStorage.removeItem("foxe_studio_keuangan_state");
      S=JSON.parse(JSON.stringify(INITIAL_STATE));
      render();
    }
  };

  // Interaksi 12 Kotak Bulan di Section Tahunan
  document.querySelectorAll(".month-card, .btn-go-month").forEach(el => {
    el.onclick = (e) => {
      e.stopPropagation();
      const m = +el.dataset.month;
      view = "dash";
      render();
      document.querySelector(".main").scrollIntoView({block: "start"});
      if (m === 9) {
        showToast("📊 Membuka Dashboard Live September 2026", "ok", 2500);
      } else {
        const bln = BULAN[m - 1] || "";
        showToast(`ℹ️ Bulan ${bln} 2026 belum dicocokkan. Menampilkan Dashboard September 2026 (Live).`, "neutral", 3500);
      }
    };
  });

  // tooltip chart
  const days=R.days.filter(d=>d.berjalan);
  document.querySelectorAll(".hitg").forEach(h=>{
    const r=days[+h.dataset.i]; if(!r)return;
    h.onmousemove=e=>tipShow(e,`<b>${r.d} ${BULAN[+R.c.bulan.split("-")[1]-1]} · ${r.hari}</b>
      <div class="r"><span>Cash</span><span>${rp(r.cash)}</span></div>
      <div class="r"><span>Transfer</span><span>${rp(r.transfer)}</span></div>
      <div class="r"><span>Omzet hari ini</span><span>${rp(r.omzet)}</span></div>
      <div class="r"><span>Progresif</span><span>${rp(r.cum)}</span></div>
      <div class="r"><span>Growth</span><span>${r.growth==null?"—":(r.growth>=0?"+":"")+pct(r.growth)}</span></div>
      <div class="r"><span>Transaksi</span><span>${num(r.txPaid)} masuk / ${num(r.tx)}</span></div>`);
    h.onmouseleave=tipHide;});
}

/* ============================ export xlsx ============================ */
async function exportXlsx(){
  const R=compute(), wb=XLSX.utils.book_new();
  const mn=BULAN[+R.c.bulan.split("-")[1]-1], yr=R.c.bulan.split("-")[0];
  const hdr=t=>[[`${t} | FOXE STUDIO | ${mn.toUpperCase()} ${yr} | s.d. ${R.cutDay} ${mn.toUpperCase()} | ${R.c.status.toUpperCase()}`],[]];
  const add=(name,rows)=>XLSX.utils.book_append_sheet(wb,XLSX.utils.aoa_to_sheet(rows),name.slice(0,31));

  add("Log Transaksi",[...hdr("LOG TRANSAKSI"),
    ["No","Tanggal Setoran","Nama Client","Paket","Tanggal Foto","Cash","Transfer","Total Masuk","Metode Pembayaran","Admin","Fotografer"],
    ...S.orders.filter(o=>o.tanggal<=R.c.cutoff).sort((a,b)=>a.tanggal<b.tanggal?-1:1).map((o,i)=>{
      const c=dnum(o.cash),t=dnum(o.transfer);
      return [i+1,o.tanggal,o.client,npak(o.paket),o.tanggalFoto||"",c,t,c+t,c&&t?"Cash + Transfer":c?"Cash":t?"Transfer":"",o.admin||"",o.fotografer||""]})]);

  add("Omzet Harian",[...hdr("OMZET HARIAN & PROGRESIF"),
    ["Tanggal","Hari","Jumlah Transaksi","Cash","Transfer","Omzet Harian","Omzet Progresif","Growth vs Hari Lalu","Rata-rata Transaksi"],
    ...R.days.map(d=>d.berjalan
      ?[d.d,d.hari,d.tx,d.cash,d.transfer,d.omzet,d.cum,d.growth==null?"":+(d.growth).toFixed(4),Math.round(d.avg)]
      :[d.d,d.hari,"","","","","","",""]),
    ["TOTAL",""," "+R.tx,R.cash,R.transfer,R.omzet,R.omzet,"",Math.round(R.avgTx)],[],
    ["Omzet s.d. cut-off",R.omzet],["Rata-rata / hari",Math.round(R.runRate)],
    [`Proyeksi ${R.dim} hari`,Math.round(R.proyeksi)],["Sisa hari",R.dim-R.hariBerjalan],["Status",R.c.status]]);

  add("Paket & Crew",[...hdr("ANALISIS PAKET & CREW"),
    ["Ranking","Paket","Jumlah Transaksi","Total Nilai"],
    ...R.paket.map((p,i)=>[i+1,p.paket,p.tx,p.nilai]),[],
    ["ORDER PER ADMIN"],["Admin","Jumlah Order","Porsi","Nilai Transaksi"],
    ...R.admin.arr.map(a=>[a.nama,a.n,+a.porsi.toFixed(4),a.nilai]),[],
    ["ASSIGNMENT PER FOTOGRAFER"],["Fotografer","Jumlah Assignment","Porsi","Nilai Transaksi"],
    ...R.fotografer.arr.map(f=>[f.nama,f.n,+f.porsi.toFixed(4),f.nilai]),[],
    ["DATA QUALITY"],["Jenis","Jumlah"],
    ["Admin belum diisi",R.admin.kosong],["Fotografer belum diisi",R.fotografer.kosong],
    ["Admin di luar roster shift",R.offRoster.admin.reduce((s,x)=>s+x.n,0)],
    ["Fotografer di luar roster shift",R.offRoster.fotografer.reduce((s,x)=>s+x.n,0)],
    ["Transaksi Rp0",R.rp0]]);

  const orang=R.shift.filter(s=>s.total>0).map(s=>s.nama);
  const byd=new Map(); R.shiftDetail.forEach(s=>{const m=byd.get(s.tanggal)||new Map();
    m.set(String(s.nama).toUpperCase(),(m.get(String(s.nama).toUpperCase())||0)+dnum(s.slot));byd.set(s.tanggal,m)});
  add("Rekap Shift",[...hdr("REKAP SHIFT"),
    ["RULES: 1 slot tercatat = 1 shift. Nama sama 2 slot pada hari sama = 2 shift."],[],
    ["Nama","Total Shift","Porsi"],...R.shift.filter(s=>s.total>0).map(s=>[s.nama,s.total,+s.porsi.toFixed(4)]),[],
    ["Tanggal","Hari",...orang,"Total"],
    ...R.days.map(d=>{const m=byd.get(d.ds);
      return d.berjalan?[d.d,d.hari,...orang.map(n=>(m&&m.get(n))||0),orang.reduce((s,n)=>s+((m&&m.get(n))||0),0)]
      :[d.d,d.hari,...orang.map(()=>""),""]}),
    ["TOTAL","",...orang.map(n=>R.shift.find(s=>s.nama===n).total),R.shiftTot]]);

  const FMT='"Rp" #,##0';
  Object.keys(wb.Sheets).forEach(n=>{const ws=wb.Sheets[n];
    Object.keys(ws).forEach(a=>{ if(a[0]==="!")return; const c=ws[a];
      if(c.t==="n"&&Math.abs(c.v)>=1000){c.z=FMT}
      else if(c.t==="n"&&Math.abs(c.v)<=1&&String(c.v).includes(".")){c.z="0.0%"}});
    const w=[];for(let i=0;i<14;i++)w.push({wch:i===1?22:i===0?20:14});ws["!cols"]=w;});

  const out=XLSX.write(wb,{bookType:"xlsx",type:"array"});
  const name=`Foxe_Studio_Laporan_${mn}_${yr}_${R.c.status==="Final"?"FINAL":"s.d."+R.cutDay}.xlsx`;
  const blob=new Blob([out],{type:"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"});
  const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download=name;a.click();
  setTimeout(()=>URL.revokeObjectURL(a.href),2000);
}
document.getElementById("btnExport").onclick=async e=>{
  const b=e.currentTarget;b.disabled=true;const t=b.textContent;b.textContent="Menyiapkan…";
  try{await exportXlsx();b.textContent="Tersimpan";}catch(err){b.textContent="Gagal";}
  setTimeout(()=>{b.textContent=t;b.disabled=false},1800);};

// Initialize Theme
const savedTheme = localStorage.getItem("foxe_studio_theme") || "dark";
document.documentElement.setAttribute("data-theme", savedTheme);

/* ============================ AUTHENTICATION SYSTEM (SOLUSI 1) ============================ */
const AUTH_KEY = "foxe_studio_auth_token_v1";
const VALID_HASHES = [
  "85ec11c08e12c6db362082a46267150136507c7dac5712c6cf526feaceea7241", // 202688 (Default Studio PIN)
  "fd05a2c03c09715cdf08acd15f01abd477f7e7a32d34cc5282eeb8d2dd996a44", // 123456
  "b2558bd3f534e7c602b6f893138512a1e20948be8d9fa2b044560e92f1ead53b", // 202609
  "a634cdf391c6b7b911c46e9c873de639fc933434d17b277b3ee6fe419f244cc2"  // 889900
];

async function hashPin(pin) {
  const msgUint8 = new TextEncoder().encode(pin + "_foxe_studio_secret_salt_2026");
  const hashBuffer = await crypto.subtle.digest("SHA-256", msgUint8);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, "0")).join("");
}

function checkSavedAuth() {
  try {
    const raw = localStorage.getItem(AUTH_KEY);
    if (!raw) return false;
    const parsed = JSON.parse(raw);
    if (parsed.expires && Date.now() < parsed.expires && VALID_HASHES.includes(parsed.token)) {
      return true;
    }
  } catch(e){}
  return false;
}

let enteredPin = "";

function updatePinDots() {
  const dots = document.querySelectorAll("#pinDots .dot");
  dots.forEach((dot, idx) => {
    if (idx < enteredPin.length) {
      dot.classList.add("filled");
    } else {
      dot.classList.remove("filled");
    }
  });
}

async function verifyPin() {
  if (enteredPin.length < 4) return;
  const hash = await hashPin(enteredPin);
  const customHash = localStorage.getItem("foxe_custom_pin_hash");
  if (VALID_HASHES.includes(hash) || (customHash && hash === customHash)) {
    const remember = document.getElementById("chkRemember") ? document.getElementById("chkRemember").checked : true;
    if (remember) {
      const authData = {
        token: hash,
        expires: Date.now() + (30 * 24 * 60 * 60 * 1000)
      };
      localStorage.setItem(AUTH_KEY, JSON.stringify(authData));
    }
    unlockDashboard();
  } else {
    const errEl = document.getElementById("lockError");
    if (errEl) {
      errEl.hidden = false;
      errEl.textContent = "PIN salah. Silakan coba lagi.";
    }
    const pinDots = document.getElementById("pinDots");
    if (pinDots) {
      pinDots.classList.add("shake");
      setTimeout(() => {
        pinDots.classList.remove("shake");
        enteredPin = "";
        updatePinDots();
        const pinInp = document.getElementById("pinInput");
        if (pinInp) pinInp.value = "";
      }, 500);
    }
  }
}

function unlockDashboard() {
  const lock = document.getElementById("lockScreen");
  const appEl = document.querySelector(".app");
  if (lock) {
    lock.style.transition = "opacity 0.25s ease, transform 0.25s ease";
    lock.style.opacity = "0";
    lock.style.transform = "scale(1.04)";
    setTimeout(() => {
      lock.style.display = "none";
      if (appEl) {
        appEl.style.filter = "none";
        appEl.style.pointerEvents = "auto";
      }
    }, 250);
  }
}

function lockDashboard() {
  localStorage.removeItem(AUTH_KEY);
  enteredPin = "";
  updatePinDots();
  const lock = document.getElementById("lockScreen");
  const appEl = document.querySelector(".app");
  if (lock) {
    lock.style.display = "flex";
    lock.style.opacity = "1";
    lock.style.transform = "none";
    if (appEl) {
      appEl.style.filter = "blur(14px)";
      appEl.style.pointerEvents = "none";
    }
    const pinInp = document.getElementById("pinInput");
    if (pinInp) {
      pinInp.value = "";
      pinInp.focus();
    }
    const errEl = document.getElementById("lockError");
    if (errEl) errEl.hidden = true;
  }
}

// Bind Keypad & Events
const pinInput = document.getElementById("pinInput");
const pinKeypad = document.getElementById("pinKeypad");
const keyClear = document.getElementById("keyClear");
const keySubmit = document.getElementById("keySubmit");
const btnLock = document.getElementById("btnLock");

if (btnLock) {
  btnLock.onclick = () => lockDashboard();
}

if (pinKeypad) {
  pinKeypad.querySelectorAll(".key-btn[data-val]").forEach(btn => {
    btn.onclick = () => {
      if (enteredPin.length < 6) {
        enteredPin += btn.dataset.val;
        if (pinInput) pinInput.value = enteredPin;
        updatePinDots();
        if (enteredPin.length === 6) verifyPin();
      }
    };
  });
}

if (keyClear) {
  keyClear.onclick = () => {
    enteredPin = enteredPin.slice(0, -1);
    if (pinInput) pinInput.value = enteredPin;
    updatePinDots();
    const errEl = document.getElementById("lockError");
    if (errEl) errEl.hidden = true;
  };
}

if (keySubmit) {
  keySubmit.onclick = () => verifyPin();
}

if (pinInput) {
  pinInput.oninput = () => {
    enteredPin = pinInput.value.replace(/[^0-9]/g, "").slice(0, 6);
    pinInput.value = enteredPin;
    updatePinDots();
    if (enteredPin.length === 6) verifyPin();
  };
  pinInput.onkeydown = e => {
    if (e.key === "Enter") verifyPin();
  };
}

// Focus input when clicking anywhere on lock card
const lockCard = document.querySelector(".lock-card");
if (lockCard && pinInput) {
  lockCard.addEventListener("click", e => {
    if (!e.target.closest("button") && !e.target.closest("input")) {
      pinInput.focus();
    }
  });
}

// Initial Auth Check
if (checkSavedAuth()) {
  const lock = document.getElementById("lockScreen");
  if (lock) lock.style.display = "none";
} else {
  lockDashboard();
}

/* ============================ MODUL UPDATE & SINKRONISASI ============================ */
const GITHUB_TOKEN_KEY = "foxe_github_token";
const AUTO_FULL_SYNC_KEY = "foxe_auto_drive_sync";
const GITHUB_REPO = "whynunuu/FoxeStudio";
const GITHUB_WORKFLOW = "daily_sync.yml";

function showToast(msg, type="ok", duration=3500) {
  const t = document.getElementById("toast");
  if (!t) return;
  t.textContent = msg;
  t.className = "toast show " + (type === "err" ? "err" : "ok");
  clearTimeout(t._timer);
  t._timer = setTimeout(() => {
    t.className = "toast";
  }, duration);
}

function getSavedGithubToken() {
  return localStorage.getItem(GITHUB_TOKEN_KEY) || "";
}

function updateTokenUI() {
  const token = getSavedGithubToken();
  const badge = document.getElementById("tokenStatusBadge");
  const inputSec = document.getElementById("tokenInputSec");
  const savedSec = document.getElementById("tokenSavedSec");
  const chkAuto = document.getElementById("chkAutoFullSync");
  const autoSync = localStorage.getItem(AUTO_FULL_SYNC_KEY) === "true";

  if (chkAuto) chkAuto.checked = autoSync;

  if (token) {
    if (badge) { badge.textContent = "Terhubung"; badge.className = "pill final"; }
    if (inputSec) inputSec.hidden = true;
    if (savedSec) savedSec.hidden = false;
  } else {
    if (badge) { badge.textContent = "Belum Terhubung"; badge.className = "pill neutral"; }
    if (inputSec) inputSec.hidden = false;
    if (savedSec) savedSec.hidden = true;
  }
}

function openSyncModal() {
  const modal = document.getElementById("syncModal");
  if (!modal) return;
  const R = compute();
  const cutEl = document.getElementById("modalCutoff");
  const lastEl = document.getElementById("modalLastSync");
  const ok = syncSukses();
  if (cutEl) cutEl.textContent = `Cut-off: s.d. ${R.cutDay} ${BULAN[+R.c.bulan.split("-")[1]-1]}`;
  if (lastEl) lastEl.textContent = ok ? `Terakhir: ${wibParts(ok.mulai).tgl.split(" ").slice(0,2).join(" ")} ${wibParts(ok.mulai).jam}` : "Terakhir: —";

  // Reset status box
  const act = document.getElementById("syncActions");
  const sb = document.getElementById("syncStatusBox");
  if (act) act.hidden = false;
  if (sb) sb.hidden = true;

  updateTokenUI();
  modal.classList.add("open");
}

function closeSyncModal() {
  const modal = document.getElementById("syncModal");
  if (modal) modal.classList.remove("open");
}

async function fastRefresh(silent = false) {
  const btn = document.getElementById("btnUpdateData");
  const originalHtml = btn ? btn.innerHTML : "🔄 Update";
  if (btn) { btn.innerHTML = "⏳ Refresh..."; btn.disabled = true; }

  try {
    const res = await fetch("foxe_full_state.json?t=" + Date.now(), { cache: "no-store" });
    if (!res.ok) throw new Error("Gagal mengambil data dari server (HTTP " + res.status + ")");
    const latest = await res.json();
    
    const curSyncId = (S.sync && S.sync[0] && S.sync[0].id) || "";
    const newSyncId = (latest.sync && latest.sync[0] && latest.sync[0].id) || "";
    
    S = latest;
    localStorage.setItem("foxe_studio_keuangan_state", JSON.stringify(S));
    localStorage.setItem("foxe_studio_keuangan_sync_id", newSyncId || "sync_" + Date.now());
    render();

    if (!silent) {
      const ok = syncSukses();
      const jam = ok ? wibParts(ok.mulai).jam : "";
      showToast("✅ Data tampilan berhasil diperbarui!" + (jam ? ` (Update ${jam} WIB)` : ""));
    }
    closeSyncModal();
    return true;
  } catch (err) {
    if (!silent) showToast("⚠️ " + err.message, "err");
    return false;
  } finally {
    if (btn) {
      btn.innerHTML = "✅ Terkini";
      setTimeout(() => { btn.innerHTML = originalHtml; btn.disabled = false; }, 1800);
    }
  }
}

async function triggerGoogleDriveSync() {
  const token = getSavedGithubToken();
  if (!token) {
    openSyncModal();
    const inp = document.getElementById("txtGithubToken");
    if (inp) {
      inp.focus();
      inp.style.borderColor = "var(--crit)";
      setTimeout(() => { inp.style.borderColor = "var(--hairline-strong)"; }, 1500);
    }
    showToast("Masukkan GitHub Token Anda terlebih dahulu untuk Full Sync Google Drive", "err");
    return;
  }

  const act = document.getElementById("syncActions");
  const sb = document.getElementById("syncStatusBox");
  const title = document.getElementById("syncStatusTitle");
  const desc = document.getElementById("syncStatusDesc");
  const btnTop = document.getElementById("btnUpdateData");

  if (act) act.hidden = true;
  if (sb) sb.hidden = false;
  if (title) title.textContent = "Memicu sinkronisasi Google Drive...";
  if (desc) desc.textContent = "Mengirim instruksi ke GitHub Cloud...";
  if (btnTop) { btnTop.innerHTML = "⏳ Syncing..."; btnTop.disabled = true; }

  try {
    // 1. Trigger workflow_dispatch
    const dispatchUrl = `https://api.github.com/repos/${GITHUB_REPO}/actions/workflows/${GITHUB_WORKFLOW}/dispatches`;
    const res = await fetch(dispatchUrl, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ ref: "main" })
    });

    if (res.status !== 204 && !res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.message || `Gagal memicu GitHub Actions (Status: ${res.status})`);
    }

    if (title) title.textContent = "Sedang mengunduh dari Google Drive...";
    if (desc) desc.textContent = "Memproses File 1 Log Order, File 2 Schedule, dan File Neraca...";
    showToast("🚀 Sinkronisasi Google Drive telah dimulai di cloud!");

    // 2. Poll foxe_full_state.json sampai update (maksimal 45 detik)
    const startSyncId = (S.sync && S.sync[0] && S.sync[0].id) || "";
    let completed = false;
    let attempts = 0;
    const maxAttempts = 15; // 15 x 3 detik = 45 detik

    const pollInterval = setInterval(async () => {
      attempts++;
      if (desc) desc.textContent = `Menunggu hasil kalkulasi cloud... (${attempts * 3} detik)`;

      try {
        const checkRes = await fetch("foxe_full_state.json?t=" + Date.now(), { cache: "no-store" });
        if (checkRes.ok) {
          const checkData = await checkRes.json();
          const checkSyncId = (checkData.sync && checkData.sync[0] && checkData.sync[0].id) || "";
          if (checkSyncId && checkSyncId !== startSyncId) {
            clearInterval(pollInterval);
            completed = true;

            S = checkData;
            localStorage.setItem("foxe_studio_keuangan_state", JSON.stringify(S));
            localStorage.setItem("foxe_studio_keuangan_sync_id", checkSyncId);
            render();

            if (title) title.textContent = "✅ Sinkronisasi Berhasil!";
            if (desc) desc.textContent = "Data terbaru telah aktif di website.";
            showToast("✅ Berhasil! Data website telah diperbarui dari Google Drive.");

            setTimeout(() => {
              closeSyncModal();
              if (btnTop) { btnTop.innerHTML = "🔄 Update"; btnTop.disabled = false; }
            }, 1200);
          }
        }
      } catch (e) {
        console.warn("Polling state check:", e);
      }

      if (attempts >= maxAttempts && !completed) {
        clearInterval(pollInterval);
        if (title) title.textContent = "Sinkronisasi Masih Berjalan di Cloud";
        if (desc) desc.textContent = "GitHub Actions sedang memproses. Klik 'Refresh Cepat' beberapa saat lagi untuk memuatnya.";
        showToast("ℹ️ Proses cloud masih berlangsung. Silakan klik Update lagi dalam 15-20 detik.", "ok", 5000);
        setTimeout(() => {
          closeSyncModal();
          if (btnTop) { btnTop.innerHTML = "🔄 Update"; btnTop.disabled = false; }
        }, 3000);
      }
    }, 3000);

  } catch (err) {
    if (title) title.textContent = "Gagal Sinkronisasi";
    if (desc) desc.textContent = err.message;
    showToast("❌ " + err.message, "err", 5000);
    if (btnTop) { btnTop.innerHTML = "🔄 Update"; btnTop.disabled = false; }
  }
}

function wireSyncEvents() {
  const btnUpd = document.getElementById("btnUpdateData");
  const btnSettings = document.getElementById("btnSyncSettings");
  const btnClose = document.getElementById("btnCloseSyncModal");
  const modal = document.getElementById("syncModal");
  const optFast = document.getElementById("btnOptFast");
  const optDrive = document.getElementById("btnOptDrive");
  const btnSaveToken = document.getElementById("btnSaveToken");
  const btnRemoveToken = document.getElementById("btnRemoveToken");
  const txtToken = document.getElementById("txtGithubToken");
  const chkAuto = document.getElementById("chkAutoFullSync");

  if (btnUpd) {
    btnUpd.onclick = (e) => {
      if (e.shiftKey) {
        openSyncModal();
        return;
      }
      const token = getSavedGithubToken();
      const autoSync = localStorage.getItem(AUTO_FULL_SYNC_KEY) === "true";
      if (token && autoSync) {
        triggerGoogleDriveSync();
      } else {
        openSyncModal();
      }
    };
  }

  if (btnSettings) {
    btnSettings.onclick = () => openSyncModal();
  }

  if (btnClose) {
    btnClose.onclick = () => closeSyncModal();
  }

  if (modal) {
    modal.onclick = (e) => {
      if (e.target === modal) closeSyncModal();
    };
  }

  if (optFast) {
    optFast.onclick = () => fastRefresh();
  }

  if (optDrive) {
    optDrive.onclick = () => triggerGoogleDriveSync();
  }

  if (btnSaveToken && txtToken) {
    btnSaveToken.onclick = () => {
      const val = txtToken.value.trim();
      if (!val) {
        showToast("Masukkan token GitHub yang valid", "err");
        return;
      }
      localStorage.setItem(GITHUB_TOKEN_KEY, val);
      txtToken.value = "";
      updateTokenUI();
      showToast("✅ Token GitHub berhasil disimpan aman di browser ini!");
    };
    txtToken.onkeydown = (e) => {
      if (e.key === "Enter") btnSaveToken.click();
    };
  }

  if (btnRemoveToken) {
    btnRemoveToken.onclick = () => {
      if (confirm("Hapus token GitHub dari browser ini?")) {
        localStorage.removeItem(GITHUB_TOKEN_KEY);
        updateTokenUI();
        showToast("Token GitHub telah dihapus.");
      }
    };
  }

  if (chkAuto) {
    chkAuto.onchange = () => {
      localStorage.setItem(AUTO_FULL_SYNC_KEY, chkAuto.checked ? "true" : "false");
    };
  }
}

/* ============================ start ============================ */
wireSyncEvents();
render();
</script>

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_template)

print("Generated index.html successfully with full embedded state and persistence!")


