# Reunaehdot

Yhtälöt ovat kaikissa virtauksissa samat. Virtauksen tekee juuri
tietyksi virtaukseksi sen reunat: missä on seinä, mistä neste tulee ja
minne se menee. Reunaehdot ovat myös yleisin syy siihen, että huolella
tehty lasku antaa väärän tuloksen. Tässä luvussa käydään läpi neljä
reunatyyppiä, niiden toteutus porrastetussa hilassa ja kaksi koetta:
kanava, jossa virtaus kehittyy, ja este, jonka avulla mitataan, kuinka
paljon reunan paikka vaikuttaa tulokseen.

## Neljä reunaa

| Reuna | Reunaa vastaan kohtisuora nopeus | Reunan suuntainen nopeus | Paine |
|---|---|---|---|
| tarttuva seinä | 0 | seinän oma nopeus | ei ehtoa: gradientti määräytyy |
| liukuva seinä, symmetriataso | 0 | gradientti 0 | sama |
| sisäänvirtaus | annettu profiili | 0 | sama |
| ulosvirtaus | gradientti 0 | gradientti 0 | annettu, tavallisesti 0 |

**Tarttumisehto** (*no-slip*) on viskoosin nesteen perusominaisuus:
seinän kohdalla neste liikkuu seinän mukana. Siitä syntyvät rajakerrokset,
kitka ja pyörteisyys. **Liukuva seinä** on idealisointi, jolla
kuvataan symmetriatasoa tai kaukana olevaa häiriötöntä rajaa.

Paineelle ei anneta ehtoa niillä reunoilla, joilla nopeus tunnetaan.
Projektio ei koske näihin pintoihin, mikä vastaa ehtoa "painegradientti
reunaa vastaan kohtisuoraan on nolla" potentiaalille $\varphi$.
Ulosvirtausreunalla tilanne on päinvastainen: nopeutta ei tunneta, joten
paineelle annetaan arvo ja nopeus määräytyy laskusta.

Jos alueella ei ole yhtään ulosvirtausreunaa, sisään tulevan
tilavuusvirran on oltava nolla, ja paineen taso jää vapaaksi. Jos
ulosvirtausreuna on, sen paine kiinnittää tason.

## Toteutus haamupisteillä

Porrastetussa hilassa reunaa vastaan kohtisuora nopeus sijaitsee
täsmälleen reunalla, joten sen arvo asetetaan suoraan. Reunan suuntainen
nopeus on puolen ruudun päässä reunasta. Sen ehto toteutetaan
**haamupisteellä** alueen ulkopuolella, kuten vuoreunaehto
differenssimenetelmässä: haamuarvo valitaan niin, että haamun ja
sisimmän arvon keskiarvo reunalla on haluttu.

```{.python tiedosto="esimerkit/07-virta/virta.py" osa="reunat"}
```

Tarttuvalle seinälle haamuarvo on $2U_\text{seinä} - u_\text{sisin}$ ja
liukuvalle sama kuin sisin arvo. Sama peilaus tekee esteen: esteen
sisään jäävät pinnat toimivat viereisten virtaavien pintojen
haamupisteinä.

Mitkä pinnat ovat tuntemattomia, päätetään ratkaisijaa luotaessa. **Avoin
pinta** on sellainen, jonka nopeuden paine korjaa: kahden nesteruudun
välinen sisäpinta tai ulosvirtausreunan pinta. Paineyhtälön matriisi
kootaan vain avoimista pinnoista.

```{.python tiedosto="esimerkit/07-virta/virta.py" osa="pinnat"}
```

```{.python tiedosto="esimerkit/07-virta/virta.py" osa="painematriisi"}
```

Ulosvirtausreunalla paine on nolla reunapinnalla, joka on puolen ruudun
päässä viimeisestä painepisteestä. Se lisää matriisin lävistäjälle
termin ja tekee matriisista säännöllisen.

## Kanavavirtaus kehittyy

Ensimmäinen koe on kanava, johon neste tulee vasemmalta tasaisella
nopeudella. Seinillä nopeus on nolla, joten profiilin on muututtava.
Kaukana sisääntulosta sen pitää olla luvun 2 paraabeli, jonka huippu on
1,5 kertaa keskinopeus ja jonka painegradientti on $-12\nu U/H^2$.

```{.python tiedosto="esimerkit/08-kanava.py" osa="tehtava"}
```

```{.python tiedosto="esimerkit/08-kanava.py" osa="tarkistukset"}
```

```{.tuloste tiedosto="esimerkit/08-kanava.odotettu" rivit="1-5"}
```

![Ylhäällä vaakanopeus ja virtaviivat kanavan alkuosassa. Alhaalla
vasemmalla nopeusprofiili neljässä kohdassa, oikealla keskilinjan
nopeus kolmella Reynoldsin luvulla.](kuvat/kanava.png){width=95%}

Tarkistuksia on kolme, ja ne mittaavat eri asioita.

- **Tilavuusvirta** on jokaisessa poikkileikkauksessa sama
  pyöristystarkkuudella. Tämä on projektion ansio eikä kerro
  tarkkuudesta mitään, mutta jos se ei toteutuisi, ohjelmassa olisi
  virhe.
- **Profiili** on kehittyneellä osalla paraabeli kolmen tuhannesosan
  tarkkuudella.
- **Painegradientti** poikkeaa teoriasta kolmasosaprosentin.

