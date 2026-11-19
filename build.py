#!/usr/bin/env python3
import json, base64, html, os
HERE = os.path.dirname(os.path.abspath(__file__))
THUMBS = os.path.join(HERE, "photos")
d = json.load(open(os.path.join(HERE, "plants.json"), encoding="utf-8"))
E = html.escape
LK = d["light_key"]; TIPS = d["tips"]; BL = d["blocks"]; WK = d["window_key"]; CK = d["cold_key"]
ROTV = {"Low": "low", "Medium": "medium", "High": "high", "Likes moisture": "moist"}
LIGHT_SHORT = {"bars2": "2 strips", "bars1": "1 strip", "skylight": "Skylight", "gooseneck": "Gooseneck"}

def uri(fn):
    if not fn: return None
    p = os.path.join(THUMBS, fn)
    if not os.path.exists(p): return None
    return "data:image/jpeg;base64," + base64.b64encode(open(p, "rb").read()).decode()

def illus_uri(pid):
    p = os.path.join(HERE, "illus", pid + ".svg")
    if not os.path.exists(p): return None
    return "data:image/svg+xml;base64," + base64.b64encode(open(p, "rb").read()).decode()

def initials(n):
    w = [x for x in n.replace("-", " ").split() if x[0].isalpha()]
    return (w[0][0] + (w[1][0] if len(w) > 1 else w[0][1] if len(w[0]) > 1 else "")).upper()

def placeholder(p):
    return (f'<div class="ph b{p["block"]}" aria-hidden="true"><span class="s1"></span><span class="s2"></span>'
            f'<span class="s3"></span><b>{E(initials(p["name"]))}</b></div>')

def card(p):
    b = str(p["block"]); u = uri(p.get("photo"))
    iu = None if u else illus_uri(p["id"])
    img = (f'<img src="{u or iu}"{"" if u else ' class="ill"'} alt="{E(p["name"])}" loading="lazy">' if (u or iu) else placeholder(p))
    alt = p.get("alt_light")
    lights = [p["light"]] + ([alt] if alt else [])
    lt = f'<span class="badge light">{E(LK[p["light"]])}</span>'
    if alt: lt += f'<span class="badge also">also OK: {E(LK[alt])}</span>'
    rot = p["rot"]
    rc = {"Low": "low", "Medium": "med", "High": "high"}.get(rot, "moist")
    rl = f"Rot risk: {E(rot)}" if rot in ("Low", "Medium", "High") else E(rot)
    tox = {"high":'<span class="badge tox">🐕⚠️ Toxic to dogs: keep up high</span>',"mild":'<span class="badge tox mild">🐕 Mildly toxic to dogs</span>',"spines":'<span class="badge tox spn">🐕 Spines: keep away from dogs</span>'}.get(p.get("toxic"),"")
    return f'''<article class="card b{b}" tabindex="0" role="button" aria-expanded="false" data-block="{b}" data-dog="{p.get("toxic") or "safe"}" data-window="{p["window"]}" data-cold="{p["cold"]}" data-rot="{ROTV[p["rot"]]}" data-name="{E(p["name"].lower())}" data-light="{' '.join(lights)}" data-search="{E((p["name"]+" "+p["latin"]+" "+p["looks"]+" "+p["care"]).lower())}">
<div class="photo">{img}</div>
<div class="body">
<div class="top"><span class="badge blk b{b}">Block {b}</span><span class="mono pot">{E(p["pot"]) if "pot" in p["pot"] else E(p["pot"])+" pot"}</span></div>
<h3>{E(p["name"])}</h3>
<p class="latin">{E(p["latin"])}</p>
<div class="badges">{lt}<span class="badge rot {rc}">{rl}</span>{tox}</div>
<div class="more">
<h4 class="mono">When it's thirsty</h4><p class="temp">{E(p["thirsty"])}</p><h4 class="mono">Windowsill &amp; cold</h4><div class="badges"><span class="badge win w-{p["window"]}">{E(WK[p["window"]])}</span><span class="badge cold k-{p["cold"]}">{E(CK[p["cold"]])}</span></div><p class="temp"><b>Temperature:</b> best {E(p["temp_ideal"])} · minimum {E(p["temp_min"])} (with dry soil)</p>
<h4 class="mono">How to spot it</h4><p>{E(p["looks"])}</p>
<h4 class="mono">Care</h4><p>{E(p["care"])}</p>
</div>
<span class="hint mono">Tap for details</span>
</div></article>'''

