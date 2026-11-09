# TRADE ATLAS

Répertoire d'entreprises, de fournisseurs, d'importateurs et de relations commerciales documentées. Interface statique en français avec recherche, filtres et export CSV.

## Veille gratuite

Le script `scripts/refresh.py` interroge quotidiennement quatre flux de recherche **Google News RSS**, avec un seul appel **GDELT** en secours lorsque tous les flux RSS sont indisponibles, afin de découvrir des **mentions de presse** relatives aux fabricants, au packaging et aux accessoires. Les flux gratuits peuvent être temporairement limités ; le système signale honnêtement les échecs et ne prétend pas avoir actualisé les expéditions douanières. Les résultats sont stockés dans `data/veille.json` et consultables dans l'onglet **Veille quotidienne**.

**Attention :** ces articles ne sont pas des preuves douanières. Les 70 fiches et 49 relations ImportYeti historiques restent figées à leur date d'archive. Aucun accès automatique aux bases privées ImportYeti/Volza n'est inclus.

## Mise en ligne gratuite avec GitHub Pages

1. Ouvre **Settings → Pages** dans ce dépôt.
2. Sous **Build and deployment**, sélectionne **GitHub Actions** comme source.
3. Vérifie dans **Settings → Actions → General → Workflow permissions** que les workflows peuvent écrire dans le dépôt (`Read and write permissions`).
4. Va dans **Actions → TRADE ATLAS - Veille gratuite quotidienne → Run workflow** pour effectuer le premier contrôle et publier.
5. Une fois le déploiement réussi, le site sera accessible à [republikgarden-a11y.github.io/tradeatlas](https://republikgarden-a11y.github.io/tradeatlas/).

L'action est prévue tous les jours vers **9 h 23, heure de Paris**. GitHub peut décaler une exécution. Sur les dépôts publics inactifs depuis 60 jours, les workflows planifiés peuvent être automatiquement désactivés.

## Alternative Netlify

Connecte **ce dépôt** au site Netlify existant pour conserver son URL. Le fichier `netlify.toml` prévoit une publication des fichiers statiques depuis la racine. Un simple dépôt manuel du ZIP sur Netlify ne suffit pas à activer la veille.

## Exécution locale

```bash
python scripts/refresh.py
python -m http.server 8000
```

Ouvre http://localhost:8000/ ; aucun paquet Python supplémentaire n'est requis. Une connexion internet est nécessaire pour la collecte. Les erreurs externes sont indiquées dans `data/veille.json`, et un échec ne doit pas être présenté comme une mise à jour de données douanières.
