# Pilkkominen ja arviointi

Arvio on perusteltu käsitys siitä, paljonko työtä jokin vaatii.
Arvioita tarvitaan päätöksiin: kannattaako työ tehdä, mikä tehdään
ensin ja mitä voidaan luvata. Tässä luvussa käsitellään työn
pilkkomista, arviointitekniikoita ja syitä, joiden takia arviot ovat
järjestelmällisesti liian pieniä. Luku 6 jatkaa ennustamiseen
mitatusta historiasta.

## Arvio, tavoite ja sitoumus

Steve McConnell erottaa kolme asiaa, jotka arkipuheessa sekoittuvat:

- **Arvio** on ennuste: ”tämä vie todennäköisesti 4–7 viikkoa”.
- **Tavoite** on liiketoiminnan toive: ”tarvitsemme tämän messuille
  maaliskuussa”.
- **Sitoumus** on lupaus: ”toimitamme nämä ominaisuudet maaliskuun
  loppuun mennessä”.

Kun arviolta pyydetään tavoitteen näköistä lukua, saadaan toiveikas
sitoumus, jota kukaan ei ole arvioinut. Terve järjestys on tehdä arvio
ensin, verrata sitä tavoitteeseen ja sitoutua vasta, kun ero on
käsitelty: laajuutta karsitaan, aikataulua siirretään tai riski
hyväksytään tietoisesti.

Arvio on aina väli tai jakauma. Yksi luku on arvion väärinkäyttöä,
koska se piilottaa epävarmuuden, joka on arvion tärkein sisältö.

## Epävarmuuskartio

Arvion tarkkuus riippuu siitä, kuinka paljon työstä tiedetään. Barry
Boehmin aineistoon perustuva **epävarmuuskartio** kuvaa tätä: hankkeen
alussa, kun on vain idea, toteuma voi olla neljäsosa arviosta tai
nelinkertainen. Epävarmuus pienenee vain, kun päätöksiä tehdään ja
asioita selviää.

![Epävarmuuskartio McConnellin esittämin kertoimin. Kartio ei kapene
ajan kuluessa itsestään vaan sitä mukaa, kun avoimia kysymyksiä
ratkaistaan.](kuvat/kartio.png){width=66%}

Kartiosta seuraa kaksi käytännön sääntöä. Ensiksi alkuvaiheen
arviosta ei pidä tehdä sitoumusta: kiinteä hinta ja aikataulu pelkän
idean perusteella on arpapeliä. Toiseksi arvio päivitetään, kun tieto
lisääntyy. Kuukauden työn jälkeen tiedetään enemmän kuin alussa, ja
arvion pitää muuttua sen mukana.

## Työn pilkkominen

Suurta työtä ei voi arvioida eikä seurata. Se pilkotaan osiin, joista
jokainen on niin pieni, että sen sisällön ymmärtää.

Perinteinen väline on **työn ositus** (*work breakdown structure*,
WBS): hierarkia, jossa koko toimitus jaetaan osatuloksiin ja ne
edelleen työpaketeiksi. Ositus tehdään tulosten, ei tehtävien mukaan,
ja sen tarkoitus on varmistaa, ettei mitään unohdu: asennus, koulutus,
tietojen siirto ja dokumentaatio ovat osia, jotka jäävät helposti
arviosta pois.

Ohjelmistossa ratkaisevaa on pilkkomisen suunta. **Vaakasuora** jako
seuraa arkkitehtuurin kerroksia: ensin tietokanta, sitten palvelukerros
ja lopuksi käyttöliittymä. Mikään ei toimi ennen kuin kaikki kerrokset
ovat valmiit, ja integraatio jää loppuun. **Pystysuora viipale** kulkee
kaikkien kerrosten läpi ja toteuttaa yhden kapean toiminnon kokonaan:
asiakas voi hakea tuotetta nimellä. Viipaleen voi näyttää käyttäjälle,
ja se testaa arkkitehtuurin heti.

Suuren tarinan voi viipaloida esimerkiksi

