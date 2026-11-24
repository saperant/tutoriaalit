# Elektroniikan perusteet ja SPICE

Tiivis suomenkielinen tutoriaali sähköpiirien perusteista ohjelmoijalle
ja insinööriopiskelijalle: jännite, virta, resistanssi ja teho,
piirianalyysi, kondensaattori ja kela, vaihtovirta ja impedanssi,
diodit sekä transistorit kytkiminä. Jokainen piiri lasketaan käsin
Pythonilla ja simuloidaan avoimella ngspice-simulaattorilla, ja
esimerkit vertaavat tuloksia automaattisesti. Valmiit dokumentit:
[elektroniikan-perusteet.pdf](https://saperant.github.io/tutoriaalit/materiaalit/elektroniikan-perusteet.pdf)
ja pikaopas
[elektroniikan-perusteet-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/elektroniikan-perusteet-pikaopas.pdf).

## Sisältö

1. Johdanto – jännitteenjakaja käsin ja ngspicellä, apumoduuli
   `spice.py`
2. Jännite, virta, resistanssi ja teho – Ohmin laki, tehonkesto,
   E-sarjat, toleranssit, mittarin kuormitus
3. Piirianalyysi – Kirchhoffin lait, solmujännitemenetelmä NumPylla,
   Theveninin ja Nortonin vastineet, superpositio
4. Kondensaattori ja kela – RC- ja RL-transientit, I2C-väylän
   nousuaika, kosketinvärähtelyn poisto
5. Vaihtovirta, impedanssi ja taajuusvaste – tehollisarvo,
   kompleksinen impedanssi, RC-alipäästö, resonanssi
6. Diodit – Shockleyn yhtälö ja parametrien sovitus, LEDin etuvastus,
   tasasuuntaaja, zener, suojadiodit
7. Transistorit kytkiminä – BJT ja MOSFET, vapaakäyntidiodi,
   CMOS-invertteri
8. SPICE syvemmin – netlist, analyysit, aliohjelmat ja silmukat,
   Monte Carlo, konvergenssi ja mallien rajat
9. Lopuksi – nyrkkisäännöt ja lähteet

## Rakentaminen

```text
make testaa   # rakenne, ruff, mypy --strict ja esimerkit (vaatii ngspicen)
make pdf      # elektroniikan-perusteet.pdf ja pikaopas
make kuvat    # piirtää kuvat/-hakemiston kuvat uudelleen (schemdraw)
```

Esimerkit ajetaan esimerkkihakemistossa, esimerkiksi
`python3 04-rc.py`. Kehityskontissa (`.devcontainer/elektroniikan-perusteet`)
ngspice ja Python-kirjastot ovat valmiina.

## Lisenssi

Teksti ja esimerkit: Creative Commons Nimeä–JaaSamoin 4.0 (CC BY-SA 4.0).
