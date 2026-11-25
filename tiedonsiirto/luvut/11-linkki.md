# Kokonainen linkki ja simulaation testaus

Edellisten lukujen osat toimivat erikseen, kun muut osat ovat
ihanteellisia: ajoitus tunnetaan, vaihe tunnetaan ja kohina on
kalibroitu. Todellinen vastaanotin joutuu ratkaisemaan kaiken kerralla
pelkästä vastaanotetusta signaalista. Tässä luvussa rakennetaan pieni
pakettilinkki alusta loppuun ja testataan se. Lopuksi käydään läpi,
miten Monte Carlo -tuloksen luotettavuus arvioidaan.

## Paketin rakenne

Lähetin muuttaa tavut biteiksi, lisää loppuun CRC-16:n ja moduloi bitit
QPSK-symboleiksi. Paketin alkuun tulee alkuosa, joka on 13 merkin
Barker-koodi kahdesti peräkkäin. Toistoa käytetään taajuusvirheen
estimointiin. Symbolit suodatetaan RRC-pulssilla, neljä näytettä
symbolia kohti.

```{.python tiedosto="esimerkit/11-linkki/linkki.py" osa="lahetin"}
```

Kanava viivästää pakettia tuntemattoman määrän näytteitä, lisää
taajuus- ja vaihevirheen sekä kohinan:

```{.python tiedosto="esimerkit/11-linkki/linkki.py" osa="kanava"}
```

## Vastaanotin

Vastaanotin tekee vaiheet luvun 8 suosittelemassa järjestyksessä:

1. **Sovitettu suodin** (luku 5).
2. **Kehys ja ajoitus**: alkuosan korrelaatio jokaisella näytteellä.
   Suurin itseisarvo kertoo sekä kehyksen alun että parhaan
   näytevaiheen (luku 8). Tässä yksinkertaisessa vastaanottimessa
   kellovirhettä ei ole, joten näytevaihe pysyy paketin ajan samana.
3. **Karkea taajuus**: alkuosan puoliskojen vaihe-ero. Kun alkuosan
   modulaatio poistetaan kertomalla sen konjugaatilla, jäljelle jää
   kanavan kierto, joka kasvaa taajuusvirheen verran 13 symbolissa.
4. **Vaihe**: korrelaatio alkuosaan taajuuskorjauksen jälkeen. Koska
   alkuosa tunnetaan, neljän kulman epävarmuutta ei synny (luku 7).
5. **Vaiheen seuranta**: päätösohjattu toisen asteen silmukka.
6. **Päätökset ja CRC.**

```{.dot otsikko="Pakettivastaanottimen vaiheet. Alkuosaa käytetään kolmeen estimaattiin; silmukka seuraa vaihetta paketin loppuun."}
digraph vastaanotin {
  rankdir=LR; nodesep=0.2; ranksep=0.25;
  node [shape=box, fontsize=10];
  suodin [label="sovitettu\nsuodin"];
  kehys [label="kehys ja\najoitus"];
  taajuus [label="karkea\ntaajuus"];
  vaihe [label="vaihe"];
  seuranta [label="vaiheen\nseuranta"];
  paatos [label="päätökset\nja CRC"];
  suodin -> kehys -> taajuus -> vaihe -> seuranta -> paatos;
}
```

```{.python tiedosto="esimerkit/11-linkki/linkki.py" osa="vastaanotin"}
```

## Pakettivirhesuhde

Linkkiä verrataan ihanteelliseen vastaanottimeen, joka tuntee
ajoituksen ja vaiheen. Sen pakettivirhesuhde on $1 - (1 - P_b)^n$,
missä $n$ on paketin bittien määrä. Jokaisella paketilla on eri
satunnainen viive, taajuus- ja vaihevirhe.

```{.python tiedosto="esimerkit/11-linkki/main.py" osa="per"}
```

```{.tuloste tiedosto="esimerkit/11-linkki.odotettu"}
```

Ilman vaiheen seurantaa linkki kadottaa puolet paketeista vielä
10 dB:llä. Syy ei näy kohinattomassa testissä: alkuosan 13 symbolin
taajuusestimaatissa on kohinan aiheuttama pieni virhe, joka kertyy 136
datasymbolin aikana kymmenien asteiden vaihevirheeksi. Päätösohjattu
seuranta korjaa kertyneen virheen, ja toteutushäviö ihanteelliseen
verrattuna on enää noin 0,2 dB. Tällaiset ongelmat löytyvät vain vertaamalla koko ketjua
teoriaan kohinan kanssa.

## Simulaation testaus

