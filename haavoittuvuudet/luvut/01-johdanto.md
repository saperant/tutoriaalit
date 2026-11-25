# Johdanto {.runko-johdanto}

*Haavoittuvuus* on ohjelmointivirhe, jonka avulla syötteen antaja saa
ohjelman tekemään jotain, mitä sen ei pitänyt tehdä: lukemaan
salaisuuden, kirjoittamaan väärään paikkaan muistissa tai kaatumaan
palvelun kannalta pahimpaan aikaan. C:n ja C++:n kaltaisissa kielissä
suuri osa vakavista haavoittuvuuksista on *muistiturvallisuusvirheitä*:
puskurin yli kirjoittamista, vapautetun muistin käyttöä ja
kokonaislukujen ylivuotoja. Tämä tutoriaali opettaa löytämään,
ymmärtämään, arvioimaan ja korjaamaan niitä omassa koodissa.

Näkökulma on puolustava. Työkalut ovat samoja, joita tietoturva-
ammattilaiset käyttävät: sanitoijat, debuggeri, fuzzerit, staattiset
analysaattorit ja käännöksen suojaukset. Niillä selvitetään, mitä virhe
mahdollistaisi, jotta sen vakavuus voidaan arvioida ja korjaus
priorisoida. Toimivia hyökkäyksiä ei rakenneta: kun luvussa puhutaan
*hyödyntämisestä*, se tarkoittaa hyödynnettävyyden arviointia ja niitä
periaatteita, joiden takia suojaukset ovat olemassa.

## Vastuulauseke

Materiaali on tarkoitettu opetukseen ja oman koodin parantamiseen.

- **Käytä tekniikoita vain omiin ohjelmiisi, omiin järjestelmiisi tai
  kohteisiin, joihin sinulla on kirjallinen lupa.** Lupa on oltava
  ennen testausta, ja siinä on rajattava kohteet, ajankohta ja
  menetelmät. Työpaikalla luvan antaa järjestelmän omistaja, ei
  pelkästään esihenkilö.
- **Luvaton tunkeutuminen on rikos.** Suomen rikoslain 38. luku
  säätää rangaistavaksi muun muassa tietomurron, tietoliikenteen
  häirinnän, tietojärjestelmän häirinnän ja vahingollisen
  tietokoneohjelman levittämisen. Myös yritys voi olla rangaistava, ja
  vahingonkorvausvastuu tulee erikseen. Tämä on yleiskuvaus, ei
  oikeudellinen neuvo; epäselvissä tapauksissa kysy juristilta.
- **Tekijät eivät vastaa materiaalin väärinkäytöstä.** Esimerkit ovat
  paketin omia, tarkoituksella haavoittuvia pieniä ohjelmia, jotka
  ajetaan paikallisesti. Niissä ei ole verkkoskannausta, vieraita
  kohteita eikä oikeiden hyökkäysten koodia.

Vasara rakentaa talon ja rikkoo ikkunan; ammattilainen käyttää sitä
rakentamiseen. Samoin tämän paketin taidot ovat arvokkaita juuri siksi,
että niillä virheet löydetään ennen kuin joku muu löytää ne. Jos haluat
harjoitella haastavampia tehtäviä, luvussa 12 on luettelo laillisista
harjoitusympäristöistä ja kilpailuista, joissa kohteet on tehty
nimenomaan tähän tarkoitukseen.

## Ensimmäinen löydös

Vieraskirja tallentaa kävijöiden nimet keossa oleviin tietueisiin.
Nimelle on varattu 16 tavua, mutta kopiointi ei tarkista pituutta:

```{.c tiedosto="esimerkit/01-ensimmainen/vieraskirja.c" osa="kirjaa"}
```

Ohjelma käännetään *AddressSanitizerin* (ASan) ja
*UndefinedBehaviorSanitizerin* (UBSan) kanssa. Kääntäjä lisää jokaisen
muistiviittauksen ympärille tarkistuksen, ja ajonaikainen kirjasto
pitää kirjaa siitä, mikä muisti on varattua:

```{.bash tiedosto="esimerkit/01-ensimmainen/aja.sh" osa="kaanna"}
```

```{.bash tiedosto="esimerkit/yhteinen.sh" osa="liput"}
```

Tavalliset nimet toimivat:

```{.tuloste tiedosto="esimerkit/01-ensimmainen/odotettu" osa="t1"}
```

Ylipitkä nimi pysäyttää ohjelman heti ensimmäisessä virheellisessä
kirjoituksessa:

```{.bash tiedosto="esimerkit/01-ensimmainen/aja.sh" osa="pitka"}
```

```{.tuloste tiedosto="esimerkit/01-ensimmainen/odotettu" osa="t2"}
```

