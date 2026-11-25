# Automaatioskriptien mallit

Bashin tärkein käyttö on automaatio: asennukset, käyttöönotot,
varmuuskopiot ja ylläpitotyöt. Niille on vakiintunut joukko malleja,
jotka tekevät skriptistä turvallisen ajaa uudelleen, kokeilla etukäteen
ja keskeyttää. Tämä luku kokoaa ne. Konttien ja pilvi-infrastruktuurin
automaatiotyökalut käsitellään taidossa *Kontit ja
pilvi-infrastruktuuri*.

## Idempotenssi

Skripti on *idempotentti*, kun sen ajaminen toiseen kertaan ei muuta
mitään. Idempotentin asennusskriptin voi ajaa uudelleen keskeytyksen
jälkeen tai varmuuden vuoksi, eikä kenenkään tarvitse tietää, missä
tilassa kone oli.

Malli on *varmista*-funktio: se tarkistaa, onko haluttu tila jo voimassa,
ja muuttaa vain, jos ei ole. Funktio kertoo tekemänsä muutokset, jotta
ajon lokista näkee, mitä tapahtui.

```{.bash tiedosto="esimerkit/10-idempotentti.sh" osa="apu"}
```

```{.bash tiedosto="esimerkit/10-idempotentti.sh" osa="asennus"}
```

```{.tuloste tiedosto="esimerkit/10-idempotentti.odotettu"}
```

Toinen ajo ei tulostanut mitään, koska kaikki oli jo kunnossa. Useat
komennot ovat valmiiksi idempotentteja: `mkdir -p`, `ln -sfn`,
`install -d`, `cp` samalla sisällöllä ja `systemctl enable`. Rivin
lisäys tiedostoon (`>>`) ja `useradd` eivät ole, joten ne tarvitsevat
tarkistuksen. `grep -qxF` vertaa koko riviä kiinteänä merkkijonona,
joten rivin erikoismerkkejä ei tulkita säännöllisenä lausekkeena.

## Kuivaharjoitus

Kuivaharjoitus (*dry run*) näyttää, mitä skripti tekisi, muuttamatta
mitään. Se on välttämätön poistaville ja massamuutoksia tekeville
skripteille. Luotettava toteutus ohjaa kaikki muuttavat komennot yhden
funktion kautta, jolloin yksittäistä komentoa ei voi unohtaa:

```{.bash tiedosto="esimerkit/10-kuivaharjoitus.sh" osa="aja"}
```

```{.bash tiedosto="esimerkit/10-kuivaharjoitus.sh" osa="kaytto"}
```

Argumenteilla `-n lokit/vanhat 30` tuloste on

```{.tuloste tiedosto="esimerkit/10-kuivaharjoitus.odotettu"}
```

Komento tulostetaan `%q`-muodossa, joten tulosteen voi kopioida ja ajaa
sellaisenaan. Lukevat komennot (`find`) ajetaan myös kuivaharjoituksessa,
koska muuten ei tiedettäisi, mitä poistettaisiin.

## Atominen julkaisu

Kun uusi versio kopioidaan suoraan vanhan päälle, palvelu voi nähdä
puoliksi päivitetyt tiedostot, eikä paluu edelliseen versioon onnistu.
*Versiohakemistomallissa* jokainen versio asennetaan omaan hakemistoonsa,
ja palvelu käyttää symbolista linkkiä `nykyinen`, joka käännetään
osoittamaan uuteen versioon:

```{.bash tiedosto="esimerkit/10-julkaisu.sh" osa="vaihto"}
```

```{.dot otsikko="Linkin vaihto: uusi linkki luodaan väliaikaisella nimellä ja nimetään vanhan päälle"}
digraph {
  rankdir=LR; nodesep=0.25;
  subgraph cluster_e {
    label="ln -sfn v1.10.0 nykyinen.uusi"; color="#D9E0E3";
    e1 [label="nykyinen", shape=plaintext];
    e2 [label="nykyinen.uusi", shape=plaintext];
    ev1 [label="v1.9.0/"]; ev2 [label="v1.10.0/"];
    e1 -> ev1; e2 -> ev2;
  }
  subgraph cluster_j {
    label="mv -T nykyinen.uusi nykyinen"; color="#D9E0E3";
    j1 [label="nykyinen", shape=plaintext];
    jv1 [label="v1.9.0/"]; jv2 [label="v1.10.0/"];
    j1 -> jv2;
  }
  ev2 -> j1 [style=invis];
}
```

