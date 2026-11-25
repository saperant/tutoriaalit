# FreeRTOS ja Zephyr

Kide opettaa, miten ydin toimii. Tuotantoon valitaan valmis ydin, jonka
takana on vuosien käyttö, testaus, tuki ja usein sertifiointi. Tämä
luku vertaa Kideä kahteen yleisimpään avoimen lähdekoodin RTOSiin ja
kertoo, mitä niissä on enemmän. Vertailu on tehty ytimien
dokumentaation pohjalta: tämän tutoriaalin testit ajavat vain Kideä,
ja ainoa tässä luvussa ajettu esimerkki on ohjelmistoajastin, joka on
rakennettu Kiden päälle FreeRTOSin mallin mukaan.

## FreeRTOS

FreeRTOS on yleisin mikrokontrollerien RTOS. Richard Barry julkaisi
sen vuonna 2003, ja vuodesta 2017 sitä on ylläpitänyt Amazon. Lisenssi
on MIT, joten sitä voi käyttää suljetussakin tuotteessa. Ydin on
muutama C-tiedosto (`tasks.c`, `queue.c`, `list.c`, `timers.c`,
`event_groups.c`, `stream_buffer.c`) sekä portti ja keko. Sen lisäksi
on erillisiä kirjastoja: TCP/IP-pino, MQTT, HTTP, OTA-päivitykset ja
PKCS #11 -rajapinta.

Kiden rajapinta on FreeRTOSin osajoukko. Tärkeimmät vastaavuudet ja
erot:

| Kide | FreeRTOS | Ero |
|--------------|----------------------|---------------|
| `xTaskCreateStatic`, `xTaskCreate` | samat | FreeRTOSissa myös `vTaskDelete`, `vTaskSuspend`, `vTaskResume` |
| `vTaskDelay`, `vTaskDelayUntil` | samat (`xTaskDelayUntil` palauttaa tiedon myöhästymisestä) | |
| `xQueueSend`, `xQueueReceive` | samat, lisäksi `xQueueSendToFront`, `xQueuePeek`, `xQueueOverwrite` | |
| `xSemaphoreCreate...Static`, `Take`, `Give` | samat, lisäksi rekursiivinen mutex | |
| `xEventGroupSetBits`, `WaitBits` | samat, lisäksi `xEventGroupSync` | FromISR-versio viivästetty |
| `xTaskNotifyGive`, `ulTaskNotifyTake` | samat, lisäksi `xTaskNotify` (bitit, arvo) ja useita indeksejä | |
| `pvPortMalloc` (heap_1) | heap_1–heap_5 | |
| ei | ohjelmistoajastimet (`xTimerCreate`) | ajetaan ajastinpalvelun tehtävässä; ks. seuraava osio |
| ei | stream- ja message buffer | yhden kirjoittajan ja lukijan tavuvirta |
| ei | SMP, MPU-portit, tikitön uni, jäljityskoukut | |

Asetukset ovat tiedostossa `FreeRTOSConfig.h`, ja Kiden
`kide_asetukset.h` käyttää samoja nimiä. Tärkeimmät on käyty läpi tässä
tutoriaalissa: `configTICK_RATE_HZ`, `configMAX_PRIORITIES`,
`configUSE_TIME_SLICING`, `configMAX_SYSCALL_INTERRUPT_PRIORITY`,
`configCHECK_FOR_STACK_OVERFLOW` ja `configASSERT`. Kehitysvaiheessa
`configASSERT` kannattaa ottaa käyttöön aina, koska se tarkistaa luvun 5
keskeytysprioriteetit ja monta muuta käyttövirhettä.

Portteja on kymmenille arkkitehtuureille ja kääntäjille. Cortex-M-
porteista on valittava ytimen mukaan: `ARM_CM3`, `ARM_CM4F` (liukuluku-
yksikkö), `ARM_CM4_MPU`, `ARM_CM33` (TrustZone) ja niin edelleen. Väärä
portti toimii usein lähes oikein, esimerkiksi M4F-piirissä
`ARM_CM3`-portti ei tallenna liukulukurekistereitä, ja liukulukuja
käyttävät tehtävät sotkevat toistensa laskennan.

## Ohjelmistoajastimet

Taulukon puutteista yksi on niin yleinen työkalu, että se kannattaa
katsoa tarkemmin. *Ohjelmistoajastin* kutsuu funktiota tietyn ajan
kuluttua tai tasaisin välein ilman, että työlle tarvitaan oma
tehtävä: protokollan aikakatkaisu, LEDin vilkutus, painikkeen
värähtelyn suodatus. FreeRTOSissa ajastimet (`xTimerCreate`,
`xTimerStart`) hoitaa yksi ytimen luoma tehtävä, *ajastinpalvelu*
(*timer daemon*). `xTimerStart` ei käynnistä ajastinta itse vaan
lähettää palvelulle komennon jonossa, ja palvelu nukkuu jonossa
seuraavaan erääntymiseen asti.

