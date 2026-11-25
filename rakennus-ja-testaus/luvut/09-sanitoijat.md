# Sanitoijat

Testi näkee vain sen, minkä ohjelma tulostaa tai palauttaa. C-ohjelman
pahimmat virheet eivät näy kummassakaan: puskurin ylivuoto voi
kirjoittaa naapurimuuttujaan ilman näkyvää seurausta, ja
määrittelemätön käytös voi tuottaa testikoneella oikean tuloksen ja
asiakkaalla väärän. *Sanitoija* lisää käännöksessä ohjelmaan
tarkistuksia, jotka huomaavat virheen sillä hetkellä, kun se tapahtuu,
ja kertovat tarkasti missä.

| Sanitoija | Valitsin | Havaitsee | Hidastus |
|-----------|----------|-----------|----------|
| AddressSanitizer (ASan) | `-fsanitize=address` | rajojen ylitykset, vapautetun muistin käytön, vuodot | noin 2× |
| UndefinedBehaviorSanitizer (UBSan) | `-fsanitize=undefined` | ylivuodot, virheelliset siirrot, kohdistusvirheet | vähäinen |
| ThreadSanitizer (TSan) | `-fsanitize=thread` | kilpatilanteet | 5–15× |
| MemorySanitizer (MSan) | `-fsanitize=memory` | alustamattoman muistin käytön (vain Clang) | noin 3× |

ASan ja UBSan voi yhdistää samaan käännökseen, ja se on tavallinen
kehitysversio (kuten luvun 6 esiasetus `kehitys`). TSan ja MSan
tarvitsevat kumpikin oman käännöksensä. Sanitoijat ovat testityökaluja,
eikä niillä käännettyä ohjelmaa toimiteta tuotantoon: ne kasvattavat
muistinkäyttöä ja niiden ajonaikainen kirjasto ei ole suunniteltu
hyökkäyksiä vastaan.

Valgrindin Memcheck löytää osin samat muistivirheet ilman
uudelleenkäännöstä, koska se ajaa valmista ohjelmaa emuloidulla
suorittimella. Se on noin 20–50 kertaa hidastava, mutta hyödyllinen,
kun ohjelmaa tai sen kirjastoja ei voi kääntää sanitoijilla.

## AddressSanitizer

Tavallinen ohi yhdellä -virhe kirjoittaa yhden alkion liikaa:

```{.c tiedosto="esimerkit/09-sanitoijat/ylivuoto.c"}
```

Ilman sanitoijaa tällainen ohjelma voi toimia, kaatua tai rikkoa
muistinvaraajan tietorakenteet niin, että kaatuminen tapahtuu vasta
paljon myöhemmin aivan muualla. ASan ympäröi jokaisen varauksen
myrkytetyllä alueella (*redzone*) ja tarkistaa jokaisen muistiviittauksen
ennen sen tekemistä:

```{.bash tiedosto="esimerkit/09-sanitoijat/aja.sh" osa="asan"}
```

Raportti kertoo virheen lajin (`heap-buffer-overflow`), kirjoituksen
koon (8 tavua, yksi `double`), kutsupinon virheen hetkellä ja sen, mihin
varaukseen osoite liittyy: 0 tavua 40-tavuisen alueen jälkeen, eli
heti viidennen alkion perään. Myös varauksen kutsupino näytetään, mikä
on usein tärkein tieto, koska virheellinen koko on laskettu varauksen
kohdalla. Esimerkki näyttää raportista vain olennaiset rivit;
alkuperäisessä on lisäksi osoitteet, prosessinumero, kirjastojen polut
ja muistikartta. Ne poistava suodatin on tavallinen `sed`-komento:

```{.bash tiedosto="esimerkit/09-sanitoijat/aja.sh" osa="siisti"}
```

ASan havaitsee myös muistivuodot ohjelman lopussa (LeakSanitizer).
Valitsin `-fno-omit-frame-pointer` parantaa kutsupinojen laatua, ja
debug-tieto (`-g`) tuo pinoon tiedostot ja rivit.

