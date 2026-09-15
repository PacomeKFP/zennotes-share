# R1 - Typographie et polices - zennotes-share
Date : 2026-09-15. Pages cibles : lecture publique + admin. Sans build, un seul fichier, mobile d'abord.

## Combinaison retenue
- Lecture : `Source Serif 4` (CDN Google Fonts) + fallback `Georgia, Bitstream Charter, Times New Roman, serif`
- UI admin : `Inter` (CDN) + fallback `system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif`
- Code : `ui-monospace, SFMono-Regular, Menlo, Consolas, Liberation Mono, monospace`
- Variables : `--font-read`, `--font-ui`, `--font-mono`. Jamais plus de 2 familles par page.

## Recommandations actionnables
1. Charger les 2 polices en `woff2` via un seul `<link>` Google Fonts avec `display=swap`, puis fallback systeme immediat si CDN bloque.
2. Lecture publique : corps a `17px` desktop et `18px` article large, plancher strict a `16px` sur mobile pour eviter le zoom auto iOS.
3. Admin : corps a `15px` ou `16px`, petits labels a `13-14px` avec contraste mini `4.5:1`, jamais sous `12px`.
4. Appliquer l'echelle `12 / 14 / 16 / 18 / 20 / 24 / 32 / 40px` avec ratio `1.25`, definie en `rem` via `:root`.
5. Rendre le `h1` fluide avec `clamp(1.75rem, 1.3rem + 2.2vw, 2.5rem)` et les `h2/h3` fixes a `1.5rem / 1.25rem`.
6. Hauteurs de ligne sans unite : lecture `1.6`, UI `1.5`, titres `1.15` pour h1 et `1.25` pour h2/h3, code `1.5`.
7. Colonne lecture : `max-width: 65ch` plafonnee a `40rem` (640px), centree, marges laterales `20px` mobile et `24px` desktop.
8. Admin : conteneur `max-width: 72rem` (1152px), cartes et tableaux en pleine largeur, texte d'aide limite a `60ch`.
9. Paragraphes lecture : `margin: 0 0 1.5em`, intertitres avec plus d'espace dessus que dessous, listes avec `line-height: 1.5`.
10. Titres : `text-wrap: balance`, corps : `text-wrap: pretty`, alignement a gauche uniquement, activer `hyphens: auto` + `overflow-wrap: break-word`.
11. Ne jamais justifier, ne pas toucher au tracking du corps, ajouter `+0.04em` aux labels tout en majuscules et `-0.01em` au h1 large.
12. Verifier a `390px`, a `1280px` et a zoom `200 %` : pas de scroll horizontal, mesure entre `45-75` signes desktop et `30-50` mobile.
