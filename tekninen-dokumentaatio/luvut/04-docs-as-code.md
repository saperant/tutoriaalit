# Dokumentaatio koodina

*Docs as code* tarkoittaa, että dokumentaatiota käsitellään samoilla
välineillä kuin koodia: se kirjoitetaan tekstitiedostoina, säilytetään
versionhallinnassa, katselmoidaan, rakennetaan automaattisesti ja
testataan. Idea on yksinkertainen, ja sen seuraukset ovat suuret.

## Miksi koodin viereen

Wikissä tai tekstinkäsittelyohjelmassa oleva dokumentaatio elää omaa
elämäänsä. Kun koodi muuttuu, dokumentti pitäisi muistaa päivittää
toisessa järjestelmässä, toisilla oikeuksilla ja ilman katselmointia.
Se unohtuu. Kun dokumentaatio on samassa repositoriossa:

- **Muutos on yksi kokonaisuus.** Koodi ja sen dokumentaatio muuttuvat
  samassa commitissa, ja katselmoija näkee molemmat.
- **Versiot täsmäävät.** Version 1.1 dokumentaatio on tagissa `v1.1`,
  ei ”jossain historiassa”.
- **Historia selittää.** `git blame` kertoo, milloin ja miksi kappale
  kirjoitettiin.
- **Kone tarkistaa.** Rakennus epäonnistuu, jos linkki on rikki tai
  esimerkki ei toimi.

Hinta on se, että kirjoittajan pitää osata versionhallinta ja
merkintäkieli. Kehittäjille se ei ole este. Jos dokumentaatiota
kirjoittavat myös muut, selainkäyttöliittymä repositorioon tai
erillinen muokkain madaltaa kynnystä.

## Merkintäkielet

Kevyt merkintäkieli on tekstiä, jota voi lukea sellaisenaan ja josta
työkalu tuottaa HTML:n tai PDF:n. Yleisimmät ovat Markdown ja
reStructuredText (reST). Sama opas molemmilla; ensin Markdown:

```{.markdown tiedosto="esimerkit/mkdocs/docs/opas.md"}
```

Ja reStructuredText:

```{.rst tiedosto="esimerkit/sphinx/opas.rst"}
```

Erot näkyvät kolmessa kohdassa. reST:n otsikot alleviivataan,
Markdownin otsikot alkavat risuaidalla. reST:ssä on *rooleja* ja
*direktiivejä* (`:func:`, `.. doctest::`), joilla tekstiin liitetään
merkitys: viittaus funktioon tai testattava esimerkki. Markdownissa
vastaavaa laajennusmekanismia ei ole, joten työkalut ovat keksineet
omansa, kuten HTML-kommentin, jolla tässä merkitään komennon tuloste.

| Ominaisuus | Markdown | reStructuredText |
|-------------------|---------------------------|---------------------------|
| oppimiskynnys | matala, useimmat osaavat | korkeampi |
| määrittely | CommonMark ja murteet | yksi toteutus (Docutils) |
| laajennettavuus | työkalukohtaiset lisäykset | roolit ja direktiivit |
| ristiviittaukset | linkki tiedostoon | viittaus kohteeseen nimellä |
| tyypillinen työkalu | MkDocs, Docusaurus, pandoc | Sphinx |

Muita vaihtoehtoja ovat AsciiDoc, joka on reST:n tapaan suunniteltu
kirjoihin ja käsikirjoihin, ja MyST, joka tuo reST:n roolit ja
direktiivit Markdownin syntaksiin Sphinxissä. Valinnalla on vähemmän
väliä kuin sillä, että projekti käyttää yhtä kieltä johdonmukaisesti.

## Tapausesimerkki: tämä tutoriaalisarja

Luet docs as code -putken tulosta. Tutoriaalit kirjoitetaan
Markdownilla, ja pandoc muuntaa ne PDF:ksi kolmen periaatteen varassa.

```{.dot otsikko="Tutoriaalin PDF syntyy lähteistä, joita testi ja rakennus käyttävät yhdessä"}
digraph {
  rankdir=LR;
  md [label="luvut/*.md\n(teksti)"];
  es [label="esimerkit/\n(koodi ja\nodotetut tulosteet)"];
  testi [label="make testaa\n(kääntää, ajaa,\nvertaa)"];
  suodin [label="pandoc-suotimet\n(koodi ja kaaviot\ntekstiin)"];
  pdf [label="PDF", shape=note];
  es -> testi;
  md -> testi [label="viittaukset"];
  md -> suodin;
  es -> suodin [label="sisällytys"];
  suodin -> pdf [label="XeLaTeX"];
}
```