## UndefinedBehaviorSanitizer

Etumerkillisen kokonaisluvun ylivuoto on C:ssä määrittelemätöntä
käytöstä. Tavallisesti tulos kiertyy, mutta kääntäjä saa olettaa,
ettei ylivuotoa tapahdu, ja optimoida sen mukaan. Esimerkin laskelma
ylittää `int`-tyypin rajan:

```{.c tiedosto="esimerkit/09-sanitoijat/summa.c"}
```

```{.bash tiedosto="esimerkit/09-sanitoijat/aja.sh" osa="ubsan"}
```

Ilman sanitoijaa ohjelma tulostaa negatiivisen keston eikä mikään
varoita. UBSan pysäyttää ohjelman kohdassa, jossa ylivuoto tapahtui, ja
kertoo arvot. Oletuksena UBSan tulostaa virheen ja jatkaa. Valitsin
`-fno-sanitize-recover=all` pysäyttää ohjelman ensimmäiseen virheeseen,
jolloin testi epäonnistuu eikä virhe huku lokiin. Testeissä tämä on
oikea asetus.

## ThreadSanitizer

Kilpatilanne syntyy, kun kaksi säiettä käyttää samaa muistia ilman
synkronointia ja ainakin toinen kirjoittaa:

```{.c tiedosto="esimerkit/09-sanitoijat/kilpa.c"}
```

Tulos voi olla oikein tuhat kertaa peräkkäin ja väärin seuraavalla
kerralla, kuormitetulla koneella tai toisella prosessorilla. TSan
seuraa jokaista muistiviittausta ja synkronointitapahtumaa ja
raportoi viittausparit, joiden välillä ei ole *happens before*
-suhdetta. Se ei tarvitse kilpatilanteen todellista toteutumista,
vaan riittää, että molemmat viittaukset tapahtuvat ajon aikana:

```{.bash tiedosto="esimerkit/09-sanitoijat/aja.sh" osa="tsan"}
```

```{.tuloste tiedosto="esimerkit/09-sanitoijat.odotettu"}
```

TSanin raportti näyttää kummankin viittauksen kutsupinon ja
säikeiden luontikohdat. Esimerkki jättää ne pois, koska säikeiden
järjestys vaihtelee ajosta toiseen. Korjaus on `_Atomic long laskuri`
tai lukko. Säikeiden synkronointia käsitellään C-kielen tutoriaalissa.

## Sumutus

Sanitoija löytää virheen vain polulta, jonka testi suorittaa.
*Sumutus* (*fuzzing*) tuottaa polut automaattisesti: sumutin kutsuu
testattavaa funktiota yhä uusilla syötteillä, mittaa kattavuuden ja
säilyttää ne syötteet, jotka veivät suorituksen uuteen haaraan.
Sanitoija toimii oraakkelina, joka kertoo, milloin syöte rikkoi jotain.
Kohteeksi sopii jokainen funktio, joka jäsentää ohjelman ulkopuolelta
tulevaa dataa. Seuraavassa jäsentimessä on virhe, jota tavalliset
testit `"lampo=22"` ja `"=5"` eivät löydä:

```{.c tiedosto="esimerkit/09-sanitoijat/sumutus.c" osa="jasennin"}
```

Clangin libFuzzerille kirjoitetaan *sumutuskohde*, joka välittää
syötteen testattavalle funktiolle. Valitsin `-fsanitize=fuzzer` linkittää
mukaan sumuttimen ja sen `main`-funktion:

```{.c tiedosto="esimerkit/09-sanitoijat/sumutus.c" osa="kohde"}
```

```{.bash tiedosto="esimerkit/09-sanitoijat/aja.sh" osa="sumutus"}
```

Edellä näytetyn tulosteen viimeinen osa näyttää tuloksen: sumutin löytää
muutamassa tuhannessa kokeilussa syötteen, jossa yhtäsuuruusmerkin
jälkeen on yli seitsemän numeroa, ja ASan pysäyttää ohjelman pinon
ylivuotoon. Syöte tallentuu tiedostoon `crash-<tiiviste>`. Kun tiedosto
annetaan ohjelmalle argumenttina, virhe toistuu ilman sumutusta, joten
löydöksestä saa suoraan regressiotestin. Korjauksen jälkeen tiedosto
lisätään testisyötteiden joukkoon (*corpus*).

