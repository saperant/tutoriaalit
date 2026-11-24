# Moniytimet ja koherenssi

Vuoteen 2005 asti suorittimet nopeutuivat ilmaiseksi: transistorit
pienenivät, jännite laski samassa suhteessa (Dennardin skaalaus), ja
kellotaajuus nousi ilman, että tehonkulutus pinta-alaa kohden kasvoi.
Kun jännitettä ei enää voinut laskea vuotovirtojen vuoksi, taajuus
pysähtyi 3–5 GHz:iin. Transistoreita tuli silti lisää, ja ne käytettiin
useampaan ytimeen. Moniydin ei kuitenkaan nopeuta yksisäikeistä
ohjelmaa, ja rinnakkaisen ohjelman on jaettava data ytimien kesken.
Tämä luku käsittelee, miten laitteisto pitää jaetun muistin
yhtäpitävänä ja mitä se maksaa.

Rinnakkaisohjelmoinnin työkalut (säikeet, lukot, atomiset muuttujat)
käydään läpi taidossa *Moderni C++*. Tässä katsotaan, mitä niiden alla
tapahtuu.

## Koherenssiongelma

Jokaisella ytimellä on oma L1- ja L2-välimuisti. Jos ydin 0 lukee
muuttujan `x`, ydin 1 kirjoittaa siihen, ja ydin 0 lukee uudelleen,
ytimen 0 välimuistissa on vanha arvo. **Koherenssi** tarkoittaa, että
kullekin osoitteelle:

1. Lukija näkee viimeisimmän kirjoituksen arvon (kun kirjoituksesta on
   kulunut riittävästi aikaa).
2. Kaikki ytimet näkevät saman osoitteen kirjoitukset samassa
   järjestyksessä (kirjoitusten sarjallisuus).

Ratkaisu on **mitätöintiprotokolla**: ennen kuin ydin kirjoittaa
lohkoon, kaikkien muiden ytimien kopiot mitätöidään. Kirjoittajalla on
silloin ainoa kopio, ja seuraava lukija joutuu hakemaan sen.

## MESI

Jokaisella välimuistin rivillä on yksi neljästä tilasta:

| Tila | Merkitys | Saa lukea | Saa kirjoittaa |
|------|----------|-----------|----------------|
| M (*modified*) | ainoa kopio, likainen | kyllä | kyllä |
| E (*exclusive*) | ainoa kopio, puhdas | kyllä | kyllä, siirtyy M:ään hiljaa |
| S (*shared*) | voi olla muillakin, puhdas | kyllä | vasta mitätöinnin jälkeen |
| I (*invalid*) | ei kelvollinen | ei | ei |

Nuuskivassa (*snooping*) toteutuksessa kaikki välimuistit kuuntelevat
yhteistä väylää ja reagoivat muiden pyyntöihin:

- **BusRd**: ydin lukee lohkon, jota sillä ei ole. Jos jollakin on se
  tilassa M, se kirjoittaa datan takaisin (ja usein suoraan lukijalle)
  ja siirtyy S:ään. E siirtyy S:ään. Lukija saa E:n, jos kenelläkään
  muulla ei ollut kopiota, muuten S:n.
- **BusRdX**: ydin kirjoittaa lohkoon, jota sillä ei ole. Kaikki muut
  kopiot mitätöidään (M kirjoittaa ensin takaisin).
- **BusUpgr**: ydin kirjoittaa S-tilaiseen lohkoon. Data on jo
  paikallaan, joten riittää mitätöidä muut.

Saman yhden rivin tilasiirtymät kaaviona. Yhtenäiset kaaret ovat oman
ytimen tapahtumia, katkoviivat toisen ytimen väyläpyyntöjä, joita rivi
nuuskii. Siirtymät M:stä vaativat lisäksi takaisinkirjoituksen:

```{.dot otsikko="MESI-protokollan tilasiirtymät yhdelle riville"}
digraph {
  nodesep=0.9; ranksep=0.6;
  edge [fontsize=8];
  node [shape=circle, width=0.55, fixedsize=true];
  I; {rank=same; E; S;} M;
  I -> E [label="luku (yksin)"];
  I -> S [label="luku (jaettu)"];
  I -> M [label="kirjoitus"];
  E -> M [label="kirjoitus"];
  S -> M [label="kirjoitus\n(BusUpgr)"];
  E -> S [label="BusRd", style=dashed];
  M -> S [label="BusRd", style=dashed];
  S -> I [label="BusRdX,\nBusUpgr", style=dashed];
  E -> I [label="BusRdX", style=dashed];
  M -> I [label="BusRdX", style=dashed];
}
```

Protokolla koodina:

```{.cpp tiedosto="esimerkit/10-mesi.cpp" osa="protokolla"}
```

Kolmen ytimen viitesarja samaan lohkoon:

```{.cpp tiedosto="esimerkit/10-mesi.cpp" osa="jono"}
```

