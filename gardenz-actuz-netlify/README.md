# Gardenz Actuz — adresse Netlify existante

Ce dossier permet de conserver https://gardenzactuz.netlify.app/ et de servir
le journal actualisé sur GitHub sans manipuler un ZIP.

## Raccordement du projet existant, une seule fois

- Projet Netlify : gardenzactuz (ne pas créer un autre projet).
- Dépôt GitHub : republikgarden-a11y/tradeatlas.
- Branche : main.
- Base directory : gardenz-actuz-netlify.
- Build command : vide.
- Publish directory : . (le dossier de base lui-même).

Le fichier netlify.toml du dossier définit la publication et ignore les builds
lorsque seules les données du journal changent ailleurs dans le dépôt.
Les trois collectes restent dans le workflow GitHub existant : 09h17, 13h17,
18h17 Europe/Paris, avec les retards possibles du planificateur.

La règle _redirects est une réécriture HTTP 200, pas une redirection du navigateur.
Les pages, images, polices et archives sont celles du journal GitHub ; l’adresse
Netlify reste affichée. Aucun nouveau service payant ou secret n’est requis par
le code. Les quotas gratuits des deux hébergeurs continuent de s’appliquer.

La reprise du cache renouvelle l’ancien moteur de lecture une seule fois sans
effacer les favoris. En secours : /reparer-cache.html sur le site publié.

Ce dossier préparé n’est pas une preuve de publication. Après le raccordement,
attendre Published et contrôler l’adresse publique, la date réelle de collecte,
le bouton Français et une ancienne édition.
