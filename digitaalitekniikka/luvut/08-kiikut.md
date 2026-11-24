# Salvat ja kiikut

Muisti syntyy takaisinkytkennästä. Kaksi ristiinkytkettyä porttia
pitää toisiaan tilassa, johon ne on asetettu. Tästä rakennetaan salpa,
salvoista kiikku, ja kiikuista kaikki digitaalinen muisti
rekistereistä tilakoneisiin.

## SR-salpa

SR-salpa on kaksi NOR-porttia, joiden lähdöt on kytketty toistensa
tuloihin. S (set) asettaa lähdön Q ykköseksi, R (reset) nollaa sen.
Kun molemmat ovat nollia, salpa pitää tilansa:

```{.python tiedosto="esimerkit/08-sr-salpa.py" osa="salpa"}
```

```{.python tiedosto="esimerkit/08-sr-salpa.py" osa="koe"}
```

```{.tuloste tiedosto="esimerkit/08-sr-salpa.odotettu"}
```

Asetus ja nollaus näkyvät kahden porttiviiveen jälkeen, ja tila säilyy,
kun S ja R palaavat nollaan. Kielletty syöte S = R = 1 pakottaa
molemmat lähdöt nollaan, mikä rikkoo oletuksen $Qn = \bar{Q}$. Kun
molemmat vapautuvat samaan aikaan (hetki 28), kumpikaan portti ei
voita, ja salpa jää värähtelemään.

Oikeassa piirissä viiveet eivät ole täsmälleen samat, ja värähtely
päättyy lopulta jompaankumpaan tilaan. Kuinka nopeasti ja kumpaan, ei
ole ennustettavissa. Tämä on *metastabiilisuus*: bistabiili piiri on
hetken tasapainopisteessä, kuin pallo mäen huipulla.

Jos asetuspulssi on lyhyempi kuin takaisinkytkennän kierros (tässä
neljä aikayksikköä), salpa ei ehdi lukittua. Sama ilmiö on kiikun
asetusajan (setup) taustalla.

## D-salpa ja D-kiikku

SR-salpaa on hankala käyttää, koska siinä on kielletty syöte. *D-salpa*
tekee siitä datamuistin: kun sallinta (en) on 1, salpa on läpinäkyvä ja
lähtö seuraa syötettä D; kun sallinta on 0, salpa pitää viimeisen
arvon.

```{.systemverilog tiedosto="esimerkit/08-kiikut.sv" osa="salpa"}
```

*D-kiikku* näytteistää syötteen vain kellon nousevalla reunalla. Se
on kaksi D-salpaa peräkkäin vastakkaisilla sallinnoilla
(*master–slave*): ensimmäinen on auki kellon ollessa alhaalla, toinen
ylhäällä, joten data pääsee läpi vain reunalla.

```{.systemverilog tiedosto="esimerkit/08-kiikut.sv" osa="kiikku"}
```

Ero näkyy, kun syöte muuttuu kellon ollessa ylhäällä:

```{.systemverilog tiedosto="esimerkit/08-kiikut.sv" osa="testipenkki"}
```

```{.tuloste tiedosto="esimerkit/08-kiikut.odotettu"}
```

Hetkellä 17 salpa on seurannut D:n nollaan, mutta kiikku pitää
reunalla 10 näytteistämänsä ykkösen. Hetkellä 37 sama toistuu
toisinpäin. Kiikku muuttuu vain reunalla (hetki 30), salpa koko ajan,
kun kello on ylhäällä.

Tämä tekee kiikusta synkronisen suunnittelun perustan. Kun kaikki
kiikut näytteistävät samalla reunalla, logiikalla on koko kellojakso
aikaa laskea seuraava arvo, ja välitilat (luvun 7 piikit) eivät näy.
Salvalla data voisi kulkea monen logiikkatason läpi saman
kellopulssin aikana, mikä tekee ajoituksesta vaikean analysoida.

## Asetus- ja pitoaika

Kiikku näytteistää oikein vain, jos syöte on vakaa hetken ennen
reunaa (*asetusaika*, setup time $t_{su}$) ja hetken sen jälkeen
(*pitoaika*, hold time $t_h$). Lähtö muuttuu viiveellä $t_{cq}$
reunan jälkeen.

| Parametri | Merkitys | Tyypillinen (moderni prosessi) |
|-----------|----------|--------------------------------|
| $t_{su}$ | syötteen vakaus ennen reunaa | 20–50 ps |
| $t_h$ | syötteen vakaus reunan jälkeen | 0–30 ps |
| $t_{cq}$ | viive reunasta lähtöön | 30–80 ps |

Alla oleva kuva näyttää ikkunan aikajanalla. Syötteen on oltava vakaa
koko ikkunan $t_{su} + t_h$ ajan reunan ympärillä, ja uusi arvo näkyy
lähdössä vasta viiveen $t_{cq}$ jälkeen.

