# Kangas

Jäykkä kappale on yksi ääripää. Toinen on kappale, jonka koko tarkoitus
on muuttaa muotoaan: kangas, köysi, hiukset, hyytelö. Tällaiset
*pehmeät kappaleet* mallinnetaan hiukkasjoukkona, jonka hiukkasia
sitovat toisiinsa jouset tai rajoitteet. Tässä luvussa kangas tehdään
ensin jousilla, nähdään, miksi se ei riitä, ja korjataan asia
menetelmällä, joka on luvun 7 rajoitteiden lähisukulainen.

## Kangas hiukkasina

Kangas on ruudukko hiukkasia. Vierekkäisiä hiukkasia yhdistää *lanka*,
jolla on lepopituus. Langat ruudukon sivuilla vastustavat venymistä ja
lävistäjien langat ruutujen vinoutumista.

```{.cpp tiedosto="esimerkit/yhteinen/kangas.hpp" osa="kangas"}
```

Hiukkasella ei ole asentoa eikä hitaustensoria, joten tila on pelkkä
paikka ja nopeus. Kiinnitetty hiukkanen on käänteismassa nolla, kuten
liikkumaton kappale.

## Jouset ja jäykkyysraja

Suora tapa on tehdä jokaisesta langasta jousi: voima on jousivakio
kertaa venymä, ja voimat integroidaan puoli-implisiittisellä
Eulerilla.

```{.cpp tiedosto="esimerkit/yhteinen/kangas.hpp" osa="jouset"}
```

Oikea kangas ei juuri veny, joten jousien pitäisi olla jäykkiä.
Esimerkki ripustaa 144 hiukkasen kankaan kahdesta kulmastaan ja mittaa
suurimman venymän eri jousivakioilla:

```{.cpp tiedosto="esimerkit/11-kangas.cpp" osa="ripustus"}
```

```{.cpp tiedosto="esimerkit/11-kangas.cpp" osa="jousikoe"}
```

```{.tuloste tiedosto="esimerkit/11-kangas.odotettu" rivit="1-7"}
```

Löysillä jousilla simulaatio on vakaa, mutta kangas venyy
moninkertaiseksi. Kun jousivakiota kasvatetaan, simulaatio räjähtää
ennen kuin kangas on lähelläkään jäykkää. Syy on integraattorin
stabiilisuusraja: jousen ja massan värähtelytaajuus on
$\omega = \sqrt{k/m}$, ja eksplisiittinen menetelmä on vakaa vain, kun
$\omega\,\Delta t$ on alle noin kahden (taito *Numeeriset menetelmät*;
*jäykkä yhtälö*). Kymmenen gramman hiukkanen, johon kiinnittyy
kahdeksan lankaa, rikkoo ehdon jo jousivakiolla 32 N/m.

Askeleen lyhentäminen kahdeksasosaan siirtää rajaa, mutta jäykin
vakaa kangas venyy silti kolmanneksen, ja laskenta kahdeksankertaistuu.
Implisiittinen integraattori olisi vakaa millä tahansa jäykkyydellä,
mutta se vaatii yhtälöryhmän ratkaisun joka askeleella. Peleissä on
päädytty kolmanteen tapaan.

## Sijaintipohjainen dynamiikka

*Sijaintipohjainen dynamiikka* (*position based dynamics*, PBD) ei
laske voimia lainkaan. Lanka ei ole jousi vaan rajoite: hiukkasten
etäisyyden on oltava lepopituus. Askeleessa on kolme vaihetta:

1. Ennusta jokaisen hiukkasen uusi paikka sen nopeudesta ja
   ulkoisista voimista.
2. Siirrä hiukkasia suoraan, kunnes rajoitteet toteutuvat. Jokainen
   lanka käsitellään vuorollaan ja kierros toistetaan, kuten luvun 7
   ratkaisijassa.
3. Laske nopeus siitä, mihin hiukkanen lopulta päätyi: uusi paikka
   miinus vanha jaettuna askeleella.

```{.cpp tiedosto="esimerkit/yhteinen/kangas.hpp" osa="pbd"}
```

Kolmas vaihe on menetelmän ydin. Koska nopeus johdetaan paikoista,
rajoitteen korjaus ei voi lisätä järjestelmään energiaa samalla
tavalla kuin Baumgarten korjaus: siirto kohti sallittua tilaa on
aina myös nopeuden muutos samaan suuntaan. Menetelmä pysyy vakaana
kierrosmäärästä ja askeleen pituudesta riippumatta.

