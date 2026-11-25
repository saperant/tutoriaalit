# Kognitiivinen kuorma ja tiimin koko

Edellisen luvun malli perustuu väitteeseen, että tiimi pystyy
hallitsemaan vain rajallisen määrän asioita. Tämä luku katsoo, mistä
raja tulee, kuinka suuri tiimi voi olla ja miten kuormaa voi arvioida.

## Miksi tiimit ovat pieniä

*Ohjelmistoprojektin hallinta* johti Brooksin laista, että $n$ hengen
ryhmässä on $n(n-1)/2$ viestintäpolkua. Kahdeksalla polkuja on 28,
kuudellatoista jo 120. Kun ryhmä kasvaa, jokainen käyttää yhä
suuremman osan ajastaan pysyäkseen selvillä muiden tekemisistä.

Ratkaisu on jakaa väki tiimeihin ja sopia, että tiimien välillä
viestitään rajapinnan kautta eikä jokainen jokaisen kanssa:

```{.python tiedosto="esimerkit/05-viestinta.py" osa="polut"}
```

```{.tuloste tiedosto="esimerkit/05-viestinta.odotettu"}
```

Yhtenä ryhmänä 128 hengellä olisi yli 8 000 mahdollista
viestintäpolkua. Kuuteentoista kahdeksan hengen tiimiin jaettuna
polkuja on tiimien sisällä 448, ja jos kukin tiimi on tekemisissä
kolmen naapurin kanssa, tiimisuhteita on 24. Laskelma olettaa, että
rajapinnat pitävät. Jos jokaisen tiimin on puhuttava jokaisen kanssa,
tiimisuhteita on 120 ja ongelma on vain siirtynyt tasoa ylemmäs. Tiimijako
kannattaa vasta, kun tiimien väliset riippuvuudet ovat harvoja.

![Viestintäpolkujen määrä väen kasvaessa: yksi ryhmä, kahdeksan hengen
tiimit sisäisine polkuineen ja tiimien väliset suhteet, kun kullakin
tiimillä on kolme naapuria.](kuvat/viestinta.png){width=50%}

## Kuinka suuri tiimi

Käytännön suositukset osuvat samaan haarukkaan. Scrum-opas neuvoo
pitämään tiimin enintään kymmenen hengen kokoisena, Team Topologies
puhuu viidestä yhdeksään hengestä, ja Amazonin ”kahden pizzan
sääntö” sanoo saman ruokamäärinä. Alaraja tulee haavoittuvuudesta:
kolmen hengen tiimissä yhden loma tai lähtö vie kolmanneksen
kapasiteetista ja usein ainoan osaajan (luku 6).

Suurempien ryhmien kokoja perustellaan usein **Dunbarin luvuilla**.
Antropologi Robin Dunbar päätteli kädellisten aivojen koosta, että
ihminen pystyy ylläpitämään noin 150 vakaata sosiaalista suhdetta, ja
sisempiä piirejä on kuvattu luvuilla 5, 15 ja 50. Luvut ovat
käyttökelpoinen muistisääntö siitä, että luottamus ei skaalaudu
rajatta: viidentoista hengen ryhmässä kaikki vielä tuntevat toistensa
työn, 50 hengen osastossa eivät. Tarkkoina rajoina niihin ei pidä
nojata, sillä myöhempien analyysien mukaan aineistosta johdetun luvun
epävarmuus on erittäin suuri.

## Pitkäikäiset tiimit

Tiimi ei ole tuottava heti. Bruce Tuckmanin vuonna 1965 kuvaamat
vaiheet (muodostuminen, kuohunta, sopiminen, suoriutuminen) ovat
yksinkertaistus, mutta ydin pätee: ihmisten täytyy oppia toistensa
tavat, ennen kuin yhteistyö on sujuvaa. Tutkimus tukee tätä.
Ohjelmistopalveluyrityksen projekteja tarkastelleissa tutkimuksissa
tiimit, joiden jäsenet olivat työskennelleet aiemmin yhdessä,
tuottivat vähemmän virheitä ja pysyivät paremmin aikataulussa.

Tästä seuraa periaate **työ tuodaan tiimille, ei ihmisiä työn luo**.
Kun projekti päättyy, tiimi saa uuden tehtävän eikä hajoa. DeMarco ja
Lister kuvaavat samaa kirjassaan *Peopleware*: yhteen hitsautunut
tiimi on organisaation arvokkain ja helpoimmin tuhottava omaisuus.

