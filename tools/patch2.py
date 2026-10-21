import sys, json

src, textbook, dst, url = sys.argv[1:5]
s = open(src, encoding='utf-8').read()
TXT = json.load(open(textbook, encoding='utf-8'))['data']

def rep(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)

# 1. embedded audio goes away; clips are served as files under audio/<deck>/
i = s.find('<script>window.AUD=')
j = s.find('</script>', i) + len('</script>')
assert i > 0
s = s[:i] + s[j:]

# 2. css
rep('.mic{display:inline-block;',
    '.sync{font-size:.8rem;color:var(--muted);margin:-6px 0 0}\n'
    '.deck button{font-size:.92rem;padding:12px 6px}\n'
    '.mic{display:inline-block;')

# 3. header + deck switcher
rep("<h1>DRIVER'S VOCAB · 驾照词汇</h1>", '<h1 id="ttl">DRIVER\'S VOCAB · 驾照词汇</h1>')
rep('<p>87 个加州驾照词汇和短语 · 听美音 · 语音检测 · 拼写</p>', '<p id="sub">87 个加州驾照词汇和短语 · 听美音 · 语音检测 · 拼写</p>')
rep('<div class="bar">\n    <div class="seg" role="group" aria-label="练习模式">',
    '<div class="seg deck" role="group" aria-label="选择词表">\n'
    '    <button id="dDrv" aria-pressed="true">🚗 加州驾照 87 词</button>\n'
    '    <button id="dTxt" aria-pressed="false">📖 教材生词 68 词</button>\n'
    '  </div>\n\n'
    '  <div class="bar">\n    <div class="seg" role="group" aria-label="练习模式">')

# 4. word lists and decks
rep('const D=[', 'const mk=(r,i)=>({n:i+1,w:r[0],zh:r[1],ipa:r[2],ph:r[3],phzh:r[4]});\nconst DRV=[')
rep('].map((r,i)=>({n:i+1,w:r[0],zh:r[1],ipa:r[2],ph:r[3],phzh:r[4]}));',
    '].map(mk);\nconst TXT=' + json.dumps([r[:5] for r in TXT], ensure_ascii=False) + '.map(mk);')
rep('const GROUPS=[["全部 87 个"', 'const DRV_G=[["全部 87 个"')
rep('const SPK=',
    'const TXT_G=[["全部 68 个",1,68],["我圈的生词 · 1–49",1,49],["教材蓝色新词 · 50–68",50,68]];\n'
    'const DECKS={\n'
    ' drv:{D:DRV,G:DRV_G,key:"drv-st2",ttl:"DRIVER\'S VOCAB · 驾照词汇",sub:"87 个加州驾照词汇和短语 · 听美音 · 语音检测 · 拼写"},\n'
    ' txt:{D:TXT,G:TXT_G,key:"txt-st",ttl:"TEXTBOOK VOCAB · 教材生词",sub:"68 个教材生词（Animal Behavior，p162–172）· 听美音 · 语音检测 · 拼写"}};\n'
    'let deck="drv";try{if(DECKS[localStorage.getItem("drv-deck")])deck=localStorage.getItem("drv-deck")}catch(e){}\n'
    'let D=DECKS[deck].D, GROUPS=DECKS[deck].G;\n'
    'const SPK=')

# 5. tips
rep('③ 按住「🎤 读单词」或「🎤 读短语」开口读，松开后看手机听懂了没有',
    '③ 点「🎤 读单词」或「🎤 读短语」开口读，读完停一下会自动结束（也可以再点一下结束），然后看手机听懂了没有')
rep('进度只保存在当前这台设备的浏览器里。',
    '进度会自动同步到你的 Google Drive（文件夹「Freya的新单词」里的学习记录表），iPhone 和 iPad 进度互通。')

# 6. per-deck progress
rep('let st={};try{st=JSON.parse(localStorage.getItem("drv-st2")||"{}")}catch(e){}\n'
    'const save=()=>{try{localStorage.setItem("drv-st2",JSON.stringify(st))}catch(e){}};',
    'const stLoad=d=>{try{return JSON.parse(localStorage.getItem(DECKS[d].key)||"{}")||{}}catch(e){return {}}};\n'
    'const stSave=(d,o)=>{try{localStorage.setItem(DECKS[d].key,JSON.stringify(o))}catch(e){}};\n'
    'let st=stLoad(deck);\n'
    'const save=()=>{stSave(deck,st);syncNote()};')
rep('GROUPS.forEach((x,i)=>{const o=document.createElement("option");o.value=i;o.textContent=x[0];$("grp").appendChild(o)});',
    'function fillGroups(){$("grp").innerHTML="";GROUPS.forEach((x,i)=>{const o=document.createElement("option");o.value=i;o.textContent=x[0];$("grp").appendChild(o)})}\nfillGroups();')

