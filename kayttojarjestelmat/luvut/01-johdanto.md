# Johdanto {.runko-johdanto}

Käyttöjärjestelmä on ohjelma, joka jakaa yhden koneen monelle
ohjelmalle niin, että kukin niistä luulee olevansa koneessa yksin.
Prosessori, muisti, levyt ja verkko ovat rajallisia ja jaettuja, mutta
ohjelma näkee oman suorittimensa (prosessi ja säie), oman muistinsa
(virtuaalinen osoiteavaruus) ja nimetyt, pysyvät tavuvirrat
(tiedostot). Näiden kolmen harhan ylläpito on käyttöjärjestelmän
ytimen työ. Samalla ydin estää ohjelmia sotkemasta toisiaan ja
laitteistoa.

Tämä tutoriaali käy läpi käyttöjärjestelmän keskeiset periaatteet
kahdesta suunnasta. Ensin katsotaan, miten POSIX-rajapinta näkyy
C-ohjelmalle Linuxissa: järjestelmäkutsut, prosessit, säikeet,
muistikartoitukset, tiedostokuvaajat, putket, soketit ja signaalit.
Sitten tärkeimmät ytimen osat toteutetaan pieninä, testattavina
simulaatioina: vuorontaja, sivunkorvaus, muistinvaraaja,
levyn vuorontaminen ja oma tiedostojärjestelmä levykuvassa.

- **Prosessit ja järjestelmäkutsut:** käyttäjä- ja ydintila, kutsun
  polku ytimeen, `fork`, `exec` ja `wait`, prosessin tilat, zombit ja
  orvot sekä jäljitys straceliä.
- **Säikeet ja vuorontaminen:** pthread-säikeet, kontekstinvaihto,
  FCFS, SJF, RR ja prioriteetit sekä Linuxin CFS:n periaate.
- **Virtuaalimuisti:** `mmap`, sivuvirheet, copy-on-write,
  sivunkorvausalgoritmit ja muistinvaraajan sisäinen rakenne.
- **Tiedostot ja laitteet:** kuvaajat, inodet, linkit, puskurointi ja
  `fsync`, oma tiedostojärjestelmä sekä merkki- ja lohkolaitteet.
- **Käyttäjät, oikeudet ja suojaus:** prosessin tunnisteet, oikeuksien
  tarkistus, setuid ja kyvyt, resurssirajat sekä eristyksen mekanismit
  (nimiavaruudet, cgroupit, seccomp).
- **Prosessien välinen kommunikaatio:** putket, jaettu muisti,
  viestijonot, UNIX-soketit ja signaalit.
- **Synkronointi ja lukkiutuminen:** mutex, ehtomuuttuja ja semafori,
  klassiset ongelmat sekä lukkiutumisen ehdot ja välttäminen.

## Esitiedot ja rajaus

Tutoriaali rakentuu taidon *Tietokonearkkitehtuuri* päälle. Sieltä
oletetaan tutuiksi etuoikeustasot, ansat ja keskeytykset (luku *Ansat
ja I/O*) sekä sivutaulu ja TLB (luku *Virtuaalimuisti*, Sv32). Tässä
katsotaan, mitä ydin tekee, kun laitteisto on siirtänyt suorituksen
sille: miten se valitsee seuraavan prosessin, mitä sivuvirheen
käsittelijä tekee ja miksi ytimeen siirtyminen maksaa.

C-kieli oletetaan tutuksi taidosta *C-kieli*: osoittimet, rakenteet,
`malloc` ja tiedostojen käsittely stdio-funktioilla. Muut läheiset
taidot käsittelevät samoja asioita eri näkökulmasta, eikä niitä
toisteta täällä:

| Taito | Näkökulma | Tässä tutoriaalissa |
|----------------|-----------------------------|---------------------------|
| Komentorivi ja Linux | prosessit ja signaalit käyttäjälle (`ps`, `kill`, työt) | mitä komentojen alla tapahtuu |
| Objektitiedostot, linkitys ja ABI | ELF, ohjelman lataus, dynaaminen linkittäjä | `exec` ja muistikartta |
| Virtualisointi | kontin rakentaminen nimiavaruuksista ja cgroupeista, hypervisorit | tunnisteet, kyvyt ja eristyksen mekanismit periaatteena |
| C-kieli | säikeet ja lukot kielen tasolla | ytimen ja POSIXin näkökulma |