- työnkulun vaiheiden mukaan (ensin tilaus ilman maksua),
- sääntöjen mukaan (ensin yksi toimitustapa, sitten muut),
- datan mukaan (ensin yksi tiedostomuoto),
- onnistuneen polun ja virhetilanteiden mukaan,
- laadun mukaan (ensin toimiva, sitten nopea).

## Suhteellinen arviointi

Ihmiset arvioivat suhteita paremmin kuin absoluuttisia määriä. On
helpompi sanoa, että työ on kaksi kertaa edellisen kokoinen, kuin että
se vie yhdeksän päivää. Tähän perustuvat **tarinapisteet**: tiimi
valitsee tutun vertailutyön, antaa sille pistemäärän ja arvioi muut
suhteessa siihen. Asteikko on usein Fibonaccin lukujonon tapainen (1,
2, 3, 5, 8, 13), koska kasvavat välit muistuttavat, että suuren työn
arvio on epätarkempi. Vielä karkeampi asteikko on paitakoot S, M ja L.

**Suunnittelupokerissa** jokainen arvioi itsenäisesti ja paljastaa
arvionsa yhtä aikaa. Näin ensimmäisenä sanottu luku ei ankkuroi muita.
Suurin hyöty tulee erimielisyydestä: kun yksi sanoo 2 ja toinen 13,
he ymmärtävät työn eri tavoin, ja keskustelu paljastaa unohtuneen
vaatimuksen tai riskin. Arvio on tässä sivutuote; yhteinen ymmärrys on
päätuote.

Pisteitä on myös arvosteltu, ja kritiikki on syytä tuntea:

- Pisteet eivät ole aikaa, mutta niitä käytetään aikana. Kun johto
  muuntaa pisteet päiviksi, suhteellisen arvioinnin etu katoaa.
- Pisteet ovat tiimikohtaisia. Kahden tiimin nopeuksia ei voi verrata
  eikä laskea yhteen.
- Kun nopeudesta tehdään tavoite, arviot kasvavat. Tämä on esimerkki
  Goodhartin laista: mittari, josta tulee tavoite, lakkaa olemasta
  hyvä mittari.
- Arviointiin kuluu aikaa, eikä ole selvää, parantaako se ennusteita.
  Luvussa 6 verrataan pisteisiin ja kappalemääriin perustuvia
  ennusteita.

## Kolmipistearvio

Kun arvio tarvitaan päivinä, epävarmuuden saa näkyviin kysymällä kolme
lukua: **paras**, **todennäköisin** ja **huonoin** tapaus.
PERT-menetelmä (*program evaluation and review technique*, 1950-luvun
lopulta) laskee niistä odotusarvon ja keskihajonnan:

$$E = \frac{o + 4m + p}{6}, \qquad \sigma = \frac{p - o}{6}$$

Tässä $o$ on paras, $m$ todennäköisin ja $p$ huonoin arvio.
Riippumattomien tehtävien odotusarvot lasketaan yhteen, ja hajonnat
yhdistetään neliöjuurella varianssien summasta.

```{.python tiedosto="esimerkit/05-kolmipiste.py" osa="pert"}
```

Esimerkki vertaa kaavoja simulointiin, jossa jokaisen tehtävän kesto
arvotaan vinosta jakaumasta samojen kolmen luvun perusteella:

```{.tuloste tiedosto="esimerkit/05-kolmipiste.odotettu"}
```

Todennäköisimpien arvojen summa (43 päivää) on taas liian pieni, kuten
johdannossa. PERT-odotusarvo (51,5 päivää) osuu simuloituun keskiarvoon,
ja 85 %:n varmuuteen tarvitaan noin 58 päivää.

Kolmipistearvion heikko kohta on huonoin tapaus. Ihmiset arvioivat sen
liian lähelle todennäköisintä, koska todella huonoa tapausta ei haluta
ajatella. Apuna voi kysyä, kuinka kauan työ kesti silloin, kun se
viimeksi meni pahasti pieleen.

## Puskurin paikka

Tulosteen kolme viimeistä riviä vastaavat kysymykseen, mihin varmuusvara
sijoitetaan.

```{.python tiedosto="esimerkit/05-kolmipiste.py" osa="puskuri"}
```