# 7. audio from files
rep('  const b64=window.AUD&&window.AUD[key]; if(!b64)return;\n', '  if(!key)return;\n')
rep('player.src="data:audio/mpeg;base64,"+b64;', 'player.src="audio/"+deck+"/"+key+".mp3";')

# 8. tap once to talk; recognition ends by itself after a pause
rep('  stopAsked=false;talkCb=onAlts;let finals=[],done=false;\n'
    '  const finish=()=>{if(done)return;done=true;',
    '  stopAsked=false;talkCb=onAlts;let finals=[],done=false;\n'
    '  const guard=setTimeout(stopTalk,12000);\n'
    '  const finish=()=>{if(done)return;done=true;clearTimeout(guard);stopAsked=true;if(mr&&mr.state!=="inactive")mr.stop();')
rep('rec.maxAlternatives=5;rec.continuous=true;', 'rec.maxAlternatives=5;rec.continuous=false;')
rep('rec.onerror=e=>{if(e.error==="not-allowed"||e.error==="service-not-allowed"){done=true;onErr(',
    'rec.onerror=e=>{if(e.error==="not-allowed"||e.error==="service-not-allowed"){done=true;clearTimeout(guard);stopAsked=true;if(mr&&mr.state!=="inactive")mr.stop();onErr(')
rep('rec.onend=finish;rec.start()}catch(e){}}', 'rec.onend=finish;rec.start()}catch(e){finish()}}')
rep('mr.start();if(stopAsked)mr.stop()}', 'mr.start();if(stopAsked)mr.stop()}')  # unchanged, asserts structure
rep('<button class="btn talk" id="tW">🎤 按住 读单词</button><button class="btn talk" id="tP">🎤 按住 读短语</button>',
    '<button class="btn talk" id="tW" data-l="🎤 读单词">🎤 读单词</button><button class="btn talk" id="tP" data-l="🎤 读短语">🎤 读短语</button>')
rep('${SR?"按住按钮开口读，读完松开。":', '${SR?"点一下按钮开口读，读完停一下会自动结束。":')
rep('''  const bindTalk=(btn,t)=>{
    const down=e=>{e.preventDefault();if(btn.classList.contains("rec"))return;tgt=t;lastRes="";
      btn.classList.add("rec");$("res").innerHTML='<span class="hint">正在听……读完松开</span>';
      startTalk(alts=>run(alts),showMine,msg=>{$("res").innerHTML=`<span class="verdict bad">${msg}</span>`})};
    const up=()=>{if(!btn.classList.contains("rec"))return;btn.classList.remove("rec");$("res").innerHTML='<span class="hint">识别中……</span>';stopTalk()};
    btn.addEventListener("pointerdown",down);
    ["pointerup","pointercancel","pointerleave"].forEach(ev=>btn.addEventListener(ev,up));
    btn.addEventListener("contextmenu",e=>e.preventDefault())};''',
'''  const bindTalk=(btn,t)=>{
    const reset=()=>{btn.classList.remove("rec");btn.textContent=btn.dataset.l};
    btn.onclick=()=>{
      if(btn.classList.contains("rec")){btn.textContent="识别中…";$("res").innerHTML='<span class="hint">识别中……</span>';stopTalk();return}
      if(document.querySelector(".talk.rec"))return;
      player.pause();if(playingBtn){playingBtn.classList.remove("playing");playingBtn=null}
      tgt=t;lastRes="";btn.classList.add("rec");btn.textContent="■ 正在听（点我结束）";
      $("res").innerHTML='<span class="hint">正在听……读完停一下就会自动结束</span>';
      startTalk(alts=>{reset();run(alts)},showMine,msg=>{reset();$("res").innerHTML=`<span class="verdict bad">${msg}</span>`})};
    btn.addEventListener("contextmenu",e=>e.preventDefault())};''')
rep("没听清，按住按钮离手机近一点再读一次。", "没听清，离手机近一点，点按钮再读一次。")

