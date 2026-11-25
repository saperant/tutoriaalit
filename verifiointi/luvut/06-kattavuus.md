# Kattavuus

Satunnaistestin läpäisy kertoo, että tulostaulu ei löytänyt virheitä.
Se ei kerro, mitä testi teki. Ehkä generaattori ei koskaan täyttänyt
jonoa, tai ehkä se ei koskaan lukenut tyhjästä jonosta. *Kattavuus*
(coverage) mittaa, mitkä tilanteet ajo todella tuotti. Se on
verifioinnin edistymisen tärkein mittari ja valmiuskriteerien ydin
(luku 2).

Kattavuutta on kahta lajia:

| Laji | Mitä mittaa | Kuka määrittelee | Puute |
|------|-------------|------------------|-------|
| koodikattavuus | mitkä RTL:n rivit, haarat ja bitit ajettiin | työkalu automaattisesti | ei tiedä määrittelystä mitään |
| toiminnallinen kattavuus | mitkä määrittelyn tilanteet syntyivät | verifioija käsin | kattaa vain sen, mitä verifioija keksi |

Lajit täydentävät toisiaan. Koodikattavuus löytää RTL:stä kohdat,
joita mikään testi ei käyttänyt, mutta ei huomaa toimintoa, joka
puuttuu koodista kokonaan. Toiminnallinen kattavuus mittaa
määrittelyn tilanteita, mutta vain niitä, jotka joku kirjasi
kattavuusmalliin.

## Koodikattavuus

Simulaattorit mittaavat koodikattavuutta usealla tarkkuudella:

| Mittari | Kohde | Kysymys |
|---------|-------|---------|
| rivi- tai lohkokattavuus | lause tai peräkkäisten lauseiden lohko | ajettiinko? |
| haarakattavuus | `if`/`else`- ja `case`-haarat | valittiinko kumpikin suunta? |
| ehto- ja lausekekattavuus | loogisen lausekkeen osaehdot | vaikuttiko jokainen osaehto tulokseen? |
| bittikattavuus (toggle) | signaalin jokainen bitti | vaihtuiko 0 → 1 ja 1 → 0? |
| tilakonekattavuus | tilat ja tilasiirtymät | käytiinkö jokaisessa? |

Verilator mittaa rivi-, haara- ja bittikattavuuden valitsimella
`--coverage`. Kattavuus kirjoitetaan simulaation lopussa tiedostoon,
mutta valitsimen `--binary` tuottama pääohjelma ei kirjoita sitä.
Siksi esimerkki käyttää omaa pääohjelmaa, joka on muuten samanlainen
mutta tallentaa kattavuuden lopuksi:

```{.cpp tiedosto="esimerkit/06-kattavuus/paa.cpp"}
```

Verilatorin työkalu `verilator_coverage` yhdistää tiedostoja
(`--write`), merkitsee lähdekoodiin kattamattomat rivit
(`--annotate`) ja muuntaa tiedot lcov-muotoon (`--write-info`), josta
saa HTML-raportin. Sen raportti kattaa kuitenkin kaikki käännetyt
tiedostot testipenkki mukaan lukien. Esimerkki käyttää siksi pientä
omaa työkalua, joka lukee tiedostot ja tiivistää kattavuuden yhdelle
lähdetiedostolle. Tiedoston jokainen rivi on yksi kattavuuspiste
avain–arvo-pareina ja osumamäärä:

```{.python tiedosto="esimerkit/tyokalut/koodikattavuus.py" osa="lue"}
```

Johdannon ohjattu testi saa FIFOn rivi- ja haarakattavuuden täyteen:

```{.tuloste tiedosto="esimerkit/odotetut/kattavuus-ohjattu.odotettu"}
```

Bittikattavuus jää alle puoleen, koska testi kirjoitti vain arvot
`8'h10`–`8'h13`, eivätkä datan ylimmät bitit vaihtuneet koskaan. Se on
helppo korjata satunnaisella datalla. Tärkeämpi havainto on
johdannosta: sama ohjattu testi päästi läpi vian
`BUGI_SAMANAIKAINEN`, vaikka jokainen RTL:n rivi ja haara ajettiin.

Syy on haarakattavuuden luonteessa. Määrän päivitys on muotoa `if
(kirjoita && !lue) ... else if (lue && !kirjoita) ...`. Haarakattavuus
kysyy vain, valittiinko kumpikin haara ja niiden ohi menevä polku.
Ohi mentiin tyhjäkäynnillä, joten mittari täyttyi, mutta
yhdistelmää "kirjoitus ja luku samaan aikaan" ei syntynyt koskaan.
Ehtokattavuus olisi kysynyt, vaikuttiko `!lue` koskaan tulokseen, ja
paljastanut aukon. Verilatorin nykyiset versiot mittaavat myös
lausekekattavuutta; kaupallisissa simulaattoreissa se on ollut
vakio-ominaisuus pitkään.

