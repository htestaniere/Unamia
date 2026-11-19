import os, pathlib, tempfile
URL = (pathlib.Path(__file__).resolve().parent.parent / "index.html").as_uri()
TMP = tempfile.gettempdir()
CHROME = os.environ.get("CHROME_PATH") or None   # facultatif : chemin d'un Chrome/Chromium déjà installé
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CHROME)
    pg=b.new_page(viewport={'width':1280,'height':1000},accept_downloads=True);errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL)
    pg.click('#newBtn');pg.fill('#f-client','Léa');pg.click('.chip[data-k=remplissage]')
    print('visible prevu:',pg.is_visible('#f-inv'))
    pg.click('#stSeg button[data-s=fait]');pg.click('.pays label:has-text("Lydia")')
    print('visible fait:',pg.is_visible('#f-inv'),pg.inner_text('#f-inv'))
    with pg.expect_download() as d: pg.click('#f-inv')
    print('file:',d.value.suggested_filename)
    pg.click('.ev');print('reopen:',pg.inner_text('#f-inv'),'|',pg.inner_text('#invNote')[:40])
    with pg.expect_download() as d: pg.click('#f-inv')
    print('file2:',d.value.suggested_filename, pg.evaluate("invs.size"))
    pg.click('#newBtn');pg.fill('#f-client','Zoé');pg.click('.chip[data-k=semi]');pg.click('#stSeg button[data-s=fait]');pg.click('.pays label:has-text("PayPal")');pg.click('#f-save')
    pg.click('nav.tabs >> text=Rapport');pg.click('#dlInvoices') if False else None
    print(pg.evaluate("uninvoicedCount(curYm())"), errs);b.close()