# 9. sync (two decks, two sheets) + deck switching
SYNC = r'''
/* 同步到 Google Drive */
const SYNC_URL="__URL__";
const DEV=/iPad/.test(navigator.userAgent)||(/Macintosh/.test(navigator.userAgent)&&navigator.maxTouchPoints>1)?"iPad":/iPhone/.test(navigator.userAgent)?"iPhone":/Mac/.test(navigator.userAgent)?"Mac":"其他设备";
let syncKey="";try{syncKey=localStorage.getItem("drv-key")||""}catch(e){}
{const m=location.hash.match(/k=([\w-]+)/);if(m){syncKey=m[1];try{localStorage.setItem("drv-key",syncKey)}catch(e){}
  try{history.replaceState(null,"",location.pathname+location.search)}catch(e){}}}
let syncQ=[];try{syncQ=JSON.parse(localStorage.getItem("drv-q")||"[]")}catch(e){}
syncQ.forEach(q=>{q.d=q.d||"drv"});
const known={drv:{},txt:{}};let syncBusy=false,syncAgain=false,syncTimer=0;
const saveQ=()=>{try{localStorage.setItem("drv-q",JSON.stringify(syncQ))}catch(e){}};
const syncEl=document.createElement("div");syncEl.className="sync";syncEl.id="sync";$("stats").after(syncEl);
const syncShow=t=>{syncEl.textContent=t};
const deckSt=d=>d===deck?st:stLoad(d);
function enqueueNew(){let added=false;
  for(const d in DECKS){const o=deckSt(d),L=DECKS[d].D;
    for(const k in o){const n=+k;for(const t of ["say","spell"]){
      if(o[k][t]&&!(known[d][k]&&known[d][k][t])&&!syncQ.some(q=>q.d===d&&q.n===n&&q.t===t)){const x=L[n-1]||{};
        syncQ.push({d,n,t,w:x.w||"",zh:x.zh||"",at:Date.now(),dev:DEV});added=true}}}}
  if(added)saveQ();return added}
function mergeRemote(d,r){let changed=false;const o=deckSt(d);
  for(const k in r){for(const t of ["say","spell"]){if(r[k][t]){
    (known[d][k]||(known[d][k]={}))[t]=true;
    if(!(o[k]&&o[k][t])){(o[k]||(o[k]={}))[t]=true;changed=true}}}}
  if(changed)stSave(d,o);
  return changed&&d===deck}
function syncNote(){if(!syncKey)return;enqueueNew();clearTimeout(syncTimer);syncTimer=setTimeout(syncRun,800)}
async function syncRun(){
  if(!syncKey){syncShow("☁️ 还没连接 Google Drive：用带同步码的链接打开一次即可。");return}
  if(syncBusy){syncAgain=true;return}
  syncBusy=true;syncShow("☁️ 正在同步…");let changed=false;
  try{
    for(const d in DECKS){
      const g=await (await fetch(SYNC_URL+"?deck="+d+"&key="+encodeURIComponent(syncKey),{cache:"no-store"})).json();
      if(!g.ok)throw new Error(g.error==="key"?"同步码不对":"同步失败");
      if(mergeRemote(d,g.st||{}))changed=true}
    enqueueNew();
    for(const d in DECKS){const sent=syncQ.filter(q=>q.d===d);if(!sent.length)continue;
      const p=await (await fetch(SYNC_URL,{method:"POST",headers:{"Content-Type":"text/plain;charset=utf-8"},body:JSON.stringify({key:syncKey,deck:d,events:sent})})).json();
      if(!p.ok)throw new Error("上传失败");
      syncQ=syncQ.filter(q=>!sent.includes(q));saveQ();
      if(mergeRemote(d,p.st||{}))changed=true}
    const t=new Date();syncShow("☁️ 已同步到 Google Drive · "+t.getHours()+":"+String(t.getMinutes()).padStart(2,"0"));
    if(changed)render();
  }catch(e){
    syncShow("☁️ "+(navigator.onLine===false?"现在离线，联网后自动上传":(e.message||"同步失败")+"，稍后自动重试")+(syncQ.length?"（待上传 "+syncQ.length+" 条）":""));
  }finally{syncBusy=false;if(syncAgain){syncAgain=false;syncTimer=setTimeout(syncRun,500)}}
}
window.addEventListener("online",syncRun);
document.addEventListener("visibilitychange",()=>{if(document.visibilityState==="visible")syncRun()});

/* 切换词表 */
function setDeck(k){
  deck=k;D=DECKS[k].D;GROUPS=DECKS[k].G;st=stLoad(k);
  g=0;idx=0;shown=false;lastRes="";spellMsg="";myUrl=null;myFor=0;
  try{localStorage.setItem("drv-deck",k)}catch(e){}
  fillGroups();$("grp").value="0";
  $("ttl").textContent=DECKS[k].ttl;$("sub").textContent=DECKS[k].sub;
  $("dDrv").setAttribute("aria-pressed",k==="drv");$("dTxt").setAttribute("aria-pressed",k==="txt");
  player.pause();render()}
$("dDrv").onclick=()=>{if(deck!=="drv")setDeck("drv")};
$("dTxt").onclick=()=>{if(deck!=="txt")setDeck("txt")};
'''.replace('__URL__', url)

rep('$("onlyAgain").onchange=()=>{idx=0;shown=false;lastRes="";render()};\nrender();\n</script>',
    '$("onlyAgain").onchange=()=>{idx=0;shown=false;lastRes="";render()};\n' + SYNC + 'setDeck(deck);\nsyncRun();\n</script>')