Sanitoijan raportissa on osoitteita ja kirjaston sisäisiä kehyksiä,
jotka vaihtelevat ajosta toiseen. Paketin apuskripti `raportti.py`
tiivistää siitä olennaisen: virheen lajin (*heap-buffer-overflow*),
operaation (25 tavun kirjoitus), kohdan omassa koodissa ja muistialueen
(20 tavun varaus, jonka loppuun kirjoitus osui). Raportin lukemista
käsitellään tarkemmin luvussa 9. Ilman sanitoijaa sama ohjelma olisi
todennäköisesti jatkanut ja tulostanut jotain uskottavaa: ylivuoto
olisi korruptoinut keon hiljaa. Siksi sanitoijat kuuluvat jokaiseen
C-ohjelman testiajoon.

Korjattu versio tarkistaa pituuden ennen kopiointia ja hylkää liian
pitkän nimen:

```{.tuloste tiedosto="esimerkit/01-ensimmainen/odotettu" osa="t3"}
```

## Mitä tutoriaali kattaa

| Luku | Aihe | Työkalut |
|------|------|----------|
| 2 | Turvallinen C | `ckd_*`, varoitukset, `-fanalyzer`, clang-tidy |
| 3 | Pinon ylivuoto | ASan, pinokanari, gdb |
| 4 | Kekovirheet | ASan, glibc:n tarkistukset, gdb |
| 5 | Muotoilumerkkijonot | `-Wformat-security`, FORTIFY_SOURCE |
| 6 | Suojaukset | ASLR, NX, kanari, RELRO, PIE, FORTIFY |
| 7 | Ohjausvuon eheys | Clangin CFI, CET, PAC ja BTI |
| 8 | Fuzzaus | libFuzzer, AFL++ |
| 9 | Juurisyy, arviointi ja korjaus | raportit, regressiotestit, variaatiot |
| 10 | Tapaustutkimuksia | Heartbleed, goto fail, xz ym. |
| 11 | Vastuullinen ilmoittaminen | CVSS, CVE, `security.txt` |
| 12 | Lopuksi | harjoitusympäristöt, lähteet |

Luvut 2–5 käsittelevät virheluokkia, luvut 6–7 suojauksia, jotka
rajaavat niiden vaikutusta, ja luvut 8–9 työtapoja, joilla virheet
löydetään ja korjataan järjestelmällisesti. Luku 10 kertoo, miltä
nämä virheet ovat näyttäneet oikeissa ohjelmissa ja miten ne olisi
voitu välttää.

Lukujen 1–9 esimerkit ovat samannumeroisissa hakemistoissa
(`esimerkit/03-pino` ja niin edelleen). Luvun 10 koodiotteet ovat
hakemistossa `esimerkit/tapaukset` ja luvun 11 esimerkki hakemistossa
`esimerkit/10-ilmoittaminen`.

## Esitiedot ja rajaus

*Takaisinmallinnus* on tärkein esitieto: x86-64-assemblyn lukeminen,
pinokehys, gdb:n eräajo ja `objdump`. Tämä paketti viittaa niihin eikä
toista niitä. *C-kieli* ja *Objektitiedostot, linkitys ja ABI*
(RELRO, PIE, GOT ja PLT) ovat taustaa. *Tietoturva kehitystyössä*
käsittelee kehitysprosessia, staattista analyysia (SAST), riippuvuuksien hallintaa
ja toimitusketjua organisaation tasolla; *Tietoturvan perusteet*
uhkamallinnusta ja sääntelyä. *Web-sovellusten tietoturva* käsittelee
web-haavoittuvuudet; tämä paketti keskittyy natiivikoodiin.

Kohdealusta on Linux x86-64 (Ubuntu 24.04, GCC 14, Clang 20, glibc
2.39). Osoitteet, kehysten asettelu ja kirjaston viestit vaihtelevat
versioiden välillä, mutta periaatteet eivät.

## Esimerkit

Jokainen esimerkki on hakemisto `esimerkit/NN-nimi/`, jossa on
ohjelmat ja skripti `aja.sh`. `esimerkit/testaa.sh` ajaa skriptit ja
vertaa tulosteita tiedostoihin `odotettu`. Kaatumiset ajetaan
apufunktiolla, joka tarkistaa, että ohjelma todella päättyy virheeseen,
ja tiivistää raportin:

```{.bash tiedosto="esimerkit/yhteinen.sh" osa="kaatuu"}
```

Esimerkit tarvitsevat GCC 14:n, Clang 20:n (myös clang-tidy ja lld),
gdb:n, binutilsin, AFL++:n, AArch64-ristikääntäjän, Pythonin ja
ShellCheckin. Kehityskontti on hakemistossa
`.devcontainer/haavoittuvuudet`.