blocks_html = ""
for k, b in BL.items():
    blocks_html += f'''<div class="blk-card b{k}" data-b="{k}"><div class="mono bn">Block {k}</div>
<div class="bname">{E(b["name"].split("·",1)[1].strip())}</div><div class="mono bt">{E(b["time"])}</div>
<div class="cad cad-w"><span class="mono">Nov–Feb</span><strong>{E(b["winter"])}</strong></div>
<div class="cad cad-g"><span class="mono">Mar–Oct</span><strong>{E(b["growing"])}</strong></div></div>'''

def chips(f, alllabel, items, extra=""):
    h = f'<button class="chip on" data-f="{f}" data-v="all" aria-pressed="true">{alllabel}</button>'
    for v, label, *cls in items:
        c = (" " + cls[0]) if cls else ""
        h += f'<button class="chip{c}" data-f="{f}" data-v="{v}" aria-pressed="false">{E(label)}</button>'
    return h

chips_b = chips("block", "All", [(k, f"Block {k}", f"c{k}") for k in BL])
chips_l = chips("light", "Any light", list(LIGHT_SHORT.items()))
chips_w = chips("window", "Any", [("great", "Great on sill"), ("ok", "OK on sill"), ("no", "Needs bars")])
chips_c = chips("cold", "Any", [("40", "Cool-tolerant 40°F"), ("45", "Above 45°F"), ("50", "Keep warm 50°F")])
chips_d = chips("dog", "Any", [("safe", "Safe"), ("mild", "Mild"), ("high", "Toxic"), ("spines", "Spines")])
chips_r = chips("rot", "Any", [("low", "Low"), ("medium", "Medium"), ("high", "High"), ("moist", "Likes moisture")])
SORTS = [("block", "By block"), ("tox", "Most toxic first"), ("cold", "Most cold-tolerant first"),
         ("window", "Best for windowsill first"), ("rot", "Lowest rot risk first"), ("az", "A–Z")]
chips_s = "".join(f'<button class="chip{" on" if k == "block" else ""}" data-f="sort" data-v="{k}" aria-pressed="{"true" if k == "block" else "false"}">{v}</button>' for k, v in SORTS)

signs = "".join(f"<li>{E(s)}</li>" for s in TIPS["signs"])
qr = "".join(f'<div class="qp"><h4 class="mono">{l}</h4><p>{E(TIPS[k])}</p></div>' for l, k in
             [("Dogs 🐕", "dogs"), ("How much water", "water_amount"), ("Wattage", "watts"), ("Cold damage", "cold_signs"), ("Pests", "pests"), ("Thirsty or overwatered?", "thirsty_note"), ("Lights", "lights"), ("Soil", "soil"), ("New arrivals", "new_arrivals"), ("Root rot", "root_rot")])
n = len(d["plants"])

