"""Tilastoja tentin arvosanoista listan avulla."""

arvosanat = [3, 5, 0, 4, 2, 5, 1, 0, 3, 4]   # 0 = hylätty

hyvaksytyt = [a for a in arvosanat if a > 0]
print(f"Osallistujia {len(arvosanat)}, hyväksyttyjä {len(hyvaksytyt)}")
print(f"Keskiarvo (hyväksytyt): {sum(hyvaksytyt) / len(hyvaksytyt):.2f}")
print(f"Paras {max(arvosanat)}, heikoin hyväksytty {min(hyvaksytyt)}")

# Jakauma: indeksi on arvosana, alkio on lukumäärä.
jakauma = [0] * 6
for arvosana in arvosanat:
    jakauma[arvosana] += 1
for arvosana in range(5, -1, -1):
    print(f"{arvosana}: {'#' * jakauma[arvosana]}")

print("Järjestyksessä:", sorted(arvosanat, reverse=True))
print("Kolme ensimmäistä:", arvosanat[:3], "viimeinen:", arvosanat[-1])