Kidessä ajastimia ei ole, mutta ne voi rakentaa sen jonon päälle
samalla periaatteella. Esimerkin toteutus on noin viisikymmentä riviä:

```{.c tiedosto="esimerkit/17-ajastimet/main.c" osa="tyypit"}
```

```{.c tiedosto="esimerkit/17-ajastimet/main.c" osa="kaynnista"}
```

```{.c tiedosto="esimerkit/17-ajastimet/main.c" osa="palvelu"}
```

Palvelun silmukassa on kaksi syytä herätä: jonoon tuli komento, tai
odotuksen aikaraja täyttyi, jolloin lähin ajastin on erääntynyt.
Jaksollisen ajastimen seuraava hetki lasketaan edellisestä
erääntymisestä eikä nykyhetkestä, joten myöhästyminen ei kasaudu
(sama asia kuin `vTaskDelayUntil`in ja `vTaskDelay`n ero luvussa 2).

Takaisinkutsut ajetaan palvelun kontekstissa, sen pinossa ja sen
prioriteetilla. Tästä seuraa kolme sääntöä, jotka esimerkki näyttää:

```{.c tiedosto="esimerkit/17-ajastimet/main.c" osa="kutsut"}
```

```{.c tiedosto="esimerkit/17-ajastimet/main.c" osa="sovellus"}
```

```{.tuloste tiedosto="esimerkit/testit/17-ajastimet.odotettu"}
```

- **Takaisinkutsu ei saa odottaa eikä laskea pitkään.** Hidas
  takaisinkutsu vei seitsemän tikkiä, ja sinä aikana erääntynyt vilkku
  ajettiin kolme tikkiä myöhässä. Kaikki ajastimet jakavat yhden
  tehtävän.
- **Takaisinkutsu herättää, tehtävä tekee.** Aikakatkaisun
  takaisinkutsu vain antaa ilmoituksen, ja sovellustehtävä käsittelee
  tilanteen omalla prioriteetillaan ja omassa pinossaan.
- **Palvelun prioriteetti on ajastimien tarkkuus.** Jokainen palvelua
  tärkeämpi tehtävä viivästyttää takaisinkutsuja. FreeRTOSissa
  prioriteetti on asetus `configTIMER_TASK_PRIORITY`, ja komentojonon
  pituus `configTIMER_QUEUE_LENGTH`: jos jono on täynnä,
  `xTimerStart` odottaa tai epäonnistuu kuten mikä tahansa lähetys.

Ajastin ei korvaa jaksollista tehtävää, jolla on määräaika: sen
ajoitus riippuu muista takaisinkutsuista, eikä sitä voi analysoida
erikseen (luku 9). Tiukat jaksot tehdään omana tehtävänään tai
laitteiston ajastimella.

## Zephyr

Zephyr on Linux Foundationin hallinnoima RTOS, jonka lisenssi on
Apache 2.0. Se on laajempi kuin FreeRTOS: siinä on laiteajurimalli,
laitepuu (*devicetree*) laitteiston kuvaukseen, Kconfig-asetukset kuten
Linuxissa, verkkopinot (IPv4/IPv6, Bluetooth LE, Thread), tiedostojärjestelmät,
USB, lokitus ja komentotulkki. Projekteja hallitaan `west`-työkalulla.
Zephyr sopii laitteisiin, joissa on useita laitteita ja protokollia ja
joiden on toimittava monella piirillä. Hinta on oppimiskynnys ja
suurempi muistin tarve.

Zephyrin käsitteet vastaavat FreeRTOSin käsitteitä, mutta nimet ja
osa merkityksistä ovat toisin:

| Käsite | FreeRTOS | Zephyr |
|----------|------------------|----------------------------|
| tehtävä | task, `xTaskCreate` | thread, `k_thread_create`, `K_THREAD_DEFINE` |
| prioriteetti | suurempi luku tärkeämpi | **pienempi luku tärkeämpi**; negatiiviset ovat yhteistoiminnallisia, joita ei keskeytetä |
| viive | `vTaskDelay(tikit)` | `k_sleep(K_MSEC(10))` |
| jono | `xQueueSend` | `k_msgq_put`, myös `k_fifo`, `k_pipe` |
| semafori | `xSemaphoreTake` | `k_sem_take` |
| mutex | `xSemaphoreCreateMutex` | `k_mutex_lock` (periytys mukana) |
| tapahtumat | event group | `k_event`, `k_poll` |
| asetukset | `FreeRTOSConfig.h` | `prj.conf` (Kconfig) ja laitepuu |

