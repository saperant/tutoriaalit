# Tapahtuma- ja syklipohjainen simulointi

Analyyttinen malli käsittelee keskiarvoja. Kun pyynnöt kilpailevat
resurssista, tulos riippuu niiden ajoituksesta: kuka tuli ensin, kuinka
moni odotti samaan aikaan, ja kuinka kauan resurssi oli varattu.
Simulaattori näkee tämän, koska se toistaa tapahtumat yksi kerrallaan.
Tässä luvussa sama muistijärjestelmä mallinnetaan kolmella
tarkkuustasolla, ja tuloksia verrataan toisiinsa ja luvun 4 MVA:han.

## Kaksi tapaa edetä ajassa

**Syklipohjainen** (*cycle-driven*) simulaattori käy joka kellojaksolla
läpi kaikki komponentit ja päivittää niiden tilan. Malli on suoraviivainen
ja vastaa laitteistoa: jokainen rekisteri ja jono päivittyy kellon
tahdissa. Hinta on se, että työtä tehdään myös jaksoilla, joilla
mitään ei tapahdu.

**Tapahtumapohjainen** (*event-driven*) simulaattori pitää jonoa
tulevista tapahtumista ja hyppää suoraan seuraavaan. Kun laskenta kestää
100 ns, simulaattori ei käy läpi sataa jaksoa vaan herättää ytimen 100 ns
myöhemmin. Hiljaisina aikoina tämä on kertaluokkia nopeampaa, mutta
mallin on itse laskettava, milloin seuraava tapahtuma on.

SystemC tukee kumpaakin. `SC_METHOD`, joka on herkkä kellon nousevalle
reunalle, on syklipohjainen komponentti. `SC_THREAD`, joka odottaa
`wait(t)`, ja TLM-2.0:n annotoidut viiveet ovat tapahtumapohjaisia.
Paketti *Korkean tason mallinnus* esittelee molemmat; tässä niitä
verrataan saman järjestelmän malleina.

## Järjestelmä

$K$ ydintä tekee kukin 1000 hutipyyntöä. Pyyntöjen välissä ydin laskee
1–199 ns, ja sillä on yksi pyyntö kerrallaan kesken. Pyyntö kulkee
väylän läpi (4 ns) muistiohjaimelle, joka palvelee yhden pyynnön
kerrallaan (10 ns), ja DRAM-käyttö kestää vielä 40 ns. Ilman kilpailua
pyynnön viive on 54 ns. Parametrit ovat samat kuin luvun 4
MVA-esimerkissä.

Laskenta-ajat tulevat kiinteän siemenen satunnaislukugeneraattorista,
joten kaikki mallit saavat täsmälleen saman kuorman:

```{.cpp tiedosto="esimerkit/05-muisti/main.cpp" osa="kuorma"}
```

## Kolme mallia

**LT-malli** on paketin *Korkean tason mallinnus* tapaan löyhästi
ajoitettu: ydin lähettää `b_transport`-kutsun väylän kautta muistille,
joka lisää kiinteän viiveen. Väylä ja muisti ovat samat mallit kuin
siinä paketissa (`esimerkit/mallit/`). Kilpailua ei ole: jokainen pyyntö
kestää 54 ns, vaikka sata ydintä lähettäisi samaan aikaan.

```{.cpp tiedosto="esimerkit/05-muisti/main.cpp" osa="ydin"}
```

**Varausmalli** korvaa muistin ohjaimella, joka muistaa, milloin se
vapautuu. Pyyntö alkaa aikaisintaan silloin, ja odotus lisätään
viiveeseen. Malli on edelleen tapahtumapohjainen ja TLM-yhteensopiva:
ydin on sama, vain kohde vaihtuu.

```{.cpp tiedosto="esimerkit/05-muisti/main.cpp" osa="varaus"}
```

**Syklipohjainen malli** kirjoittaa ytimet ja ohjaimen `SC_METHOD`eiksi,
jotka ajetaan joka nanosekunti. Ne viestivät signaaleilla, joiden arvo
näkyy vastaanottajalle seuraavalla jaksolla, kuten rekisterin lähtö.
Ohjaimella on oikea jono, josta se ottaa seuraavan pyynnön, kun edellinen
on palveltu:

```{.cpp tiedosto="esimerkit/05-muisti/main.cpp" osa="sykli"}
```

Mallien kytkentä valitaan komentoriviltä:

```{.cpp tiedosto="esimerkit/05-muisti/main.cpp" osa="kokoonpano"}
```

```{.bash tiedosto="esimerkit/05-muisti/aja.sh"}
```

```{.tuloste tiedosto="esimerkit/05-muisti/odotettu"}
```

Sarakkeet ovat simuloitu aika, saavutettu kaista, pyynnön keskimääräinen
viive ja prosessien heräämiset. Heräämiset mittaavat simuloinnin
työmäärää: ne eivät riipu koneen nopeudesta, toisin kuin seinäkelloaika.

## Tarkkuus

Vertailuesimerkki lukee mallien tulosteen, laskee viiveen virheen
syklimalliin verrattuna ja lisää MVA:n ennusteen luvusta 4:

```{.python tiedosto="esimerkit/05-vertailu.py" osa="virheet"}
```

```{.tuloste tiedosto="esimerkit/05-vertailu.odotettu"}
```

