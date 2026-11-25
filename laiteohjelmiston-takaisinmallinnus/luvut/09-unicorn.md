# Emulointi Unicornilla

QEMU ajaa koko laitteen; usein halutaan ajaa vain yksi funktio
nähdäkseen, mitä se laskee. *Unicorn* on QEMU:n suoritusytimestä
irrotettu kirjasto, joka emuloi prosessoria ilman konetta tai
oheislaitteita. Sillä voi kartoittaa muistin itse, asettaa rekisterit
ja ajaa minkä tahansa koodinpätkän — ihanteellinen yksittäisen
funktion, kuten tarkistus- tai purkualgoritmin, tutkimiseen.

## Laite Unicornissa

Unicorn ei tiedä mitään Cortex-M:stä itsestään, joten muisti
kartoitetaan käsin: flash, RAM ja oheislaitealue. Oheislaitteista
mallinnetaan vain se, mitä funktio tarvitsee — tässä UART0:n lähetys,
jotta tulostava funktio toimii. Funktio ajetaan AAPCS-konvention mukaan:
argumentit rekistereihin `r0`–`r3`, paluuosoite erityiseen osoitteeseen,
johon pysähdytään. `emu`-moduulin `Laite`-luokka kokoaa tämän; UART:n
mallinnus on hook, joka kerää DATA-rekisteriin kirjoitetut tavut:

```{.python tiedosto="esimerkit/tyokalut/emu.py" osa="hookit"}
```

```{.dot otsikko="Unicornissa laitteesta on vain se, mikä kartoitetaan: kolme muistialuetta, yksi sivu paluuosoitteelle ja hook UART0:n rekistereihin."}
digraph {
  rankdir=LR; nodesep=0.2; ranksep=0.55;
  skripti [label="Python-skripti:\nargumentit r0–r3,\nlr = paluusivu,\npc = funktio"];
  subgraph cluster_u {
    label="Unicorn: pelkkä prosessori"; color="#5B6B70"; style=dashed;
    flash [label="0x00000000 flash-kuva"]; ram [label="0x20000000 RAM ja pino"];
    oheis [label="0x40000000 oheislaitealue"];
    paluu [label="0x30000000 paluusivu"];
  }
  hook [label="hook: UART0:n\nkirjoitukset talteen"];
  tulos [label="paluuarvo r0,\nkäskymäärä"];
  skripti -> flash [label="aja"];
  oheis -> hook;
  paluu -> tulos [label="pysähdys"];
}
```

## Tarkistusfunktion ajaminen

Luvussa 5 funktio `0x109fc` tunnistettiin CRC-32:ksi vakiosta
`0xedb88320`. Hypoteesi todistetaan ajamalla funktio ja vertaamalla
tulosta tunnettuun arvoon:

```{.python tiedosto="esimerkit/09-unicorn/emuloi.py" osa="crc"}
```

```{.tuloste tiedosto="esimerkit/09-unicorn/odotettu" osa="s1"}
```

Tuloste täsmää zlibin CRC-32:een merkkijonolle `123456789`
(`0xcbf43926`), joten funktio on standardi CRC-32. Käskymäärä laskee
toisella kutsulla, koska funktio muodostaa CRC-taulukon vain kerran;
tämäkin yksityiskohta näkyy emuloimalla.

## Salausfunktion ajaminen

Kiinnostavin kohde on XTEA-purku (`0x105ac`). Ajamalla se laitteen omaa
avainta ja asetuslohkon salattua kenttää vastaan nähdään, mitä laite
purkaa. Rinnalla ajetaan Python-viitetoteutus sen varmistamiseksi, että
algoritmi on ymmärretty oikein:

```{.python tiedosto="esimerkit/09-unicorn/emuloi.py" osa="purku"}
```

```{.tuloste tiedosto="esimerkit/09-unicorn/odotettu" osa="s2"}
```

Laitteen funktio ja viitetoteutus antavat saman tuloksen, ja
purettu kenttä paljastuu huoltosalasanaksi. **Tämä on luvun tärkein
puolustuksellinen havainto:** kun avain on poltettu laiteohjelmistoon ja
yksikin kuva on saatavilla, salaus ei suojaa mitään — kuka tahansa voi
purkaa salaisuuden emuloimalla laitteen omaa koodia. Oman tuotteen
salasanan tai avaimen löytyminen näin on auditoinnin tulos, joka johtaa
korjaukseen: salaisuudet kuuluvat laitekohtaiseen, suojattuun
avainvarastoon (TPM, turvaelementti, piirin OTP-alue), eivät jaettuun
koodiin. Tätä käsittelee *Sulautettujen järjestelmien tietoturva*.

## Tulostavan funktion ajaminen

Myös sivuvaikutuksellisen funktion voi ajaa, kun tarvittava oheislaite
on mallinnettu. Komennon `versio` käsittelijä kirjoittaa UARTiin:

```{.python tiedosto="esimerkit/09-unicorn/emuloi.py" osa="versio"}
```

```{.tuloste tiedosto="esimerkit/09-unicorn/odotettu" osa="s3"}
```

UART-hook kerää tulosteen, ja versioteksti vahvistaa funktion
tehtävän. Näin yksittäisiä käsittelijöitä voi tutkia ilman, että koko
komentotulkkia tarvitsee ajaa.

## Käytännössä

- **Aja yksittäinen funktio Unicornilla.** Kun haluat tietää, mitä
  funktio laskee, kartoita muisti, aseta argumentit ja aja. Se on
  nopeampaa ja kohdennetumpaa kuin koko laitteen ajo.
- **Vahvista hypoteesi referenssillä.** Tunnistettu algoritmi
  todistetaan ajamalla laitteen funktio ja oma toteutus rinnakkain
  samoilla syötteillä. Jos tulokset täsmäävät, tulkinta on oikea.
- **Mallinna vain tarvittavat oheislaitteet.** Hook UART:n DATA-
  rekisteriin riittää tulostaville funktioille; muuta ei tarvita.
- **Puolustus:** emulointi purkaa kovakoodatun avaimen suojaaman
  salaisuuden vaivatta. Käytä sitä oman tuotteen auditointiin ja siirrä
  avaimet suojattuun avainvarastoon. Fuzzaa emuloituja jäsentimiä
  (kehykset, otsakkeet) löytääksesi puskurivirheet (luku 10).

## Itsearviointi

- Osaat kartoittaa muistin Unicorniin ja ajaa yksittäisen funktion
  AAPCS-konvention mukaan.
- Osaat vahvistaa tunnistetun algoritmin ajamalla laitteen funktion ja
  viitetoteutuksen rinnakkain.
- Osaat mallintaa oheislaitteen hookilla sivuvaikutuksellisen funktion
  ajamiseksi.
- Osaat selittää, miksi laiteohjelmistoon poltettu avain ei suojaa
  salaisuutta, ja mihin avaimet kuuluvat.
