# Säikeet ja kontekstinvaihto

Säie (engl. thread) on suorituksen kulku: ohjelmalaskuri, rekisterit
ja pino. Prosessissa on aina vähintään yksi säie, ja kaikki saman
prosessin säikeet jakavat osoiteavaruuden, avoimet tiedostot ja
signaalinkäsittelijät. Säikeiden luonti ja niiden välinen viestintä on
siksi halvempaa kuin prosessien: dataa ei tarvitse kopioida, riittää
että toinen säie lukee samaa muistia. Hinta on se, että jaetun datan
käyttö on synkronoitava (luku 14), ja yhden säikeen muistivirhe kaataa
koko prosessin.

C-kielen taidossa säikeitä käytettiin kielen `<threads.h>`-rajapinnan
kautta. Tässä luvussa käytetään POSIXin pthread-rajapintaa, joka
on Unixeissa se varsinainen toteutus ja tarjoaa enemmän: esteet,
lukijat–kirjoittajat-lukot, ominaisuusoliot ja suoritinaffiniteetin.

## Säikeen luonti ja odotus

`pthread_create` käynnistää funktion uudessa säikeessä ja välittää
sille yhden `void *`-argumentin. Funktion paluuarvon saa
`pthread_join`-kutsulla, joka myös vapauttaa säikeen resurssit – se
on säikeiden `waitpid`. Säie, jota ei koskaan odoteta, on irrotettava
(`pthread_detach`), tai siitä jää zombi.

Esimerkki laskee miljoonan luvun summan neljässä osassa. Kukin säie
kirjoittaa tuloksensa omaan rakenteeseensa, joten säikeet eivät
kilpaile samasta muistista, eikä lukkoja tarvita:

```{.c tiedosto="esimerkit/03-saikeet.c" osa="osa"}
```

```{.c tiedosto="esimerkit/03-saikeet.c" osa="luo"}
```

```{.tuloste tiedosto="esimerkit/03-saikeet.odotettu"}
```

Tulosteesta näkyy kolme asiaa. Ensinnäkin `thread_local`-muuttuja
(C23:ssa avainsana) on jokaisella säikeellä oma: säikeet laskivat
omaansa 250 000:een, mutta pääsäikeen kopio on yhä nolla. `errno` on
toteutettu samalla tavalla, minkä vuoksi säikeet eivät sotke toistensa
virhekoodeja. Toiseksi jokaisella säikeellä on oma ytimen tunniste
TID, ja vain pääsäikeen TID on sama kuin prosessin PID. Linuxissa säie
on ytimen silmissä tavallinen tehtävä (`task_struct`), joka jakaa
muistin muiden kanssa; `/proc/<pid>/task` listaa ne. Kolmanneksi
testityökalut voivat lisätä omia säikeitään: ThreadSanitizer
käynnistää taustasäikeen, joten esimerkki tarkistaa vain alarajan.

`pthread_barrier_t` on *este*: jokainen säie odottaa
`pthread_barrier_wait`-kutsussa, kunnes ennalta sovittu määrä säikeitä
on saapunut. Esimerkissä este pitää kaikki säikeet elossa sen ajan,
kun pääsäie laskee ne.

### Mitä säie omistaa

| Jaettu kaikkien säikeiden kesken | Säiekohtainen |
|------------------------------------------|------------------------------|
| osoiteavaruus: koodi, globaalit, keko | rekisterit ja ohjelmalaskuri |
| avoimet tiedostokuvaajat | pino |
| signaalinkäsittelijät | signaalimaski |
| PID, käyttäjätunnisteet, nykyinen hakemisto | TID, `errno`, `thread_local`-muuttujat |

Pinon koko on Linuxissa oletuksena 8 MiB (`ulimit -s`), ja sen voi
asettaa ominaisuusoliolla `pthread_attr_setstacksize`. Pinon perässä
on suojasivu, joten ylivuoto kaatuu sivuvirheeseen eikä turmele
naapurin pinoa.

## Kontekstinvaihto

Kun ydin vaihtaa suorittimella ajettavan säikeen, se tekee
*kontekstinvaihdon*:

1. Siirtyminen ytimeen: ajastinkeskeytys, järjestelmäkutsu tai
   sivuvirhe. Käyttäjän rekisterit tallennetaan ytimen pinoon jo
   ansassa.
2. Vuorontaja valitsee seuraavan säikeen (luku 4).
3. Ytimen oma pino-osoitin ja kutsun säilyttämät rekisterit
   vaihdetaan (`__switch_to`). Liukulukurekisterit tallennetaan, jos
   säie on käyttänyt niitä.
4. Jos uusi säie kuuluu eri prosessiin, osoiteavaruus vaihdetaan:
   sivutaulun juuri (`satp` RISC-V:ssä, `CR3` x86:ssa). ASID- tai
   PCID-tunnisteiden ansiosta TLB:tä ei tarvitse tyhjentää kokonaan.
