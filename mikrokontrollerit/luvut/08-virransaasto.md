# Virransäästötilat

Paristolla toimiva anturi, joka mittaa lämpötilan kerran minuutissa,
on 99,9 prosenttia ajasta tekemättä mitään. Sen käyttöikä ei riipu
siitä, kuinka nopeasti mittaus tehdään, vaan siitä, kuinka vähän
virtaa kuluu odottaessa. Mikrokontrollerin virrankulutus voi vaihdella
kuusi kertaluokkaa: täydellä teholla laskeva piiri kuluttaa
milliampeereja, syvimmässä unessa oleva nanoampeereja.

## Mihin virta kuluu

CMOS-logiikan virrankulutuksessa on kaksi osaa. *Dynaaminen* kulutus
syntyy, kun transistorit vaihtavat tilaa, ja se on verrannollinen
kellotaajuuteen ja käyttöjännitteen neliöön. *Staattinen* kulutus eli
vuotovirta kuluu aina, kun osa on jännitteellinen, ja se kasvaa
lämpötilan mukana. Keinot seuraavat suoraan:

- **Pysäytä kello** siltä, mikä ei tee mitään: prosessorilta odotuksen
  ajaksi ja käyttämättömiltä oheislaitteilta kokonaan.
- **Tee työ nopeasti ja nuku** (*race to idle*). Kaksinkertainen
  kellotaajuus kuluttaa kaksinkertaisen virran puolet lyhyemmän ajan,
  ja sen jälkeen piiri nukkuu pidempään.
- **Katkaise jännite** osilta, joita ei tarvita. Silloin vuotovirtakin
  loppuu, mutta osan tila menetetään.

## Cortex-M:n lepotilat

Ydin tarjoaa kaksi käskyä ja kolme asetusbittiä. Varsinaiset tilat ja
niiden nimet määrää piirin valmistaja, joka kytkee ytimen
lepopyynnön omaan virranhallintaansa.

| Käsky tai bitti | Merkitys |
|-----------------|----------|
| `wfi` | nuku, kunnes keskeytys tulee odottavaksi |
| `wfe` | nuku, kunnes tapahtumarekisteri on asetettu; nollaa sen |
| `sev` | aseta tapahtumarekisteri (myös muissa ytimissä) |
| SCR.SLEEPDEEP | syvä uni: piiri pysäyttää myös kellolähteitä |
| SCR.SLEEPONEXIT | nukahda heti, kun viimeinen käsittelijä päättyy |
| SCR.SEVONPEND | myös sallimaton odottava keskeytys herättää WFE:n |

Valmistajien tilat muistuttavat toisiaan. Taulukon virrat ovat
suuruusluokkia tyypillisille nykyisille piireille; tarkat arvot ovat
piirin datalehdessä ja riippuvat jännitteestä, lämpötilasta ja
päällä olevista oheislaitteista.

| Tila | Mikä pysähtyy | Herättäjä | Kulutus |
|------|---------------|-----------|---------|
| ajo | ei mikään | – | 30–200 µA/MHz |
| uni (sleep) | prosessorin kello | mikä tahansa keskeytys | noin kolmannes ajosta |
| syvä uni (stop) | nopeat kellot, useimmat oheislaitteet | RTC, nasta, matalan tehon ajastin | 1–50 µA |
| valmiustila (standby) | lähes kaikki, RAM menetetään | RTC, herätysnasta; alkaa resetistä | alle 1 µA |

Syvästä unesta herääminen vie mikrosekunneista satoihin mikrosekunteihin,
koska oskillaattorien on käynnistyttävä ja tasaannuttava. Valmiustilasta
herääminen on reset: ohjelma alkaa alusta, ja säilytettävä tieto on
tallennettava varmistusrekistereihin tai flashiin.

## WFI ja kadonnut herätys

Pääsilmukka nukkuu, kun työtä ei ole: se tarkistaa keskeytyksen
asettaman lipun ja kutsuu WFI:tä, jos lippu on nolla. Näin suoraan
kirjoitettuna silmukassa on kilpailutilanne. Jos keskeytys tulee ehdon tarkistuksen
jälkeen mutta ennen WFI:tä, käsittelijä asettaa lipun ja palaa, ja
prosessori nukahtaa lipusta huolimatta. Se herää vasta seuraavaan
keskeytykseen, joka voi tulla millisekunnin tai tunnin päästä.

Ratkaisu perustuu WFI:n ominaisuuteen: se herää odottavaan
keskeytykseen, vaikka PRIMASK estäisi sen käsittelyn. Tarkistus ja
nukahtaminen tehdään keskeytykset kiellettyinä, ja ne sallitaan
heräämisen jälkeen, jolloin odottanut käsittelijä ajetaan.

```{.c tiedosto="esimerkit/09-uni/main.c" osa="silmukka"}
```

Esimerkki näyttää molemmat tavat. Keskeytys laukaistaan
ohjelmallisesti juuri tarkistuksen ja WFI:n väliin, ja yhden
sekunnin päähän asetettu ajastin toimii varaherätyksenä:

```{.c tiedosto="esimerkit/09-uni/main.c" osa="kadonnut"}
```

```{.c tiedosto="esimerkit/09-uni/main.c" osa="isr"}
```

```{.tuloste tiedosto="esimerkit/testit/09-uni.odotettu"}
```

