# Allekirjoitukset ja toistettavat buildit

Lukitustiedosto ja SBOM kertovat, *mitä* ohjelmistossa on. Tämä luku
vastaa kahteen muuhun kysymykseen: **kuka** teki muutoksen ja
**vastaako** julkaistu paketti lähdekoodia. Molemmat ratkaistaan
kryptografisilla allekirjoituksilla ja buildeilla, jotka kuka tahansa
voi toistaa. Allekirjoitusten toiminta opetetaan taidossa
*Kryptografia*; tässä niitä käytetään.

## Committien allekirjoitus

Gitin `user.name` ja `user.email` ovat vapaasti kirjoitettavia, joten
kuka tahansa voi tehdä commitin toisen nimissä. Allekirjoitettu commit
sitoo muutoksen avaimeen. Gitissä voi käyttää GPG:n sijaan
SSH-avaimia, jotka kehittäjillä on jo valmiiksi:

```{.bash tiedosto="esimerkit/07-allekirjoitus.sh" osa="asetukset"}
```

```{.bash tiedosto="esimerkit/07-allekirjoitus.sh" osa="commitit"}
```

```{.bash tiedosto="esimerkit/07-allekirjoitus.sh" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/07-allekirjoitus.odotettu"}
```

Allekirjoitus on vain niin hyvä kuin luotettujen avainten lista:
vieraan avaimen allekirjoitus on teknisesti kelvollinen (`U`), mutta
allekirjoittaja ei ole luotettu, joten tarkistus hylkää sen.
Koodialustat pitävät listaa käyttäjien avaimista ja näyttävät
merkinnän *Verified*. Haarasuojaus voi vaatia allekirjoitetut commitit
päähaaraan.

Allekirjoitus todistaa, mikä avain teki commitin, ei sitä, että muutos
on hyvä. Varastettu avain allekirjoittaa yhtä hyvin. Siksi avain
kannattaa säilyttää laiteavaimessa (FIDO2, `ed25519-sk`) tai
käyttöjärjestelmän avainsäilössä, ja katselmointi on edelleen tarpeen.

## Julkaisun allekirjoitus

Käyttäjä lataa julkaisun peilistä, CDN:stä tai pakettirekisteristä.
Jokainen välikäsi voi muuttaa sitä. Tiivistelista (`SHA256SUMS`)
paljastaa muutoksen, kun lista on aito, ja allekirjoitus todistaa
listan aitouden:

```{.bash tiedosto="esimerkit/07-julkaisu.sh" osa="allekirjoita"}
```

```{.bash tiedosto="esimerkit/07-julkaisu.sh" osa="tarkista"}
```

```{.tuloste tiedosto="esimerkit/07-julkaisu.odotettu"}
```

Kolmas tapaus on tärkein: hyökkääjä, joka muuttaa sekä paketin että
tiivistelistan, jää kiinni vain allekirjoituksen ansiosta. Neljäs,
näyttämättä jätetty tapaus on se, että hyökkääjä vaihtaa myös avaimen.
Siksi luotettu avain haetaan eri reittiä kuin julkaisu: projektin
verkkosivulta, aiemmasta julkaisusta tai avainpalvelimelta.

**Sigstore** ratkaisee avainten hallinnan toisin: allekirjoitusavain on
kertakäyttöinen, ja se sidotaan kehittäjän tai CI-ajon OIDC-identiteettiin
(esimerkiksi "tämän repositorion julkaisutyönkulku"). Allekirjoitukset
kirjataan julkiseen läpinäkyvyyslokiin (Rekor), joten väärinkäyttö
näkyy. `cosign` allekirjoittaa konttikuvia, ja PyPI ja npm tukevat
julkaisujen todisteita (*attestations*) samalla periaatteella.

## Toistettavat buildit

Allekirjoitus todistaa, kuka julkaisun teki, mutta ei sitä, että se
on rakennettu julkaistusta lähdekoodista. SolarWinds-hyökkäyksessä
lähdekoodi oli puhdas, mutta build-palvelimeen istutettu koodi lisäsi
takaoven buildin aikana. **Toistettava build** (*reproducible build*)
tuottaa samasta lähdekoodista bitilleen saman tuloksen, joten kuka
tahansa voi rakentaa paketin uudelleen ja verrata.

