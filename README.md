# zennotes-share

Partage de notes ZenNotes par liens éphémères. Sidecar indépendant en lecture seule, déployé sur Modal en scale-to-zero. Voir `SPEC.md` pour le cahier des charges.

## Install dev

```bash
pip install -e .
python tests/test_links.py
```

## Déploiement

```bash
modal secret create zennotes-share-admin SHARE_ADMIN_TOKEN=<cle-aleatoire>
modal deploy share_app.py
```

URL publique : `https://<workspace>--zennotes-share-api.modal.run`
Page admin : `/` (clé demandée une fois, gardée en session navigateur).

## API

```bash
H="Authorization: Bearer $SHARE_ADMIN_TOKEN"
curl -H "$H" -X POST $SHARE_URL/api/links \
  -d '{"path":"quick/ma-note.md","ttl_hours":24,"max_views":5}'
curl -H "$H" $SHARE_URL/api/links
curl -H "$H" -X DELETE $SHARE_URL/api/links/<token>
```

Lecture publique : `$SHARE_URL/s/<token>` (mot de passe via `?p=`).

## Smoke live

```bash
SHARE_URL=... SHARE_ADMIN_TOKEN=... python tests/test_live_share.py
```

## Coûts

Scale-to-zero : aucun container au repos, extinction ~2 min après le trafic. Seuls le Volume partagé et le Dict de liens sont facturés au stockage.
