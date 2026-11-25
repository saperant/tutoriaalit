# Käynnistystestit ja jatkuva integraatio

Sulautetun Linuxin vika näkyy usein vasta, kun koko järjestelmä
käynnistetään: ytimen asetus puuttuu, laitepuussa on väärä osoite,
palvelu käynnistyy liian aikaisin tai sammutus jumittuu. Yksikkötestit
eivät näe näitä. *Käynnistystesti* käynnistää järjestelmän, seuraa
konsolia ja tarkistaa, että odotetut asiat tapahtuvat odotetussa
järjestyksessä. Kun testi ajetaan jokaisesta muutoksesta CI:ssä,
käynnistyksen rikkova muutos huomataan samana päivänä.

## Testauksen tasot

| Taso | Mitä ajetaan | Missä | Löytää |
|------|--------------|-------|--------|
| yksikkötestit | funktiot | isäntä | logiikkavirheet |
| emuloidut ohjelmat | ristiinkäännetty ohjelma | `qemu-aarch64` | arkkitehtuurierot (luku 2) |
| järjestelmä emulaattorissa | ydin ja juuri | `qemu-system-aarch64` | asetukset, init, palvelut |
| laitetestit (HIL) | oikea kuva | oikea laite | ajurit, ajoitus, laitteisto |

Emulaattori ei korvaa oikeaa laitetta: QEMU:n virt-koneessa ei ole
laitteesi ajureita, sen ajoitus ei vastaa todellista, eikä siinä ole
laitteiston vikoja. Mutta se löytää suurimman osan konfiguraation,
juuritiedostojärjestelmän ja palvelujen virheistä minuuteissa, ja sitä
voi ajaa rinnakkain niin monta kuin CI-koneessa on ytimiä. *Laitetesteissä*
(hardware in the loop) testikone ohjaa laitteen virtaa releellä, lukee
sarjakonsolia, vaihtaa SD-korttia multiplekserillä ja ajaa samat testit
oikealla laitteistolla. Avoimia kehyksiä tähän ovat LAVA (jota KernelCI
käyttää ytimen testaamiseen sadoilla laitteilla) ja labgrid.

## Kaksi tapaa tarkistaa tuloste

Tämän tutoriaalin esimerkit tarkistetaan kahdella tavalla. Useimmissa
koko tuloste verrataan tallennettuun (*kultainen tuloste*), ja ytimen
lokista suodatetaan pois aikaleimat ja osoitteet. Vertailu on tiukka:
mikä tahansa muutos tulosteessa huomataan, myös odottamaton uusi
varoitus. Haittana on, että tallennettu tuloste on päivitettävä aina,
kun jokin tarkoituksellisesti muuttuu.

Toinen tapa on *odottaa* tiettyjä rivejä järjestyksessä aikarajojen
kanssa, kuten `expect`-työkalu tai pexpect tekevät. Se sallii muun
tulosteen vaihdella, se voi lähettää syötettä (kuten U-Bootin komennot
luvussa 5), ja se päättää testin heti, kun jotain menee pieleen,
odottamatta koko aikarajaa. Tuotannon testikehykset ovat yleensä tätä
tyyppiä.

## Käynnistystestien ajuri

Ajuri lukee vaihetiedoston ja ajaa sen QEMU:a vastaan. Vaiheet ovat
`odota` (säännöllinen lauseke ja aikaraja), `laheta` (teksti
konsoliin) ja `loppu` (odotettu paluuarvo). Seuraava testi tarkistaa
luvun 7 init-järjestelmän:

```{.text tiedosto="esimerkit/10-kaynnistystesti/palvelut.vaiheet"}
```

Ajurin ydin on luokka, joka lukee prosessin tulostetta estämättä ja
etsii lauseketta edellisen osuman jälkeen:

```{.python tiedosto="esimerkit/10-kaynnistystesti/kaynnistystesti.py" osa="konsoli"}
```

Kolme yksityiskohtaa tekee siitä luotettavan:

- **Tulostetta käsitellään tavuina, ei riveinä.** U-Bootin kehote `=> `
  ja teksti *Hit any key to stop autoboot* eivät pääty rivinvaihtoon,
  joten rivi kerrallaan lukeva testi jäisi odottamaan ikuisesti.
- **Haku jatkuu edellisen osuman lopusta.** Kahdesti odotettu kehote
  vaatii kaksi eri kehotetta, ei samaa kahdesti.
- **Ytimen paniikki tunnistetaan joka kierroksella.** Testi päättyy heti
  ja kertoo syyn, eikä odota aikarajaa.

```{.python tiedosto="esimerkit/10-kaynnistystesti/kaynnistystesti.py" osa="aja"}
```

Testin oma tuloste ei sisällä konsolin raakatekstiä, joten se on
toistettava, vaikka ajoitukset ja osoitteet vaihtelevat:

```{.make tiedosto="esimerkit/Makefile" osa="testit"}
```

```{.tuloste tiedosto="esimerkit/testit/10-palvelut.odotettu"}
```

## Kun käynnistys epäonnistuu

Testin arvo mitataan sillä, miten se kertoo viasta. Seuraava
initramfs on rikki: siitä puuttuu `/init`.

```{.text tiedosto="esimerkit/10-kaynnistystesti/rikki.lista"}
```

Sama vaihetiedosto ajettuna tätä järjestelmää vastaan:

```{.tuloste tiedosto="esimerkit/testit/10-paniikki.odotettu"}
```

Virheilmoitus on aluksi yllättävä: miksi ydin yrittää kiinnittää
juurta, vaikka initramfs on olemassa? Koska initramfsistä ei löytynyt
`rdinit`-ohjelmaa, ydin siirtyy vanhaan käynnistystapaan ja yrittää
kiinnittää komentorivin `root=`-laitteen. Sitä ei ole annettu, joten
laite on `unknown-block(0,0)`. Sama ilmoitus tulee, kun juurilaitteen
ajuri tai tiedostojärjestelmä puuttuu ytimestä, kun `root=` osoittaa
väärään osioon tai kun levy ilmestyy vasta myöhemmin eikä komentorivillä
ole `rootwait`-parametria. Testi kertoi syyn sekunnissa, kun aikarajaan
olisi ollut minuutti.

## Käynnistystestit CI:ssä

Ytimen kääntäminen on käynnistystestien hitain vaihe. Tämän tutoriaalin
ympäristö kääntää ytimen hakemistoon, jonka nimi on fragmenttien
tiiviste (luku 1), joten CI:n välimuisti voi käyttää samaa tiivistettä
avaimenaan: ydin käännetään vain, kun fragmentti muuttuu. Muut vaiheet
kestävät sekunteja.

Hyvä käynnistystestien putki:

1. kääntää kuvan rakennustyökalulla tai välimuistista
2. ajaa ristiinkäännettyjen ohjelmien yksikkötestit `qemu-aarch64`:llä
3. käynnistää kuvan QEMU:ssa ja ajaa käynnistystestit
4. ajaa yöllä samat testit oikeilla laitteilla
5. säilyttää epäonnistuneen ajon koko konsolilokin artefaktina.

Viimeinen kohta on tärkeä: kultaisen tulosteen ero tai ajurin
virheilmoitus kertoo, *mikä* meni pieleen, mutta *miksi* löytyy
yleensä ytimen lokista rivejä aiemmin. Kun loki ei riitä, syytä
etsitään seuraavan luvun keinoin.

Rakennustyökaluissa on omat testikehyksensä. Buildrootin `support/testing`
käynnistää kuvia QEMU:ssa Pythonin `unittest`-testeillä, ja Yocton
`testimage` ajaa testit valmiissa kuvassa QEMU:ssa tai laitteessa.
*Ptest*-paketit (`ptest-runner`) ajavat ohjelmien omat testit
kohdelaitteessa.

## Käytännössä

- **Testaa koko käynnistys jokaisesta muutoksesta.** Ydin, laitepuu ja
  juuritiedostojärjestelmä muuttuvat usein yhdessä, ja vain
  käynnistys todistaa, että ne sopivat yhteen.
- **Tee testeistä toistettavia.** Suodata aikaleimat ja osoitteet,
  kiinnitä rakennusten aikaleimat ja testaa vain sitä, mitä testin on
  tarkoitus testata.
- **Käytä lyhyitä aikarajoja ja tunnista viat aktiivisesti.** Paniikki,
  *Oops* tai *Unable to mount root* päättävät testin heti; pitkä
  aikaraja viivästää jokaista epäonnistunutta ajoa.
- **Tallenna konsoliloki.** Epäonnistuneen ajon loki on ainoa todiste,
  kun vika ilmenee vain kerran sadassa.
- **Testaa myös sammutus ja uudelleenkäynnistys.** Jumittuva sammutus
  ja epäonnistuva toinen käynnistys ovat tavallisia vikoja, joita
  käynnistyksen testaaminen ei näe.

## Itsearviointi

- Osaat kuvata sulautetun Linuxin testauksen tasot ja kertoa, mitä
  kukin löytää ja mitä ei.
- Osaat vertailla kultaista tulostetta ja odottavaa tarkistusta ja
  valita niistä tilanteeseen sopivan.
- Osaat kirjoittaa käynnistystestin, joka odottaa konsolin tulosteita,
  lähettää syötettä ja tunnistaa ytimen paniikin.
- Osaat tulkita virheen *Unable to mount root fs* ja luetella sen
  tavallisimmat syyt.
- Osaat suunnitella CI-putken, joka kääntää ytimen vain tarvittaessa ja
  säilyttää epäonnistuneiden ajojen lokit.
