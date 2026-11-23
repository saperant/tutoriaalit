"""Tulostus ja muotoilu f-merkkijonoilla."""

from datetime import date
from decimal import Decimal

# @alku muotoilu
hinta = Decimal("1234.5")
osuus = 0.0734
paiva = date(2026, 11, 23)
nimi = "Ada"

print(f"{nimi!r:>8}|{nimi:<8}|{nimi:^8}|")
print(f"{hinta:,.2f} €".replace(",", " "))
print(f"{osuus:.1%} {osuus:.3e}")
print(f"{paiva:%d.%m.%Y} {paiva.isoformat()}")
print(f"{hinta=} {len(nimi)=}")      # = näyttää lausekkeen ja arvon
print(f"{255:#x} {255:08b} {7:03d}")
# @loppu muotoilu
