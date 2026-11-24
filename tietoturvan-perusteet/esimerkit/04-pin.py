"""Tiiviste ei ole salaus: lyhyt salaisuus löytyy kokeilemalla."""

import hashlib
import time

# Tietokantavuoto paljastaa PIN-koodin SHA-256-tiivisteen.
vuotanut = hashlib.sha256(b"4071").hexdigest()

# @alku haku
alku = time.perf_counter()
for luku in range(10_000):
    ehdokas = f"{luku:04d}".encode()
    if hashlib.sha256(ehdokas).hexdigest() == vuotanut:
        loydetty = ehdokas.decode()
        break
kesto = time.perf_counter() - alku
# @loppu haku

print(f"PIN on {loydetty}")
print("aikaa alle sekunti:", kesto < 1.0)
