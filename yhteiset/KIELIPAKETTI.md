# Kielipaketin rakenne

Tämä dokumentti määrittelee ohjelmointikieltä opettavan tutoriaalipaketin
(*kielipaketin*) rakenteen. Kaikki kielipaketit noudattavat samaa runkoa,
jotta lukija löytää saman asian eri kielistä samasta kohdasta ja jotta
paketit eivät toista toisiaan tai taitopuun muita taitoja. Tarkistin
`yhteiset/tarkista_paketti.py` valvoo rakennetta.

## Kolme tasoa

| Taso | Kenelle | Missä |
|------|---------|-------|
| **Perusteet** | Kieltä opetteleva, myös ohjelmoinnin aloittelija taitopuun esitietojen jälkeen | Paketin ydinluvut |
| **Kokeneelle** | Kehittäjä, joka osaa jonkin toisen kielen ja haluaa siirtyä nopeasti | Luku *Kieli X kokeneelle*, pikaopas ja lukujen itsearvioinnit |
| **Erityistarpeet** | Kehittäjä, jolla on rajattu tarve: kehys, integraatio toiseen kieleen, suorituskyky, tietokannat | Omat taidot taitopuussa (esim. *C++:n suorituskyky*, *Python ja C/C++ yhteen*). Eivät kuulu kielipakettiin. |

## Kielikohtainen ja yleinen sisältö

Kielipaketti opettaa sen, mikä on **kielikohtaista**. Kieliriippumattomat
käsitteet opetetaan kerran taitopuun omassa taidossa, ja kielipaketti
viittaa siihen.

| Aihe | Yleisellä tasolla | Kielipaketissa |
|------|-------------------|----------------|
| Algoritmit | *Algoritmit*, *Tietorakenteet* | Kirjaston valmiit algoritmit ja kokoelmat, niiden takuut ja oikea käyttö |
| Suorituskyky | *Suorituskyvyn analyysi ja optimointi* | Mikä kielessä on kallista ja mikä halpaa: poikkeukset, allokaatiot, kopiot, dynaaminen sidonta, roskienkeruu, globaali tulkkilukko |
| Rinnakkaisuus | *Rinnakkaisohjelmointi* | Kielen säikeet, muistimalli, synkronointi ja asynkronisuus |
| Testaus | *Käännösjärjestelmät, testaus ja CI* | Kielen testikehykset ja -käytännöt |
| Suunnittelumallit | (oma taito tarvittaessa) | Kielen idiomit ja mallit, joita kielen piirteet tukevat tai tekevät tarpeettomiksi |
| Verkko, GUI, tietokannat | Omat taidot | Viittaus |

Esimerkki: poikkeus on Pythonissa halpa ja idiomaattinen tapa ilmaista
tavallisiakin poikkeamia (*EAFP: easier to ask forgiveness than
permission*), mutta C++:ssa poikkeuksen heittäminen on kallista. Siksi C++:ssa
poikkeusta ei käytetä normaalin ohjausvuon osana. Tällainen hintatieto
kuuluu kielipakettiin, koska samat mallit eivät siirry kielestä toiseen.

## Pakolliset luvut

Jokaisen luvun pääotsikkoon merkitään, mitä rungon osaa se edustaa:

```markdown
# Virheenkäsittely {.runko-virheet}
```

