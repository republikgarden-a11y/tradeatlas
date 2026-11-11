# Gardenz Actuz

Revue de presse cannabis, CBD et chanvre pour Charles et les lecteurs adultes de l’écosystème Gardenz. Le besoin principal est de retrouver les nouvelles du jour et les sources en quelques secondes, puis de parcourir les dates et conserver des articles.

## Contraintes confirmées
- Aucun coût additionnel : dépôt GitHub public, Pages, runners Linux standard et traduction neuronale exécutée localement lors de la préparation. Aucun service, clé d’API ou modèle IA facturable.
- Actualisation quotidienne indépendante de l’ordinateur du lecteur. Collectes prévues à 09h17, 13h17 et 18h17 Europe/Paris, sous réserve des délais GitHub et de la disponibilité des sources.
- Conserver les anciennes éditions du 2 au 9 novembre 2026 et leurs visuels.
- Univers journal papier, manchette gothique existante, brun et sépia, mode images en couleurs.
- Les nouvelles sont des titres et extraits de presse attribués, avec accès à l’éditeur. Les traductions automatiques anglaises et allemandes sont disponibles en français par défaut, avec retour à l’original en un clic. Les textes source restent inchangés ; aucune traduction n’est présentée comme une vérification journalistique.

## Fonctionnement
Neuf flux publics : Newsweed, Le Cannabiste, Marijuana Moment, Ganjapreneur, Hanf Magazin, Business of Cannabis, HempToday, Cannabis Health et NORML. NORML est identifié comme organisation militante. Les dates viennent des publications ; les rubriques sont des aides de navigation automatiques. Une collecte sans nouvelle peut être réussie. Un échec global conserve les données et la dernière vraie réussite et ne crée aucune fausse édition quotidienne.

La revue du jour cumule les publications collectées de cette journée sur une fenêtre glissante de 24h. Les anciennes collectes restent consultables par date ; le fil conserve 30 jours. Les favoris et leur texte sont locaux à l’appareil. Le mode hors connexion conserve le texte essentiel et les images/éditions déjà consultées. Les liens vers les éditeurs demandent Internet.

## Traduction française
Le lecteur active/désactive le français par un interrupteur toujours visible ; sa préférence reste sur son appareil. Les titres et extraits sont traduits avec des modèles Qwen3-4B-Instruct-2507 pour l’allemand et OPUS-MT Transformer Big pour l’anglais, téléchargés publiquement puis exécutés sur le runner gratuit. Aucun appel d’inférence payant et aucun téléchargement de modèle sur le téléphone. Une traduction est réutilisée uniquement si langue, titre et extrait source correspondent exactement. Les nouvelles éditions et les favoris conservent leurs deux versions. Le lien « Lire en français » des sources étrangères ouvre Google Traduction pour l’article complet ; le lien « Source originale » reste disponible. Une traduction manquante est signalée et ne fait pas passer un titre étranger pour du français.
