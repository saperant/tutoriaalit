# Modulaarinen monoliitti

Modulaarinen monoliitti on yksi sovellus, joka on jaettu moduuleihin
yhtä tiukasti kuin mikropalvelut: jokaisella moduulilla on julkinen
rajapinta, oma tieto ja selvät riippuvuudet. Ero mikropalveluihin on,
että rajaa valvoo testi eikä verkko. Moduulien välinen kutsu on
edelleen metodikutsu, ja muutokset voi tehdä yhdessä transaktiossa.

## Moduulin rakenne

Esimerkin kaupassa on kolme moduulia: myynti, varasto ja laskutus.
Jokainen on Java-paketti, jonka juuri on moduulin julkinen rajapinta,
ja alipaketti `sisainen` sen toteutus:

```text
kauppa/
├── myynti/
│   ├── Tilaukset.java          julkinen: tilaa()
│   ├── TilausTehty.java        julkinen tapahtuma
│   └── sisainen/TilausTaulu.java
├── varasto/
│   ├── Varasto.java            julkinen: saldo()
│   ├── SaldoEiRiita.java
│   └── sisainen/               SaldoTaulu, VarausKuuntelija
└── laskutus/
    ├── Laskut.java
    └── sisainen/               LaskuTaulu, LaskuKuuntelija
```

Javan näkyvyyssäännöt eivät riitä rajaksi. `TilausTaulu` on oltava
julkinen, jotta `Tilaukset` voi käyttää sitä alipaketista, ja silloin
myös laskutus voi käyttää sitä. Java-moduulit (JPMS) ratkaisisivat tämän
JAR-tasolla, mutta vaativat jokaisen moduulin omaksi käännösyksiköksi.
Kevyempi ja yleisempi tapa on kirjoittaa säännöt testeiksi.

## Rajat testeinä

ArchUnit lukee käännetyt luokat ja tarkistaa niiden riippuvuudet.
Kolme sääntöä riittää moduulirajoiksi:

```{.java tiedosto="esimerkit/modulaarinen/src/test/java/fi/tutoriaalit/palvelut/kauppa/ModuulirajatTest.java" osa="saannot"}
```

Ensimmäinen sääntö kieltää käyttämästä toisen moduulin sisäosia,
toinen kieltää syklit moduulien välillä ja kolmas kiinnittää
riippuvuuden suunnan: myynti ei tunne varastoa eikä laskutusta, vaan
ne tuntevat myynnin julkisen tapahtuman. Testi varmistaa myös, että
sääntö todella huomaa rikkomuksen. Testikoodin `Oikopolku` lukee
varaston taulua sen rajapinnan ohi:

```{.java tiedosto="esimerkit/modulaarinen/src/test/java/fi/tutoriaalit/palvelut/kauppa/ModuulirajatTest.java" osa="rikkomus"}
```

Sääntö kaatuu, ja virheilmoitus nimeää luokan ja riippuvuuden. Kun
säännöt ajetaan jokaisessa käännöksessä, raja ei rapistu huomaamatta.
Spring Modulith tekee saman Spring-sovelluksille valmiina: se tunnistaa
moduulit paketeista, tarkistaa rajat, piirtää moduulikaavion ja tarjoaa
moduulikohtaiset integraatiotestit.

## Tieto kuuluu moduulille

Rajat koskevat myös tietokantaa. Jokaisella moduulilla on omat
taulunsa, ja etuliite kertoo omistajan:

```{.sql tiedosto="esimerkit/modulaarinen/src/main/resources/schema.sql" osa="skeema"}
```

Moduuli ei lue toisen moduulin tauluja eikä tee liitoksia niiden yli.
Sääntö tuntuu tiukalta, kun kaikki on samassa tietokannassa, mutta se
on ehto sille, että moduulin voi myöhemmin siirtää omaksi palvelukseen:
sen tieto lähtee mukaan ilman, että muut moduulit hajoavat. Tietokannan
käyttöoikeuksilla (skeema per moduuli, oma käyttäjä) säännön voi myös
pakottaa.

## Tapahtumat moduulien välillä

Myynti ei kutsu varastoa. Se julkaisee tapahtuman siitä, mitä tapahtui,
ja jatkaa:

```{.java tiedosto="esimerkit/modulaarinen/src/main/java/fi/tutoriaalit/palvelut/kauppa/myynti/Tilaukset.java" osa="tilaukset"}
```

Varasto kuuntelee tapahtumaa. Springin `@EventListener` ajetaan
synkronisesti samassa säikeessä ja samassa transaktiossa kuin
julkaisija, joten varaus ja tilaus tallentuvat yhdessä:

```{.java tiedosto="esimerkit/modulaarinen/src/main/java/fi/tutoriaalit/palvelut/kauppa/varasto/sisainen/VarausKuuntelija.java" osa="varaus"}
```

Laskutus taas haluaa reagoida vasta, kun tilaus on varmasti
tallennettu. `@TransactionalEventListener` ajetaan oletuksena
julkaisijan transaktion onnistuneen vahvistuksen jälkeen:

```{.java tiedosto="esimerkit/modulaarinen/src/main/java/fi/tutoriaalit/palvelut/kauppa/laskutus/sisainen/LaskuKuuntelija.java" osa="lasku"}
```

`REQUIRES_NEW` on tässä välttämätön, ja sen unohtaminen on tavallinen
virhe: vahvistuksen jälkeen ajettava kuuntelija on yhä kiinni jo
päättyneessä transaktiossa, eivätkä sen kirjoitukset tallennu. Testit
näyttävät molemmat käytökset:

```{.java tiedosto="esimerkit/modulaarinen/src/test/java/fi/tutoriaalit/palvelut/kauppa/KauppaTest.java" osa="testit"}
```

Liian suuri tilaus perutaan kokonaan: varaston poikkeus kumoaa myös
tilauksen, eikä laskua synny. Tämä on monoliitin etu, jota
mikropalveluissa ei ole. Siellä sama tarvitsee sagan (luku 10).

Vahvistuksen jälkeinen kuuntelija on eri asia. Jos prosessi kaatuu
tilauksen tallennuksen ja laskun luonnin välissä, lasku jää syntymättä.
Spring Modulith ratkaisee tämän tallentamalla julkaistut tapahtumat
tauluun samassa transaktiossa (*event publication registry*) ja
toistamalla käsittelemättömät käynnistyksessä. Se on sama outbox-malli,
jota luku 10 käyttää palvelujen välillä.

## Moduulista palveluksi

Kun moduulille tulee syy erota (oma tiimi, oma julkaisutahti),
siirto etenee näin:

1. Moduulin julkinen rajapinta muutetaan etäkutsuksi tai viesteiksi.
   Tapahtumat siirtyvät viestinvälittäjään (luku 8).
2. Synkroniset, samassa transaktiossa tapahtuvat kuuntelijat
   korvataan sagalla tai hyväksytään eventual consistency.
3. Moduulin taulut siirretään omaan tietokantaansa.

Jos moduulin rajat ovat pitäneet, vaiheet 1 ja 3 ovat mekaanisia.
Vaihe 2 vaatii liiketoimintapäätöksen. Kauppa voi esimerkiksi päättää,
että tilauksen saa jättää ennen kuin varaus on vahvistettu.

## Käytännössä

- **Raja on sopimus, jota testi valvoo.** Ilman ArchUnitin tai Spring
  Modulithin kaltaista tarkistusta modulaarinen monoliitti rapistuu
  mutapalloksi ensimmäisen kiireen aikana.
- **Riippuvuudet yhteen suuntaan.** Ydinmoduuli (myynti) julkaisee
  tapahtumia, ja muut kuuntelevat. Syklinen riippuvuus tarkoittaa, että
  moduulit pitäisi yhdistää tai jakaa toisin.
- **Moduulilla on omat taulunsa.** Toisen moduulin tauluun ei liitytä
  SQL:ssä; tieto haetaan sen rajapinnasta tai kopioidaan tapahtumista.
- **Valitse kuuntelijan vaihe tietoisesti.** Saman transaktion
  kuuntelija antaa johdonmukaisuuden mutta kytkee moduulit;
  vahvistuksen jälkeinen tarvitsee pysyvän tapahtumarekisterin.
- **Hinnat:** moduulien välinen kutsu on edelleen nanosekunteja, ja
  rajojen valvonta maksaa vain testiajon. Siksi modulaarinen monoliitti
  on hyvä oletus.

## Itsearviointi

- Osaat jakaa sovelluksen moduuleihin, joilla on julkinen rajapinta
  ja sisäinen toteutus, ja selittää, miksi Javan näkyvyys ei riitä.
- Osaat kirjoittaa moduulirajat ArchUnit-säännöiksi ja varmistaa, että
  ne huomaavat rikkomuksen.
- Osaat käyttää prosessinsisäisiä tapahtumia moduulien irrottamiseen
  ja valita kuuntelijan transaktiovaiheen.
- Osaat kuvata, miten moduuli erotetaan palveluksi ja mitkä vaiheet
  vaativat liiketoimintapäätöksen.