| Luokka | Sisältö |
|--------|---------|
| `runko-johdanto` | Historia, käyttökohteet, mihin kieli ei sovellu, standardit ja toteutukset, työkalut, ensimmäinen ohjelma |
| `runko-kokeneelle` | Kielen ajattelutapa, vastaavuudet muihin kieliin, hinnat (mikä on kallista), tärkeimmät sudenkuopat ja lukuohje kokeneelle |
| `runko-tyypit` | Tyypit, lausekkeet, tulostus, muotoilu ja syötteen lukeminen |
| `runko-ohjaus` | Ohjausrakenteet ja funktiot |
| `runko-muisti` | Muistimalli, elinajat ja resurssienhallinta |
| `runko-kokoelmat` | Kokoelmat, merkkijonot ja standardikirjaston ydin algoritmeineen |
| `runko-omat-tyypit` | Rakenteet, luokat, rajapinnat ja geneerisyys |
| `runko-virheet` | Virheenkäsittely |
| `runko-modulit` | Modulit, projektin rakenne, rajapinnat ja riippuvuudet |
| `runko-rinnakkaisuus` | Rinnakkaisuus kielen keinoin |
| `runko-tyokalut` | Käännös, debuggaus, profilointi, testaus ja koodin laatu |
| `runko-kaytannot` | Idiomit, mallit ja nyrkkisäännöt koottuina |
| `runko-lahteet` | Lähteet, dokumentaatio, kirjat ja ulkoiset kirjastot linkkeineen |

Säännöt:

- *Johdanto* on ensimmäinen luku ja *Kokeneelle* toinen.
- *Käytännöt* ja *Lähteet* ovat viimeisissä luvuissa; ne voivat olla
  samassa luvussa.
- Muiden lukujen järjestys noudattaa kielen pedagogiikkaa. Esimerkiksi
  C:ssä osoittimet opetetaan ennen taulukoita.
- Yksi rungon osa voi jakautua usealle luvulle, ja luvulla voi olla useita
  luokkia. Paketissa voi olla myös kielen omia lisälukuja, kuten C++:n
  käännösaikainen laskenta.

Jos jokin rungon osa ei sovellu kieleen (esim. Bashissa ei ole omia
tyyppejä eikä muistimallia), se ilmoitetaan paketin `metadata.yaml`-
tiedostossa, ja kokeneelle-luku kertoo syyn:

```yaml
runko_ei_sovellu: [muisti, omat-tyypit]
```

## Taitopaketit

Tutoriaalit, jotka eivät opeta yleiskäyttöistä ohjelmointikieltä, kuten
RTL-suunnittelu, SQL tai HTML ja CSS, ovat *taitopaketteja*. Niissä on
vapaa lukujako, mutta ensimmäinen luku on johdanto
(`{.runko-johdanto}`), viimeinen sisältää lähteet (`{.runko-lahteet}`),
muut luvut päättyvät osioihin *Käytännössä* ja *Itsearviointi*, ja
paketissa on pikaopas. Paketin Makefile valitsee rakenteen:

```make
NIMI    := sql
KIELI   := sql python        # testaajan kieliprofiilit
RAKENNE := taito             # kieli tai taito
include ../yhteiset/paketti.mk
```

## Luvun rakenne

Jokainen sisältöluku (muut kuin johdanto, kokeneelle, käytännöt ja
lähteet) päättyy kahteen osioon:

1. **`## Käytännössä`** kertoo, miten ammattilaiset luvun asioita
   käyttävät: yleiset mallit ja parhaat käytännöt perusteluineen,
   kielikohtaiset hinnat ja sudenkuopat. Perustelu on tärkeämpi kuin sääntö.
2. **`## Itsearviointi`** luettelee vähintään kolme osaamisväitettä
   muodossa "Osaat …". Kokenut lukija lukee itsearvioinnin ensin ja
   ohittaa luvun, jos hallitsee kaikki väitteet.

## Ei "Hello, World" -materiaalia

Esimerkit opettavat oikeita taitoja:

- Esimerkki ratkaisee tunnistettavan tehtävän, kuten syötteen
  jäsentämisen, resurssin hallinnan tai rajapinnan suunnittelun. Ei
  `foo`- ja `bar`-nimiä.
- Esimerkki on kirjoitettu niin kuin tuotantokoodi: virheet tarkistetaan,
  resurssit vapautetaan, syöte validoidaan ja rajapinnat dokumentoidaan.
  Jos jotain yksinkertaistetaan, se sanotaan.
