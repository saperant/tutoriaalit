# Johdanto {.runko-johdanto}

Oheislaitteen rekisterit ovat laitteiston ja ohjelmiston sopimus.
Sama sopimus kirjoitetaan monta kertaa: RTL toteuttaa rekisterit,
ajurin C-otsake nimeää niiden osoitteet ja bitit, käsikirja kuvaa ne
ihmiselle, UVM-testipenkki mallintaa ne verifiointia varten,
debuggeri näyttää ne SVD-tiedostosta ja käyttöjärjestelmä löytää
laitteen laitepuusta. Jos jokainen näistä kirjoitetaan käsin, ne
alkavat erota toisistaan ensimmäisessä muutoksessa. Virhe näkyy
vasta, kun ajuri kirjoittaa väärään bittiin oikealla piirillä.

Ratkaisu on kirjoittaa sopimus kerran koneluettavaan muotoon ja
tuottaa kaikki muu siitä. Taidoissa *SoC-integraatio* ja
*EDA-työkaluketjujen automatisointi* tämä tehtiin omalla
kuvausmuodolla ja pienellä generaattorilla. Tässä taidossa samaan
käytetään alan standardeja:

- **SystemRDL 2.0** (Accellera) on kieli rekisterien ja
  osoiteavaruuksien kuvaamiseen. Siinä on tarkka semantiikka sille,
  mitä kentän lukeminen ja kirjoittaminen tekevät.
- **IP-XACT** (IEEE 1685) on XML-muoto kokonaisten IP-lohkojen
  kuvaamiseen: portit, väyläliitännät, muistikartat, rekisterit ja
  tiedostot. Työkalut vaihtavat sillä tietoa keskenään.
- **CMSIS-SVD** (Arm) kuvaa mikrokontrollerin oheislaitteet
  debuggereille ja koodigeneraattoreille, ja **laitepuu** kertoo
  käyttöjärjestelmälle, mitä laitteita piirissä on ja missä.
- **UVM-rekisterimalli** on verifiointiympäristön kopio
  rekisterikartasta.

Lisäksi käydään läpi kuvaukset, jotka eivät koske rekistereitä mutta
kulkevat samoissa työkaluketjuissa: ajoitusrajoitteet (SDC),
virranhallinnan aikomus (UPF), solukirjastot (Liberty), fyysiset
kuvaukset (LEF/DEF) ja aaltomuodot (VCD/FST).

## Esitiedot ja rajaus

Taito rakentuu kahden edeltäjänsä päälle, eikä niiden asioita toisteta:

| Taito | Mitä tästä oletetaan |
|------------------|------------------------------------------|
| SoC-integraatio | APB- ja AXI-väylät, rekisterilohkot, muistikartat, keskeytykset ja IP-XACT:n idea |
| EDA-työkaluketjujen automatisointi | Python-vuot, oma rekisterigeneraattori, tuotettujen tiedostojen tahdin tarkistus CI:ssä |

Kolme lukua sivuaa taitoja, jotka eivät ole esitietoja. UVM-
rekisterimalli (luku 8) liittyy taitoon *Laitteiston verifiointi*,
C-otsakkeiden käyttö (luku 7) taitoihin *Mikrokontrollerit ja
bare-metal-ohjelmointi* ja *Oheislaiteväylät* ja laitepuu (luku 10)
taitoihin *Sulautettu Linux* ja *Linux-laiteajurit*. Luvut kertovat
tarvittavan taustan lyhyesti, ja ne voi lukea ilman näitä taitoja.

Rajaus: tässä käytetään valmiita generaattoreita eikä rakenneta omaa
(se tehtiin taidossa *EDA-työkaluketjujen automatisointi*), ja
IP-XACT:sta käsitellään muistikartan vienti ja tuonti, ei kokonaisen
piirin kokoamista `design`-kuvauksista.

## Esimerkit

Kaikki esimerkit käsittelevät samoja kolmea lohkoa:

| Lohko | Kuvaus | Mitä sillä näytetään |
|-----------|------------------------|---------------------------------|
| ajastin | `rdl/ajastin.rdl` | perusrakenteet, regblock, C, UVM, IP-XACT |
| tapahtumat | `rdl/kayttaytyminen.rdl` | kenttien käyttäytyminen: laskurit, pulssit, keskeytykset |
| dma | `rdl/dma.rdl` | parametrit, rekisteritaulukot ja omat ominaisuudet |

Ajastin on sama lohko, jonka *EDA-työkaluketjujen automatisointi*
kuvasi omalla TOML-muodollaan, joten muotoja voi verrata suoraan.
Tiedosto `rdl/soc.rdl` kokoaa lohkot pieneksi järjestelmäpiiriksi,
josta tuotetaan SVD-tiedosto ja laitepuun solmut.

