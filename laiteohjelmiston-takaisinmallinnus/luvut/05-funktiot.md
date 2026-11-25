# Funktioiden ja kirjastojen tunnistaminen

Symbolittomassa kuvassa funktioilla ei ole nimiä, vain osoitteita.
Analyysi etenee kahdessa vaiheessa: ensin löydetään funktiot, sitten
tunnistetaan, mitkä niistä ovat kirjastofunktioita tai tunnettuja
algoritmeja, jotta huomio voi keskittyä sovelluksen omaan logiikkaan.

## Funktioiden etsintä

Funktiot löytyvät seuraamalla kutsuja. Juuret ovat vektoritaulun
käsittelijät; niistä `bl`-kutsuja seuraamalla löytyvät kaikki suoraan
kutsutut funktiot. `thumb`-moduulin `tutki` tekee rekursiivisen
läpikäynnin yhden funktion sisällä, ja `etsi_funktiot` laajentaa sen
kutsupuuksi. Pelkät kutsut eivät kuitenkaan löydä funktioita, joihin
viitataan vain osoittimella (komento- ja tehtävätaulut), joten mukaan
otetaan datan funktio-osoittimet:

```{.bash tiedosto="esimerkit/05-funktiot/aja.sh" osa="kutsut"}
```

```{.tuloste tiedosto="esimerkit/05-funktiot/odotettu" osa="s1"}
```

```{.bash tiedosto="esimerkit/05-funktiot/aja.sh" osa="osoittimet"}
```

```{.tuloste tiedosto="esimerkit/05-funktiot/odotettu" osa="s2"}
```

Pelkillä kutsuilla löytyy 15 funktiota; funktio-osoittimet lisäävät
komentojen ja tehtävien käsittelijät, jolloin tulos on 46. Taulukon
`kutsujia`-sarake on hyödyllinen: paljon kutsuttu funktio (esim.
`konsoli_merkki`) on apufunktio, kutsumaton on sisääntulopiste tai vain
osoittimella käytetty.

## Kirjastofunktioiden allekirjoitukset

Osa funktioista on C-kirjaston koodia (`memcpy`, `strcmp`), joka on
sama kaikissa samalla työkaluketjulla käännetyissä ohjelmissa. Ne
tunnistaa *allekirjoituksista*: funktion ensimmäiset tavut, joista
`bl`-kutsujen kohdeosoitteet (jotka riippuvat linkityksestä) on
peitetty. Tämä on sama idea kuin IDA:n FLIRT ja Ghidran Function ID,
ja *Takaisinmallinnus* käytti sitä riisuttuihin x86-64-ohjelmiin.
Allekirjoitukset tehdään viiteohjelmasta, joka käyttää samoja funktioita
ja käännetään samalla kääntäjällä:

```{.python tiedosto="esimerkit/tyokalut/allekirjoitus.py" osa="peita"}
```

```{.bash tiedosto="esimerkit/05-funktiot/aja.sh" osa="allekirjoitukset"}
```

```{.tuloste tiedosto="esimerkit/05-funktiot/odotettu" osa="s3"}
```

Neljä kuvan funktiota tunnistuu C-kirjaston funktioiksi. Niitä ei
tarvitse tutkia tarkemmin, ja niiden tunnistus auttaa myös sovelluksen
koodia: funktio, joka kutsuu `memcpy`:tä, käsittelee puskureita.

## Algoritmit vakioista

Monet algoritmit käyttävät tunnistettavia vakioita: CRC-polynomeja,
hajautusfunktioiden alkuarvoja ja salainten kierrosvakioita. Funktion
lataama vakio kertoo usein suoraan, mitä se tekee:

```{.python tiedosto="esimerkit/tyokalut/algoritmit.py" osa="vakiot"}
```

```{.tuloste tiedosto="esimerkit/05-funktiot/odotettu" osa="s4"}
```

Kolme funktiota tunnistuu: CRC-32, CRC-16/CCITT ja XTEA-lohkosalain
(delta·32 on purkusuunnan kierrosvakio). Nyt tiedetään, että laite
laskee kahta tarkistetta ja purkaa jotain XTEA:lla; mitä se purkaa,
selviää ajamalla funktio (luku 9).

## Päättelyjen tarkistus

Oppimateriaalissa on vastausavain: laitteen ELF-tiedosto symboleineen.
Oikeassa työssä sitä ei ole, mutta tässä sillä tarkistetaan, että
löydetyt funktioiden alut ja nimeämiset osuvat oikeaan:

```{.tuloste tiedosto="esimerkit/05-funktiot/odotettu" osa="s5"}
```

Kaikki 46 löydettyä funktiota osuvat ELF:n funktiosymboleihin, ja
vakioista ja allekirjoituksista tehdyt nimeämiset ovat oikein.

## Käytännössä

- **Löydä funktiot kahdella tavalla.** Kutsupuu vektoritaulusta löytää
  suoraan kutsutut; datan funktio-osoittimet löytävät taulukoiden
  kautta kutsutut. Kumpikin tarvitaan.
- **Karsi kirjastokoodi ensin.** Allekirjoitukset tunnistavat
  `memcpy`:n ja `strcmp`:n, jotka eivät kaipaa analyysia. Tee
  allekirjoitukset omalla, samalla kääntäjällä käännetyllä
  viiteohjelmalla.
- **Tunnista algoritmit vakioista.** CRC-polynomi, salaimen kierrosvakio
  tai hajautuksen alkuarvo kertoo funktion tehtävän ennen kuin yhtään
  käskyä on luettu.
- **Puolustus:** kovakoodattu salaimen vakio ja avain ovat kuvassa
  näkyvissä. Jaettu, laitteisiin poltettu avain ei suojaa mitään, kun
  yhdenkin laitteen kuva on saatavilla (luku 9). Avaimet kuuluvat
  suojattuun avainvarastoon, eivät koodiin.

## Itsearviointi

- Osaat löytää kuvan funktiot sekä kutsupuusta että datan
  funktio-osoittimista.
- Osaat tehdä kirjastofunktioiden allekirjoitukset viiteohjelmasta ja
  tunnistaa niillä kuvan kirjastokoodin.
- Osaat tunnistaa algoritmin sen käyttämistä vakioista.
- Osaat tarkistaa päättelysi symbolitaulua vastaan, kun sellainen on
  oppimistarkoituksessa saatavilla.
