# Mittauskäynnistys ja etätodennus

Turvallinen käynnistys päättää laitteessa: kelvoton kuva ei
käynnisty. **Mittauskäynnistys** (*measured boot*) ei päätä mitään,
vaan kirjaa. Jokainen vaihe tiivistää seuraavan ennen sen ajamista ja
tallentaa tiivisteen tavalla, jota myöhemmät vaiheet eivät voi
väärentää. Laite voi sitten todistaa ulkopuoliselle, mitä se on
käynnistänyt (**etätodennus**, *remote attestation*), ja palvelu
päättää, luottaako se laitteeseen.

Molemmat tarvitaan. Turvallinen käynnistys estää vieraan koodin, mutta
ei kerro palvelimelle mitään. Mittauskäynnistys kertoo palvelimelle,
ajaako laite hyväksyttyä versiota, vaikka kaikki allekirjoitetut
versiot kelpaisivat käynnistykseen.

## Laajennettava rekisteri

Mittaukset kootaan rekisteriin, jota ei voi asettaa vaan ainoastaan
**laajentaa** (TPM:ssä *platform configuration register*, PCR):

```{.python tiedosto="esimerkit/05-mittaus.py" osa="pcr"}
```

Koska uusi arvo on tiiviste vanhasta ja mittauksesta, rekisterin
loppuarvo riippuu jokaisesta mittauksesta ja niiden järjestyksestä.
Haittaohjelma, joka pääsee suoritukseen, voi laajentaa rekisteriä
mutta ei palauttaa sitä arvoon, joka vastaisi aitoa ketjua: se
vaatisi tiivistefunktion murtamista.

```{.python tiedosto="esimerkit/05-mittaus.py" osa="kaynnistys"}
```

Rekisterin lisäksi laite pitää **tapahtumalokia** (*event log*):
luetteloa mitatuista osista ja niiden tiivisteistä. Loki ei ole
suojattu, mutta todentaja voi toistaa sen ja verrata tulosta
rekisteriin.

## Etätodennus

Todentaja lähettää satunnaisen haasteen (*nonce*). Laite allekirjoittaa
haasteen ja rekisterin arvon **todennusavaimella**, joka ei koskaan
poistu laitteesta (TPM:ssä *attestation key*). Todentaja tarkistaa
allekirjoituksen, toistaa lokin ja vertaa mittauksia hyväksyttyjen
versioiden luetteloon:

```{.dot otsikko="Etätodennus. Haaste tekee lainauksesta kertakäyttöisen, ja rekisterin arvo sitoo sen siihen, mitä laite todella käynnisti. Loki kertoo todentajalle, mistä osista rekisterin arvo syntyi."}
digraph {
  layout=neato; splines=false;
  node [shape=point, width=0.01, height=0.01, style=invis];
  edge [arrowsize=0.7];
  d0 [label="todentaja (taustajärjestelmä)", shape=box, style="rounded,filled", width=0, height=0.3, pos="0.00,0!"];
  dL [pos="0.00,-2.20!"];
  d0 -> dL [arrowhead=none, style=dotted];
  l0 [label="laite", shape=box, style="rounded,filled", width=0, height=0.3, pos="3.40,0!"];
  lL [pos="3.40,-2.20!"];
  l0 -> lL [arrowhead=none, style=dotted];
  d1 [pos="0.00,-0.51!"]; l1_ [pos="3.40,-0.51!"];
  d1 -> l1_ [];
  t1 [shape=plain, style="", fontsize=9, label="1. haaste (satunnainen, kertakäyttöinen)", pos="1.70,-0.41!"];
  l2 [pos="3.40,-0.87!"]; d2_ [pos="0.00,-0.87!"];
  l2 -> d2_ [];
  t2 [shape=plain, style="", fontsize=9, label="2. lainaus: allekirjoitus(haaste, rekisteri)", pos="1.70,-0.77!"];
  l3 [pos="3.40,-1.23!"]; d3_ [pos="0.00,-1.23!"];
  l3 -> d3_ [];
  t3 [shape=plain, style="", fontsize=9, label="3. tapahtumaloki: mitä mitattiin", pos="1.70,-1.13!"];
  o4 [shape=plain, style="", fontsize=9, label=<<i>todentaja: tarkistaa allekirjoituksen,</i>>, pos="1.70,-1.59!"];
  o5 [shape=plain, style="", fontsize=9, label=<<i>toistaa lokin ja vertaa hyväksyttyihin</i>>, pos="1.70,-1.95!"];
}
```

```{.python tiedosto="esimerkit/05-mittaus.py" osa="todentaja"}
```

```{.tuloste tiedosto="esimerkit/05-mittaus.odotettu"}
```

Jokainen tarkistus torjuu eri hyökkäyksen:

- **Allekirjoitus ja haaste** estävät väärennetyn tai toistetun
  lainauksen: vanha lainaus aidolta laitteelta ei kelpaa uuteen
  haasteeseen.
- **Lokin toisto** paljastaa valehtelevan lokin: haittaohjelma voi
  kirjoittaa lokiin aitojen osien tiivisteet, mutta rekisteri sisältää
  oikeat.
- **Hyväksytyt mittaukset** ovat käytäntö: todentaja voi hylätä myös
  aidon mutta haavoittuvan version.

## TPM, DICE ja todennusavaimen alkuperä

Todennus on vain niin luotettava kuin todennusavain. PC:issä ja
palvelimissa avain on **TPM 2.0** -piirissä, jonka valmistaja on
varmentanut (*endorsement key*). Mikrokontrollereissa TPM on usein
liian kallis, ja TCG:n **DICE**-malli (*Device Identifier Composition
Engine*) tekee saman pienemmällä laitteistolla: laitteessa on
salaisuus (UDS), jota vain ROM voi lukea. ROM johtaa siitä ja
seuraavan vaiheen mittauksesta uuden salaisuuden (CDI) ja lukitsee
UDS:n. Jos ensimmäinen vaihe muuttuu, CDI ja siitä johdetut avaimet
muuttuvat, eikä muutettu ohjelmisto voi esiintyä aitona.

## Käytännössä

- **Käytä mittauksia käytäntöihin.** Palvelu voi rajata pääsyn
  laitteisiin, joiden ohjelmisto on hyväksytty, ja eristää
  muut automaattisesti.
- **Mittaa kaikki suoritettava ja asetukset**, jotka vaikuttavat
  tietoturvaan (esim. debug-tila päällä). Mittaamaton osa on sokea
  piste.
- **Haaste joka kerta.** Ilman tuoretta haastetta vanha lainaus
  voidaan toistaa.
- **Pidä hyväksyttyjen mittausten luettelo julkaisuputkessa**, jolloin
  uusi versio hyväksytään samalla kun se julkaistaan.

## Itsearviointi

- Osaat selittää turvallisen käynnistyksen ja mittauskäynnistyksen
  eron ja sen, miksi molempia tarvitaan.
- Osaat toteuttaa laajennettavan rekisterin ja tarkistaa
  tapahtumalokin sitä vasten.
- Osaat kuvata etätodennuksen haasteineen ja kertoa, mihin
  todennusavaimen luotettavuus perustuu (TPM, DICE).
