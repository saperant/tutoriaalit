# Hajautettu monoliitti ja muut antimallit

*Hajautettu monoliitti* on järjestelmä, joka on jaettu palveluihin
mutta käyttäytyy kuin monoliitti: palveluja ei voi julkaista erikseen,
yksi vika kaataa kaiken, ja jokainen pyyntö kulkee usean palvelun
kautta. Siinä on mikropalvelujen hinta ilman niiden hyötyjä. Tämä luku
mittaa kaksi sen tunnusmerkkiä ja luettelee yleisimmät syyt.

## Synkroniset kutsuketjut

Tyypillinen hajautettu monoliitti syntyy, kun jokainen palvelu kysyy
tarvitsemansa tiedon seuraavalta: myynti kysyy hinnoittelulta, joka
kysyy asiakkuuksilta, joka kysyy luottotiedoilta. Esimerkin ketjussa
jokainen palvelu tekee 40 millisekunnin työn ja kutsuu sitten
seuraavaa:

```{.java tiedosto="esimerkit/etakutsut/src/main/java/fi/tutoriaalit/palvelut/etakutsut/ketju/Ketju.java" osa="ketju"}
```

Viiveet laskevat yhteen. Jos kyselyt eivät riipu toisistaan, ne voi
tehdä rinnakkain, jolloin kokonaisaika on hitaimman kutsun mittainen:

```{.java tiedosto="esimerkit/etakutsut/src/test/java/fi/tutoriaalit/palvelut/etakutsut/ketju/KetjuTest.java" osa="viive"}
```

Rinnakkaistaminen auttaa viiveeseen mutta ei saatavuuteen. Jos
pyyntö tarvitsee viisi palvelua, joista kukin toimii 99 % ajasta, koko
pyyntö onnistuu vain, kun kaikki viisi toimivat:

```{.java tiedosto="esimerkit/etakutsut/src/main/java/fi/tutoriaalit/palvelut/etakutsut/ketju/Saatavuus.java" osa="saatavuus"}
```

```{.java tiedosto="esimerkit/etakutsut/src/test/java/fi/tutoriaalit/palvelut/etakutsut/ketju/KetjuTest.java" osa="saatavuus"}
```

Saatavuus on yksittäisten saatavuuksien tulo: $0{,}99^5 \approx 0{,}951$.
Viiden "kahden ysin" palvelun ketju toimii vain 95 % ajasta, eli noin
18 päivää vuodessa jokin pyyntö epäonnistuu. Mitä pidempi synkroninen
ketju, sitä heikompi järjestelmä, vaikka jokainen osa olisi hyvä.

Korjauskeinot ovat arkkitehtuurisia: tieto kopioidaan tapahtumista
paikalliseksi näkymäksi (luku 4), kutsuketju korvataan viesteillä
(luku 8), tai palvelut, jotka aina tarvitsevat toisiaan, yhdistetään.

## Jaettu tietokanta

Kaksi palvelua lukee ja kirjoittaa samoja tauluja. Seuraukset:

- Skeeman muutos vaatii kaikkien käyttäjien yhtäaikaisen päivityksen.
  Kenenkään ei ole turvallista nimetä saraketta uudelleen.
- Sääntöjä on kahdessa paikassa, ja ne alkavat erota.
- Toisen palvelun raskas kysely hidastaa toista; kapasiteettia ei voi
  mitoittaa palvelukohtaisesti.
- Kumpikaan ei voi vaihtaa tallennustapaa.

Jaettu tietokantapalvelin ei sinänsä ole ongelma, jos jokaisella
palvelulla on oma skeemansa ja käyttäjänsä, kuten esimerkin
`viestit`-modulissa. Ongelma on jaettu *skeema*.

## Muut tunnusmerkit

| Antimalli | Oire | Korjaus |
|-----------|------|---------|
| Lukittu julkaisu (*lockstep deployment*) | palvelut on julkaistava yhdessä | yhteensopivat rajapinnat, sopimustestit (luku 11) |
| Puhelias rajapinta | näkymä tarvitsee kymmeniä kutsuja | karkeampi rajapinta, BFF (luku 11) |
| Entiteettipalvelut | palvelu per taulu, logiikka kutsujissa | jako kyvykkyyksien mukaan (luku 4) |
| Jaettu domain-kirjasto | yhteinen `Tuote`-luokka kaikissa palveluissa | jokaisella kontekstilla oma malli |
| Hajautettu transaktio (2PC) | palvelut lukitsevat toistensa resurssit | saga (luku 10) |
| Nanopalvelut | enemmän palveluja kuin kehittäjiä | yhdistä, modulaarinen monoliitti |
| Älykäs väylä | liiketoimintalogiikkaa integraatiokerroksessa | logiikka palveluihin, tyhmät putket |

Jaettu kirjasto ei aina ole antimalli. Tekniset kirjastot (lokitus,
mittarit, todennus) ovat hyödyllisiä. Ongelma syntyy, kun kirjastossa
on liiketoiminnan malli, koska silloin sen muutos on kaikkien palvelujen
yhtäaikainen muutos.

## Kahden vaiheen vahvistus

Hajautettu transaktio *kahden vaiheen vahvistuksella* (*two-phase
commit*, 2PC, XA) lupaa, että usean tietokannan muutokset tallentuvat
yhdessä. Koordinaattori kysyy ensin kaikilta, voivatko ne vahvistaa
(ja nämä lukitsevat resurssinsa), ja käskee sitten vahvistamaan. Jos
koordinaattori kaatuu vaiheiden välissä, osallistujat odottavat
lukot päällä. Saatavuus on osallistujien saatavuuksien tulo, kuten
kutsuketjussa. Siksi mikropalvelut eivät käytä 2PC:tä, vaan korvaavat
sen sagalla, joka hyväksyy hetkellisen epäjohdonmukaisuuden.

## Käytännössä

- **Mittaa ketjut.** Hajautettu jäljitys (OpenTelemetry) näyttää,
  monenko palvelun läpi pyyntö kulkee. Yli kolmen palvelun synkroninen
  ketju on varoitusmerkki.
- **Rinnakkaista riippumattomat kutsut**, mutta muista, että saatavuus
  ei parane rinnakkaistamalla.
- **Oma skeema ja käyttäjä jokaiselle palvelulle**, vaikka
  tietokantapalvelin olisi yhteinen.
- **Testaa itsenäinen julkaisu.** Jos palvelua ei voi julkaista yksin
  rikkomatta muita, järjestelmä on hajautettu monoliitti, vaikka kaavio
  näyttäisi muulta.
- **Hinnat:** ketjun viive on summa ja saatavuus tulo; jaettu skeema
  tekee jokaisesta muutoksesta usean tiimin projektin.

## Itsearviointi

- Osaat tunnistaa hajautetun monoliitin oireet ja selittää, miksi se
  on huonompi kuin kumpikaan puhdas vaihtoehto.
- Osaat laskea synkronisen ketjun viiveen ja saatavuuden ja perustella,
  miksi rinnakkaistaminen auttaa vain viiveeseen.
- Osaat selittää jaetun tietokannan haitat ja erottaa jaetun
  palvelimen jaetusta skeemasta.
- Osaat selittää, miksi kahden vaiheen vahvistusta ei käytetä
  mikropalvelujen välillä.
