"""Testien yhteiset apuvälineet: konttikuvien nimet ja konttien luonti.

Paketin tuonti vaihtaa Testcontainersin siivoojakontin (Ryuk) kuvan
peilin kuvaksi, ennen kuin yhtään konttia käynnistetään."""

from testcontainers.core.config import testcontainers_config

from testiapu import kuvat

testcontainers_config.ryuk_image = kuvat.RYUK
