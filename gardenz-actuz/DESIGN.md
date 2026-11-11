---
name: Gardenz Actuz
description: Un journal de presse cannabis, CBD et chanvre sur papier clair et encre brune.
colors:
  paper: "#f7f2e6"
  ink: "#30271c"
  line: "#c5b9a3"
  green: "#35543c"
  muted: "#6b5b45"
  outer: "#e5ddcf"
  field: "#fffdf5"
typography:
  display:
    fontFamily: "Fraktur, serif"
    fontSize: "clamp(58px, 8.5vw, 96px)"
    fontWeight: 400
    lineHeight: 1.12
    letterSpacing: "-0.015em"
  headline:
    fontFamily: "Georgia, 'Times New Roman', serif"
    fontSize: "36px"
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: "-0.025em"
  title:
    fontFamily: "Georgia, 'Times New Roman', serif"
    fontSize: "28px"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.02em"
  body:
    fontFamily: "Georgia, 'Times New Roman', serif"
    fontSize: "18px"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "system-ui, sans-serif"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.5
rounded:
  none: "0px"
  control: "3px"
  pill: "20px"
spacing:
  tight: "8px"
  control: "14px"
  gutter: "20px"
  section: "30px"
components:
  button-neutral:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "9px 14px"
  button-dark:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    rounded: "{rounded.control}"
    padding: "9px 14px"
  search-field:
    backgroundColor: "{colors.field}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "10px 9px"
    width: "100%"
  reading-tab:
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "14px 0 12px"
  topic-selected:
    backgroundColor: "{colors.green}"
    textColor: "#fff"
    rounded: "{rounded.pill}"
    padding: "8px 12px"
  article-row:
    rounded: "{rounded.none}"
    padding: "28px 0"
  save-button:
    rounded: "{rounded.control}"
    padding: "8px 10px"
  masthead:
    textColor: "{colors.ink}"
    typography: "{typography.display}"
---

# Design System: Gardenz Actuz

## Overview

**Creative North Star: "Le journal papier Gardenz"**

Gardenz Actuz prolonge son identité de journal : papier clair, encre brune, manchette gothique et photographies ou illustrations issues des éditeurs, traitées en sépia. Le mode Read privilégie une lecture éditoriale dense et calme, avec des sources et des dates immédiatement identifiables.

Le vert forêt accompagne les actions, la sélection et les sources. Il reste un accent de navigation au sein du journal brun. Les anciennes éditions conservent leurs documents et leur présentation historique ; leurs particularités ne définissent pas les nouveaux composants.

**Key Characteristics:**
- Papier clair et encre brune.
- Fraktur pour la signature, sérif pour la lecture, sans sérif pour les repères.
- Articles séparés par des filets, avec une hiérarchie de texte nette.
- Visuels de presse attribués, sépia par défaut et couleurs à la demande.

## Colors

La palette associe des tons de papier chauds à une encre sombre et un accent végétal discret. Les valeurs normatives figurent dans le frontmatter.

### Primary
- **Vert forêt** (`green`) : sources, liens de lecture, rubrique sélectionnée, statut courant et focus clavier.

### Neutral
- **Papier clair** (`paper`) : feuille de lecture et navigation.
- **Encre brune** (`ink`) : manchette, titres, texte et filets forts.
- **Filet beige** (`line`) : séparations et bordures des contrôles.
- **Brun secondaire** (`muted`) : dates, légendes, explications et labels.
- **Table de lecture** (`outer`) : fond extérieur à la feuille.
- **Champ ivoire** (`field`) : recherche et listes de sélection.

## Typography

**Display Font:** Fraktur, avec repli sérif ; police locale dans `assets/fraktur.ttf`.
**Body Font:** Georgia, avec Times New Roman et sérif en repli.
**Label Font:** system-ui, avec repli sans sérif, pour la lecture actuelle.

La signature gothique donne son caractère au journal. Les titres et extraits sérif portent la lecture ; les informations de service utilisent une voix plus petite et plus neutre.

### Hierarchy
- **Display** : grande manchette centrée ; l’identité compacte de la barre utilise la même famille.
- **Headline** : titre de la une ; sur mobile, il passe à (31px) avec une interligne de (1.18).
- **Title** : titres d’articles du fil ; sur mobile, ils passent à (27px).
- **Body** : prose à (18px), interligne de (1.6) ; les extraits de bureau utilisent (1.65) et une largeur maximale de (70ch).
- **Label** : métadonnées à (12px), avec des variantes de service entre (11px) et (15px). Les légendes et les repères restent distincts du corps de lecture.

