import os, pathlib, tempfile
URL = (pathlib.Path(__file__).resolve().parent.parent / "index.html").as_uri()
TMP = tempfile.gettempdir()
CHROME = os.environ.get("CHROME_PATH") or None   # facultatif : chemin d'un Chrome/Chromium déjà installé
from playwright.sync_api import sync_playwright
MOCK = r"""
(()=>{
 const S = JSON.parse(localStorage.getItem('__server')||'{}'); // fake server persisted across reloads
 window.__failNext = +(localStorage.getItem('__fail')||0);
 const save=()=>localStorage.setItem('__server',JSON.stringify(S));
 let listeners=[];
 const emit=(fromCache)=>listeners.forEach(f=>f({metadata:{fromCache,hasPendingWrites:false},docs:Object.entries(S).map(([id,v])=>({id,exists:true,data:()=>v}))}));
 const col={doc:id=>({set:d=>new Promise((res,rej)=>setTimeout(()=>{ if(window.__failNext>0){window.__failNext--;rej({code:'unavailable',message:'net'});return} S[id]=JSON.parse(JSON.stringify(d));save();res();emit(false)},30))}),
   onSnapshot:(f,e)=>{listeners.push(f);setTimeout(()=>emit(false),50);return()=>{}}};
 window.claude={use:async n=>n==='db'?{collection:()=>col}:n==='user'?{id:async()=>'u1'}:null};
})();
"""
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CHROME)
    ctx=b.new_context(viewport={'width':1280,'height':900});ctx.add_init_script(MOCK)
    pg=ctx.new_page();errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL);pg.wait_for_timeout(300)
    print('1 status:',pg.inner_text('#status'))
    # simulate network failure for next 3 writes
    pg.evaluate("window.__failNext=3")
    pg.click('#newBtn');pg.fill('#f-client','Léa');pg.click('.chip[data-k=semi]');pg.click('#f-save')
    pg.wait_for_timeout(200);print('2 status during failure:',pg.inner_text('#status'))
    print('  pending in LS:',pg.evaluate("Object.keys(JSON.parse(localStorage.getItem('carnet-ongles-v1-pending-u1')||'{}'))"))
    # reload before retry succeeds -> pending must survive and be resent
    pg.evaluate("localStorage.setItem('__fail','0')");pg.reload();pg.wait_for_timeout(600)
    print('3 after reload status:',pg.inner_text('#status'),'| server docs:',pg.evaluate("Object.keys(JSON.parse(localStorage.getItem('__server')))"))
    print('  rdv visible:',pg.locator('.ev').count())
    # delete -> trash -> restore
    pg.click('.ev');pg.click('#f-del');pg.click('#cYes');pg.wait_for_timeout(200)
    print('4 after delete ev:',pg.locator('.ev').count(),'server deletedAt:',pg.evaluate("Object.values(JSON.parse(localStorage.getItem('__server'))).filter(v=>v.deletedAt).length"))
    pg.click('nav.tabs >> text=Réglages');print('  trash:',pg.inner_text('#trashBox')[:60].replace('\n',' '))
    pg.click('[data-restore]');pg.wait_for_timeout(200);pg.click('nav.tabs >> text=Planning');print('  restored ev:',pg.locator('.ev').count())
    # server wiped -> restore offer from mirror
    pg.evaluate("localStorage.setItem('__server','{}')");pg.reload();pg.wait_for_timeout(600)
    print('5 alerts:',pg.inner_text('#alerts')[:120].replace('\n',' '))
    pg.click('[data-act=restore]');pg.wait_for_timeout(400)
    print('  after restore ev:',pg.locator('.ev').count(),'server docs:',len(pg.evaluate("Object.keys(JSON.parse(localStorage.getItem('__server')))")))
    pg.screenshot(path=TMP+'/a1.png')
    print('errs',errs);b.close()