Pysyvyydellä on myös hintansa. Vuosia muuttumaton tiimi voi
sulkeutua, ja osaaminen jää sen sisälle. Hallittu kierto, jossa yksi
jäsen vaihtaa tiimiä silloin tällöin, levittää tietoa hajottamatta
tiimiä.

## Kognitiivinen kuorma

John Swellerin kognitiivisen kuorman teoria (1988) kuvaa, miten
työmuistin rajallisuus vaikuttaa oppimiseen. Team Topologies lainaa
siitä jaottelun ja soveltaa sitä tiimiin:

| Kuorman laji | Mistä syntyy | Mitä sille tehdään |
|------------------|------------------------------|--------------------------|
| sisäinen | tehtävän perusosaaminen: kieli, kehykset | koulutus, parityö, harkitut tekniikkavalinnat |
| ulkoinen | ympäristö: miten julkaisen, mistä löydän lokit | automatisointi, alusta, hyvä dokumentaatio |
| hyödyllinen | itse ongelma: liiketoiminta-alueen säännöt | tähän halutaan jättää tilaa |

Siirto yksilön oppimisesta tiimin vastuisiin on vertaus, ei mitattu
tulos, eikä tiimin kuormalle ole vakiintunutta mittaria. Vertaus on
silti hyödyllinen, koska se muuttaa kysymyksen. ”Ehtiikö tiimi tehdä
tämän?” on kapasiteettikysymys. ”Pystyykö tiimi pitämään tämän
mielessään?” on kuormakysymys, ja siihen vastaus voi olla ei, vaikka
kalenterissa olisi tilaa.

Oireita liiallisesta kuormasta ovat jatkuva tehtävien vaihtelu, osat,
joihin kukaan ei uskalla koskea, pitkä perehdytys ja se, että tiimi
ei ehdi parantaa mitään, koska kaikki aika menee pinnalla
pysymiseen.

## Karkea mittari

Team Topologies ehdottaa nyrkkisääntöä: luokittele tiimin
vastuualueet yksinkertaisiksi, mutkikkaiksi tai kompleksisiksi.
Yksi tiimi voi hoitaa kaksi tai kolme yksinkertaista aluetta tai yhden
kompleksisen, mutta ei kahta mutkikasta. Säännöstä saa pisteytyksen,
johon voi lisätä tekniikoiden määrän ja päivystyksen. Kustakin
tiimistä kirjataan alueet vaativuuksineen, tekniikat ja se, päivystääkö
tiimi:

```{.python tiedosto="esimerkit/05-kuorma.py" osa="tiimit"}
```

```{.python tiedosto="esimerkit/05-kuorma.py" osa="mittari"}
```

```{.tuloste tiedosto="esimerkit/05-kuorma.odotettu"}
```

Mittari on tarkoituksella karkea. Sen arvo on vertailussa: kun
tilaustiimi saa kolme huomiota ja hakutiimi ei yhtään, on syytä kysyä
tilaustiimiltä, miltä työ tuntuu. Paras mittari onkin kysely: tiimiltä
kysytään säännöllisesti, kuinka hyvin se kokee hallitsevansa
vastuualueensa, ja vastausten muutosta seurataan. Kuormaa ei näe ulkoa.

Kuormaa kevennetään neljällä tavalla: siirretään alue toiselle
tiimille, jaetaan tiimi kahtia murtumatasoa pitkin (luku 4), siirretään
ulkoista kuormaa alustalle (luku 6) tai karsitaan tekniikoita.

## Käytännössä

- **Rajaa vastuut, älä vain työmäärää.** WIP-raja rajoittaa
  yhtäaikaisia töitä; vastuualueiden määrä rajoittaa sitä, mitä tiimin
  on ylipäätään muistettava.
- **Älä jaa tiimiä vain koon vuoksi.** Kahtiajako ilman selkeää rajaa
  tuottaa kaksi tiimiä, jotka tekevät kaiken yhdessä.
- **Varo yhden hengen vastuualueita.** Alue, jonka vain yksi ihminen
  hallitsee, ei ole tiimin vastuulla vaan yksilön.

## Itsearviointi

- Osaat laskea viestintäpolut ja selittää, milloin tiimijako vähentää
  koordinointia.
- Osaat perustella tiimin koon ylä- ja alarajan ja kertoa, mitä
  Dunbarin luvuista voi päätellä ja mitä ei.
- Osaat erottaa sisäisen, ulkoisen ja hyödyllisen kuorman ja nimetä
  keinon kunkin hallintaan.
- Osaat arvioida tiimin kuormaa vastuualueiden vaativuudesta ja tiedät
  mittarin rajat.
