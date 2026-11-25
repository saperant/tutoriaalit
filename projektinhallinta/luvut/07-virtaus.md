# Virtaus

Virtaus tarkoittaa työn kulkua ideasta käyttöön. Kun katsotaan työtä
eikä tekijöitä, huomataan, että suurimman osan ajasta työ odottaa:
jonossa, katselmointia, testiympäristöä tai päätöstä. Tässä luvussa
määritellään virtauksen mittarit ja näytetään simuloimalla kolme
ilmiötä, joihin virtauksen ohjaaminen perustuu: keskeneräisen työn
rajoittaminen lyhentää läpimenoaikaa, korkea kuormitusaste pidentää
jonoja jyrkästi ja koko ketjun läpäisyn määrää sen kapein kohta.

## Mittarit

| Mittari | Määritelmä | Yksikkö |
|----------------------|----------------------------------------------|----------------|
| läpimenoaika (*lead time*) | tilauksesta valmiiksi, asiakkaan näkemä aika | päivää |
| kiertoaika (*cycle time*) | aloituksesta valmiiksi, tiimin näkemä aika | päivää |
| läpäisy (*throughput*) | valmistuneita töitä aikayksikössä | työtä/viikko |
| keskeneräinen työ (WIP) | aloitetut mutta ei valmiit työt | työtä |
| työn ikä | kuinka kauan keskeneräinen työ on ollut auki | päivää |
| virtaustehokkuus | työstetty aika jaettuna läpimenoajalla | prosenttia |

Termit läpimenoaika ja kiertoaika määritellään eri lähteissä eri
tavoin, joten tiimin on sovittava, mistä kello alkaa ja mihin se
päättyy. Olennaista on mitata koko matka, jonka asiakas odottaa.

Kolmea mittaria sitoo **Littlen laki**. Vakaassa järjestelmässä pätee
keskiarvoille

$$\text{kiertoaika} = \frac{\text{keskeneräinen työ}}{\text{läpäisy}}$$

Jos tiimillä on kesken 12 työtä ja valmista tulee neljä viikossa, työ
viipyy keskimäärin kolme viikkoa. Kaava kertoo myös, mistä kiertoaika
lyhenee: läpäisyä kasvattamalla, mikä on vaikeaa, tai keskeneräistä
työtä vähentämällä, mikä on päätös. Laki on jonoteorian perustulos
(John Little 1961), ja sitä käytetään samassa muodossa taidoissa
*Arkkitehtuurin mallinnus ja suunnittelutilan tutkiminen* ja
*Skaalautuvien järjestelmien suunnittelu* palvelupyynnöille.

## Keskeneräisen työn raja

Simulaattorissa `virtaus.py` on neljän hengen tiimi. Töitä saapuu
satunnaisesti keskimäärin 0,7 päivässä, ja keskimääräinen työ vaatii
neljä henkilötyöpäivää, joten tiimin kuormitus on 70 %. Tiimi jakaa
aikansa tasan keskeneräisten töiden kesken.

Mallin ratkaiseva oletus on, että samanaikaiset työt maksavat. Kun
tekijällä on useampi työ kesken, osa ajasta kuluu vaihtamiseen:
asiayhteyden palauttamiseen, haarojen yhdistämiseen ja kysymyksiin
vastaamiseen. Gerald Weinbergin tunnettu nyrkkisääntö on, että jokainen
rinnakkainen työ vie noin viidenneksen ajasta. Mallissa häviö on 15 %
jokaista lisätyötä kohden, ja se on rajattu enintään neljännekseen
tiimin tehosta.

```{.python tiedosto="esimerkit/virtaus.py" osa="teho"}
```

Simulaation ydin on silmukka, jossa työt saapuvat jonoon, tiimi vetää
jonosta uuden työn aina kun raja sallii ja keskeneräiset etenevät:

```{.python tiedosto="esimerkit/virtaus.py" osa="simulointi"}
```

Töistä kirjataan saapumis-, aloitus- ja valmistumishetki, joista
mittarit lasketaan:

