# Kaaviot koodina

Kaavio on dokumentaation tehokkain ja lyhytikäisin osa. Hyvä kaavio
korvaa sivun tekstiä; piirto-ohjelmalla tehty kaavio on kuva, jonka
lähdetiedosto on hukassa ja jota kukaan ei uskalla muuttaa. Kun kaavio
kirjoitetaan tekstinä, se on versionhallinnassa, sen muutos näkyy
katselmoinnissa ja sen piirtää kone.

## Kolme kieltä

Yleisimmät kaaviokielet ovat Graphviz, Mermaid ja PlantUML. Sama
verkko, esimerkkikirjaston moduulien riippuvuudet, kaikilla kolmella.
Graphviz:

```{.text tiedosto="esimerkit/kaaviot/riippuvuudet.dot"}
```

Mermaid:

```{.text tiedosto="esimerkit/kaaviot/riippuvuudet.mmd"}
```

PlantUML:

```{.text tiedosto="esimerkit/kaaviot/riippuvuudet.puml"}
```

Kaikissa kuvataan solmut ja kaaret, ja asettelun tekee työkalu.
Kirjoittaja ei siirtele laatikoita, mikä on sekä vahvuus (kaavion
muuttaminen on yhden rivin muutos) että rajoitus (asettelua voi vain
ohjata vihjeillä).

| Ominaisuus | Graphviz | Mermaid | PlantUML |
|---------------------|-------------------|----------------------|-------------------|
| vahvuus | verkot ja puut, asettelu | näkyy sellaisenaan GitHubissa ja GitLabissa | UML-kaaviot kattavasti |
| sekvenssikaaviot | ei | kyllä | kyllä |
| ajoympäristö | natiivi ohjelma | JavaScript, selain | Java |
| käyttö rakennuksessa | kevyt | vaatii selaimen | vaatii JVM:n |

Tämä tutoriaalisarja käyttää Graphvizia, koska se on yksi pieni
ohjelma ilman ajoympäristöä. Yllä olevat Mermaid- ja PlantUML-lähteet
tuottaa sama generaattori kuin Graphviz-lähteen, ja testi vertaa ne
tallennettuihin, mutta niitä ei piirretä testeissä. Muita vaihtoehtoja
ovat D2 ja C4-malleille tarkoitettu Structurizr DSL, jossa malli
kuvataan kerran ja eri tasojen kaaviot ovat sen näkymiä.

## Kaavion laji tehtävän mukaan

| Kysymys | Kaavio | Esimerkki tässä tutoriaalissa |
|-----------------------------------|---------------------|-----------------------------|
| Mistä osista tämä koostuu? | lohko- tai C4-kaavio | luvut 1 ja 10 |
| Mikä riippuu mistä? | riippuvuusverkko | tämä luku |
| Missä järjestyksessä osat keskustelevat? | sekvenssikaavio | alla |
| Missä tiloissa asia voi olla? | tilakaavio | päätöksen tilat, luku 10 |
| Miten tieto kulkee? | vuokaavio | luvun 4 putki |

Sekvenssikaavio näyttää viestit aikajärjestyksessä osapuolten
välillä. Lukeman vastaanotto Mermaidilla:

```{.text tiedosto="esimerkit/kaaviot/sekvenssi.mmd"}
```

Lähde on luettavissa piirtämättäkin: osapuolet, viestit ja haarat ovat
omilla riveillään. Sama PlantUML-kielellä eroaa lähinnä nuolten
merkinnässä. Sekvenssikaavio kannattaa piirtää vain tärkeimmistä
tapauksista ja niistä, joissa järjestys yllättää; jokaista kutsua ei
dokumentoida.

## Kaavio koodista

Riippuvuusverkko on tieto, joka on jo koodissa. Käsin piirrettynä se
on väärin heti, kun joku lisää tuonnin. Esimerkkien generaattori lukee
paketin lähdetiedostot ja kerää niiden `import`-lauseet:

```{.python tiedosto="esimerkit/kaaviot/riippuvuudet.py" osa="kaaret"}
```

Tulos on tämän luvun alun Graphviz-lähde, josta syntyy kuva:

```{.dot tiedosto="esimerkit/kaaviot/riippuvuudet.dot" otsikko="Kirjaston saa moduulien riippuvuudet lähdekoodista tuotettuna" leveys="60%"}
```

Kaaviosta näkee arkkitehtuurin säännön, jota ei ole kirjoitettu
mihinkään: `lukema` ei riipu mistään, `tilasto` riippuu vain siitä, ja
HTTP-käsittelijä ja komentorivi ovat uloimpana. Tuotettu lähde on
versionhallinnassa, ja testi vertaa sitä generaattorin tulokseen:

```{.makefile tiedosto="esimerkit/Makefile" osa="kaaviot"}
```

Jos joku lisää moduuliin `lukema` tuonnin moduulista `palvelu`, testi
epäonnistuu, kunnes kaavio päivitetään, ja katselmoija näkee
erotuksessa uuden nuolen, joka kulkee väärään suuntaan. Kaaviosta
tulee näin arkkitehtuurin vahti. Sama ajatus on tämän tutoriaalisarjan
laitteistopuolen ajoituskaavioissa: kaavio tuotetaan simulaatiosta, ja
testi vertaa sitä tallennettuun.

Valmiita generaattoreita on joka kielelle: pydeps ja pyreverse
Pythonille, Doxygenin kutsu- ja sisällytysverkot C:lle ja C++:lle,
jdeps Javalle ja madge JavaScriptille. Tietokannan skeemasta saa
ER-kaavion (esimerkiksi SchemaSpy) ja infrastruktuurin kuvauksesta
verkkokaavion.

## Milloin kaavio vanhenee

Kaaviot jakautuvat kahteen ryhmään sen mukaan, mistä niiden tieto
tulee:

- **Koodista johdettava** (riippuvuudet, luokat, tietokannan rakenne):
  generoi, älä piirrä. Käsin piirretty versio on väärin viikon
  kuluttua.
- **Päätöksistä johdettava** (konteksti, kontit, tärkeimmät
  sekvenssit): piirrä käsin tekstinä ja pidä yleisellä tasolla. Mitä
  vähemmän yksityiskohtia, sitä harvemmin kaavio muuttuu.

Vaarallisin on välimuoto: käsin piirretty yksityiskohtainen kaavio,
joka näyttää tarkalta ja on väärin.

## Käytännössä

- **Yksi kaavio, yksi kysymys.** Kaavio, joka näyttää rakenteen,
  tietovirrat ja käyttöönoton yhtä aikaa, ei näytä mitään niistä.
- **Otsikko ja selite.** Kuvateksti kertoo, mitä kaavio esittää. Jos
  väreillä tai muodoilla on merkitys, se kerrotaan.
- **Nuolille teksti.** Nuoli ilman tekstiä voi tarkoittaa kutsua,
  tietovirtaa tai riippuvuutta. Lukija arvaa väärin.
- **Enintään kymmenkunta laatikkoa.** Suurempi kaavio jaetaan tasoihin
  kuten C4:ssä.
- **Lähde versionhallintaan, kuva rakennukseen.** Jos kuva
  tallennetaan, testi varmistaa, että se vastaa lähdettään.
- **Teksti rinnalle.** Kaavio näyttää rakenteen, mutta ei perustele
  sitä. Kappale kaavion vieressä kertoo, mitä siitä pitää huomata.

## Itsearviointi

- Osaat kirjoittaa riippuvuusverkon ja sekvenssikaavion tekstinä.
- Osaat valita kaaviolajin sen mukaan, mihin kysymykseen kaavio
  vastaa.
- Osaat tuottaa kaavion lähdekoodista ja selittää, miten testi pitää
  sen ajan tasalla.
- Osaat erottaa kaaviot, jotka kannattaa generoida, niistä, jotka
  piirretään käsin.