CSS = r'''
:root{--bg:#e9e8e3;--ink:#141414;--mut:#505050;--pad:#1f9e5a;--padd:#147a43;--mag:#ff2d8a;--mus:#141414;--pur:#1f9e5a;--pink:#ffd3e6;--line:#bdbcb6;--card:#f2f1ec;--r:4px}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 "JetBrains Mono",ui-monospace,Menlo,monospace}
.mono{font-family:"JetBrains Mono",ui-monospace,Menlo,monospace;font-size:.72rem;letter-spacing:.06em;text-transform:uppercase}
.wrap{max-width:1000px;margin:0 auto;padding:0 16px}
header{padding:28px 0 8px}
.eyebrow{color:var(--mag)}
h1{font-size:clamp(1.7rem,7vw,2.8rem);line-height:1.05;margin:6px 0 8px;letter-spacing:.04em;text-transform:uppercase;font-weight:800}
h1 i{font-style:normal;color:var(--mag)}h1 i::before{content:"+"}
.sub{color:var(--mut);margin:0 0 18px}
.rule{background:var(--ink);color:#fff;border-radius:var(--r);padding:16px 18px;border-left:10px solid var(--mag);font-size:1.1rem;font-weight:600}
.rule .mono{display:block;color:#ffd0e6;margin-bottom:4px}
h2{font-size:1.3rem;margin:28px 0 10px;letter-spacing:-.01em}
.blocks{display:grid;grid-template-columns:1fr;gap:10px}
.blk-card{background:var(--card);border:2px solid var(--line);border-top:8px solid var(--c);border-radius:var(--r);padding:12px 14px}
.blk-card .bn{color:var(--c2)}.bname{font-weight:700}.bt{color:var(--mut);margin:2px 0 8px;text-transform:none;letter-spacing:0}
.cad{display:flex;justify-content:space-between;align-items:center;gap:8px;padding:6px 10px;border-radius:10px;margin-top:4px;border:2px solid transparent;background:#f1efe4}
.cad.now{background:var(--c);color:var(--cink);border-color:var(--ink)}
.cad.now::after{content:"NOW";font:700 .6rem "JetBrains Mono",monospace;background:var(--ink);color:#fff;border-radius:6px;padding:1px 5px;order:3}
.b1{--c:#ff2d8a;--c2:#c4005f;--cink:#141414}.b2{--c:#1f9e5a;--c2:#147a43;--cink:#fff}.b3{--c:#141414;--c2:#141414;--cink:#ff2d8a}
.season{color:var(--mut);margin:8px 2px 0}
.filters{z-index:5;background:var(--bg);padding:10px 0;border-bottom:2px solid var(--line);margin-top:20px}
.row{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px;align-items:center}
.row>.mono{color:var(--mut);margin-right:4px}
.chip{font:600 .85rem "JetBrains Mono",monospace;border:2px solid var(--ink);background:#fff;color:var(--ink);border-radius:3px;padding:6px 12px;text-transform:uppercase;letter-spacing:.04em;cursor:pointer;min-height:36px}
.chip.on{background:var(--ink);color:#fff}.chip:hover{border-color:var(--mag)}
.chip.c1.on{background:#ff2d8a;border-color:#ff2d8a;color:#141414}.chip.c2.on{background:#1f9e5a;border-color:#1f9e5a}.chip.c3.on{background:#141414;color:#ff2d8a}
.search{width:100%;font:500 1rem "JetBrains Mono",monospace;padding:10px 14px;border:2px solid var(--ink);border-radius:14px;background:#fff}
.search:focus,.chip:focus-visible,.card:focus-visible{outline:3px solid var(--mag);outline-offset:2px}
.countrow{display:flex;align-items:center;flex-wrap:wrap;gap:6px 14px;margin:12px 2px}
.count{color:var(--mut)}
.linkbtn{background:none;border:0;padding:6px 2px;color:var(--mag);text-decoration:underline;text-underline-offset:3px;cursor:pointer;font-weight:700}
.linkbtn:focus-visible{outline:3px solid var(--mag);outline-offset:2px}
.ftop{display:none}
.fsearch{margin-bottom:0}
.badge.win,.badge.cold{background:#fff}
.badge.w-great,.badge.k-40{background:var(--pad);border-color:var(--pad);color:#fff}
.badge.w-no{background:transparent}
.badge.k-50{background:var(--pink)}
.grid{display:grid;grid-template-columns:1fr;gap:14px}
.card{background:var(--card);border:2px solid var(--ink);border-radius:var(--r);overflow:hidden;display:flex;cursor:pointer;box-shadow:inset 6px 0 0 var(--c)}
.card[hidden]{display:none}
.photo{width:110px;min-height:110px;flex:none;background:#e8e5d6}
.photo img{width:100%;height:100%;object-fit:cover;display:block}.photo img.ill{object-fit:contain;padding:6px;background:#e9e8e3}
.body{padding:12px 14px;min-width:0;flex:1}
.top{display:flex;gap:8px;align-items:center;justify-content:space-between}
.pot{color:var(--mut)}
h3{margin:6px 0 0;font-size:1.02rem;line-height:1.2;text-transform:uppercase;letter-spacing:.02em}
.latin{font-style:italic;color:var(--mut);margin:0 0 8px;font-size:.92rem}
.badges{display:flex;flex-wrap:wrap;gap:5px}
.badge{font:700 .7rem "JetBrains Mono",monospace;padding:3px 8px;border-radius:8px;border:1.5px solid var(--ink);background:#fff;letter-spacing:.02em}
.badge.blk{background:var(--c);color:var(--cink);border-color:var(--c);text-transform:uppercase}
.badge.light{background:#fff}.badge.also{background:#fff;border-style:dashed;font-weight:400}
.badge.low{background:#c9ecd7}.badge.med{background:#ffe1ee}.badge.high{background:#ff2d8a;color:#141414;border-color:#141414}.badge.moist{background:#dcd0f0;color:#40226b;border-color:#40226b}
.badge.tox{background:#1d2320;color:#fff}.badge.tox.mild{background:#1f9e5a}.badge.tox.spn{background:#fff;color:#1d2320}
.more{display:none;margin-top:10px}
.card.open .more{display:block}
.more h4{margin:10px 0 2px;color:var(--c2)}
.more p{margin:0}
.hint{display:block;margin-top:8px;color:var(--mut);font-size:.62rem}
.card.open .hint{display:none}
.card.open{flex-direction:column}
.card.open .photo{width:100%;height:auto;aspect-ratio:1/1;max-height:420px}
.ph{position:relative;width:100%;height:100%;min-height:110px;overflow:hidden;background:var(--c)}
.ph span{position:absolute;display:block;background:rgba(255,255,255,.28)}
.ph .s1{width:60%;height:60%;border-radius:50%;left:-15%;bottom:-20%}
.ph .s2{width:40%;height:40%;border-radius:22%;right:8%;top:10%;background:rgba(0,0,0,.15)}
.ph .s3{width:30%;height:12%;border-radius:99px;right:-5%;bottom:15%}
.ph b{position:absolute;inset:0;display:grid;place-items:center;font:700 clamp(1.6rem,8vw,3rem) "JetBrains Mono",monospace;color:var(--cink);letter-spacing:-.04em}
.install{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-top:12px}.install .mono{color:var(--mut);text-transform:none;letter-spacing:0}.temp{margin:8px 0 0;font-size:.9rem}.empty{padding:30px;text-align:center;color:var(--mut)}
.quick{margin:36px 0 40px;background:#fff;border:2px solid var(--ink);border-radius:var(--r);padding:6px 18px 18px;box-shadow:none}
.quick h2{margin-top:14px}
.quick ul{padding-left:20px;margin:0}.quick li{margin:4px 0}.quick li::marker{color:var(--mag)}
.qp h4{margin:16px 0 2px;color:var(--pur)}.qp p{margin:0}
footer{padding:0 0 30px;color:var(--mut)}
@media(max-width:699px){
.chip{padding:6px 10px;font-size:.8rem}
.filters{display:flex;flex-direction:column}
.fsearch{order:1;margin-bottom:8px}
.ftop{display:flex;order:2;align-items:center;gap:10px;min-width:0;margin-bottom:2px}
.fpanel{order:3;margin-top:8px}
.filters.collapsed .fpanel{display:none}
.ftoggle{flex:none}
.ftoggle::after{content:" +"}
.ftoggle[aria-expanded="true"]::after{content:" \2212"}
.fsum{color:var(--mut);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0;text-transform:none;letter-spacing:0}
.filters:not(.collapsed) .fsum{display:none}
}
@media(min-width:700px) and (min-height:860px){
.filters{position:sticky;top:0}
}
@media(min-width:700px){
.wrap{padding:0 24px}
.blocks{grid-template-columns:repeat(3,1fr)}
.grid{grid-template-columns:1fr 1fr}
.search{width:auto;min-width:260px;flex:1}
.card.open{grid-column:1/-1;flex-direction:row}
.card.open .photo{width:300px;aspect-ratio:auto;max-height:none}
}
@media print{
@page{margin:12mm}
body{background:#fff;font-size:10pt}
.filters,.hint,.count,.countrow,.empty{display:none!important}
.card[hidden]{display:flex!important}
.grid{grid-template-columns:1fr 1fr;gap:8px}
.card{break-inside:avoid;page-break-inside:avoid;box-shadow:none;border-width:1.5px}
.card .more{display:block!important}
.card.open{grid-column:auto;flex-direction:row}
.photo,.card.open .photo{width:80px;aspect-ratio:auto;max-height:none}
.body{padding:8px 10px}
.blocks{grid-template-columns:repeat(3,1fr)}
.quick{break-inside:avoid;box-shadow:none}
*{-webkit-print-color-adjust:exact;print-color-adjust:exact}
}
'''