```{.cpp tiedosto="esimerkit/11-kangas.cpp" osa="pbdkoe"}
```

```{.tuloste tiedosto="esimerkit/11-kangas.odotettu" alkaen="PBD, 2 s" asti="64 kierrosta"}
```

Jäykkyys tulee kierrosten määrästä: 64 kierroksella kangas venyy
kolme prosenttia, eikä mikään määrä räjäytä simulaatiota. Energia
pienenee jokaisella asetuksella. Hinta on se, että jäykkyys riippuu
kierrosten määrästä ja askeleen pituudesta eikä ole materiaalin
ominaisuus. Menetelmän laajennus XPBD korjaa tämän antamalla
rajoitteelle *myötäävyyden* (*compliance*), jolloin jäykkyys on
fysikaalinen suure ja tulos ei riipu kierrosmäärästä.

Menetelmän edeltäjä on paikkapohjainen Verlet-integrointi, jossa
nopeutta ei tallenneta lainkaan vaan se on kahden peräkkäisen paikan
erotus. Sitä käytettiin jo 2000-luvun alun peleissä köysiin ja
räsynukkeihin.

## Törmäys on rajoite

Sijaintipohjaisessa menetelmässä törmäys ei tarvitse impulsseja.
"Hiukkanen ei saa olla pallon sisällä" on rajoite samassa silmukassa
kuin langat: sisään joutunut hiukkanen siirretään pallon pinnalle.
Kitka tehdään samoin palauttamalla pintaa koskettavaa hiukkasta
osittain kohti askeleen alkupaikkaa.

```{.cpp tiedosto="esimerkit/11-kangas.cpp" osa="pallo"}
```

```{.tuloste tiedosto="esimerkit/11-kangas.odotettu" alkaen="kangas pallon päällä"}
```

![Vapaa kangas putoaa pallon päälle ja jää roikkumaan sen
varaan.](kuvat/kangas.png){width=100%}

Hiukkaset jäävät pallon pinnalle sentin päähän, koska törmäyssäde on
asetettu hieman pallon sädettä suuremmaksi. Kangas on pinta, ja ilman
tätä varaa hiukkasten väliset kolmiot leikkaisivat pallon läpi.

Esimerkistä puuttuu kaksi asiaa, jotka tekevät oikeasta
kangassimulaatiosta vaikean: kankaan törmäys itseensä ja taipumisen
vastustus. Edellinen vaatii hiukkasten keskinäiset törmäykset ja
tilarakenteen, jälkimmäinen lisärajoitteet joka toisen hiukkasen
välille tai vierekkäisten kolmioiden väliselle kulmalle.

## Käytännössä

- **PBD on pelien oletus pehmeille kappaleille.** Kangas, köysi,
  hiukset ja pehmeät oliot tehdään lähes aina sijaintipohjaisesti,
  koska menetelmä ei räjähdä ja sen hinta on ennustettava.
- **Jäykkyys aliaskeleilla.** Yksi kierros monessa lyhyessä
  aliaskeleessa suppenee nopeammin kuin monta kierrosta yhdessä
  pitkässä askeleessa, kuten jäykillä kappaleillakin.
- **Kiinnitys on käänteismassa nolla.** Hahmon vaatteet kiinnitetään
  luurankoon liikuttamalla kiinnitettyjä hiukkasia animaation
  mukana.
- **Yksinkertaiset törmäysmuodot.** Kangas törmää hahmon kapseleihin
  ja palloihin, ei sen kolmioverkkoon.
- **Jäykät ja pehmeät erikseen.** Useimmissa peleissä kangas reagoi
  jäykkiin kappaleisiin, mutta ei työnnä niitä: kytkentä on
  yksisuuntainen, mikä pitää ratkaisijat erillään.
- **Venymän katto.** Suurin sallittu venymä (esimerkiksi 10 %)
  pakotetaan vielä ratkaisijan jälkeen, alkaen kiinnityspisteistä.
  Näin kangas ei veny, vaikka kierrokset loppuvat kesken.

## Itsearviointi

- Osaat selittää, miksi jäykkä jousi ja eksplisiittinen integraattori
  eivät sovi yhteen.
- Osaat kuvata sijaintipohjaisen dynamiikan kolme vaihetta ja
  perustella, miksi menetelmä on vakaa.
- Osaat kertoa, mistä jäykkyys sijaintipohjaisessa menetelmässä tulee
  ja mitä ongelmaa XPBD ratkaisee.
- Osaat toteuttaa törmäyksen ja kitkan sijaintirajoitteina.
