"""Lance tous les scénarios de test. Usage : python tests/run_all.py
Prérequis : pip install playwright && playwright install chromium
(ou CHROME_PATH=/chemin/vers/chrome). Chaque scénario pilote l'application dans un navigateur."""
import subprocess, sys, pathlib
ok = True
for f in sorted(pathlib.Path(__file__).parent.glob("test_*.py")):
    r = subprocess.run([sys.executable, str(f)], capture_output=True, text=True)
    bad = r.returncode != 0 or "Traceback" in r.stdout + r.stderr or "Error" in r.stdout
    print(("ÉCHEC " if bad else "OK    ") + f.name)
    if bad:
        ok = False
        print((r.stdout + r.stderr)[-600:])
sys.exit(0 if ok else 1)