Kun ohjatun testin ja satunnaistestin kattavuus yhdistetään, kaikki
kolme mittaria ovat täynnä:

```{.tuloste tiedosto="esimerkit/odotetut/kattavuus-yhdistetty.odotettu"}
```

Koodikattavuuden täysi lukema on siis välttämätön mutta ei riittävä
ehto. Kattamaton rivi on aina löydös: joko testeistä puuttuu
tilanne, tai rivi on kuollutta koodia. Täysi kattavuus ei kerro
mitään puuttuvista tilanteista.

## Toiminnallinen kattavuus

Toiminnallinen kattavuusmalli kirjoitetaan määrittelystä samaan
aikaan kuin verifiointisuunnitelma. Sen rakennuspalikat ovat:

- **kattavuuspiste** (coverpoint): seurattava arvo, kuten jonon
  täyttöaste;
- **lokerot** (bins): arvon kiinnostavat luokat, kuten tyhjä,
  osittain täysi ja täysi;
- **laittomat lokerot** (illegal bins): arvot, joita ei saa
  koskaan esiintyä; osuma on virhe;
- **ohitettavat lokerot** (ignore bins): arvot, joita ei lasketa,
  koska ne ovat mahdottomia tai yhdentekeviä;
- **ristikattavuus** (cross): kahden pisteen lokeroiden kaikki
  yhdistelmät, kuten "täysi jono ja samanaikainen kirjoitus ja luku".

SystemVerilogissa malli kirjoitetaan `covergroup`-rakenteena:

```text
covergroup fifo_kat @(posedge clk iff !rst);
    tila: coverpoint maara {
        bins tyhja = {0}; bins osittain = {[1:3]}; bins taysi = {4};
        illegal_bins yli = {[5:7]};
    }
    toimi: coverpoint {pop, push};
    risti: cross tila, toimi;
endgroup
```

Verilator 5.020 ei tue `covergroup`-rakennetta lainkaan, joten
esimerkit käyttävät omaa pientä Python-mallia, jonka idea on sama.
Kattavuuspiste kirjaa arvon ensimmäiseen lokeroon, jonka ehto
täyttyy, ja nostaa virheen laittomasta arvosta:

```{.python tiedosto="esimerkit/pythonpenkit/kattavuus.py" osa="piste"}
```

Ristikattavuus kirjaa lokeroparit. Aukko on pari, johon ei osuttu:

```{.python tiedosto="esimerkit/pythonpenkit/kattavuus.py" osa="risti"}
```

FIFOn malli seuraa täyttöastetta, toimenpidettä ja niiden ristiä.
Toimenpide on koodattu luvuksi `push + 2·pop`:

```{.python tiedosto="esimerkit/pythonpenkit/fifo_ymparisto.py" osa="kattavuus"}
```

## Aukot ja niiden sulkeminen

Luvun 4 apufunktio `aja` kirjaa jokaisen jakson havainnon tähän
malliin ja tulostaa kattavuuden testin jälkeen. Ehjän FIFOn ajossa
näkyy kolmen testin kattavuus:

```{.tuloste tiedosto="esimerkit/odotetut/cocotb-fifo.odotettu"}
```

Sama tieto näkyy alla lämpökarttana: jokainen ruutu on yksi ristin
lokero ja luku on osumien määrä. Valkoinen ruutu on aukko.

![Ristikattavuus täyttöaste × toimenpide kolmelle testille. Kuva on
tuotettu samasta ajosta kuin yllä oleva raportti
(`kuvat/piirra.py`).](kuvat/ristikattavuus.png){width=95%}

Ohjattu testi ei koskaan levännyt eikä kirjoittanut ja lukenut yhtä
aikaa. Satunnaistetusta testistä puuttuu kaksi ristin lokeroa:
`tyhja*pop` ja `tyhja*push+pop`. Se on luvun 5 kohtelias generaattori:
koska se ei koskaan lue tyhjästä jonosta, sääntöä "luku tyhjästä
hylätään" ei testattu kertaakaan. Vika `BUGI_TYHJA` jäisi siis
satunnaistestiltä löytymättä, ja kattavuusraportti kertoo sen
etukäteen.

Aukko suljettiin kirjoittamalla kolmas testi `kulmat`, joka painottaa
juuri puuttuvia tilanteita. Sen rakenne on kiinteä, ja satunnaisuus on
vain määrissä ja datassa:

```{.python tiedosto="esimerkit/pythonpenkit/test_fifo.py" osa="kulmat"}
```

`kulmat` ei yksin kata kaikkea, mutta testit yhdessä kattavat ristin
kokonaan. Kun FIFOssa on vika `BUGI_TYHJA`, vain `kulmat` löytää sen:

```{.tuloste tiedosto="esimerkit/odotetut/cocotb-fifo-tyhja.odotettu" alkaen="läpi"}
```

