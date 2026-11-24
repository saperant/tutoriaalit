# Monte Carlo -menetelmät

Monte Carlo -menetelmä arvioi luvun satunnaisotoksella: todennäköisyys
on osumien osuus ja integraali satunnaispisteiden keskiarvo. Menetelmä
toimii, kun analyyttistä ratkaisua ei ole, ja sen virhe pienenee
ulottuvuudesta riippumatta kuten $1/\sqrt{n}$.

## Piin arvio ja virheen pieneneminen

Neljäsosaympyrän ala on $\pi/4$. Kun pisteitä arvotaan
yksikköneliöön, ympyrän sisään osuvien osuus arvioi alaa. Toistetaan
arvio 20 kertaa kullakin otoskoolla ja lasketaan virheen neliöllinen
keskiarvo:

```{.python tiedosto="esimerkit/10-pii.py" osa="pii"}
```

```{.tuloste tiedosto="esimerkit/10-pii.odotettu"}
```

Sarake *virhe·√n* pysyy vakiona: virhe on verrannollinen lukuun
$1/\sqrt{n}$. Yksi lisädesimaali vaatii sata kertaa enemmän pisteitä.
Monte Carlo on siksi hyvä karkeisiin arvioihin ja huono tarkkoihin.

## Integrointi ja keskivirhe

Integraali $\int_0^1 f(x)\,dx$ on $f(U)$:n odotusarvo, kun $U$ on
tasajakautunut. Arvion keskivirhe on $s/\sqrt{n}$, jossa $s$ on
otoksen keskihajonta, joten Monte Carlo kertoo samalla oman
tarkkuutensa:

```{.python tiedosto="esimerkit/10-integraali.py" osa="perus"}
```

Varianssia voi pienentää. *Ositettu otanta* jakaa välin osiin ja
arpoo kuhunkin saman määrän pisteitä, jolloin pisteet eivät kasaudu.
Samalla pistemäärällä keskivirhe pienenee tässä sadasosaan:

```{.python tiedosto="esimerkit/10-integraali.py" osa="ositettu"}
```

## Korkeat ulottuvuudet

Kuutiohila tarvitsee $d$ ulottuvuudessa $k^d$ pistettä, mikä on
mahdotonta jo kymmenessä ulottuvuudessa. Monte Carlon virhe riippuu
vain pisteiden määrästä. Pallon tilavuuden arvio havainnollistaa myös
rajoituksen: kun osuvien osuus pienenee, suhteellinen virhe kasvaa.

```{.python tiedosto="esimerkit/10-integraali.py" osa="ulottuvuus"}
```

```{.tuloste tiedosto="esimerkit/10-integraali.odotettu"}
```

Kymmenulotteisessa kuutiossa pallon sisään osuu vain 0,25 % pisteistä,
joten tarkkuus jää heikoksi. Harvinaisten tapahtumien
todennäköisyyksiin tarvitaan *tärkeysotantaa* (*importance sampling*),
joka arpoo pisteitä tiheämmin tärkeille alueille ja korjaa painoilla.
Säteenseuranta käyttää samaa ideaa valon polkujen otantaan (taito
*Säteenseuranta*).

## Käytännössä

- **Ilmoita keskivirhe.** Monte Carlo -arvio ilman epävarmuutta on
  puolikas tulos; $s/\sqrt{n}$ on ilmainen.
- **Pienennä varianssia ennen kuin lisäät pisteitä.** Ositus,
  tärkeysotanta ja vastakkaiset muuttujat parantavat tarkkuutta
  moninkertaisesti ilman lisälaskentaa.
- **Käytä Monte Carloa, kun ulottuvuuksia on paljon.** Hilat ja
  kvadratuurit ovat parempia yhdessä tai kahdessa ulottuvuudessa.
- **Simuloi harvinaiset tapahtumat varoen.** Kun tapahtuma on hyvin
  harvinainen, tavallinen otanta näkee sen vain harvoin; tarvitaan
  tärkeysotantaa tai analyyttinen arvio.

## Itsearviointi

- Osaat arvioida integraalin tai todennäköisyyden Monte Carlolla ja
  ilmoittaa sen keskivirheen.
- Osaat selittää, miksi virhe pienenee kuten $1/\sqrt{n}$, ja arvioida
  tarvittavan otoskoon.
- Osaat pienentää varianssia ositetulla otannalla ja tunnistaa,
  milloin tarvitaan tärkeysotantaa.
