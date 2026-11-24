# SystemRDL:n perusteet

SystemRDL 2.0 on Accelleran standardoima kieli, jolla kuvataan
rekisterit, niiden kentät ja osoiteavaruudet. Kieli muistuttaa
syntaksiltaan SystemVerilogia, mutta siinä ei ole logiikkaa: kuvaus
kertoo, *mitä* rekisterit ovat ja miten niiden kentät käyttäytyvät,
ja generaattorit päättävät, *miten* ne toteutetaan.

## Komponentit

Kuvaus koostuu sisäkkäisistä komponenteista:

| Komponentti | Merkitys | Sisältää |
|-------------|----------------------------------------|-----------------|
| `field` | bittikenttä, pienin yksikkö | ominaisuuksia |
| `reg` | rekisteri, yksi osoitteellinen sana | kenttiä |
| `regfile` | rekisteriryhmä, esimerkiksi DMA-kanava | rekistereitä |
| `addrmap` | osoitekartta: lohko tai kokonainen piiri | kaikkia edellisiä |
| `mem` | muistialue, esimerkiksi puskuri | (ei kenttiä) |
| `signal` | kuvauksen ulkopuolinen signaali, esim. nollaus | ominaisuuksia |

Komponentti voidaan *määritellä* nimellä ja *instantioida* useasti
(`reg ohjaus { ... }; ohjaus CTRL0; ohjaus CTRL1;`) tai määritellä ja
instantioida samalla kertaa nimettömänä, kuten tämän luvun
esimerkeissä. Nimetty määrittely kannattaa, kun sama rakenne toistuu.

Ajastimen kuvauksen alku:

```{.systemverilog tiedosto="esimerkit/rdl/ajastin.rdl" osa="ajastin"}
```

`addrmap ajastin` on lohkon osoitekartta. `name` ja `desc` ovat
ihmiselle tarkoitettuja nimiä, jotka päätyvät dokumentaatioon.
`default`-lausekkeet asettavat oletusarvot kaikille saman
näkyvyysalueen komponenteille: rekisterit ovat 32-bittisiä, ohjelmisto
voi lukea ja kirjoittaa kenttiä (`sw = rw`) ja laitteisto lukea niitä
(`hw = r`).

Kenttä kirjoitetaan muodossa `field { ominaisuudet } NIMI[ylin:alin] =
nollausarvo;`. Rekisteri sijoitetaan osoitteeseen operaattorilla `@`.
Jos osoite jätetään pois, kääntäjä sijoittaa rekisterin seuraavaan
vapaaseen tasattuun osoitteeseen. Eksplisiittinen osoite on
rekisterikartalla kuitenkin tavallisesti parempi: lisäys kuvauksen
keskelle ei silloin siirrä myöhempien rekisterien osoitteita.

## Pääsy ohjelmistolle ja laitteistolle

Kentällä on kaksi pääsyominaisuutta, ja ne ovat kentän tärkein tieto:

| Ominaisuus | Arvot | Merkitys |
|------------|-------|------------------------------------------------|
| `sw` | `rw`, `r`, `w`, `rw1`, `w1`, `na` | mitä ohjelmisto voi väylän kautta tehdä |
| `hw` | `rw`, `r`, `w`, `na` | mitä laitteisto näkee tai ohjaa |

Kentän toteutus seuraa yhdistelmästä. `sw = rw; hw = r` on tavallinen
ohjausbitti: ohjelmisto kirjoittaa, ja laitteisto saa arvon lähtönä.
`sw = r; hw = w` on tilakenttä: laitteisto antaa arvon tulona joka
jaksolla, eikä kenttään tarvita kiikkua lainkaan. `sw = rw; hw = rw`
tarkoittaa, että molemmat voivat kirjoittaa, ja silloin on päätettävä,
kumpi voittaa samalla jaksolla. SystemRDL määrittelee tämän
ominaisuudella `precedence`: oletuksena ohjelmiston kirjoitus voittaa
(`precedence = sw`), ja `precedence = hw` kääntää järjestyksen.

Ajastimen loput rekisterit:

```{.systemverilog tiedosto="esimerkit/rdl/ajastin.rdl" osa="status"}
```

`LASKURI.ARVO` on laitteiston arvo (`sw = r; hw = w`), joten sillä ei
ole nollausarvoa. `STATUS.VALMIS` on lippu, jonka laitteisto asettaa
(`hwset`) ja ohjelmisto nollaa kirjoittamalla ykkösen
(`onwrite = woclr`). Se on keskeytyslähde (`intr`). Rekisterin jälkeinen
dynaaminen sijoitus `STATUS.VALMIS->enable = CTRL.IE` kytkee
keskeytyksen sallinnan toiseen kenttään. Näitä ominaisuuksia käsitellään
seuraavassa luvussa.

