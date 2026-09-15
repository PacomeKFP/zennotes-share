# R1 Admin Mobile-First pour zennotes-share
Contexte : sidecar mono fichier HTML sans build, variable ADMIN_HTML dans app.py. Usage proprio sur mobile.

## Principes
1. Designer a 360px en premier, puis etendre a desktop par media queries a 800px et 1100px.
2. Une seule colonne sur mobile, ordre : filtre notes, creation lien, liens actifs. Pas de grille 2 colonnes sous 800px.
3. Cibles tactiles 44px min pour boutons, lignes de notes et icones copier et revoquer.
4. Garder zero dependance : CSS inline avec variables, JS vanilla, meta viewport, input 16px min contre le zoom iOS.

## Ecran 1 : connexion par cle
5. Centrer une carte unique avec 1 champ password, 1 bouton Ouvrir plein largeur, texte aide sur stockage onglet seul.
6. Valider a l'Entree, message d'erreur inline sous le champ, garder la cle saisie en cas d'echec.

## Ecran 2 : navigateur de notes avec filtre
7. Barre de recherche sticky sous le header avec compteur de resultats et bouton effacer en croix.
8. Liste en cartes compactes : titre sur 1 ligne tronquee plus chemin petit en gris, selection avec bordure accent a gauche.
9. Prevoir etat vide : si filtre sans resultat, afficher texte bienveillant plus bouton Reinitialiser le filtre.

## Ecran 3 : creation de lien
10. Formulaire court vertical : chemin preselectionne en lecture seule modifiable, duree en segments [24h, 7j, 30j] plus champ libre, vues max et mot de passe replie en details optionnels.
11. CTA principal Creer le lien sticky en bas sur mobile, validation inline immediate, succes avec URL copiable plus bouton Copier 48px.
12. Erreurs ciblees : chemin invalide, duree hors borne, mot de passe trop court, chaque erreur sous son champ, focus sur premier champ fautif.

## Ecran 4 : liste des liens
13. Remplacer le tableau par des cartes sur mobile : note en titre, badges Expire et Vues, 2 boutons larges Copier et Revoquer par carte. Repasser en tableau a 4 colonnes sur desktop seulement.
14. Revoquer avec confirmation en bottom sheet mobile et dialogue simple desktop, action annulable par toast avec bouton Annuler 5s.
15. Feedbacks : toast bas centre 1 a 2 lignes max 3s dismissible au tap, etat vide initial avec CTA Creer mon premier lien, etat hors ligne avec bouton Reessayer.

## Desktop
16. Reprendre la grille actuelle max 72rem : notes a gauche 22rem fixe, formulaire plus liens a droite, header compact avec statut cle et bouton Deconnexion.