Zephyrissa staattinen määrittely on tavallisin: makrot kuten
`K_THREAD_DEFINE` ja `K_MSGQ_DEFINE` varaavat olion käännösaikana.

## Muita ytimiä ja standardeja

- **Eclipse ThreadX** (aiemmin Azure RTOS ThreadX): kypsä ydin, jolla
  on turvallisuussertifiointeja ja joka on ollut MIT-lisenssillä
  Eclipse-säätiön alla vuodesta 2024.
- **µC/OS-II ja -III**: pitkään kaupallisia, avoimen lähdekoodin
  Apache 2.0 -lisenssillä vuodesta 2020.
- **SAFERTOS**: FreeRTOSin toiminnalliseen malliin perustuva,
  turvallisuussertifioitu (IEC 61508 SIL 3) kaupallinen ydin.
- **VxWorks, QNX, INTEGRITY, PikeOS**: kaupallisia ytimiä isompiin
  järjestelmiin, usein muistinsuojauksella ja POSIX-rajapinnalla.
  QNX on mikroydin, jonka ajurit ovat erillisiä prosesseja.
- **RTEMS**: avoin RTOS, jota käytetään paljon avaruussovelluksissa.
- **CMSIS-RTOS2**: ARM:n määrittelemä yhteinen rajapinta, jonka voi
  toteuttaa usean ytimen päälle. Sen avulla väliohjelmisto ei riipu
  ytimestä.
- **AUTOSAR Classic ja OSEK/VDX**: autoteollisuuden staattisesti
  määritelty käyttöjärjestelmä, jossa tehtävät, resurssit ja
  prioriteettikatot kuvataan työkalulla ennen käännöstä.

## Sertifiointi

Turvallisuuskriittisessä tuotteessa käyttöjärjestelmä on osa
turvallisuusperustelua. Standardit IEC 61508 (yleinen),
ISO 26262 (autot), IEC 62304 (lääkintälaitteet) ja DO-178C (ilmailu)
vaativat, että ohjelmiston kehitysprosessi, vaatimukset, testaus ja
kattavuus on dokumentoitu. Avoimen lähdekoodin ydintä voi käyttää, mutta
sen perustelu on tehtävä itse. Siksi turvallisuuskriittisissä
tuotteissa käytetään usein valmiiksi sertifioitua ydintä (SAFERTOS,
ThreadX, INTEGRITY, QNX, PikeOS) ja sen sertifiointipakettia. Zephyrissä
on käynnissä turvallisuussertifiointia tavoitteleva projekti.

Sertifiointi koskee myös tapaa käyttää ydintä. Tyypilliset vaatimukset
ovat ne, joita tässä tutoriaalissa on suositeltu muutenkin: staattinen
muistinvaraus, rajatut odotukset, analysoidut vasteajat, tarkistetut
keskeytysprioriteetit ja valvottu pinonkäyttö.

## Käytännössä

- **Valitse ydin tuotteen, ei tottumuksen mukaan.** Pieni laite, jossa
  on muutama tehtävä: FreeRTOS tai ThreadX. Monta protokollaa ja
  laitetta, monta piiriä: Zephyr. Turvallisuuskriittinen: sertifioitu
  ydin.
- **Käytä valmistajan tukemaa porttia** ja tarkista sen versio ja
  asetukset itse.
- **Ota `configASSERT` ja pinon ylivuodon tarkistus käyttöön**
  kehitysvaiheessa. Ne löytävät suurimman osan käyttövirheistä.
- **Pidä sovellus irti ytimen rajapinnasta**, jos ytimen vaihto on
  mahdollinen: ohut oma kerros tai CMSIS-RTOS2 tekee siirrosta
  helpomman.
- **Pidä ajastimen takaisinkutsu lyhyenä** ja anna varsinainen työ
  tehtävälle; aseta ajastinpalvelun prioriteetti sen mukaan, kuinka
  tarkkoja ajastimien pitää olla.
- **Muista prioriteettien suunta.** FreeRTOS: suurempi on tärkeämpi.
  Zephyr ja NVIC: pienempi on tärkeämpi.

## Itsearviointi

- Osaat kertoa, mitä FreeRTOSissa on Kiden lisäksi ja mitä tärkeimmät
  asetukset tekevät.
- Osaat selittää, miten ohjelmistoajastimet toimivat ajastinpalvelun
  tehtävässä, ja mitä siitä seuraa takaisinkutsujen sisällölle ja
  tarkkuudelle.
- Osaat kääntää FreeRTOS-ohjelman käsitteet Zephyrin käsitteiksi ja
  muistaa prioriteettien eri suunnan.
- Osaat valita ytimen tuotteen tarpeiden mukaan ja kertoa, mitä
  sertifiointi edellyttää.