**LT-malli** on oikeassa vain, kun kuorma on kevyt. Kahdeksalla
ytimellä se aliarvioi viiveen 6 %, 16:lla 25 % ja 32:lla 75 %. Kaista
on vielä pahemmin väärin: 32 ytimellä LT-malli ennustaa 13 GB/s, kun
ohjain pystyy enintään 6,4 GB/s:iin. LT-malli on oikea työkalu
ohjelmistokehitykseen, jossa toiminta ratkaisee ja ajoituksen tarkkuus
ei, mutta arkkitehtuurin mitoitukseen se ei sovi.

**Varausmalli** osuu alle 0,3 %:n päähän syklimallista. Pienet erot
tulevat samanaikaisten pyyntöjen järjestyksestä: syklimalli palvelee
saman jakson pyynnöt ytimen numeron järjestyksessä, varausmalli
siinä järjestyksessä, jossa SystemC ajaa säikeet.

**MVA** osuu kevyellä ja raskaalla kuormalla, mutta polven kohdalla
16 ytimellä se yliarvioi viiveen 16 %. MVA olettaa eksponentiaaliset
palveluajat, mutta tämän ohjaimen palveluaika on vakio. Luvun 4 mukaan
vakiopalvelu puolittaa jonotuksen, joten MVA:n virhe on suurin siellä,
missä jonotusta on, mutta ohjain ei ole vielä täynnä.

## Nopeus

Viimeinen sarake on syklimallin ja varausmallin heräämisten suhde:
syklimalli tekee 90–166 kertaa enemmän työtä. Se herättää jokaisen ytimen
joka jaksolla, vaikka ydin vain laskee, ja ohjaimen joka jaksolla, vaikka
jono on tyhjä. Varausmalli herää kahdesti pyyntöä kohden. Kun mallit
antavat saman tuloksen, tapahtumapohjainen on parempi.

Syklipohjaisen mallin etu tulee esiin, kun vuorovaikutukset ovat
monimutkaisia: liukuhihnan vaiheet, jotka lukevat toistensa tilaa joka
jaksolla, tai DRAM, jonka ajoitusrajoitteet (tRCD, tRP, tFAW ja muut)
koskevat jaksoja. Silloin tapahtumien laskeminen etukäteen on yhtä
monimutkaista kuin itse malli, ja virheen riski kasvaa. gem5:n
O3-suoritinmalli ja DRAMSim3 ovat syklipohjaisia; gem5:n muistijärjestelmä
ja verkkomallit tapahtumapohjaisia.

## Kvantti rikkoo varausmallin

Varausmalli on oikein vain, jos pyynnöt saapuvat ohjaimelle
aikajärjestyksessä. Ajallisesti irrotettu ydin (paketin *Korkean tason
mallinnus* luku 9) kulkee simulaatioaikaa edellä ja lähettää pyyntöjä
tulevaisuudesta. Tulosteen viimeinen rivi ajaa varausmallin 16 ytimellä
1 µs:n kvantilla: viive on 632 ns syklimallin 72 ns:n sijaan. Ydin, joka
on mikrosekunnin edellä, varaa ohjaimen tulevaisuudesta, ja ytimet,
joiden pyyntö on oikeasti aiemmin, joutuvat jonoon sen taakse.

Tämä on yleinen ongelma: nopeus tulee siitä, että komponentit eivät
synkronoi, ja tarkkuus siitä, että ne synkronoivat. Ratkaisuja on
kolme. Kvantti pidetään pienenä suhteessa resurssin palveluaikaan; tai
kilpailu mallinnetaan tilastollisesti (esimerkiksi viiveen lisänä, joka
lasketaan kuormasta jonoteorialla); tai käytetään AT-tyylisiä
transaktioita, joissa kohde päättää, milloin pyyntö hyväksytään.

## Käytännössä

- **Sama järjestelmä kahdella mallilla.** Kun nopea ja tarkka malli
  ovat samaa mieltä, nopeaa voi käyttää laajaan tutkimiseen. Kun ne
  eroavat, ero kertoo, mikä ilmiö (tässä kilpailu) puuttuu nopeasta.
- **Mittaa simuloinnin työ, ei aikaa.** Heräämisten, tapahtumien tai
  simuloitujen käskyjen määrä on toistettava mittari. Seinäkelloaika
  riippuu koneesta ja kuormasta.
- **LT toiminnalle, AT tai syklit ajoitukselle.** Ilman kilpailua
  mallinnettu muistijärjestelmä antaa liian hyvän kuvan juuri silloin,
  kun järjestelmä on kiinnostavimmillaan eli kuormitettuna.
- **Varaus on halpa tapa mallintaa kilpailua**, kun pyynnöt tulevat
  aikajärjestyksessä. Tarkista se ajamalla sama kuorma eri kvanteilla:
  tuloksen ei pidä muuttua.

## Itsearviointi

- Osaat selittää syklipohjaisen ja tapahtumapohjaisen simuloinnin erot,
  hinnat ja tyypilliset käyttökohteet.
- Osaat kirjoittaa saman resurssin LT-mallina, varausmallina ja
  syklipohjaisena SystemC-mallina.
- Osaat vertailla malleja toisiinsa ja analyyttiseen ennusteeseen ja
  selittää erot mallien oletuksilla.
- Osaat selittää, miksi ajallinen irrottaminen rikkoo varausmallin, ja
  kolme tapaa korjata ongelma.
