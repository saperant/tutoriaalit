# Mutexit ja prioriteetin inversio

Yhteinen resurssi, kuten SPI-väylä, näyttö tai globaali rakenne, on
suojattava niin, että vain yksi tehtävä käyttää sitä kerrallaan.
Taidossa *Käyttöjärjestelmät* tähän käytettiin mutexia. Mutex ja
binäärisemafori näyttävät samalta: kumpikin on joko vapaa tai varattu.
Erot ovat kuitenkin olennaisia, ja niistä tärkein liittyy
prioriteetteihin.

| Ominaisuus | Binäärisemafori | Mutex |
|------------|-----------------|-------|
| omistaja | ei | varaaja |
| kuka antaa | kuka tahansa, myös keskeytys | vain haltija |
| alkutila | tyhjä | vapaa |
| prioriteetin periytys | ei | kyllä |
| keskeytyksessä | antaa saa | ei |

## Prioriteetin inversio

Prioriteetin inversio syntyy, kun tärkeä tehtävä odottaa vähemmän
tärkeää. Pieni inversio on väistämätön: jos matala tehtävä pitää
väylää ja korkea tarvitsee sitä, korkean on odotettava, että matala
saa siirtonsa valmiiksi. Odotus on kuitenkin rajattu, koska siirto on
lyhyt. Ongelma syntyy, kun mukaan tulee keskitason tehtävä, joka ei
tarvitse väylää lainkaan. Se keskeyttää matalan, ja korkea odottaa nyt
myös keskitasoa, jonka työ voi olla kuinka pitkä tahansa. Inversio on
rajaton.

Tunnetuin tapaus on Mars Pathfinder vuonna 1997. Laskeutujan
tietokone käynnistyi toistuvasti uudelleen, koska korkean prioriteetin
väylänhallintatehtävä odotti mutexia, jota matalan prioriteetin
säädatan keruutehtävä piti, ja keskitason viestintätehtävät estivät
keruutehtävää ajamasta. Ajastin huomasi, ettei väylänhallinta ollut
valmistunut ajoissa, ja käynnisti järjestelmän uudelleen. VxWorksin
mutexissa oli prioriteetin periytys, mutta se oli pois päältä.
Insinöörit kytkivät sen päälle maasta käsin.

## Esimerkki

Kolme tehtävää: matala varaa väylän ja siirtää dataa neljä tikkiä,
korkea tarvitsee väylää hetkellä 1, ja keskitaso laskee kuusi tikkiä
hetkestä 2 alkaen. Perusversio suojaa väylän binäärisemaforilla,
muunnelma mutexilla.

```{.c tiedosto="esimerkit/13-inversio/main.c" osa="tehtavat"}
```

```{.c tiedosto="esimerkit/13-inversio/main.c" osa="luonti"}
```

Binäärisemaforilla:

```{.tuloste tiedosto="esimerkit/testit/13-inversio.odotettu"}
```

Mutexilla:

```{.tuloste tiedosto="esimerkit/testit/13-inversio-mutex.odotettu"}
```

Semaforilla korkea odottaa yhdeksän tikkiä, joista kuusi on
keskitason laskentaa. Mutexilla matala perii korkean prioriteetin 3
sillä hetkellä, kun korkea jää odottamaan. Keskitaso herää hetkellä 2
mutta ei pääse ajoon, koska matala on nyt sitä tärkeämpi. Matala
vapauttaa väylän hetkellä 4, palaa prioriteettiin 1, ja korkea saa
väylän. Korkean odotus on enää matalan jäljellä oleva siirtoaika.
Keskitaso valmistuu myöhemmin kuin semaforiversiossa, mikä on juuri
tarkoitus: tärkeämpi työ menee ensin.

## Periytyksen toteutus

Kun tehtävä jää odottamaan mutexia, jonka haltija on vähemmän tärkeä,
haltijan prioriteetti nostetaan odottajan tasolle. Haltija siirretään
uuden prioriteetin valmislistaan, ja jos se itse odottaa jossakin, sen
paikka odotuslistassa korjataan. Kun haltija vapauttaa viimeisen
mutexinsa, sen prioriteetti palautetaan perusarvoon.

```{.c tiedosto="esimerkit/kide/tehtava.c" osa="periytys"}
```

```{.c tiedosto="esimerkit/kide/jono.c" osa="anna"}
```

Kiden toteutus on tarkoituksella yksinkertainen. Siitä puuttuu kolme
asiaa, jotka FreeRTOSissa on:

