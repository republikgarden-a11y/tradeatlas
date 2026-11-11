# Gardenz Actuz

Journal cannabis, CBD et chanvre. Une application statique, sans API payante, sans compte lecteur et sans service facturable.

- **À la une** : collecte automatique de cinq flux RSS publics, vers 09h07 Europe/Paris et seconde collecte à 11h37. Les extraits gardent leur langue originale et ne prétendent pas être des synthèses vérifiées. Les images sont celles publiées par les sources ; les refus d'accès ne sont pas contournés.
- **Bulletins vérifiés** : les huit éditions existantes du 2 au 9 novembre 2026, intégralement conservées. Leur rédaction et recoupement restent un travail éditorial distinct.
- Recherche, filtre de langue, favoris locaux, sépia/couleurs, installation et archives hors ligne.
- Date de collecte réussie, sources en échec et retard visibles. Une panne conserve les données antérieures, publie son état et fait échouer le workflow après publication pour signalement dans GitHub.

## Gratuité
GitHub Pages et les exécuteurs Linux standards GitHub Actions d'un dépôt public sont utilisés. Aucun secret, aucune API IA, aucune carte bancaire ni recharge. Pas de serveur Netlify dans le parcours de lecture. Les limites et disponibilités de GitHub et des sources s'appliquent ; un horaire cron n'est pas une garantie à la minute.

## Maintenance
`python3 scripts/refresh.py` actualise la collecte. `python3 -m unittest discover -s scripts -p 'test_*.py'` contrôle le traitement RSS. Le fichier `.github/workflows/gardenz-actuz.yml` est à la racine du dépôt GitHub, pas dans le dossier du site. Les autres fichiers restent dans `gardenz-actuz/`.

Les données et images collectées sont publiques, leurs droits restent à leurs auteurs. Les textes intégraux des articles ne sont pas copiés. La synthèse éditoriale autonome en français du brief initial ne peut pas être remplacée honnêtement par ce collecteur sans IA : il est explicitement présenté comme un fil de sources.

## Importer une édition vérifiée
Conserver le format Gardenz-Actuz-AAAA-MM-JJ.html ; lancer `python3 importer-editions.py /chemin/édition.html` (lxml), puis `python3 preparer-cache.py` et enregistrer le résultat dans Git. Ne pas supprimer les anciennes éditions.
