# Tallennus ja RAID

Levy on palvelimen yleisimmin hajoava osa. Tallennuksen suunnittelussa
päätetään kolme asiaa: millaisia levyjä käytetään, miten ne yhdistetään
niin, että yhden vika ei vie dataa, ja kuinka pitkään järjestelmä on
haavoittuvainen vian jälkeen.

## Levyt ja liitännät

| Liitäntä | Käyttö | Huomioita |
|----------|--------|-----------|
| SATA | Edulliset suuret levyt, arkistot | Yksi yhteys, kuluttajalevyjen virheenkäsittely |
| SAS | Palvelinlevyt ja levyhyllyt | Kaksi porttia (kaksi ohjainta), parempi virheraportointi, laajennettavissa |
| NVMe | Nopea SSD suoraan PCIe-väylään | Satoja tuhansia I/O-operaatioita sekunnissa, pieni viive |

SSD-levyn kuluminen mitataan kirjoituksina: valmistaja ilmoittaa
kestävyyden muodossa TBW (terabytes written) tai DWPD (drive writes per
day). Lokeja ja tietokantoja kirjoittava palvelin voi kuluttaa
kuluttajaluokan SSD:n loppuun vuodessa. Kuntotiedot luetaan
`smartctl`-työkalulla (SMART); kasvavat uudelleenkohdistetut sektorit
ja kulumisprosentti ovat vaihdon merkkejä.

## RAID-tasot

RAID (redundant array of independent disks) yhdistää levyt yhdeksi
laitteeksi. Tasot eroavat siinä, kuinka paljon kapasiteettia menee
vikasietoisuuteen ja kuinka paljon kirjoitukset hidastuvat:

```{.python tiedosto="esimerkit/03-kapasiteetti.py" osa="tasot"}
```

```{.tuloste tiedosto="esimerkit/03-kapasiteetti.odotettu"}
```

- **RAID 0** raidoittaa datan levyjen yli ilman vikasietoisuutta.
  Yhden levyn vika vie kaiken.
- **RAID 1** peilaa saman datan kahdelle (tai useammalle) levylle.
- **RAID 10** raidoittaa peilipareja: nopea ja vikasietoinen, mutta
  puolet tilasta menee kopioihin.
- **RAID 5** tallentaa jokaiseen raitaan yhden pariteettilohkon. Tilaa
  menetetään vain yhden levyn verran, mutta jokainen pieni kirjoitus
  vaatii neljä levyoperaatiota (lue data ja pariteetti, kirjoita
  molemmat).
- **RAID 6** tallentaa kaksi pariteettilohkoa ja kestää kaksi
  levyvikaa.

Kirjoitusrangaistus ratkaisee usein valinnan: tietokanta, joka tekee
paljon pieniä satunnaisia kirjoituksia, toimii RAID 10:llä selvästi
nopeammin kuin RAID 6:lla samoilla levyillä.

## Pariteetti

RAID 5:n pariteetti on raidan datalohkojen XOR. Koska XOR on oma
käänteisoperaationsa, minkä tahansa puuttuvan lohkon voi laskea muiden
lohkojen XOR:na:

```{.python tiedosto="esimerkit/03-pariteetti.py" osa="kirjoitus"}
```

```{.python tiedosto="esimerkit/03-pariteetti.py" osa="koe"}
```

```{.tuloste tiedosto="esimerkit/03-pariteetti.odotettu"}
```

Pariteetin paikka kiertää levyltä toiselle, jotta pariteettikirjoitukset
eivät kuormita yhtä levyä (RAID 4:n ongelma). RAID 6:n toinen
pariteetti lasketaan Reed–Solomon-koodilla, jotta kaksi puuttuvaa
lohkoa voidaan ratkaista.

## Uudelleenrakennus ja lukuvirheet

Kun levy hajoaa, RAID toimii heikennetyssä tilassa (degraded). Uusi
levy rakennetaan uudelleen lukemalla **kaikki** muut levyt kokonaan.
Kaksi asiaa tekee tästä vaarallisen hetken:

