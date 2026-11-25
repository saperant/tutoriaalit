# Käyttäjät ja oikeudet

Linux on monen käyttäjän järjestelmä. Jokaisella prosessilla on
käyttäjä ja ryhmät, ja jokaisella tiedostolla omistaja, ryhmä ja
oikeudet. Myös palvelut ajetaan omina käyttäjinään (`www-data`,
`postgres`), jotta murrettu palvelu ei pääse käsiksi muuhun
järjestelmään.

## Käyttäjät ja ryhmät

| Komento | Tehtävä |
|---------|---------|
| `id` | Oma käyttäjä, ryhmät ja numerotunnisteet |
| `getent passwd kaisa` | Käyttäjän tiedot (myös LDAP:sta ym.) |
| `getent group docker` | Ryhmän jäsenet |
| `sudo komento` | Aja komento pääkäyttäjänä; oikeudet tiedostossa `/etc/sudoers` |
| `sudo -u postgres psql` | Aja toisena käyttäjänä |
| `sudo -i` | Pääkäyttäjän kuori (käytä säästeliäästi) |
| `useradd -m -s /bin/bash olli` | Luo käyttäjä kotihakemistoineen |
| `usermod -aG docker olli` | Lisää ryhmään; voimaan seuraavasta kirjautumisesta |

Käyttäjät ovat tiedostossa `/etc/passwd`, salasanatiivisteet tiedostossa
`/etc/shadow` ja ryhmät tiedostossa `/etc/group`. Pääkäyttäjä `root`
(UID 0) ohittaa oikeustarkistukset. Siksi tämän tutoriaalin
testikontissa, joka ajetaan pääkäyttäjänä, kirjoitussuojattuun
tiedostoon voi kirjoittaa. Esimerkit näyttävät oikeudet mutta eivät
nojaa siihen, että pääsy evätään.

## Oikeuksien merkintä

Jokaisella tiedostolla on kolme oikeusjoukkoa: omistaja (*u*), ryhmä
(*g*) ja muut (*o*). Kukin joukko koostuu lukuoikeudesta (*r*, 4),
kirjoitusoikeudesta (*w*, 2) ja suoritusoikeudesta (*x*, 1).
Oktaalimuodossa jokainen numero on joukon oikeuksien summa: `750` on
`rwxr-x---`.

```{.dot otsikko="Oikeudet `rwxr-x---` ovat oktaalina `750`: jokainen numero on yhden joukon bittien summa"}
digraph {
  node [shape=plaintext];
  t [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="6">
    <tr><td colspan="3" bgcolor="#EEF2F4">omistaja (u)</td>
        <td colspan="3" bgcolor="#EEF2F4">ryhmä (g)</td>
        <td colspan="3" bgcolor="#EEF2F4">muut (o)</td></tr>
    <tr><td>r</td><td>w</td><td>x</td><td>r</td><td>-</td><td>x</td>
        <td>-</td><td>-</td><td>-</td></tr>
    <tr><td>4</td><td>2</td><td>1</td><td>4</td><td>0</td><td>1</td>
        <td>0</td><td>0</td><td>0</td></tr>
    <tr><td colspan="3">4 + 2 + 1 = 7</td><td colspan="3">4 + 0 + 1 = 5</td>
        <td colspan="3">0 + 0 + 0 = 0</td></tr>
  </table>>];
}
```

| Oikeus | Tiedostolle | Hakemistolle |
|--------|-------------|--------------|
| `r` | Sisällön luku | Nimien listaus |
| `w` | Sisällön muutos | Nimien lisäys, poisto ja uudelleennimeäminen |
| `x` | Suoritus ohjelmana | Läpikulku: pääsy sisällä oleviin nimiin |

Taulukon oikea sarake on usein yllätys: tiedoston poistaminen vaatii
kirjoitusoikeuden *hakemistoon*, ei tiedostoon. Hakemiston `x` ilman
`r`:ää sallii avata tiedoston, jonka nimen tietää, mutta ei listata
hakemistoa.

```{.bash tiedosto="esimerkit/03-oikeudet.sh" osa="luonti"}
```

```{.bash tiedosto="esimerkit/03-oikeudet.sh" osa="muutos"}
```

```{.tuloste tiedosto="esimerkit/03-oikeudet.odotettu"}
```

Symbolinen muoto (`u+x`, `go-r`, `a=r`) muuttaa vain mainitut bitit.
Oktaalimuoto asettaa kaikki kerralla ja on selkeämpi, kun lopputulos
tiedetään. Skripti käynnistyy `./julkaise.sh`-muodossa vasta, kun
suoritusoikeus on asetettu. Ensimmäinen rivi `#!` kertoo, mikä tulkki
sen suorittaa.

## Oletusoikeudet: umask

Uusi tiedosto saa oikeudet `666` ja hakemisto `777`, joista poistetaan
*umaskin* bitit. Yleinen oletus `022` poistaa kirjoitusoikeuden
ryhmältä ja muilta:

```{.bash tiedosto="esimerkit/03-umask.sh" osa="umask"}
```

