Ohjeet
======

Virheellisten rivien ohittaminen
--------------------------------

Tiedostossa voi olla rivejä, joita ei voi jäsentää. Kerää virheet
erikseen, jotta yksi viallinen rivi ei pysäytä koko käsittelyä:

.. testcode::

   from saa import LukemaVirhe, jasenna_rivi

   rivit = ["kumpula;2026-11-25T12:00:00+02:00;-3.5;81",
            "kumpula;2026-11-25T13:00:00+02:00;99;81"]
   lukemat, virheet = [], []
   for numero, rivi in enumerate(rivit, 1):
       try:
           lukemat.append(jasenna_rivi(rivi))
       except LukemaVirhe as virhe:
           virheet.append(f"rivi {numero}: {virhe}")
   print(len(lukemat), virheet)

.. testoutput::

   1 ['rivi 2: lampotila_c: 99.0 on mittausalueen ulkopuolella']

Lämpötilakäyrän tasoittaminen
-----------------------------

Käytä funktiota :func:`saa.tilasto.liukuva_keskiarvo`. Ikkunan koko
kannattaa valita mittausvälin mukaan: tunnin välein mitatuille arvoille
ikkuna 3 tasoittaa yksittäiset poikkeamat mutta säilyttää vuorokauden
vaihtelun.
