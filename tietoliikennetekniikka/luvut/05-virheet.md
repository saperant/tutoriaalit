# Virheiden havaitseminen ja korjaus

Kohina, häipymä ja häiriöt kääntävät bittejä. Virheiden käsittelyyn on
kaksi strategiaa: **havaitseminen**, jolloin virheellinen kehys
hylätään ja tarvittaessa lähetetään uudelleen, ja **korjaus**
(*forward error correction*, FEC), jolloin vastaanotin korjaa virheet
itse lisäbittien avulla. Lankaverkot luottavat enimmäkseen
havaitsemiseen, radioverkot ja nopeat linkit korjaukseen.

## Pariteetti ja CRC

Pariteettibitti kertoo, onko ykkösiä pariton vai parillinen määrä. Se
havaitsee jokaisen yhden bitin virheen, mutta kaksi virhettä kumoaa
toisensa. **CRC** (*cyclic redundancy check*) käsittelee kehyksen
bittejä polynomin kertoimina ja laskee jakojäännöksen sovitulla
generaattoripolynomilla. Ethernetin kehyksen lopussa on 32-bittinen
CRC (FCS, *frame check sequence*), ja sama algoritmi on zlibissä ja
PNG-kuvissa:

```{.python tiedosto="esimerkit/05-crc.py" osa="crc"}
```

```{.python tiedosto="esimerkit/05-crc.py" osa="kokeet"}
```

```{.tuloste tiedosto="esimerkit/05-crc.odotettu"}
```

CRC-32 havaitsee varmasti kaikki enintään 32 bitin purskevirheet ja
Ethernetin enimmäiskokoisessa kehyksessä kaikki enintään kolmen bitin
virheet. Muuten havaitsematta jäämisen
todennäköisyys on noin $2^{-32}$. CRC suojaa satunnaisilta virheiltä
mutta **ei** tahalliselta muokkaukselta: hyökkääjä voi laskea uuden
CRC:n muokatulle datalle. Eheyden suojaamiseen tarvitaan MAC (taito
*Kryptografia*).

## Hamming-koodi

Virheenkorjaava koodi lisää dataan niin paljon rakennetta, että
vastaanotin tunnistaa, mikä bitti on kääntynyt. Hamming(7,4) lisää
neljään databittiin kolme tarkistusbittiä. Vastaanotin kertoo saadun
sanan tarkistusmatriisilla $H$; tulos (syndrooma) on nolla, jos sana on
ehjä, ja muuten se on täsmälleen virheellisen bitin sarake $H$:ssa:

```{.python tiedosto="esimerkit/05-hamming.py" osa="matriisit"}
```

Simuloidaan kanavaa, joka kääntää jokaisen bitin todennäköisyydellä
$p$:

```{.python tiedosto="esimerkit/05-hamming.py" osa="simulaatio"}
```

```{.tuloste tiedosto="esimerkit/05-hamming.odotettu"}
```

Koodi korjaa yhden virheen seitsemästä, joten lohko menee pieleen vain,
jos virheitä on vähintään kaksi. Kun $p = 0{,}001$, virhetodennäköisyys
pienenee kahdella kertaluokalla 75 %:n lisäbittien hinnalla.
Simuloitu tulos noudattaa teoriaa (harvinaisimmissa tapauksissa
satunnaisvaihtelu näkyy). Nykyjärjestelmät käyttävät tehokkaampia
koodeja – Reed–Solomon (kuitu, QR-koodit), LDPC (Wi-Fi, 5G:n data,
10GBASE-T) ja polar-koodit (5G:n ohjauskanavat) –, mutta periaate on
sama: redundanssia vastineeksi luotettavuudesta.

## Purskevirheet ja lomitus

Häipymä ja häiriöpiikit eivät käännä yksittäisiä bittejä vaan
peräkkäisiä bittejä. Yhden virheen korjaava koodi ei selviä neljän
bitin purskeesta. **Lomitus** (*interleaving*) järjestää bitit niin,
että peräkkäiset lähetetyt bitit kuuluvat eri koodisanoihin:

```{.python tiedosto="esimerkit/05-lomitus.py" osa="lomitus"}
```

```{.tuloste tiedosto="esimerkit/05-lomitus.odotettu"}
```

Lomittamattomassa lähetyksessä purske tuhoaa yhden sanan kokonaan.
Lomitettuna jokaiseen sanaan osuu yksi virhe, jonka Hamming-koodi
korjaa. Hinta on viive: vastaanottimen on odotettava koko lomituslohko
ennen purkamista. Siksi puhesovellukset käyttävät lyhyttä ja
tiedostonsiirto pitkää lomitusta.

## Käytännössä

- **Valitse strategia kanavan mukaan.** Havaitseminen ja uudelleenlähetys
  (ARQ) on tehokasta, kun virheitä on vähän ja kierrosaika lyhyt.
  FEC kannattaa, kun virheitä on paljon, viive on pitkä (satelliitti)
  tai paluukanavaa ei ole (yleislähetys). Radioverkot yhdistävät molemmat
  (HARQ).
- **CRC ei ole tarkistussumma tietoturvalle.** Käytä MAC:ia tai
  allekirjoitusta, kun muokkaus voi olla tahallista.
- **Tarkista eheys myös ylemmillä kerroksilla.** Linkkikerroksen CRC
  suojaa vain linkin, ei muistia, levyä eikä reitittimen sisäisiä
  virheitä. Siksi TCP:llä on oma tarkistussummansa ja tiedostoilla
  omat tiivisteensä.
- **Muista FEC:n viive.** Lomitus ja pitkät koodit lisäävät viivettä;
  viiveherkissä sovelluksissa (puhe, pelit, ohjaus) lyhyt koodi ja
  uudelleenlähetyksen sietäminen ovat parempia.

## Itsearviointi

- Osaat laskea CRC-32:n ja selittää, mitkä virheet se havaitsee
  varmasti ja miksi se ei suojaa tahalliselta muokkaukselta.
- Osaat koodata ja korjata Hamming(7,4)-sanan syndroomalla.
- Osaat laskea lohkovirheen todennäköisyyden koodilla ja ilman ja
  verrata sitä simulaatioon.
- Osaat selittää lomituksen hyödyn purskevirheissä ja sen hinnan
  viiveenä.
