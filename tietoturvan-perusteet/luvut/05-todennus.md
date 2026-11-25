# Todennus

**Todennus** (*authentication*) vastaa kysymykseen "kuka olet?".
**Valtuutus** (*authorization*) vastaa kysymykseen "mitä saat tehdä?"
ja on seuraavan luvun aihe. Ne sekoitetaan usein, ja moni vakava
haavoittuvuus syntyy, kun todennettu käyttäjä oletetaan valtuutetuksi
kaikkeen.

## Todennuksen tekijät

Todennus perustuu yhteen tai useampaan tekijään:

| Tekijä | Esimerkkejä | Heikkous |
|--------|-------------|----------|
| jotain mitä tiedät | salasana, PIN | arvattavissa, kalasteltavissa, uudelleenkäytetty |
| jotain mitä sinulla on | puhelin, turva-avain, älykortti | voi kadota tai varastaa |
| jotain mitä olet | sormenjälki, kasvot | ei vaihdettavissa, jos vuotaa |

**Monivaiheinen tunnistus** (MFA, *multi-factor authentication*)
yhdistää eri tekijöitä, jolloin yhden vuoto ei riitä. Kaksi salasanaa
ei ole monivaiheinen tunnistus, koska ne ovat samaa tekijää.

MFA-menetelmät eroavat toisistaan merkittävästi:

- **Tekstiviestikoodi** on heikoin: numeron voi kaapata operaattorin
  kautta (SIM-vaihto), ja koodin voi kalastella.
- **Sovelluksen kertakäyttökoodi** (TOTP) on parempi, mutta sekin
  voidaan kalastella: käyttäjä kirjoittaa koodin väärennetylle
  sivulle, ja hyökkääjä käyttää sen heti.
- **Push-hyväksyntä** on altis väsytykselle: hyökkääjä lähettää
  hyväksyntäpyyntöjä, kunnes käyttäjä painaa "hyväksy" päästäkseen
  niistä eroon. Torjuntana numeron täsmäytys: käyttäjä kirjoittaa
  sovellukseen kirjautumissivulla näkyvän numeron.
- **Pääsyavaimet ja turva-avaimet** (FIDO2, WebAuthn) kestävät
  kalastelua, koska allekirjoitus sidotaan palvelun osoitteeseen.
  Väärennetty sivu ei saa kelvollista vastausta. Tämä on nykyinen
  suositus (taito *Web-sovellusten tietoturva*).

## Salasanat

NISTin ohje SP 800-63B (versio 4, 2025) kokoaa nykyiset salasanakäytännöt, jotka
kumoavat monta vanhaa tapaa:

