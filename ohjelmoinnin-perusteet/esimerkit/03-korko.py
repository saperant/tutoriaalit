"""Kuinka monessa vuodessa säästö kaksinkertaistuu?"""

alkupaaoma = 1000.0
korko = 0.045          # 4,5 % vuodessa
tavoite = 2 * alkupaaoma

saldo = alkupaaoma
vuodet = 0
while saldo < tavoite:
    saldo = saldo * (1 + korko)
    vuodet = vuodet + 1
    if vuodet % 5 == 0:
        print(f"{vuodet:>2} v: {saldo:8.2f} €")

print(f"Tavoite {tavoite:.0f} € saavutetaan {vuodet} vuodessa.")
