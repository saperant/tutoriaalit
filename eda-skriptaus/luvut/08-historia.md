# Historia ja trendit

Yksittäinen regressio kertoo, mikä on rikki nyt. Historia kertoo,
milloin se meni rikki, onko jokin testi rikki vain joskus ja
paraneeko vai huononeeko tilanne. Näihin kysymyksiin vastataan
tallentamalla jokaisen regression tulokset tietokantaan. SQLite
riittää hyvin: se on yksi tiedosto, se tulee Pythonin mukana, ja
kyselyt ovat tavallista SQL:ää. Useamman koneen CI tallentaa samaan
skeemaan esimerkiksi PostgreSQL-palvelimelle.

## Skeema

```{.python tiedosto="esimerkit/vuo/historia.py" osa="skeema"}
```

Taulu `ajo` on yksi regressioajo. Versio on se commit, jonka koodia
ajettiin, ja järjestys kertoo versioiden paikan historiassa.
Commit-tunnisteista järjestystä ei voi päätellä, joten se tallennetaan
erikseen (esimerkiksi `git rev-list --count HEAD`). Samaa versiota voi
ajaa monta kertaa. Juuri uusinta-ajot paljastavat epävakaat testit.

Taulu `tulos` on yksi testin ja siemenen ajo. Allekirjoitus (luku 7)
tallennetaan tuloksen mukana, joten kyselyt voivat ryhmitellä vikoja
ilman lokeja. Lokit itse säilytetään tiedostoina tai CI:n
artefakteina, eikä niitä kannata kopioida tietokantaan. `kirjaa`
tallentaa koko ajon yhtenä transaktiona (`with yhteys`): kesken
kaatunut kirjaus ei jätä puolikasta ajoa.

## Trendi

```{.python tiedosto="esimerkit/vuo/historia.py" osa="trendi"}
```

Kysely laskee läpäisseet ja kaikki tulokset kustakin versiosta. Jos
versiota on ajettu useasti, mukaan otetaan vain viimeisin ajo.
`SUM(t.tila = 'ok')` laskee tosien vertailujen määrän, koska SQLite
käsittelee totuusarvoa lukuna 1 tai 0.

## Ensimmäinen hylkäävä versio

Kun vika löytyy, ensimmäinen kysymys on, mikä muutos sen toi.
Allekirjoituksittain ryhmitelty ensimmäinen esiintymä vastaa siihen
suoraan:

```{.python tiedosto="esimerkit/vuo/historia.py" osa="ensimmainen"}
```

Ikkunafunktio `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)`
numeroi kunkin allekirjoituksen esiintymät versiojärjestyksessä, ja
ulompi kysely valitsee ensimmäisen. `COUNT(*) OVER (...)` laskee
samassa kyselyssä, montako kertaa allekirjoitus on nähty kaikkiaan.

Jos regressiota ei ajeta jokaiselle commitille, ensimmäinen
hylkäävä versio rajaa vain välin: vika tuli jossain edellisen
läpäisseen ja tämän version välillä. Väli puolitetaan komennolla
`git bisect run`, jolle annetaan skripti. Skripti ajaa hylkäävän
testin hylkäävällä siemenellä ja palauttaa 0, jos testi meni läpi, ja
1, jos ei. Historia kertoo, mikä testi ja siemen bisektiin kannattaa
valita.

## Epävakaat testit

Epävakaa (*flaky*) testi menee samalla koodilla ja samalla siemenellä
joskus läpi ja joskus ei. Satunnaistetussa testissä siemen kiinnittää
ärsykkeet, joten epävakauden syy on muualla: kilpatilanne
testipenkissä, aikaraja, joka ylittyy kuormitetulla koneella,
alustamaton muuttuja tai riippuvuus ympäristöstä. Epävakaa testi on
pahempi kuin rikkinäinen, koska se opettaa ohittamaan punaisen
tuloksen.

```{.python tiedosto="esimerkit/vuo/historia.py" osa="epavakaat"}
```

Kysely ryhmittelee tulokset version, testin ja siemenen mukaan.
`COUNT(DISTINCT t.tila = 'ok')` on 2 vain, jos ryhmässä on sekä
läpäissyt että hylätty tulos.