Vian `BUGI_SAMANAIKAINEN` löysi luvussa 5 vain satunnaistettu testi.
Kulmatesti kirjoittaa ja lukee yhtä aikaa vain täyteen tai tyhjään
jonoon, joissa jompikumpi toimenpide hylätään, joten se ei osu
lokeroon `osittain*push+pop`. Kumpikaan testi ei siis korvaa toista.

Viallisen lohkon kattavuusraporttia ei pidä lukea sellaisenaan.
`BUGI_TAYSI` kaataa kaikki kolme testiä, ja raportti näyttää samalla
aukkoja, joita ehjällä lohkolla ei ole:

```{.tuloste tiedosto="esimerkit/odotetut/cocotb-fifo-taysi.odotettu"}
```

Kattavuus kirjataan DUT:n havaitusta tilasta. Viallinen DUT ei koskaan
päässyt neljään sanaan, joten lokerot `taysi*...` jäivät tyhjiksi.
Kattavuus luetaan siksi vain ajoista, jotka läpäisivät tarkistukset.

Tämä on *kattavuusohjatun verifioinnin* (coverage-driven
verification) silmukka:

1. kirjoita kattavuusmalli määrittelystä;
2. aja satunnaistestejä monella siemenellä ja yhdistä kattavuus;
3. tutki aukot;
4. sulje aukko muuttamalla rajoitteita, painoja tai kirjoittamalla
   kohdennettu testi;
5. toista, kunnes malli on täynnä tai jäljellä olevat aukot on
   perusteltu.

Aukon syitä on kolme, ja ne käsitellään eri tavoin:

| Syy | Esimerkki | Toimenpide |
|-----|-----------|------------|
| generaattori ei tuota tilannetta | kohtelias generaattori | muuta rajoitteita tai kirjoita kohdennettu testi |
| tilanne on mahdoton | lukeminen nollauksen aikana, kun ajuri on pysäytetty | ohitettava lokero perusteluineen |
| kattavuusmalli on väärin | väärä raja-arvo lokerossa | korjaa malli |

Mahdottomaksi luokittelu on vaarallisin, koska se sulkee aukon
ilman testiä. Perustelu kirjataan, ja mieluiten mahdottomuus
todistetaan formaalisti (luku 8).

## Kattavuus väitteistä

Kattavuuskohteen voi kirjoittaa myös väitteenä: SystemVerilogin
`cover property` laskee, kuinka monta kertaa ehto toteutui
(luku 7), ja formaalissa tarkistuksessa `cover` pyytää ratkaisijaa
etsimään ajon, jossa ehto toteutuu (luku 8). Väitepohjainen kattavuus
sopii aikajärjestyksiin, kuten "pyyntö, jota seuraa myöntö kolmen
jakson kuluttua", joita kattavuuspisteellä on vaikea ilmaista.

## Käytännössä

- **Toiminnallinen malli määrittelystä, ennen testejä.** Malli, joka
  kirjoitetaan testien jälkeen, kuvaa sitä, mitä testit jo tekevät.
- **Ristit ovat arvokkaimpia.** Yksittäiset pisteet täyttyvät lähes
  itsestään; vikoja on yhdistelmissä. Rajaa ristit kuitenkin tarkasti,
  koska lokeroiden määrä kasvaa tulona.
- **Laittomat lokerot ovat tarkistuksia.** Ne kannattaa käyttää, kun
  sääntö koskee arvoalueita.
- **Koodikattavuus katselmoidaan rivi riviltä.** Lukema ei riitä:
  jokainen kattamaton rivi on joko puuttuva testi, kuollutta koodia
  tai perusteltu poikkeus.
- **Yhdistä kattavuus koko regressiosta.** Yksittäinen testi kattaa
  harvoin kaiken, eikä sen tarvitsekaan. Kaupalliset työkalut
  tallentavat kattavuuden UCIS-tietokantoihin, joita voi yhdistää.
- **Täysi kattavuus ei ole todiste.** Se kertoo, että mallin tilanteet
  syntyivät, ei sitä, että tarkistukset olisivat huomanneet virheen
  niissä. Siksi tarvitaan myös istutetut viat (luku 2).

## Itsearviointi

- Osaat selittää koodikattavuuden ja toiminnallisen kattavuuden eron
  ja sen, miksi tarvitaan molemmat.
- Osaat mitata Verilatorilla rivi-, haara- ja bittikattavuuden ja
  yhdistää usean ajon tulokset.
- Osaat selittää, miksi täysi haarakattavuus voi päästää läpi
  samanaikaisten tapahtumien vian.
- Osaat suunnitella kattavuuspisteen lokeroineen, laittomine
  lokeroineen ja ristikattavuuksineen.
- Osaat analysoida kattavuusaukon syyn ja valita, suljetaanko se
  testillä vai perustellaanko se mahdottomaksi.
