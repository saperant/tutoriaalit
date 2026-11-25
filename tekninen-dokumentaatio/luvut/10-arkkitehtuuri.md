# Arkkitehtuurin kuvaus

Koodista näkee, mitä ohjelma tekee. Siitä ei näe, mistä osista
järjestelmä koostuu, miksi osat on jaettu näin eikä mitä vaihtoehtoja
harkittiin. Arkkitehtuurin kuvaus on se dokumentaation osa, jota ei
voi generoida, ja siksi sen pitää olla lyhyt.

## Kenelle ja kuinka paljon

Arkkitehtuurikuvauksen lukija on uusi kehittäjä, naapuritiimin
integroija tai kirjoittaja itse vuoden kuluttua. Hän haluaa kartan:
riittävän tarkan suunnistamiseen, ei jokaista polkua. Kuvaus, joka
toistaa koodin rakenteen luokka luokalta, vanhenee ensimmäisessä
refaktoroinnissa. Kuvaus, joka kertoo järjestelmän osat, niiden
vastuut ja keskeiset päätökset, pysyy totena vuosia.

## C4: neljä tarkkuustasoa

Simon Brownin C4-malli jakaa kuvauksen tasoihin kuten kartat
mittakaavoihin. Jokaisella tasolla on oma lukijansa:

| Taso | Näyttää | Lukija |
|---------------|----------------------------------------|---------------------|
| 1 konteksti | järjestelmän, käyttäjät ja naapurijärjestelmät | kuka tahansa |
| 2 kontit | ajettavat osat: sovellukset, tietokannat, jonot | kehittäjät, ylläpito |
| 3 komponentit | yhden kontin sisäiset osat | kontin kehittäjät |
| 4 koodi | luokat ja funktiot | harvoin piirretään |

C4:n *kontti* on erikseen ajettava tai käyttöönotettava osa
(palveluprosessi, tietokanta, selainsovellus), ei Docker-kontti.
Kontekstikaavio on johdannossa. Sääasemapalvelun kontit:

```{.dot tiedosto="esimerkit/kaaviot/c4-kontit.dot" otsikko="C4-taso 2: sääasemapalvelun kontit"}
```

Kaavion säännöt ovat tärkeämpiä kuin merkintätapa. Jokaisessa
laatikossa on nimi, tyyppi tai tekniikka hakasulkeissa ja vastuu
yhdellä virkkeellä. Jokaisella nuolella on suunta ja teksti, joka
kertoo, mitä sitä pitkin kulkee ja millä protokollalla. Nimetön nuoli
kahden nimettömän laatikon välillä ei kerro mitään.

Tasot 1 ja 2 piirretään käsin, koska niiden tieto ei ole koodissa.
Taso 3 kannattaa tuottaa koodista, jos se ylipäätään piirretään
(luku 11), ja taso 4 jätetään kehitysympäristön tehtäväksi.

## Runko: arc42

Kaaviot tarvitsevat ympärilleen tekstin. arc42 on arkkitehtuuridokumentin
valmis runko, kaksitoista otsikkoa, joista tärkeimmät ovat:

| Osio | Kysymys, johon se vastaa |
|--------------------------|--------------------------------------------|
| tavoitteet ja sidosryhmät | Mitä varten järjestelmä on ja kenelle? |
| reunaehdot | Mitkä asiat on annettu eikä niistä päätetä? |
| konteksti | Mihin järjestelmä rajautuu? (C4-taso 1) |
| ratkaisustrategia | Mitkä ovat keskeiset valinnat? |
| rakenne | Mistä osista se koostuu? (C4-tasot 2–3) |
| ajonaikainen näkymä | Miten osat toimivat yhdessä tärkeimmissä tapauksissa? |
| käyttöönotto | Missä osat ajetaan? |
| läpileikkaavat asiat | Miten lokit, virheet ja tietoturva hoidetaan? |
| päätökset | Miksi näin? (päätösloki) |
| laatuvaatimukset | Mitä ”riittävän hyvä” tarkoittaa? |
| riskit ja tekninen velka | Mikä voi mennä vikaan? |
| sanasto | Mitä termit tarkoittavat? |

Rungon arvo on siinä, että se muistuttaa kysymyksistä, jotka
unohtuvat, ja että lukija löytää saman asian samasta paikasta
projektista toiseen. Jokaista otsikkoa ei tarvitse täyttää: tyhjä
osio poistetaan, eikä sitä täytetä täytteellä.

## Laatuvaatimukset skenaarioina

”Järjestelmän pitää olla nopea ja luotettava” ei ole vaatimus, koska
sitä ei voi todeta täyttyneeksi. Laatuvaatimus kirjoitetaan
skenaarioksi: mitä tapahtuu, missä tilanteessa ja mikä on mitattava
vaste.

