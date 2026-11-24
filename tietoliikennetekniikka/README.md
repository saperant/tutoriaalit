# Tietoliikennetekniikka

Tiivis suomenkielinen tutoriaali siitä, miten bitit kulkevat:
siirtotiet, kanavan kapasiteetti, linjakoodaus, virheenkorjaus,
multipleksointi, kytkentätavat ja viive, kanavanvaraus, Ethernet,
matkaviestinverkot sekä jonot ja palvelun laatu. Jokainen ilmiö
lasketaan tai simuloidaan Pythonilla ja NumPylla, ja tulosta verrataan
teoriaan. Valmiit dokumentit:
[tietoliikennetekniikka.pdf](https://saperant.github.io/tutoriaalit/materiaalit/tietoliikennetekniikka.pdf)
ja pikaopas
[tietoliikennetekniikka-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/tietoliikennetekniikka-pikaopas.pdf).

## Sisältö

1. Johdanto – mitä tietoliikennetekniikka on, desibelit
2. Siirtotiet – kupari, valokuitu ja radio
3. Kanavan kapasiteetti – Nyquist, Shannon, linkkibudjetti
4. Linjakoodaus ja kehystys – NRZ, Manchester, 4B5B, PAM4, bittitäyttö
5. Virheiden havaitseminen ja korjaus – CRC, Hamming, lomitus
6. Multipleksointi – TDM, FDM, WDM, OFDM, CDMA
7. Kytkentätavat ja viive – piiri- ja pakettikytkentä, viiveen osat,
   kaistan ja viiveen tulo
8. Kanavanvaraus – ALOHA, CSMA/CD, CSMA/CA, Token Ring, TDMA
9. Ethernet – fyysiset kerrokset, kehyksen tehokkuus, vähimmäiskoko,
   automaattinen neuvottelu
10. Matkaviestinverkot – 4G- ja 5G-arkkitehtuuri, numerologia,
    huippunopeus, solut
11. Jonot ja palvelun laatu – M/M/1, Littlen laki, prioriteetit,
    rahakkeen ämpäri, DiffServ
12. Lopuksi – nyrkkisäännöt, jatkotaidot, lähteet

## Rakentaminen

```text
make testaa   # rakenne, ruff, mypy --strict ja esimerkkien ajot
make pdf      # tietoliikennetekniikka.pdf ja pikaopas
```

Esimerkit toimivat Python 3.12:lla ja uudemmilla; ne tarvitsevat
NumPyn. Tarkistukseen tarvitaan ruff ja mypy (kehityskontissa valmiina).

Lisenssi: CC BY-SA 4.0.