- **Pituus ennen monimutkaisuutta.** Ainoana tekijänä käytettävä
  salasana on vähintään 15 merkkiä, MFA:n osana vähintään 8; pitkät
  salalauseet sallitaan. Pakollisia merkkiluokkia ("iso
  kirjain, numero, erikoismerkki") ei vaadita, koska ne tuottavat
  ennustettavia salasanoja (`Kesä2026!`).
- **Ei pakotettua vaihtoa** määräajoin, vain kun on syytä epäillä
  vuotoa.
- **Vuotaneiden salasanojen esto.** Uusi salasana tarkistetaan
  tunnettujen vuotaneiden ja yleisten salasanojen listaa vasten.
- **Salasananhallinta sallitaan:** liittäminen leikepöydältä ei saa
  olla estetty.

Tallennus tapahtuu hitaalla, suolatulla tiivisteellä (luku
*Kryptografia käyttäjän näkökulmasta*).

## Arvaushyökkäysten rajoittaminen

Verkon yli tehtävät arvaukset on rajoitettava. Pysyvä lukitus
viiden virheen jälkeen on huono ratkaisu, koska se antaa hyökkääjälle
keinon lukita kenen tahansa tili. Parempi on kasvava viive:

```{.python tiedosto="esimerkit/05-yritykset.py" osa="rajoitin"}
```

```{.tuloste tiedosto="esimerkit/05-yritykset.odotettu"}
```

Tuhannesta yrityksestä vain kaksitoista ehtii tarkistettavaksi, ja
viive kasvaa eksponentiaalisesti. Tilikohtainen rajoitus ei kuitenkaan
pysäytä **salasanaruiskutusta** (*password spraying*), jossa hyökkääjä
kokeilee yhtä yleistä salasanaa tuhansiin tileihin. Siksi tarvitaan
myös osoitekohtaiset rajat ja havaitseminen (luku *Lokitus,
havaitseminen ja poikkeamat*).

## Kertakäyttökoodit

TOTP-koodi (*time-based one-time password*, RFC 6238) lasketaan
jaetusta avaimesta ja kellonajasta. Sovellus ja palvelin laskevat
saman koodin 30 sekunnin jaksoissa ilman verkkoyhteyttä:

```{.python tiedosto="esimerkit/05-totp.py" osa="totp"}
```

Tarkistuksessa on kaksi tietoturvayksityiskohtaa. Kellot eivät ole
täsmälleen samassa ajassa, joten myös viereiset jaksot hyväksytään.
Lisäksi kerran käytettyä koodia ei hyväksytä uudelleen, jotta olan
yli kurkistettu tai siepattu koodi ei kelpaa toista kertaa:

```{.python tiedosto="esimerkit/05-totp.py" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/05-totp.odotettu"}
```

Esimerkin neljä ensimmäistä riviä tarkistavat toteutuksen standardin
testivektoreita vasten. Tämä on hyvä tapa kaikessa kryptografiassa:
oma toteutus, joka "näyttää toimivan", voi tuottaa vääriä tuloksia.

## Istunnot

HTTP on tilaton, joten kirjautumisen jälkeen palvelin antaa
**istuntotunnisteen**, joka lähetetään jokaisen pyynnön mukana
(tavallisesti evästeessä). Tunniste on yhtä arvokas kuin salasana:
sen haltija on kirjautunut käyttäjä. Siksi

- tunniste on pitkä ja satunnainen (`secrets`, vähintään 128 bittiä),
- se vanhenee sekä käyttämättömänä että enimmäisajan jälkeen,
- se vaihdetaan aina, kun oikeudet muuttuvat (kirjautuminen,
  oikeuksien korotus),
- uloskirjautuminen mitätöi sen palvelimella, ei vain selaimessa.

```{.python tiedosto="esimerkit/05-istunnot.py" osa="istunnot"}
```

```{.tuloste tiedosto="esimerkit/05-istunnot.odotettu"}
```

Tunnisteen vaihto kirjautuessa torjuu **istunnon kiinnityksen**
(*session fixation*): hyökkääjä hankkii anonyymin istunnon ja saa uhrin
käyttämään sitä esimerkiksi linkin kautta. Jos tunniste ei vaihdu,
hyökkääjällä on uhrin kirjautumisen jälkeen kirjautunut istunto.
Kaaviossa palvelin vaihtaa tunnisteen vaiheessa 5, joten hyökkääjän
tuntema tunniste lakkaa kelpaamasta. Esimerkin tulosteen ensimmäinen
rivi on kaavion vaihe 7:

```{.dot otsikko="Istunnon kiinnitys ja sen torjunta: tunniste vaihtuu kirjautuessa."}
digraph {
  nodesep=0.2; ranksep=0.3;
  node [shape=point, width=0.04, color="#5B6B70"];
  edge [arrowhead=none, style=dashed, color="#B8C4C8", weight=100];
  t0 [shape=box, width=1.0, label="hyökkääjä"];
  t0 -> t0_0 -> t0_1 -> t0_2 -> t0_3 -> t0_4 -> t0_5 -> t0_6 -> t0_7;
  t1 [shape=box, width=1.0, label="uhri"];
  t1 -> t1_0 -> t1_1 -> t1_2 -> t1_3 -> t1_4 -> t1_5 -> t1_6 -> t1_7;
  t2 [shape=box, width=1.0, label="palvelin"];
  t2 -> t2_0 -> t2_1 -> t2_2 -> t2_3 -> t2_4 -> t2_5 -> t2_6 -> t2_7;
  {rank=same; t0 -> t1 -> t2 [style=invis, weight=1];}
  {rank=same; t0_0; t1_0; t2_0;}
  {rank=same; t0_1; t1_1; t2_1;}
  {rank=same; t0_2; t1_2; t2_2;}
  {rank=same; t0_3; t1_3; t2_3;}
  {rank=same; t0_4; t1_4; t2_4;}
  {rank=same; t0_5; t1_5; t2_5;}
  {rank=same; t0_6; t1_6; t2_6;}
  {rank=same; t0_7; t1_7; t2_7;}
  edge [style=solid, arrowhead=normal, color="#1F2A2E", constraint=false, weight=1];
  t0_0 -> t2_1 [label="1. avaa kirjautumissivun"];
  t2_1 -> t0_2 [label="2. anonyymi istunto X"];
  t0_2 -> t1_3 [label="3. linkki, jossa istunto X"];
  t1_3 -> t2_4 [label="4. kirjautuu istunnossa X"];
  t2_4 -> t1_5 [label="5. uusi tunniste Y, X mitätöidään"];
  t0_5 -> t2_6 [label="6. pyyntö tunnisteella X"];
  t2_6 -> t0_7 [label="7. hylätty: X ei ole voimassa"];
}
```

Evästeiden suojausmääreet (`Secure`, `HttpOnly`, `SameSite`) ja
tokenipohjaiset istunnot, kuten JWT, käsitellään taidossa
*Web-sovellusten tietoturva*.

## Käytännössä

- **Älä rakenna kirjautumista itse, jos voit välttää sen.** Kehysten
  valmiit toteutukset ja kirjautumispalvelut (OpenID Connect) ovat
  testatumpia kuin oma koodi. Ymmärrä silti, mitä ne tekevät.
- **Tarjoa kalastelua kestävä MFA.** Pääsyavaimet ja FIDO2-avaimet
  ensisijaisesti, TOTP varalla, tekstiviesti vain viimeisenä keinona.
- **Samat virheilmoitukset.** "Väärä käyttäjätunnus tai salasana", ei
  "käyttäjää ei ole". Sama koskee salasanan palautusta: vastaus ei saa
  paljastaa, onko osoite rekisterissä.
- **Rajoita, älä lukitse.** Kasvava viive tilikohtaisesti,
  nopeusrajoitus osoitekohtaisesti ja hälytys poikkeavasta määrästä.
- **Salasanan palautus on kirjautuminen.** Palautuslinkki on
  kertakäyttöinen, lyhytikäinen ja satunnainen, ja sen käyttö
  mitätöi muut istunnot.
- **Kirjaa todennustapahtumat.** Onnistuneet ja epäonnistuneet
  kirjautumiset, MFA-muutokset ja salasanan vaihdot ovat
  tutkinnan tärkein lähde.

## Itsearviointi

- Osaat erottaa todennuksen ja valtuutuksen ja kertoa, mihin
  kumpaakin tarvitaan.
- Osaat vertailla MFA-menetelmiä kalastelun ja väsytyksen kestävyyden
  kannalta.
- Osaat toteuttaa istunnonhallinnan, joka vanhentaa tunnisteet ja
  torjuu istunnon kiinnityksen.
- Osaat suunnitella arvaushyökkäysten rajoituksen, joka ei mahdollista
  tilien lukitsemista palvelunestona.
