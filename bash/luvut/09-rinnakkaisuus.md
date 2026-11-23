# Putket, prosessit ja rinnakkaiset työt {.runko-rinnakkaisuus}

Bashin rinnakkaisuus on prosessien rinnakkaisuutta. Säikeitä ja jaettua
muistia ei ole: jokainen putken osa, taustatyö ja alikuori on oma
prosessinsa, ja ne viestivät putkien, tiedostojen, paluuarvojen ja
signaalien kautta. Tämä tekee rinnakkaisuudesta turvallista, mutta
tulokset on kerättävä erikseen. Yleiset käsitteet, kuten kilpatilanteet
ja lukitus, käsitellään taitopuun taidossa *Rinnakkaisohjelmointi*.

## Prosessit ja alikuoret

| Rakenne | Prosessi | Muuttujat näkyvät kutsujalle |
|---------|----------|------------------------------|
| `{ komennot; }` | sama kuori | kyllä |
| `( komennot )` | alikuori | ei |
| `$(komento)` | alikuori | ei, vain tuloste |
| `a` \| `b` | kumpikin osa alikuoressa | ei |
| `komento &` | taustalla oleva alikuori | ei, vain paluuarvo `wait`:lla |
| `<(komento)` | alikuori, tuloste tiedostona | ei |

Alikuori perii muuttujien kopiot, funktiot ja avoimet tiedostot, mutta
muutokset eivät palaa. Tätä voi käyttää hyväksi: `( cd hakemisto &&
make )` vaihtaa hakemistoa vain alikuoressa. Vain ympäristöön viedyt
(`export`) muuttujat ja `export -f`:llä viedyt funktiot näkyvät ulkoisille
ohjelmille, kuten `bash -c`:lle.

## Taustatyöt ja wait

`komento &` käynnistää komennon taustalle ja jatkaa heti. `$!` on
taustatyön prosessitunnus. `wait pid` odottaa työn päättymistä ja
palauttaa sen paluuarvon, ja pelkkä `wait` odottaa kaikkia.

Rinnakkaisuutta on rajoitettava: sata yhtäaikaista yhteyttä samaan
palvelimeen on palvelunestohyökkäys. Esimerkki tarkistaa palvelimet niin,
että enintään kolme tarkistusta on käynnissä kerrallaan. Varsinainen työ
on simuloitu:

```{.bash tiedosto="esimerkit/09-rinnakkain.sh" osa="tyo"}
```

`wait -n` (4.3) odottaa minkä tahansa taustatyön päättymistä, ja `-p`
(5.1) kertoo, minkä. Assosiatiivinen taulukko yhdistää prosessitunnuksen
palvelimeen, jotta epäonnistuneet voidaan raportoida:

```{.bash tiedosto="esimerkit/09-rinnakkain.sh" osa="ajo"}
```

```{.bash tiedosto="esimerkit/09-rinnakkain.sh" osa="raportti"}
```

```{.tuloste tiedosto="esimerkit/09-rinnakkain.odotettu"}
```

`wait -n || tila=$?` on tarpeen tiukassa tilassa: ilman sitä epäonnistunut
taustatyö lopettaisi koko skriptin `set -e`:n takia.

Taustatöiden tulosteet sekoittuvat, jos ne kirjoittavat samaan
vakiotulosteeseen. Tavallinen ratkaisu on, että jokainen työ kirjoittaa
omaan tiedostoonsa (`> "$tyohak/$nimi.log"`), ja tulokset yhdistetään
lopuksi.

## xargs -P

Kun sama komento ajetaan monelle syötteelle, `xargs -P` hoitaa
rinnakkaisuuden rajoituksen itse. `find -print0 | xargs -0` käsittelee
mielivaltaiset tiedostonimet. Esimerkki pakkaa lokit neljällä
rinnakkaisella `gzip`-prosessilla:

```{.bash tiedosto="esimerkit/09-xargs.sh" osa="xargs"}
```

Oman funktion ajaminen `xargs`:llä vaatii, että funktio viedään
ympäristöön `export -f`:llä ja ajetaan `bash -c`:llä. Argumentti
välitetään `bash -c`:n positioparametrina eikä liitetä komentotekstiin,
jolloin tiedostonimen erikoismerkit eivät voi muuttua koodiksi:

```{.bash tiedosto="esimerkit/09-xargs.sh" osa="funktio"}
```

```{.tuloste tiedosto="esimerkit/09-xargs.odotettu"}
```

Valitsimella `-n 1` jokainen komento saa yhden tiedoston. GNU Parallel
(`parallel`) on monipuolisempi vaihtoehto, mutta sitä ei ole
oletusasennuksissa.

