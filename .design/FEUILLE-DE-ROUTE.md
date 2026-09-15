# FEUILLE-DE-ROUTE refonte design zennotes-share (fait foi)

Socle : P-robuste. Public : esprit P-lecture-first. Admin : esprit P-admin-power SANS bottom-sheet custom. Degradation N0/N1/N2 partout. Sans build, CSS inline, JS vanilla.

## 1. Tokens finaux

```css
:root{color-scheme:light dark;
--bg:#fbfaf7;--fg:#23211c;--muted:#6f6a5e;--surface:#fff;--border:#e8e2d5;
--link:#3d56c4;--accent:#4f6df5;--focus:#2f4bff;--code-bg:#f1eee6;--danger:#b3261e;
--font-read:"Source Serif 4",Georgia,"Bitstream Charter","Times New Roman",serif;
--font-ui:Inter,system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;
--font-mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
--sp-1:.25rem;--sp-2:.5rem;--sp-4:1rem;--sp-6:1.5rem;--sp-12:3rem;
--radius-s:.375rem;--radius-m:.5rem;--radius-l:.8rem;--shadow-sm:0 1px 3px rgba(0,0,0,.06)}
@media(prefers-color-scheme:dark){:root{--bg:#191813;--fg:#ece7db;--muted:#a8a294;
--surface:#23211b;--border:#3a372e;--link:#9db1ff;--accent:#7c93ff;--focus:#aebfff;
--code-bg:#26221c;--danger:#ff8a80}}
html[data-theme="light"]{color-scheme:light}html[data-theme="dark"]{color-scheme:dark}
```
Polices : systeme en base, 1 seul `<link>` Google Fonts `display=swap` (Source Serif 4 + Inter) en progres non bloquant. Jamais plus de 2 familles par page. Code toujours mono systeme.
Tailles (rem) : 12/14/16/18/20/24/32/40, ratio 1.25. Lecture 17px mobile mini 16px strict, 18px desktop. Admin 15/16px, labels 13/14px, jamais sous 12px, inputs 16px mini anti zoom iOS. H1 `clamp(1.75rem,1.3rem+2.2vw,2.5rem)`, h2 1.5rem, h3 1.25rem.
Lignes : 1.6 lecture, 1.5 UI, 1.15 h1, 1.25 h2/h3, 1.5 code. Titres `balance`, corps `pretty`, gauche seul, `hyphens:auto`.
Layout : lecture `max-width:40rem` plafonne `65ch`, marges 20px mobile / 24px desktop. Admin `max-width:72rem`. Tranche : 46rem refuse, 40rem + 65ch retenu.
Theme : `auto` par defaut suit systeme. Manuel `light|dark|auto` en `localStorage zn-theme`, pose par script inline dans `<head>` anti flash. Contraste vise : 4.5:1 texte, 3:1 UI et focus. Focus `:focus-visible{outline:2px solid var(--focus);outline-offset:2px}`.

## 2. Spec page publique `/s/{token}`

Ordre : top bar fine (logo + badge Lecture partagee + temps lecture, theme range en pied), hero H1 + meta (date MAJ, duree, expiration) + filet, sommaire `details` TOUJOURS replie par defaut si 3+ h2, article `.pub-article`, pied discret (Partage via ZenNotes + expiration + Copier le lien, rien de marketing).
Composants : progression 3px sans chiffre, callouts 3 max (info, attention, astuce) au filet gauche, code scroll-x interne + bouton Copier, tableaux en `.table-scroll{overflow-x:auto}` + `tabindex=0` + ombre indice, images `max-width:100%` + lazy + legende + alt visible, bouton haut de page apres 2 ecrans, zones scroll clavier.
Pipeline serveur `render.py` : `Markdown>=3.7`, `pymdown-extensions==11.0.2`, `Pygments>=2.19,<2.21`, `bleach>=6.1`, `KaTeX>=0.16.21`. Extensions : tables, sane_lists, toc (slugify pymdownx), attr_list, md_in_html, superfences (`disable_indented_code_blocks True`), highlight (`use_pygments True`, `guess_lang False`), tasklist (`custom_checkbox True`), arithmatex (`generic True`, `smart_dollar True`), inlinehilite. Pygments CSS genere une fois via `HtmlFormatter`. Wikilinks et frontmatter resolus AVANT markdown comme aujourd hui.
Bleach strict : tags = base + h1-h6, pre, img, table, thead, tbody, tr, th, td, hr, div, span, label, input. Attrs : a href/title, img src/alt/title, class sur code/pre/span/div/li/ul/label, th/td align, input type/checked/disabled. `strip True`. Jamais script, style, on*, MathML, SVG, b64, snippets.
KaTeX client seul : `katex.min.js` puis `auto-render.min.js` en `defer` + SRI + crossorigin, init sur `DOMContentLoaded`. Ordre : `$$` display, puis `$` inline, puis `\( \)` et `\[ \]`. Options `trust:false, throwOnError:false, strict:warn`. `$2.50` ne rend pas de maths par design.
Replis : N0 sans JS ni CDN = lecture complete, code deja colore serveur, maths en source `$..$` lisible en scroll-x jamais vide. N1 fonts OK = confort seul. N2 KaTeX OK = belles formules. Si copie JS KO, bouton masque. Si `toc` vide, sommaire masque.
Etats : mot de passe = meme gabarit lecture, 1 champ centre + bouton Afficher + `enterkeyhint=go` + `autocorrect off` + `autocapitalize off`, erreur douce sans jargon, rappel d expiration. 404 neutre = `Ce lien est invalide ou expire`, sans code, sans detail, SANS bouton Copier (rien a copier). Ni pub ni partage social.
Print : `@media print` en fin de CSS masque nav/boutons/progression/formulaires, fond blanc texte noir, `@page{margin:2cm}`, liens externes avec URL affichee, bloc `.print-only` (titre + URL + date).

