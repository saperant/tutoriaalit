# MkDocs ja julkaisu

MkDocs on Markdown-pohjainen sivustogeneraattori. Se tekee vähemmän
kuin Sphinx ja on siksi nopeampi oppia: hakemisto Markdown-tiedostoja,
yksi asetustiedosto ja tuloksena sivusto, jossa on valikko ja haku.

## Projekti

Esimerkkinä on komentoriviohjelman käsikirja. Asetustiedosto nimeää
sivut ja kertoo, mitkä viat ovat varoituksia:

```{.yaml tiedosto="esimerkit/mkdocs/mkdocs.yml"}
```

Sivut ovat tavallista Markdownia hakemistossa `docs/`, ja linkit
osoittavat toisiin Markdown-tiedostoihin (luvun 4 opas). MkDocs
muuntaa linkit sivuston osoitteiksi ja tarkistaa samalla, että kohde
ja sen ankkuri ovat olemassa.

## Tiukka tila

Valitsin `--strict` tekee varoituksista virheitä, kuten Sphinxin
`-W`. Esimerkkien Makefile rakentaa käsikirjan ja tekee sitten
kopion, johon lisätään linkki olemattomaan sivuun ja olemattomaan
otsikkoon:

```{.makefile tiedosto="esimerkit/Makefile" osa="mkdocs"}
```

```{.tuloste tiedosto="esimerkit/mkdocs/rikki.odotettu"}
```

Kohteen kommentti kertoo sudenkuopasta, joka löytyi tätä esimerkkiä
tehdessä. Valitsin `-q` hiljentää varoitukset, ja koska tiukka tila
laskee tulostettuja varoituksia, `mkdocs build -q --strict` hyväksyy
rikkinäisen linkin. Tarkistus, jonka ei ole koskaan nähty
epäonnistuvan, voi olla pois päältä. Siksi jokaisella tämän
tutoriaalin tarkistuksella on viallinen näyte, jonka on jäätävä
kiinni.

## Upotetut tulosteet

Käsikirja näyttää, mitä ohjelma tulostaa. Käsin kopioitu tuloste
vanhenee, kun ohjelman tuloste muuttuu. Markdownissa ei ole
Sphinxin `doctest`-direktiiviä, joten esimerkit merkitsevät komennon
HTML-kommentilla (luvun 4 opas), ja pieni työkalu ajaa komennon ja
vertaa tulostetta lohkon sisältöön. Valitsimella `--korjaa` se
kirjoittaa lohkon uudelleen, joten tuloste päivitetään ajamalla
työkalu eikä leikkaamalla ja liimaamalla. Sama tekniikka sopii
README:n käyttöesimerkkeihin ja `--help`-tulosteisiin, ja valmiita
toteutuksia ovat esimerkiksi cog ja mdsh.

## Sphinx vai MkDocs

| Tarve | Sphinx | MkDocs |
|---------------------------|-----------------------|-------------------------|
| merkintäkieli | reST (tai MyST) | Markdown |
| viite koodista | sisäänrakennettu (`autodoc`) | laajennus (mkdocstrings) |
| tarkistetut viittaukset koodiin | kyllä | laajennuksella |
| esimerkkien ajo | `doctest`-laajennus | erillinen työkalu |
| PDF ja muut muodot | kyllä (LaTeX, EPUB, man) | laajennuksilla |
| oppimiskynnys | korkeampi | matala |
| sopii parhaiten | kirjaston viite ja käsikirja | käsikirja, ohjeet, sivusto |

Muita saman perheen työkaluja ovat Docusaurus (JavaScript, versioitu
dokumentaatio valmiina), Antora (AsciiDoc, usean repositorion
dokumentaatio), mdBook (Rust-yhteisön kirjat) ja Hugo (yleinen
sivustogeneraattori). Periaatteet ovat samat: teksti
versionhallinnassa, rakennus komentoriviltä ja varoitukset virheinä.
Valinta kannattaa tehdä sen mukaan, tarvitaanko viitettä koodista ja
mitä merkintäkieltä kirjoittajat osaavat.

## Julkaisu

Rakennettu dokumentaatio on hakemisto staattisia tiedostoja, joten sen
voi julkaista millä tahansa verkkopalvelimella. Julkaisu kuuluu
jatkuvan integraation putkeen:

1. Jokainen muutosehdotus rakentaa dokumentaation tiukassa tilassa.
   Rikkinäinen linkki estää yhdistämisen kuten epäonnistunut testi.
2. Päähaaran muutos julkaisee kehitysversion dokumentaation.
3. Versiotagi julkaisee version dokumentaation pysyvään osoitteeseen.

Julkaisualustoja ovat esimerkiksi GitHub Pages ja GitLab Pages, jotka
palvelevat putken tuottaman hakemiston, sekä Read the Docs, joka
rakentaa Sphinx- ja MkDocs-projektit itse ja hoitaa versiot ja
esikatselut. Putken rakentaminen on taidon *Jatkuva integraatio ja
toimitus* aihe; tämän tutoriaalisarjan oma putki rakentaa PDF:t ja
julkaisee ne samalla tavalla.

Julkaistun dokumentaation osoitteet ovat rajapinta. Muut sivut ja
hakukoneet linkittävät niihin, joten sivua ei siirretä jättämättä
uudelleenohjausta.

## Käytännössä

- **Rakenna tiukassa tilassa myös paikallisesti.** `mkdocs serve`
  näyttää sivun selaimessa ja päivittää sen tallennettaessa, mutta
  vasta `mkdocs build --strict` kertoo, onko sivusto ehjä.
- **Älä hiljennä tarkistusta, jonka tulosta luet.** Jos loki on liian
  pitkä, ohjaa se tiedostoon ja näytä virheen sattuessa.
- **Valikko asetustiedostoon.** Ilman `nav`-asetusta sivut ovat
  valikossa aakkosjärjestyksessä, ja uusi sivu ilmestyy sinne, minne
  nimi sen vie.
- **Älä kopioi tulosteita käsin.** Jokainen dokumentissa näkyvä
  tuloste on joko testin odotusarvo tai työkalun kirjoittama.
- **Yksi työkalu projektia kohden, jos mahdollista.** Tässä
  esimerkissä on kaksi, jotta niitä voi verrata. Oikeassa projektissa
  kaksi dokumentaatiosivustoa tarkoittaa kahta paikkaa, joista lukija
  etsii.

## Itsearviointi

- Osaat pystyttää MkDocs-projektin ja määritellä sen valikon.
- Osaat rakentaa sivuston tiukassa tilassa ja kertoa, mitkä viat se
  löytää.
- Osaat pitää dokumentissa näkyvän komennon tulosteen ajan tasalla
  ilman käsityötä.
- Osaat valita Sphinxin ja MkDocsin välillä projektin tarpeiden
  perusteella ja kuvata, miten dokumentaatio julkaistaan putkesta.