```{.python tiedosto="esimerkit/virtaus.py" osa="tietomalli"}
```

```{.tuloste tiedosto="esimerkit/virtaus.odotettu"}
```

Ajetaan sama työvirta kuudella eri rajalla:

```{.python tiedosto="esimerkit/07-wip.py" osa="mittarit"}
```

```{.tuloste tiedosto="esimerkit/07-wip.odotettu"}
```

Tulos on luvun tärkein taulukko:

- **Läpäisy on sama rajoilla 4–12 ja ilman rajaa**, 3,5 työtä viikossa.
  Tiimi tekee kaiken, mitä saapuu. Raja ei siis tässä mallissa lisää
  valmistuvan työn määrää.
- **Läpimenoaika kolminkertaistuu, kun raja poistetaan**: 5,8 päivästä
  16,1 päivään. Ilman rajaa jokainen saapuva työ aloitetaan heti,
  kesken on keskimäärin 11 työtä ja jokainen niistä etenee hitaasti.
  Asiakas odottaa pidempään, vaikka työ ”aloitettiin heti”.
- **Ennustettavuus paranee.** 85 %:n persentiili on rajalla 4 alle
  kymmenen päivää, ilman rajaa lähes 30.
- **Liian tiukka raja on haitallinen.** Rajalla 2 kaksi neljästä
  tekijästä on jouten, läpäisy putoaa ja jono kasvaa rajatta. Raja ei
  ole sitä parempi, mitä pienempi se on.
- **Littlen laki pätee** jokaisella rivillä: läpäisy kertaa kiertoaika
  jaettuna keskeneräisten määrällä on noin yksi.

Mekanismi on arkinen. Kun raja estää aloittamasta uutta, ainoa tapa
edetä on saada jotain valmiiksi. Kanban-yhteisön iskulause on *lopeta
aloittaminen, aloita lopettaminen*.

## Kumulatiivinen virtauskaavio

**Kumulatiivinen virtauskaavio** näyttää kertymät päivittäin: montako
työtä on saapunut, aloitettu ja valmistunut. Käyrien pystysuora väli on
kyseisessä tilassa olevien töiden määrä ja vaakasuora väli aika, jonka
työ siinä viipyy.

![Kumulatiivinen virtauskaavio samasta työvirrasta rajalla 4 ja ilman
rajaa. Rajan kanssa työ odottaa jonossa (harmaa) ja keskeneräisten
kaista pysyy kapeana; ilman rajaa kaikki on työn alla ja kaista on
leveä.](kuvat/cfd.png){width=88%}

Kaaviosta luetaan kolme asiaa. Levenevä kaista kertoo, että vaiheeseen
tulee työtä nopeammin kuin siitä lähtee: siinä on pullonkaula.
Valmiiden käyrän kulmakerroin on läpäisy. Jos saapuneiden käyrä nousee
jyrkemmin kuin valmiiden, jono kasvaa eikä projekti valmistu koskaan
nykyisellä tahdilla.

Yksittäisten töiden läpimenoajat kannattaa piirtää hajontakuvioksi ja
merkitä siihen persentiilit. Kuvio näyttää hajonnan, jonka keskiarvo
piilottaa, ja antaa suoraan palvelulupauksen: ”85 % töistä valmistuu
yhdeksässä päivässä”. Daniel Vacanti käsittelee näitä kuvioita ja
niihin perustuvaa ennustamista laajasti.

![Läpimenoaikojen hajontakuvio rajalla 4. Jokainen piste on yksi työ;
vaakaviivat ovat persentiilit.](kuvat/lapimeno.png){width=62%}

## Kuormitusaste ja jonot

Yleinen tavoite on pitää kaikki koko ajan työllistettyinä. Jonoteoria
kertoo, mitä se maksaa. Kun töitä saapuu satunnaisesti ja niiden kesto
vaihtelee, yhden tekijän jonossa keskimääräinen läpimenoaika on