open(dst, 'w', encoding='utf-8').write(s)
print('ok', len(s.encode('utf-8')))

# 10. name and icon
s = open(dst, encoding='utf-8').read()
def rep2(old, new):
    global s
    assert s.count(old) == 1, old
    s = s.replace(old, new)
rep2('<title>Freya 驾照词汇卡</title>', '<title>Freya 单词卡</title>')
rep2('<meta name="apple-mobile-web-app-title" content="驾照词汇">',
     '<meta name="apple-mobile-web-app-title" content="Freya单词卡">\n'
     '<link rel="icon" type="image/svg+xml" href="icon-v2.svg">\n'
     '<link rel="icon" type="image/png" sizes="512x512" href="icon-512-v2.png">\n'
     '<link rel="apple-touch-icon" href="apple-touch-icon-v2.png">\n<link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon-v2.png">\n'
     '<meta name="theme-color" content="#1d6a48">')
open(dst, 'w', encoding='utf-8').write(s)
print('named', len(s.encode('utf-8')))

# 11. open home-screen icon in Safari (standalone mode breaks speech recognition and shows black screen on iPhone);
#     show any startup error on screen instead of a blank page
s = open(dst, encoding='utf-8').read()
rep2('<meta name="apple-mobile-web-app-capable" content="yes">\n', '')
rep2('<meta charset="utf-8">',
     '<meta charset="utf-8">\n'
     '<script>window.addEventListener("error",function(e){try{var d=document.createElement("pre");'
     'd.style.cssText="white-space:pre-wrap;background:#fff;color:#b00;padding:12px;margin:0;font:13px/1.4 monospace";'
     'd.textContent="页面出错，请截图发给 Claude：\\n"+(e.message||"")+"\\n"+(e.filename||"")+":"+(e.lineno||"");'
     '(document.body||document.documentElement).prepend(d)}catch(x){}});</script>')
open(dst, 'w', encoding='utf-8').write(s)
print('standalone off', len(s.encode('utf-8')))

# 12. fonts must not block the first paint (slow mobile networks showed a black screen for a long time)
s = open(dst, encoding='utf-8').read()
F = 'https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=Noto+Sans:wght@400;600&family=Noto+Sans+SC:wght@400;600&display=swap'
rep2('<link rel="stylesheet" href="' + F + '">',
     '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
     '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
     '<link rel="stylesheet" href="' + F + '" media="print" onload="this.media=\'all\'">')
open(dst, 'w', encoding='utf-8').write(s)
print('fonts async', len(s.encode('utf-8')))

# 13. iPhone: second recognition got no audio. Keep ONE microphone stream alive for the whole visit
#     (stopping its tracks also cut Safari's speech-recognition capture), start recognition only after
#     the stream is live, and retry once if recognition ends instantly with nothing heard.
s = open(dst, encoding='utf-8').read()
a = s.index('/* microphone: speech recognition + my own recording */')
b = s.index('function playUrl(')
s = s[:a] + r'''/* microphone: speech recognition + my own recording */
const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
let rec=null,mr=null,myUrl=null,myFor=0,stopAsked=false,talkCb=null,micStream=null,talkId=0;
function getMic(){
  if(micStream&&micStream.getAudioTracks().some(t=>t.readyState==="live"))return Promise.resolve(micStream);
  if(!(navigator.mediaDevices&&navigator.mediaDevices.getUserMedia))return Promise.resolve(null);
  return navigator.mediaDevices.getUserMedia({audio:{echoCancellation:true,noiseSuppression:true}}).then(s=>micStream=s)}
document.addEventListener("visibilitychange",()=>{if(document.visibilityState==="hidden"&&micStream){micStream.getTracks().forEach(t=>t.stop());micStream=null}});
function startTalk(onAlts,onRec,onErr){
  const id=++talkId;stopAsked=false;talkCb=onAlts;let finals=[],done=false,tries=0,began=0;
  try{rec&&rec.abort()}catch(e){}
  const guard=setTimeout(stopTalk,12000);
  const stopRecorder=()=>{if(mr&&mr.state!=="inactive")try{mr.stop()}catch(e){}};
  const finish=()=>{if(done||id!==talkId)return;done=true;clearTimeout(guard);stopAsked=true;stopRecorder();
    const alts=!finals.length?null:finals.length===1?finals[0]:[finals.map(s=>s[0]).join(" ")];
    if(talkCb)talkCb(alts)};
  const fail=msg=>{if(done||id!==talkId)return;done=true;clearTimeout(guard);stopAsked=true;stopRecorder();onErr(msg)};
  const listen=()=>{
    if(!SR){return}
    try{const r=new SR();rec=r;r.lang="en-US";r.interimResults=false;r.maxAlternatives=5;r.continuous=false;began=Date.now();
      r.onresult=e=>{if(id!==talkId)return;for(let i=e.resultIndex;i<e.results.length;i++)if(e.results[i].isFinal)finals.push(Array.from(e.results[i]).map(a=>a.transcript))};
      r.onerror=e=>{if(id!==talkId)return;
        if(e.error==="not-allowed"||e.error==="service-not-allowed")fail("麦克风或语音识别没有被允许。请点 Safari 地址栏左边的「大小」图标 → 网站设置 → 麦克风 → 允许，然后刷新。");
        else if(e.error==="audio-capture")fail("麦克风暂时被占用。请关掉其他正在录音或通话的 App，然后刷新页面再试。")};
      r.onend=()=>{if(id!==talkId||done)return;
        if(!finals.length&&!stopAsked&&tries<1&&Date.now()-began<1500){tries++;setTimeout(listen,150);return}
        finish()};
      r.start()}catch(e){finish()}};
  getMic().then(s=>{
    if(id!==talkId||done)return;
    if(s&&window.MediaRecorder){const chunks=[];
      try{const m=new MediaRecorder(s);mr=m;
        m.ondataavailable=e=>{if(e.data&&e.data.size)chunks.push(e.data)};
        m.onstop=()=>{if(myUrl)URL.revokeObjectURL(myUrl);myUrl=URL.createObjectURL(new Blob(chunks,{type:m.mimeType||"audio/mp4"}));onRec()};
        m.start()}catch(e){}}
    if(SR)listen();else finish()
  }).catch(()=>{if(SR)listen();else fail("打不开麦克风。请在 Safari 网站设置里允许麦克风，然后刷新。")})
}
function stopTalk(){stopAsked=true;
  setTimeout(()=>{try{rec&&rec.stop()}catch(e){};if(mr&&mr.state!=="inactive")try{mr.stop()}catch(e){}},350)}
''' + s[b:]
open(dst, 'w', encoding='utf-8').write(s)
print('mic reworked', len(s.encode('utf-8')))

