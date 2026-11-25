# Virheiden havaitseminen ja korjaus

Kohina, häipymä ja häiriöt kääntävät bittejä. Virheiden käsittelyyn on
kaksi strategiaa: **havaitseminen**, jolloin virheellinen kehys
hylätään ja tarvittaessa lähetetään uudelleen, ja **korjaus**
(*forward error correction*, FEC), jolloin vastaanotin korjaa virheet
itse lisäbittien avulla. Lankaverkot luottavat enimmäkseen
havaitsemiseen, radioverkot ja nopeat linkit korjaukseen. Luku käy
ensin läpi havaitsemisen ja uudelleenlähetyksen ja sitten korjaavat
koodit ja lomituksen.

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

## Uudelleenlähetys: ARQ

Havaittu virhe korjataan lähettämällä kehys uudelleen. **ARQ**
(*automatic repeat request*) tarkoittaa menetelmiä, joissa
vastaanottaja kuittaa ehjät kehykset ja lähettäjä lähettää uudelleen
ne, joiden kuittaus jää tulematta. Menetelmiä on kolme, ja ne eroavat
siinä, mitä lähettäjä tekee kuittausta odottaessaan:

- **Pysähdy ja odota** (*stop-and-wait*): lähettäjä lähettää yhden
  kehyksen ja odottaa sen kuittauksen ennen seuraavaa.
- **Go-back-N**: lähettäjä lähettää kehyksiä jatkuvasti ja pitää
  kuittaamattomia matkalla enintään ikkunan verran (**liukuva
  ikkuna**). Vastaanottaja hyväksyy kehykset vain järjestyksessä,
  joten katoamisen jälkeen lähettäjä palaa kadonneeseen kehykseen ja
  lähettää kaiken siitä eteenpäin uudelleen.
- **Valikoiva toisto** (*selective repeat*): vain kadonnut kehys
  lähetetään uudelleen, ja vastaanottaja säilyttää sen jälkeen
  saapuneet kehykset puskurissa.

Menetelmien ero riippuu kahdesta luvusta: kehyksen katoamisen
todennäköisyydestä $p$ ja siitä, montako kehystä kierrosaikaan
mahtuu. Simulaatiossa aika on jaettu kehyksen mittaisiin viipaleisiin,
ja lähettäjä saa tiedon kehyksen kohtalosta `kierros` viipaletta
lähetyksen jälkeen:

```{.python tiedosto="esimerkit/05-arq.py" osa="pysahdy"}
```

```{.python tiedosto="esimerkit/05-arq.py" osa="palaa"}
```

```{.python tiedosto="esimerkit/05-arq.py" osa="valikoiva"}
```

Tehokkuus on perille toimitettujen kehysten osuus viipaleista.
Suluissa on kaavan antama arvo: pysähdy ja odota $(1-p)/(1+k)$,
go-back-N $(1-p)/(1+kp)$ ja valikoiva toisto $1-p$, kun kierros on
$k$ kehysaikaa.

```{.tuloste tiedosto="esimerkit/05-arq.odotettu"}
```

Pysähdy ja odota hukkaa koko kierrosajan jokaista kehystä kohti. Se
riittää, kun kierros on lyhyt kehykseen verrattuna, mutta 20 kehyksen
kierrosajalla linkistä on käytössä alle 5 %. Go-back-N täyttää linkin,
mutta jokainen katoaminen maksaa kierroksen verran jo lähetettyjä
kehyksiä: kymmenen prosentin häviöllä tehokkuus putoaa 30 %:iin.
Valikoiva toisto menettää vain kadonneet kehykset. Sen hinta on
kirjanpito: vastaanottaja tarvitsee puskurin (viimeinen sarake), ja
kuittausten on kerrottava, mitkä kehykset puuttuvat.

![Kolmen ARQ-menetelmän tehokkuus, kun kierrosaika on 20 kehysaikaa.
Viivat ovat kaavat ja pisteet simulaation tuloksia. Go-back-N on
lähes valikoivan toiston veroinen, kun virheitä on vähän, ja romahtaa,
kun niitä on paljon.](kuvat/arq.png){width=72%}

Samat menetelmät toistuvat eri kerroksilla. Wi-Fi kuittaa jokaisen
kehyksen linkillä, ja TCP on liukuvan ikkunan protokolla, joka toimii
valikoivan toiston tavoin (SACK-kuittaukset). Ikkunan mitoitus on
luvussa Kytkentätavat ja viive, ja pysähdy ja odota -protokolla
toteutetaan UDP:n päälle taidossa *Verkko-ohjelmointi*.

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

![Neljä seitsemän bitin koodisanaa lähetysjärjestyksessä. Ilman
lomitusta purske osuu neljästi sanaan 2. Lomitettuna samat neljä
peräkkäistä bittiä kuuluvat neljään eri
sanaan.](kuvat/lomitus.png){width=100%}

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
- Osaat selittää pysähdy ja odota-, go-back-N- ja valikoivan toiston
  menetelmien erot ja laskea niiden tehokkuuden häviöstä ja
  kierrosajasta.
- Osaat koodata ja korjata Hamming(7,4)-sanan syndroomalla.
- Osaat laskea lohkovirheen todennäköisyyden koodilla ja ilman ja
  verrata sitä simulaatioon.
- Osaat selittää lomituksen hyödyn purskevirheissä ja sen hinnan
  viiveenä.
