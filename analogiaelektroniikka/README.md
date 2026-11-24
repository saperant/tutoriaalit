# Analogiaelektroniikka

Tiivis suomenkielinen tutoriaali analogiaelektroniikan rakennuspalikoista
ohjelmoijalle ja insinööriopiskelijalle: transistorivahvistimet,
operaatiovahvistimet, aktiiviset suodattimet, takaisinkytkennän
stabiilisuus, AD- ja DA-muuntimet sekä kohina ja signaalin eheys.
Jokainen piiri lasketaan mallilla Pythonilla ja simuloidaan avoimella
ngspice-simulaattorilla, ja esimerkit vertaavat tuloksia automaattisesti.
Valmiit dokumentit:
[analogiaelektroniikka.pdf](https://saperant.github.io/tutoriaalit/materiaalit/analogiaelektroniikka.pdf)
ja pikaopas
[analogiaelektroniikka-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/analogiaelektroniikka-pikaopas.pdf).

## Sisältö

1. Johdanto – mittausketju, invertoiva vahvistin ja virtuaalimaa,
   apumoduuli ja mallikirjastot
2. Transistorivahvistimet – toimintapiste, sen herkkyys vahvistukselle
   ja lämpötilalle, piensignaalimalli, emitteriseuraaja
3. Operaatiovahvistimet – makromalli, vahvistus ja kaistanleveys,
   integraattori, instrumentointivahvistin, todellisen vahvistimen rajat
4. Aktiiviset suodattimet – Sallen-Key ja MFB, symbolinen analyysi
   SymPyllä, Monte Carlo, Butterworth ja Bessel, antialiasointi
5. Takaisinkytkentä ja stabiilisuus – silmukkavahvistus, vaihevara,
   kapasitiivinen kuorma ja kompensointi
6. AD- ja DA-muuntimet – kvantisointi ja SNR, SAR, näytteenotto ja
   pito, sigma-delta, R-2R-tikapuu, referenssi
7. Kohina ja signaalin eheys – terminen kohina, kohinabudjetti,
   heijastukset siirtolinjassa, maadoitus ja ohitus
8. Lopuksi – nyrkkisäännöt ja lähteet

Esitiedot: *Elektroniikan perusteet ja SPICE* ja *Differentiaaliyhtälöt
ja Laplace-muunnos*.

## Rakentaminen

```text
make testaa   # rakenne, ruff, mypy --strict ja esimerkit (vaatii ngspicen)
make pdf      # analogiaelektroniikka.pdf ja pikaopas
make kuvat    # piirtää kuvat/-hakemiston kuvat uudelleen (schemdraw)
```

Esimerkit ajetaan esimerkkihakemistossa, esimerkiksi
`python3 04-sallen-key.py`. Kehityskontissa
(`.devcontainer/analogiaelektroniikka`) ngspice ja Python-kirjastot ovat
valmiina. Operaatiovahvistimen makromalli on tiedostossa
`esimerkit/operaatiovahvistimet.lib`.

## Lisenssi

Teksti ja esimerkit: Creative Commons Nimeä–JaaSamoin 4.0 (CC BY-SA 4.0).