- Mallit ja käytännöt nimetään (RAII, nollan sääntö, `goto`-siivous,
  läpinäkymätön osoitin, EAFP), jotta lukija tunnistaa ne muualla.
- Väärä tapa näytetään vain, jos se on yleinen virhe, ja silloin
  testattuna `.ei-kaanny`- tai `.kaatuu`-esimerkkinä.

Koodilohkot kirjoitetaan rivin alkuun, ei luettelon kohdan sisään
sisennettyinä: tarkistimet etsivät vain sisentämättömiä lohkoja. Taulukon
solussa olevan koodin pystyviiva näkyy PDF:ssä muodossa `\|`, joten
sellaista koodia ei kirjoiteta taulukkoon.

## Kaaviot ja kuvat

Kuva kertoo usein enemmän kuin kappale tekstiä: ajoituskaavio
kättelystä, tilakone, riippuvuusverkko tai mittaustuloksen kuvaaja.
Kaaviot kirjoitetaan tekstinä koodilohkoihin, ja suodatin `kaaviot.lua`
piirtää ne PDF:ään (ks. `yhteiset/kaaviot.py`):

- **Ajoituskaavio** `{.ajoituskaavio}` kirjoitetaan WaveDromin
  JSON-muodon osajoukolla (kellot `p`/`P`, tasot `0`/`1`, data `=` ja
  `data`-luettelo, `x`, `z`, ryhmät ja katkot).
- **Graphviz-kaavio** `{.dot}` sopii tilakoneisiin, verkkoihin,
  lohkokaavioihin ja riippuvuuksiin.
- `otsikko="…"` tekee kaaviosta numeroidun kuvan kuvatekstein, ja
  `leveys="60%"` rajaa leveyttä. Muuten kaavio ladotaan
  luonnolliseen kokoonsa, joten kaikkien kaavioiden teksti on
  samankokoista.

Kuten koodi, myös kaavion pitää vastata testattua todellisuutta. Kun
kaavio kuvaa simuloitua piiriä, se tuotetaan simulaation VCD-tiedostosta:

```
python3 ../../yhteiset/kaaviot.py vcd sim.vcd --kello clk \
    --signaalit valid,ready,data --alku 2 --jaksot 10 > kattely.json
```

Tiedosto `kattely.json` on versionhallinnassa ja kirjassa näytetään
`{.ajoituskaavio tiedosto="esimerkit/kattely.json"}`. Esimerkkien testi
tuottaa JSONin uudelleen ja vertaa sitä tallennettuun, joten muutos
piirissä paljastuu kaaviossa. Arvo näytetään jaksolla sellaisena kuin se
on kellon nousevan reunan jälkeen.

Mittaus- ja laskentatulosten kuvaajat tehdään Matplotlibilla
skriptillä `kuvat/piirra.py` (`make kuvat`), ja syntyneet PNG-tiedostot
ovat versionhallinnassa.

## Pikaopas

Paketin juuressa on `pikaopas.md`, josta rakennetaan muutaman sivun
vaakasuuntainen kaksipalstainen PDF `<paketti>-pikaopas.pdf`. Se on
kokeneen kehittäjän muistilista: syntaksi tiiviisti, idiomit, hinnat,
sudenkuopat ja työkalukomennot. Pikaoppaan koodi tulee testatuista
esimerkkitiedostoista samoin kuin lukujen koodi.

## Tarkistukset

`make testaa` ajaa kielipaketille esimerkkien testien lisäksi tarkistimen,
joka varmistaa, että

- kaikki pakolliset rungon osat löytyvät ja johdanto, kokeneelle,
  käytännöt ja lähteet ovat oikeilla paikoillaan,
- jokainen sisältöluku päättyy osioihin *Käytännössä* ja *Itsearviointi*
  tässä järjestyksessä,
- itsearvioinnissa on vähintään kolme osaamisväitettä, ja
- pikaopas on olemassa.
