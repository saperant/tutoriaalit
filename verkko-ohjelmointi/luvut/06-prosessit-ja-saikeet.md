# Moniasiakaspalvelimet: prosessit ja säikeet

Tähänastiset palvelimet ovat palvelleet yhtä asiakasta kerrallaan.
Kun ensimmäinen asiakas odottaa omaa syötettään, muut jonottavat
kuuntelujonossa. Palvelimen on siis tehtävä monta asiaa yhtä aikaa.
Siihen on kaksi perustapaa: jokainen yhteys saa oman suorituspolkunsa
(prosessin tai säikeen), jossa estävät kutsut ovat sallittuja, tai yksi
säie seuraa kaikkia yhteyksiä ja käsittelee vain valmiit (luku 7).

| Malli | Eristys | Hinta yhteyttä kohden | Jaettu tila | Esimerkkejä |
|----------------------|-------------------|----------------------|-----------------|-------------------|
| prosessi per yhteys | täysi | prosessi (`fork`) | ei, IPC tarvitaan | perinteinen inetd, OpenSSH, PostgreSQL |
| säie per yhteys | ei | säie ja pino | kaikki, lukot | Java-palvelimet, Apache worker |
| säiepooli | ei | ei luontia | kaikki, lukot | tietokantapalvelimet, Tomcat |
| tapahtumasilmukka | ei | tilarakenne | yksi säie | nginx, Redis, Node.js |

## Prosessi asiakasta kohden

Malli on vanhin ja yksinkertaisin. Palvelin hyväksyy yhteyden ja
haarauttaa lapsen. Lapsi palvelee yhteyden ja lopettaa, ja vanhempi
palaa heti hyväksymään seuraavaa. Kummankin on suljettava se kuvaaja,
jota se ei tarvitse: lapsi kuuntelijan ja vanhempi yhteyden. Muuten
yhteys ei sulkeudu, kun lapsi lopettaa, koska vanhemmalla on yhä
viittaus siihen.

```{.c tiedosto="esimerkit/06-prosessit.c" osa="palvelin"}
```

Palvelu itse on estävää koodia, ja se on mallin vahvuus. Protokollan
voi kirjoittaa suoraviivaisesti, ja stdio puskuroi rivit. Lukemiseen
ja kirjoittamiseen tarvitaan erilliset `FILE`-oliot, koska yhteinen
puskuri sotkisi suunnat:

```{.c tiedosto="esimerkit/06-prosessit.c" osa="palvele"}
```

Tässä on tavallinen ansa. Muotoilu `fscanf(f, "NELIO %ld\n", &x)`
näyttää lukevan yhden rivin, mutta välilyöntimerkki `\n` muotoilussa
ohittaa *kaikki* tyhjät merkit ja odottaa ensimmäistä ei-tyhjää. Se
jää siis odottamaan seuraavaa riviä, jota asiakas ei lähetä ennen
vastausta, ja molemmat jumiutuvat. `fgets` ja `sscanf` lukevat tasan
yhden rivin.

Päättynyt lapsi jää *zombiksi*, kunnes vanhempi korjaa sen
`waitpid`-kutsulla. Palvelin ei voi odottaa estävästi, koska se on
`accept`-kutsussa, joten korjaus tehdään `SIGCHLD`-käsittelijässä.
Käsittelijä kutsuu `waitpid`-funktiota silmukassa, koska signaalit
eivät jonoudu: kaksi lähes samanaikaista lopetusta voi tuottaa yhden
signaalin. Se myös säilyttää `errno`n, koska keskeytetty pääohjelma
saattaa juuri tutkia sitä:

```{.c tiedosto="esimerkit/06-prosessit.c" osa="korjaa"}
```

`SA_RESTART` jatkaa signaalin keskeyttämää `accept`-kutsua
automaattisesti. Ilman sitä `accept` palaisi virheellä `EINTR`.
Lopuksi palvelin odottaa kaikkien lasten päättymistä. Signaali
estetään ennen tarkistusta, ja `sigsuspend` sallii sen atomisesti
odottaessaan. Muuten signaali voisi tulla tarkistuksen ja odotuksen
välissä, ja palvelin odottaisi ikuisesti.

```{.tuloste tiedosto="esimerkit/06-prosessit.odotettu"}
```

Prosessimallin hinta on `fork`-kutsu yhteyttä kohden: sivutaulun
kopio, copy-on-write-virheet ja prosessin vaihdot. Satoja yhteyksiä
sekunnissa malli kestää hyvin, mutta kymmeniä tuhansia samanaikaisia
yhteyksiä se ei kestä. Vastineeksi kaatuva työprosessi vie mukanaan
vain yhden yhteyden, ja työprosessin voi pudottaa vähäisemmille
oikeuksille (OpenSSH:n etuoikeuksien erottelu). Esihaarautettu malli
(Apache prefork, PostgreSQL:n yhteysprosessit) välttää haarauttamisen
hinnan pitämällä valmiita prosesseja odottamassa.