5. Paluu käyttäjätilaan uuden säikeen tallennetuilla rekistereillä.

Itse vaihto kestää mikrosekunnin luokkaa. Suurempi hinta on usein
epäsuora: uuden säikeen data ei ole välimuisteissa eikä sen
osoitteenmuunnokset TLB:ssä. Saman prosessin säikeiden välinen vaihto
on halvempi, koska osoiteavaruus säilyy.

Vaihtoja on kahta lajia. *Vapaaehtoinen* vaihto syntyy, kun säie
odottaa jotain – I/O:ta, lukkoa, unta – ja luovuttaa suorittimen
itse. *Tahaton* vaihto syntyy, kun vuorontaja keskeyttää säikeen,
koska sen aikaviipale loppui tai tärkeämpi säie heräsi. Ydin laskee
molemmat, ja `getrusage(RUSAGE_THREAD, …)` palauttaa ne kentissä
`ru_nvcsw` ja `ru_nivcsw`. Esimerkin funktio `vaihdot` lukee ne.
Säie, joka nukkuu 20 kertaa, tekee vähintään 20 vapaaehtoista
vaihtoa:

```{.c tiedosto="esimerkit/03-vaihdot.c" osa="odotus"}
```

Kun kaksi säiettä kiinnitetään samaan suorittimeen ja kumpikin pyörii
laskusilmukassa 0,3 sekuntia, kumpikin joutuu luovuttamaan
suorittimen toiselle kesken laskun:

```{.c tiedosto="esimerkit/03-vaihdot.c" osa="kilpailu"}
```

```{.tuloste tiedosto="esimerkit/03-vaihdot.odotettu"}
```

Samat laskurit näkyvät komentoriviltä: `/proc/<pid>/status` (kentät
`voluntary_ctxt_switches` ja `nonvoluntary_ctxt_switches`) ja
`/usr/bin/time -v`. Paljon tahattomia vaihtoja kertoo, että
suorittimia on liian vähän säikeisiin nähden; paljon vapaaehtoisia,
että ohjelma odottaa – usein lukkoa tai pieniä I/O-operaatioita.

## Ydinsäikeet ja käyttäjäsäikeet

pthread-säikeet ovat Linuxissa *1:1-malli*: jokainen käyttäjän säie on
oma ytimen säikeensä, ja ydin vuorontaa ne. Vaihtoehtoja on kaksi.
*N:1-mallissa* kirjasto vuorontaa monta käyttäjäsäiettä yhdellä
ytimen säikeellä: vaihto on halpa funktiokutsu, mutta yksi estävä
järjestelmäkutsu pysäyttää kaikki, eivätkä säikeet käytä montaa
suoritinta. *M:N-malli* (Go:n gorutiinit, Erlangin prosessit, Javan
virtuaaliset säikeet) jakaa monta kevyttä säiettä muutamalle ytimen
säikeelle ja muuttaa estävät kutsut ei-estäviksi kulissien takana.

Ydin käyttää lisäksi omia säikeitään, joilla ei ole käyttäjätilaa
lainkaan: `ps`-listauksen hakasulkeissa näkyvät `[kworker/0:1]` ja
`[ksoftirqd/0]` hoitavat viivästettyä työtä ja keskeytysten
jälkikäsittelyä.

## Käytännössä

- **Anna jokaiselle säikeelle oma tulospaikka:** taulukko
  rakenteita, jotka pääsäie yhdistää `pthread_join`-kutsujen jälkeen,
  ei tarvitse lukkoja.
- **Odota tai irrota jokainen säie:** `pthread_join` tai
  `pthread_detach`, muuten resurssit vuotavat.
- **Älä välitä pino-osoitinta säikeelle, joka elää funktiota
  pidempään:** argumentin on oltava elossa koko säikeen ajan.
- **Mittaa vaihdot ennen optimointia:** `getrusage` ja
  `/proc/<pid>/status` kertovat, odottaako ohjelma vai kilpaileeko se
  suorittimesta.
- **Aja säieohjelmat ThreadSanitizerilla:** kilpatilanne voi jäädä
  piiloon tuhansissa ajoissa mutta näkyy TSanille ensimmäisellä
  kerralla.

## Itsearviointi

- Osaat luoda säikeitä, välittää niille argumentteja ja kerätä niiden
  tulokset ilman lukkoja.
- Osaat luetella, mitä säikeet jakavat ja mikä on säiekohtaista,
  ja selittää `thread_local`-muuttujan ja `errno`n yhteyden.
- Osaat kuvata kontekstinvaihdon vaiheet ja selittää, miksi
  prosessien välinen vaihto on kalliimpi kuin säikeiden.
- Osaat erottaa vapaaehtoiset ja tahattomat kontekstinvaihdot ja
  mitata ne.
- Osaat verrata 1:1-, N:1- ja M:N-säiemalleja.
