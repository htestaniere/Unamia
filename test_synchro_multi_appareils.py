"""Teste la connexion et la synchronisation entre deux appareils avec un FAUX serveur Supabase (tests/mock_supabase.js).
Le vrai serveur n'est jamais contacté."""
import os, pathlib, subprocess, sys, tempfile
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = pathlib.Path(tempfile.gettempdir()) / "unamia-test-sync.html"
subprocess.run([sys.executable, str(ROOT / "build_web.py"), str(ROOT / "tests/mock_supabase.js"), str(OUT)], check=True)
CHROME = os.environ.get("CHROME_PATH") or None
from playwright.sync_api import sync_playwright
USERS = {}; ROWS = {}
def srv(op, a):
    if op == 'signup':
        if a[0] in USERS: return {'error': 'User already registered'}
        USERS[a[0]] = (a[1], 'u' + str(len(USERS) + 1)); op = 'login'
    if op == 'login':
        u = USERS.get(a[0])
        if not u or u[0] != a[1]: return {'error': 'Invalid login credentials'}
        return {'session': {'user': {'id': u[1], 'email': a[0]}}}
    if op == 'upsert': ROWS.setdefault(a[0], {})[a[1]['id']] = a[1]['data']; return True
    if op == 'list': return [{'id': k, 'data': v} for k, v in sorted(ROWS.get(a[0], {}).items())][a[1]:a[2] + 1]
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    def device():
        ctx = b.new_context(viewport={'width':1280,'height':760}); ctx.expose_function('__srv', srv)
        pg = ctx.new_page(); pg.errs = []; pg.on('pageerror', lambda e: pg.errs.append(str(e))); pg.goto(OUT.as_uri()); pg.wait_for_selector('#sbLogin'); return ctx, pg
    def rdv(pg, c, t):
        pg.click('#newBtn'); pg.fill('#f-client', c); pg.fill('#f-start', t); pg.fill('#f-date', '2026-11-19'); pg.click('.chip[data-k=semi]'); pg.click('#f-save')
    ctxA, A = device()
    A.click('[data-m=up]'); A.fill('#sbE', 'nail@x.fr'); A.fill('#sbP', 'short'); A.click('#sbLogin button.p'); assert 'trop court' in A.inner_text('#sbM')
    A.fill('#sbP', 'motdepasse1'); A.click('#sbLogin button.p'); A.wait_for_selector('#sbLogin', state='detached')
    rdv(A, 'Léa', '10:00'); A.wait_for_timeout(500); assert any(k.startswith('rdv-') for k in ROWS['u1'])
    ctxB, B = device()
    B.fill('#sbE', 'nail@x.fr'); B.fill('#sbP', 'faux'); B.click('#sbLogin button.p'); B.wait_for_timeout(200); assert 'incorrect' in B.inner_text('#sbM')
    B.fill('#sbP', 'motdepasse1'); B.click('#sbLogin button.p'); B.wait_for_selector('#sbLogin', state='detached'); B.wait_for_timeout(600)
    assert B.locator('.ev:has-text("Léa")').count() == 1
    rdv(B, 'Inès', '14:00'); B.wait_for_timeout(500)
    A.evaluate("window.dispatchEvent(new Event('focus'))"); A.wait_for_timeout(600); assert A.locator('.ev:has-text("Inès")').count() == 1
    ctxA.set_offline(True); rdv(A, 'Zoé', '16:00'); A.wait_for_timeout(600)
    assert not any('Zoé' in str(v) for v in ROWS['u1'].values())
    ctxA.set_offline(False); A.evaluate("window.dispatchEvent(new Event('online'))"); A.wait_for_timeout(2500)
    assert any('Zoé' in str(v) for v in ROWS['u1'].values())
    A.reload(); A.wait_for_timeout(1500); assert A.locator('#sbLogin').count() == 0
    assert len([k for k in ROWS['u1'] if k.startswith('bak-')]) == 1   # une seule sauvegarde mensuelle
    A.click('[data-tab=reglages]'); assert 'Sauvegardes mensuelles' in A.inner_text('#snapBox')
    A.click('#sbOut'); A.wait_for_selector('#sbLogin')
    assert not A.errs and not B.errs, (A.errs, B.errs); print('OK'); b.close()