# 14. diagnostics: when nothing is recognised, show why (error code, tries, ms) so Freya can screenshot it
s = open(dst, encoding='utf-8').read()
rep2('let rec=null,mr=null,myUrl=null,myFor=0,stopAsked=false,talkCb=null,micStream=null,talkId=0;',
     'let rec=null,mr=null,myUrl=null,myFor=0,stopAsked=false,talkCb=null,micStream=null,talkId=0,talkInfo="";')
rep2('const id=++talkId;stopAsked=false;talkCb=onAlts;let finals=[],done=false,tries=0,began=0;',
     'const id=++talkId;stopAsked=false;talkCb=onAlts;let finals=[],done=false,tries=0,began=0,errs=[];const t0=Date.now();talkInfo="";')
rep2('const finish=()=>{if(done||id!==talkId)return;done=true;',
     'const finish=()=>{if(done||id!==talkId)return;done=true;talkInfo=(errs.join(",")||"无错误")+" · 试"+(tries+1)+"次 · "+(Date.now()-t0)+"ms"+(micStream?"":" · 无麦克风流");')
rep2('r.onerror=e=>{if(id!==talkId)return;\n', 'r.onerror=e=>{if(id!==talkId)return;errs.push(e.error);\n')
rep2("""$("res").innerHTML=SR?'<span class="hint">没听清，离手机近一点，点按钮再读一次。</span>':"";""",
     """$("res").innerHTML=SR?'<span class="hint">没听清，离手机近一点，点按钮再读一次。</span><span class="hint" style="display:block;font-size:.75rem;opacity:.7">诊断：'+esc(talkInfo)+'</span>':"";""")
open(dst, 'w', encoding='utf-8').write(s)
print('diag', len(s.encode('utf-8')))

# 15. in-app browsers inject their own scripts; their errors arrive as a bare "Script error." with no file.
#     Only report errors that come from this page.
s = open(dst, encoding='utf-8').read()
rep2('window.addEventListener("error",function(e){try{',
     'window.addEventListener("error",function(e){if(!e.filename||e.filename.indexOf(location.origin)!==0)return;try{')
open(dst, 'w', encoding='utf-8').write(s)
print('err filter', len(s.encode('utf-8')))

# 16. home-screen web apps (iOS 26 opens them as web apps by default) have their own storage, so the
#     sync code must stay in the URL that gets saved to the home screen: do not strip #k= any more.
s = open(dst, encoding='utf-8').read()
rep2('\n  try{history.replaceState(null,"",location.pathname+location.search)}catch(e){}}}', '}}')
open(dst, 'w', encoding='utf-8').write(s)
print('keep hash', len(s.encode('utf-8')))

