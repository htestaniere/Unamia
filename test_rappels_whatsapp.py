import os, pathlib, datetime, urllib.parse
URL = (pathlib.Path(__file__).resolve().parent.parent / "app.src.html").as_uri()
CHROME = os.environ.get("CHROME_PATH") or None
from playwright.sync_api import sync_playwright
tm = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME); pg = b.new_page(viewport={'width':1280,'height':800})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); pg.goto(URL)
    def rdv(c, t, ph):
        pg.click('#newBtn'); pg.fill('#f-client', c); pg.fill('#f-date', tm); pg.fill('#f-start', t); pg.fill('#f-phone', ph)
        pg.click('.chip[data-k=semi]'); pg.click('#f-save')
    rdv('Léa Martin', '10:00', '06 12 34 56 78'); rdv('Inès', '14:30', '')
    href = pg.get_attribute('[data-wa]', 'href'); print(urllib.parse.unquote(href))
    assert href.startswith('https://wa.me/33612345678?text='), href
    # 1. après envoi, la cliente sort de la liste
    with pg.expect_popup(): pg.click('[data-wa]')
    pg.wait_for_timeout(700)
    txt = pg.inner_text('#remBox'); assert 'Léa' not in txt and 'Inès' in txt, txt
    # 2. numéro ajouté pour Inès : bouton d'envoi
    pg.click('[data-edit]'); pg.fill('#f-phone', '+33 7 98 76 54 32'); pg.click('#f-save'); pg.wait_for_timeout(300)
    assert pg.locator('[data-wa]').count() == 1
    # 3. dans la fiche de Léa : renvoyer le rappel
    pg.click('.ev:has-text("Léa")'); pg.wait_for_timeout(200)
    assert pg.is_visible('#f-wa') and 'Renvoyer' in pg.inner_text('#f-wa'), pg.inner_text('#waRow')
    before = pg.evaluate("[...appts.values()].find(a=>a.client==='Léa Martin').remindedAt")
    with pg.expect_popup(): pg.click('#f-wa')
    after = pg.evaluate("[...appts.values()].find(a=>a.client==='Léa Martin').remindedAt")
    assert after and after >= before, (before, after)
    assert 'Léa' not in pg.inner_text('#remBox')
    # 4. autoremplissage du téléphone pour une cliente déjà connue
    pg.click('#newBtn'); pg.fill('#f-client', 'léa martin'); pg.press('#f-client', 'Tab')
    assert pg.input_value('#f-phone') == '06 12 34 56 78'
    assert not errs, errs; print('OK', errs); b.close()