Les anciens numéros comportent des règles de lisibilité propres à leur panneau. Ne pas étendre leurs tailles de métadonnées au fil actuel.

## Layout

Le vocabulaire commun est celui de la feuille centrée, des colonnes éditoriales et des filets horizontaux. La lecture actuelle est contenue dans une largeur maximale de (1280px), avec un retrait de bureau de (48px). Les blocs respirent par des espacements plutôt que par une succession de cartes détachées.

La surface actuelle compose sa une et son sommaire en (1.7fr / 1fr), avec un intervalle de (34px). Sous (1050px), le sommaire mesure (280px) et les retraits passent à (32px). Ce rapport décrit cette surface ; il ne fixe pas la composition de tout futur écran.

À (760px) et moins, la lecture passe sur une colonne et les retraits à (20px). Le sommaire suit la une avec un filet supérieur. Les onglets et rubriques peuvent défiler horizontalement. Les outils de recherche se répartissent sur deux colonnes, avec la recherche puis la source sur toute la largeur. Les articles sans visuel utilisent la largeur du texte disponible.

## Elevation & Depth

Les articles restent plats sur le papier. Les filets simples ou doubles structurent les niveaux ; une ombre douce sous la feuille de lecture la distingue du fond extérieur. L’ombre n’est pas répétée sous chaque article. La valeur exacte de cette ombre est conservée dans le sidecar.

## Shapes

La feuille, les images et les articles ont des contours droits. Les contrôles courants ont des angles légèrement adoucis ; les rubriques utilisent une forme de pastille. Les filets simples marquent les séparations ordinaires, les doubles filets les coupures éditoriales fortes. Les dialogues et composants des archives gardent leurs formes particulières.

## Components

### Buttons

Contrôles compacts et lisibles, avec une hauteur minimale de (44px). Le bouton neutre utilise l’encre et un filet beige ; le bouton sombre inverse l’encre et le papier. Les actions de barre ont une typographie sans sérif plus petite. Le focus visible commun est un contour vert de (3px), décalé de (4px).

### Inputs / Fields

Les champs ivoire ont un filet beige, des angles légèrement adoucis et une hauteur minimale de (46px). Leur texte est sans sérif à (14px), puis (16px) sur mobile. Les labels restent séparés du champ. Les listes de sélection suivent le même langage que la recherche.

### Navigation

Les vues sont des onglets plats. L’onglet actif associe graisse renforcée, texte vert et soulignement de (3px) ; le survol annonce le lien par le vert. Le défilement horizontal conserve l’accès aux vues sur mobile.

### Chips

Les rubriques sont des pastilles à filet beige. La rubrique sélectionnée utilise un fond vert et un texte blanc ; `aria-pressed` porte son état. Elles restent sur une ligne défilante sur mobile.

### Cards / Containers

Un article du fil est une rangée séparée par un filet, sans ombre individuelle. Le titre, la source, la date et la langue précèdent l’extrait ; la lecture chez l’éditeur et l’action Garder terminent le bloc. Les liens de titre se soulignent au survol. L’état Gardé ajoute un fond vert pâle et remplit le signet, en plus du libellé et de `aria-pressed`.

### Masthead & images

La manchette Fraktur et les doubles filets sont la signature réutilisable du journal. Les visuels proviennent des publications et conservent leur provenance dans les données, ainsi que les crédits HTML existants des archives. Ils peuvent être documentaires ou illustratifs selon l’éditeur. Le filtre sépia est actif par défaut ; la commande Images en couleurs permet de retrouver les couleurs. Les cadrages dépendent du rôle du visuel ; un document ou une affiche d’archive peut conserver son format intégral.

Les transitions de couleur et de fond restent courtes (0.18s) ; celles du filtre d’image durent (0.25s), lorsque la préférence de mouvement l’autorise. La préférence de mouvement réduit supprime le défilement animé.

## Do's and Don'ts

### Do:
- **Do** conserver la manchette Fraktur, le papier clair et l’encre brune.
- **Do** séparer la prose de lecture des dates, sources et légendes par la typographie.
- **Do** conserver les crédits, la provenance et l’accès explicite au média d’origine.
- **Do** rendre la sélection et le focus visibles en plus de leurs états accessibles.

### Don't:
- **Don't** transformer chaque article en carte flottante avec une ombre.
- **Don't** généraliser les règles typographiques héritées des archives aux métadonnées actuelles.
- **Don't** remplacer les visuels de presse par des images synthétiques.
- **Don't** imposer la composition de cette une à tous les futurs écrans.
