"""Build a ready-to-list product kit for a script: <slug>.zip plus <slug>.listing.txt.

Stores like Payhip and Gumroad have no way for a script to create products, as far as I know, so the
pipeline hands you finished files (the workflow publishes them as a downloadable artifact) and you
upload them in a couple of minutes.
"""
import pathlib
import zipfile

from common import OUT

LICENSE = """You may use this script for your own and your clients' work.
You may not resell or redistribute the kit itself.
Provided as is, with no warranty. Test on a copy of your data first."""


def build(script, cfg):
    kit_dir = OUT / "kits"
    kit_dir.mkdir(parents=True, exist_ok=True)
    slug = script["slug"]
    py_name = "tool.py"   # the generator is told to refer to the kit script as tool.py
    readme = (f"{script['product_name']}\n{'=' * len(script['product_name'])}\n\n"
              f"{script['kit_readme'].strip()}\n\nLICENSE\n{LICENSE}\n")
    zpath = kit_dir / f"{slug}.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(py_name, script["kit_code"])
        z.writestr("README.txt", readme)
    price = (cfg.get("store") or {}).get("price_usd", 7)
    listing = (f"NAME: {script['product_name']}\nPRICE: ${price}\nFILE: {zpath.name}\n\n"
               f"DESCRIPTION:\n{script['product_blurb']}\n\n"
               f"Includes: {py_name} (robust command-line version), README.txt (setup, how it works, "
               f"adapting it, limitations).\n"
               f"Free core code from the video: see the video description.\n\n"
               f"BEFORE YOU LIST IT: run {py_name} once on sample data and read README.txt. "
               f"The pipeline checks that the code compiles, not that it does what the README says.\n")
    (kit_dir / f"{slug}.listing.txt").write_text(listing)
    return zpath