```{.tuloste tiedosto="esimerkit/10-mesi.odotettu"}
```

Ensimmäinen lukija saa E-tilan, koska muilla ei ole kopiota. Kun ydin 1
lukee, molemmat ovat S:ssä. Ytimen 1 kirjoitus tarvitsee vain
päivityksen (BusUpgr), joka mitätöi ytimen 0 kopion. Ytimen 0 kirjoitus
taas vaatii BusRdX:n, koska sillä ei ole kopiota lainkaan, ja se
mitätöi ytimen 2 S-kopion. Sen jälkeen ytimen 0 luku osuu omaan
M-riviin ilman väylää.

## Miksi E-tila

E-tila on MESI:n ero vanhempaan MSI-protokollaan. Ilman sitä
yksityisen datan luku ja kirjoitus maksaa kaksi väylätapahtumaa: BusRd
tuo lohkon S-tilaan ja BusUpgr mitätöi muut kopiot, joita ei ole.
E-tilassa ydin tietää olevansa ainoa, ja kirjoitus on paikallinen:

```{.cpp tiedosto="esimerkit/10-mesi.cpp" osa="msi"}
```

Tuloste näkyy edellä: 200 väylätapahtumaa MSI:llä, 100 MESI:llä.
Useimmat lohkot ovat yksityisiä (pino, säikeen omat muuttujat), joten
ero on suuri. AMD:n MOESI lisää O-tilan (*owned*), jossa likainen lohko
voidaan jakaa ilman takaisinkirjoitusta, ja Intelin MESIF F-tilan
(*forward*), joka nimeää yhden jakajan vastaamaan pyyntöihin.

## Väärä jakaminen

Koherenssi toimii lohkon eikä muuttujan tarkkuudella. Jos kaksi säiettä
kirjoittaa kumpikin omaa muuttujaansa, mutta muuttujat ovat samassa
64 tavun lohkossa, lohko pomppii ytimeltä toiselle jokaisella
kirjoituksella. Tämä on **väärä jakaminen** (*false sharing*):

```{.cpp tiedosto="esimerkit/10-mesi.cpp" osa="vaara"}
```

Kun laskurit ovat 4 tavun päässä toisistaan, 2 000 kasvatusta tuottaa
lähes 4 000 väylätapahtumaa, 2 000 mitätöintiä ja 2 000
takaisinkirjoitusta. Kun ne ovat eri lohkoissa, väylää tarvitaan vain
kahdesti. Oikealla laitteistolla jokainen siirto ytimeltä toiselle maksaa
40–100 ns, joten väärä jakaminen voi hidastaa koodia kymmenkertaisesti,
vaikka ohjelmassa ei ole yhtään jaettua muuttujaa.

Korjaus on sijoittaa säikeiden kuumat muuttujat eri lohkoihin:
`alignas(std::hardware_destructive_interference_size)` C++:ssa, tai
kerätä säiekohtaiset tulokset paikallisiin muuttujiin ja yhdistää ne
lopuksi.

## Hakemistot

Nuuskiva väylä ei skaalaudu: jokainen huti lähetetään kaikille, ja
väylän kaista jaetaan kaikkien ytimien kesken. Suurissa järjestelmissä
käytetään **hakemistoa** (*directory*): jokaisella lohkolla on merkintä,
joka kertoo, millä ytimillä on kopio. Pyyntö menee hakemistolle, joka
lähettää mitätöinnit vain kopioiden haltijoille. Nykyisissä
palvelinsuorittimissa hakemisto on usein L3:n yhteydessä
(*snoop filter*), ja ytimet ovat rengas- tai verkkoyhteyksissä.

## Atomiset operaatiot

Lukko tai laskuri, jota useampi ydin päivittää, tarvitsee
lukea–muokkaa–kirjoita-operaation, jota mikään muu ydin ei voi
keskeyttää. RISC-V tarjoaa kaksi tapaa (A-laajennus):

- **AMO** (*atomic memory operation*): `amoadd.w`, `amoswap.w` ja muut
  tekevät koko operaation yhtenä käskynä. Välimuisti hankkii lohkon
  M-tilaan ja pitää sen, kunnes operaatio on valmis.
- **LR/SC** (*load-reserved*, *store-conditional*): `lr.w` lukee ja
  merkitsee lohkon varatuksi, `sc.w` kirjoittaa vain, jos varaus on
  voimassa (kukaan ei kirjoittanut väliin). Epäonnistunut `sc` toistetaan.

Molemmat ovat koherenssin päällä rakennettuja: niiden hinta on lohkon
hankkiminen yksinoikeudella. Kun monta ydintä kilpailee samasta lukosta,
lohko pomppii väylällä samoin kuin väärässä jakamisessa, ja yksi lukko
voi sarjallistaa koko ohjelman.

## Muistimalli