## Säie asiakasta kohden

Säie on halvempi kuin prosessi, ja säikeet jakavat muistin. Jaettu
tila on mallin hyöty ja vaara: palvelimen yhteinen data on
suojattava. Esimerkin avain–arvo-varastoa suojaa mutex:

```{.c tiedosto="esimerkit/06-saikeet.c" osa="varasto"}
```

Hyväksyjä luo jokaiselle yhteydelle irrotetun (detached) säikeen.
Irrotetun säikeen resurssit vapautuvat sen päättyessä ilman
`pthread_join`-kutsua. Kuvaaja välitetään varattuna argumenttina eikä
osoittimena hyväksyjän paikalliseen muuttujaan, jonka seuraava
kierros ylikirjoittaisi ennen kuin uusi säie ehtii lukea sen:

```{.c tiedosto="esimerkit/06-saikeet.c" osa="hyvaksy"}
```

```{.c tiedosto="esimerkit/06-saikeet.c" osa="kasittelija"}
```

Irrotettuja säikeitä ei voi liittää, joten pääsäie tietää niiden
päättymisestä vain laskurin ja ehtomuuttujan avulla. Sama rakenne
tarvitaan siistiin sammutukseen (luku 10):

```{.c tiedosto="esimerkit/06-saikeet.c" osa="odota"}
```

```{.tuloste tiedosto="esimerkit/06-saikeet.odotettu"}
```

Neljä asiakasta lisäsi yhteistä laskuria 250 kertaa kukin
rinnakkaisissa säikeissä, ja tulos on tasan 1000. Testaaja ajaa
esimerkin myös ThreadSanitizerilla. Jos lukko poistetaan, TSan
ilmoittaa kilpatilanteesta (data race), vaikka laskettu summa
sattuisikin olemaan oikein.

Säiemallin rajat ovat muisti ja vaihdot. Jokaisella säikeellä on oma
pinonsa (Linuxissa oletuksena 8 MiB virtuaalimuistia, josta vain
käytetty osa varataan), ja tuhansien säikeiden välillä vaihtelu
kuluttaa suorittimen välimuistit. Yksi säie, joka jää jumiin tai
kaatuu, voi kaataa koko palvelimen, koska eristystä ei ole.
*Säiepooli* rajaa säikeiden määrän: hyväksyjä panee yhteydet jonoon,
ja kiinteä joukko työsäikeitä ottaa niitä sieltä. Malli on luettava ja
kestää kuormaa, mutta hidas asiakas varaa työsäikeen koko yhteytensä
ajaksi.

## Hitaat asiakkaat

Estävissä malleissa jokainen avoin yhteys varaa prosessin tai säikeen,
vaikka asiakas ei tekisi mitään. Slowloris-hyökkäys käyttää tätä
hyväkseen: se avaa satoja yhteyksiä ja lähettää pyyntöjä tavu
kerrallaan minuuttien välein, kunnes palvelimen kaikki säikeet
odottavat. Torjunta vaatii aikarajat (luku 10) ja yhteyksien
enimmäismäärän. Pohjimmiltaan malli on vaihdettava sellaiseen,
jossa odottava yhteys ei varaa suorituspolkua (luku 7).

## Käytännössä

- **Sulje turhat kuvaajat haarautuksen jälkeen:** lapsi kuuntelijan,
  vanhempi yhteyden. `SOCK_CLOEXEC` ja `accept4` estävät kuvaajien
  vuotamisen `exec`-kutsun yli.
- **Korjaa lapset:** `SIGCHLD`-käsittelijä silmukalla, `WNOHANG` ja
  `errno` talteen, tai `SA_NOCLDWAIT`, jos paluuarvoja ei tarvita.
- **Välitä säikeelle omistettu argumentti:** varattu rakenne, jonka
  säie vapauttaa, ei osoitinta silmukan muuttujaan.
- **Lukitse jaettu tila ja aja ThreadSanitizer:** kilpatilanne voi
  tuottaa oikean tuloksen testissä ja väärän tuotannossa.
- **Rajaa rinnakkaisuus:** säiepooli tai yhteyksien enimmäismäärä,
  jotta kuormahuippu ei kaada palvelinta.
- **Vältä `fscanf`-muotoilun välilyöntejä verkossa:** lue rivi
  `fgets`-kutsulla ja jäsennä se `sscanf`-kutsulla.

## Itsearviointi

- Osaat kirjoittaa palvelimen, joka haarauttaa työprosessin yhteyttä
  kohden, ja korjata päättyneet lapset ilman zombeja ja kilpatilanteita.
- Osaat kirjoittaa palvelimen, joka luo säikeen yhteyttä kohden,
  välittää säikeelle omistetun argumentin ja suojata jaetun tilan.
- Osaat odottaa irrotettujen säikeiden päättymistä laskurin ja
  ehtomuuttujan avulla.
- Osaat vertailla prosessi-, säie- ja säiepoolimallia eristyksen,
  hinnan ja hitaiden asiakkaiden kannalta.