1. **Lukuvirhe.** Levyvalmistajat ilmoittavat korjaamattomien
   lukuvirheiden (URE) tason, esimerkiksi yksi virhe 10^14^ luettua
   bittiä kohti. RAID 5:ssä yksikin lukuvirhe uudelleenrakennuksen
   aikana tarkoittaa, että osa datasta on menetetty.
2. **Kesto.** Suuren levyn uudelleenrakennus kestää vuorokauden tai
   enemmän, ja koko sen ajan toinen levyvika vie kaiken.

```{.python tiedosto="esimerkit/03-ure.py" osa="ure"}
```

```{.tuloste tiedosto="esimerkit/03-ure.odotettu"}
```

Valmistajien URE-luvut ovat ylärajoja, ja todelliset levyt ovat yleensä
parempia, mutta suuruusluokka on selvä: suurilla levyillä RAID 5 ei ole
enää turvallinen. Siksi suurille levyille valitaan RAID 6, RAID 10 tai
hajautettu tallennus (Ceph, ZFS:n RAID-Z2). Lisäksi samasta erästä
ostetut levyt hajoavat usein samoihin aikoihin, joten toinen vika
uudelleenrakennuksen aikana on todennäköisempi kuin riippumattomuus
antaisi olettaa.

## Ohjelmallinen RAID: mdadm

Linuxin ohjelmallista RAIDia hallitaan `mdadm`-työkalulla. Komennot
vaativat pääkäyttäjän oikeudet ja oikeat levyt (tai silmukkalaitteet),
joten niitä ei ajeta tämän tutoriaalin testeissä:

```text
mdadm --create /dev/md0 --level=6 --raid-devices=6 /dev/sd[b-g]
cat /proc/mdstat                       # tila ja uudelleenrakennus
mdadm --detail /dev/md0                # levyt, tila, viat
mdadm /dev/md0 --fail /dev/sdc --remove /dev/sdc
mdadm /dev/md0 --add /dev/sdh          # uusi levy, rakennus alkaa
echo check > /sys/block/md0/md/sync_action   # säännöllinen tarkistus
```

Viimeinen rivi on tärkeä: säännöllinen tarkistus lukee kaikki levyt ja
löytää lukuvirheet silloin, kun pariteetti on vielä ehjä ja ne voidaan
korjata. Ubuntu ajaa sen oletuksena kuukausittain. Laitteistopohjaisessa
RAID-ohjaimessa sama toiminto on nimeltään *patrol read*.

## Käytännössä

- **RAID ei ole varmuuskopio.** RAID suojaa levyviasta, ei poistetulta
  tiedostolta, kiristyshaittaohjelmalta, ohjelmistovialta eikä
  tulipalolta. Luku *Varmuuskopiointi* käsittelee ne.
- **Valitse taso kuorman mukaan.** Satunnaisia pieniä kirjoituksia
  tekevä kuorma RAID 10:lle, suuret peräkkäiset tiedostot RAID 6:lle.
- **Suurille levyille kaksinkertainen pariteetti.** RAID 5:n riski
  kasvaa levyjen koon mukana.
- **Kuuma varalevy (hot spare)** lyhentää heikennetyn tilan kestoa,
  koska uudelleenrakennus alkaa heti eikä vasta, kun joku vaihtaa
  levyn.
- **Valvo tila ja aja tarkistukset.** Heikennetty RAID ilman hälytystä
  on RAID 0.
- **Testaa levynvaihto** ennen kuin sitä tarvitaan, myös se, että
  oikea levy tunnistetaan (merkkivalo, sarjanumero).

## Itsearviointi

- Osaat laskea RAID-tasojen käytettävän kapasiteetin, vikasietoisuuden
  ja kirjoitusrangaistuksen ja valita tason kuorman mukaan.
- Osaat selittää, miten XOR-pariteetilla rakennetaan puuttuva levy
  uudelleen.
- Osaat arvioida uudelleenrakennuksen keston ja lukuvirheen riskin ja
  perustella, miksi suurille levyille valitaan RAID 6.
- Osaat kertoa, mitä RAID ei suojaa ja miksi se ei korvaa
  varmuuskopioita.
