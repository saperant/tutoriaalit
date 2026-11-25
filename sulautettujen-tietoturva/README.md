# Sulautettujen järjestelmien tietoturva

Tiivis suomenkielinen tutoriaali sulautettujen laitteiden
tietoturvasta: luottamusketju, versionpalautuksen esto,
mittauskäynnistys, avainten säilytys ja PUF, päivitykset, debug-portit,
sivukanavat, vikahyökkäykset sekä standardit ja EU:n
kyberkestävyyssäädös. Valmiit dokumentit:
[sulautettujen-tietoturva.pdf](https://saperant.github.io/tutoriaalit/materiaalit/sulautettujen-tietoturva.pdf)
ja pikaopas
[sulautettujen-tietoturva-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/sulautettujen-tietoturva-pikaopas.pdf).

Esitiedot: taidot *Mikrokontrollerit ja bare-metal-ohjelmointi* ja
*Kryptografia*.

**Vastuulauseke.** Materiaali on tarkoitettu opetukseen ja omien
laitteiden suojaamiseen. Fyysiset hyökkäykset (sivukanavat, viat,
debug-portit) ajetaan simulaatioina ja QEMU:ssa itse käännetyllä
ohjelmistolla. Mittaa, avaa ja häiritse vain laitteita, jotka omistat
tai joiden testaamiseen sinulla on kirjallinen lupa. Luvaton
tunkeutuminen ja tietojärjestelmän häirintä ovat rikoksia (rikoslain
38. luku). Tekijät eivät vastaa materiaalin väärinkäytöstä.

## Sisältö

1. Johdanto – laboratorio: QEMU, Cortex-M3 ja testiavaimet
2. Laitteen uhkamalli – pääsytasot, koko kannan murto, toimitusketju,
   elinkaari
3. Turvallinen käynnistys – luottamusketju, kuvan muoto, Ed25519
   Monocypherilla, skenaariot QEMU:ssa
4. Versionpalautuksen esto – turvaversio, OTP-laskuri
5. Mittauskäynnistys ja etätodennus – PCR, tapahtumaloki, TPM, DICE
6. Avainten säilytys – turvaelementti, TrustZone, laitekohtaiset
   avaimet, satunnaisuus, PUF ja sumea poimija, laitteen identiteetti
   taustajärjestelmälle
7. Päivitykset – A/B ja kokeilukäynnistys, manifesti, delta
8. Debug-portit – lukitustasot, todennettu debug, sarjakonsoli
9. Sivukanavat – ajoitushyökkäys, korrelaatiotehoanalyysi, maskaus
10. Vikahyökkäykset – vikamallit, kovennettu päätös
11. Standardit ja sääntely – ETSI EN 303 645, EN 18031, IEC 62443, CRA
12. Lopuksi – nyrkkisäännöt, mallit, lähteet

## Esimerkit

- `esimerkit/laite/`: käynnistin ja sovellus Cortex-M3:lle
  (`arm-none-eabi-gcc`, QEMU `mps2-an385`). Viisi skenaariota:
  aito kuva, peukaloitu kuva, versionpalautus, vieras avain ja
  A/B-valinta. Mukana on Monocypher 4.0.2 (BSD-2-Clause tai CC0).
- `esimerkit/*.c`: OTP-laskuri, ajoitushyökkäys ja vikahyökkäyksen
  simulointi isäntäkoneella (GCC ja Clang, sanitoijat).
- `esimerkit/*.py`: kuvatyökalu, mittauskäynnistys, laiteavaimet,
  PUF, päivitysmenetelmät, manifesti, delta, todennettu debug,
  tehoanalyysi ja vaatimusten jäljitys (ruff, mypy --strict,
  `cryptography` 50.0.1).

Kokeiluissa käytetään RFC 8032:n julkisia testiavaimia.

## Rakentaminen

```text
make testaa   # rakenne, esimerkit ja QEMU-skenaariot
make pdf      # tutoriaali ja pikaopas
make kuvat    # piirtää kuvat/-hakemiston kuvaajat (Matplotlib)
```

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

Tarvitaan `gcc-arm-none-eabi`, `libnewlib-arm-none-eabi`,
`qemu-system-arm` ja Pythonin `cryptography`; kehityskontissa
(`.devcontainer/sulautettujen-tietoturva`) ne ovat valmiina.