# 17. open instantly from the device (service worker caches the page; new versions show on next launch)
s = open(dst, encoding='utf-8').read()
rep2('setDeck(deck);\nsyncRun();\n</script>',
     'setDeck(deck);\nsyncRun();\n'
     'if("serviceWorker" in navigator)window.addEventListener("load",()=>{navigator.serviceWorker.register("sw.js").catch(()=>{})});\n</script>')
open(dst, 'w', encoding='utf-8').write(s)
print('sw', len(s.encode('utf-8')))

# 18. Safari on iPhone/iPad cannot reliably recognise speech while the page also holds the microphone
#     (diagnostic: "aborted · 12415ms" = recogniser heard nothing while the recorder had audio).
#     Recognition now runs alone and starts inside the tap; recording for comparison is its own button.
s = open(dst, encoding='utf-8').read()
a = s.index('/* microphone: speech recognition + my own recording */')
b = s.index('function playUrl(')
s = s[:a] + r'''/* microphone: speech recognition, and separately my own recording */
const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
let rec=null,mr=null,myUrl=null,myFor=0,stopAsked=false,talkCb=null,talkId=0,talkInfo="",recStream=null,recTimer=0;
function releaseMic(){if(mr&&mr.state!=="inactive")try{mr.stop()}catch(e){};if(recStream){recStream.getTracks().forEach(t=>t.stop());recStream=null}}
function startTalk(onAlts,onRec,onErr){
  const id=++talkId;stopAsked=false;talkCb=onAlts;let finals=[],done=false,tries=0,began=0,errs=[];const t0=Date.now();talkInfo="";
  releaseMic();try{rec&&rec.abort()}catch(e){}
  const guard=setTimeout(stopTalk,8000);
  const finish=()=>{if(done||id!==talkId)return;done=true;clearTimeout(guard);stopAsked=true;
    talkInfo=(errs.join(",")||"无错误")+" · 试"+(tries+1)+"次 · "+(Date.now()-t0)+"ms";
    const alts=!finals.length?null:finals.length===1?finals[0]:[finals.map(s=>s[0]).join(" ")];
    if(talkCb)talkCb(alts)};
  const fail=msg=>{if(done||id!==talkId)return;done=true;clearTimeout(guard);stopAsked=true;onErr(msg)};
  const listen=()=>{
    try{const r=new SR();rec=r;r.lang="en-US";r.interimResults=false;r.maxAlternatives=5;r.continuous=false;began=Date.now();
      r.onresult=e=>{if(id!==talkId)return;for(let i=e.resultIndex;i<e.results.length;i++)if(e.results[i].isFinal)finals.push(Array.from(e.results[i]).map(a=>a.transcript))};
      r.onerror=e=>{if(id!==talkId)return;errs.push(e.error);
        if(e.error==="not-allowed"||e.error==="service-not-allowed")fail("麦克风或语音识别没有被允许。请点 Safari 地址栏左边的「大小」图标 → 网站设置 → 麦克风 → 允许，然后刷新。");
        else if(e.error==="audio-capture")fail("麦克风暂时被占用。请关掉其他正在录音或通话的 App，然后刷新页面再试。")};
      r.onend=()=>{if(id!==talkId||done)return;
        if(!finals.length&&!stopAsked&&tries<1&&Date.now()-began<1500){tries++;setTimeout(listen,150);return}
        finish()};
      r.start()}catch(e){errs.push(String(e&&e.name||e));finish()}};
  listen()
}
function stopTalk(){stopAsked=true;try{rec&&rec.stop()}catch(e){}}
function recordMine(btn,onDone,onErr){
  if(mr&&mr.state==="recording"){clearTimeout(recTimer);mr.stop();return}
  if(!(navigator.mediaDevices&&navigator.mediaDevices.getUserMedia&&window.MediaRecorder)){onErr("这个浏览器不支持录音。");return}
  try{rec&&rec.abort()}catch(e){}
  const label=btn.textContent;
  navigator.mediaDevices.getUserMedia({audio:true}).then(s=>{recStream=s;const chunks=[];
    const m=new MediaRecorder(s);mr=m;
    m.ondataavailable=e=>{if(e.data&&e.data.size)chunks.push(e.data)};
    m.onstop=()=>{clearTimeout(recTimer);s.getTracks().forEach(t=>t.stop());if(recStream===s)recStream=null;
      btn.classList.remove("rec");btn.textContent=label;
      if(myUrl)URL.revokeObjectURL(myUrl);myUrl=URL.createObjectURL(new Blob(chunks,{type:m.mimeType||"audio/mp4"}));onDone()};
    m.start();btn.classList.add("rec");btn.textContent="■ 录音中（点我结束）";
    recTimer=setTimeout(()=>{if(m.state==="recording")m.stop()},6000)
  }).catch(()=>onErr("打不开麦克风。请在 Safari 网站设置里允许麦克风，然后刷新。"))
}
''' + s[b:]
rep2('<div class="btns"><button class="btn" id="mine"${myUrl&&myFor===x.n?"":" hidden"}>',
     '<div class="btns"><button class="btn talk" id="recMe">⏺ 录一遍对比</button></div>\n'
     '        <div class="btns"><button class="btn" id="mine"${myUrl&&myFor===x.n?"":" hidden"}>')
