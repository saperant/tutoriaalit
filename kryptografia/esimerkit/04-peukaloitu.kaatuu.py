"""Väärä avain tai muuttunut viesti: purku päättyy poikkeukseen."""

import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

aead = AESGCM(AESGCM.generate_key(bit_length=128))
nonce = os.urandom(12)
salattu = aead.encrypt(nonce, b"tilisiirto 100 EUR", None)
vaara_avain = AESGCM(AESGCM.generate_key(bit_length=128))
vaara_avain.decrypt(nonce, salattu, None)