Jos jokainen tehtävä saa oman varansa niin, että se pitää 85 %:n
varmuudella, varojen summa on 68 päivää. Koko projektin 85 %:n varmuus
saavutetaan kuitenkin 58 päivällä, koska tehtävien ylitykset ja
alitukset tasaavat toisiaan. Omien varojen summa pitäisi 99 %:n
varmuudella, mutta se maksaa kymmenen päivää enemmän.

Tehtäväkohtaisilla varoilla on toinenkin ongelma: ne kuluvat.
**Parkinsonin lain** mukaan työ laajenee täyttämään sille varatun ajan,
ja töiden aloittamista lykätään, kun aikaa tuntuu olevan
(”opiskelijasyndrooma”). Aikaisin valmistunut tehtävä ei siis
aikaista seuraavaa, mutta myöhästynyt myöhästyttää. Eliyahu Goldrattin
kriittisen ketjun menetelmä tekee tästä johtopäätöksen: tehtävät
arvioidaan ilman varaa, ja varat kootaan yhdeksi projektin puskuriksi,
jonka kulumista seurataan. Sama ajatus toimii ilman menetelmän
muuta koneistoa: lupaa asiakkaalle päivä, johon sisältyy puskuri, ja
pidä tiimin sisäiset tavoitteet tiukempina.

## Kriittinen polku

Kun tehtävillä on riippuvuuksia, projektin kesto ei ole kestojen summa
vaan pisimmän polun pituus. **Kriittisen polun menetelmä** (*critical
path method*, CPM) laskee jokaiselle tehtävälle aikaisimman
mahdollisen alun ja myöhäisimmän sallitun lopun. Niiden erotus on
**pelivara**. Tehtävät, joilla pelivaraa ei ole, muodostavat kriittisen
polun: jokainen päivän viive niissä viivästää koko projektia.

```{.dot otsikko="Esimerkin tehtäväverkko. Kestot päivinä; kriittinen polku on lihavoitu."}
digraph {
  rankdir=LR; nodesep=0.25; ranksep=0.4;
  m [label="määrittely\n5", penwidth=1.8];
  tk [label="tietokanta\n9"]; r [label="rajapinta\n10", penwidth=1.8];
  kl [label="käyttöliittymä\n15"]; i [label="integraatio\n6", penwidth=1.8];
  t [label="testaus\n5", penwidth=1.8]; ko [label="käyttöönotto\n3", penwidth=1.8];
  m -> tk; m -> r [penwidth=1.8]; m -> kl;
  tk -> i; r -> i [penwidth=1.8]; kl -> t;
  i -> t [penwidth=1.8]; t -> ko [penwidth=1.8];
}
```

Laskenta on kaksi läpikäyntiä topologisessa järjestyksessä (taito
*Algoritmit*): eteenpäin aikaisimmat loput, taaksepäin myöhäisimmät.

```{.python tiedosto="esimerkit/05-kriittinen-polku.py" osa="cpm"}
```

```{.tuloste tiedosto="esimerkit/05-kriittinen-polku.odotettu"}
```

Tulosteen alkuosa on perinteinen CPM-tulos: projekti kestää 29 päivää,
ja tietokannalla ja käyttöliittymällä on päivän pelivara.

Loppuosa näyttää, mitä epävarmuus tekee. Kun jokaisen tehtävän kesto
vaihtelee, kriittinen polku ei ole sama joka kerta: rajapinta on
kriittinen vain noin puolessa toistoista, ja ”pelivaralliset”
tietokanta ja käyttöliittymä päätyvät kriittisiksi joka viidennellä tai
kolmannella kerralla. Lisäksi projektin keskimääräinen kesto (34,0
päivää) on pidempi kuin kriittisen polun keskimääräinen kesto (32,9
päivää). Tämä **yhtymäkohtien harha** johtuu siitä, että testaus alkaa
vasta, kun hitain edeltäjistä on valmis, ja kolmesta rinnakkaisesta
haarasta jokin on lähes aina myöhässä. Mitä enemmän rinnakkaisia
polkuja yhtyy, sitä optimistisempi yksittäisen polun laskelma on.