rep2('$("mine").onclick=e=>{if(myUrl)playUrl(myUrl,e.currentTarget)};',
     '$("mine").onclick=e=>{if(myUrl)playUrl(myUrl,e.currentTarget)};\n'
     '  $("recMe").onclick=e=>{player.pause();recordMine(e.currentTarget,showMine,msg=>{$("res").innerHTML=`<span class="verdict bad">${msg}</span>`})};')
rep2('④ 点「听我的录音」和标准音对比', '④ 点「⏺ 录一遍对比」录下自己的读音（再点一下或 6 秒后结束），然后点「听我的录音」和标准音对比')
open(dst, 'w', encoding='utf-8').write(s)
print('split rec', len(s.encode('utf-8')))

# 19. trace which capture stages Safari reached (a=audio started, s=sound, p=speech, r=result),
#     and when nothing is heard offer keyboard dictation in place on the same card.
s = open(dst, encoding='utf-8').read()
rep2('let finals=[],done=false,tries=0,began=0,errs=[];const t0=Date.now();talkInfo="";\n  releaseMic();',
     'let finals=[],done=false,tries=0,began=0,errs=[],evs="";const t0=Date.now();talkInfo="";\n  releaseMic();')
rep2('talkInfo=(errs.join(",")||"无错误")+" · 试"+(tries+1)+"次 · "+(Date.now()-t0)+"ms";',
     'talkInfo=(errs.join(",")||"无错误")+" · 事件 "+(evs||"无")+" · 试"+(tries+1)+"次 · "+(Date.now()-t0)+"ms"+(navigator.standalone||matchMedia("(display-mode: standalone)").matches?" · 网页App":" · 浏览器");')
rep2('r.onresult=e=>{if(id!==talkId)return;for(',
     'r.onstart=()=>{evs+="o"};r.onaudiostart=()=>{evs+="a"};r.onsoundstart=()=>{evs+="s"};r.onspeechstart=()=>{evs+="p"};\n'
     '      r.onresult=e=>{if(id!==talkId)return;evs+="r";for(')
rep2("""opacity:.7">诊断：'+esc(talkInfo)+'</span>':"";return}""",
     """opacity:.7">诊断：'+esc(talkInfo)+'</span>':"";
      if(SR){inp.hidden=false;inp.value="";inp.placeholder="改用键盘听写：点这里，再点键盘上的 🎤（键盘先切到英文）"}return}""")
open(dst, 'w', encoding='utf-8').write(s)
print('trace+dictation', len(s.encode('utf-8')))

# 20. clips were re-mastered louder (+11 dB with limiter); bump the query so devices fetch the new files
s = open(dst, encoding='utf-8').read()
rep2('player.src="audio/"+deck+"/"+key+".mp3";', 'player.src="audio/"+deck+"/"+key+".mp3?v=2";')
open(dst, 'w', encoding='utf-8').write(s)
print('audio v2', len(s.encode('utf-8')))

# 21. diagnostics: how many recognitions this page load, and whether a clip was played since the last one
s = open(dst, encoding='utf-8').read()
rep2('  if(!key)return;\n', '  if(!key)return;\n  window.__played=1;\n')
rep2('talkInfo=(errs.join(",")||"无错误")+" · 事件 "+(evs||"无")',
     'talkInfo=(errs.join(",")||"无错误")+" · 事件 "+(evs||"无")+" · 第"+talkId+"次"+(window.__playedBefore?" · 之前放过读音":" · 之前没放读音")')
rep2('releaseMic();try{rec&&rec.abort()}catch(e){}\n  const guard=setTimeout(stopTalk,8000);',
     'releaseMic();try{rec&&rec.abort()}catch(e){}\n  window.__playedBefore=window.__played;window.__played=0;\n  const guard=setTimeout(stopTalk,8000);')
open(dst, 'w', encoding='utf-8').write(s)
print('diag2', len(s.encode('utf-8')))

# 22. iPad diagnostic "事件 oa · 之前放过读音 · 网页App": capture started but delivered silence right after
#     clip playback. Fully unload the player before listening, and if 2.5 s pass with audio started but no
#     sound, restart recognition once (tagged "|" in the event trace).
s = open(dst, encoding='utf-8').read()
rep2('  window.__playedBefore=window.__played;window.__played=0;\n  const guard=setTimeout(stopTalk,8000);',
     '  window.__playedBefore=window.__played;window.__played=0;\n'
     '  try{player.pause();player.removeAttribute("src");player.load()}catch(e){}\n'
     '  if(playingBtn){playingBtn.classList.remove("playing");playingBtn=null}\n'
     '  let guard=setTimeout(stopTalk,8000);')