Jatkotaidot on lueteltu viimeisessä luvussa.

Lukujärjestys seuraa ytimen kolmea harhaa. Luvut 2–4 käsittelevät
suoritinta, luvut 5–7 muistia ja luvut 8–11 tiedostoja, oikeuksia ja
laitteita. Luvut 12–15 kertovat, miten eristetyt prosessit ja säikeet
tekevät yhteistyötä. Jokainen luku nojaa edellisiin, joten ne
kannattaa lukea järjestyksessä.

## Ydin ja sen rakenne

Ydin (engl. kernel) on se osa käyttöjärjestelmää, joka suoritetaan
etuoikeutetussa tilassa. Kaikki muu – komentotulkki, kirjastot,
palvelut – on tavallisia prosesseja. Ytimen rakenteesta on kolme
päälinjaa:

- **Monoliittinen ydin** (Linux, BSD:t): ajurit, tiedostojärjestelmät
  ja vuorontaja samassa osoiteavaruudessa. Nopea, mutta ajurin virhe
  voi kaataa koko järjestelmän.
- **Mikroydin** (seL4, QNX, MINIX 3): ytimessä vain osoiteavaruudet,
  säikeet ja viestinvälitys; ajurit ovat omia prosessejaan.
  Vikasietoinen, mutta jokainen palvelu maksaa viestin.
- **Hybridi** (Windows NT, XNU): mikroytimen rakenne, mutta suuri osa
  palveluista ajetaan ytimen tilassa.

Koneen käynnistyessä laiteohjelmisto (UEFI) lataa
käynnistyslataimen, tämä ytimen, ja ydin käynnistää ensimmäisen
prosessin, jonka numero on 1 (luku 2). Ketju käydään läpi taidossa
*Sulautettu Linux*; tässä tutoriaalissa ydin on jo käynnissä.

Esimerkit ajetaan Linuxissa. Rajapinnat ovat POSIXin mukaisia, ja
Linux-kohtaiset laajennukset (`signalfd`, `/proc`) merkitään tekstissä.

## Esimerkit ja testaus

Esimerkit ovat C23:a. Testaaja kääntää ne GCC 14:llä ja Clang 20:llä
varoitukset virheinä, AddressSanitizerin ja
UndefinedBehaviorSanitizerin kanssa, ja säikeitä käyttävät esimerkit
lisäksi ThreadSanitizerilla. Ohjelma ajetaan tyhjässä väliaikaisessa
hakemistossa, ja sen tulostetta verrataan tallennettuun tulosteeseen.

Prosessinumerot, osoitteet, ajat ja säikeiden järjestys vaihtelevat
ajosta toiseen, joten esimerkit tulostavat vain pysyviä asioita:
paluuarvoja, laskureita, totuusarvoja ja virhekoodien nimiä. Ytimen
osat simuloidaan kiinteällä syötteellä.

Kaikki esimerkit käyttävät pientä otsaketta, joka lopettaa ohjelman
selkeään virheilmoitukseen, jos järjestelmäkutsu epäonnistuu.
POSIX-funktiot ilmoittavat virheestä palauttamalla -1 ja asettamalla
`errno`-muuttujan; pthread-funktiot palauttavat virhekoodin suoraan ja
`mmap` arvon `MAP_FAILED`:

```{.c tiedosto="esimerkit/tarkista.h"}
```

Jokaisen esimerkin alussa oleva `#define _GNU_SOURCE` avaa C23-tilassa
POSIX- ja Linux-laajennukset (`fork`, `MAP_ANONYMOUS` …). Komento
`make testaa` ajaa esimerkit, ja kehityskontissa
(`.devcontainer/kayttojarjestelmat`) on mukana `strace`. Luvun 9
kaksi esimerkkiä tarvitsee pääkäyttäjän oikeudet; luku kertoo, miten
ne ajetaan.
