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
Sama periaate palvelimille on taidossa *Palvelinympäristöt* ja
pilvi-infrastruktuurille taidossa *Kontit ja pilvi-infrastruktuuri*.

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
  ja vertailusta kuvaukseen, jolloin asetusten ajautuminen (*drift*)
  havaitaan; kirjoittaminen laitteisiin tulee vasta, kun lukeminen on
  luotettavaa.

## Itsearviointi

- Osaat kuvata verkon koneluettavana kuvauksena ja tuottaa siitä
  asetukset.
- Osaat kirjoittaa kuvaukselle tarkistukset, jotka pysäyttävät
  virheelliset muutokset ennen käyttöönottoa.
- Osaat järjestää verkkomuutoksen katselmoinnin, testauksen,
  käyttöönoton ja palautuksen.
