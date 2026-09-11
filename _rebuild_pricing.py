#!/usr/bin/env python3
"""Rebuild pricing/index.html from gen_preise() with EN URL/slug mapping."""
from __future__ import annotations

import _gen_pages as g
from _i18n import DE_SITE_URL, EN_SITE_URL

_INT_SLUGS = {
    "gruendung-deutschland": "founding-germany",
    "leben-arbeiten-deutschland": "living-working-germany",
    "business-turnaround": "business-turnaround",
    "expansion-tochtergesellschaft": "expansion-subsidiary",
}


def _to_en(html: str) -> str:
    html = html.replace("/preise/", "/pricing/")
    html = html.replace('href="../preise/', 'href="../pricing/')
    html = html.replace("../internationale-angebote/", "../international-services/")
    for de_slug, en_slug in _INT_SLUGS.items():
        html = html.replace(de_slug, en_slug)
    html = html.replace("Zur Angebotsseite mit allen Details →", "View offer page for details →")
    # Schema/canonical → EN; hreflang de + x-default stay on beraterium.de
    html = html.replace(DE_SITE_URL, EN_SITE_URL)
    html = html.replace(
        f'hreflang="de" href="{EN_SITE_URL}/pricing/"',
        f'hreflang="de" href="{DE_SITE_URL}/preise/"',
    )
    html = html.replace(
        f'hreflang="x-default" href="{EN_SITE_URL}/pricing/"',
        f'hreflang="x-default" href="{DE_SITE_URL}/preise/"',
    )
    return html


def main() -> None:
    orig_write = g.write

    def write(path: str, html: str) -> None:
        if path == "preise/index.html":
            orig_write("pricing/index.html", _to_en(html))
            return
        orig_write(path, html)

    g.write = write
    g.gen_preise()
    print("EN pricing/index.html rebuilt")


if __name__ == "__main__":
    main()