Väärä tapa heräsi vasta sekunnin päästä ajastimeen, vaikka tapahtuma
oli jo käsitelty. Oikea tapa heräsi heti. Ensimmäinen rivi näyttää,
että oikean silmukan jokainen herätys vastasi yhtä tapahtumaa.

Ilman ohjelmallista laukaisua virhe näkyisi vain harvoin: ikkuna on
muutaman käskyn mittainen. Se on silti todellinen, ja oireena on
satunnainen, keskeytysvälin mittainen viive, jota on lähes mahdoton
jäljittää.

## WFE ja tapahtumat

WFE käyttää yhden bitin *tapahtumarekisteriä*. Jos bitti on asetettu,
WFE nollaa sen ja jatkaa heti; muuten se nukkuu, kunnes jokin asettaa
bitin. Bitin asettavat käsky `sev` (myös toisessa ytimessä), poikkeuksen
alku ja loppu sekä SEVONPEND-asetuksella mikä tahansa uusi odottava
keskeytys. Koska tapahtuma jää muistiin, WFE:llä ei ole WFI:n
kilpailuongelmaa samassa muodossa: tarkistuksen ja WFE:n väliin osunut
tapahtuma saa WFE:n palaamaan heti.

WFE:tä käytetään moniytimisissä piireissä odotukseen lukon
vapautumista (toinen ydin vapauttaa ja kutsuu `sev`), ja SEVONPEND
mahdollistaa heräämisen keskeytyksestä, jota ei haluta käsitellä:
linja jätetään kieltämättä NVIC:ssä, ja ohjelma lukee tilan itse.
QEMU käsittelee WFE:n vihjeenä ja jatkaa heti, joten tätä ei
esitetä esimerkissä.

## SLEEPONEXIT

Joissakin ohjelmissa kaikki työ tehdään keskeytyksissä, ja pääohjelma
vain nukkuu. Silloin SCR.SLEEPONEXIT-bitti saa prosessorin nukahtamaan
suoraan käsittelijän lopusta palaamatta pääohjelmaan. Kehyksen purku ja
uusi tallennus jäävät pois, mikä säästää sekä aikaa että virtaa.
Pääohjelma voi palata asiaan nollaamalla bitin käsittelijässä. QEMU ei
mallinna tätä bittiä.

## Tikki ja syvä uni

Millisekunnin SysTick herättää prosessorin tuhat kertaa sekunnissa,
vaikka työtä olisi kerran sekunnissa. Lisäksi SysTick pysähtyy
syvässä unessa, koska sen kello pysähtyy. Pienen virran järjestelmät
käyttävät siksi *tikitöntä* ajoitusta: ennen nukahtamista lasketaan,
milloin seuraava ajastettu työ on, asetetaan matalan tehon ajastin tai
RTC herättämään silloin, ja heräämisen jälkeen korjataan aikalaskuri
nukutulla ajalla. FreeRTOS:n `configUSE_TICKLESS_IDLE` ja Zephyrin
tikitön ydin tekevät tämän automaattisesti.

## Mittaaminen

Virrankulutusta ei voi päätellä koodista; se mitataan. Tavallinen
yleismittari ei riitä, koska virta vaihtelee nanoampeereista
milliampeereihin mikrosekunneissa. Käytännön työkaluja ovat
kehityskorttien virranmittausliittimet, tarkoitukseen tehdyt
mittalaitteet (esimerkiksi Nordicin Power Profiler Kit ja Joulescope)
sekä sarjavastus ja oskilloskooppi. Kun mittauksen rinnalla vaihdetaan
GPIO-nastan tilaa ohjelman vaiheiden mukaan, näkee, mikä koodin osa
kuluttaa.

Tavallisimmat syyt liian suureen lepovirtaan ovat kelluvat
tulonastat (tulo kelluu kynnysjännitteen tuntumassa, ja tuloaste
kuluttaa virtaa), päälle jääneet oheislaitteet ja kellot, ulkoiset
komponentit, joiden virtaa ei katkaista, sekä debuggeri: kytketty
debuggeri pitää usein ytimen kellot käynnissä unen aikana.

## Käytännössä

- **Nuku aina, kun työtä ei ole**, ja tee tarkistus ja WFI
  keskeytykset kiellettyinä.
- **Selvitä piirin lepotilat ja herättäjät käyttöohjeesta** ennen kuin
  valitset ajastimet ja nastat: kaikki eivät toimi syvässä unessa.
- **Kytke käyttämättömät nastat** määrättyyn tilaan, älä jätä niitä
  kellumaan.
- **Älä herätä prosessoria turhaan.** Tikitön ajoitus ja laitteiston
  DMA tai ajastimet, jotka toimivat itsenäisesti, säästävät
  herätyksiä.
- **Mittaa kulutus ilman debuggeria** ja todellisilla oheislaitteilla.

## Itsearviointi

- Osaat selittää dynaamisen ja staattisen kulutuksen ja *race to idle*
  -periaatteen.
- Osaat kuvata Cortex-M:n lepokäskyt ja SCR:n bitit sekä
  valmistajien tyypilliset lepotilat ja niiden herättäjät.
- Osaat näyttää WFI-silmukan kilpailutilanteen ja kirjoittaa
  nukkumisen oikein.
- Osaat kertoa, miten WFE ja tapahtumarekisteri eroavat WFI:stä.
- Osaat perustella tikittömän ajoituksen ja luetella lepovirran
  tavallisimmat vuotokohdat.
