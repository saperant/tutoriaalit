# Johdanto

Tämän repositorion tutoriaalit eivät ole irrallisia oppaita, vaan ne
muodostavat *taitopuun*. Jokainen tutoriaali opettaa yhden taidon, ja
taito voi edellyttää toisia taitoja. Kun esitiedot hallitaan, taito
avautuu, ja se puolestaan avaa uusia taitoja. Kiinteiden kurssipolkujen
sijaan oppija voi kulkea puussa kohti sitä osaamista, jota hän
tarvitsee.

*Roolit* ovat ammattiprofiileja, kuten laitteistoarkkitehti tai
sulautettujen ohjelmistojen kehittäjä. Rooli määritellään muutamana
tavoitetaitona, ja sen polku on näiden tavoitteiden ja kaikkien niiden
esitietojen joukko. Samat perustaidot palvelevat useita rooleja: C-kieli
on osa lähes jokaista polkua.

## Periaatteet

1. **Yksi taito, yksi tutoriaali.** Taito on rajattu kokonaisuus, jonka
   laajuus on 2–5 opintopistettä. Laajempi aihe jaetaan useaksi
   taidoksi.
2. **Esitiedot ovat välttämättömiä.** Taito edellyttää toista vain, jos
   sen sisältöä ei voi ymmärtää ilman sitä. Esitiedoiksi merkitään vain
   välittömät esitiedot. Jos A edellyttää B:tä ja B C:tä, A:n kohdalla ei
   mainita C:tä erikseen. Näin kaaviosta näkee suoraan, mikä mahdollistaa
   minkä.
3. **Kaikki on testattavissa.** Jokaiselle taidolle on määritelty,
   miten sen esimerkit testataan automaattisesti. Työkalut ovat avointa
   lähdekoodia, jotta testit voi ajaa missä tahansa: esimerkiksi
   Verilator, Yosys ja cocotb laitteistosuunnittelussa, QEMU sulautetuissa
   järjestelmissä ja Mesan ohjelmistototeutus grafiikkarajapinnoissa.
4. **Puu on dataa.** Taitopuu on kirjoitettu tiedostoon `taitopuu.toml`.
   Tarkistin varmistaa, ettei puussa ole syklejä, tarpeettomia
   esitietoja tai viittauksia puuttuviin taitoihin, ja että jokainen taito
   kuuluu johonkin rooliin. Tämän dokumentin kaaviot, taulukot ja kuvaukset
   generoidaan samasta tiedostosta.

## Taitopuun lukeminen

Kunkin taidon *taso* on sen pisimmän esitietoketjun pituus. Tason 1
taidoilla ei ole esitietoja. Tason 5 taito edellyttää vähintään neljää
peräkkäistä taitoa. Saman tason taidot eivät riipu toisistaan, joten
ne voi opiskella missä järjestyksessä tahansa tai rinnakkain.

*Laajuus* on arvio opintopisteinä. Yksi opintopiste vastaa noin
27 tunnin työtä, joten 5 op:n tutoriaali on noin 135 tunnin kokonaisuus
harjoituksineen. Koko taitopuun laajuus on 240 op, mikä on saman verran
kuin ammattikorkeakoulun insinöörin tutkinto. Yksittäisen roolin polku
on tästä noin kolmannes tai puolet.

## Ohjaavat lähteet

Taitopuun aiherajauksessa on käytetty kahta ohjaavaa lähdettä:
roadmap.sh-sivuston opintopolkuja ja ammattikorkeakoulujen
insinöörikoulutuksen opintojaksorakennetta.

### roadmap.sh

roadmap.sh on yhteisön ylläpitämä kokoelma ohjelmistoalan
opintopolkuja. Siitä on käyty läpi seuraavien polkujen aiheet:
C, C++, Rust, Python, Computer Science, Data Structures and Algorithms,
Linux, Shell/Bash, Git ja GitHub, Cyber Security, Network Engineer,
System Design, Game Developer, Server Side Game Developer, DevOps,
Docker ja Kubernetes. Kunkin taidon kohdalla mainitaan polut, joiden
aiheita taito kattaa.

