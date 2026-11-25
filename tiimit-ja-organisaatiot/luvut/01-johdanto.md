# Johdanto {.runko-johdanto}

Ohjelmiston tekevät ihmiset, ja ihmiset on jaettu tiimeihin. Jako
päättää, kuka puhuu kenen kanssa päivittäin, kenen työjonoon muutos
menee odottamaan ja kuka herää yöllä, kun palvelu kaatuu. Siksi
organisaatiokaavio on tekninen päätös siinä missä tietokannan valinta:
se näkyy järjestelmän rakenteessa, toimitusnopeudessa ja laadussa.

*Ohjelmistoprojektin hallinta* käsitteli yhden tiimin työtä:
vaatimuksia, arvioita, virtausta ja riskejä. Tämä tutoriaali nousee
tasoa ylemmäs ja kysyy, miten monta tiimiä järjestetään saman
järjestelmän ympärille. Aiheita ovat Conwayn laki, perinteiset
organisaatiomallit, Team Topologies, kognitiivinen kuorma, omistajuus
ja alustat, DevOps ja SRE, päätöksenteko sekä skaalausmallit.

Mitään mallia ei esitetä ratkaisuna kaikkeen. Jokaisesta kerrotaan,
mihin ongelmaan se syntyi, mihin se perustuu, mitä siitä tiedetään ja
missä sen rajat ovat. Organisaatiomalleja myydään paljon, ja niiden
tutkimusnäyttö on usein ohuempaa kuin esitysten varmuus antaa
ymmärtää. Kun näyttöä on, se mainitaan; kun väite on jonkun
kokemukseen perustuva nyrkkisääntö, sekin sanotaan.

## Esimerkkiyritys

Esimerkkinä on verkkokauppa, jota tekee kaksitoista kehittäjää.
Järjestelmässä on neljä ominaisuutta (haku, ostoskori, tilaus ja
maksu), ja jokaisessa on kolme kerrosta: käyttöliittymä, rajapinta ja
tietokanta. Osia on siis kaksitoista. Osat kutsuvat toisiaan näin:

```{.python tiedosto="esimerkit/organisaatio.py" osa="riippuvuudet"}
```

Väen voi jakaa tiimeihin ainakin kahdella tavalla. Kerroksittain
syntyy kolme neljän hengen erikoistiimiä, ominaisuuksittain neljä
kolmen hengen tiimiä, joissa jokaisessa on yksi kunkin kerroksen
osaaja:

```{.python tiedosto="esimerkit/organisaatio.py" osa="jaot"}
```

```{.dot otsikko="Samat kaksitoista osaa kahdella tiimijaolla: kerroksittain (vaakarivit) ja ominaisuuksittain (pystysarakkeet)"}
digraph {
  rankdir=TB; nodesep=0.25; ranksep=0.3;
  node [width=0.9, fixedsize=true, height=0.38];
  subgraph cluster_ui { label="käyttöliittymätiimi"; style=dashed;
    hu [label="haku/ui"]; ku [label="kori/ui"];
    tu [label="tilaus/ui"]; mu [label="maksu/ui"]; }
  subgraph cluster_api { label="rajapintatiimi"; style=dashed;
    ha [label="haku/api"]; ka [label="kori/api"];
    ta [label="tilaus/api"]; ma [label="maksu/api"]; }
  subgraph cluster_db { label="tietokantatiimi"; style=dashed;
    hd [label="haku/db"]; kd [label="kori/db"];
    td [label="tilaus/db"]; md [label="maksu/db"]; }
  hu -> ha -> hd; ku -> ka -> kd; tu -> ta -> td; mu -> ma -> md;
  ka -> ha [constraint=false]; ta -> ka [constraint=false];
  ta -> ma [constraint=false]; ma -> ta [constraint=false];
}
```

Kumpi jako on parempi? Se riippuu siitä, millaisia muutoksia
järjestelmään tehdään. Luetellaan kahdeksan tyypillistä muutosta ja
lasketaan, montako tiimiä kukin vaatii:

```{.python tiedosto="esimerkit/01-jako.py" osa="muutokset"}
```

```{.python tiedosto="esimerkit/01-jako.py" osa="laskenta"}
```

```{.tuloste tiedosto="esimerkit/01-jako.odotettu"}
```

Summa on sama, mutta jakauma on päinvastainen. Uusi hakusuodatin
vaatii kerrosjaossa kolmen tiimin työn oikeassa järjestyksessä,
ominaisuusjaossa yhden. Ulkoasun uudistus taas on kerrosjaossa yhden
tiimin työ ja ominaisuusjaossa neljän. Jokainen tiimijako tekee osan
muutoksista helpoiksi ja osan kalliiksi. Tärkein kysymys on siis,
kumpia muutoksia tulee enemmän, ja siihen vastaa versionhallinnan
historia (luku 2).

Tämä on tutoriaalin perusajatus: **tiimiraja on rajapinta**. Rajan
sisällä muutos on keskustelu työpöydän yli, rajan yli se on pyyntö
toisen tiimin työjonoon. Organisaation suunnittelu on sen
päättämistä, mitkä muutokset saavat olla halpoja.

## Mitä tutoriaali kattaa

| Luku | Kysymys |
|------|--------------------------------------------------------|
| 2 | Miksi järjestelmän rakenne seuraa organisaation rakennetta? |
| 3 | Mitä perinteiset organisaatiomallit optimoivat ja mitä luovutus maksaa? |
| 4 | Mitä Team Topologies ehdottaa ja mitä siitä tiedetään? |
| 5 | Kuinka paljon yksi tiimi voi omistaa? |
| 6 | Kuka omistaa koodin, palvelun ja alustan? |
| 7 | Kuka vastaa tuotannosta: DevOps ja SRE? |
| 8 | Kuka päättää arkkitehtuurista? |
| 9 | Mitä skaalausmallit ratkaisevat ja mihin hintaan? |
| 10 | Miten hajautettu tiimi toimii ja miten organisaatiota muutetaan? |

Esimerkit ovat pieniä Python-ohjelmia, jotka laskevat, simuloivat tai
lukevat Git-historiaa. Mallien luvut ovat havainnollistavia, eivät
mitattuja: niiden tarkoitus on näyttää, mistä ilmiö johtuu ja mihin
suuntaan parametrit vaikuttavat. Analyysit (yhdessä muuttuvat
tiedostot, omistajuus, CODEOWNERS-kattavuus) toimivat sellaisinaan
omaan repositorioon.

## Esitiedot ja rajaus

Esitietona on *Ohjelmistoprojektin hallinta*: Scrum, Kanban, virtaus,
jonot ja Brooksin laki oletetaan tutuiksi. Esimerkkien lukemiseen
riittää *Ohjelmoinnin perusteet (Python)* ja *Versionhallinta (Git)*.

| Aihe | Taito |
|--------------------------------|--------------------------------|
| mikropalvelut, rajatut kontekstit | *Palveluarkkitehtuurit* |
| palvelutasotavoitteet ja virhebudjetti | *Skaalautuvien järjestelmien suunnittelu* |
| toimitusputki ja toimituskyvyn mittarit | *Jatkuva integraatio ja toimitus* |
| arkkitehtuurikuvaukset ja päätöslokit | *Tekninen dokumentaatio* |
| katselmointi ja tietoturva prosessissa | *Tietoturva kehitystyössä* |

## Esimerkkien ajaminen

```text
make testaa      # ruff, mypy --strict ja esimerkkien tulosteet
python3 esimerkit/03-luovutukset.py
```

Esimerkit käyttävät vain Pythonin standardikirjastoa ja Gitiä. Kaksi
esimerkkiä luo työhakemistoon pienen Git-repositorion, joten ne
kannattaa ajaa tyhjässä hakemistossa.