Koherenssi koskee yhtä osoitetta. **Muistimalli** (*memory consistency
model*) kertoo, missä järjestyksessä *eri* osoitteiden lataukset ja
talletukset näkyvät muille ytimille.

- **Sarjallinen johdonmukaisuus** (SC): kaikki operaatiot näyttävät
  tapahtuvan jossakin yhteisessä järjestyksessä, joka säilyttää kunkin
  ytimen ohjelmajärjestyksen. Intuitiivinen, mutta estää
  kirjoituspuskurin ja monet optimoinnit.
- **TSO** (x86): talletukset voivat jäädä kirjoituspuskuriin, joten
  myöhempi lataus toiseen osoitteeseen voi ohittaa aiemman talletuksen.
  Muut järjestykset säilyvät.
- **RVWMO** (RISC-V) ja ARMin malli: heikko järjestys. Laitteisto saa
  järjestää riippumattomat operaatiot uudelleen, ja ohjelma pyytää
  järjestyksen erikseen `fence`-käskyllä tai `.aq`/`.rl`-bitein
  atomisissa käskyissä.

Ohjelmoijan ei tarvitse muistaa näitä yksityiskohtia, jos hän käyttää
kielen muistimallia: C++:n `std::atomic` oletusjärjestyksellä
(`memory_order_seq_cst`) antaa SC:n kaikilla alustoilla, ja kääntäjä
lisää tarvittavat aidat. Tietokilpailu (*data race*) ilman atomisia
operaatioita on sen sijaan määrittelemätöntä käytöstä juuri siksi, että
laitteisto ei lupaa mitään.

## NUMA

Suuressa palvelimessa on useita suoritinpiirejä (tai yhdessä piirissä
useita sirupaloja, *chiplet*), ja jokaisella on oma muistiohjaimensa.
Ydin pääsee oman solmunsa muistiin nopeammin kuin toisen: tyypillisesti
paikallinen viive on noin 80–100 ns ja etäinen 130–200 ns, ja etäinen
kaista on pienempi. Tämä on **NUMA** (*non-uniform memory access*).
Koherenssi säilyy, joten ohjelma toimii oikein, mutta hitaammin.

Jos osuus $p$ viitteistä menee paikalliseen muistiin, keskimääräinen
viive on $p \cdot t_\text{paik} + (1 - p) \cdot t_\text{etä}$. Kun
$t_\text{paik} = 90$ ns ja $t_\text{etä} = 150$ ns, täysin
paikallinen ohjelma on noin 1,3 kertaa nopeampi kuin satunnaisesti
sijoiteltu, jossa puolet viitteistä on etäisiä.

Linux sijoittaa sivun sen solmun muistiin, jonka ydin koskee siihen
ensimmäisenä (*first touch*). Jos pääsäie alustaa koko taulukon ja
työsäikeet käyttävät sitä eri solmuilla, kaikki muisti on yhdellä
solmulla. Työkalut: `numactl --hardware` näyttää topologian ja viiveet,
`numactl --cpunodebind --membind` sitoo prosessin, ja `perf c2c` löytää
solmujen välillä pomppivat lohkot.

## Käytännössä

- **Jaa työ, älä dataa.** Paras rinnakkainen ohjelma kirjoittaa
  säiekohtaisiin rakenteisiin ja yhdistää tulokset harvoin. Jokainen
  jaettu kirjoitettava lohko on sarjallistava kohta.
- **Erota kuumat muuttujat.** Säiekohtaiset laskurit, jonon pää ja häntä
  sekä lukot omiin lohkoihinsa. Mittaa `perf c2c`:llä.
- **Lukkiutuva laskuri ei skaalaudu.** `fetch_add` yhteen muuttujaan
  sadalta ytimeltä on yhtä nopea kuin yhdeltä ytimeltä, tai hitaampi.
  Käytä säiekohtaisia osasummia.
- **Amdahl rajoittaa.** Jos 5 % työstä on sarjallista, edes ääretön
  määrä ytimiä ei nopeuta yli 20-kertaisesti. Koherenssiliikenne ja
  lukot kasvattavat sarjallista osuutta.
- **Sido säikeet NUMA-järjestelmässä.** Alusta data säikeessä, joka sitä
  käyttää, ja sido säikeet ytimiin (`pthread_setaffinity_np`,
  OpenMP:n `OMP_PROC_BIND`).

## Itsearviointi

- Osaat seurata MESI-protokollan tilat ja väylätapahtumat usean ytimen
  viitesarjalle.
- Osaat selittää, mitä E-tila säästää MSI:hin verrattuna.
- Osaat tunnistaa väärän jakamisen ja korjata sen.
- Osaat kertoa, miten LR/SC ja AMO toimivat koherenssin päällä ja miksi
  kilpailtu lukko on hidas.
- Osaat erottaa koherenssin ja muistimallin sekä selittää NUMA:n
  vaikutuksen ja first touch -periaatteen.