```{.tuloste tiedosto="esimerkit/03-umask.odotettu"}
```

Palvelimella, jossa käsitellään luottamuksellista dataa, umask `027`
tai `077` on parempi oletus. Palveluille umask asetetaan
palveluyksikössä (`UMask=0027`, luku *Paketit, palvelut ja lokit*).

## Oikeuksien korjaaminen

Tyypillinen tilanne: verkkosivuston tiedostot on kopioitu arkistosta
tai Windows-levyltä, ja oikeudet ovat sekaisin. Kaikkien
kirjoitettavissa olevat tiedostot löytyvät `find -perm`-ehdolla
(komento `find` käsitellään luvussa *Etsintä, massatoiminnot ja
arkistot*):

```{.bash tiedosto="esimerkit/03-korjaus.sh" osa="etsinta"}
```

Rekursiivinen `chmod -R` ja iso `X` (suoritusoikeus vain hakemistoille
ja tiedostoille, joilla se jo on jollakulla) näyttää oikealta
ratkaisulta, mutta se säilyttää aiemmin virheellisesti annetun
suoritusoikeuden:

```{.bash tiedosto="esimerkit/03-korjaus.sh" osa="iso-x"}
```

Luotettava tapa käsittelee hakemistot ja tiedostot erikseen ja antaa
suoritusoikeuden vain sitä tarvitseville:

```{.bash tiedosto="esimerkit/03-korjaus.sh" osa="korjaus"}
```

```{.tuloste tiedosto="esimerkit/03-korjaus.odotettu"}
```

Omistajan vaihto tehdään komennolla `chown -R www-data:www-data
sivusto`. Se vaatii pääkäyttäjän oikeudet.

## Erikoisbitit

| Bitti | Oktaali | Tiedostolle | Hakemistolle |
|-------|---------|-------------|--------------|
| setuid | 4000 | Ajetaan omistajan oikeuksin (`passwd`) | – |
| setgid | 2000 | Ajetaan ryhmän oikeuksin | Uudet tiedostot perivät hakemiston ryhmän |
| sticky | 1000 | – | Vain omistaja voi poistaa omat tiedostonsa (`/tmp`) |

```{.bash tiedosto="esimerkit/03-erikoisbitit.sh" osa="bitit"}
```

```{.tuloste tiedosto="esimerkit/03-erikoisbitit.odotettu"}
```

setgid-hakemisto ja umask `002` ovat tiimin jaetun hakemiston
perusresepti: kaikki uudet tiedostot kuuluvat projektiryhmälle ja ovat
ryhmän kirjoitettavissa. setuid-ohjelmat ovat tietoturvan kannalta
herkkiä, ja ne löytää komennolla `find / -perm -4000 -type f
2>/dev/null`. Loppuosa `2>/dev/null` piilottaa virheilmoitukset
hakemistoista, joihin ei ole lukuoikeutta (luku *Putket ja
uudelleenohjaukset*).

Hienojakoisempiin tarpeisiin, kuten yhden lisäkäyttäjän lukuoikeuteen,
on ACL-luettelot (`setfacl -m u:olli:r tiedosto`, `getfacl`).

## Käytännössä

- **Vähimmät oikeudet.** Palvelut omina käyttäjinään, salaisuudet
  (`.env`, avaimet) oikeuksilla `600`, ei koskaan `777`. Jos jokin
  "toimii vain 777:llä", oikea korjaus on omistaja tai ryhmä.
- **sudo yksittäisille komennoille**, ei pysyvää pääkäyttäjän kuorta.
  Komento `sudo` kirjaa käytön lokiin ja pakottaa miettimään, mikä
  tarvitsee oikeuksia.
- **`sudo` ei koske uudelleenohjausta**: `sudo echo x > /etc/tiedosto`
  epäonnistuu, koska kuori avaa tiedoston tavallisena käyttäjänä.
  Oikea muoto on `echo x | sudo tee /etc/tiedosto`.
- **Ryhmä ja setgid jaettuihin hakemistoihin**, ei jokaisen tiedoston
  oikeuksien käsin säätämistä.
- **Korjaa oikeudet `find -type`-ehdoilla** ja tarkista lopputulos
  ennen ja jälkeen (`find -perm`, `stat -c '%a %n'`).
- **Ryhmäjäsenyys tulee voimaan uudesta kirjautumisesta.** `id`
  näyttää nykyisen kuoren ryhmät, `getent group` tiedoston tilan.

## Itsearviointi

- Osaat lukea oikeudet sekä merkkimuodossa että oktaalina ja selittää
  `r`-, `w`- ja `x`-oikeuden merkityksen hakemistolle.
- Osaat asettaa oikeudet `chmod`-komennolla ja korjata kokonaisen
  hakemistopuun oikeudet hallitusti.
- Osaat kertoa, miten umask määrää uusien tiedostojen oikeudet.
- Osaat perustaa tiimille jaetun hakemiston setgid-bitillä ja
  ryhmällä.
- Osaat käyttää `sudo`-komentoa niin, että myös uudelleenohjaus tehdään
  pääkäyttäjänä.