## Esimerkki

Esimerkki simuloi neljän version historian, jossa vika tulee koodiin
versiossa c3:

```{.python tiedosto="esimerkit/08-historia.py" osa="versiot"}
```

Jokainen versio ajetaan kahdeksalla siemenellä ja kirjataan
historiaan. Lopuksi versio c4 ajetaan uudelleen, ja epävakautta
havainnollistetaan muuttamalla yhden siemenen tulos käsin. Testipenkki
on deterministinen, joten oikeaa epävakautta siihen ei saa:

```{.python tiedosto="esimerkit/08-historia.py" osa="kirjaus"}
```

```{.python tiedosto="esimerkit/08-historia.py" osa="kyselyt"}
```

```{.tuloste tiedosto="esimerkit/08-historia.odotettu"}
```

![Sama historia kuvana. Vasemmalla trendi, jossa versiosta on mukana
viimeisin ajo. Oikealla jokainen ajo siemenittäin: versio c3 rikkoo
neljä siementä, ja c4:n uusinta-ajossa siemen 7 vaihtaa tulosta,
vaikka koodi on sama.](kuvat/historia.png){width=92%}

Trendi näyttää, että versio c3 rikkoi testin. Versio c4 näyttää
paremmalta kuin c3, mutta vain siksi, että uusinta-ajossa siemen 7 meni
läpi. Ensimmäisen hylkäävän version kysely osoittaa versioon c3, ja
epävakaiden kysely löytää siemenen 7. Ilman historiaa c4:n parempi
tulos olisi voinut näyttää korjaukselta. Kuva on piirretty samasta
tietokannasta samoilla kyselyillä (`kuvat/piirra.py`): tällainen
ruudukko on yksinkertaisin kojelauta, ja se tehdään Matplotlibilla
muutamalla kymmenellä rivillä.

## Mitä historiasta voi tehdä

- **Karanteeni.** Tunnettu epävakaa testi siirretään omaan listaansa.
  Sitä ajetaan edelleen, mutta sen tulos ei kaada putkea. Karanteenilla
  on omistaja ja määräaika, kuten luvun 6 hyväksytyillä
  varoituksilla.
- **Uusintapolitiikka.** Hylätty ajo ajetaan kerran uudelleen samalla
  siemenellä. Jos tulos muuttuu, testi merkitään epävakaaksi eikä
  ajoa hyväksytä. Pelkkä uusiminen kunnes menee läpi piilottaa vian.
- **Kesto ja resurssit.** Samaan tauluun tallennetaan ajon kesto ja
  muistinkulutus. Kymmenen prosentin hidastuminen versiosta toiseen on
  helppo nähdä kyselyllä ja vaikea huomata muuten.
- **Kojelauta.** Trendi ja avoimet allekirjoitukset näytetään CI:n
  koostesivulla. Luvun 5 koosteet toimivat sellaisinaan.

## Käytännössä

- **Kirjaa jokainen ajo.** Myös onnistuneet ajot tallennetaan, koska
  ilman niitä ei löydy ensimmäistä hylkäävää versiota eikä epävakaita
  testejä.
- **Versio ja järjestys.** Commit-tunniste ja sen paikka historiassa
  tallennetaan erikseen.
- **Allekirjoitus tietokantaan, loki tiedostoon.** Kyselyt käyttävät
  allekirjoituksia, ja ihminen lukee lokin.
- **Epävakaa testi korjataan.** Karanteeni on väliaikainen. Pysyvä
  korjaus on syyn löytäminen.

## Itsearviointi

- Osaat suunnitella regressiohistorian tietokantaskeeman ja kirjata
  ajot transaktioina.
- Osaat kirjoittaa SQL-kyselyt trendille, ensimmäiselle hylkäävälle
  versiolle ja epävakaille testeille.
- Osaat käyttää historiaa `git bisect` -haun lähtökohtana.
- Osaat selittää, miksi epävakaa testi on haitallisempi kuin
  rikkinäinen ja miten sitä käsitellään.
