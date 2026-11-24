# Salaisuuksien hallinta tuotannossa

Palvelut tarvitsevat salaisuuksia: tietokantojen tunnuksia,
kolmansien osapuolten API-avaimia ja salausavaimia. Taidossa
*Tietoturva kehitystyössä* käsiteltiin, miten salaisuudet pidetään
poissa koodista ja kehitysympäristöistä. Tässä luvussa katsotaan,
mistä tuotantopalvelu saa ne ja miten ne suojataan levossa.

## Salaisuusvarasto

Salaisuusvarasto (Vault, pilvien Secrets Manager -palvelut, OpenBao)
on palvelu, jolta muut palvelut hakevat salaisuutensa ajon aikana.
Sen tärkeimmät ominaisuudet:

- **Pääsy identiteetin mukaan.** Palvelu todentaa itsensä
  työkuormansa identiteetillä (luvut 3–4), ja varasto antaa vain ne
  salaisuudet, joihin sillä on oikeus.
- **Auditointi.** Jokainen luku kirjataan: tiedetään, kuka luki mitä
  ja milloin.
- **Kierto ja vuokrat.** Salaisuuksilla on versiot ja elinikä.

Esimerkin varasto antaa salaisuuden vain, jos identiteetillä on
oikeus polkuun:

```{.java tiedosto="esimerkit/salaisuudet/src/main/java/fi/tutoriaalit/palveluturva/salaisuudet/Salaisuusvarasto.java" osa="staattinen"}
```

```{.java tiedosto="esimerkit/salaisuudet/src/test/java/fi/tutoriaalit/palveluturva/salaisuudet/SalaisuudetTest.java" osa="luvat"}
```

**Alkusalaisuuden ongelma** (*secret zero*): jos palvelu todentaa
itsensä varastolle salasanalla, se salasana on taas salaisuus, joka
pitää toimittaa jotenkin. Työkuormien identiteetit ratkaisevat
ongelman: alusta todentaa palvelun (Kubernetesin palvelutilin token,
pilven instanssin identiteetti, SPIFFE), eikä alkusalaisuutta ole.

**Ympäristömuuttujat** ovat yleinen tapa antaa salaisuudet
konteille. Ne ovat parempia kuin koodi, mutta ne näkyvät prosessin
tiedoissa (`/proc/<pid>/environ`), periytyvät aliprosesseille,
tulostuvat virheraporteissa ja konttien tarkastelussa. Tiedostoon
liitetty salaisuus (Kubernetesin Secret taltiona) tai suora haku
varastosta ovat turvallisempia.

## Avainpalvelu ja kirjekuorisalaus

Tietokantaan tallennettavat arkaluonteiset tiedot (maksutiedot,
henkilötunnukset) salataan sovelluksessa ennen tallennusta.
Avainpalvelu (KMS) hallitsee pääavaimia, jotka eivät koskaan poistu
siitä. Sovellus pyytää palvelulta datan avaimen, salaa datan sillä
itse ja tallentaa datan rinnalle vain kääreen eli pääavaimella
salatun datan avaimen. Tämä on *kirjekuorisalaus* (*envelope
encryption*).

```{.java tiedosto="esimerkit/salaisuudet/src/main/java/fi/tutoriaalit/palveluturva/salaisuudet/Avainpalvelu.java" osa="rajapinta"}
```

```{.java tiedosto="esimerkit/salaisuudet/src/main/java/fi/tutoriaalit/palveluturva/salaisuudet/Avainpalvelu.java" osa="kaari"}
```

```{.java tiedosto="esimerkit/salaisuudet/src/main/java/fi/tutoriaalit/palveluturva/salaisuudet/Kirjekuori.java" osa="kirjekuori"}
```

Miksi ei salata kaikkea suoraan avainpalvelussa? Avainpalvelu on
verkkopalvelu: jokainen kutsu maksaa millisekunteja ja usein rahaa,
ja sillä on kutsurajat. Kirjekuorisalauksessa avainpalvelua kutsutaan
kerran datan avainta kohti, ja itse data salataan paikallisesti.

**Konteksti** (AWS:ssä *encryption context*, Google Cloud KMS:ssä
*additional authenticated data*) sidotaan kääreeseen ja dataan AEAD:n
lisädatana. Asiakkaan 42 kirjekuori ei aukea asiakkaan 43 rivillä,
joten tietokantaan kirjoitusoikeuden saanut hyökkääjä ei voi siirtää
salattuja arvoja riviltä toiselle:

```{.java tiedosto="esimerkit/salaisuudet/src/test/java/fi/tutoriaalit/palveluturva/salaisuudet/SalaisuudetTest.java" osa="kirjekuoriTesti"}
```

## Pääavaimen kierto

Pääavain kierretään luomalla siitä uusi versio. Vanhoja versioita ei
poisteta heti, koska niillä käärittyjä avaimia on yhä tallessa:

```{.java tiedosto="esimerkit/salaisuudet/src/main/java/fi/tutoriaalit/palveluturva/salaisuudet/Avainpalvelu.java" osa="kierto"}
```

Kierron jälkeen kääreet voidaan kääriä uudelleen taustatyönä. Data ei
muutu, vain muutaman kymmenen tavun kääre vaihtuu. Kun kaikki on
kääritty uudelleen, vanha versio poistetaan:

```{.java tiedosto="esimerkit/salaisuudet/src/test/java/fi/tutoriaalit/palveluturva/salaisuudet/SalaisuudetTest.java" osa="kiertoTesti"}
```

Version poistolla on tarkoituksellinen käyttö: *kryptografinen
tuhoaminen* (*crypto-shredding*). Kun asiakkaan tiedoille on oma
pääavain tai datan avain, sen poisto tekee tiedot lukukelvottomiksi
kaikkialla, myös varmuuskopioissa. Tämä on usein ainoa käytännöllinen
tapa toteuttaa poistopyyntö tiedoille, joita on kopioitu moneen
paikkaan.

## Käytännössä

- **Salaisuus haetaan ajon aikana identiteetillä.** Ei koodissa, ei
  kuvassa, ei mieluiten ympäristömuuttujassa.
- **Kirjekuorisalaus ja konteksti.** Arkaluonteinen data salataan
  sovelluksessa, ja konteksti sitoo salatun arvon paikkaansa.
- **Erota avainten käyttäjä ja ylläpitäjä.** Palvelu saa käyttää
  avainta salaukseen ja purkuun, mutta ei poistaa eikä viedä sitä.
  Ylläpitäjä saa hallita avainta, mutta ei purkaa dataa.
- **Kierrä säännöllisesti ja automaattisesti.** Kierto, jota ei
  tehdä, ei toimi silloin kun avain vuotaa.
- **Varmuuskopio ja avain eri paikkoihin.** Varmuuskopio, jonka
  vieressä on purkuavain, ei ole salattu.

## Itsearviointi

- Osaat kuvata salaisuusvaraston roolin ja ratkaista alkusalaisuuden
  ongelman työkuormien identiteeteillä.
- Osaat toteuttaa kirjekuorisalauksen ja perustella kontekstin
  sitomisen.
- Osaat kiertää pääavaimen ja kääriä datan avaimet uudelleen ilman,
  että dataa salataan uudelleen.
- Osaat selittää kryptografisen tuhoamisen ja sen käyttötapaukset.
