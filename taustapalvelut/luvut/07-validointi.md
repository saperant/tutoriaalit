# Validointi ja virheiden käsittely

Jokainen rajapinnan läpi tuleva arvo on epäluotettava, kunnes se on
tarkistettu. Tarkistus tehdään kerran, rajalla, ja sen jälkeen sisäinen
koodi käsittelee vain kelvollisia arvoja. Virheet palautetaan
asiakkaalle tavalla, jonka se ymmärtää, ja kirjataan lokiin tavalla,
jonka ylläpitäjä ymmärtää.

## Bean Validation rajalla

Pyynnön DTO:n kentät merkitään rajoitteilla (`@NotBlank`, `@Size`,
`@PositiveOrZero`, `@Min`, `@Email`, `@Pattern`), ja `@Valid`
ohjainmetodin parametrissa käynnistää tarkistuksen ennen kuin metodia
kutsutaan. Rajoitteet ovat luvun 3 DTO-määrittelyissä; ohjain itse
pysyy siistinä:

```{.java tiedosto="esimerkit/kauppa/src/main/java/fi/tutoriaalit/kauppa/tuote/TuoteOhjain.java" osa="lisays"}
```

`@Valid` sisäkkäisessä tyypissä (`List<@Valid RiviPyynto>`
tilauspyynnössä) tarkistaa myös listan alkiot. Kyselyparametrien
rajoitteet (`@Min(0) int sivu`) tarkistetaan Spring 6.1:stä lähtien
automaattisesti *menetelmävalidointina*.

Virheellinen pyyntö ei koskaan päädy palveluun. Testi varmistaa sen
ja sen, että virheet palautetaan kentittäin:

```{.java tiedosto="esimerkit/kauppa/src/test/java/fi/tutoriaalit/kauppa/tuote/TuoteOhjainTest.java" osa="validointi"}
```

Kenttäkohtaiset virheet kootaan ongelmakuvaukseen omana
ominaisuutenaan. Kentän nimi ja rajoitteen tunnus (`NotBlank`) ovat
koneluettavia; viesti on oletusviesti, jonka kieli riippuu
palvelimen lokaalista, ja käyttöliittymä yleensä kääntää sen itse
tunnuksen perusteella.

```{.java tiedosto="esimerkit/kauppa/src/main/java/fi/tutoriaalit/kauppa/virheet/Ongelmat.java" osa="kentat"}
```

## Muoto, sisältö ja säännöt

Validointi jakautuu kolmeen tasoon, ja kukin tehdään omassa paikassaan:

| Taso | Esimerkki | Missä | Vastaus |
|------|-----------|-------|---------|
| Muoto | ei JSONia, väärä tyyppi | viestimuunnin (Jackson) | 400 |
| Sisältö | tyhjä nimi, negatiivinen hinta | Bean Validation DTO:ssa | 400 tai 422 |
| Sääntö | saldo ei riitä, versio vanhentunut | palvelu, tietokanta | 409, 412 |

Säännöt riippuvat tilasta, eikä niitä voi tarkistaa DTO:sta. Ne
kuuluvat palveluun, ja tietokannan rajoitteet ovat viimeinen
puolustuslinja. Saldosääntö on tästä hyvä esimerkki: sitä ei
tarkisteta lainkaan erikseen, vaan ehdollinen päivitys on sekä tarkistus
että muutos (luku 6).

## Jäsennä, älä vain tarkista

*Parse, don't validate* -periaate: rajalla raakasyöte muunnetaan
tyypiksi, joka voi olla olemassa vain kelvollisena. Sen jälkeen
tarkistusta ei tarvitse toistaa, eikä sitä voi unohtaa.
`TilausOhjain` muuntaa validoidun DTO:n palvelun tyypiksi
`TilausPalvelu.Rivi`, eikä palvelu koskaan näe HTTP-pyynnön
muotoa. Pidemmälle vietynä tunnisteet, rahamäärät ja sähköpostiosoitteet
ovat omia arvotyyppejään (`record Sahkoposti(String arvo)`, jonka
konstruktori tarkistaa muodon), jolloin kääntäjä estää sekoittamasta
tuotetunnistetta tilaustunnisteeseen. Tekniikka (omat tyypit ja
recordit) esitellään taidossa *Java*.

