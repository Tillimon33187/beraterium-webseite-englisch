"""RA preparation questionnaire — EN locale wrapper around site/_ra_prep.py."""
from __future__ import annotations

import importlib.util
from pathlib import Path

_site_ra_prep = Path(__file__).resolve().parent.parent / "site" / "_ra_prep.py"
_spec = importlib.util.spec_from_file_location("_ra_prep_de", _site_ra_prep)
_mod = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_mod)

selfcheck = _mod.selfcheck


def ra_prep_frontend_config(**kwargs):
    kwargs.setdefault("locale", "en")
    return _mod.ra_prep_frontend_config(**kwargs)


def ra_prep_config_json(**kwargs):
    kwargs.setdefault("locale", "en")
    return _mod.ra_prep_config_json(**kwargs)