rep2('''    try{const r=new SR();rec=r;r.lang="en-US";r.interimResults=false;r.maxAlternatives=5;r.continuous=false;began=Date.now();
      r.onstart=()=>{evs+="o"};r.onaudiostart=()=>{evs+="a"};r.onsoundstart=()=>{evs+="s"};r.onspeechstart=()=>{evs+="p"};
      r.onresult=e=>{if(id!==talkId)return;''',
'''    try{const r=new SR();rec=r;r.lang="en-US";r.interimResults=false;r.maxAlternatives=5;r.continuous=false;began=Date.now();let heard=false;
      const live=()=>!r.__retired&&id===talkId&&!done;
      r.onstart=()=>{evs+="o"};r.onaudiostart=()=>{evs+="a"};r.onsoundstart=()=>{evs+="s";heard=true};r.onspeechstart=()=>{evs+="p";heard=true};
      setTimeout(()=>{if(!live()||heard||finals.length||stopAsked||tries>=1)return;
        tries++;evs+="|";r.__retired=true;try{r.abort()}catch(e){}
        clearTimeout(guard);guard=setTimeout(stopTalk,6000);setTimeout(listen,300)},2500);
      r.onresult=e=>{if(!live())return;''')
rep2('r.onerror=e=>{if(id!==talkId)return;errs.push(e.error);', 'r.onerror=e=>{if(!live())return;errs.push(e.error);')
rep2('r.onend=()=>{if(id!==talkId||done)return;', 'r.onend=()=>{if(!live())return;')
open(dst, 'w', encoding='utf-8').write(s)
print('silent retry', len(s.encode('utf-8')))

# 23. Safari diagnostic "oa|oa · 第5次": after a few uses the capture stays silent for the rest of the page.
#     (a) pin the audio session to play-and-record (Safari 16.4+ Audio Session API) so playback and
#         recognition stop switching categories; (b) offer a one-tap reload that keeps the current card.
s = open(dst, encoding='utf-8').read()
rep2('function startTalk(onAlts,onRec,onErr){\n',
     'function pinSession(){try{if(navigator.audioSession&&navigator.audioSession.type!=="play-and-record")navigator.audioSession.type="play-and-record"}catch(e){}}\n'
     'function startTalk(onAlts,onRec,onErr){\n  pinSession();\n')
rep2('function recordMine(btn,onDone,onErr){\n', 'function recordMine(btn,onDone,onErr){\n  pinSession();\n')
rep2('+(navigator.standalone||matchMedia("(display-mode: standalone)").matches?" · 网页App":" · 浏览器");',
     '+(navigator.standalone||matchMedia("(display-mode: standalone)").matches?" · 网页App":" · 浏览器")+(navigator.audioSession?" · 会话 "+navigator.audioSession.type:" · 无会话API");')
rep2('if(SR){inp.hidden=false;inp.value="";inp.placeholder="改用键盘听写：点这里，再点键盘上的 🎤（键盘先切到英文）"}return}',
     'if(SR){inp.hidden=false;inp.value="";inp.placeholder="改用键盘听写：点这里，再点键盘上的 🎤（键盘先切到英文）";'
     '$("res").insertAdjacentHTML("beforeend",\'<div class="btns" style="margin-top:8px"><button class="btn" id="fixSR" type="button">🔄 刷新恢复识别（停在这个词）</button></div>\');'
     '$("fixSR").onclick=()=>{try{sessionStorage.setItem("drv-resume",JSON.stringify({deck,mode,g,idx,shown:true,only:$("onlyAgain").checked}))}catch(e){};location.reload()}}return}')
rep2('setDeck(deck);\nsyncRun();\n',
     'setDeck(deck);\n'
     '{let r=null;try{r=JSON.parse(sessionStorage.getItem("drv-resume")||"null");sessionStorage.removeItem("drv-resume")}catch(e){}\n'
     ' if(r&&DECKS[r.deck]){if(r.deck!==deck)setDeck(r.deck);mode=r.mode||"say";g=+r.g||0;$("grp").value=String(g);$("onlyAgain").checked=!!r.only;idx=+r.idx||0;shown=!!r.shown;render();\n'
     '  setTimeout(()=>{const res=$("res");if(res)res.innerHTML=\'<span class="hint">已刷新。现在点「🎤 读单词」或「🎤 读短语」再读一次。</span>\'},0)}}\n'
     'syncRun();\n')
open(dst, 'w', encoding='utf-8').write(s)
print('session+resume', len(s.encode('utf-8')))
