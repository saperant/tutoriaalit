# Verkko koodina

Verkkoja ylläpidettiin pitkään kirjautumalla laitteeseen ja
kirjoittamalla komentoja. Jokainen muutos oli käsityötä, laitteiden
asetukset ajautuivat erilleen, ja dokumentaatio jäi jälkeen. Kun verkko
kuvataan koodina, totuuden lähde on versionhallinnassa oleva kuvaus,
asetukset tuotetaan siitä koneellisesti, ja jokainen muutos katselmoidaan
ja testataan kuten ohjelmakoodi.

## Kuvaus ja generaattori

Esimerkin toimipisteen verkko on kuvattu TOML-tiedostona: segmentit
osoitteineen ja laitteet segmentteineen.

```{.toml tiedosto="esimerkit/11-verkko/verkko.toml"}
```

Generaattori tarkistaa kuvauksen ja tuottaa siitä käyttöönottokomennot.
Tarkistukset ovat samoja, joita kokenut ylläpitäjä tekee päässään:
menevätkö verkot päällekkäin, onko yhdyskäytävä verkossaan, onko osoite
jo käytössä.

```{.python tiedosto="esimerkit/11-verkko/main.py" osa="tarkistus"}
```

Komennot tuotetaan kuvauksesta. Laboratoriossa ne ovat `labra.sh`:n
funktioita; tuotannossa samasta kuvauksesta tuotettaisiin laitteiden
asetustiedostot mallipohjilla (esimerkiksi Jinja2) tai rajapintakutsut.

```{.python tiedosto="esimerkit/11-verkko/main.py" osa="komennot"}
```

```{.tuloste tiedosto="esimerkit/11-verkko.odotettu"}
```

## Käyttöönotto ja varmennus

Käyttöönotto ajaa tuotetut komennot ja varmentaa tuloksen. Varmennus on
yhtä tärkeä kuin muutos: verkko on kunnossa vasta, kun kuvauksen lupaamat
yhteydet on testattu.

```{.bash tiedosto="esimerkit/11-kayttoonotto.sh" osa="kayttoonotto"}
```

```{.bash tiedosto="esimerkit/11-kayttoonotto.sh" osa="varmennus"}
```

Virheellinen muutos jää kiinni ennen kuin se koskee yhteenkään laitteeseen:

```{.bash tiedosto="esimerkit/11-kayttoonotto.sh" osa="virheellinen"}
```

```{.tuloste tiedosto="esimerkit/11-kayttoonotto.odotettu"}
```

## Muutoksenhallinta

Koodina hallitun verkon muutos kulkee samaa reittiä kuin ohjelmistomuutos:

1. Muutos tehdään kuvaukseen haarassa ja avataan katselmoitavaksi.
2. CI tarkistaa kuvauksen, tuottaa asetukset ja näyttää eron nykyiseen
   tilaan (*plan*). Testiympäristö, kuten tämän tutoriaalin
   laboratorio tai valmistajan virtuaalilaitteet (containerlab),
   ajaa hyväksymistestit.
3. Hyväksytty muutos otetaan käyttöön koneellisesti huoltoikkunassa,
   ja varmennus ajetaan heti perään.
4. Jos varmennus epäonnistuu, edellinen versio palautetaan.

Työkaluina käytetään esimerkiksi Ansiblea, Nornirta tai valmistajien
hallintajärjestelmiä, ja totuuden lähteenä NetBoxia tai
versionhallintaa. Työkalua tärkeämpää on periaate: käsin tehty muutos
tuotantolaitteeseen on poikkeus, joka kirjataan ja viedään kuvaukseen
saman tien. Muuten seuraava koneellinen käyttöönotto kumoaa sen.

## Vianetsinnän menetelmä

Kun jokin ei toimi, edetään kerros kerrokselta ja varmennetaan jokainen
oletus mittaamalla:

1. **Fyysinen ja L2:** onko liitäntä ylhäällä (`ip -br link`), onko
   osoite opittu kytkimen välitystauluun oikeaan VLANiin ja porttiin,
   onko STP estänyt portin?
2. **L3:** onko laitteella oikea osoite ja peite (`ip -br addr`),
   löytyykö reitti kohteeseen ja takaisin (`ip route get`), vastaako
   yhdyskäytävä (ARP-taulu)?
3. **Suodatus:** pudottaako palomuuri (laskurit, `nft monitor trace`,
   lokit)? Tarkista molemmat suunnat ja kaikki matkan palomuurit.
4. **Palvelut:** saako laite DHCP:ltä oikeat tiedot, ratkeaako nimi,
   kuunteleeko palvelu (`ss -ltn`)?
5. **Kaappaa.** `tcpdump -ni <liitäntä> host <osoite>` matkan eri
   kohdissa näyttää, mihin asti paketti pääsee. Missä paketti viimeksi
   nähtiin, siellä on vika.

Jokaisesta vaiheesta kirjataan havainto, ei oletusta. "Palomuuri on
kunnossa" on oletus; "pudotuslaskuri ei kasvanut testin aikana" on
havainto.

## Käytännössä

- **Totuuden lähde ensin.** Ennen automaatiota sovitaan, mikä on
  kuvauksen paikka, ja nykytila tuodaan sinne. Automaatio väärästä
  lähteestä monistaa virheet.
- **Pienet, toistettavat muutokset.** Yksi muutos kerrallaan, jokaisella
  oma varmennus ja palautus.
- **Testit ovat osa kuvausta.** Sallitut ja kielletyt virrat
  kirjoitetaan testeiksi, jotka ajetaan jokaisen muutoksen jälkeen ja
  säännöllisesti muutenkin.
- **Lue ennen kirjoitusta.** Automaatio aloitetaan tilan keräämisestä
  ja vertailusta (*drift detection*); kirjoittaminen laitteisiin tulee
  vasta, kun lukeminen on luotettavaa.
- **Vianetsinnässä havaintoja, ei oletuksia,** ja kerros kerrallaan.

## Itsearviointi

- Osaat kuvata verkon koneluettavana kuvauksena ja tuottaa siitä
  asetukset.
- Osaat kirjoittaa kuvaukselle tarkistukset, jotka pysäyttävät
  virheelliset muutokset ennen käyttöönottoa.
- Osaat järjestää verkkomuutoksen katselmoinnin, testauksen,
  käyttöönoton ja palautuksen.
- Osaat edetä vianetsinnässä kerros kerrallaan ja todentaa jokaisen
  oletuksen mittaamalla.
