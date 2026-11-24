# Keskeytykset ja RTOS

Keskeytys on edelleen nopein tapa reagoida laitteeseen. RTOS ei muuta
sitä, mutta se muuttaa sen, mitä käsittelijässä tehdään. Pääsilmukka-
ohjelmassa käsittelijä asettaa lipun tai lisää tavun rengaspuskuriin,
ja pääsilmukka huomaa sen joskus. RTOS-ohjelmassa käsittelijä herättää
tehtävän, joka odottaa juuri tätä tapahtumaa, ja jos tehtävä on
tärkeämpi kuin keskeytetty, se ajaa heti käsittelijän jälkeen.

## FromISR-funktiot

Keskeytyskäsittelijä ei ole tehtävä: sillä ei ole TCB:tä, se ei voi
jäädä odottamaan, ja se ajaa keskeytetyn tehtävän päällä. Siksi ytimen
funktioista on keskeytyksiä varten omat versionsa, joiden nimi päättyy
`FromISR`. Ne eroavat tavallisista kolmella tavalla:

- **Ne eivät odota.** `xQueueSendFromISR` palaa heti, jos jono on
  täynnä. Aikarajaparametria ei ole.
- **Ne eivät vaihda tehtävää itse.** Jos ne herättävät keskeytettyä
  tehtävää tärkeämmän tehtävän, ne asettavat kutsujan muuttujan
  (`pxHigherPriorityTaskWoken`, Kidessä `heratti`). Käsittelijä
  pyytää vaihtoa lopussa makrolla `portYIELD_FROM_ISR`.
- **Ne käyttävät keskeytyksen kriittistä osiota**, joka tallentaa ja
  palauttaa BASEPRI:n vanhan arvon, koska keskeytys voi tulla toisen
  käsittelijän tai tehtävän kriittisen osion päälle.

```{.c tiedosto="esimerkit/kide/jono.c" osa="isr"}
```

Vaihdon pyytäminen vasta lopussa on tärkeää. Jos käsittelijä herättää
kolme tehtävää, vaihtoa pyydetään kerran, ja PendSV valitsee niistä
tärkeimmän, kun käsittelijä on valmis.

## Viivästetty käsittely

Hyvä käsittelijä tekee vain välttämättömän: kuittaa laitteen, lukee
datan, joka muuten katoaa, ja herättää tehtävän. Raskas työ, kuten
protokollan jäsennys, tehdään tehtävässä. Tätä kutsutaan viivästetyksi
käsittelyksi (*deferred interrupt processing*). Linuxissa vastaava jako
on *top half* ja *bottom half*. Jako pitää keskeytysviiveen lyhyenä,
koska käsittelijä ei peitä muita keskeytyksiä pitkään. Lisäksi
käsittelytehtävän prioriteetti voidaan valita muiden tehtävien
joukosta.

```{.c tiedosto="esimerkit/06-keskeytys/main.c" osa="isr"}
```

```{.c tiedosto="esimerkit/06-keskeytys/main.c" osa="kasittelija"}
```

Esimerkissä matalan prioriteetin tehtävä laukaisee keskeytyksen
ohjelmallisesti, kuin laite olisi saanut näytteen valmiiksi.
Kahdella ensimmäisellä kerralla käsittelijä pyytää vaihtoa,
kahdella viimeisellä ei:

```{.c tiedosto="esimerkit/06-keskeytys/main.c" osa="laukaisija"}
```

```{.tuloste tiedosto="esimerkit/testit/06-keskeytys.odotettu"}
```

Kun vaihtoa pyydetään, käsittelytehtävä ajaa ennen kuin laukaisija
ehtii jatkaa: viive on nolla tikkiä, käytännössä muutama mikrosekunti.
Ilman pyyntöä käsittelytehtävä on valmis mutta odottaa seuraavaan
tikkiin, jolloin ydin huomaa, että tärkeämpi tehtävä on valmiina
(FreeRTOS: `xYieldPending`). Viive on silloin jopa tikin, ja huonolla
tuurilla se olisi ilman tätä tarkistusta mielivaltaisen pitkä.
Unohtunut `portYIELD_FROM_ISR` on yleinen ja huomaamaton virhe:
ohjelma toimii, mutta vasteaika on satunnaisesti tikin pidempi.

Usein binäärisemaforia kevyempi tapa on tehtäväilmoitus
`vTaskNotifyGiveFromISR` (luku 7).

## BASEPRI ja prioriteettiraja

Ytimen tietorakenteita muutetaan sekä tehtävistä että keskeytyksistä,
joten muutokset on suojattava. Yksinkertaisin keino olisi kieltää
kaikki keskeytykset PRIMASKilla. Silloin jokainen ytimen kutsu
pidentäisi kaikkien keskeytysten viivettä, myös niiden, joilla ei ole
mitään tekemistä ytimen kanssa. Cortex-M3:n BASEPRI peittää vain
keskeytykset, joiden prioriteetti on annettu arvo tai heikompi. Ydin
nostaa BASEPRI:n arvoon `configMAX_SYSCALL_INTERRUPT_PRIORITY`.

