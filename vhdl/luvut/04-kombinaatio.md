# Kombinaatiologiikka

Kombinaatiologiikan lähtö riippuu vain tulojen nykyisistä arvoista.
VHDL:ssä se kuvataan joko rinnakkaisilla sijoituksilla tai
prosessilla, joka lasketaan uudelleen aina, kun jokin tulo muuttuu.
Molemmat tuottavat saman laitteiston; valinta on luettavuuskysymys.

## Rinnakkaiset sijoitukset

Arkkitehtuurin rungossa olevat lauseet ovat *rinnakkaisia*: ne ovat
olemassa yhtä aikaa, ja niiden järjestyksellä ei ole merkitystä. Kolme
muotoa kattaa lähes kaiken:

| Muoto | Laitteisto | Esimerkki |
|-------|------------|-----------|
| `y <= lauseke;` | portit | `aktiiviset <= pyynnot and maski;` |
| `y <= a when ehto else b;` | prioriteettiketju | `vasen <= (others => '0') when kymmenet = "0000" else raaka;` |
| `with s select y <= ...` | rinnakkainen multiplekseri | luvun 2 seitsensegmenttidekooderi |

Ehdollinen sijoitus `when ... else` testaa ehdot järjestyksessä, joten
ensimmäinen tosi ehto voittaa. Valitseva sijoitus `with ... select`
vaatii, että valinnat kattavat kaikki arvot, ja ne eivät saa olla
päällekkäisiä. Kääntäjä tarkistaa molemmat.

## Prosessi ja process (all)

Kun logiikassa on silmukoita, sisäkkäisiä ehtoja tai välituloksia,
prosessi on luettavampi. Prosessin sisällä lauseet suoritetaan
peräkkäin, mutta lopputulos on edelleen kombinaatiologiikkaa:
synteesi laskee, mikä arvo kullekin signaalille jää voimaan.

Prosessin *herkkyyslista* kertoo, mitkä signaalit herättävät sen.
VHDL-2008:n `process (all)` ottaa listaan automaattisesti kaikki
prosessissa luetut signaalit. Kombinaatioprosessissa käytetään aina
sitä.

Esimerkki on keskeytysohjaimen prioriteettikooderi. Se valitsee
sallituista pyynnöistä sen, jonka indeksi on pienin:

```{.vhdl tiedosto="esimerkit/04-keskeytys.vhd" osa="ohjain"}
```

```{.tuloste tiedosto="esimerkit/04-keskeytys.odotettu"}
```

Kolme yksityiskohtaa ovat VHDL-tyypillisiä. Prosessin alussa olevat
*oletussijoitukset* takaavat, että jokainen lähtö saa arvon jokaisella
suorituksella. Silmukka avautuu synteesissä kahdeksaksi peräkkäiseksi
ehdoksi; koska silmukka kulkee ylhäältä alas, viimeisenä sijoitettu
eli pienin indeksi jää voimaan. Lähtö `numero` on rajattu
kokonaisluku, jonka leveyden synteesi päättelee generic-parametrista
`N`, joten erillistä leveysparametria ei tarvita.

## case ja luettelotyypit

`case` on prosessin `with ... select`: rinnakkainen valinta, jonka
haarojen on katettava kaikki arvot. Luettelotyypin kanssa kattavuus on
erityisen arvokas, koska uuden arvon lisääminen tyyppiin paljastaa
jokaisen `case`-lauseen, joka ei sitä käsittele (luku 6).

Seuraava ALU valitsee operaation luettelotyypistä. Tyyppi on
paketissa, koska sitä käytetään portissa:

```{.vhdl tiedosto="esimerkit/04-alu.vhd" osa="paketti"}
```

```{.vhdl tiedosto="esimerkit/04-alu.vhd" osa="alu"}
```

```{.tuloste tiedosto="esimerkit/04-alu.odotettu"}
```

Yhteen- ja vähennyslasku tehdään yhdeksällä bitillä, jotta kanto ja
lainaus jäävät talteen (luku 3). Muuttujat `ua`, `ub` ja `laaja` ovat
välituloksia: ne saavat arvon ennen käyttöä jokaisessa haarassa, joten
niistä ei synny muistia. Oletussijoitus `kanto <= '0'` kattaa haarat,
joissa kantoa ei aseteta. Lippu `nolla` lasketaan rinnakkaisella
sijoituksella sisäisestä signaalista `t`.

## Salpa puuttuvasta sijoituksesta

Jos kombinaatioprosessin jokin polku jättää signaalin sijoittamatta,
signaalin on muistettava edellinen arvonsa. Kellotonta muistia kutsutaan
*salvaksi* (latch). Salpa on FPGA:ssa ja synkronisessa suunnittelussa
lähes aina virhe: ajoitusanalyysi ei käsittele sitä kunnolla, ja
lähtö riippuu tulojen muutosjärjestyksestä.

