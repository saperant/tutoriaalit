"""Rahasummat: ei liukulukuja, vaan sentit tai Decimal."""

from decimal import ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal

# @alku raha
hinnat = [0.10] * 3
print(sum(hinnat), sum(hinnat) == 0.30)
print(sum([10] * 3), "senttiä")
print(sum([Decimal("0.10")] * 3))
# @loppu raha
# @alku alv
veroton = Decimal("12.345")
for tapa in (ROUND_HALF_UP, ROUND_HALF_EVEN):
    print(tapa, veroton.quantize(Decimal("0.01"), rounding=tapa))
alv = (Decimal("19.90") * Decimal("0.255")).quantize(Decimal("0.01"))
print("ALV 25,5 %:", alv)
print(round(2.675, 2), Decimal(2.675))
# @loppu alv