roadmap.sh:n sisältö on tekijänoikeudella suojattua, eikä sen
lisenssi salli sisällön uudelleenjulkaisua. Siksi tähän repositorioon ei
ole kopioitu roadmap.sh:n tekstiä, kuvia tai rakennetta. Polkuja on
käytetty vain tarkistuslistana siitä, mitä aiheita kullakin alueella
yleisesti pidetään keskeisinä. Kaikki tutoriaalien sisältö kirjoitetaan
itse.

roadmap.sh:ssa ei ole polkuja sulautetuille järjestelmille,
laitteistosuunnittelulle (RTL, FPGA, korkean tason mallinnus),
signaalinkäsittelylle eikä takaisinmallinnukselle. Näiden alueiden
rakenne perustuu alan vakiintuneeseen opetukseen ja käytäntöihin.

### Ammattikorkeakoulut

Taitojen laajuudet ja jako opintojaksoiksi noudattavat suomalaisten
ammattikorkeakoulujen insinöörikoulutuksen rakennetta: tyypillinen
opintojakso on 3–5 op, ja tutkinto on 240 op. Kunkin taidon kohdalla
mainitaan tyypillinen vastaava opintojakson nimi, kuten
*Digitaalitekniikka*, *Mikrokontrollerit* tai *Tietoliikennetekniikka*.
Nimet ovat yleisiä nimityksiä eivätkä viittaa tietyn oppilaitoksen
opetussuunnitelmaan. Oppilaitosten opinto-oppaita ei saatu haettua
tätä versiota laadittaessa. Vertailu yksittäisiin opetussuunnitelmiin
on luonteva jatkokehityskohde.

## Esimerkki: laitteistoarkkitehti

Laitteistoarkkitehti työskentelee kolmella tasolla: hän mallintaa
järjestelmää korkean tason malleilla (*high-level model*, HLM), toteuttaa
ja verifioi laitteiston rekisterinsiirtotasolla (RTL) ja automatisoi
työkaluketjuja skripteillä. Taitopuussa nämä ovat kolme toisiinsa
kietoutuvaa juonnetta:

- **Mallinnus:** C-kieli → Moderni C++ → Korkean tason mallinnus
  (SystemC/TLM) → Arkkitehtuurin mallinnus ja suunnittelutilan
  tutkiminen. Mallinnus edellyttää myös ymmärrystä siitä, mitä
  mallinnetaan: digitaalitekniikka → assembly → tietokonearkkitehtuuri.
  Lisäksi tarvitaan kiinteän pilkun aritmetiikkaa, jotta mallit voi
  tehdä bittitarkoiksi.
- **Toteutus:** Digitaalitekniikka → RTL-suunnittelu → Laitteiston
  verifiointi ja FPGA-toteutus.
- **Työkalut:** Ohjelmoinnin perusteet → Python työkaluohjelmointiin →
  EDA-työkaluketjujen automatisointi. Python on myös nykyaikaisen
  verifioinnin kieli (cocotb), joten verifiointi edellyttää sitä.

Juonteet kohtaavat arkkitehtuurin tutkimisessa, jossa korkean tason
malleilla, suorituskykyanalyysillä ja todennäköisyyslaskennalla
vertaillaan toteutusvaihtoehtoja ennen kuin niistä kirjoitetaan RTL:ää.
Valinnaisina syvennyksinä polulle sopivat korkean tason synteesi,
DSP-algoritmien laitteistototeutus ja kääntäjätekniikka.

Seuraavat luvut esittelevät koko taitopuun, roolipolut ja jokaisen
taidon suunnitellun sisällön. Viimeinen luku ehdottaa järjestystä,
jossa tutoriaalit kannattaa kirjoittaa.