Version hakemisto valmistellaan nimellä `.kesken` ja nimetään valmiiksi
vasta lopuksi, joten keskeytynyt julkaisu ei jätä valmiilta näyttävää
hakemistoa. Linkin vaihto tehdään kahdessa vaiheessa: `ln -sfn` korvaa
linkin poistamalla ja luomalla, mikä ei ole atomista. Uusi linkki
luodaan siksi väliaikaisella nimellä ja nimetään vanhan päälle
`mv -T`:llä, joka on atominen uudelleennimeäminen (luku 6).

Paluu edelliseen versioon on sama vaihto toiseen suuntaan. Vanhat versiot
siivotaan, jotta levy ei täyty:

```{.bash tiedosto="esimerkit/10-julkaisu.sh" osa="siivous"}
```

`sort -V` lajittelee versionumerot oikein: `v1.10.0` on uudempi kuin
`v1.9.0`, vaikka aakkosjärjestys väittää muuta. `${JULKAISUT:?}` on
varmistus: jos muuttuja olisi tyhjä, `rm -rf` kohdistuisi juureen.

## Uudelleenyritys

Verkkokomennot epäonnistuvat tilapäisesti. *Uudelleenyritys
eksponentiaalisella viiveellä* yrittää uudelleen kasvavin välein, jotta
kuormittunut palvelu ehtii toipua:

```{.bash tiedosto="esimerkit/10-julkaisu.sh" osa="yritys"}
```

Funktio ottaa komennon taulukkona (`"$@"`), joten sitä voi käyttää minkä
tahansa komennon kanssa ilman lainausongelmia. Vain tilapäiset virheet
kannattaa yrittää uudelleen. Funktio ei erottele virheitä, joten sitä
käytetään komentoihin, joiden virheet ovat tyypillisesti tilapäisiä.
Esimerkin lopussa uudelleenjulkaisu ajetaan ilman sitä, koska jo olemassa
oleva versio on pysyvä virhe, jota uudelleenyritys vain viivästyttäisi.

```{.bash tiedosto="esimerkit/10-julkaisu.sh" osa="ajo"}
```

```{.tuloste tiedosto="esimerkit/10-julkaisu.odotettu"}
```

## Muita malleja

- **Esitarkistukset ensin.** Skripti tarkistaa tarvitsemansa komennot
  (`command -v jq > /dev/null || kuole "jq puuttuu"`), oikeudet ja
  levytilan ennen kuin muuttaa mitään.
- **Vahvistus vaarallisille toimille.** Interaktiivinen kysymys vain, kun
  syöte on pääte (`[[ -t 0 ]]`), ja valitsin `--kylla` automaatiota
  varten.
- **Ei kovakoodattuja polkuja**, vaan asetukset valitsimista tai
  ympäristömuuttujista oletusarvoineen.
- **Aikaleimattu loki virhetulosteeseen** (luku 8), jotta CI-järjestelmän
  tai cronin lokista näkee, missä vaiheessa ajo oli.

## Käytännössä

- **Idempotentit varmista-funktiot** asennukseen ja konfigurointiin.
  Skriptin on oltava turvallinen ajaa uudelleen keskeytyksen jälkeen.
- **Kaikki muuttavat komennot yhden `aja`-funktion kautta**, jolloin
  kuivaharjoitus ja lokitus kattavat ne kaikki.
- **Versiohakemistot ja symbolinen linkki** julkaisuun. Linkki käännetään
  atomisesti `mv -T`:llä, ja paluu edelliseen versioon on yksi komento.
- **`${MUUTTUJA:?}` jokaisessa `rm -rf`-polussa**, jossa on muuttuja.
- **Uudelleenyritys eksponentiaalisella viiveellä** vain tilapäisille
  virheille, ja yritysten määrä rajattuna.
- **Hinta:** idempotenssi ja kuivaharjoitus maksavat muutaman rivin
  skriptiä kohti. Ilman niitä jokainen keskeytynyt ajo on käsityötä.

## Itsearviointi

- Osaat kirjoittaa idempotentin asennusskriptin, joka kertoo tekemänsä
  muutokset ja on toisella ajokerralla hiljaa.
- Osaat toteuttaa kuivaharjoituksen niin, että yksittäinen komento ei voi
  jäädä sen ulkopuolelle.
- Osaat julkaista uuden version atomisesti symbolisen linkin vaihdolla
  ja siivota vanhat versiot.
- Osaat kirjoittaa uudelleenyritysfunktion, joka ottaa minkä tahansa
  komennon argumentteineen.
