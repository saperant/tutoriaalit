# Mallit: Amdahl ja roofline

Ennen kuin optimoi, kannattaa laskea, paljonko voisi enimmillään
voittaa. Kaksi yksinkertaista mallia vastaa siihen. Amdahlin laki
kertoo, mitä koko ohjelma hyötyy yhden osan nopeuttamisesta.
Roofline-malli kertoo, rajoittaako ydintä laskenta vai muistin
kaistanleveys ja kuinka lähellä rajaa ollaan.

## Amdahlin laki

Olkoon $p$ se osuus ajosta, johon muutos vaikuttaa, ja $s$ kerroin,
jolla tämä osa nopeutuu. Muu osa $1 - p$ kestää yhtä kauan kuin ennen,
joten kokonaisnopeutus on

$$S = \frac{1}{(1 - p) + p/s}.$$

```{.c tiedosto="esimerkit/03-amdahl.c" osa="amdahl"}
```

Kun $s$ kasvaa rajatta, $S$ lähestyy arvoa $1/(1 - p)$. Jos puolet
ajasta on nopeutettavissa, mikään optimointi ei tee ohjelmasta yli
kaksi kertaa nopeampaa. Tietokonearkkitehtuurin johdannossa laki
esiteltiin laitteistonäkökulmasta; ohjelmistossa se on vielä
armottomampi, koska profiili jakautuu yleensä moneen osaan.

```{.c tiedosto="esimerkit/03-amdahl.c" osa="taulukko"}
```

```{.tuloste tiedosto="esimerkit/03-amdahl.odotettu"}
```

Taulukosta näkyy kaksi käytännön sääntöä. Ensinnäkin osuus ratkaisee
enemmän kuin kerroin: 99 %:n osan nopeuttaminen neljä kertaa (3,88)
voittaa 50 %:n osan nopeuttamisen äärettömästi (2,00). Toiseksi
kertoimen kasvattamisen hyöty loppuu nopeasti: kun $p = 0{,}9$,
kerroin 16 antaa 6,4 ja kerroin 64 vasta 8,8.

Kaavan voi myös kääntää. Jos tavoite on kaksinkertainen nopeus, kuinka
suuri osuus on nopeutettava?

```{.c tiedosto="esimerkit/03-amdahl.c" osa="tarvittava"}
```

Profiilin suurimman funktion osuus kertoo siis heti, onko tavoite
ylipäätään mahdollinen ilman, että muutetaan rakennetta laajemmin.
Sama laki pätee rinnakkaistamiseen, kun $s$ on ytimien määrä: jos
kymmenesosa työstä on sarjallista, sata ydintä antaa alle
kymmenkertaisen nopeuden. Rinnakkaisohjelmointi on oma taitonsa;
Gustafsonin laki täydentää Amdahlia tilanteessa, jossa ongelman koko
kasvaa ytimien mukana.

## Laskenta vai muisti

Suorittimen ydin pystyy tekemään kymmeniä liukulukuoperaatioita
jaksossa, mutta lataamaan muistista vain muutamia tavuja jaksossa.
Kumpi raja tulee vastaan, riippuu ytimen *laskentaintensiteetistä*:

$$I = \frac{\text{liukulukuoperaatiot}}{\text{muistista siirretyt tavut}}
\quad [\text{FLOP/B}].$$

Esimerkiksi *triad* `a[i] = b[i] + s*c[i]` tekee kaksi operaatiota
(kertolasku ja yhteenlasku) alkiota kohden ja siirtää 32 tavua: kaksi
luettavaa double-lukua (16 B) ja kirjoitettava, jonka rivi luetaan
ensin välimuistiin ja kirjoitetaan sitten takaisin (16 B). Sen
intensiteetti on $2/32 = 0{,}0625$.

## Roofline-malli

Roofline-malli (Williams, Waterman ja Patterson 2009) piirtää
saavutettavan suorituskyvyn intensiteetin funktiona. Katto koostuu
kahdesta suorasta: vinosta muistikatosta $B \cdot I$, jossa $B$ on
kaistanleveys, ja vaakasuorasta laskentakatosta $P$, joka on huipputeho.
Ytimen suorituskyky on enintään näistä pienempi:

```{.c tiedosto="esimerkit/03-roofline.c" osa="malli"}
```

