import os, pathlib, tempfile
URL = (pathlib.Path(__file__).resolve().parent.parent / "app.src.html").as_uri()
TMP = tempfile.gettempdir()
CHROME = os.environ.get("CHROME_PATH") or None   # facultatif : chemin d'un Chrome/Chromium déjà installé
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path=CHROME)
    pg=b.new_page(viewport={'width':1280,'height':1000});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(URL)
    pg.click('#newBtn');pg.fill('#f-client','Léa');pg.fill('#f-date','2026-11-17');pg.fill('#f-start','10:00');pg.click('.chip[data-k=semi]');pg.click('#f-save')
    box=pg.locator('.ev').bounding_box();col=pg.locator('.col[data-date="2026-11-20"]').bounding_box()
    pg.mouse.move(box['x']+20,box['y']+10);pg.mouse.down();pg.mouse.move(box['x']+60,box['y']+40,steps=5)
    pg.mouse.move(col['x']+30,box['y']+10+52*4,steps=10);pg.mouse.up()
    print(pg.evaluate("[...appts.values()].map(a=>a.date+' '+a.start)"))
    # click opens modal
    pg.click('.ev');print('modal open',pg.is_visible('#ov.on'));pg.click('#f-cancel')
    pg.click('#seg button[data-m=month]')
    me=pg.locator('.me').bounding_box();t=pg.locator('.mc[data-date="2026-11-25"]').bounding_box()
    pg.mouse.move(me['x']+10,me['y']+5);pg.mouse.down();pg.mouse.move(t['x']+40,t['y']+50,steps=10);pg.mouse.up()
    print(pg.evaluate("[...appts.values()].map(a=>a.date+' '+a.start)"),pg.locator('.mc.drop').count())
    print(errs);b.close()