| Ominaisuus | Heräte | Vaste ja mittari |
|---------------|----------------------------------|----------------------------------|
| suorituskyky | tutkija hakee aseman yhteenvedon | vastaus alle 200 ms, kun lukemia on vuoden ajalta |
| saatavuus | tietokantapalvelin kaatuu | asemat puskuroivat; lukemia ei katoa 24 tunnin katkossa |
| muunneltavuus | asemaan lisätään tuulianturi | uusi kenttä käyttöön yhden tiimin työllä viikossa |
| käytettävyys | asema lähettää virheellisen rivin | vastaus nimeää virheellisen kentän |

Skenaario on samalla testin ja hälytyksen määrittely, ja se
perustelee arkkitehtuuripäätökset: 24 tunnin puskuri asemassa on
olemassa toisen rivin takia.

## Päätösloki

Arkkitehtuuripäätös (*architecture decision record*, ADR) on lyhyt
dokumentti yhdestä päätöksestä. Michael Nygardin alkuperäinen malli on
kolme osiota:

```{.markdown tiedosto="esimerkit/adr/malli.md"}
```

Päätökset numeroidaan ja säilytetään repositoriossa. Olennaista on,
että päätöstä ei muokata jälkikäteen. Kun tilanne muuttuu,
kirjoitetaan uusi päätös, joka korvaa vanhan, ja vanhan tilaksi
merkitään *korvattu*:

```{.dot tiedosto="esimerkit/kaaviot/adr-tilat.dot" otsikko="Arkkitehtuuripäätöksen tilat" leveys="70%"}
```

Näin loki kertoo myös historian. Sääasemapalvelu tallensi lukemat
ensin SQLiteen ja siirtyi sitten PostgreSQL:ään:

```{.markdown tiedosto="esimerkit/adr/0003-tallennus-postgresqliin.md"}
```

Tausta kertoo mitatun ongelman, päätös on yksi virke aktiivissa, ja
seuraukset luettelevat myös haitat ja hylätyn vaihtoehdon
perusteluineen. Vuoden kuluttua joku ehdottaa aikasarjatietokantaa, ja
vastaus on valmiina: sitä harkittiin, ja tässä on syy, miksi sitä ei
valittu, sekä luku, jonka muuttuessa asia kannattaa arvioida
uudelleen.

Koska päätökset ovat rakenteisia tiedostoja, niiden rakenteen voi
tarkistaa. Esimerkkien tarkistin varmistaa numeroinnin, tilan,
pakolliset osiot ja sen, että korvaus on kirjattu molempiin
päätöksiin:

```{.python tiedosto="esimerkit/tyokalut/adr.py" osa="tarkista"}
```

Sama työkalu tulostaa hakemiston:

```{.tuloste tiedosto="esimerkit/adr/hakemisto.odotettu"}
```

Päätös kirjataan, kun valinta on kallis perua, vaihtoehtoja oli
oikeasti tai joku kysyy vuoden kuluttua miksi. Kirjaston valinta
yhteen tiedostoon ei tarvitse päätöstä; tietokannan, viestimuodon tai
palvelujaon valinta tarvitsee. Taito *Palveluarkkitehtuurit* käyttää
päätöslokia palvelujaon perusteluun.

## Käytännössä

- **Aloita kontekstikaaviosta.** Jos järjestelmän rajaa ja naapureita
  ei saa piirrettyä, tarkemmat kaaviot eivät auta.
- **Kuvaa vähemmän, pidä ajan tasalla.** Kaksi oikeaa kaaviota ja
  viisi päätöstä on parempi kuin kattava kuvaus, johon ei luoteta.
- **Päätös kirjataan päätöshetkellä.** Jälkikäteen kirjoitettu tausta
  on arvailua, ja hylätyt vaihtoehdot on unohdettu.
- **Kirjoita haitat.** Päätös ilman haittoja on mainos. Haitat ovat
  se tieto, jota seuraava päättäjä tarvitsee.
- **Arkkitehtuurikuvaus repositorioon.** Sama katselmointi, samat
  tarkistukset ja sama historia kuin koodilla.
- **Linkitä koodista päätökseen.** Kommentti ”ks. ADR 0003” kertoo,
  miksi outo ratkaisu on tahallinen.

## Itsearviointi

- Osaat piirtää järjestelmästä C4-mallin konteksti- ja
  konttikaavion ja kertoa, mitä kummallekin tasolle kuuluu.
- Osaat kirjoittaa laatuvaatimuksen mitattavana skenaariona.
- Osaat kirjoittaa arkkitehtuuripäätöksen taustoineen, seurauksineen
  ja hylättyine vaihtoehtoineen.
- Osaat selittää, miksi päätöstä ei muokata vaan se korvataan
  uudella.
