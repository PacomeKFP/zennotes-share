# P lecture-first : page publique star, admin sobre

Principe : 80 % du soin sur `/s/{token}`, admin = outil rapide. Sans build, un seul `app.py`, CSS inline en `BASE_CSS`, mobile first.

## 1. Tokens

```css
:root{
  color-scheme: light dark;
  --font-read: "Source Serif 4", Georgia, "Bitstream Charter", "Times New Roman", serif;
  --font-ui: Inter, system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  --bg: #fbfaf7; --fg: #23211c; --muted: #6f6a5e; --surface: #fff; --border: #e8e2d5;
  --link: #3d56c4; --accent: #4f6df5; --focus: #2f4bff; --call-info: #3d56c4;
  --sp-1: .25rem; --sp-2: .5rem; --sp-4: 1rem; --sp-6: 1.5rem; --sp-12: 3rem;
  --radius-m: .5rem; --radius-l: .8rem; --shadow-sm: 0 1px 3px rgba(0,0,0,.06);
}
@media (prefers-color-scheme: dark){
  :root{ --bg:#191813; --fg:#ece7db; --muted:#a8a294; --surface:#23211b;
    --border:#3a372e; --link:#9db1ff; --accent:#7c93ff; --focus:#aebfff; }
}
html[data-theme="light"]{ color-scheme: light; }
html[data-theme="dark"]{ color-scheme: dark; }
```

Typo : corps lecture 17px mobile, 18px desktop, mini 16px strict. Admin 15-16px, labels 13-14px, jamais sous 12px. Ligne 1.6 lecture, 1.5 UI, 1.15 h1. H1 `clamp(1.75rem,1.3rem+2.2vw,2.5rem)`, h2 1.5rem, h3 1.25rem. Colonne `65ch` max `40rem`, marges 20px mobile et 24px desktop.

## 2. Page publique `/s/{token}` section par section

1. Top bar fixe 3px progression + ligne : logo, badge "Lecture partagee", temps lecture, bouton theme.
2. Hero : h1 balance, meta (date MAJ, duree, expiration lien), filet `border-bottom`.
3. Sommaire `details` ouvert si 3+ h2, ancres douces, lien # au survol et au tap.
4. Article `.pub-article` : p `0 0 1.5em`, img `max-width:100%` + lazy + legende, code scroll-x + bouton Copier, tableaux en `.table-scroll` avec ombre indice, callouts 3 max (info, attention, astuce) a bord gauche, maths scroll-x.
5. Pied discret : "Partage via ZenNotes", expiration, bouton Copier le lien. Rien de marketing.
6. Etats : mot de passe (meme gabarit, 1 champ centre, erreur douce), 404 neutre ("lien invalide ou expire", pas de code 403/404 en gros).
7. Print : masque nav et boutons, fond blanc, URL externes affichees, bloc print-only titre + URL + date.

## 3. Page admin `/` sobre et fonctionnelle

Garde grille actuelle `max-width:72rem`, 1 colonne sous 800px. Ordre mobile : filtre, creation, liens actifs.
1. Login : carte centree, 1 password, bouton Ouvrir 100 %, Entree valide, erreur inline, cle gardee en echec.
2. Notes : recherche sticky + compteur + croix effacer, cartes compactes titre 1 ligne + chemin gris, selection bordure accent gauche, etat vide bienveillant.
3. Creation : chemin preselectionne modifiable, duree en segments [24h,7j,30j] + champ libre, vues max et password en `details`, CTA sticky bas mobile, succes URL + Copier 48px.
4. Liens : cartes mobile (titre, badges Expire et Vues, Copier et Revoquer 44px), tableau 4 col desktop seul. Revocation avec confirm simple + toast Annuler 5s. Toast bas centre 3s, etat vide avec CTA, etat hors ligne avec Reessayer.
5. Aucune serif ni ombre lourde cote admin : Inter, cartes plates existantes, focus `:focus-visible` conserve.

## 4. Pipeline de rendu

Serveur : `Markdown>=3.7`, `pymdown-extensions==11.0.2`, `Pygments>=2.19,<2.21`, `bleach>=6.1`.
Extensions : `tables, sane_lists, toc, attr_list, md_in_html, pymdownx.superfences, pymdownx.highlight, pymdownx.tasklist, pymdownx.arithmatex, pymdownx.inlinehilite`. Config : superfences sans code indente, highlight `guess_lang False` + `use_pygments True`, tasklist `custom_checkbox True`, arithmatex `generic True` + `smart_dollar True`, toc avec slugify stable.
Bleach : ajout `label` + `class` sur `span, div, pre, code, label, li, ul`, `th,td[align]`, jamais `script, style, on*`. KaTeX `>=0.16.21` cote client en auto-render ordre `$$` puis `$` puis `\( \)` et `\[ \]`, options `trust False, throwOnError False, strict warn`, CDN avec SRI + defer, appel sur `DOMContentLoaded`.

## 5. Strategie mobile

Base 360px, `@media(min-width:800px)` admin 2 col, `@media(min-width:1100px)` confort lecture. Zero scroll-x page a 360px, code et tableaux en scroll interne clavier (`tabindex 0`). Cibles 44px actions, 24px mini absolu. `prefers-reduced-motion: reduce` coupe animations. Test : 390px, 1280px, zoom 200 %.

## 6. Repris et refuse des R1

Repris : R1-typo (Source Serif 4 + Inter, echelle rem, h1 clamp, 65ch), R1-lecture (header minimal, progression 3px, sommaire repliable, callouts 3 max, print), R1-rendu (pymdownx.highlight + arithmatex generic + KaTeX client + bleach strict), R1-admin (1 colonne mobile, segments duree, cartes liens, toast), R1-a11y (variables semantiques, color-scheme, contraste 4.5:1, focus visible, reduced-motion), R1-css (BASE_CSS en 7 blocs, BEM `.btn--primary`, prefixes `.pub-` et `.adm-`, tokens seuls dans `:root`).
Refuse : R1-lecture police systeme pour vitesse (on garde serif CDN avec fallback, gain lecture superieur), zebrage figeable des tableaux (trop lourd, scroll-x + ombre suffit), R1-rendu highlight.js client (on garde Pygments serveur, zero JS au premier paint), R1-a11y bascule theme avec libelle texte visible (icone + aria-label suffit sur page lecture), R1-css wrap 46rem unique (on garde 40rem + 65ch de R1-typo), R1-admin bottom-sheet de confirmation (dialogue natif plus simple et robuste).

## 7. Taches pour 2 developpeurs

Dev A (page publique + rendu) :
1. Migrer `render.py` vers pipeline pymdownx + bleach + tests bornes (maths, code inconnu, taches, tableaux).
2. Extraire `BASE_CSS` + `PUB_HTML` : tokens, top bar, hero, progression JS, sommaire, callouts.
3. Ajouter KaTeX SRI + auto-render + bouton Copier code + retour en haut + print CSS.
4. Unifier password et 404 au gabarit lecture + theme auto et manuel sans flash.

Dev B (admin sobre) :
5. Refonte responsive admin : 1 colonne mobile, segments duree, `details` options, CTA sticky.
6. Cartes liens mobile + tableau desktop, confirm suppression, toast Annuler, etats vides et hors ligne.
7. Accessibilite formulaires : labels, `aria-describedby`, `role status`, focus clavier, Entree et Esc.
8. Recette commune : 360px, 1280px, zoom 200 %, contraste AA, zero scroll-x, doc une ligne par ajout dans `.design/`.