```{.ajoituskaavio otsikko="Asetus- ja pitoaika kellon nousevan reunan ympärillä"}
{"signal": [
  {"name": "clk", "wave": "l......h......"},
  {"name": "d", "wave": "x...=......x..", "data": ["vakaa"]},
  {"name": "ikkuna", "wave": "z...2..3...z..", "data": ["t_su", "t_h"]},
  {"name": "q", "wave": "=.........=...", "data": ["vanha", "uusi"]}
], "config": {"hscale": 0.7}}
```

Jos syöte muuttuu ikkunan sisällä, kiikun sisäinen salpa jää
tasapainopisteen lähelle, kuten SR-salpa edellä: lähtö voi olla
hetken välitasolla tai heilahdella ennen kuin se asettuu.

## Metastabiilisuus ja tahdistin

Synkronisen piirin sisällä asetus- ja pitoaika taataan ajoitusanalyysillä
(luku 11). Ulkoinen, toisen kellon tahdissa muuttuva signaali
(painonappi, sarjaportti, toinen kellotusalue) voi kuitenkin muuttua
milloin tahansa, joten metastabiilisuus on väistämätöntä. Sen voi vain
tehdä epätodennäköiseksi antamalla kiikulle aikaa ratketa ennen kuin
sen lähtöä käytetään.

Ratkeamaton tila heikkenee eksponentiaalisesti aikavakiolla $\tau$,
joten keskimääräinen vikaväli on

$$\text{MTBF} = \frac{e^{t_r/\tau}}{T_w\, f_{kello}\, f_{data}}$$

jossa $t_r$ on ratkeamiseen jäävä aika ja $T_w$ metastabiilisuusikkuna.

```{.python tiedosto="esimerkit/08-mtbf.py" osa="parametrit"}
```

```{.python tiedosto="esimerkit/08-mtbf.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/08-mtbf.odotettu"}
```

Eksponentti tekee eron dramaattiseksi. Kun ensimmäisen kiikun lähtö
menee logiikan kautta muualle, vika tulee alle millisekunnissa. Kun
lähtö menee suoraan toiseen kiikkuun, MTBF on tunteja. Kahden kiikun
*tahdistin* antaa lähes kokonaisen lisäjakson, ja vikaväli kasvaa
miljooniin vuosiin. Siksi jokainen asynkroninen syöte kulkee kahden
(nopeissa piireissä kolmen) kiikun ketjun läpi ennen käyttöä.

Alla oleva kuva näyttää tapahtumat. Asynkroninen syöte muuttuu juuri
kellon reunalla, joten ensimmäinen kiikku jää hetkeksi välitilaan
(merkitty tuntemattomana). Se ehtii ratketa ennen seuraavaa reunaa,
jolla toinen kiikku näytteistää jo vakaan arvon. Ratkeamisen suunta on
satunnainen: jos ensimmäinen kiikku olisi ratkennut nollaan, muutos
olisi näkynyt yhtä jaksoa myöhemmin, mutta toinen kiikku ei näe
välitilaa kummassakaan tapauksessa.

```{.ajoituskaavio otsikko="Kahden kiikun tahdistin: välitila ratkeaa ennen kuin sitä käytetään"}
{"signal": [
  {"name": "clk", "wave": "lhlhlhlhlhlh"},
  {"name": "asynk", "wave": "0....1......"},
  {"name": "ff1", "wave": "0....x1....."},
  {"name": "ff2", "wave": "0......1...."}
], "config": {"hscale": 0.8}}
```

Monibittisten arvojen siirto kellotusalueelta toiselle on oma
aiheensa (*RTL-suunnittelu*, kellotusalueiden ylitys).

## Käytännössä

- **Kiikut, ei salpoja.** Synkroninen suunnittelu käyttää reunaherkkiä
  kiikkuja. Salpa RTL-koodissa on yleensä virhe: puutteellinen `if`
  tai `case` kombinatorisessa lohkossa päättelee salvan (*RTL-
  suunnittelu*, luku 4).
- **Jokainen asynkroninen syöte tahdistetaan.** Kaksi kiikkua peräkkäin
  ilman logiikkaa välissä. Toisen kiikun lähtöä saa käyttää.
- **MTBF lasketaan, ei arvata.** Kriittisissä järjestelmissä
  tahdistimen MTBF lasketaan valmistajan parametreilla. Kymmenkertainen
  kellotaajuus tai datanopeus lyhentää vikaväliä kymmenkertaisesti,
  mutta lisäjakso pidentää sitä eksponentiaalisesti.
- **Nollauskin on asynkroninen syöte.** Nollauksen vapautus tahdistetaan
  kelloon, muuten osa kiikuista lähtee liikkeelle jaksoa muita
  aiemmin.

## Itsearviointi

- Osaat selittää, miten kaksi ristiinkytkettyä NOR-porttia muistaa
  tilansa ja mitä kielletty syöte tekee.
- Osaat kertoa D-salvan ja D-kiikun eron ja sen, miksi synkroninen
  suunnittelu käyttää kiikkuja.
- Osaat määritellä asetus- ja pitoajan sekä kiikun viiveen.
- Osaat selittää metastabiilisuuden, laskea tahdistimen MTBF:n ja
  perustella, miksi tahdistimessa on kaksi kiikkua.