Tavallinen build ei ole toistettava, koska tulokseen päätyy
ympäristöstä riippuvaa tietoa: aikaleimat, käyttäjä- ja ryhmätunnukset,
tiedostojen järjestys ja polut. Pakkaus tar-arkistoksi näyttää ongelman
ja korjauksen:

```{.bash tiedosto="esimerkit/07-toistettava.sh" osa="tavallinen"}
```

```{.bash tiedosto="esimerkit/07-toistettava.sh" osa="toistettava"}
```

```{.tuloste tiedosto="esimerkit/07-toistettava.odotettu"}
```

Valitsimet poistavat vaihtelun lähteet: `--sort=name` järjestyksen,
`--mtime` aikaleimat (yleensä arvoksi asetetaan viimeisen commitin aika,
`SOURCE_DATE_EPOCH`), `--owner` ja `--group` käyttäjätunnukset ja
`gzip -n` pakkauksen otsakkeeseen tallennetun ajan. Samat ongelmat
koskevat kääntäjiä, JAR-tiedostoja ja konttikuvia; Reproducible
Builds -projekti dokumentoi korjaukset eri työkaluille.

## SLSA-tasot

**SLSA** (*Supply-chain Levels for Software Artifacts*) jäsentää
build-ketjun turvallisuuden tasoiksi. Versio 1.0 määrittelee
build-polun tasot:

| Taso | Vaatimus | Mitä se estää |
|------|----------|---------------|
| Build L1 | build tuottaa alkuperätiedon (*provenance*): mistä lähteestä, millä prosessilla | tuntemattomat julkaisut, virheet |
| Build L2 | build ajetaan isännöidyssä palvelussa, joka allekirjoittaa alkuperätiedon | julkaisun muokkaus buildin jälkeen |
| Build L3 | build-ajot ovat eristettyjä toisistaan, eikä build voi väärentää alkuperätietoa | saastunut build-ympäristö, toisen ajon vaikutus |

Alkuperätieto on allekirjoitettu dokumentti (in-toto-todiste), jonka
käyttäjä tai julkaisun vastaanottaja tarkistaa: "tämä paketti
rakennettiin repositorion `yritys/palvelu` commitista `abc123`
työnkulussa `release.yml`". GitHub Actions tuottaa tason L3 todisteita
valmiilla työnkuluilla.

## Käytännössä

- **Allekirjoita commitit ja julkaisut.** SSH- tai laiteavaimella
  committeihin, Sigstorella tai erillisellä avaimella julkaisuihin.
- **Tarkista, älä vain allekirjoita.** Haarasuojaus vaatii
  allekirjoitukset; käyttöönotto tarkistaa julkaisun ja kuvan
  allekirjoituksen ennen ajoa.
- **Luotettu avain eri reittiä.** Avain, joka tulee samasta paikasta
  kuin julkaisu, ei todista mitään.
- **Toistettavuus on tavoite.** Aloita helpoista vaihtelun lähteistä
  (aikaleimat, järjestys) ja vertaa kahden buildin tuloksia CI:ssä.
- **Alkuperätieto julkaisun mukana.** SLSA-taso L2 on nykyisillä
  CI-palveluilla vähäinen vaiva.

## Itsearviointi

- Osaat allekirjoittaa git-commitit SSH-avaimella ja tarkistaa ne
  luotettujen allekirjoittajien listalla.
- Osaat allekirjoittaa julkaisun tiivistelistan ja selittää, miksi
  luotettu avain haetaan eri reittiä.
- Osaat kertoa, mitä Sigstore ja läpinäkyvyysloki tuovat
  avaintenhallintaan.
- Osaat tehdä pakkauksesta toistettavan ja selittää vaihtelun lähteet.
- Osaat kuvata SLSA:n build-tasot ja alkuperätiedon.
