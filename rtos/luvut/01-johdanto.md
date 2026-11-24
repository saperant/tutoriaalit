# Johdanto {.runko-johdanto}

Reaaliaikakäyttöjärjestelmä (RTOS, *real-time operating system*) on
pieni ydin, joka jakaa mikrokontrollerin prosessoriajan usealle
*tehtävälle*. Jokaisella tehtävällä on oma pinonsa ja oma ohjelmansa,
ja ydin vaihtaa ajettavaa tehtävää prioriteettien perusteella. Toisin
kuin Linux tai Windows, RTOS ei lupaa hyvää keskimääräistä läpäisyä
vaan *ennustettavan* vasteajan: tärkein valmis tehtävä pääsee ajoon
aina, ja ytimen omat toiminnot vievät tunnetun ajan.

Pienimmät laitteet pärjäävät ilman käyttöjärjestelmää. Taidon
*Mikrokontrollerit* luvussa 11 rakennettiin pääsilmukka, tapahtumajono
ja tilakone. Malli toimii, kun kaikki työ on lyhyttä. Se murtuu, kun
mukaan tulee pitkä laskenta (salaus, suodatus, pakkaus) samaan aikaan
kuin tiukka aikaraja (moottorin ohjaus, protokollan kuittaus):
pääsilmukassa pitkä työ on pilkottava käsin palasiksi, ja jokainen
uusi ominaisuus muuttaa kaikkien muiden vasteaikoja. RTOS tekee
pilkkomisen automaattisesti. Pitkä työ kirjoitetaan suoraviivaiseksi
koodiksi matalan prioriteetin tehtävään, ja ydin keskeyttää sen heti,
kun kiireellisempi tehtävä tulee valmiiksi.

Tutoriaali käsittelee

- **reaaliaikaisuutta**: määräajat, vasteaika, huojunta ja
  determinismi sekä jaksollisen tehtävän oikea toteutus
- **tehtäviä ja vuorontamista**: tehtävän tilat, valmislistat,
  etuoikeutus, saman prioriteetin vuorottelu ja idle-tehtävä
- **kontekstinvaihtoa**: miten Cortex-M3 vaihtaa tehtävää PendSV-
  poikkeuksessa ja miksi tehtävillä on oma pinonsa (PSP)
- **keskeytyksiä**: FromISR-funktiot, viivästetty käsittely, BASEPRI
  ja keskeytysprioriteettien raja
- **viestintää ja synkronointia**: jonot, semaforit, tapahtumaryhmät
  ja tehtäväilmoitukset
- **mutexeja ja prioriteetin inversiota**: miksi binäärisemafori ei
  sovi yhteisen resurssin suojaksi ja mitä prioriteetin periytys tekee
- **ajoitusanalyysiä**: nopeusmonotoninen vuorontaminen, Liu–Laylandin
  raja ja vasteaika-analyysi, jonka tulosta verrataan ajoon
- **muistinhallintaa**: staattinen ja dynaaminen varaus, muistipoolit,
  pinon mitoitus ja ylivuodon tunnistus
- **testausta isäntäkoneella** ja **FreeRTOSia ja Zephyria** käytännön
  ytiminä.

Esitiedoiksi oletetaan taito *Mikrokontrollerit*: Cortex-M-
arkkitehtuuri, vektoritaulu ja käynnistyskoodi, NVIC ja keskeytysten
prioriteetit, PRIMASK ja BASEPRI sekä HardFault-analyysi. Siellä
rakennettu käynnistyskoodi, linkkeriskripti ja UART-konsoli ovat tämän
tutoriaalin pohjana. Toinen esitieto on taito *Käyttöjärjestelmät*:
prosessit ja säikeet, vuorontamisalgoritmit, synkronointi ja
lukkiutuminen yleisellä tasolla. Tässä samat asiat tehdään ilman
muistinhallintayksikköä, ilman ydintilan ja käyttäjätilan rajaa ja
aikarajojen ehdoilla.

## Kide: oma pieni ydin

Valmiin RTOSin käyttö on helppoa, mutta sen sisäinen toiminta jää
helposti mustaksi laatikoksi: miksi FromISR-funktio on eri kuin
tavallinen, miksi mutex ei saa olla keskeytyksessä tai miksi
`vTaskDelay` ajelehtii. Tutoriaalin esimerkit ajetaan siksi omalla
noin 1200 rivin (kommentteineen) opetusytimellä, jonka nimi on *Kide*. Sen rajapinta
jäljittelee FreeRTOSia: funktioiden nimet, parametrit ja merkitykset
ovat samat niiltä osin kuin ne on toteutettu, joten esimerkit
kääntyvät pienin muutoksin myös FreeRTOSilla. Luku 12 kertoo erot.

