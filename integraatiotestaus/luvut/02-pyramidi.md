# Testipyramidi ja integraatiotestien paikka

Testipyramidi on vanha mutta yhä hyödyllinen kuva: paljon nopeita
yksikkötestejä, vähemmän integraatiotestejä ja muutama päästä päähän
-testi. Kuvan ajatus ei ole testien lukumäärien suhde vaan hinta:
mitä ylempänä testi on, sitä hitaammin se ajetaan, sitä vaikeammin
vika paikannetaan ja sitä useammin testi epäonnistuu syystä, joka ei
ole koodin vika.

```{.dot otsikko="Testipyramidi: hinta kasvaa ylöspäin, kattavuus alaspäin"}
digraph {
  rankdir=TB; nodesep=0.3; ranksep=0.15;
  node [shape=box, width=4.2];
  e2e [label="Päästä päähän: koko järjestelmä\nminuutteja, harvoin", width=2.2];
  int [label="Integraatio: oma koodi + oikeat riippuvuudet\nsekunteja, jokaisessa muutoksessa", width=3.4];
  yks [label="Yksikkö: oma koodi + väärennökset\nmillisekunteja, jatkuvasti", width=4.6];
  e2e -> int -> yks [style=invis];
}
```

## Mitä yksikkötesti näkee

Yksikkötesti eristää testattavan koodin. Varastopalvelun logiikka
testataan väärennöksillä: muistissa toimiva varasto, tynkä, joka
palauttaa aina saman hinnan, ja vakoilija, joka kirjaa julkaistut
tapahtumat. Nimet ja niiden erot käsitellään luvussa 6.

```{.python tiedosto="esimerkit/testit/test_yksikko.py" osa="kaksoiset"}
```

```{.python tiedosto="esimerkit/testit/test_yksikko.py" osa="yksikkotesti"}
```

Testi on nopea, deterministinen ja kertoo vian tarkasti: jos hinta
lasketaan väärin, vika on palvelussa. Sama tiedosto tarkistaa myös, että
hintapalvelun katko ei lukitse saldoa ja että liian suuri tilaus ei
julkaise tapahtumaa. Tällaiset säännöt kuuluvat yksikkötesteihin, ja
niitä kannattaa olla paljon.

## Mitä yksikkötesti ei näe

Yksikkötesti ei näe mitään, mikä on väärennöksen ulkopuolella. Saumoissa
piilevät viat ovat tyypillisesti näitä:

| Sauma | Esimerkki viasta |
|-------|------------------|
| SQL-murre | lause toimii SQLitessä mutta ei PostgreSQLissä |
| rajoitteet | uniikkirajoite tai CHECK hylkää rivin |
| transaktiot | samanaikaiset päivitykset ylivaraavat saldon |
| tyypit ja muunnokset | aikavyöhyke, desimaalit, merkistö |
| serialisointi | JSON-kentän nimi tai tyyppi muuttuu |
| verkko | aikaraja, katkos, uudelleenyritykset |
| asetukset | väärä yhteysosoite, puuttuva oikeus |

Yleinen oikotie on testata "oikeaa tietokantaa" muistissa toimivalla
SQLitellä, koska se ei vaadi mitään asennusta. Seuraava esimerkki ajaa
saman skeeman ja samat lauseet sekä SQLitessä että PostgreSQLissä:

```{.python tiedosto="esimerkit/luku02/murre.py" osa="lauseet"}
```

```{.tuloste tiedosto="esimerkit/luku02/murre.odotettu"}
```

SQLite hyväksyy liian pitkän merkkijonon `varchar(8)`-sarakkeeseen ja
tekstiä kokonaislukusarakkeeseen, koska sen tyypit ovat suosituksia
(*type affinity*), eivät rajoitteita. Sen `LIKE` ei välitä
kirjainkoosta, PostgreSQLin välittää. Teksti ja luku vertautuvat eri
tavoin, ja NULL lajitellaan eri päähän. Jokainen rivi on testi, joka
menisi SQLitellä läpi ja tuotannossa rikki, tai päinvastoin. Testi on
yhtä hyvä kuin sen ympäristön samankaltaisuus tuotannon kanssa.

## Hinta ja hyöty

Integraatiotesti maksaa kolmella tavalla:

- **Aika.** PostgreSQL-kontti käynnistyy pari sekuntia, ja jokainen
  kysely kulkee verkon yli. Ratkaisu on käynnistää kontti kerran koko
  testiajolle ja eristää testit transaktioilla (luvut 4 ja 5).
- **Ympäristö.** Testi tarvitsee Dockerin ja kuvat. CI-ympäristössä tämä
  on yleensä valmiina, kehittäjän koneella ei aina (luku 10).
- **Epävakaus.** Ajoitus- ja verkko-ongelmat voivat tehdä testistä
  epävakaan (*flaky*). Ratkaisu on odottaa valmiutta eikä nukkua
  arvattua aikaa (luku 3).

Hyöty on, että testi kertoo, toimiiko koodi niiden ohjelmien kanssa,
joiden kanssa se ajetaan tuotannossa. Vika löytyy kehittäjän koneelta
eikä tuotannon lokista.

## Mitä testataan millä tasolla

Varastopalvelussa jako on tämä:

| Taso | Mitä | Tiedosto |
|------------|------------------------------------|-----------------------|
| yksikkö | palvelun säännöt väärennöksillä | `test_yksikko.py` |
| sopimus | tallennuksen säännöt: väärennös ja PostgreSQL | `test_varasto.py` |
| integraatio | samanaikaisuus PostgreSQLissä | `test_samanaikaisuus.py` |
| integraatio | HTTP-asiakas, välimuisti, viestit | `test_hinnat.py` ym. |
| vikasietoisuus | viive ja katkos vikaproxyn takana | `test_viat.py` |
| palvelusopimus | hintapalvelun vastauksen muoto | `test_sopimus.py` |

Jokainen integraatiotesti testaa *yhtä* saumaa. Testi, joka käynnistää
kaiken ja tarkistaa lopputuloksen, on hidas ja kertoo vian syystä
vähän. Kun testi epäonnistuu, nimen ja kontin pitäisi kertoa, mikä
sauma petti.

## Käytännössä

- Testaa liiketoimintasäännöt yksikkötesteillä ja saumat
  integraatiotesteillä. Älä testaa samaa sääntöä kummallakin ilman syytä.
- Älä korvaa tuotannon tietokantaa toisella tietokannalla testeissä.
  Muistikanta on houkutteleva, mutta se testaa eri ohjelmaa.
- Mitoita integraatiotestien määrä saumojen, ei rivien mukaan: yksi
  hyvä testi jokaiselle SQL-lauseelle, rajoitteelle ja virheelle, jonka
  riippuvuus voi palauttaa.
- Pidä integraatiotestit samassa ajossa kuin yksikkötestit, jos ne ovat
  tarpeeksi nopeita. Erillinen "hidas" sarja, jota ajetaan harvoin,
  rapistuu.

## Itsearviointi

- Osaat kertoa, mitä testipyramidin tasot maksavat ja mitä ne löytävät.
- Osaat luetella saumoja, joiden virheet yksikkötesti ohittaa.
- Osaat perustella, miksi tuotannon tietokantaa ei kannata korvata
  testeissä muistikannalla.
- Osaat jakaa sovelluksen testit tasoille niin, että jokainen
  integraatiotesti testaa yhtä saumaa.