JS = r'''
(function(){
var KEY="plantcare.filters.v1",ROWS=["block","light","window","cold","dog","rot"];
var LABEL={block:"Block",light:"Light",window:"Window",cold:"Cold",dog:"Dogs",rot:"Rot"};
var st={block:[],light:[],window:[],cold:[],dog:[],rot:[],sort:"block",q:""};
var cards=[].slice.call(document.querySelectorAll(".card"));
var grid=document.getElementById("grid");
var RK={
 tox:{high:0,mild:1,spines:2,safe:3},
 window:{great:0,ok:1,no:2},
 rot:{low:0,medium:1,high:2,moist:3}
};
cards.forEach(function(c,i){c.dataset.i=i});
var cnt=document.getElementById("count"),emp=document.getElementById("empty"),
 fsum=document.getElementById("fsum"),ftoggle=document.getElementById("ftoggle"),
 filters=document.getElementById("filters"),qel=document.getElementById("q");
var chipEls=[].slice.call(document.querySelectorAll(".chip[data-f]"));
function chipsOf(f){return chipEls.filter(function(x){return x.dataset.f===f})}
function allowed(f){return chipsOf(f).map(function(x){return x.dataset.v}).filter(function(v){return v!=="all"})}
function has(c,f){var vals=(" "+c.dataset[f]+" ");return st[f].some(function(v){return vals.indexOf(" "+v+" ")>-1})}
function key(c,mode){
 var d=c.dataset;
 if(mode==="tox")return RK.tox[d.dog];
 if(mode==="cold")return +d.cold;
 if(mode==="window")return RK.window[d.window];
 if(mode==="rot")return RK.rot[d.rot];
 return 0;
}
function cmp(a,b){
 var r=0;
 if(st.sort==="az")r=a.dataset.name<b.dataset.name?-1:a.dataset.name>b.dataset.name?1:0;
 else r=key(a,st.sort)-key(b,st.sort);
 return r||(a.dataset.block-b.dataset.block)||(a.dataset.i-b.dataset.i);
}
function active(){return ROWS.reduce(function(n,f){return n+(st[f].length?1:0)},0)}
function summary(){
 var parts=[];
 ROWS.forEach(function(f){
  if(!st[f].length)return;
  var t=st[f].map(function(v){var c=chipsOf(f).filter(function(x){return x.dataset.v===v})[0];return c.textContent.replace(/^Block /,"")});
  parts.push(LABEL[f]+" "+t.join("/"));
 });
 if(st.q)parts.push('"'+st.q+'"');
 return parts.length?parts.join(" · "):"No filters";
}
function save(){
 try{localStorage.setItem(KEY,JSON.stringify({f:ROWS.reduce(function(o,f){o[f]=st[f];return o},{}),sort:st.sort}))}catch(e){}
}
function load(){
 try{
  var o=JSON.parse(localStorage.getItem(KEY)||"null");
  if(!o||typeof o!=="object")return;
  ROWS.forEach(function(f){
   var a=o.f&&o.f[f],ok=allowed(f);
   if(Array.isArray(a))st[f]=a.filter(function(v){return ok.indexOf(v)>-1});
  });
  if(typeof o.sort==="string"&&allowed("sort").indexOf(o.sort)>-1)st.sort=o.sort;
 }catch(e){}
}
function sync(){
 ROWS.forEach(function(f){
  chipsOf(f).forEach(function(x){
   var on=x.dataset.v==="all"?st[f].length===0:st[f].indexOf(x.dataset.v)>-1;
   x.classList.toggle("on",on);x.setAttribute("aria-pressed",on);
  });
 });
 chipsOf("sort").forEach(function(x){
  var on=x.dataset.v===st.sort;x.classList.toggle("on",on);x.setAttribute("aria-pressed",on);
 });
 var n=active();
 ftoggle.firstChild.nodeValue="Filters"+(n?" ("+n+")":"");
 fsum.textContent=summary();
}
function apply(){
 var n=0;
 cards.forEach(function(c){
  var ok=ROWS.every(function(f){return !st[f].length||has(c,f)})&&(!st.q||c.dataset.search.indexOf(st.q)>-1);
  c.hidden=!ok; if(ok)n++;
 });
 cards.slice().sort(cmp).forEach(function(c){grid.appendChild(c)});
 cnt.textContent="Showing "+n+" of "+cards.length+" plants";
 emp.hidden=n>0;
 sync();
}
chipEls.forEach(function(b){
 b.addEventListener("click",function(){
  var f=b.dataset.f,v=b.dataset.v;
  if(f==="sort")st.sort=v;
  else if(v==="all")st[f]=[];
  else{var i=st[f].indexOf(v);if(i>-1)st[f].splice(i,1);else st[f].push(v)}
  apply();save();
 });
});
qel.addEventListener("input",function(e){st.q=e.target.value.trim().toLowerCase();apply()});
document.getElementById("clear").addEventListener("click",function(){
 ROWS.forEach(function(f){st[f]=[]});st.q="";qel.value="";apply();save();
});
ftoggle.addEventListener("click",function(){
 var c=filters.classList.toggle("collapsed");ftoggle.setAttribute("aria-expanded",!c);
});
function toggle(c){var o=c.classList.toggle("open");c.setAttribute("aria-expanded",o)}
cards.forEach(function(c){
 c.addEventListener("click",function(){toggle(c)});
 c.addEventListener("keydown",function(e){if(e.key==="Enter"||e.key===" "){e.preventDefault();toggle(c)}});
});
var m=new Date().getMonth(),winter=(m>=10||m<=1);
document.querySelectorAll(".blk-card").forEach(function(b){
 b.querySelector(winter?".cad-w":".cad-g").classList.add("now");
});
document.getElementById("season").textContent=winter?"Right now it's winter (Nov–Feb): use the winter cadence.":"Right now it's growing season (Mar–Oct): use the growing cadence.";
load();apply();
})();
/* install (as in Thunder Plus): offer the browser's install prompt when it can install; nothing shows inside the installed app */
(function(){
var evt=null,$=function(i){return document.getElementById(i)};
function st(btn,msg){$("installRow").hidden=false;$("installBtn").hidden=!btn;$("installMsg").textContent=msg}
var DONE="Installed. Look for Plant Care in your app list.";
addEventListener("beforeinstallprompt",function(e){e.preventDefault();evt=e;st(true,"Adds Plant Care to this device as its own app.")});
$("installBtn").addEventListener("click",function(){if(!evt)return;evt.prompt();evt.userChoice.then(function(r){evt=null;st(false,r.outcome==="accepted"?DONE:"Not installed.")})});
addEventListener("appinstalled",function(){evt=null;st(false,DONE)});
if(!matchMedia("(display-mode: standalone)").matches&&navigator.getInstalledRelatedApps)
 navigator.getInstalledRelatedApps().then(function(a){if(a.length)st(false,"Already installed on this device. Open it from your app list.")}).catch(function(){});
if("serviceWorker" in navigator&&location.protocol==="https:")navigator.serviceWorker.register("sw.js").catch(function(){});
})();

'''

