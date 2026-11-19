# Unamia — Planning & compta

Outil de planning et de comptabilité pour une prothésiste ongulaire (Unamia, manucure russe).
Une seule page HTML autonome : `index.html` (pas de build, pas de dépendance à installer).

## Fonctionnalités

- Planning semaine et mois, rendez-vous déplaçables par glisser-déposer
- Prestations multiples par rendez-vous (remplissage, semi, rallongement, dépose, pédicure, nail art, réparation) avec prix et durée modifiables
- Statuts : prévu, réalisé, annulé, pas venue (avec acompte ou frais conservés) ; moyen de paiement (espèces, Lydia, PayPal, virement)
- Factures à numérotation continue et figée (F-AAAA-0001…), à la demande depuis le rendez-vous ou en fin de mois
- Rapport mensuel, livre des recettes, export CSV
- Dépenses par catégorie, estimation des cotisations URSSAF, jauges plafond micro-entreprise et franchise de TVA
- Sauvegarde fiabilisée : file d'attente avec renvoi automatique, copie miroir dans le navigateur, corbeille, export/import JSON

## Utilisation

Ouvrir `index.html` dans un navigateur : les données sont alors enregistrées dans ce navigateur (`localStorage`).
Publiée comme artifact Claude, la page enregistre les données en ligne dans l'espace privé de l'utilisatrice (capacités `db`, `user` et `downloads`).

## Réglages par défaut (2026)

Cotisations 21,2 % + CFP 0,3 % (prestations artisanales BIC), plafond de CA 83 600 €, franchise de TVA 37 500 €.
Tous modifiables dans l'onglet Réglages. Les montants affichés sont des estimations : le chiffre officiel est celui de la déclaration URSSAF.

## Contenu du dépôt

- `index.html` : l'application complète (code, styles, logo intégré)
- `assets/logo-original.png` : logo fourni par la cliente ; `assets/logo-rond.png` : version détourée en cercle (220 px), celle qui est intégrée dans la page
- `tests/` : scénarios automatiques (Playwright) : facturation et numéros figés, statuts et dépenses, glisser-déposer, bouton facture dans le rendez-vous, durée automatique, fiabilité de la sauvegarde (coupures réseau, rechargement, corbeille, restauration)

## Tests

```
pip install playwright && playwright install chromium
python tests/run_all.py
```

Ce sont des scénarios de vérification qui pilotent la page dans un navigateur : ils échouent si une étape plante ou si la page lève une erreur, mais ne comparent pas tous les montants automatiquement.

## Charte graphique Unamia

Fond crème `#F8F4EE`, brun chocolat `#4B3427` (boutons, texte `#3A2A22`), beige du logo `#AA9E8B`, vert sauge `#5F7F66` (réalisé), caramel `#A97B3F` (à clôturer).
Titres en Cormorant Garamond, texte en Jost (Google Fonts).

## Synchronisation multi-appareils (Supabase)

`index.html` = `app.src.html` + `web/supabase.umd.js` + `web/backend.js` (reconstruire avec `python3 build_web.py`).
Connexion e-mail + mot de passe ; les données sont dans la table `docs` (sécurité RLS : chacun ne voit que ses lignes, voir `supabase/setup.sql`).
Sans connexion internet, les saisies sont gardées sur l'appareil et renvoyées automatiquement.
La clé « publishable » dans `web/backend.js` est publique par conception ; ne jamais y mettre la clé `secret`.