- **Ketjuttuva periytys.** Jos haltija itse odottaa toista mutexia,
  myös sen haltijan prioriteetti pitäisi nostaa. Kide ei tee sitä, ja
  monet ytimet toteuttavat ketjun vain osittain. Sisäkkäisiä mutexeja
  kannattaa siksi välttää.
- **Periytyksen purku aikarajan jälkeen.** Jos korkea luopuu
  odotuksesta aikarajan vuoksi, haltija pitää perimänsä prioriteetin
  vapautukseen asti. FreeRTOS laskee sen takaisin
  (`vTaskPriorityDisinheritAfterTimeout`).
- **Useiden mutexien tarkka kirjanpito.** Kide palauttaa
  perusprioriteetin vasta, kun kaikki mutexit on vapautettu, vaikka
  osa perityistä prioriteeteista olisi jo tarpeettomia. FreeRTOS tekee
  samoin.

## Prioriteettikatto

Periytyksen vaihtoehto on *prioriteettikatto* (*priority ceiling*):
mutexille annetaan kiinteä prioriteetti, joka on sen tärkeimmän
käyttäjän prioriteetti, ja varaaja nostetaan siihen heti varattaessa.
Inversio rajoittuu silloin yhteen kriittiseen osioon, ja
yksiprosessorijärjestelmässä menetelmä estää myös mutexien välisen
lukkiutumisen, koska kukaan muu mutexin käyttäjä ei pääse ajoon
haltijan aikana. Hinta on, että
prioriteetti nousee joka varauksella, myös silloin, kun kukaan ei
odota. Katto on käytössä OSEK/AUTOSAR-käyttöjärjestelmissä ja Adan
Ravenscar-profiilissa. FreeRTOSissa sitä ei ole, mutta sen voi
toteuttaa nostamalla prioriteetin itse.

## Lukkiutuminen ja aikarajat

Mutexit tuovat mukanaan lukkiutumisen. Sen syyt ja ehkäisy (Coffmanin
ehdot, lukkojärjestys) käsiteltiin taidossa *Käyttöjärjestelmät*.
Sulautetussa järjestelmässä kaksi käytäntöä on erityisen hyödyllistä:

- **Kiinteä lukkojärjestys.** Jos tehtävä tarvitsee kaksi mutexia, se
  varaa ne aina samassa järjestyksessä.
- **Aikaraja ja virhe.** `xSemaphoreTake(mutex, pdMS_TO_TICKS(50))`
  ja virheilmoitus aikarajan täyttyessä tekevät lukkiutumisesta
  näkyvän ja diagnosoitavan. Ikuinen odotus tekee siitä laitteen, joka
  vain lakkaa toimimasta.

## Käytännössä

- **Suojaa yhteinen resurssi mutexilla, älä semaforilla.** Vain
  mutexilla on omistaja ja prioriteetin periytys.
- **Pidä kriittinen alue lyhyenä.** Periytys rajoittaa inversion
  haltijan jäljellä olevaan aikaan, joten haltijan työ on mitoitettava.
  Pitkä siirto kannattaa tehdä DMA:lla ja odottaa sen valmistumista
  ilman mutexia.
- **Älä käytä mutexia keskeytyksessä.** Keskeytyksellä ei ole
  prioriteettia, jonka haltija voisi periä, eikä se voi jäädä
  odottamaan.
- **Harkitse vartijatehtävää** (*gatekeeper*). Kun resurssilla on yksi
  omistajatehtävä, jolle muut lähettävät pyynnöt jonossa, mutexia ei
  tarvita lainkaan, ja inversio näkyy jonon odotusaikana.
- **Analysoi inversio.** Ajoitusanalyysissä (luku 9) tehtävän
  vasteaikaan lisätään pisin aika, jonka vähemmän tärkeä tehtävä voi
  pitää sen tarvitsemaa mutexia (*blocking time*).

## Itsearviointi

- Osaat selittää mutexin ja binäärisemaforin erot ja sen, miksi
  semafori ei sovi resurssin suojaksi.
- Osaat kuvata rajattoman prioriteetin inversion aikajanana ja kertoa
  Mars Pathfinderin tapauksen pääpiirteet.
- Osaat selittää prioriteetin periytyksen toteutuksen ja sen
  rajoitukset.
- Osaat verrata prioriteetin periytystä ja prioriteettikattoa.
- Osaat ehkäistä lukkiutumista lukkojärjestyksellä ja aikarajoilla.