$$\text{läpimenoaika} = \frac{\text{työn kesto}}{1 - \text{kuormitusaste}}$$

Kaava koskee yksinkertaisinta jonomallia (M/M/1), jossa saapumisvälit
ja kestot ovat eksponenttijakautuneita. Simuloidaan jono ja verrataan:

```{.python tiedosto="esimerkit/07-jono.py" osa="jono"}
```

```{.tuloste tiedosto="esimerkit/07-jono.odotettu"}
```

![Läpimenoaika kuormitusasteen funktiona. Käyrä on jonoteorian kaava ja
pisteet simuloituja.](kuvat/kuormitus.png){width=60%}

Kun kuormitus on 50 %, työ kestää jonoineen kaksi kertaa oman
kestonsa. 80 %:n kuormalla kerroin on viisi ja 95 %:n kuormalla
kaksikymmentä: työ odottaa 95 % ajasta. Käyrä on jyrkkä juuri sillä
alueella, jota pidetään tehokkaana.

Tämä on Reinertsenin kirjan keskeinen väite: tuotekehityksessä
kapasiteetin täysi käyttö on kallista, koska jonot ovat näkymättömiä ja
viivästymisen hinta suuri. Tehtaassa kone seisoo näkyvästi, mutta
jonossa odottava vaatimus ei näy missään. Tarkat luvut riippuvat
vaihtelun määrästä. Jos työt ovat tasakokoisia ja saapuvat tasaisesti,
jonoa ei synny suurellakaan kuormalla. Siksi töiden pilkkominen
samankokoisiksi ja tasainen syöttö parantavat virtausta ilman lisäväkeä.

Sama pätee jaettuihin resursseihin. Tietokanta-asiantuntija,
tietoturvakatselmoija tai testiympäristö, jonka kalenteri on täynnä, on
jono, jonka läpi kaikkien työ kulkee.

## Pullonkaula

Työ kulkee yleensä useamman vaiheen läpi. Eliyahu Goldrattin
**rajoitteiden teoria** lähtee havainnosta, että ketjun läpäisy on sen
hitaimman vaiheen läpäisy. Parannus missä tahansa muualla ei lisää
valmista työtä vaan ainoastaan keskeneräistä.

Mallinnetaan kolmivaiheinen linja: kehitys tuottaa keskimäärin viisi
työtä päivässä, katselmointi ehtii kolme ja testaus neljä.

```{.python tiedosto="esimerkit/07-pullonkaula.py" osa="linja"}
```

```{.tuloste tiedosto="esimerkit/07-pullonkaula.odotettu"}
```

Viisi vaihtoehtoa näyttävät teorian askeleet:

1. **Lähtötilanne.** Läpäisy on kolme päivässä eli katselmoinnin tahti.
   Kehitys on täydessä työssä, ja katselmointijonossa on satoja töitä.
2. **Lisää kehittäjiä.** Läpäisy ei muutu lainkaan. Jono kasvaa
   kaksinkertaiseksi ja kiertoaika pitenee, koska sama katselmoija
   käsittelee yhä pidempää jonoa.
3. **Lisää katselmoija.** Läpäisy nousee lähes neljään, jolloin
   seuraava rajoite on testaus. Pullonkaula siirtyy, ei katoa.
4. **Jonoraja.** Kun kehitys ei saa aloittaa uutta katselmointijonon
   ollessa täynnä, läpäisy pysyy kolmessa mutta kiertoaika putoaa
   viidestäkymmenestä päivästä kahteen. Hinta on, että kehitys on
   jouten 41 % ajasta.
5. **Jonoraja ja apu.** Kun jouten jäävät kehittäjät katselmoivat,
   vaikka hitaammin kuin varsinaiset katselmoijat, läpäisy nousee
   3,5:een ilman lisäväkeä.

