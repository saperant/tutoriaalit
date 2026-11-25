"""Hypothesiksen asetukset: toistettava ajo ilman esimerkkitietokantaa."""

from hypothesis import settings

# @alku profiili
settings.register_profile(
    "kirja", derandomize=True, database=None, deadline=None,
    max_examples=200, print_blob=False)
settings.load_profile("kirja")
# @loppu profiili
