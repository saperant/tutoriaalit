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
   ja lämpötilalle, piensignaalimalli, emitteriseuraaja, MOSFET
   vahvistimena, differentiaalipari
3. Operaatiovahvistimet – makromalli, vahvistus ja kaistanleveys,
   integraattori, instrumentointivahvistin, todellisen vahvistimen rajat
4. Aktiiviset suodattimet – Sallen-Key ja MFB, symbolinen analyysi
   SymPyllä, Monte Carlo, Butterworth ja Bessel, antialiasointi
5. Takaisinkytkentä ja stabiilisuus – silmukkavahvistus, vaihevara,
   kapasitiivinen kuorma ja kompensointi, vertailija ja hystereesi
6. AD- ja DA-muuntimet – kvantisointi ja SNR, R-2R-tikapuu, PWM ja
   RC-suodin, SAR, näytteenotto ja pito, sigma-delta, referenssi
7. Kohina ja signaalin eheys – terminen kohina, kohinabudjetti,
   heijastukset siirtolinjassa, maadoitus ja ohitus
8. Lopuksi – nyrkkisäännöt, jatkotaidot ja lähteet

Esitiedot: *Elektroniikan perusteet ja SPICE* ja *Differentiaaliyhtälöt
ja Laplace-muunnos*. Laitteita ei tarvita: jokainen piiri simuloidaan,
ja tulokset näytetään piirikaavioiden rinnalla aaltomuotoina ja
taajuusvasteina.

## Rakentaminen

```text
make testaa   # rakenne, ruff, mypy --strict ja esimerkit (vaatii ngspicen)
make pdf      # analogiaelektroniikka.pdf ja pikaopas
make kuvat    # piirtää kuvat/-hakemiston kuvat uudelleen (schemdraw, Matplotlib)
```

Esimerkit ajetaan esimerkkihakemistossa, esimerkiksi
`python3 04-sallen-key.py`. Kehityskontissa
(`.devcontainer/analogiaelektroniikka`) ngspice ja Python-kirjastot ovat
valmiina. Operaatiovahvistimen makromalli on tiedostossa
`esimerkit/operaatiovahvistimet.lib`.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks. [Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

## Lisenssi

Teksti ja esimerkit: Creative Commons Nimeä–JaaSamoin 4.0 (CC BY-SA 4.0).