```{.c tiedosto="esimerkit/kide/portti_cm3.c" osa="kriittinen"}
```

Keskeytykset jakautuvat näin kahteen ryhmään:

| NVIC-prioriteetti | Ydin peittää | Saa kutsua FromISR | Käyttö |
|------------------------|----------------------|-------------|------------------------------|
| 0–4 (kiireellisemmät) | ei koskaan | ei | moottorin kommutointi, nopea protokolla |
| 5–7 (heikommat) | kriittisissä osioissa | kyllä | UART, ajastimet, DMA:n valmistuminen |

Kiireellisemmän ryhmän keskeytysten viive ei riipu ytimestä lainkaan,
mutta ne eivät saa kutsua ydintä, koska ydin ei ole suojautunut niiltä.
Jos sellainen käsittelijä kutsuisi `xSemaphoreGiveFromISR`ia kesken
tehtävän kriittisen osion, se muuttaisi listaa, jota tehtävä on
muuttamassa. Kide tarkistaa tämän kuten FreeRTOS
(`vPortValidateInterruptPriority`):

```{.c tiedosto="esimerkit/kide/portti_cm3.c" osa="tarkistus"}
```

Esimerkki näyttää molemmat ryhmät. Kriittisen osion aikana laukaistu
prioriteetin 2 keskeytys ajetaan heti, mutta prioriteetin 6 keskeytys
odottaa osion loppuun. Lopuksi prioriteetin 2 käsittelijä kutsuu
ydintä, ja väite pysäyttää ohjelman.

```{.c tiedosto="esimerkit/07-basepri/main.c" osa="kasittelijat"}
```

```{.c tiedosto="esimerkit/07-basepri/main.c" osa="tehtava"}
```

```{.tuloste tiedosto="esimerkit/testit/07-basepri.odotettu"}
```

Ilman tarkistusta virhe olisi pahimmanlaatuinen: ohjelma toimisi
lähes aina, ja harvoin, kun keskeytys osuu juuri kriittiseen osioon,
lista menisi rikki ja laite kaatuisi kaukana virheen paikasta.

Kaksi yksityiskohtaa aiheuttaa usein ongelmia. **Prioriteettibittien
määrä**: Cortex-M3-piirit toteuttavat 3–8 bittiä, ja arvot ovat
8-bittisen kentän yläbiteissä. `configMAX_SYSCALL_INTERRUPT_PRIORITY`
on kentän arvo (Kidessä `5 << 5` = `0xA0`), ei prioriteetin numero.
**Oletusprioriteetti** on 0 eli kiireellisin. Keskeytys, jonka
prioriteettia ei ole asetettu, kuuluu siis ryhmään, joka ei saa kutsua
ydintä. Siksi jokaisen ytimen kanssa toimivan keskeytyksen prioriteetti
on asetettava itse.

## Käytännössä

- **Tee käsittelijästä lyhyt.** Kuittaa, lue välttämätön data ja
  herätä tehtävä. Raskas työ tehtävään.
- **Kutsu aina `portYIELD_FROM_ISR`.** Ilman sitä herätetty tehtävä
  odottaa seuraavaan tikkiin.
- **Käytä keskeytyksissä vain FromISR-funktioita** ja vain
  keskeytyksissä, joiden prioriteetti on enintään
  `configMAX_SYSCALL_INTERRUPT_PRIORITY`. Ota `configASSERT` käyttöön
  kehitysvaiheessa, niin tarkistus tehdään.
- **Aseta jokaisen keskeytyksen prioriteetti.** Oletus 0 on väärä
  kaikille ytimen kanssa toimiville keskeytyksille.
- **Varaa nopeimmat keskeytykset ytimen ohi.** Jos käsittelijän viive
  on kriittinen (mikrosekunteja), anna sille kiireellisempi prioriteetti
  ja välitä tulokset tehtäville esimerkiksi rengaspuskurin ja
  ohjelmallisesti laukaistun heikomman keskeytyksen kautta.

## Itsearviointi

- Osaat kertoa, miten FromISR-funktiot eroavat tavallisista ja miksi.
- Osaat toteuttaa viivästetyn keskeytyskäsittelyn semaforilla tai
  ilmoituksella ja selittää `portYIELD_FROM_ISR`:n merkityksen.
- Osaat selittää, mitkä keskeytykset BASEPRI peittää ja mitkä saavat
  kutsua ydintä.
- Osaat asettaa NVIC-prioriteetin oikein suhteessa arvoon
  `configMAX_SYSCALL_INTERRUPT_PRIORITY`.