| Tiedosto | Sisältö | FreeRTOSissa |
|----------|---------|--------------|
| `kide.h` | rajapinta ja tyypit | `FreeRTOS.h`, `task.h`, `queue.h`, `semphr.h` |
| `kide_asetukset.h` | asetukset | `FreeRTOSConfig.h` |
| `lista.c` | ytimen listat | `list.c` |
| `tehtava.c` | tehtävät, vuorontaja, tikki | `tasks.c` |
| `jono.c` | jonot, semaforit, mutexit | `queue.c` |
| `tapahtumat.c` | tapahtumaryhmät | `event_groups.c` |
| `muisti.c` | dynaaminen muisti | `heap_1.c` |
| `portti_cm3.c` | Cortex-M3:n portti | `port.c` (ARM_CM3) |
| `portti_isanta.c` | isäntäportti (Linux) | POSIX-portti |

Kide on tehty luettavaksi, ei tuotantoon. Siitä puuttuu tehtävien
poistaminen ja keskeyttäminen, ohjelmistoajastimet, moniydintuki ja
monia tarkistuksia, ja listat on toteutettu yksinkertaisimmalla
tavalla. Kaikki puuttuva on kuitenkin samaa tekniikkaa kuin se, mikä
on mukana.

## Laboratorio

Esimerkit ajetaan QEMU-emulaattorin `mps2-an385`-koneessa (Cortex-M3,
25 MHz), samassa kuin taidossa *Mikrokontrollerit*. Ajon lopuksi
ohjelma kertoo paluuarvonsa semihostingilla, ja testi vertaa
tulosteen ja paluuarvon tallennettuun. Reaaliaikaesimerkkien tuloste
riippuu siitä, missä kohdassa keskeytykset tulevat. Siksi QEMU
ajetaan valitsimella `-icount`, jolloin emuloitu aika etenee
suoritettujen käskyjen eikä seinäkellon mukaan: jokainen ajo on käsky
käskyltä sama, vaikka kone olisi kuormitettu.

```{.make tiedosto="esimerkit/Makefile" osa="liput"}
```

Valitsin `shift=3` tarkoittaa, että yksi käsky vie 2³ = 8 ns emuloitua
aikaa, ja `sleep=off`, että aika hyppää WFI-käskyssä suoraan seuraavaan
keskeytykseen. Kymmenen sekunnin emuloitu ajo vie siksi vain
sekunnin murto-osan. Tiedostot:

- `esimerkit/kide/`: ydin ja Cortex-M3:n portti
- `esimerkit/isanta/`: isäntäportti (luku 11)
- `esimerkit/yhteinen/`: käynnistyskoodi, linkkeriskripti ja konsoli
  taidosta *Mikrokontrollerit* sekä aikajanan piirtäjä
- `esimerkit/NN-nimi/`: esimerkit ja `esimerkit/testit/`: niiden
  odotetut tulosteet.

Komento `make` kääntää ja ajaa kaiken, `make aja E=01-tehtavat` yhden
esimerkin. Tarvittavat työkalut ovat `gcc-arm-none-eabi`,
`libnewlib-arm-none-eabi` ja `qemu-system-arm`; kehityskontissa
(`.devcontainer/rtos`) ne ovat valmiina.

## Ensimmäinen ohjelma

Ensimmäisessä ohjelmassa on kolme tehtävää. Tehtävä on C-funktio, joka
ei palaa: sen runko on ikuinen silmukka, joka tekee työnsä ja jää sitten
odottamaan. `vTaskDelay(n)` siirtää tehtävän odottamaan *n* tikkiä.
Tikki on ytimen ajan yksikkö, tässä yksi millisekunti. Odotuksen
aikana tehtävä ei kuluta prosessoriaikaa.

```{.c tiedosto="esimerkit/01-tehtavat/main.c" osa="tehtavat"}
```

`main` luo tehtävät ja käynnistää vuorontajan. Jokaiselle tehtävälle
annetaan nimi, pinon koko sanoina, parametri, prioriteetti sekä
muisti pinolle ja ohjauslohkolle (TCB). Prioriteetti on luku 0–7, ja
**suurempi luku on tärkeämpi**. NVIC:n keskeytysprioriteeteissa asia on
päinvastoin, mikä on FreeRTOS-ohjelmoijien yleisimpiä sekaannuksia.
`vTaskStartScheduler` ei palaa: siitä lähtien prosessori ajaa
tehtäviä.

```{.c tiedosto="esimerkit/01-tehtavat/main.c" osa="main"}
```

```{.tuloste tiedosto="esimerkit/testit/01-tehtavat.odotettu"}
```

Hetkellä 50 sekä mittaus että raportti heräävät samassa tikissä.
Mittaus tulostaa ensin, koska sen prioriteetti on suurempi. Hetkellä
0 sama järjestys näkyy käynnistyksessä. Valvoja on tärkein ja ajaa
ensimmäisenä, mutta se vain jää odottamaan hetkeen 60, jolloin se
lopettaa ajon.

## Itsearviointi

- Osaat kertoa, mitä RTOS lupaa ja mitä ei, ja milloin pääsilmukka
  riittää.
- Osaat luoda tehtävän ja käynnistää vuorontajan.
- Osaat kääntää ja ajaa tutoriaalin esimerkit ja kertoa, miksi QEMU
  ajetaan `-icount`-valitsimella.
