# P-robuste : proposition sobre et tolerante aux pannes

Principe : page lisible sans JS ni CDN. Tout ajout distant est optionnel et rate silencieusement. Esthetique par typo et espace, pas par effets.

## 1. Tokens

Couleurs (sementique, light par defaut, dark via media) :
```
:root{--bg:#faf9f6;--fg:#1f1e1b;--muted:#6b675e;--surface:#fff;--border:#e3ded2;
--link:#2f4fd0;--accent:#2f4fd0;--focus:#1a3fd4;--code-bg:#f1eee6;color-scheme:light dark}
@media(prefers-color-scheme:dark){:root{--bg:#171512;--fg:#ece8df;--muted:#b3ac9e;
--surface:#221f1b;--border:#3a352c;--link:#9db1ff;--accent:#9db1ff;--focus:#c2cfff;--code-bg:#26221c}}
```

Polices : systeme d abord, CDN en progres :
```
--font-read:Georgia,"Bitstream Charter","Times New Roman",serif;
--font-ui:system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;
--font-mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
```
Optionnel : Source Serif 4 + Inter via un seul link Google Fonts avec display=swap et preconnect non bloquant. Si echec, fallback immediat sans CLS car metriques proches.
Echelle : 12/14/16/18/20/24/32px en rem. Corps lecture 17px mobile mini 16px, UI 15px. Interligne 1.6 lecture, 1.5 UI. Mesure 65ch max 40rem.

## 2. Page publique /s/{token}

Ordre : header fin (logo + badge Lecture partagee + temps lecture), hero H1 clamp + meta (date, expiration), sommaire details replie si 3+ titres, article, pied discret (Partage via ZenNotes + expiration + bouton Copier lien).
Etats : mot de passe (meme gabarit, 1 champ centre, erreur douce), 404 neutre (Ce lien est invalide ou expire, sans code).
Composants sobres : progression 3px sans chiffre, callouts 3 max au filet gauche, tableaux en scroll-x avec tabindex 0, code en scroll-x + bouton Copier, images lazy avec alt visible, bouton haut de page apres 2 ecrans, print CSS texte seul.

## 3. Page admin /

Mobile first 1 colonne : filtre notes sticky + compteur, creation lien, liens actifs en cartes. Desktop 800px+ : grille 22rem + 1fr, max 72rem.
Connexion : carte centree, 1 champ password, validation Entree, erreur inline, cle gardee en sessionStorage onglet seul.
Creation : chemin preselectionne, duree en segments 24h/7j/30j + champ libre, options repliees en details, CTA sticky bas mobile, succes avec URL + bouton Copier 48px.
Liens : cartes avec badges Expire/Vues + 2 boutons larges Copier/Revoquer, confirm simple, toast bas centre 3s avec Annuler 5s pour revoquer, etats vide et hors ligne avec Reessayer.

## 4. Pipeline de rendu avec replis

Serveur (render.py) :
```
extensions=[tables,sane_lists,toc,attr_list,md_in_html,superfences,highlight,tasklist,arithmatex,inlinehilite]
superfences+highlight avec use_pygments True, guess_lang False, CSS Pygments inline genere une fois.
arithmatex generic True + smart_dollar True pour format span/div que bleach garde.
bleach : ajouter label + class sur label,li,ul,span,div,pre,code. Jamais script, style, on*.
```
Epingler : Markdown>=3.7, pymdown-extensions 11.0.2, Pygments 2.19.x, bleach>=6.1.
Client : katex.min.js + auto-render en defer avec SRI, ordre $$ puis $ puis \( \) et \[ \]. Options trust false, throwOnError false, strict warn, lance sur DOMContentLoaded.
Replis : sans JS, code deja colore serveur et maths en texte brut lisible ($..$ visible, jamais vide). Si KaTeX CDN echoue, texte source reste. Si police CDN echoue, systeme prend le relais. Zero renderToString serveur.

## 5. Strategie de degradation

Niveau 0 (HTML+CSS inline seuls) : lecture complete, admin utilisable au clavier, contraste AA verifie.
Niveau 1 (CDN polices OK) : confort typographique, aucun changement de layout.
Niveau 2 (KaTeX OK) : belles formules, sinon scroll-x sur source large.
Regles : aucun link ou script bloquant, defer partout, pas de @import, pas de framework, base CSS commune BASE_CSS en 7 blocs avec prefixes .pub- et .adm-, focus visible 2px, reduced-motion coupe animations, theme auto + bascule manuelle en localStorage avec script anti flash dans head.

## 6. Repris et refuse des R1

Repris : R1-typo (echelle rem, clamp H1, 65ch, hyphens), R1-rendu (superfences+highlight serveur, arithmatex generic, SRI KaTeX), R1-lecture (header fin, sommaire replie, print, 404 douce), R1-admin (mobile 360px, cartes, segments duree, toast), R1-a11y (variables semantiques, focus, cibles 44px, print-only), R1-css (BASE_CSS, tokens 2 couches, BEM simple, table-scroll).
Refuse : R1-typo (chargement woff2 manuel, on garde link simple), R1-rendu (highlight.js client + MathML/SVG serveur + snippets/b64, risque et flash), R1-lecture (zoom clic image complexe + partage social, hors scope ephemere), R1-admin (bottom sheet custom, on garde confirm natif), R1-a11y (bascule theme obligatoire cote serveur, auto systeme suffit en v1), R1-css (spacing rem obligatoire hors root, on tolere px pour bordures 1px).

## 7. Taches pour 2 devs

Dev A (page publique + rendu) :
1. Migrer render.py vers pipeline superfences/highlight/arithmatex + bleach + tests bornes.
2. Extraire CSS lecture en BASE_CSS blocs 1-5 + page publique (header, hero, sommaire, print).
3. Ajouter KaTeX defer SRI + fallback texte + bouton Copier code + progression.
4. Etats password/404 + a11y lecture (focus, reduced-motion, contrastes).

Dev B (admin) :
5. Extraire CSS admin en blocs 6-7 + cartes mobiles + tableau desktop + toast.
6. Refaire ecrans cle/filtre/creation (segments duree, details, validation inline).
7. Liste liens en cartes + confirm natif + Annuler 5s + etats vide/hors ligne.
8. Theme auto + bascule manuelle + audit clavier 200 pourcent + 360px.