Seuraavasta osoitedekooderista puuttuu tapaus, jossa osoite ei osu
kumpaankaan alueeseen:

```{.vhdl tiedosto="esimerkit/04-salpa.kaatuu.vhd" osa="virhe"}
```

Simulaattori toimii kuten salpa: osoitteessa F000 RAMin valinta jää
päälle edellisestä osoitteesta. Testipenkki huomaa sen:

```{.tuloste tiedosto="esimerkit/04-salpa.virhe"}
```

Synteesityökalu ilmoittaa salvasta varoituksena, joka hukkuu helposti
satojen muiden joukkoon. GHDL:n synteesi pitää sitä oletuksena virheenä:

```text
$ ghdl --synth --std=08 04-salpa.kaatuu.vhd -e dekooderi
04-salpa.kaatuu.vhd:19:3:error: latch infered for net "cs_ram"
```

Korjaus on oletussijoitus prosessin alkuun (`cs_ram <= '0'; cs_uart <=
'0';`) tai `else`-haara, joka kattaa loput tapaukset. Oletussijoitus on
parempi, koska se pysyy oikeana, kun ehtoja lisätään.

## Puutteellinen herkkyyslista

Ennen VHDL-2008:aa herkkyyslista kirjoitettiin käsin. Jos siitä puuttuu
signaali, simulaattori ei herätä prosessia, kun vain se muuttuu.
Synteesi taas ei käytä herkkyyslistaa lainkaan, vaan tekee logiikan
lausekkeista. Simulointi ja laitteisto käyttäytyvät eri tavalla:

```{.vhdl tiedosto="esimerkit/04-herkkyys.kaatuu.vhd" osa="virhe"}
```

```{.tuloste tiedosto="esimerkit/04-herkkyys.virhe"}
```

Tällainen virhe on vaarallinen, koska testit voivat mennä läpi
sattumalta, jos `c` muuttuu aina samaan aikaan kuin `a` tai `b`. GHDL
varoittaa siitä valitsimella `-Wsensitivity`, ja synteesityökalut
yleensä raportoivat sen. Kombinaatioprosessissa kirjoitetaan siksi aina
`process (all)`.

## Ehtolauseet ja prioriteetti

`if`–`elsif` muodostaa prioriteettiketjun samoin kuin `when ... else`.
Jos ehdot ovat toisensa poissulkevia, kuten osoitealueet, `case` tai
erilliset ehdot kertovat lukijalle ja synteesille, ettei prioriteettia
tarvita. Pitkä `elsif`-ketju kriittisellä polulla tuottaa pitkän
multiplekseriketjun; ajoituksen kannalta rinnakkainen rakenne on
parempi (ks. *RTL-suunnittelu SystemVerilogilla*, luku 4).

VHDL-2008 sallii ehdollisen ja valitsevan sijoituksen myös prosessin
sisällä (`y <= a when s = '1' else b;`), mikä lyhentää yksinkertaisia
valintoja.

## Käytännössä

- **`process (all)` kombinaatiologiikalle.** Käsin kirjoitettu
  herkkyyslista on virhelähde ilman hyötyä. Kellotetussa prosessissa
  listassa on vain kello ja mahdollinen asynkroninen nollaus.
- **Oletussijoitukset ensin.** Jokainen kombinaatioprosessin lähtö saa
  arvon prosessin alussa. Tämä poistaa salvat ja tekee prosessista
  helpon laajentaa.
- **Rinnakkainen sijoitus yksinkertaiseen, prosessi monimutkaiseen.**
  Yksi rivi logiikkaa on luettavin rinnakkaisena lauseena;
  silmukat, sisäkkäiset ehdot ja välitulokset prosessissa.
- **`when others` vektorille, ei luettelotyypille.** Vektorin
  `case` tarvitsee `others`-haaran metatilojen takia. Luettelotyypin
  kaikki arvot kannattaa luetella, jotta kääntäjä löytää unohtuneet.
- **Tarkista salvat synteesiraportista.** Ennen kuin malli viedään
  laitteeseen, synteesin varoitukset luetaan. `ghdl --synth` on nopea
  tapa tarkistaa yksittäinen lohko.

## Itsearviointi

- Osaat kirjoittaa saman logiikan rinnakkaisilla sijoituksilla ja
  `process (all)` -prosessilla ja valita niistä luettavamman.
- Osaat kertoa, miksi puuttuva sijoitus tuottaa salvan ja miten
  oletussijoitus estää sen.
- Osaat kertoa, miksi puutteellinen herkkyyslista saa simuloinnin ja
  laitteiston käyttäytymään eri tavalla.
- Osaat käyttää `case`-lausetta luettelotyypin kanssa niin, että
  kääntäjä tarkistaa kattavuuden.