## Poikkeukset ja virhevastaukset

Virheiden kulku palvelussa:

1. Palvelu heittää merkityksellisen poikkeuksen (`EiLoydy`,
   `SaldoEiRiita`). Poikkeus ei tiedä HTTP:stä.
2. Ohjainneuvoja `Ongelmat` muuntaa sen ongelmakuvaukseksi, jolla on
   oikea tilakoodi ja vakaa `type`.
3. Springin omat poikkeukset (väärä sisältötyyppi, puuttuva parametri,
   tuntematon polku) saavat saman muodon Bootin oletuskäsittelijältä.
4. Odottamaton poikkeus päätyy Bootin virhekäsittelyyn: asiakas saa
   500-vastauksen ilman yksityiskohtia, ja loki saa pinojäljen.

Testi tarkistaa 404-vastauksen sisältötyypin, tyypin ja kuvauksen:

```{.java tiedosto="esimerkit/kauppa/src/test/java/fi/tutoriaalit/kauppa/tuote/TuoteOhjainTest.java" osa="puuttuu"}
```

Poikkeusta ei käytetä normaalin ohjausvuon välineenä silmukoissa:
Javassa poikkeuksen luonti kerää pinojäljen, mikä on kallista
(Java-tutoriaalin hintaluku). Pyyntöä kohden yksi poikkeus on kuitenkin
mitätön kustannus verrattuna tietokantakutsuun, joten rajapinnan virheet
ovat poikkeuksia.

## Virheiden kirjaaminen

- 4xx on asiakkaan virhe, joka kirjataan korkeintaan `INFO`- tai
  `DEBUG`-tasolla. Jos jokainen väärä salasana on `ERROR`, oikeat
  virheet hukkuvat.
- 5xx on palvelun virhe: `ERROR` ja pinojälki, kerran. Poikkeusta ei
  kirjata jokaisessa kerroksessa uudelleen ennen kuin se heitetään
  eteenpäin.
- Lokiin ei kirjata salasanoja, tunnisteita (*token*), henkilötunnuksia
  eikä kokonaisia pyyntöjen runkoja. Henkilötiedot lokissa ovat
  GDPR:n mukaan henkilötietojen käsittelyä.

## Käytännössä

- **Tarkista kerran, rajalla**, ja muunna sisäisiksi tyypeiksi.
  Sisäinen koodi ei toista tarkistuksia "varmuuden vuoksi".
- **Rajoitteet DTO:hon, säännöt palveluun, invariantit tietokantaan.**
  Kukin taso tarkistaa sen, minkä se pystyy tarkistamaan luotettavasti.
- **Kenttäkohtaiset virheet koneluettavina**: kenttä ja rajoitteen
  tunnus. Asiakas ei jäsennä virheviestiä.
- **Yksi paikka virheiden muunnokselle** (`@RestControllerAdvice`).
  Ohjaimissa ei ole `try`–`catch`-lohkoja, jotka tekevät
  virhevastauksia käsin.
- **Hinta:** Bean Validation käyttää heijastusta ja on nopea
  (mikrosekunteja pyyntöä kohden). Raskas tarkistus, kuten
  tietokantahaku "onko nimi jo käytössä", ei kuulu rajoitemerkintään:
  se on kilpatilanne. Yksilöivä rajoite tietokannassa ja sen virheen
  muunnos 409:ksi on oikea ratkaisu.

## Itsearviointi

- Osaat merkitä DTO:n kentät rajoitteilla ja validoida rungon,
  sisäkkäiset alkiot ja kyselyparametrit.
- Osaat jakaa tarkistukset muodon, sisällön ja sääntöjen tasoille ja
  valita kullekin tilakoodin.
- Osaat soveltaa jäsennä, älä vain tarkista -periaatetta.
- Osaat muuntaa poikkeukset ongelmakuvauksiksi yhdessä paikassa ja
  kirjata virheet oikealla tasolla.
