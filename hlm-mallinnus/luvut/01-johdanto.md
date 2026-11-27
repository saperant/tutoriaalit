# Johdanto {.runko-johdanto}

Piirin RTL-kuvaus valmistuu tavallisesti vasta, kun arkkitehtuurin
tärkeimmät päätökset on jo tehty. Silloin on myöhäistä huomata, että
väylä ei riitä, puskurit ovat liian pieniä tai että kiinteän pilkun
luvuista puuttuu kaksi bittiä. Ohjelmistotiimi taas haluaisi aloittaa
ajurien ja käyttöjärjestelmän sovittamisen kuukausia ennen ensimmäistä
FPGA-prototyyppiä. Molempiin tarpeisiin vastaa *korkean tason malli*:
laitteiston toiminnallinen ja tarvittaessa ajoitettu kuvaus, joka on
kirjoitettu ohjelmointikielellä ja simuloituu satoja tai tuhansia kertoja
nopeammin kuin RTL.

Tämä tutoriaali opettaa korkean tason mallinnuksen standardityökalut:
**SystemC** on C++-kirjasto, jolla kuvataan rinnakkain toimivia
laitteistolohkoja, signaaleja ja kelloja, ja **TLM-2.0**
(*transaction-level modeling*) on SystemC:n päälle rakennettu standardi,
jolla lohkot keskustelevat transaktioina eli kokonaisina luku- ja
kirjoituspyyntöinä yksittäisten johtimien sijaan. Molemmat on
standardoitu IEEE 1666 -standardissa, ja kaikki suuret EDA-toimittajat
tukevat niitä.

## Abstraktiotasot

Samaa laitteistoa voi mallintaa usealla tarkkuudella. Mitä tarkempi
malli, sitä hitaampi simulointi ja sitä myöhemmin malli on käytettävissä.

| Taso | Mitä kuvataan | Aika | Nopeus | Käyttö |
|----------------|------------------------|--------------|--------------|------------------------------|
| algoritmi | funktio, ei rakennetta | ei aikaa | nopein | algoritmin ja bittileveyksien valinta |
| LT-transaktio | lohkot, rekisterit, osoitekartta | likimääräinen | 10–100 Mkäskyä/s | virtuaaliprototyyppi, ohjelmistokehitys |
| AT-transaktio | väylän vaiheet ja liukuhihna | vaiheiden tarkkuus | 0,1–1 Mkäskyä/s | arkkitehtuurin suorituskyky |
| syklitarkka | jokainen kellojakso | sykli | hidas | mikroarkkitehtuuri, laitteistomalli HLS:lle |
| RTL | rekisterit ja logiikka | sykli ja delta | hitain | toteutus, synteesi |

Nopeusluvut ovat suuruusluokkia: ne riippuvat mallin koosta ja siitä,
kuinka paljon malli synkronoi. Taulukon tärkein viesti on, että tasojen
välillä on kertaluokkien ero ja että kullekin kysymykselle valitaan
karkein taso, joka siihen vielä vastaa.

*Virtuaaliprototyyppi* on koko järjestelmän malli, jossa prosessorin
käskytason simulaattori (ISS, *instruction set simulator*) ajaa oikeaa
ohjelmistoa ja laitteet ovat LT-tason TLM-malleja. Ohjelmisto ei
huomaa eroa oikeaan laitteeseen: se lukee ja kirjoittaa samoja
rekistereitä samoista osoitteista. Virtuaaliprototyypillä voi kehittää
ajureita ennen piiriä, ajaa regressiotestejä tuhansilla koneilla ja
tutkia virhetilanteita, joita oikeassa laitteessa on vaikea tuottaa.

## Mitä tutoriaali kattaa

| Luku | Aihe | Sisältö | Esimerkkihakemistot |
|-----|---------------------------|--------------------------------|-----------------------------|
| 2 | Ensimmäinen malli | moduuli, portit, signaalit, kello | `01-laskuri` |
| 3 | Prosessit ja tapahtumat | `SC_METHOD`, `SC_THREAD`, ilmoitukset | `02-tapahtumat` |
| 4 | Simulaatioydin | delta-syklit, aika, tavalliset virheet | `03-delta`, `04-aika`, `05-virheet` |
| 5 | Kanavat ja rajapinnat | oma FIFO-kanava | `06-jono` |
| 6 | Bittitarkat tyypit | `sc_int`, `sc_lv`, `sc_fixed`, FIR | `07-tyypit`, `08-fir` |
| 7 | TLM-2.0:n perusteet | generic payload, `b_transport` | `09-tlm-muisti` |
| 8 | Väylä ja oheislaitteet | osoitekartta, rekisterit | `10-vayla` |
| 9 | Ajallinen irrottaminen ja DMI | kvantti, suora muistiväylä | `11-kvantti`, `12-dmi` |
| 10 | AT-mallinnus | neljä vaihetta, liukuhihna | `13-at` |
| 11 | Virtuaaliprototyyppi | RISC-V-ISS ajaa ohjelmaa | `14-prototyyppi` |
| 12 | Keskeytykset | keskeytyslinja, CSR:t, `wfi`, kvantin vaikutus | `15-keskeytykset` |
| 13 | Mallin ja RTL:n vastaavuus | Verilator ja SystemC yhdessä | `16-vastaavuus` |
| 14 | Lopuksi | nyrkkisäännöt, vianetsintä, lähteet | |