**Koodia ei kirjoiteta tekstiin.** Luvun Markdown-lähteessä koodilohko
on tyhjä ja viittaa tiedostoon:

    ```{.python tiedosto="esimerkit/saa/tilasto.py" osa="keskiarvo"}
    ```

Pandoc-suodin lukee tiedoston ja sijoittaa merkintöjen `@alku
keskiarvo` ja `@loppu keskiarvo` välisen osan lohkoon. Sama tiedosto
käännetään ja ajetaan testissä, joten kirjassa ei voi olla koodia, joka
ei toimi. Tarkistin hylkää luvun, jossa on käsin kirjoitettu
koodilohko.

**Tulosteet ovat testin odotusarvoja.** Ohjelman tuloste näytetään
tiedostosta, johon testi vertaa ohjelman todellista tulostetta. Jos
ohjelma muuttuu, testi epäonnistuu, kunnes odotettu tuloste ja sen
mukana kirja päivitetään.

**Kaaviot ovat tekstiä.** Yllä oleva kaavio on kirjoitettu lähteeseen
Graphviz-kielellä, ja suodin piirtää sen rakennuksen aikana (luku 11).
Kaavion muutos näkyy katselmoinnissa rivien muutoksena.

Rakennus ajetaan jokaisesta muutoksesta jatkuvan integraation
palvelussa: testit ensin, sitten PDF:t, ja valmiit tiedostot
julkaistaan verkkosivulle. PDF:t eivät ole versionhallinnassa, koska
ne ovat käännöstuotteita kuten binäärit.

## Katselmointi ja versiot

Dokumentaation katselmointi on eri työtä kuin koodin. Katselmoija
lukee muutoksen lukijan silmin: löytyykö vastaus, toimiiko esimerkki,
onko termi sama kuin muualla. Rakennettu esikatselu auttaa, koska
merkintäkielen erotus ei näytä, miltä sivu näyttää. Moni
julkaisupalvelu rakentaa esikatselun jokaisesta muutosehdotuksesta.

Julkaistulla ohjelmistolla on useita versioita käytössä yhtä aikaa, ja
jokaisen käyttäjä tarvitsee oman versionsa dokumentaation. Tavallinen
ratkaisu on julkaista dokumentaatio versioittain (`/1.2/`, `/2.0/`)
ja ohjata osoite `/latest/` uusimpaan vakaaseen versioon. Vanhan
version sivulle lisätään huomautus, että uudempi on olemassa. Koska
dokumentaatio on samassa repositoriossa kuin koodi, vanhan version
dokumentaatio rakentuu vanhasta tagista ilman erillistä arkistointia.

## Käytännössä

- **Dokumentaatio samaan muutokseen kuin koodi.** Erillinen
  ”dokumentoidaan myöhemmin” -tehtävä jää tekemättä.
- **Rakennus on yksi komento.** Jos dokumentaation rakentaminen vaatii
  ohjeen, sitä ei rakenneta paikallisesti eikä virheitä huomata.
- **Lukitse työkalujen versiot.** Dokumentaatiotyökalun päivitys
  muuttaa tulosta kuten kääntäjän päivitys, ja rikkoutuneen rakennuksen
  syy pitää löytää versionhallinnasta.
- **Yksi rivi virkettä tai kappaletta kohden ei ole pakko.** Tärkeämpää
  on, että rivitys on vakaa: uudelleenrivitetty kappale näyttää
  katselmoinnissa kokonaan muuttuneelta.
- **Generoitu tiedosto joko rakennetaan tai tarkistetaan.** Jos
  generoitu tiedosto on versionhallinnassa, testi varmistaa, että se
  vastaa lähdettään. Muuten se vanhenee huomaamatta.

## Itsearviointi

- Osaat perustella, miksi dokumentaatio kannattaa pitää koodin kanssa
  samassa repositoriossa, ja nimetä ratkaisun hinnan.
- Osaat kirjoittaa saman sivun Markdownilla ja reStructuredTextillä ja
  kertoa kielten olennaiset erot.
- Osaat kuvata putken, jossa dokumentin koodi ja tulosteet tulevat
  testatuista tiedostoista.
- Osaat kertoa, miten usean version dokumentaatio julkaistaan.
