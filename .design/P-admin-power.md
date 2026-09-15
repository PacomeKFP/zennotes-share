# P Admin Power : admin star, public simple
Angle : admin rapide et dense, utilisable au pouce sur mobile, avec navigateur de notes excellent. Public : lecture elegante mais volontairement simple. Zero build, CSS inline dans app.py, JS vanilla.
Fichiers touches : src/zennotes_share/app.py (PAGE_HTML, ADMIN_HTML, BASE_CSS), src/zennotes_share/render.py.

## 1. Tokens
Couleurs (clair) : --bg #f6f4ef, --surface #ffffff, --fg #1f1e1a, --muted #6b675c, --border #e8e2d5, --accent #4f6df5, --accent-d #3d56c4, --danger #b3261e, --focus #4f6df5.
Sombre : memes noms surcharges par prefers-color-scheme puis html[data-theme], jamais de couleur en dur hors :root. color-scheme: light dark.
Polices : --font-read "Source Serif 4", Georgia, serif (public seul). --font-ui Inter, system-ui, Segoe UI, Roboto, sans-serif (admin). --font-mono ui-monospace, Menlo, Consolas, monospace. Max 2 familles par page.
Tailles : echelle 12/14/16/18/20/24/32/40 en rem. h1 clamp(1.75rem, 1.3rem + 2.2vw, 2.5rem). h2 1.5rem, h3 1.25rem. Public 17px mini, 18px article. Admin 15/16px, labels 13/14px, jamais sous 12px, inputs 16px mini anti zoom iOS.
Rythme : line-height lecture 1.6, UI 1.5, h1 1.15, code 1.5. text-wrap balance titres, pretty corps, gauche seul, hyphens auto.
Espaces : base 4px : --sp-1 .25rem, --sp-2 .5rem, --sp-4 1rem, --sp-6 1.5rem, --sp-12 3rem. Radius s .375rem, m .5rem, l .8rem. Shadow sm/md legers.
Layouts : .wrap public max 46rem / 65ch centre, marges 20px mobile 24px desktop. .adm-layout max 72rem, desktop grid 22rem + 1fr, mobile 1 colonne.

## 2. Page publique, section par section
Header minimal fixe : logo ZenNotes + badge Lecture partagee + temps lecture. Pas de nav ni pub.
Hero : H1 28px fluide, meta ligne date + duree + expiration, filet discret.
Progression : barre 3px accent en haut, sans chiffre.
Sommaire : details repliable sous hero si 3+ titres, ancres douces, lien # visible survol et tap.
Article : .pub-article 65ch max, images 100% + legende + lazy + alt, code scroll-x + bouton Copier, tableaux scroll-x + zebrage, maths scroll-x, callouts 3 max info/attention/astuce.
Pied : Partage via ZenNotes + expiration, bouton Copier le lien, rien de marketing.
Etats : mot de passe (carte centree, 1 champ, erreur douce), 404 neutre sans code ni detail, vocabulaire simple.
Print : texte seul noir sur blanc, nav et boutons masques, URLs externes affichees, print-only titre + URL + date.

## 3. Page admin, section par section
Login : carte centree 24rem, 1 champ password + bouton Ouvrir plein largeur, Entree valide, erreur inline, cle gardee en echec, aide stockage onglet seul.
Header compact : dot + ZenNotes Share + statut cle + Deconnexion + bascule theme 44px.
Bloc 1 filtre notes : recherche sticky + compteur + croix effacer, liste cartes compactes titre 1 ligne tronquee + chemin gris, bordure accent gauche si selection, vide bienveillant + Reinitialiser.
Bloc 2 creation lien : chemin preselectionne modifiable, duree segments 24h/7j/30j + champ libre, vues max et mot de passe en details, CTA Creer sticky bas mobile 48px, erreurs inline + focus premier fautif, succes URL copiable + Copier.
Bloc 3 liens actifs : cartes mobile (titre + badges Expire/Vues + 2 boutons Copier/Revoquer 44px), tableau 4 colonnes des 800px, Revocation bottom sheet mobile + toast Annuler 5s, vide initial avec CTA premier lien, hors ligne + Reessayer.
Feedbacks : toast bas centre 1/2 lignes 3s tap pour fermer, role status aria-live polite.