out = f'''<!DOCTYPE html>
<html lang="en">
<head>
<link rel="manifest" href="manifest.webmanifest">
<meta name="theme-color" content="#e9e8e3">
<link rel="icon" href="icons/icon-192.png?v=2">
<link rel="apple-touch-icon" href="icons/icon-192.png?v=2">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Plant Care Guide</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700;800&amp;display=swap">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<header>
<div class="mono eyebrow">Succulents &amp; cacti · reference</div>
<h1>Plant Care<i></i></h1>
<p class="sub">{n} plants, organized by plant. Tap a card for the full details.</p>
<div class="rule"><span class="mono">The golden rule</span>{E(TIPS["golden_rule"])}</div>
<div class="install" id="installRow" hidden><button class="chip on" id="installBtn" hidden>Install app</button><span class="mono" id="installMsg"></span></div>
</header>
<section aria-labelledby="wn">
<h2 id="wn">Watering nights</h2>
<div class="blocks">{blocks_html}</div>
<p class="season mono" id="season"></p>
</section>
<section>
<div class="filters collapsed" id="filters">
<div class="ftop"><button class="chip ftoggle" id="ftoggle" aria-expanded="false" aria-controls="fpanel">Filters</button><span class="fsum mono" id="fsum"></span></div>
<div class="fpanel" id="fpanel">
<div class="row" data-row="block"><span class="mono">Block</span>{chips_b}</div>
<div class="row" data-row="light"><span class="mono">Light</span>{chips_l}</div>
<div class="row" data-row="window"><span class="mono">Window</span>{chips_w}</div>
<div class="row" data-row="cold"><span class="mono">Cold</span>{chips_c}</div>
<div class="row" data-row="dog"><span class="mono">Dogs</span>{chips_d}</div>
<div class="row" data-row="rot"><span class="mono">Rot risk</span>{chips_r}</div>
<div class="row" data-row="sort"><span class="mono">Sort</span>{chips_s}</div>
</div>
<div class="row fsearch"><input id="q" class="search" type="search" placeholder="Search plants, latin names, notes" aria-label="Search plants"></div>
</div>
<div class="countrow"><span class="count mono" id="count"></span><button type="button" class="linkbtn mono" id="clear">Clear all</button></div>
<div class="grid" id="grid">
{chr(10).join(card(p) for p in d["plants"])}
</div>
<div class="empty" id="empty" hidden>No plants match those filters.</div>
</section>
<section class="quick" aria-labelledby="qr">
<h2 id="qr">Quick reference</h2>
<h4 class="mono" style="color:var(--pur);margin:0 0 6px">Signs to watch for</h4>
<ul>{signs}</ul>
{qr}
</section>
<footer class="mono">Plant Care Guide · {n} plants</footer>
</div>
<script>{JS}</script>
</body>
</html>
'''
open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(out)
print("wrote", len(out), "bytes")
