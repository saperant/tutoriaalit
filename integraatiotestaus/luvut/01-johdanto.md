# Johdanto {.runko-johdanto}

Yksikkötesti kertoo, että funktio tekee mitä sen kirjoittaja ajatteli.
Se ei kerro, ajatteliko kirjoittaja oikein tietokannasta, välimuistista,
viestijonosta tai toisesta palvelusta. Suuri osa tuotannon vioista
syntyy juuri näissä saumoissa: SQL-lause toimii SQLitessä mutta ei
PostgreSQLissä, rajoite hylkää rivin, jonka väärennös hyväksyi,
aikaleimasta puuttuu aikavyöhyke, verkko hidastuu ja aikaraja laukeaa,
tai toinen palvelu muuttaa vastauksensa muotoa.

*Integraatiotesti* ajaa oman koodin oikeaa riippuvuutta vasten. Ennen
kontteja se tarkoitti yhteistä testitietokantaa, jonka sisältö oli aina
vähän rikki, tai asennusohjetta, jota kukaan ei jaksanut seurata. Nyt
riippuvuus käynnistetään testin alussa kertakäyttöiseen konttiin ja
poistetaan lopuksi. *Testcontainers* on kirjasto, joka tekee tämän
testikoodista käsin: kontti on testin fixture siinä missä mikä tahansa
muukin olio.

Tämä tutoriaali opettaa integraatiotestauksen yhden esimerkkisovelluksen
avulla:

1. testipyramidi ja se, mitä yksikkötesti ei näe (luku 2),
2. Testcontainers: kontin elinkaari, odotus ja oma kuva (luku 3),
3. pytestin fixturet ja niiden laajuudet konttien kanssa (luku 4),
4. testidata, migraatiot ja testien eristys (luku 5),
5. testikaksoiset ja milloin oikea riippuvuus on parempi (luku 6),
6. välimuisti ja viestijono oikeita palveluita vasten (luku 7),
7. verkkovikojen simulointi (luku 8),
8. sopimustestaus palvelujen välillä (luku 9),
9. integraatiotestit CI:ssä (luku 10).

## Esitiedot ja rajaus

Lukija tuntee Pythonin ja pytestin perusteet (taito *Python
työkaluohjelmointiin*:
fixturet, parametrointi), SQL:n (taito *SQL ja relaatiotietokannat*:
transaktiot, rajoitteet, indeksit) sekä kontit (taito *Kontit ja pilvi-infrastruktuuri*:
kuvat, Dockerfile, verkot). Taustapalveluiden puolelta *Taustapalvelut*
käsittelee testipyramidin ja Testcontainersin lyhyesti Javan ja
Springin näkökulmasta; tämä tutoriaali syventää aihetta kielestä
riippumattomasti.

## Esimerkkisovellus

Esimerkkinä on pieni varastopalvelu. Se pitää kirjaa tuotteista ja
niiden saldoista PostgreSQLissä, varaa tuotteita tilauksille, hakee
hinnat ulkoisesta hintapalvelusta HTTP:llä, pitää hintoja välimuistissa
Redisissä ja julkaisee varaustapahtumat Redis Streamsiin laskutuksen
luettavaksi. Kokoonpano on tavallinen taustapalvelu pienoiskoossa:

```{.dot otsikko="Varastopalvelu ja sen riippuvuudet"}
digraph {
  rankdir=LR;
  node [width=1.4];
  palvelu [label="VarastoPalvelu\n(Python)"];
  pg [label="PostgreSQL\ntuotteet, varaukset", shape=cylinder];
  redis [label="Redis\nhintavälimuisti", shape=cylinder];
  virta [label="Redis Streams\nvaraukset", shape=cylinder];
  hinnat [label="Hintapalvelu\n(HTTP + JSON)"];
  laskutus [label="Laskutus\n(kuluttajaryhmä)"];
  palvelu -> pg [label="SQL"];
  palvelu -> redis [label="GET/SET"];
  palvelu -> hinnat [label="GET /hinnat/{sku}"];
  palvelu -> virta [label="XADD"];
  virta -> laskutus [label="XREADGROUP"];
}
```

Palvelun ydin on lyhyt. Se riippuu vain rajapinnoista, joten
yksikkötesti voi antaa sille väärennökset ja integraatiotesti oikeat
toteutukset:

```{.python tiedosto="esimerkit/varasto/palvelu.py" osa="palvelu"}
```

Sovellus on hakemistossa `esimerkit/varasto/`:

| Tiedosto | Sisältö |
|----------|---------|
| `malli.py` | tietomalli ja poikkeukset |
| `varasto.py` | tallennuksen rajapinta, PostgreSQL ja muistiväärennös |
| `migraatiot.py`, `migraatiot/` | skeema numeroituina SQL-tiedostoina |
| `hinnat.py` | hintapalvelun asiakas aikarajoin ja uudelleenyrityksin |
| `valimuisti.py` | hintojen välimuisti Redisissä |
| `tapahtumat.py` | varaustapahtumat Redis Streamsissä |
| `palvelu.py` | liiketoimintalogiikka |

Testien apuvälineet ovat hakemistossa `testiapu/` (konttikuvat, konttien
luonti, testidata), testit hakemistossa `testit/` ja testien
apupalvelut (hintapalvelun väärennös ja vikaproxy) hakemistossa
`apukuva/`. Lukujen omat esimerkit ovat hakemistoissa `luku02/` …
`luku10/`.

Tietomalli on tarkoituksella pieni, mutta siinä on oikeiden
järjestelmien kompastuskivet: SKU on yksilöivä kirjainkoosta
riippumatta, saldo ei saa mennä negatiiviseksi, aikaleimat tallennetaan
aikavyöhykkeen kanssa ja samanaikaiset varaukset eivät saa ylivarata.

```{.python tiedosto="esimerkit/varasto/malli.py"}
```

## Esimerkkien ajaminen

Esimerkit tarvitsevat Dockerin. Kehityskontissa
(`.devcontainer/integraatiotestaus`) kontti käyttää isännän
Docker-sokettia, ja kaikki Python-paketit ovat valmiina. Muualla
tarvitaan Docker sekä paketit, jotka on lueteltu tiedostossa
`esimerkit/luku10/vaatimukset.txt`.

```text
make -C esimerkit                 # tarkistukset, testit, esimerkit
make -C esimerkit pytest          # vain testit/
make -C esimerkit luku06/valehteleva
```

Ensimmäinen ajo lataa PostgreSQL-, Redis- ja Python-kuvat (yhteensä
noin 580 Mt), seuraavat käyttävät paikallisia kopioita. Koko sarja
kestää kirjoittajan koneella noin puoli minuuttia, josta suurin osa on
konttien käynnistämistä.

Kaikkien esimerkkien tulosteet verrataan tallennettuihin. Siksi ne eivät
tulosta konttien tunnisteita, satunnaisia porttinumeroita tai aikoja,
vaan vain asiat, jotka eivät vaihdu ajosta toiseen. Testien tuloste on
pytestin tavallinen pisterivi.

## Mitä integraatiotesti ei ole

Integraatiotesti ei korvaa yksikkötestejä eikä päästä päähän -testejä.
Se on hitaampi kuin yksikkötesti ja kattaa vähemmän kuin koko
järjestelmän testi. Tämän tutoriaalin näkökulma on yhden palvelun
integraatiotesti: oma koodi ja sen välittömät riippuvuudet. Monen
palvelun yhteistoiminta varmistetaan sopimustesteillä (luku 9), ei
käynnistämällä koko järjestelmää jokaisessa testissä.