Esimerkkihakemiston rakenne:

| Hakemisto | Sisältö |
|--------------|------------------------------------------------|
| `rdl/` | SystemRDL-kuvaukset ja tahallaan virheelliset kuvaukset (`virheet/`) |
| `kuvaus/` | Python-kirjasto: kääntäminen, malli ja omat generaattorit |
| `tuotettu/` | kuvauksista tuotetut tiedostot, tallennettu versionhallintaan |
| `tb/` | testipenkit tuotetuille rekisterilohkoille |
| `c/` | ajuri, joka käyttää tuotettua otsaketta |
| `muut/` | SDC- ja UPF-esimerkit ja niiden tarkistin |
| `vertailu/` | ajastimen kuvaus omassa TOML-muodossa |

Numeroidut ohjelmat `01-malli.py` … `13-muut.py` ovat lukujen
esimerkit. Jokaisen tulostetta verrataan tiedostoon `.odotettu`.
Ohjelmien numerot seuraavat aiheiden järjestystä, eivät lukujen
numeroita:

| Luku | Ohjelmat |
|------|----------|
| 2 Yksi totuuden lähde | `12-siirtyma` |
| 3 SystemRDL:n perusteet | `01-malli` |
| 4 Kenttien käyttäytyminen | `03-kayttaytyminen` |
| 5 Parametrit, taulukot ja tarkistukset | `04-parametrit`, `02-virheet` |
| 6 Rekisterilohko RTL:ksi | `05-regblock` |
| 7 Ohjelmisto ja dokumentaatio | `06-c`, `07-dokumentit` |
| 8 UVM-rekisterimalli | `08-uvm` |
| 9 IP-XACT | `09-ipxact` |
| 10 CMSIS-SVD ja laitepuu | `10-svd-laitepuu` |
| 11 Työkaluketju ja CI | `11-tahdissa` |
| 12 Muut kuvaukset | `13-muut` |

```text
cd esimerkit
make              # tarkistukset, yksikkötestit ja kaikki esimerkit
make 05-regblock  # yksi esimerkki
make tuota        # tuottaa hakemiston tuotettu/ kuvauksista
```

## Työkalut ja lisenssit

Kaikki työkalut ovat avointa lähdekoodia ja asennettavissa pipillä tai
Ubuntun paketeista. Ne ovat valmiina kehityskontissa
`.devcontainer/kuvausstandardit`.

| Työkalu | Versio | Lisenssi | Tehtävä |
|------------------|---------|----------|----------------------------------|
| systemrdl-compiler | 1.33.0 | MIT | SystemRDL-kääntäjä ja Python-rajapinta |
| PeakRDL | 1.5.0 | LGPL-3.0 | komentorivityökalu ja liitännäiset |
| PeakRDL-regblock | 1.3.1 | LGPL-3.0 | rekisterilohko SystemVerilogina |
| PeakRDL-cheader | 1.2.0 | LGPL-3.0 | C-otsake |
| PeakRDL-uvm | 2.4.0 | LGPL-3.0 | UVM-rekisterimalli |
| PeakRDL-ipxact | 3.5.0 | GPL-3.0 | IP-XACT-vienti ja -tuonti |
| Verilator | 5.020 | LGPL-3.0 / Artistic-2.0 | lint ja simulointi |
| xmllint, dtc, tclsh | Ubuntu 24.04 | avoimia | XML-, laitepuu- ja Tcl-tarkistukset |

Generaattorin lisenssi koskee generaattoria itseään. Se, millä
ehdoilla generaattorin tuottamaa koodia saa käyttää, riippuu
työkalusta ja sen pohjatiedostojen ehdoista. Yrityksessä asia
tarkistetaan työkalukohtaisesti ennen käyttöönottoa, kuten minkä
tahansa ulkopuolisen IP:n kohdalla.

## Miten luet tätä

Luvut 2–5 käsittelevät kuvauksia: miksi standardi, SystemRDL:n
perusteet, kenttien käyttäytyminen sekä parametrit ja tarkistukset.
Luvut 6–10 käyvät läpi kuluttajat yksi kerrallaan: RTL, ohjelmisto ja
dokumentaatio, UVM, IP-XACT sekä SVD ja laitepuu. Luku 11 kokoaa
työkaluketjun ja CI:n. Luku 12 on liitteenomainen katsaus muihin
suunnitteluvuon kuvauksiin, jotka eivät koske rekistereitä.
Kokenut lukija voi aloittaa lukujen itsearvioinneista.