## 4. Pipeline rendu minimal mais solide
Extensions : tables, sane_lists, toc (slugify pymdownx), attr_list, md_in_html, pymdownx.superfences (no indented), pymdownx.highlight (use_pygments True, guess_lang False), pymdownx.tasklist (custom_checkbox True), pymdownx.arithmatex (generic True, smart_dollar True), pymdownx.inlinehilite.
Bleach : tags = base + h1-h6, pre, img, table, thead, tbody, tr, th, td, hr, div, span, label, input. Attrs : a href/title, img src/alt/title, code/pre/span/div/li/ul/label class, th/td align, input type/checked/disabled. strip True. Jamais script, style, on*, MathML, SVG.
Client KaTeX : auto-render ordre $$ display puis $ inline puis \( \) et \[ \] , trust false, throwOnError false, strict warn, CDN SRI + crossorigin + defer, init DOMContentLoaded. $2.50 ne rend pas de maths par design.
Securite : frontmatter strip, wikilinks resolus avant markdown, images relatives vers ./a/, Pygments CSS via HtmlFormatter .highlight, zero highlight.js en cumul.
Versions : Markdown>=3.7, pymdown-extensions==11.0.2, Pygments>=2.19 <2.21, bleach>=6.1, KaTeX>=0.16.21. Tests bornes : $$ multiligne, $ dans code, tableau align, frontmatter, gros code inconnu neutre.

## 5. Strategie mobile-first
Base 360px 1 colonne, ordre filtre puis creation puis liens. Media 800px (2 col admin, tableau) et 1100px (air). Titres clamp, pas de grille 2 col sous 800px.
Tactile : 44px mini actions Copier, Creer, Revoquer, theme, lignes notes. 24px absolu si dense avec espacement. Inputs 16px, CTA sticky, recherche sticky sous header.
Scroll : jamais de scroll page horizontal a 360px. Code et tableaux en scroll-x interne avec ombre indice et tabindex 0 clavier. Images max 100%.
Accessibilite : focus 2px + offset 2px contraste 3:1, 1 seul h1, labels + aria-describedby erreurs, Esc ferme dialogues, focus piege puis rendu, reduced-motion coupe animations, contrastes 4.5:1 texte et 3:1 UI valides clair et sombre.
Perf : 1 link Google Fonts display swap + fallback immediat, KaTeX defer seul sur public,.zero framework, script anti flash theme dans head.

## 6. Ce que je reprends et refuse (R1)
Reprends R1-admin : 360px first, 1 colonne ordonnee, 44px, zero dependance, recherche sticky + compteur, cartes compactes, segments duree + details, CTA sticky, cartes liens + tableau desktop, toast + bottom sheet.
Reprends R1-lecture : header minimal, hero + meta, progression 3px, sommaire repliable, etats mot de passe et 404 neutres, print propre.
Reprends R1-typo : duo Source Serif 4 + Inter + mono, echelle 1.25, clamp h1, 65ch/40rem, 16px plancher, balance/pretty.
Reprends R1-rendu : superfences + highlight Pygments, tasklist custom, arithmatex generic, ordre KaTeX, pins versions et CVE KaTeX et pymdown.
Reprends R1-a11y : variables semantiques, color-scheme, data-theme auto + localStorage + anti flash, focus visible, seuils contraste, print group.
Reprends R1-css : BASE_CSS 7 blocs, tokens bruts puis semantiques, BEM .btn/.card/.badge/.field, prefixes .pub-/.adm-, 7 composants partages.
Refuse R1-lecture : police systeme seule (garde serif lecture pour chaleur), corps 16px et gadget Copier en pied comme seul partage (vise 17px mini et succes admin copiable).
Refuse R1-rendu : codehilite seul, cumul Pygments + highlight.js, b64 et snippets, allow MathML/SVG et script math (surface XSS trop large).
Refuse R1-admin : tableau sur mobile et grille 2 colonnes sous 800px (cards + 1 colonne).
Refuse R1-css : tableaux admin en simple scroll permanent (cards mobile d abord), couleurs ou spacings en dur hors root.
Refuse R1-a11y et R1-typo : sombre par inversion ou opacite, texte justifie, tracking corps modifie, labels sous 12px.

## 7. Taches pour 2 devs
Dev A public + rendu :
A1. render.py : bascule extra/codehilite vers pipeline section 4 + bleach + tests bornes.
A2. app.py PAGE_HTML : BASE_CSS partage + gabarit header/hero/progress/TOC/article/pied + etats + print.
A3. KaTeX client + Pygments CSS + bouton Copier code + scroll-x tableaux.
A4. Verif 360px/1280px/200%, contrastes AA clair/sombre, fallback sans CDN.
Dev B admin :
B1. app.py ADMIN_HTML : BASE_CSS + layout 1 col vers grid 22rem + theme data-theme + focus.
B2. Navigateur notes : recherche sticky + compteur + vide + selection vers formulaire.
B3. Creation lien : segments duree + details + validation inline + succes copiable + sticky CTA.
B4. Liens actifs : cards mobile + tableau desktop + bottom sheet + toast Annuler + etats vide/hors ligne.