Simulaatiokoodi on ohjelmistoa, ja sen virheet ovat petollisia: väärä
kohinan taso, puolen näytteen ajoitusvirhe tai väärä normitus tuottaa
uskottavan näköisen käyrän, joka on desibelejä väärässä. Testit kannattaa
jakaa kolmeen ryhmään.

**Kohinattomat testit** tarkistavat, että ketju on oikein, kun kohinaa
ei ole. Ne ajetaan monella satunnaisella kanavalla, koska rajatapaukset
(viive nolla, vaihe lähellä $\pm\pi$, suurin taajuusvirhe) löytyvät
helpoimmin satunnaisilla parametreilla.

```{.python tiedosto="esimerkit/11-linkki/test_linkki.py" osa="kohinaton"}
```

**Rajatestit** tarkistavat normitukset ja virhetilanteet: lähetteen
energia symbolia kohti, CRC:n toiminta ja katkenneen paketin käsittely.

```{.python tiedosto="esimerkit/11-linkki/test_linkki.py" osa="rajat"}
```

**Tilastolliset testit** vertaavat kohinaista tulosta teoriaan. Ne
eivät voi vaatia tarkkaa arvoa, koska tulos on satunnaismuuttuja. Ne
testaavat, onko havainto teorian valossa uskottava: tässä binomitesti
vaatii, että havaitun virhemäärän $p$-arvo on yli 0,001. Kiinteä siemen
tekee testistä toistettavan. Merkitsevyystaso valitaan niin, että
testi epäonnistuu vain, jos simulaatiossa on todellinen virhe.

```{.python tiedosto="esimerkit/11-linkki/test_linkki.py" osa="tilasto"}
```

## Kuinka monta virhettä tarvitaan?

Monte Carlo -tuloksen tarkkuus riippuu virheiden määrästä, ei bittien
määrästä. Kun virheitä on $N_e$, bittivirhesuhteen suhteellinen
keskihajonta on noin $1/\sqrt{N_e}$. Sata virhettä antaa noin 10 %:n
keskihajonnan ja 95 %:n luottamusvälin, joka on noin ±20 %. Wilsonin
luottamusväli toimii myös pienillä virhemäärillä:

```{.python tiedosto="esimerkit/11-luottamus.py" osa="vali"}
```

Nolla virhettä ei tarkoita, että virhesuhde olisi nolla. Kun $n$
bitissä ei ole yhtään virhettä, 95 %:n yläraja on noin $3/n$:

```{.python tiedosto="esimerkit/11-luottamus.py" osa="nolla"}
```

```{.tuloste tiedosto="esimerkit/11-luottamus.odotettu"}
```

Siksi luvun 6 simulaatio jatkui, kunnes virheitä oli 400, ja luvun 9
tulos yhdellä virheellä oli vain suuntaa antava. Pienten
virhesuhteiden simulointi on kallista: $10^{-6}$ ja sata virhettä vaatii
sata miljoonaa bittiä. Kun tarvitaan pienempiä virhesuhteita, käytetään
teoreettista ekstrapolointia, painotusotantaa (*importance sampling*)
tai laitteistokiihdytettyä simulointia.

## Käytännössä

- **Rakenna vertailukohta ensin.** Ihanteellinen vastaanotin, joka
  tuntee kanavan, antaa rajan, jota vasten todellisen vastaanottimen
  toteutushäviö mitataan.
- **Testaa kohinattomana, rajoilla ja tilastollisesti.** Kohinaton testi
  löytää logiikkavirheet, rajatesti normitukset ja tilastollinen
  testi kalibroinnin.
- **Simuloi, kunnes virheitä on riittävästi.** Pysäytä virhemäärään,
  ei bittimäärään, ja raportoi luottamusväli tai virhemäärä tuloksen
  rinnalla.
- **Kiinnitä siemenet.** Käytä `numpy.random.default_rng`-generaattoria
  kiinteällä siemenellä, jotta tulokset ovat toistettavia ja testit
  deterministisiä. Älä käytä globaalia satunnaislukutilaa.
- **Mallinna kanava satunnaisilla parametreilla.** Jokaisella paketilla
  eri viive, taajuus ja vaihe paljastaa rajatapaukset, joita kiinteä
  testikanava ei löydä.

## Itsearviointi

- Osaat rakentaa pakettilinkin, jossa on alkuosa, kehys- ja
  ajoitushaku, taajuus- ja vaihe-estimaatti, vaiheen seuranta ja
  CRC-tarkistus.
- Osaat mitata vastaanottimen toteutushäviön ihanteelliseen
  vastaanottimeen verrattuna.
- Osaat kirjoittaa simulaatiokoodille kohinattomat, raja- ja
  tilastolliset testit.
- Osaat arvioida Monte Carlo -tuloksen luotettavuuden virhemäärästä ja
  laskea luottamusvälin.