Esimerkkihakemistot on numeroitu juoksevasti, ei luvun mukaan; taulukon
viimeinen sarake kertoo, mitkä hakemistot kuuluvat mihinkin lukuun.

Luvut 2–6 käsittelevät SystemC:tä signaalitasolla: miten malli
rakennetaan ja miten simulaattori sen ajaa. Luvun 6 tietotyyppejä
tarvitaan seuraavan kerran vasta luvussa 13, joten sen voi lukea myös
juuri ennen sitä. Luvut 7–10 nostavat
abstraktiotasoa transaktioihin, luku 11 kokoaa osat
virtuaaliprototyypiksi ja luku 12 lisää siihen keskeytykset. Luku 13
palaa RTL:ään: miten varmistetaan, että toteutus tekee saman kuin
malli.

## Esitiedot ja rajaus

Esimerkit ovat C++17:ää, ja tutoriaali olettaa taidon *Moderni C++*:
luokat, mallit (*templates*), lambdat ja RAII. SystemC käyttää
makroja ja moniperintää tavalla, joka selitetään kohdallaan. Taito
*Tietokonearkkitehtuuri* antaa käsitteet muistiväylästä, muistikartasta,
oheislaitteiden rekistereistä ja keskeytyksistä, ja taito *Lukujen
esitys ja kiinteän pilkun aritmetiikka* luvun 6 bittitarkoille
laskuille; sen termit (Q-muodot, vartijabitit, saturaatio) ovat tässä
samat. RTL-suunnittelun (*RTL-suunnittelu SystemVerilogilla*,
*RTL-suunnittelu VHDL:llä*) tuntemus auttaa luvuissa 4 ja 12:
SystemC:n delta-syklit ovat samat kuin VHDL:n ja Verilogin.

Tutoriaali ei käsittele SystemC:n syntetisoitavaa osajoukkoa (taito
*Korkean tason synteesi*), analogia- ja sekasignaalilaajennusta
SystemC AMS eikä UVM-SystemC:tä. Virtuaaliprototyypin prosessori on
pieni opetusmalli: se ottaa keskeytykset konetilassa, mutta
etuoikeustasot, synkroniset poikkeukset ja keskeytysohjain puuttuvat.
Malleilla tehtävät suorituskykyanalyysit ja
laitteisto–ohjelmisto-jako ovat taidossa *Arkkitehtuurin mallinnus ja
suunnittelutilan tutkiminen*, väylät ja osoitekartat oikeassa piirissä
taidossa *SoC-integraatio* ja referenssimallit testipenkeissä taidossa
*Laitteiston verifiointi*.

## Työkalut ja esimerkit

Esimerkit käyttävät Accelleran avoimen lähdekoodin referenssitoteutusta
SystemC 2.3.4, joka sisältää TLM-2.0:n. Ubuntu 24.04:ssä se asennetaan
paketista `libsystemc-dev`; RTL-esimerkki tarvitsee lisäksi Verilatorin
(versio 5). Kehityskontti `.devcontainer/hlm-mallinnus` sisältää kaiken
tarvittavan.

Jokainen esimerkki on hakemisto `esimerkit/NN-nimi/`. Sen `.cpp`-tiedostot
käännetään yhdeksi ohjelmaksi ja ajetaan, ja tulostetta verrataan
tiedostoon `odotettu`. Jos hakemistossa on skripti `aja.sh`, se
rakentaa ja ajaa esimerkin itse, esimerkiksi usealla parametrilla.
Yhteiset TLM-mallit (muisti, väylä, oheislaitteet) ovat hakemistossa
`esimerkit/mallit/`. Kaikki ajetaan näin:

```text
make -C esimerkit -j4        # kääntää, ajaa ja vertaa kaikki esimerkit
make -C esimerkit 09-tlm-muisti   # yksi esimerkki
make -C esimerkit siivoa     # poistaa käännökset
```

Testiskripti asettaa kääntäjän ja valitsimet:

```{.bash tiedosto="esimerkit/testaa.sh" osa="asetukset"}
```

Kaksi asiaa on syytä huomata heti. SystemC-kirjasto on käännetty
tietyllä C++-standardilla, ja linkittäjä tarkistaa, että ohjelma käyttää
samaa: Ubuntun paketti vaatii valitsimen `-std=c++17`, ja `-std=c++20`
tuottaa linkitysvirheen `undefined reference to
sc_api_version_2_3_4_cxx202002L`. Toiseksi kirjasto tulostaa
käynnistyessään tekijänoikeusilmoituksen, jonka ympäristömuuttuja
`SC_COPYRIGHT_MESSAGE=DISABLE` poistaa. Omassa työssä käännetään
tavallisesti CMakella; SystemC-asennus tarjoaa sekä pkg-config- että
CMake-määrittelyt.

> SystemC 3.0 (2024) vaatii C++17:n ja tukee uudempia standardeja, mutta
> jakeluiden paketit ovat vielä 2.3-sarjaa. Tutoriaalin koodi toimii
> molemmissa. Kaupallisissa simulaattoreissa (Siemens Questa, Cadence
> Xcelium, Synopsys VCS) SystemC-tuki on sisäänrakennettu, ja ne
> osaavat simuloida SystemC:tä ja RTL:ää yhdessä.
