# R1 - Systeme CSS sans build
Contexte : un seul fichier `src/zennotes_share/app.py`, CSS inline, deux pages : lecture `/s/{token}` et admin `/`. Pas de build, CDN ok avec fallback.

## Architecture proposee en 7 blocs dans une constante `BASE_CSS`
Ordre : 1 tokens, 2 reset et base, 3 layout, 4 composants, 5 page lecture, 6 page admin, 7 utilitaires et responsive.
Exemple Python : `BASE_CSS = """..."""` puis `PAGE = BASE_CSS.replace("{t}", title)` pour eviter les conflits `{}` des f-strings.

## Recommandations
1. Centraliser tous les tokens dans `:root` avec 2 couches : brut `--blue-500` puis semantique `--color-accent: var(--blue-500)`.
2. Adopter une echelle d'espacements base 4px en rem : `--sp-1: .25rem` jusqu a `--sp-12: 3rem`, bannir toute valeur px hors tokens.
3. Standardiser typo et rayons : `--font-sans: system-ui...`, `--text-sm/base/lg/xl`, `--radius-s/m/l`, `--shadow-sm/md`.
4. Utiliser une nomenclature BEM simplifiee : blocs `.card`, `.btn`, `.badge`, `.field`, variantes `.btn--primary`, `.btn--ghost`, `.btn--danger`.
5. Prefixer le specifique page : `.pub-` pour lecture (`.pub-article`, `.pub-meta`), `.adm-` pour admin (`.adm-layout`, `.adm-note`).
6. Factoriser 7 composants partages : carte, bouton, badge, champ, tableau, toast, bandeau d erreur. Meme classe sur les deux pages.
7. Construire le layout sans framework : `.wrap{max-width:46rem}` lecture, `.adm-layout{display:grid;grid-template-columns:22rem 1fr}` admin.
8. Passer en mobile-first : base 1 colonne, `@media(min-width:800px)` pour 2 colonnes admin, `clamp()` pour les titres.
9. Gerer le responsive des tableaux admin par defilement : `.table-scroll{overflow-x:auto}` au lieu de casser le layout.
10. Isoler le CSS lecture du CSS admin par bannieres `/* === 5. Lecture === */` pour garder un seul fichier lisible.
11. Eviter les fuites de style markdown : `.pub-article img{max-width:100%}`, `pre{overflow:auto}`, `table{border-collapse:collapse}`.
12. Assurer contraste et focus visibles : `:focus-visible{outline:2px solid var(--color-accent)}`, liens soulignes dans l article.
13. Prevoir theme sombre minimal via `[data-theme="dark"]` qui ne redefinit que les tokens semantiques, zero changement composant.
14. Accepter un CDN police avec fallback strict : `font-family: Inter, system-ui, sans-serif` sans `@import` bloquant.
15. Documenter chaque ajout en une ligne dans `.design/` et refuser toute couleur ou spacing en dur hors `:root`.

## Exemples
```css
:root{--sp-4:1rem;--sp-6:1.5rem;--color-accent:#4f6df5;--radius-m:.5rem}
.card{background:var(--color-surface);padding:var(--sp-6);border-radius:var(--radius-m)}
.btn{padding:var(--sp-2) var(--sp-4);border-radius:var(--radius-m)}
.btn--primary{background:var(--color-accent);color:#fff}
.badge{font-size:var(--text-xs);padding:.1rem .6rem;border-radius:999px}
.field input{width:100%;padding:.5rem .6rem;border:1px solid var(--color-border)}
.adm-layout{display:grid;gap:var(--sp-6)}@media(min-width:800px){.adm-layout{grid-template-columns:22rem 1fr}}
```
Sources : echelle 4px en rem, tokens primitifs puis semantiques, override semantique pour dark mode, mobile-first avec media sur `:root`.