## Miksi arviot ovat liian pieniä

Arviointivirhe ei ole satunnainen vaan vino samaan suuntaan. Syitä on
useita:

- **Suunnitteluharha.** Daniel Kahneman ja Amos Tversky havaitsivat,
  että ihmiset arvioivat oman hankkeensa sen suunnitelman perusteella
  ja jättävät huomiotta, kuinka vastaavat hankkeet ovat aiemmin
  sujuneet. Suunnitelma kuvaa tapauksen, jossa mikään ei mene vikaan.
- **Unohtunut työ.** Arvioon lasketaan koodaus, mutta ei katselmointia,
  testiympäristön pystytystä, tietojen siirtoa, palavereita eikä
  sairauspoissaoloja.
- **Vinot jakaumat.** Kuten luvussa 1 nähtiin, todennäköisimpien
  arvojen summa ei ole todennäköinen summa.
- **Paine.** Kun toivottu vastaus tiedetään, arvio liukuu sitä kohti.

Paras tunnettu vastalääke on **vertailuluokkaennuste**, jota Bent
Flyvbjerg on soveltanut suuriin hankkeisiin: kysytään ensin, kuinka
kauan vastaavat hankkeet ovat todella kestäneet, ja käytetään sitä
lähtökohtana. Omaa suunnitelmaa käytetään vasta säätämään tätä
perustasoa. Ohjelmistotiimille vertailuluokka on sen oma historia, ja
luku 6 rakentaa ennusteen suoraan siitä.

Douglas Hofstadter tiivisti kokemuksen itseensä viittaavaksi laiksi:
työ kestää aina kauemmin kuin odotat, vaikka ottaisit Hofstadterin lain
huomioon.

## Käytännössä

- **Anna arvio välinä ja kerro, mihin se perustuu.** ”Kuudesta
  kymmeneen viikkoa, jos maksurajapinta toimii kuten dokumentaatio
  lupaa” on arvio. ”Kahdeksan viikkoa” on arvaus.
- **Pilko ennen kuin arvioit.** Yli viikon mittainen työ sisältää
  lähes aina jotain, mitä ei ole ajateltu. Pilkkominen on arvioinnin
  arvokkain vaihe, koska se paljastaa sisällön.
- **Arvioi vain niin tarkasti kuin päätös vaatii.** Jos päätös on sama
  arvion ollessa kolme tai kuusi viikkoa, tarkempi arvio on hukkaa.
- **Käytä historiaa perustasona.** Vertaa uutta työtä tehtyihin
  vastaaviin ja niiden todellisiin kestoihin, ei muistikuvaan
  arvioista.
- **Kirjaa oletukset.** Arvio on voimassa vain oletustensa kanssa.
  Kun oletus kaatuu, arvio päivitetään eikä sitä puolusteta.
- **Yksi puskuri, näkyvästi.** Projektin lopussa oleva yhteinen
  puskuri on tehokkaampi kuin tehtäviin piilotetut varat, ja sen
  kulumisesta näkee tilanteen yhdellä silmäyksellä.
- **Seuraa myös lähes kriittisiä polkuja.** Tehtävä, jolla on päivän
  pelivara, on käytännössä kriittinen.

## Itsearviointi

- Osaat erottaa arvion, tavoitteen ja sitoumuksen ja selittää
  epävarmuuskartion merkityksen.
- Osaat pilkkoa suuren työn pystysuoriksi viipaleiksi ja perustella,
  miksi se on parempi kuin kerroksittainen jako.
- Osaat kuvata suhteellisen arvioinnin ja suunnittelupokerin sekä
  tarinapisteisiin kohdistetun kritiikin.
- Osaat laskea kolmipistearviosta odotusarvon ja hajonnan ja selittää,
  miksi yhteinen puskuri on pienempi kuin tehtäväkohtaiset varat.
- Osaat laskea tehtäväverkon kriittisen polun ja pelivarat sekä
  selittää, miksi rinnakkaiset polut pidentävät odotettua kestoa.
- Osaat nimetä syitä arvioiden optimismiin ja kuvata
  vertailuluokkaennusteen.
