"""Deploiement Modal de zennotes-share (scale-to-zero).

    modal deploy share_app.py
"""

import modal

APP_NAME = "zennotes-share"
VOLUME_NAME = "zennotes-data-prod"
DICT_NAME = "zennotes-share-links"
SECRET_NAME = "zennotes-share-admin"

app = modal.App(APP_NAME)

volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)
links = modal.Dict.from_name(DICT_NAME, create_if_missing=True)
admin_secret = modal.Secret.from_name(SECRET_NAME)

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "fastapi",
        "markdown>=3.7",
        "bleach>=6.1",
        "pygments>=2.19,<2.21",
        "pymdown-extensions==11.0.2",
    )
    .add_local_dir("src/zennotes_share", "/pkg/zennotes_share", copy=True)
)


@app.function(
    image=image,
    volumes={"/vol": volume.with_mount_options(read_only=True)},
    secrets=[admin_secret],
    scaledown_window=120,
    timeout=300,
)
@modal.asgi_app()
def api():
    import os
    import sys

    sys.path.insert(0, "/pkg")
    from zennotes_share.app import create_app

    return create_app(links, "/vol/vault", os.environ["SHARE_ADMIN_TOKEN"])
