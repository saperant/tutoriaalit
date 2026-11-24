# Jonoteoria

Jaettu resurssi palvelee pyyntöjä yksi kerrallaan: muistiohjain,
väylä, verkkokytkimen portti, välimuistin pankki. Kun pyyntöjä tulee
nopeammin kuin resurssi ehtii palvella, ne jonottavat, ja viive kasvaa.
Jonoteoria laskee tämän viiveen kuormasta ja palveluajasta. Se selittää,
miksi järjestelmä, jonka keskimääräinen käyttöaste on vain 80 %, voi
olla viiveeltään viisinkertainen tyhjään verrattuna.

Jonomalli merkitään Kendallin merkinnällä A/S/c: saapumisprosessi,
palveluajan jakauma ja palvelijoiden määrä. M (markovilainen) tarkoittaa
Poisson-saapumisia tai eksponentiaalista palveluaikaa, D vakiota ja G
yleistä jakaumaa. Eksponentiaalinen jakauma ja Poisson-prosessi on
esitelty paketissa *Todennäköisyys ja tilastot*.

## Littlen laki

Littlen laki on jonoteorian ainoa tulos, joka ei riipu jakaumista:

$$L = \lambda W.$$

Järjestelmässä keskimäärin olevien asiakkaiden määrä $L$ on
saapumisnopeus $\lambda$ kertaa keskimääräinen viipymä $W$. Laki pätee
mille tahansa vakaalle järjestelmälle, jonka rajat voi piirtää: jonolle,
palvelijalle, koko muistijärjestelmälle tai tietokoneelle. Luvussa 3
sillä laskettiin tarvittava rinnakkaisuus. Jos kaksi suuretta tunnetaan,
kolmas seuraa.

## M/M/1, M/D/1 ja M/M/c

Yhden palvelijan jonossa, jossa palvelunopeus on $\mu$ ja käyttöaste
$\rho = \lambda / \mu < 1$, viipymä on

$$W = \frac{1}{\mu - \lambda} = \frac{1/\mu}{1 - \rho}.$$

Viipymä on palveluaika jaettuna vapaana olevalla osuudella. Kun
käyttöaste lähestyy yhtä, viive kasvaa rajatta.

```{.python tiedosto="esimerkit/arkki/jonot.py" osa="mm1"}
```

Pollaczekin ja Hinchinin kaava yleistää tuloksen mille tahansa
palveluajan jakaumalle (M/G/1). Odotusaika riippuu palveluajan toisesta
momentista eli siitä, kuinka paljon palveluajat vaihtelevat:

```{.python tiedosto="esimerkit/arkki/jonot.py" osa="mg1"}
```

Usean palvelijan jonossa (M/M/c) on yhteinen jono ja $c$ palvelijaa.
Erlangin C-kaava antaa todennäköisyyden, että saapuva asiakas joutuu
odottamaan:

```{.python tiedosto="esimerkit/arkki/jonot.py" osa="mmc"}
```

Muistiohjain, joka palvelee yhden 64 tavun pyynnön 10 ns:ssa (6,4 GB/s),
kolmella mallilla. Kahden kanavan vaihtoehdossa kumpikin kanava on puolta
hitaampi, joten kokonaiskapasiteetti on sama:

```{.python tiedosto="esimerkit/04-jonot.py" osa="taulukko"}
```

```{.python tiedosto="esimerkit/04-jonot.py" osa="little"}
```

```{.tuloste tiedosto="esimerkit/04-jonot.odotettu"}
```

![Viipymä käyttöasteen funktiona. Simuloidut pisteet osuvat
M/M/1-käyrälle; vakiopalveluaika (M/D/1) puolittaa
jonotuksen.](kuvat/jonot.png){width=100%}

Taulukosta näkyy kolme asiaa, jotka toistuvat kaikissa jaetuissa
resursseissa:

1. **Viive kasvaa epälineaarisesti.** 50 %:n kuormalla viive on
   kaksinkertainen, 90 %:lla kymmenkertainen. Järjestelmä mitoitetaan
   siksi tyypillisesti 60–80 %:n käyttöasteelle, vaikka kapasiteettia
   jäisi käyttämättä.
2. **Vaihtelu maksaa.** M/D/1:n jonotus on puolet M/M/1:n jonotuksesta,
   koska vakiopalvelussa ei ole pitkiä palveluaikoja, joiden takana muut
   odottavat. DRAM-pyynnöt ovat lähes vakiomittaisia, mutta
   sivuosumat ja -hudit tuovat vaihtelua.
3. **Yksi nopea vai monta hidasta?** Kaksi puolinopeaa kanavaa on
   kevyellä kuormalla huonompi, koska yksittäinen pyyntö palvellaan
   hitaammin (20 ns). Raskaalla kuormalla ero kapenee, koska yhteinen
   jono käyttää kumpaakin palvelijaa.

## Simulointi analyyttisen tuloksen tarkistuksena

Kaavat pätevät vain oletuksillaan. Tapahtumapohjainen simulaattori ei
tarvitse oletuksia, ja samalla se testaa kaavojen toteutuksen.
Simulaattori pitää kirjaa siitä, milloin kukin palvelija vapautuu; uusi
asiakas menee ensimmäisenä vapautuvalle. Määrä järjestelmässä
lasketaan erikseen aikakeskiarvona, jotta Littlen lain voi tarkistaa:

```{.python tiedosto="esimerkit/arkki/jonot.py" osa="simulaattori"}
```

