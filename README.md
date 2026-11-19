# Unamia — Planning & compta

Outil de planning et de comptabilité pour une prothésiste ongulaire (Unamia, manucure russe).
Une seule page HTML autonome (`index.html`), hébergeable n'importe où (GitHub Pages, Netlify, Cloudflare Pages…).

## Fonctionnalités

- Planning semaine et mois, rendez-vous déplaçables par glisser-déposer
- Prestations multiples par rendez-vous (remplissage, semi, rallongement, dépose, pédicure, nail art, réparation) avec prix et durée modifiables
- Statuts : à venir, réalisé, annulé, pas venue (avec frais conservés) ; moyen de paiement (espèces, Lydia, PayPal, virement)
- Factures à numérotation continue et figée (F-AAAA-0001…), à la demande depuis le rendez-vous ou en fin de mois
- Rapport mensuel, livre des recettes, export CSV
- Dépenses par catégorie, estimation des cotisations URSSAF, jauges plafond micro-entreprise et franchise de TVA
- **Rappels WhatsApp en un clic** : téléphone par rendez-vous, liste « Rappels à envoyer » (aujourd'hui → après-demain), message modifiable dans les Réglages
- **Synchronisation multi-appareils** : connexion e-mail + mot de passe (Supabase), mêmes données sur téléphone et ordinateur
- **Sauvegarde fiabilisée** : file d'attente avec renvoi automatique, copie miroir dans le navigateur, corbeille, export/import JSON, sauvegarde automatique mensuelle en ligne (restaurable depuis les Réglages), rappel de téléchargement mensuel

## Structure

| Fichier | Rôle |
|---|---|
| `app.src.html` | **Source de l'application** (sans connexion). À modifier pour toute évolution. |
| `web/backend.js` | Connexion et synchronisation Supabase |
| `web/supabase.umd.js` | Bibliothèque supabase-js (copie locale, pas de CDN) |
| `build_web.py` | Assemble les trois fichiers ci-dessus en `index.html` : `python3 build_web.py` |
| `index.html` | **Le site à publier** (généré, ne pas éditer à la main) |
| `supabase/setup.sql` | Création de la table et des règles de sécurité (à exécuter une fois) |
| `assets/` | Logo fourni et version ronde intégrée à la page |
| `tests/` | Scénarios automatiques (Playwright) |

## Mise en place de la synchronisation (une seule fois)

1. Créer un projet Supabase, puis exécuter `supabase/setup.sql` dans *SQL Editor*.
2. Dans `web/backend.js`, renseigner `URL_` et `KEY_` avec l'URL du projet et la clé **publishable** (*Project Settings → API Keys*). Cette clé est publique par conception ; **ne jamais y mettre la clé `secret`**.
3. Créer le compte de la cliente : *Authentication → Users → Add user → Create new user*, avec **Auto Confirm User** coché.
4. `python3 build_web.py`, puis publier `index.html`.
5. Une fois le site en ligne, renseigner son adresse dans *Authentication → URL Configuration → Site URL* (nécessaire pour « mot de passe oublié »).

La sécurité repose sur les règles de la base (RLS) : chaque compte ne peut lire et écrire que ses propres lignes.
Le plan gratuit de Supabase met le projet en pause après 7 jours sans activité et ne fait pas de sauvegardes : garder le rappel mensuel de téléchargement.

## Modes de fonctionnement

- `index.html` : connexion Supabase, données en ligne + copie locale.
- `app.src.html` ouvert seul : mode local, données dans le navigateur de l'appareil (pas de synchronisation).
- Publié comme artifact Claude : données dans l'espace privé du compte Claude.

## Réglages par défaut (2026)

Cotisations 21,2 % + CFP 0,3 % (prestations artisanales BIC), plafond de CA 83 600 €, franchise de TVA 37 500 €.
Tous modifiables dans l'onglet Réglages. Les montants affichés sont des estimations : le chiffre officiel est celui de la déclaration URSSAF.

## Tests

```
pip install playwright && playwright install chromium
python tests/run_all.py          # ou CHROME_PATH=/chemin/vers/chrome
```

Les scénarios pilotent la page dans un navigateur et échouent si une étape plante ou si la page lève une erreur. Le test de synchronisation utilise un faux serveur (`tests/mock_supabase.js`) : le vrai Supabase n'est jamais contacté.