## Kääntäjä ja malli

Kuvaus käännetään kahdessa vaiheessa. *Kääntäminen* (compile) lukee
tiedostot ja tarkistaa syntaksin. *Elaborointi* (elaborate) rakentaa
mallin: se valitsee ylimmän osoitekartan, sijoittaa parametrit,
laskee osoitteet ja tarkistaa semantiikan, kuten päällekkäiset
kentät ja liian leveät nollausarvot. Komentorivityökalu `peakrdl`
tekee molemmat ennen jokaista generointia, ja Python-ohjelma voi tehdä
ne itse kirjaston `systemrdl-compiler` avulla:

```{.python tiedosto="esimerkit/kuvaus/kaanna.py" osa="kaanna"}
```

Kääntäjän viestit kulkevat `MessagePrinter`-oliolle. Oletuksena se
tulostaa ne värikoodein, mutta esimerkkien `Keraaja` kerää ne listaan,
jotta ne voi tulostaa ja testata:

```{.python tiedosto="esimerkit/kuvaus/kaanna.py" osa="keraaja"}
```

Elaboroitu malli on solmupuu (`AddrmapNode`, `RegNode`, `FieldNode`),
jonka jokaiselta solmulta voi kysyä ominaisuuksia
(`get_property("sw")`), osoitteen (`absolute_address`) ja lapset.
Esimerkkien omat generaattorit eivät käytä solmuja suoraan, vaan ne
muunnetaan ensin pieniksi tietueiksi:

```{.python tiedosto="esimerkit/kuvaus/malli.py" osa="tietueet"}
```

```{.python tiedosto="esimerkit/kuvaus/malli.py" osa="rekisterit"}
```

`descendants(unroll=True)` käy läpi koko puun, ja taulukot puretaan
alkioiksi. `get_rel_path` antaa polun suhteessa ylimpään
osoitekarttaan, esimerkiksi `STATUS` tai `KANAVA[1].OHJAUS`.

Pääsytapa ilmaistaan UVM:n lyhenteinä, koska sama sanasto on käytössä
UVM:ssä, IP-XACT:ssa ja useimmissa rekisterityökaluissa:

```{.python tiedosto="esimerkit/kuvaus/malli.py" osa="paasy"}
```

Esimerkki `01-malli.py` tulostaa ajastimen mallin:

```{.python tiedosto="esimerkit/01-malli.py" osa="taulukko"}
```

```{.tuloste tiedosto="esimerkit/01-malli.odotettu"}
```

Taulukko on jo käyttökelpoinen tuote: se on rekisterikartan tiivis
yhteenveto, joka on aina ajan tasalla. Kaikki myöhemmät generaattorit
ovat samaa rakennetta: malli sisään, teksti ulos.

## Käytännössä

- **Kirjoita osoitteet näkyviin.** Automaattinen sijoittelu siirtää
  osoitteita, kun kuvaukseen lisätään rekisteri. Eksplisiittinen `@`
  pitää ohjelmistorajapinnan vakaana.
- **Aseta oletukset kerran.** `default regwidth`, `default sw` ja
  `default hw` lyhentävät kuvausta ja tekevät poikkeukset näkyviksi:
  jokainen kentässä erikseen kirjoitettu `sw` tai `hw` on tietoinen
  valinta.
- **Kuvaa jokaiselle kentälle `desc`.** Kuvaus päätyy käsikirjaan,
  SVD-tiedostoon ja IP-XACT:iin. Rekisterin `name` on lyhyt nimi,
  `desc` täydellinen selitys.
- **Käytä kääntäjää kirjastona.** Python-rajapinta antaa saman
  tarkistetun mallin kuin komentorivityökalut, joten omat generaattorit
  ja tarkistukset ovat lyhyitä.

## Itsearviointi

- Osaat kirjoittaa SystemRDL-kuvauksen osoitekartasta, rekistereistä ja
  kentistä nollausarvoineen ja osoitteineen.
- Osaat valita kentälle `sw`- ja `hw`-pääsyn ja selittää, millainen
  toteutus kustakin yhdistelmästä syntyy.
- Osaat kääntää ja elaboroida kuvauksen Pythonilla ja käydä mallin
  rekisterit ja kentät läpi.
- Osaat muuntaa kentän pääsyn UVM-lyhenteeksi (RW, RO, W1C, RC ...).
