# Gardenz Actuz

Revue de presse gratuite sur le cannabis, le CBD et le chanvre. Application existante : https://republikgarden-a11y.github.io/tradeatlas/gardenz-actuz/

## Lire le journal
- Dernières actus : actualités des dernières 24h, source, langue, date de publication, extrait et image de l’article quand elle est accessible.
- Rubriques, recherche, périodes 24h/7j/30j, filtres de langue et de source.
- Éditions quotidiennes : une archive datée construite automatiquement, cumulée lors des collectes du jour.
- Mes articles : favoris et copies du texte sur cet appareil, y compris lorsqu’ils sortent du fil de 30 jours.
- Anciennes éditions : les huit éditions rédigées du 2 au 9 novembre 2026, préservées.
- Images sépia ou couleurs, installation, impression et lecture hors connexion du contenu déjà chargé.

## Gratuité et programmation
GitHub Pages et les runners Linux standards d’un dépôt public, sans clé d’API, sans IA payante, sans abonnement supplémentaire. Trois collectes chaque jour à 09h17, 13h17 et 18h17, Europe/Paris. Les horaires planifiés peuvent être retardés par GitHub. Les deux workflows du dépôt partagent le verrou de publication Pages pour éviter qu’un ancien déploiement écrase le plus récent.

Neuf flux publics sont interrogés. Les nouveaux articles des flux disponibles sont conservés sans l’ancienne limite de quatre par média. Après une interruption, le collecteur rattrape les dates encore présentes dans les flux, dans une limite de 14 jours. Il ne reconstitue pas artificiellement les journées manquantes. Les rubriques sont calculées automatiquement. Le français est activé par défaut pour les titres et extraits ; les originaux sont conservés et restituables par le bouton Français. Qwen3 est exécuté sur CPU dans le workflow, sans API payante. Les poids publics sont épinglés par révision ; seules les nouvelles traductions ou les textes modifiés sont calculés. « Lire en français » ouvre la traduction Google de l’article complet ; « Source originale » ouvre le média directement. Les images et droits restent à leurs éditeurs. Le fil ne prétend pas être une validation journalistique indépendante.

En cas d’échec total, latest.json conserve les articles et la dernière réussite, le statut d’erreur est publié et le workflow échoue pour que GitHub signale le problème. Aucune nouvelle archive datée n’est fabriquée. Les archives quotidiennes sont cumulées par date de collecte, avec les dates de publication propres à chaque article.

## Maintenance
Depuis la racine du dépôt :

```sh
python -m unittest discover -s gardenz-actuz/scripts -p 'test_*.py'
python gardenz-actuz/scripts/refresh.py
python gardenz-actuz/preparer-cache.py
```

Le workflow `.github/workflows/gardenz-actuz.yml` fait ces opérations, conserve les données et publie le site complet sans modifier l’application Trade Atlas à la racine. Le cache réseau est prioritaire pour HTML, CSS, JavaScript et JSON ; les images sont conservées à la lecture. Il n’impose plus le téléchargement de tous les anciens visuels avant d’installer l’application.

Pour importer une ancienne édition rédigée, conserver le format existant et lancer `python gardenz-actuz/importer-editions.py /chemin/édition.html` (lxml), puis `preparer-cache.py`. Ne jamais supprimer les autres éditions.

### Traduction
Dépendances : scripts/translation-requirements.txt (llama.cpp CPU et téléchargement des poids publics). `python gardenz-actuz/scripts/translate_fr.py` complète les traductions de latest.json et des éditions quotidiennes, conserve leurs originaux et réutilise le cache seulement à contenu identique. Aucun modèle n’est embarqué dans le site ni téléchargé par le lecteur. Une panne du moteur est signalée et garde les traductions valides déjà calculées.
