Opas: ensimmäinen yhteenveto
============================

Oppaassa jäsennetään kaksi lukemaa ja lasketaan niistä yhteenveto. Aikaa
kuluu viisi minuuttia, eikä aiempaa kokemusta kirjastosta tarvita.

Lukeman jäsentäminen
--------------------

Asema lähettää lukeman rivinä, jonka kentät erotetaan puolipisteellä.
Funktio :func:`saa.lukema.jasenna_rivi` tekee rivistä
:class:`~saa.lukema.Lukema`-olion:

.. doctest::

   >>> from saa import jasenna_rivi
   >>> lukema = jasenna_rivi("kumpula;2026-11-25T12:00:00+02:00;-3.5;81")
   >>> lukema.asema
   'kumpula'
   >>> lukema.lampotila_c
   -3.5

Yhteenveto
----------

Kun lukemia on useita, :func:`saa.tilasto.yhteenveto` laskee aseman
tunnusluvut:

.. doctest::

   >>> from saa import yhteenveto
   >>> toinen = jasenna_rivi("kumpula;2026-11-25T13:00:00+02:00;-1.5;")
   >>> tulos = yhteenveto("kumpula", [lukema, toinen])
   >>> tulos.maara, tulos.keskiarvo_c
   (2, -2.5)

Seuraavaksi: :doc:`ohjeet` kertoo, miten virheelliset rivit käsitellään.