CI:ssä sumutusta ajetaan kahdella tavalla: jokaisessa muutoksessa
lyhyt ajo tallennetulla syötejoukolla (`-runs=0` ajaa vain ne) ja
ajastettuna pidempi etsintä. Löydösten vakavuuden arviointia ja
tyypillisiä muistivirheluokkia käsittelee taito *Haavoittuvuuksien
analyysi ja torjunta*.

## Sanitoijat CI:ssä

Sanitoijien hyöty syntyy siitä, että ne ajetaan jatkuvasti. Tavallinen
järjestely on:

- kehitysversio ja jokainen CI-ajo ASanilla ja UBSanilla,
- erillinen CI-työ TSanilla, jos projektissa on säikeitä,
- `-fno-sanitize-recover=all` ja `halt_on_error`, jotta virhe
  kaataa testin,
- sumutestaus (*fuzzing*, esimerkiksi libFuzzer: `-fsanitize=fuzzer`)
  sanitoijien kanssa, jolloin satunnaiset syötteet tuottavat
  havaittavia virheitä eivätkä vain hiljaista muistin korruptiota.

Sanitoijien asetukset annetaan ympäristömuuttujilla `ASAN_OPTIONS`,
`UBSAN_OPTIONS` ja `TSAN_OPTIONS`. Hyödyllisiä arvoja ovat
`detect_leaks=1`, `halt_on_error=1`, `print_stacktrace=1` ja
`suppressions=tiedosto`, jolla ohitetaan tunnetut virheet kolmannen
osapuolen kirjastoissa. Ohitukset kuuluvat versionhallintaan
perusteluineen, ja niitä on oltava mahdollisimman vähän.

## Käytännössä

- **ASan ja UBSan kehityksen oletukseksi.** Hidastus on pieni
  verrattuna hyötyyn: virhe löytyy rivin tarkkuudella heti, kun testi
  ajetaan.
- **TSan omaksi työkseen.** Se ei toimi yhdessä ASanin kanssa, ja se
  hidastaa enemmän. Säikeitä käyttävä koodi ilman TSania on
  testaamatonta.
- **Virhe kaataa testin.** `-fno-sanitize-recover=all` ja
  `halt_on_error=1`. Varoitus lokissa ei pysäytä yhdistämistä.
- **Sanitoija löytää vain ajetun koodin virheet.** Kattavat testit
  ovat sanitoijan edellytys. Seuraava luku mittaa, kuinka paljon
  koodista testit ajavat.
- **Sumuta jokainen jäsennin.** Funktio, joka lukee tiedostoa,
  verkkoa tai käyttäjän syötettä, saa sumutuskohteen. Löydösten syötteet
  säilytetään versionhallinnassa regressiotesteinä.
- **Ei tuotantoon.** Sanitoijalla käännetty ohjelma on testiversio.
  Tuotannossa käytetään kovennusvalitsimia (`-D_FORTIFY_SOURCE=3`,
  `-fstack-protector-strong`), joita käsitellään taidossa *Tietoturva
  kehitystyössä*.

## Itsearviointi

- Osaat valita sanitoijan virhetyypin mukaan ja kertoa, mitkä niistä
  voi yhdistää samaan käännökseen.
- Osaat lukea ASanin raportista virheen lajin, kohdan ja siihen
  liittyvän varauksen.
- Osaat asettaa UBSanin pysäyttämään ohjelman ensimmäiseen virheeseen
  ja perustella, miksi testeissä niin tehdään.
- Osaat kirjoittaa jäsentimelle sumutuskohteen ja toistaa löydöksen
  tallennetulla syötteellä.
- Osaat selittää, miksi TSan löytää kilpatilanteen, vaikka tulos olisi
  oikein, ja miten sanitoijat järjestetään CI:hin.