Goldratt kuvaa saman viitenä askeleena: tunnista rajoite, käytä se
täysin hyödyksi, alista muu sen tahtiin, laajenna rajoitetta ja aloita
alusta, kun rajoite siirtyy. Neljäs vaihtoehto on ”alista” ja viides
”käytä hyödyksi”. Ohjelmistotyössä tyypillisiä pullonkauloja ovat
katselmointi, käsin tehtävä testaus, julkaisuluvat ja yksittäinen
asiantuntija.

Mallissa kehittäjät ja katselmoijat ovat eri ihmisiä, mikä kärjistää
tilannetta. Monialaisessa tiimissä pullonkaula on lievempi, koska
ihmiset voivat siirtyä sinne, missä jono on. Juuri siksi ketterät
menetelmät suosivat tiimejä, joissa kaikki tarvittava osaaminen on
tiimin sisällä.

## Erän koko ja julkaisutiheys

Luvussa 3 erän koko liittyi palautteeseen. Sillä on myös suora
vaikutus läpimenoaikaan. Jos valmis työ julkaistaan kerran kuukaudessa,
jokainen työ odottaa julkaisua keskimäärin kaksi viikkoa riippumatta
siitä, kuinka nopeasti se tehtiin. Viikoittainen julkaisu pudottaa
odotuksen kahteen ja puoleen arkipäivään. Suuri erä on myös riskialtis:
kun julkaisussa on sata muutosta ja jokin hajoaa, syyllisen etsiminen
on hidasta.

Toimituskyvyn mittaaminen ja julkaisun automatisointi kuuluvat taitoon
*Jatkuva integraatio ja toimitus*. Sen tunnetuimmat mittarit (julkaisutiheys,
muutoksen läpimenoaika, epäonnistuneiden muutosten osuus ja palautumisaika)
ovat virtausmittareita toimitusputkelle; ne ovat peräisin Forsgrenin,
Humblen ja Kimin tutkimuksesta.

## Käytännössä

- **Mittaa työn odotusaika, ei ihmisten kiirettä.** Kysy, kuinka kauan
  työ viipyy, älä kuinka täynnä kalenterit ovat. Tietotyössä työ
  odottaa suurimman osan ajasta.
- **Aseta WIP-raja ja säädä sitä.** Aloita yhdestä työstä henkeä
  kohden. Jos ihmisiä on jouten, raja on liian tiukka; jos mikään ei
  valmistu, liian löysä.
- **Seuraa työn ikää päivittäin.** Työ, joka on ollut auki kauemmin
  kuin 85 % töistä yleensä, tarvitsee huomiota nyt eikä retrospektiivissä.
- **Jätä varaa.** Tiimi, jonka suunnitelma täyttää 100 % kapasiteetista,
  toimii jonokäyrän jyrkällä osalla, ja yllätykset tulevat silti.
- **Etsi pullonkaula ennen kuin lisäät väkeä.** Katso
  virtauskaaviosta, minkä vaiheen eteen työ kertyy, ja vahvista sitä.
- **Auta jonoa, älä aloita uutta.** Kun oma vaihe on tyhjä, hyödyllisin
  työ on usein toisen vaiheen jonossa.
- **Varo mittareiden pelaamista.** Läpäisy nousee pilkkomalla työt
  keinotekoisesti ja läpimenoaika lyhenee aloittamalla kello
  myöhemmin. Mittarit ovat tiimin työkalu.

## Itsearviointi

- Osaat määritellä läpimenoajan, kiertoajan, läpäisyn ja keskeneräisen
  työn ja laskea yhden Littlen lailla kahdesta muusta.
- Osaat selittää, miksi keskeneräisen työn raja lyhentää läpimenoaikaa,
  vaikka läpäisy ei kasva, ja miksi liian tiukka raja on haitallinen.
- Osaat lukea kumulatiivista virtauskaaviota ja läpimenoaikojen
  hajontakuviota.
- Osaat perustella kuormitusasteen avulla, miksi täysi käyttöaste ei
  ole tavoite.
- Osaat tunnistaa pullonkaulan ja selittää, miksi muun vaiheen
  tehostaminen ei lisää läpäisyä.