## 3. Spec admin `/`

Mobile-first 360px : 1 colonne ordre filtre notes, creation lien, liens actifs. Desktop `>=800px` : grille `22rem + 1fr`, `>=1100px` confort. Pas de grille 2 col sous 800px. Zero dependance.
Login : carte centree 24rem, 1 password, bouton Ouvrir 100 %, Entree valide, erreur inline sous champ, cle gardee en echec, aide stockage onglet seul (`sessionStorage`).
Header compact : dot + ZenNotes Share + statut cle + Deconnexion + bascule theme 44px avec `aria-pressed`.
Bloc notes : recherche sticky sous header + compteur + croix effacer, cartes compactes (titre 1 ligne tronquee + chemin gris), selection bordure accent gauche, etat vide bienveillant + Reinitialiser.
Bloc creation : chemin preselectionne modifiable, duree en segments [24h,7j,30j] + champ libre, vues max et mot de passe replies en `details`, CTA Creer sticky bas mobile 48px, validation inline + focus premier fautif, succes URL copiable + Copier + toast `Lien copie`.
Bloc liens : cartes mobile (titre + badges Expire/Vues + 2 boutons Copier/Revoquer 44px), tableau 4 col des 800px seul. Revocation = `confirm()` natif PUIS toast Annuler 5s. Bottom-sheet custom et confirm inline REFUSES (cout JS et a11y pour action rare). Etats vide initial avec CTA premier lien, hors ligne avec Reessayer.
Feedbacks : toast bas centre 1-2 lignes 3s, tap pour fermer, `role=status` + `aria-live=polite`. Formulaires : labels explicites, erreurs `aria-describedby`, Entree soumet, Esc ferme, `prefers-reduced-motion` coupe animations.

## 4. Pieges techniques a eviter imperativement

1. Test `"<li>"` : avec tasklist custom, `<li class=...>` remplace `<li>`. Assouplir en `"<li"` + ajouter cas liste simple + bornes `$$` multiligne, `$` dans code, `$2.50` non rendu, tableau align, frontmatter.
2. Accolades et `.format` : `PAGE_HTML.format` casse sur chaque `{` CSS/JS (doublement obligatoire, erreurs silencieuses). Passer a `string.Template` ou marqueurs `__CONTENT__`/`__TITLE__`, et decouper `BASE_CSS`, `PUB_HTML`, `ADMIN_HTML`.
3. Allowlist bleach : sans `label` en tags + `class` sur label/li/ul/span/div/pre/code, bleach mutile tasklist et arithmatex. Reprendre liste exacte section 2.
4. Delimiteurs KaTeX : `$` avant `$$` capture `$$` en expression vide. Ordre impose section 2 + `generic True` sinon `<script type=math>` detruit par bleach.
5. Poids CDN : KaTeX (~300 Ko) + Fonts = 90 % du poids public. `defer` partout, pas de `@import` bloquant, pas de cumul Pygments + highlight.js (flash + fausse detection). Pinner `Pygments<2.21` (2.20 casse superfences) et `pymdown==11.0.2` (ReDoS).
6. Divers : `confirm()` iOS anxiogene accepte car rare. Sommaire toujours replie (pas ouvert). Theme lecture en pied (pas en top bar). Wrap 46rem interdit.

## 5. Decoupage en 2 lots

LOT A (page publique + render.py) : pipeline section 2 + allowlist + `PUB_HTML` (header/hero/progression/sommaire/article/pied/etats/print) + KaTeX defer SRI + Copier code + retour haut + theme auto/manuel anti flash. `tests/test_links.py` reste vert (avec ajustement `<li` documente). N apporte aucun changement a `/api/notes`.
LOT B (ADMIN_HTML dans app.py) : reprend BASE_CSS, layout 1 col vers grille, login/filtre/creation/cartes/tableau/toast/`confirm` natif + Annuler 5s/vide/hors ligne. Endpoint `/api/notes` inchange (meme contrat path/title/folder/size/updated_at).
Acceptation LOT A : 360px et 1280px zero scroll-x page, clavier seul complet, CDN coupe = article lisible + code colore + maths source visible, contraste AA clair/sombre, print texte seul, password/404 au gabarit.
Acceptation LOT B : 360px 1 colonne ordre filtre/creation/liens, 1280px grille 22rem+1fr, clavier seul (Entree/Esc/focus premier fautif), CDN coupe = admin utilisable, contraste AA, toast 3s + Annuler revoquer 5s, inputs 16px et cibles 44px (24px mini absolu).
