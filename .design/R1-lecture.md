# R1 - UX page de lecture zennotes-share
Contexte : lien ephemere, mobile first, destinataire non technique.
Sources : Medium, Substack, docs techniques, lecteurs markdown mobile.

## Structure de page cible
1. Header minimal fixe : logo ZenNotes + badge "Lecture partagee" + temps de lecture.
2. Hero titre : titre H1 28px, meta ligne (date, duree, expiration du lien), filet discret.
3. Barre de progression fine 3px en haut, couleur accent, sans pourcentage chiffre.
4. Sommaire repliable sous le hero si 3+ titres, ancres avec scroll doux.
5. Corps 68ch max, 18px, interligne 1.65, paragraphes courts aeres.
6. Pied discret : "Partage via ZenNotes", date d expiration, aucun lien marketing.

## Contenu riche
7. Images : pleine largeur col, legende grise, lazy load, clic pour zoom, alt visible si echec.
8. Code : bloc scroll horizontal interne, bouton Copier sticky, theme contraste AA, pas de retour auto.
9. Tableaux : conteneur scroll-x avec ombre indice, premiere colonne figeable, zebrage leger.
10. Maths : rendu avec fallback texte brut, taille min 16px, scroll-x si formule large.
11. Callouts : 3 styles max (info, attention, astuce), bord gauche epais + icone, jamais de rouge agressif.
12. Titres ancres : lien # visible au survol et au tap, espacement fort au dessus du H2.

## Mobile et lisibilite
13. Colonne unique, marges 16-20px, taille corps 17px mini, intertitres 22-24px.
14. Eviter tout scroll horizontal de page : tester code, tableaux et images a 360px.
15. Mode sombre auto via prefers-color-scheme, contraste texte/fond verifie AA.
16. Bouton retour en haut apres 2 ecrans, police systeme pour vitesse et zero CLS.

## Etats speciaux
17. Page mot de passe : meme gabarit, champ unique centre, message bienveillant, erreur douce sans jargon.
18. Page 404 neutre : "Ce lien est invalide ou expire", aucune info sur la note, bouton Retour discret.
19. Messages sans code : jamais "403" ou "404" en gros, vocabulaire simple pour non techniques.
20. Accessibilite : focus visible, zones scroll clavier (tabindex 0), reduction des animations.

## Petits plus qui changent tout
21. Temps de lecture estime et date de mise a jour sous le titre pour cadrer l effort.
22. Impression propre via print CSS : texte seul, sans header ni progression.
23. Partage : bouton Copier le lien en pied, pas de pop-up ni pub, respect du caractere ephemere.
