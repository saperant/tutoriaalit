# Pelipalvelimet ja otteluiden muodostus

Yksittäinen pelipalvelin ajaa yhtä tai muutamaa ottelua. Pelaajia
palvelee kokonainen järjestelmä: otteluiden muodostus, palvelinten
käynnistys ja sammutus kysynnän mukaan, alueet viiveen pienentämiseksi
ja istuntojen hallinta. Rakenne on hajautettu järjestelmä (taidot
*Kontit ja pilvi* ja *Järjestelmäsuunnittelu*), mutta muutama osa on
pelikohtainen.

## Taitoluokitus

Tasainen ottelu on hauska molemmille. Otteluiden muodostus tarvitsee
arvion pelaajan taidosta, jota ei voi mitata suoraan, vain otteluiden
tuloksista. *Elo*-luku ennustaa voiton todennäköisyyden luokitusten
erotuksesta ja päivittää luokitusta sen mukaan, kuinka yllättävä tulos
oli:

```{.cpp tiedosto="esimerkit/12-elo.cpp" osa="elo"}
```

Jono järjestetään luokituksen mukaan, ja lähekkäiset pelaavat
keskenään. Esimerkissä 200 pelaajalla on piilossa oleva todellinen
taito, ja kaikki aloittavat luvusta 1 500:

```{.cpp tiedosto="esimerkit/12-elo.cpp" osa="jono"}
```

```{.tuloste tiedosto="esimerkit/12-elo.odotettu"}
```

Alussa luokitus ei kerro mitään, ja vain viidesosa otteluista on
tasaisia (taitoero alle 100), kuten satunnaisesti muodostetuissa.
Kymmenen ottelun jälkeen luokitus jo auttaa, ja 200 ottelun jälkeen
83 % otteluista on tasaisia. Virhe pienenee hitaasti, koska Elon
K-kerroin on vakio: se ei tiedä, kuinka varma arvio on.

*Glicko* ja *Glicko-2* lisäävät luokitukseen epävarmuuden (rating
deviation): uuden pelaajan luku liikkuu nopeasti, vakiintuneen hitaasti,
ja pitkä tauko kasvattaa epävarmuutta. *TrueSkill* (Microsoft) ja sen
jatkajat laajentavat mallin joukkuepeleihin. Kaikki ovat
tilastollisia malleja, joiden parametrit sovitetaan pelin dataan.

## Ottelun muodostus

Ottelujonolla on kolme tavoitetta, jotka ovat ristiriidassa: tasaiset
ottelut, lyhyt odotus ja hyvä yhteys. Tavallinen ratkaisu on *laajeneva
ikkuna*: aluksi haetaan vastustajaa kapealta luokitusväliltä ja samalta
alueelta, ja väliä laajennetaan odotusajan kasvaessa. Pieni pelaajamäärä
(yöaika, harvinainen pelitila) pakottaa valitsemaan nopeuden ja
tasaisuuden välillä; jonon odotusaika ja otteluiden tasaisuus
seurataan mittareina.

Alueet ratkaisevat viiveen: pelaaja ohjataan palvelimelle, jonka
mitattu ping on pienin, ja ottelut muodostetaan alueen sisällä. Yhteinen
ottelu eri alueiden pelaajille käynnistetään palvelimella, joka
minimoi suurimman viiveen.

## Istunnon elinkaari

Palvelin hallitsee jokaista pelaajan istuntoa tilakoneena, jonka
ajastimet ovat palvelimen kellossa:

```{.cpp tiedosto="esimerkit/12-istunnot.cpp" osa="tilat"}
```

```{.tuloste tiedosto="esimerkit/12-istunnot.odotettu"}
```

Katkennut yhteys ei heti päätä peliä. Armonajan sisällä palaava
pelaaja jatkaa samasta paikasta (uudelleenliittyminen tarvitsee koko
tilan, ei deltaa), ja armonajan jälkeen istunto päättyy keskeytykseen,
jonka seuraukset (luokitus, rangaistukset) määritellään säännöissä.
Lataukselle on oma aikaraja, ettei yksi hidas pelaaja pidä muita
jonossa.

## Palvelinten skaalaus

- **Yksi ottelu, yksi prosessi** (tai kontti). Kaatuminen vaikuttaa
  vain yhteen otteluun, ja prosessin voi sammuttaa ottelun jälkeen.
- **Varastossa valmiita palvelimia.** Käynnistys vie sekunteja, joten
  valmiiksi käynnistettyjä odottaa varalla kysynnän mukaan.
  Kubernetes-pohjainen Agones ja pilvipalveluiden pelipalvelinpalvelut
  hoitavat tämän.
- **Pelaajan tila erillään pelipalvelimesta.** Tavarat, luokitus ja
  edistyminen tallennetaan taustapalveluun transaktioina, ei
  pelipalvelimen muistiin.

## Käytännössä

- **Luokitus epävarmuuden kanssa** (Glicko-2, TrueSkill) on parempi kuin
  pelkkä Elo; näytä pelaajille yksinkertaistettu taso, älä
  sisäistä lukua.
- **Mittaa jono:** odotusaika, otteluiden luokitusero ja viive alueittain.
  Säädä laajenevan ikkunan parametreja datan perusteella.
- **Uudelleenliittyminen kuuluu suunnitteluun**: armonaika, koko tilan
  lähetys ja sama paikka pelissä.
- **Pelipalvelin on kertakäyttöinen.** Kaikki pysyvä tieto
  taustapalveluun.
- **Hinta:** tarkka otteluiden muodostus pidentää odotusta; alueet
  jakavat pelaajakunnan pienempiin jonoihin.

## Itsearviointi

- Osaat laskea Elo-luvun odotuksen ja päivityksen ja selittää
  epävarmuuden merkityksen (Glicko).
- Osaat suunnitella ottelujonon, joka tasapainottaa tasaisuuden,
  odotuksen ja viiveen.
- Osaat mallintaa istunnon elinkaaren tilakoneena armonaikoineen.
- Osaat kuvata pelipalvelinten skaalauksen ja pysyvän tilan erottamisen.