Suorien leikkauskohta $I = P/B$ on *harjanne* (engl. ridge point).
Sen vasemmalla puolella oleva ydin on muistirajoitteinen: laskennan
nopeuttaminen ei auta, vain muistiliikenteen vähentäminen. Oikealla
puolella oleva ydin on laskentarajoitteinen: on käytettävä
vektorikäskyjä, useampia ytimiä tai vähemmän operaatioita.

```{.c tiedosto="esimerkit/03-roofline.c" osa="ytimet"}
```

```{.tuloste tiedosto="esimerkit/03-roofline.odotettu"}
```

Esimerkkikoneen (100 GFLOP/s, 20 GB/s) harjanne on 5 FLOP/B. Kaikki
yksinkertaiset vektorioperaatiot ovat kaukana sen vasemmalla puolella:
triad saavuttaa enintään 1,25 GFLOP/s eli prosentin huipusta, vaikka
koodi olisi täydellistä. Matriisitulo on ainoa laskentarajoitteinen,
koska se tekee $2n^3$ operaatiota $3n^2$ luvulle, mutta vain jos
toteutus todella käyttää jokaista ladattua lukua monta kertaa ennen
kuin se poistuu välimuistista. Siihen palataan luvussa 6.

## Oman koneen katto

Mallin luvut voi mitata. Kaistanleveyden mittaa triad suurilla
taulukoilla, jotka eivät mahdu välimuisteihin:

```{.c tiedosto="esimerkit/03-roofline.c" osa="triad"}
```

Laskentahuipun mittaa silmukka, jossa on kahdeksan riippumatonta
kertolasku–yhteenlaskuketjua rekistereissä, jotta liukuhihna pysyy
täynnä. Kirjoittajan koneella tulos oli tämä:

```{.tuloste tiedosto="esimerkit/tulokset/03-roofline.txt"}
```

Yhden ytimen skalaarikoodin huippu on muutama GFLOP/s, ja harjanne
on tässä alle 1 FLOP/B: skalaarikoodilla polynomikin on
laskentarajoitteinen. Sama ydin pystyy kuitenkin AVX-512-käskyillä
parhaimmillaan 32 double-operaatioon jaksossa (kaksi kahdeksan luvun
yhdistettyä kertolasku–yhteenlaskukäskyä eli FMA:ta), eli yli
20-kertaiseen tehoon. Kun koodi
vektoroidaan (luku 8), laskentakatto nousee ja moni ydin siirtyy
muistirajoitteiseksi. Siksi muistin käytön optimointi (luvut 5 ja 6)
ja vektorointi kulkevat käsi kädessä.

Roofline-mallissa on myös välikattoja: L1-, L2- ja L3-välimuistin
kaistat ovat moninkertaisia DRAMiin verrattuna, ja ilman vektoreita
tai FMA-käskyjä laskentakatto on matalampi. Intelin Advisor ja
LIKWID-työkalut piirtävät mallin mitatuista laskureista.

## Käytännössä

- **Laske Amdahlilla ennen kuin optimoit.** Jos kohde vie 20 %
  ajasta, se voi nopeuttaa koko ohjelmaa enintään 25 %.
- **Optimoi profiilin suurinta osaa**, ja laske uusi profiili jokaisen
  muutoksen jälkeen: osuudet muuttuvat.
- **Selvitä, onko ydin muisti- vai laskentarajoitteinen.** Muistin
  rajoittamaa ydintä ei nopeuta laskennan hiominen, eikä
  laskentarajoitteista välimuistin optimointi.
- **Intensiteettiä kasvatetaan uudelleenkäytöllä**: yhdistä
  peräkkäiset silmukat samalle datalle (silmukkafuusio) ja lohko
  laskenta välimuistiin mahtuviin paloihin.
- **Vertaa mitattua suorituskykyä kattoon.** Jos ydin saavuttaa 80 %
  katosta, lisäoptimointi on kallista; jos 5 %, jotain on vialla.

## Itsearviointi

- Osaat laskea Amdahlin lailla kokonaisnopeutuksen ja ratkaista,
  kuinka suuri osuus on nopeutettava tavoitteen saavuttamiseksi.
- Osaat laskea ytimen laskentaintensiteetin ottaen huomioon
  kirjoitusten rivinvarauksen.
- Osaat piirtää roofline-mallin ja päätellä, kumpi katto rajoittaa
  annettua ydintä.
- Osaat mitata koneen kaistanleveyden ja laskentahuipun
  suuntaa-antavasti.