## Lukitus: flock

Kun cron käynnistää skriptin viiden minuutin välein ja ajo kestää
joskus kymmenen minuuttia, kaksi ajoa voi olla käynnissä yhtä aikaa.
`flock` (util-linux) ottaa tiedostoon lukon, jota toinen prosessi ei saa
ennen kuin ensimmäinen vapauttaa sen. Lukko vapautuu automaattisesti,
kun tiedostokuvaaja suljetaan tai prosessi päättyy, myös kaatuessa.

```{.bash tiedosto="esimerkit/09-lukko.sh" osa="lukko"}
```

Esimerkki käynnistää ensimmäisen ajon prosessikorvauksella ja lukee sen
ensimmäisen rivin. Kun rivi on luettu, lukko on varmasti ensimmäisellä
ajolla, joten toinen ajo hylätään joka kerta:

```{.bash tiedosto="esimerkit/09-lukko.sh" osa="kokeilu"}
```

```{.tuloste tiedosto="esimerkit/09-lukko.odotettu"}
```

`flock -n` epäonnistuu heti, jos lukko on varattu; ilman `-n`:ää se
odottaa. Lukkotiedostoa ei poisteta siivouksessa: poisto lukon ollessa
voimassa sallisi kolmannen ajon luoda uuden tiedoston ja oman lukon.
PID-tiedostot (`echo $$ > ajo.pid`) eivät ole luotettava korvike, koska
kaatunut ajo jättää tiedoston jälkeensä.

## Signaalit ja aikakatkaisu

Pitkäkestoinen skripti, kuten jonon käsittelijä, lopettaa hallitusti,
kun se saa TERM-signaalin (esim. `systemctl stop` tai konttia
pysäytettäessä): kesken oleva työ viedään loppuun ennen lopettamista.

```{.bash tiedosto="esimerkit/09-signaalit.sh" osa="ansa"}
```

```{.bash tiedosto="esimerkit/09-signaalit.sh" osa="lahetys"}
```

Bash käsittelee signaalin vasta, kun käynnissä oleva ulkoinen komento,
tässä `sleep`, on päättynyt. Pitkä `sleep` tai verkkokomento viivästyttää
siksi lopettamista. Konttien käynnistysskriptissä tämä on tavallinen
ongelma: skriptin on joko käsiteltävä signaalit tai korvattava itsensä
palvelulla komennolla `exec palvelu`, jolloin signaalit menevät suoraan
palvelulle.

`timeout` (coreutils) rajoittaa komennon keston ja palauttaa arvon 124,
kun aika loppui:

```{.bash tiedosto="esimerkit/09-signaalit.sh" osa="timeout"}
```

```{.tuloste tiedosto="esimerkit/09-signaalit.odotettu"}
```

## Käytännössä

- **Rajoita rinnakkaisuutta.** `wait -n` ja laskuri tai `xargs -P N`;
  ei rajatonta `for … &`-silmukkaa.
- **Kerää jokaisen taustatyön paluuarvo.** `wait` ilman argumentteja
  palauttaa 0, vaikka töitä olisi epäonnistunut.
- **Jokaiselle työlle oma tulostetiedosto**, jos tulosteiden järjestyksellä
  on väliä.
- **`find -print0 | xargs -0`** ja argumentit `bash -c`:n
  positioparametreina, ei merkkijonoon liitettyinä.
- **`flock` päällekkäisten ajojen estämiseen**, ei PID-tiedostoja.
- **`trap` TERM-signaalille** pitkäkestoisissa skripteissä ja `exec`
  konttien käynnistysskriptin viimeisenä komentona.
- **`timeout` jokaiselle verkkokomennolle**, joka voi jäädä odottamaan.
- **Hinta:** prosessin käynnistys maksaa millisekunteja. Rinnakkaisuus
  kannattaa, kun yksittäinen työ kestää selvästi kauemmin, kuten
  pakkaus, lataus tai käännös. Tuhansille lyhyille töille yksi ohjelma,
  joka käsittelee kaikki, on nopeampi.

## Itsearviointi

- Osaat kertoa, mitkä rakenteet käynnistävät alikuoren ja miksi niissä
  tehdyt muuttujamuutokset katoavat.
- Osaat ajaa töitä rinnakkain rajoitetulla määrällä ja raportoida
  epäonnistuneet `wait -n -p`:n avulla.
- Osaat käyttää `xargs -0 -P`:tä oman funktion kanssa turvallisesti.
- Osaat estää skriptin päällekkäiset ajot `flock`:lla.
- Osaat kirjoittaa skriptin, joka lopettaa hallitusti TERM-signaalista,
  ja rajoittaa komennon keston `timeout`:lla.