Seinien viereen syntyy rajakerros, joka paksunee virtaussuuntaan, kunnes
ylä- ja alaseinän kerrokset kohtaavat. Siihen asti keskiosa kiihtyy,
koska seinien lähellä hidastunut neste vie tilaa. Matkaa, jonka jälkeen
profiili ei enää muutu, sanotaan **kehittymispituudeksi**.

```{.python tiedosto="esimerkit/08-kanava.py" osa="kehittyminen"}
```

```{.tuloste tiedosto="esimerkit/08-kanava.odotettu" alkaen="kehittymispituus"}
```

Kehittymispituus kasvaa suorassa suhteessa Reynoldsin lukuun ja on noin
$0{,}05\,\mathrm{Re}\,H$. Tulos on tärkeä mallintajalle: jos
sisäänvirtausreunalle annetaan tasainen profiili, sen jälkeen tarvitaan
tämän verran kanavaa ennen kuin virtaus on se, jota putken tai kanavan
keskellä oikeasti on. Reynoldsin luvulla 1 000 matka olisi viisikymmentä
kanavan korkeutta.

## Kuinka kauas reunat on vietävä

Sisään- ja ulosvirtausreuna ovat keinotekoisia: oikeassa laitteessa
virtaus jatkuu niiden takana. Reunaehto väittää, että virtaus on
reunalla tietynlainen, ja jos väite on väärä, virhe leviää alueeseen.

Koe on neliöeste kanavassa. Reynoldsin luku esteen sivun mukaan on 20,
jolloin virtaus on vakaa ja esteen taakse jää pyörrepari. Sen pituus on
herkkä suure, jota seurataan, kun reunoja siirretään.

```{.python tiedosto="esimerkit/08-reunat.py" osa="tehtava"}
```

```{.tuloste tiedosto="esimerkit/08-reunat.odotettu"}
```

![Vaakanopeus ja virtaviivat esteen ympärillä. Alemmassa kuvassa
ulosvirtausreuna (pisteviiva) on liian lähellä: sen ehto pakottaa
pyörteen venymään.](kuvat/reunat.png){width=95%}

**Sisäänvirtaus.** Tasainen profiili puolen yksikön päässä esteestä
lyhentää pyörrettä yhdeksän prosenttia, koska este joutuu virtaukseen,
jota todellisuudessa ei ole. Kun profiiliksi annetaan valmiiksi
kehittynyt paraabeli, yhden yksikön etumatka riittää prosentin
tarkkuuteen. Oikea profiili on siis arvokkaampi kuin pitkä etumatka.

**Ulosvirtaus.** Ehto "gradientti nolla, paine vakio" on väite, että
virtaus on reunalla yhdensuuntaista ja valmista. Kun reuna on 0,75
yksikköä esteen takana, virhe on alle prosentin. Kun se viedään
pyörteen hännän tuntumaan, pituus muuttuu 17 prosenttia, ja kun se
leikkaa pyörteen, neste virtaa reunasta takaisin sisään eikä tulos
tarkoita enää mitään.

Yleisohje on tehdä sama koe omalle tehtävälle: siirrä reunaa ja katso,
muuttuuko kiinnostava suure. Jos muuttuu, reuna oli liian lähellä.

## Käytännössä

- **Reunaehto on malli ympäristöstä.** Kirjaa, mitä kukin reuna
  väittää: seinä, symmetria, tunnettu sisäänvirtaus, häiriötön
  ulosvirtaus. Suurin osa virtauslaskennan virheistä on tässä listassa.
- **Anna sisäänvirtaukselle oikea profiili** tai riittävästi etumatkaa.
  Turbulentissa virtauksessa myös turbulenssisuureet tarvitsevat
  järkevät arvot sisäänvirtauksessa.
- **Vie ulosvirtausreuna kauas pyörteistä.** Takaisinvirtaus
  ulosvirtausreunalla on varoitus, jonka valmiit ohjelmat tulostavat.
  Sitä ei pidä ohittaa.
- **Käytä symmetriaa vain, jos virtaus on symmetrinen.** Geometrian
  symmetria ei riitä: luvun 10 pyörrerata on epäsymmetrinen virtaus
  symmetrisen esteen takana, ja symmetriataso estäisi sen kokonaan.
- **Tee reunan paikan herkkyyskoe.** Se maksaa yhden lisäajon ja
  vastaa kysymykseen, jota mikään hilan tihentäminen ei paljasta.
- **Porrasreuna on ensimmäistä kertalukua.** Kun vino tai kaareva pinta
  kuvataan kokonaisilla ruuduilla, pinnan paikka on väärin enintään
  puoli ruutua. Tarkat ohjelmat sovittavat hilan pintaan.

## Itsearviointi

- Osaat nimetä neljä reunatyyppiä ja kertoa, mitä kukin määrää
  nopeudelle ja paineelle.
- Osaat toteuttaa tarttuvan ja liukuvan seinän haamupisteellä
  porrastetussa hilassa.
- Osaat selittää, miksi paine annetaan ulosvirtausreunalla mutta ei
  seinällä.
- Osaat arvioida kanavavirtauksen kehittymispituuden ja tiedät, miten
  se vaikuttaa sisäänvirtausreunan paikkaan.
- Osaat tutkia herkkyyskokeella, ovatko sisään- ja ulosvirtausreuna
  riittävän kaukana.
