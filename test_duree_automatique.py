import os, pathlib, tempfile
URL = (pathlib.Path(__file__).resolve().parent.parent / "app.src.html").as_uri()
TMP = tempfile.gettempdir()
CHROME = os.environ.get("CHROME_PATH") or None   # facultatif : chemin d'un Chrome/Chromium déjà installé
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CHROME)
    pg=b.new_page(viewport={'width':1280,'height':1000});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL)
    pg.click('#newBtn');pg.fill('#f-client','Léa');pg.click('.chip[data-k=remplissage]');pg.click('.chip[data-k=nailart]')
    pg.fill('tr[data-k=nailart] input[data-f=qty]','4');pg.fill('tr[data-k=nailart] input[data-f=unit]','5')
    print('texte:',pg.inner_text('#f-durtxt'))
    pg.fill('tr[data-k=remplissage] input[data-f=dur]','75');print('apres 75:',pg.inner_text('#f-durtxt'))
    pg.screenshot(path=TMP+'/m2.png');pg.click('#f-save')
    print('rdv:',pg.evaluate("[...appts.values()].map(a=>a.duration)"))
    # ancien rdv avec durée manuelle conservée
    pg.evaluate("persist('rdv',{id:'old',client:'Old',date:'2026-11-18',start:'10:00',duration:180,items:[{k:'semi',qty:1,unit:50}],status:'prevu',done:false,fee:0,payment:''});renderAll()")
    pg.click('.ev:has-text(\"Old\")');print('ancien:',pg.inner_text('#f-durtxt'));pg.click('#f-save')
    print('ancien garde:',pg.evaluate("appts.get('old').duration"))
    print(errs);b.close()
