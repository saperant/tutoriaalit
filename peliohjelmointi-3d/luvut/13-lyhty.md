# Lyhty

Edelliset luvut tekivät osat. Tässä luvussa ne kootaan pieneksi
kolmannen persoonan peliksi, *Lyhdyksi*: hahmo kulkee tasossa, jossa on
ramppi, portaat ja muuri, ja kerää neljä lyhtyä. Peli on pieni, mutta
siinä on jokainen kolmiulotteisen pelin rakenneosa oikealla paikallaan,
ja sen askel näyttää, missä järjestyksessä osat ajetaan.

## Tila ja resurssit

Pelin tila on yksi rakenne. Ladatut resurssit ja niistä johdettu
törmäysmaailma eivät muutu pelin aikana; hahmo, kamera ja lyhdyt
muuttuvat.

```{.cpp tiedosto="esimerkit/13-lyhty/peli.hpp" osa="tila"}
```

Lataus muuntaa tason kolmeen muotoon. Solmut, joilla on verkko, ovat
sekä piirrettäviä kappaleita että törmäysmaailman kolmioita. Tyhjät
solmut ovat merkkejä, jotka tunnistetaan nimestä.

```{.cpp tiedosto="esimerkit/13-lyhty/peli.hpp" osa="lataa"}
```

## Askel

```{.dot otsikko="Lyhdyn yksi kiinteä askel. Järjestys on olennainen: kamera lasketaan hahmon liikkeen jälkeen ja piirtolista kameran jälkeen."}
digraph {
  rankdir=LR; nodesep=0.25; ranksep=0.2;
  node [width=0, height=0, margin="0.1,0.06"];
  syote [label="syöte\nkameran\nsuhteen"];
  hahmo [label="hahmo-ohjain\n(kapseli, BVH)"];
  peli [label="pelisäännöt\n(lyhdyt)"];
  anim [label="animaatio\n(painot, aika)"];
  kamera [label="kamera\n(säde,\npehmennys)"];
  lista [label="karsinta ja\npiirtolista"];
  syote -> hahmo -> peli -> anim -> kamera -> lista;
}
```

Syöte tulkitaan kameran suhteen: "eteen" on kameran katselusuunta maan
tasossa. Tämä on kolmannen persoonan pelin tavallisin ohjaus, ja se on
syy siihen, että kameran kääntö on pelin tilaa eikä pelkkää piirtoa.

```{.cpp tiedosto="esimerkit/13-lyhty/peli.hpp" osa="liike"}
```

Itse askel kutsuu edellisten lukujen osia järjestyksessä. Hahmo-ohjain
liikuttaa kapselia, hahmon suunta ja animaation paino seuraavat
liikettä eksponentiaalisella pehmennyksellä, kamera päivitetään, ja
lopuksi tarkistetaan, koskeeko hahmo lyhdyn laukaisupalloa.

```{.cpp tiedosto="esimerkit/13-lyhty/peli.hpp" osa="paivita"}
```

Kamera on luvun *Kamerat* kiertokamera kahdella lisäyksellä: säde
heitetään koko törmäysmaailmaan BVH:n läpi, ja lähemmäs tullaan heti
mutta takaisin kauemmas palataan pehmeästi.

```{.cpp tiedosto="esimerkit/13-lyhty/peli.hpp" osa="kamera"}
```

Hahmon poosi on kahden leikkeen sekoitus. Paino seuraa sitä, liikkuuko
hahmo, joten seisomaan jäävä hahmo ei pysähdy kesken askeleen vaan
liukuu lepoasentoon.

```{.cpp tiedosto="esimerkit/13-lyhty/peli.hpp" osa="poosi"}
```

Piirtoa varten kappaleet karsitaan näkymäkartiolla. Kappaleita on niin
vähän, että ne testataan yksitellen; suuremmassa tasossa tässä olisi
luvun *Näkyvyyskarsinta* hierarkia.

```{.cpp tiedosto="esimerkit/13-lyhty/peli.hpp" osa="piirtolista"}
```

## Pääohjelma ja toisto

Pääohjelma lukee syötteen tiedostosta ja ajaa pelin kiinteällä
askeleella. Syöte on tallenne samassa mielessä kuin taidossa
*Peliohjelmointi*: koska askel on kiinteä ja peli deterministinen, sama
tiedosto tuottaa aina saman pelin, ja koko peli on yksi regressiotesti.

```{.cpp tiedosto="esimerkit/13-lyhty/main.cpp" osa="silmukka"}
```

```{.tuloste tiedosto="esimerkit/13-lyhty.odotettu"}
```

Lokista näkyy jokaisen osan toiminta. Hahmo nousee rampin (korkeus
kasvaa nollasta puoleentoista metriin), laskeutuu portaat, kiertää
muurin ja kerää lyhdyt. Kameran etäisyys on yleensä viisi metriä,
mutta muurin ja tornin lähellä säde lyhentää sen alle kahteen metriin.
Näkyvien kappaleiden määrä vaihtelee kymmenestä kahteen sen mukaan,
mihin kamera katsoo. Kentän poikki juostessa hahmo hyppää, ja
viidennellätoista sekunnilla se on ilmassa.

![Kuusi ruutua pelistä kolmen sekunnin välein: ramppi, portaat, muurin
kierto, lyhty tornin vieressä ja juoksu kentän poikki. Hahmon raajat
liikkuvat kävelyleikkeen mukaan.](kuvat/lyhty.png){width=100%}

## Mitä pelistä puuttuu

Lyhty on runko. Siitä puuttuvat ääni, käyttöliittymä, valikot ja
tallennus, jotka toimivat kuten kaksiulotteisessa pelissä (taito
*Peliohjelmointi*). Piirto tapahtuu samalla askeleella kuin simulaatio;
oikea peli piirtäisi omaan tahtiinsa ja interpoloisi hahmon ja kameran
kahden askeleen välillä. Hahmo-ohjaimen puutteet on lueteltu luvussa
*Hahmon liike*. Ikkunaa ja reaaliaikaista syötettä varten tarvitaan
alustakerros, kuten SDL, ja renderöijäksi grafiikkarajapinta; kumpikaan
ei muuta tässä esitettyä rakennetta.

## Käytännössä

- **Järjestys on osa suunnittelua.** Syöte, liike, säännöt, animaatio,
  kamera, piirtolista. Väärä järjestys näkyy ruudun viiveenä tai
  tärinänä.
- **Yksi tila, monta lukijaa.** Törmäysmaailma, piirtolista ja
  pelisäännöt johdetaan samasta ladatusta tasosta, mutta kukin omaan
  muotoonsa.
- **Tallennettu syöte on paras testi.** Kokonaisen pelin ajo
  käsikirjoituksesta paljastaa virheet, jotka yksittäisten osien testit
  päästävät läpi.
- **Loki ennen kuvaa.** Paikka, tila ja laskurit tekstinä kertovat
  enemmän kuin ruudun tuijottaminen, ja ne voi tarkistaa koneellisesti.

## Itsearviointi

- Osaat luetella kolmannen persoonan pelin askeleen vaiheet oikeassa
  järjestyksessä ja perustella järjestyksen.
- Osaat selittää, miten yhdestä ladatusta tasosta syntyvät
  törmäysmaailma, piirrettävät kappaleet ja pelin merkit.
- Osaat tulkita syötteen kameran suhteen ja kytkeä hahmon suunnan ja
  animaation liikkeeseen.
- Osaat tehdä kokonaisesta pelistä regressiotestin tallennetulla
  syötteellä.