Ensimmäinen kymmenesosa asiakkaista jätetään mittaamatta. Simulointi
alkaa tyhjästä jonosta, joka ei edusta vakaata tilaa, ja tämä
*lämmittely* (*warm-up*) poistaa alun harhan. Esimerkki ajaa kolme
jonoa kolmella kuormalla ja vertaa analyyttiseen:

```{.python tiedosto="esimerkit/04-simulointi.py" osa="tapaukset"}
```

```{.tuloste tiedosto="esimerkit/04-simulointi.odotettu"}
```

Simulointi osuu teoriaan alle prosentin tarkkuudella kevyellä
kuormalla, mutta 90 %:n kuormalla eksponentiaalisilla palveluajoilla ero
on viisi prosenttia, vaikka asiakkaita on 400 000. Raskaasti kuormitetun
jonon pituus vaihtelee hitaasti, joten peräkkäiset asiakkaat ovat
voimakkaasti korreloituneita, ja tehollinen otoskoko on paljon nimellistä
pienempi. Vakiopalvelulla (M/D/1) vaihtelua on vähemmän, ja tulos on
tarkka. Luvussa 10 tämä epävarmuus mitataan toistoilla. Littlen lain
sarakkeet $L$ ja $\lambda W$ ovat lähes samat joka rivillä, kuten pitää.

## Suljettu järjestelmä

Edellä saapumiset tulivat ulkopuolelta tahdista riippumatta (*avoin*
järjestelmä). Prosessorin muistijärjestelmä on *suljettu*: ydin, jolla
on yksi hutipyyntö kesken, ei lähetä uutta ennen kuin edellinen on
palannut. Kuorma säätää itseään: kun viive kasvaa, pyyntöjä tulee
hitaammin, eikä jono kasva rajatta.

Suljetun jonoverkon tunnusluvut lasketaan *keskiarvoanalyysillä*
(*mean value analysis*, MVA). Se perustuu saapumisteoreemaan: asemalle
saapuva asiakas näkee keskimäärin saman jonon kuin verkko, jossa on yksi
asiakas vähemmän. Tästä saadaan rekursio asiakasmäärän yli:

```{.python tiedosto="esimerkit/arkki/jonot.py" osa="mva"}
```

MVA olettaa tuotemuotoisen verkon, käytännössä eksponentiaaliset
palveluajat FCFS-asemilla. Testit tarkistavat rajat: yksi asiakas ei
jonota, ja hyvin monella pullonkaula on täynnä:

```{.python tiedosto="esimerkit/testit/test_jonot.py" osa="mva"}
```

$K$ ydintä laskee keskimäärin 100 ns pyyntöjen välissä, väylä ja
DRAM-käyttö vievät 44 ns ilman jonoa, ja muistiohjain palvelee pyynnön
10 ns:ssa yksi kerrallaan:

```{.python tiedosto="esimerkit/04-mva.py" osa="parametrit"}
```

```{.python tiedosto="esimerkit/04-mva.py" osa="laskenta"}
```

```{.tuloste tiedosto="esimerkit/04-mva.odotettu"}
```

Yläraja-sarake on asymptoottinen raja: kaista on enintään $K$ kertaa
yhden ytimen kaista ilman jonoa, ja enintään pullonkaulan kapasiteetti
$1/S$. Rajojen leikkauskohta $K^* = (Z + S_{\text{yht}})/S$ on noin 15
ydintä: siitä eteenpäin lisäytimet vain pidentävät jonoa. 32 ytimellä
ohjain on täynnä, ja jokainen pyyntö odottaa keskimäärin 166 ns
jonossa. Luvussa 5 sama järjestelmä simuloidaan SystemC:llä, ja MVA:n
ennustetta verrataan siihen.

## Käytännössä

- **Littlen laki ensin.** Se pätee aina, ja sillä voi tarkistaa minkä
  tahansa mittauksen tai simuloinnin johdonmukaisuuden: jos $L$,
  $\lambda$ ja $W$ eivät täsmää, jokin on mitattu väärin.
- **Mitoita jonon polven alle.** Viive kasvaa käyttöasteen mukana kuten
  $1/(1-\rho)$. Kun resurssin käyttöaste on yli 80 %, pieni kuorman
  kasvu tuo suuren viiveen kasvun.
- **Avoin vai suljettu?** Verkkoliikenne ja palvelinpyynnöt ovat avoimia,
  prosessorin muistipyynnöt yleensä suljettuja. Väärä malli ennustaa
  kuormitetun tilan väärin: avoin malli räjähtää, suljettu tasaantuu.
- **Lämmittele ja toista.** Simuloinnin alku ei ole vakaa tila, ja
  raskaalla kuormalla yksittäinen ajo voi poiketa prosentteja.
  Hylkää alku ja aja eri siemenillä (luku 10).

## Itsearviointi

- Osaat soveltaa Littlen lakia mihin tahansa järjestelmään, jonka rajat
  osaat määritellä.
- Osaat laskea M/M/1-, M/D/1- ja M/M/c-jonon viipymän ja selittää,
  miksi palveluajan vaihtelu kasvattaa jonotusta.
- Osaat kirjoittaa tapahtumapohjaisen jonosimulaattorin ja tarkistaa
  sen analyyttisillä tuloksilla.
- Osaat laskea suljetun järjestelmän läpäisyn ja viiveen MVA:lla ja
  sen asymptoottiset rajat.
