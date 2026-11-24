# Syöte

Pelin ei pidä kysyä, onko välilyönti painettu, vaan onko *hyppy*
pyydetty. Näppäimistö, peliohjain ja kosketusnäyttö tuottavat samat
toiminnot, ja pelaaja voi vaihtaa näppäimiä. Syötteen käsittely on
myös paikka, jossa peli tuntuu joko tarkalta tai kömpelöltä.

## Toiminnot ja reunat

Laitteen tila (mitkä näppäimet ovat alhaalla) muunnetaan kerran
ruudussa toimintojen tilaksi kartan avulla. Toiminnoista tunnistetaan
kolme tapahtumaa vertaamalla edelliseen ruutuun: *painettu* (alas tällä
ruudulla), *pidetty* ja *vapautettu*.

```{.cpp tiedosto="esimerkit/03-toiminnot.cpp" osa="kartta"}
```

```{.tuloste tiedosto="esimerkit/03-toiminnot.odotettu"}
```

Hyppy kuuluu *painallukseen*, ei pitoon: muuten pelaaja hyppii
jatkuvasti nappia pitäessään. Liike taas kuuluu pitoon. Huomaa myös,
että kaksi saman toiminnon näppäintä (`D` ja oikea nuoli) eivät tuota
kahta painallusta.

Syötteen käsittely kuuluu kiinteän askeleen sisään tai sen eteen niin,
että lyhytkin painallus näkyy simulaatiolle. Jos ruudussa ajetaan kaksi
askelta, painallus käsitellään vain ensimmäisessä, muuten pelaaja
hyppää kahdesti.

## Armoa pelaajalle: puskurointi ja kojoottiaika

Ihminen ei osu ruutuun tarkasti. Kaksi tunnettua tekniikkaa tekee
hyppäämisestä armollisen:

- **Hypyn puskurointi** (jump buffering): jos hyppy painetaan juuri
  ennen alastuloa, hyppy tapahtuu, kun hahmo osuu maahan.
- **Kojoottiaika** (coyote time): reunalta pudonnut hahmo voi vielä
  hypätä muutaman ruudun ajan, kuten piirroselokuvan kojootti, joka
  putoaa vasta huomattuaan juosseensa jyrkänteen yli.

```{.cpp tiedosto="esimerkit/03-puskuri.cpp" osa="armo"}
```

```{.tuloste tiedosto="esimerkit/03-puskuri.odotettu"}
```

Ilman armoa kaksi kolmesta painalluksesta katoaa. Pelaaja ei koe
tätä ohjelmointivirheenä vaan "huonona ohjauksena".

## Komennot ja tallenne

Kun syöte muunnetaan *komennoiksi*, joita peli suorittaa, komennot
voi myös tallentaa. Determinististä peliä varten tallenne riittää
uusinnan, testitapauksen tai virheraportin toistamiseen: tiedostossa on
vain syöte, ei pelin tilaa.

```{.cpp tiedosto="esimerkit/03-tallenne.cpp" osa="komento"}
```

```{.cpp tiedosto="esimerkit/03-tallenne.cpp" osa="toisto"}
```

```{.cpp tiedosto="esimerkit/03-tallenne.cpp" osa="tarkistussumma"}
```

```{.tuloste tiedosto="esimerkit/03-tallenne.odotettu"}
```

Tarkistussumma on uusintojen ja moninpelin tärkein vianetsintäväline:
kun summat eroavat ensimmäisen kerran, tiedetään ruutu, jolla
determinismi rikkoutui.

## Käytännössä

- **Komento-malli** (command): syöte muunnetaan komennoiksi, jotka
  voidaan tallentaa, toistaa, lähettää verkon yli tai perua
  (muokkaimissa).
- **Toimintokartta asetuksiin.** Kovakoodatut näppäimet ovat
  saavutettavuusongelma; pelaajan pitää voida vaihtaa ne.
- **Reunojen tunnistus askeleessa.** Painallus ei saa kadota eikä
  monistua, vaikka ruudussa olisi nolla tai kaksi simulaatioaskelta.
- **Tallenne testinä.** Tallennettu syöte ja odotettu tarkistussumma
  ovat regressiotesti, joka huomaa, kun muutos rikkoo pelimekaniikan.
  Tutoriaalin *Kipinä*-peli testataan näin (luku *Kipinä*).
- **Peliohjaimen kuollut alue** (dead zone): tatin pieniä arvoja ei
  tulkita liikkeeksi, ja arvot skaalataan uudelleen alueen ulkopuolelta.

## Itsearviointi

- Osaat erottaa laitteen syötteen pelin toiminnoista ja tunnistaa
  painalluksen, pidon ja vapautuksen.
- Osaat toteuttaa hypyn puskuroinnin ja kojoottiajan.
- Osaat tallentaa syötteen komentoina ja toistaa pelin samaan
  lopputilaan.
- Osaat käyttää tarkistussummaa determinismin rikkoutumisen
  paikantamiseen.
