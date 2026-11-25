# Sphinxin asetukset sääasemakirjaston dokumentaatiolle.
import sys
from pathlib import Path

# Kirjasto on dokumentaation vieressä, ei asennettuna.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

project = "Sääasema"
release = "1.2.0"
language = "fi"

# @alku laajennukset
extensions = [
    "sphinx.ext.autodoc",    # viitesivut docstringeistä
    "sphinx.ext.napoleon",   # Googlen ja NumPyn docstring-tyylit
    "sphinx.ext.doctest",    # dokumenttien esimerkit ajetaan testeinä
]
# Jokainen viittaus tarkistetaan: tuntematon kohde on varoitus, ja
# varoitukset ovat rakennuksessa virheitä (sphinx-build -W).
nitpicky = True
# Standardikirjaston tyypit eivät ole tässä dokumentaatiossa. Laajennus
# sphinx.ext.intersphinx linkittäisi ne Pythonin dokumentaatioon, mutta
# se hakee kohdeluettelon verkosta jokaisessa rakennuksessa.
nitpick_ignore_regex = [("py:class", r"(datetime|collections)\..*")]
# Docstringien >>>-esimerkit ajaa pytest (--doctest-modules), jossa
# moduulin nimet ovat valmiiksi näkyvissä. Sphinx ajaa vain
# dokumenttisivujen doctest- ja testcode-lohkot.
doctest_test_doctest_blocks = ""
autodoc_member_order = "bysource"
autodoc_typehints = "description"
# @loppu laajennukset

html_theme = "alabaster"
html_last_updated_fmt = None
