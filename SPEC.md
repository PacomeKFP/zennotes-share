# Cahier des charges : zennotes-share

Partage de notes ZenNotes par liens éphémères. Sidecar indépendant, aucun fork de ZenNotes.

## 1. Contexte et objectifs

Le vault ZenNotes (fichiers `.md` sur le Volume Modal `zennotes-data-prod`) est privé et protégé par token. Besoin : partager une note précise avec un tiers via un lien à durée de vie limitée, sans compte et sans exposer le vault. Usage sporadique : quelques lectures par lien, puis extinction (scale-to-zero).

Objectifs : générer, lister et révoquer des liens éphémères ; page publique de lecture minimaliste ; interface web d'administration ; outils MCP ; coût nul au repos.

Non-objectifs (v1) : édition collaborative, commentaires publics, partage de dossiers entiers, thèmes personnalisés, analytics.

## 2. Architecture

Deux apps Modal indépendantes partageant le même Volume :

* `zennotes-secure-server` (existant) : lecture et écriture privées, scale-to-zero, always single container.
* `zennotes-share` (ce projet) : lecture seule du vault, scale-to-zero, N containers (lecture concurrente sans risque).

Le partage ne duplique aucune note : le lien pointe vers le chemin vault au moment de la création. Si la note est modifiée après, le lien sert la version à jour. Si elle est supprimée ou déplacée, le lien répond 404 (jamais d'erreur 500).

## 3. Modèle de données

Stockage : `modal.Dict` nommé `zennotes-share-links` (persistant, partagé entre containers).

Entrée par token : token URL-safe 24 octets (clé du Dict), avec les champs : `path` (chemin vault, ex `quick/Etude-IA-chinoise/01-Les-donnees.md`), `title`, `created_at` (epoch), `expires_at` (epoch), `max_views` (entier ou null = illimité), `views` (compteur), `password_sha256` (ou null).

Règles : `ttl_hours` entre 1 et 720, défaut 24. `max_views` optionnel supérieur ou égal à 1. Un lien expiré, épuisé ou révoqué répond 404 ou 410, sans distinguer les cas (pas d'oracle).

## 4. API

Base : application FastAPI servie par `@modal.asgi_app`. Auth admin : `Authorization: Bearer <SHARE_ADMIN_TOKEN>` (secret Modal `zennotes-share-admin`), jamais dans l'URL.

* `POST /api/links` body `{path, ttl_hours=24, max_views=null, password=null}` : valide le chemin (normalisé, confiné à `/vol/vault`, fichier `.md` existant), crée l'entrée, répond `{url, token, expires_at}`.
* `GET /api/links` : liste `{token, path, title, created_at, expires_at, views, max_views, has_password}` triée par création décroissante.
* `DELETE /api/links/{token}` : révocation immédiate, idempotente (200 même si absent).
* `GET /s/{token}` : page publique. Vérifie existence, expiration, quota de vues, mot de passe (`?p=` ou formulaire). Incrémente `views` uniquement sur lecture réussie de la page (pas sur les assets). Headers : `X-Robots-Tag: noindex, nofollow`, `Cache-Control: no-store`.
* `GET /s/{token}/a/{asset}` : sert un asset du vault référencé par la note (images), mêmes contrôles sauf incrémentation.

Rendu : frontmatter retiré, `![[x]]` résolu vers l'asset local si le fichier existe (sinon texte brut), `[[y]]` rendu en texte gras sans navigation, chemins d'images relatifs réécrits vers `./a/...`, HTML assaini (scripts, iframes et handlers d'événements supprimés).

## 5. Interface web

Page unique servie à `/`, sans build (HTML et JS inline) :

* Écran clé : saisie de la clé admin, conservée en `sessionStorage` uniquement, envoyée en header `Authorization`.
* Création : champ chemin (avec aide : `inbox/...`, `quick/...`), durée en heures, vues max optionnelles, mot de passe optionnel, bouton copier le lien généré.
* Liste : tableau des liens (note, expiration, vues, cadenas), boutons copier et révoquer.
* Page publique `/s/{token}` : titre, contenu rendu, formulaire mot de passe si requis, page 404/410 neutre sinon.

## 6. Sécurité

Volume monté en lecture seule côté share (aucune écriture possible sur les notes). Tokens indevinables 192 bits. Mots de passe stockés en SHA-256 (le transport est chiffré par le TLS Modal). Pas de distinction 404/410 exploitable. Anti-abus : quotas par défaut courts (24 h), révocation en un clic, aucune liste publique. Secrets jamais dans le code : `SHARE_ADMIN_TOKEN` via secret Modal, URL et token admin via variables d'environnement côté MCP.

## 7. Scale-to-zero et coûts

Fonction serverless par défaut : `min_containers` absent donc zéro, `max_containers` libre, `scaledown_window` de 120 s, `timeout` de 300 s, volume en lecture seule (pas de commit). Au repos : aucun container, aucun coût compute, seul le stockage du Volume et du Dict est facturé. Cold start attendu de quelques secondes (image légère Debian + FastAPI).

## 8. Tests

`tests/test_links.py` : logique pure sans Modal (création, expiration, quotas, mot de passe, confinement des chemins, sanitisation), exécutable par `python tests/test_links.py`. Smoke live `tests/test_live_share.py` (gardé par variables d'environnement `SHARE_URL` et `SHARE_ADMIN_TOKEN`) : crée un lien sur une note de test, lit la page publique (200 + contenu), vérifie le quota puis révoque (404). Critère d'acceptation : tests locaux verts, smoke live vert, scale-to-zero observé (aucun container après 3 minutes sans trafic).

## 9. MCP (v0.2.0 de zennotes-mcp)

Nouveaux outils dans le dépôt existant, via `SHARE_URL` et `SHARE_ADMIN_TOKEN` : `share_note(path, ttl_hours, max_views, password)` rend l'URL, `list_shares()` rend le tableau, `revoke_share(token)` révoque. Aucun secret dans le code du MCP.

## 10. Exploitation

Commandes : `modal deploy share_app.py`, `modal app logs zennotes-share`, rotation de la clé admin par `modal secret create zennotes-share-admin --force` puis redeploy. Sauvegarde : les liens vivent dans le Dict (recréables à tout moment, perte acceptable). Évolutions prévues : plugin suivant sur le même pattern (montage lecture seule du Volume + Dict dédié), webhooks d'expiration, page publique multilingue.
