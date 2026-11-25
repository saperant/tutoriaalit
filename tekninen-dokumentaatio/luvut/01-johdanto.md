# Johdanto {.runko-johdanto}

Ohjelmisto, jota kukaan ei osaa käyttää, asentaa tai muuttaa, on
arvoton, vaikka koodi olisi virheetöntä. Dokumentaatio on se osa
ohjelmistoa, joka siirtää tiedon tekijältä lukijalle: käyttäjälle,
ylläpitäjälle, uudelle tiimiläiselle ja kirjoittajalle itselleen
puolen vuoden kuluttua.

Dokumentaatio epäonnistuu yleensä kahdella tavalla. Sitä ei ole, tai
se on olemassa mutta väärin: kuvaa versiota, jota ei enää ole,
vastaa kysymykseen, jota kukaan ei kysynyt, tai on niin sekava, ettei
vastausta löydy. Jälkimmäinen on pahempi, koska väärään dokumentaatioon
luotetaan.

Tämän tutoriaalin väite on, että molemmat ongelmat ratkeavat samoilla
keinoilla kuin koodin laatuongelmat:

1. **Lukija ensin.** Jokaisella dokumentilla on lukija ja tehtävä. Kun
   ne tiedetään, rakenne seuraa (luvut 2 ja 3).
2. **Dokumentaatio on koodia.** Se on tekstitiedostoina
   versionhallinnassa koodin vieressä, muuttuu samassa muutoksessa ja
   katselmoidaan samalla tavalla (luvut 4–6).
3. **Yksi totuuden lähde.** Rajapinnan kuvaus tuotetaan koodista tai
   tarkistetaan koodia vasten, ei kirjoiteta erikseen (luvut 7–9).
4. **Rakenne näkyväksi.** Arkkitehtuuri ja sen perustelut kirjataan
   niin, että ne löytyvät vuosien päästä (luvut 10 ja 11).
5. **Dokumentaatio testataan.** Esimerkit ajetaan, linkit
   tarkistetaan ja varoitukset ovat virheitä (luku 12).

## Mitä oletetaan

Lukija osaa Pythonia ja sen työkaluja (taito *Python
työkaluohjelmointiin*: moduulit, pytest, tyyppivihjeet) ja Gitin
perusteet (taito *Versionhallinta (Git)*: haarat, katselmointi,
julkaisut ja semanttinen versiointi). C-esimerkki luvussa 8 on lyhyt,
ja sen ymmärtää lukematta C:tä sujuvasti.

Tutoriaali ei opeta yhtä työkalua perusteellisesti. Sphinx, MkDocs,
Doxygen ja OpenAPI esitellään sen verran, että niiden periaate ja
tarkistukset tulevat tutuiksi; yksityiskohdat ovat työkalujen omissa
ohjeissa, joihin luku 13 viittaa. Arkkitehtuurityylit käsittelee taito
*Palveluarkkitehtuurit*, HTTP-rajapintojen suunnittelun taito
*Taustapalvelut* ja julkaisuputket taito *Jatkuva integraatio ja
toimitus*.

## Esimerkkijärjestelmä

Kaikki esimerkit kuvaavat samaa pientä järjestelmää, sääasemapalvelua.
Asemat mittaavat lämpötilaa ja kosteutta ja lähettävät lukemat
palveluun, joka tallentaa ne ja laskee yhteenvetoja.

```{.dot tiedosto="esimerkit/kaaviot/c4-konteksti.dot" otsikko="Sääasemapalvelu ympäristössään"}
```

Järjestelmässä on neljä dokumentoitavaa osaa, ja jokaiselle sopii oma
työkalunsa:

| Osa | Kieli | Lukija | Dokumentaatio |
|--------------------|--------|--------------------|---------------------------|
| kirjasto `saa` | Python | sovelluskehittäjä | Sphinx: opas, ohjeet, viite |
| komentoriviohjelma | Python | käyttäjä, ylläpitäjä | MkDocs: käsikirja |
| rengaspuskuri | C | laiteohjelmoija | Doxygen: viite otsakkeesta |
| HTTP-rajapinta | JSON | rajapinnan käyttäjä | OpenAPI-kuvaus |

Lisäksi projektilla on kaikille yhteiset dokumentit: README,
muutosloki, osallistumisohje, toimintaohje häiriöön ja
arkkitehtuuripäätökset.

## Esimerkkien ajaminen

Esimerkit ovat hakemistossa `esimerkit/`, ja niiden Makefile ajaa
kaikki tarkistukset:

| Komento | Mitä tapahtuu |
|-------------------|----------------------------------------------|
| `make` | kaikki alla olevat |
| `make pytest` | yksikkötestit ja docstringien esimerkit |
| `make sphinx` | kirjaston dokumentaatio, varoitukset virheinä |
| `make mkdocs` | käsikirja, rikkinäiset linkit virheinä |
| `make doxygen` | C-kirjaston viite, puuttuvat kuvaukset virheinä |
| `make openapi` | rajapintakuvaus toteutusta vasten |
| `make dokumentit` | linkit, proosa, muutosloki, upotetut tulosteet |
| `make adr` | päätöslokin rakenne |
| `make kaaviot` | koodista tuotetut kaaviot ovat ajan tasalla |
| `make naytteet` | tarkistimet löytävät tahalliset viat |

Jokainen tarkistus ajetaan myös viallista näytettä vasten: tarkistin,
joka ei koskaan epäonnistu, ei tarkista mitään. Generoitua HTML:ää ei
verrata tavu tavulta, koska se muuttuu työkalun version mukana.
Vertailtavana on rakenne: mitkä kohteet on dokumentoitu ja mitä
varoituksia syntyi.

Työkalujen versiot ovat Sphinx 8.2, MkDocs 1.6, Doxygen 1.9 ja
OpenAPI 3.1. Kehityskontissa ne ovat valmiina.
