# Tiedostojärjestelmät, LVM ja ZFS

RAID antaa yhden suuren laitteen. Sen päälle tarvitaan joustava tapa
jakaa tila palveluille, kasvattaa sitä tarpeen mukaan, ottaa
tilannevedoksia ja huomata, jos data on korruptoitunut.

## Kaksi tapaa täyttyä

Tavallinen tiedostojärjestelmä (ext4, XFS) täyttyy, kun joko datalohkot
tai *inodet* loppuvat. Inode on tiedoston kuvaus: omistaja, oikeudet,
koko ja lohkojen paikat. ext4 päättää inodien määrän luontihetkellä,
ja miljoonat pienet tiedostot (välimuistit, sähköpostijonot,
istuntotiedostot) voivat käyttää ne loppuun, vaikka tilaa on jäljellä:

```{.bash tiedosto="esimerkit/04-inodet.sh" osa="luonti"}
```

```{.bash tiedosto="esimerkit/04-inodet.sh" osa="taytto"}
```

```{.tuloste tiedosto="esimerkit/04-inodet.odotettu"}
```

Vapaita lohkoja on yhä tuhansia, mutta uutta tiedostoa ei voi luoda.
Sovellus saa saman virheilmoituksen kuin täydeltä levyltä ("No space
left on device"), ja `df -h` näyttää tilaa olevan. Siksi valvotaan
molempia: `df -h` ja `df -i`. XFS varaa inodeja dynaamisesti eikä
kärsi tästä samalla tavalla.

## LVM: joustava jako

LVM (logical volume manager) lisää levyjen ja tiedostojärjestelmien
väliin kerroksen:

| Käsite | Merkitys |
|--------|----------|
| PV (physical volume) | Levy, osio tai RAID-laite LVM:n käytössä |
| VG (volume group) | Yhden tai useamman PV:n tilavaranto |
| LV (logical volume) | Varannosta jaettu "osio", jolle luodaan tiedostojärjestelmä |

Tärkeimmät hyödyt ovat kasvattaminen ilman katkoa ja tilannevedokset.
Komennot vaativat pääkäyttäjän oikeudet ja ytimen device mapperin,
joten niitä ei ajeta tämän tutoriaalin testeissä:

```text
pvcreate /dev/md0
vgcreate data /dev/md0
lvcreate -n tietokanta -L 200G data
mkfs.xfs /dev/data/tietokanta

lvextend -r -L +100G /dev/data/tietokanta   # -r kasvattaa myös fs:n
lvcreate -s -n tk-vedos -L 20G /dev/data/tietokanta  # vedos
```

LVM:n tilannevedos on copy-on-write: se tallentaa alkuperäiset lohkot,
kun niitä muutetaan. Vedokselle varattu tila kuluu muutosten tahdissa,
ja täyttyessään vedos muuttuu käyttökelvottomaksi. Vedos on siksi
lyhytikäinen apuväline, esimerkiksi johdonmukaisen varmuuskopion
ottamiseen käynnissä olevasta järjestelmästä, ei itsessään varmuuskopio.

## Hiljainen korruptoituminen

Levy voi palauttaa väärää dataa ilman lukuvirhettä: kirjoitus on
mennyt väärään paikkaan, ohjaimen välimuisti on hävittänyt sen tai
magneettinen tila on haalistunut. Tätä kutsutaan bittimädäksi
(*bit rot*). Tavallinen RAID 1 ei tiedä, kumpi kopio on oikea, koska
kumpikin luetaan onnistuneesti.

ZFS ja Btrfs tallentavat jokaisen lohkon tarkistussumman erilleen
lohkosta, sen osoittavaan metatietoon. Lukiessa summa tarkistetaan, ja
väärä kopio korvataan oikealla:

```{.python tiedosto="esimerkit/04-tarkistussummat.py" osa="peili"}
```

```{.python tiedosto="esimerkit/04-tarkistussummat.py" osa="koe"}
```

```{.tuloste tiedosto="esimerkit/04-tarkistussummat.odotettu"}
```

Läpikäynti (*scrub*) lukee säännöllisesti kaiken datan ja korjaa viat,
ennen kuin toinenkin kopio ehtii vioittua. Jos molemmat kopiot ovat
vioittuneet, tiedostojärjestelmä kertoo sen eikä palauta väärää dataa.

## ZFS:n periaatteet

ZFS yhdistää RAIDin, LVM:n ja tiedostojärjestelmän yhdeksi
kokonaisuudeksi:

- **Varanto (pool)** koostuu vdev-ryhmistä (peili, RAID-Z1/Z2/Z3).
  RAID-Z2 vastaa RAID 6:ta.
- **Copy-on-write.** Mitään lohkoa ei kirjoiteta paikalleen. Uusi
  versio kirjoitetaan uuteen paikkaan, ja osoitin päivitetään viimeisenä.
  Kaatuminen kesken kirjoituksen ei jätä tiedostojärjestelmää
  epäjohdonmukaiseksi, eikä `fsck`-tarkistusta tarvita.
- **Tilannevedokset** ovat siksi ilmaisia ja välittömiä: vedos on vain
  vanha osoitin. `zfs send` siirtää vedosten erotuksen toiselle
  koneelle, mikä on tehokas tapa replikoida dataa.
- **Tarkistussummat ja scrub** kuten yllä.
- **Pakkaus** (lz4, zstd) on yleensä nopeampi kuin pakkaamattoman datan
  kirjoittaminen levylle.

```text
zpool create data raidz2 sdb sdc sdd sde sdf sdg
zfs create -o compression=zstd data/tietokanta
zfs snapshot data/tietokanta@2026-11-24
zfs send -i @2026-11-23 data/tietokanta@2026-11-24 \
    | ssh varmistus zfs recv varmistus/tietokanta
zpool scrub data
```

ZFS:n hinta on muistinkäyttö (ARC-välimuisti) ja se, että varannon
rakennetta on vaikea muuttaa jälkikäteen: vdev-ryhmään ei voi helposti
lisätä levyjä. Varanto suunnitellaan siksi kerralla kasvuvara mukaan
lukien.

## Käytännössä

- **Valvo sekä tila että inodet.** `df -h` ja `df -i`; hälytys kasvun
  nopeudesta, ei vain rajasta (luku *Kustannukset ja kapasiteetti*).
- **Jätä tilaa kasvulle.** LVM-varantoon kannattaa jättää varaamatonta
  tilaa, jota annetaan sinne, missä sitä tarvitaan.
- **Tarkistussummat datalle, jolla on väliä.** ZFS tai Btrfs, tai
  sovellustason tarkistussummat (esimerkiksi tietokannan sivusummat).
- **Aja scrub säännöllisesti** ja hälytä sen löydöistä.
- **Vedos ei ole varmuuskopio**, koska se on samalla levyllä.

## Itsearviointi

- Osaat selittää, miksi tiedostojärjestelmä voi täyttyä inodien
  loppuessa, ja valvoa sitä.
- Osaat kuvata LVM:n käsitteet ja kertoa, mihin tilannevedosta
  käytetään ja mihin ei.
- Osaat selittää, miksi tavallinen peili ei havaitse bittimätää ja
  miten tarkistussummat ja scrub korjaavat sen.
- Osaat kertoa ZFS:n copy-on-write-periaatteen hyödyt ja rajoitukset.
