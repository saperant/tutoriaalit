# Ajallinen irrottaminen ja DMI

Luvun 7 aloittaja odotti jokaisen transaktion jälkeen. Jokainen `wait()`
on kontekstinvaihto simulaattorin ja säikeen välillä, ja
prosessorimallissa, joka tekee jokaisella käskyllä vähintään käskynhaun,
kontekstinvaihdot vievät suurimman osan ajasta. LT-tyylin kaksi
nopeuskeinoa poistavat niitä: *ajallinen irrottaminen* (*temporal
decoupling*) antaa aloittajan kulkea simulaatioajan edellä ja synkronoida
vain välillä, ja *suora muistiväylä* (*direct memory interface*, DMI)
ohittaa väylän kokonaan muistin luvuissa.

## Paikallinen aika ja kvantti

Ajallisesti irrotettu aloittaja pitää kirjaa *paikallisesta ajastaan*:
kuinka paljon se on edellä simulaatioaikaa. Se välittää paikallisen
ajan `b_transport`ille viiveargumenttina, joten kohde näkee, mihin
hetkeen pyyntö oikeasti kuuluu. Aloittaja synkronoi, eli odottaa
paikallisen aikansa ja nollaa sen, kun paikallinen aika ylittää
*kvantin* (*quantum*). Kvantti on koko mallin yhteinen asetus.

Apuluokka `tlm_utils::tlm_quantumkeeper` hoitaa kirjanpidon:

| Funktio | Merkitys |
|---------|----------|
| `set_global_quantum(t)` | koko mallin kvantti (staattinen) |
| `reset()` | paikallinen aika nollaan, seuraava synkronointihetki |
| `inc(t)` | lisää paikalliseen aikaan |
| `get_local_time()`, `set(t)` | paikallinen aika viiveargumentiksi ja takaisin |
| `get_current_time()` | simulaatioaika + paikallinen aika |
| `need_sync()` | onko kvantti täynnä |
| `sync()` | `wait(paikallinen aika)` ja nollaus |

## Kaksi aloittajaa, yksi muistipaikka

Esimerkissä tuottaja kirjoittaa viestin numeron muistiin 200 ns:n
laskennan välein, ja kuluttaja kyselee samaa muistipaikkaa 50 ns:n
välein. Kumpikin on ajallisesti irrotettu:

```{.cpp tiedosto="esimerkit/11-kvantti/main.cpp" osa="tuottaja"}
```

Siirto tehdään apufunktiolla `siirra` (`mallit/siirto.hpp`), joka
täyttää payloadin kuten luvun 7 aloittaja ja raportoi virheen, mutta ei
odota. Kuluttaja mittaa, kuinka paljon myöhemmin (omassa ajassaan) se näkee
kunkin viestin, ja vertaa samalla kahden ajastimen lukemia:

```{.cpp tiedosto="esimerkit/11-kvantti/main.cpp" osa="kuluttaja"}
```

```{.cpp tiedosto="esimerkit/11-kvantti/main.cpp" osa="main"}
```

Skripti ajaa mallin neljällä kvantilla:

```{.bash tiedosto="esimerkit/11-kvantti/aja.sh"}
```

```{.tuloste tiedosto="esimerkit/11-kvantti/odotettu"}
```

![Aloittajien oma aika simulaatioajan funktiona. Lävistäjällä
aloittaja on synkronissa; pystysuora nousu on kulkua simulaatioajan
edellä ja vaakasuora siirtymä synkronointi. Nollakvantilla jokainen
siirto tehdään lävistäjällä. Mikrosekunnin kvantilla kumpikin aloittaja
tekee koko kvantin siirrot samalla simulaatiohetkellä, tuottaja ensin:
kuluttajan ensimmäinen kysely (oma aika 50 ns) näkee jo viestin, jonka
tuottaja lähetti omassa ajassaan vasta 830 ns:n
kohdalla.](kuvat/kvantti.png){width=100%}

Kuva on piirretty esimerkin omasta jäljestä: funktion `jalki` kutsut
tuottajassa ja kuluttajassa tulostavat jokaisen siirron ajat, kun
ohjelmalle annetaan toinen argumentti (`make kuvat`). Tulos kertoo
ajallisen irrottamisen hinnan ja hyödyn:

- **Nolla kvantti** synkronoi ennen jokaista siirtoa. Kuluttaja näkee
  jokaisen viestin 0–70 ns sen jälkeen, kun se lähetettiin: viive johtuu
  vain kyselyvälistä. Kontekstinvaihtoja on 73.
- **100 ns** vähentää kontekstinvaihtoja vain vähän (62), koska yksi
  kuluttajan kierros kestää jo 80 ns. Havaintoviive kasvaa 150 ns:iin,
  ja naiivi ajastin jää 9 jaksoa jälkeen.
- **1 µs** vähentää kontekstinvaihdot yhdeksään, mutta kuluttaja näkee
  enää 5 viestiä 20:stä: tuottaja ehtii kirjoittaa saman muistipaikan
  monta kertaa ennen kuin kuluttaja saa vuoron. Yksi viesti näkyy
  kuluttajan omassa ajassa *ennen* kuin se lähetettiin: syy ja seuraus
  ovat vaihtaneet paikkaa. Lisäksi kuluttaja kyselee pidempään, koska se
  odottaa viimeistä viestiä, joten simulointi päättyy myöhemmin.
- **10 µs** on pidempi kuin koko ajo. Tuottaja ajaa kaiken ilman yhtään
  synkronointia, ja kuluttaja näkee vain viimeisen viestin.

Naiivi ajastin käyttää pelkkää simulaatioaikaa ja jää irrotetun
aloittajan perässä jälkeen jopa 97 jaksoa. Aikatietoinen ajastin laskee
ajan `sc_time_stamp() + viive` ja näyttää aloittajalle oikean ajan
kvantista riippumatta. Tästä seuraa LT-mallinnuksen sääntö: kohde, jonka
vastaus riippuu ajasta, käyttää annotoitua aikaa.

## Milloin synkronoida

Ajallinen irrottaminen on oikein niin kauan kuin aloittaja ei
kommunikoi muiden kanssa. Prosessori, joka laskee omassa
välimuistissaan, voi kulkea mikrosekunteja edellä. Kun se lukee
lippua, jota toinen aloittaja kirjoittaa, tai odottaa keskeytystä,
virhe näkyy. Käytäntöjä on kolme:

1. **Kvantti mitoitetaan sovelluksen mukaan.** Tyypillinen kvantti on
   satoja nanosekunteja tai muutama mikrosekunti: tarpeeksi pitkä, että
   kontekstinvaihtoja on vähän, ja tarpeeksi lyhyt, että ohjelmiston
   aikarajat ja keskeytysviiveet pysyvät järkevinä.
2. **Synkronoi ennen jaettua tilaa.** Aloittaja synkronoi heti, kun se
   lukee tai kirjoittaa jotain, jota muut käyttävät kommunikointiin:
   jaettua muistia, oheislaitteen tilarekisteriä tai synkronointiprimitiiviä.
   Kohde voi myös pyytää synkronointia vastaamalla viiveellä, joka
   pakottaa aloittajan odottamaan.
3. **Odotussilmukat.** Ohjelmiston kyselysilmukka (*polling loop*) on
   pahin tapaus: se pyörii kvantin loppuun näkemättä muutosta.
   Prosessorimallit tunnistavat odotuskäskyn (`wfi`, `wfe`) tai
   silmukan ja synkronoivat heti.

Luku 12 mittaa nämä keskeytyksillä: kuinka paljon kvantti viivästää
keskeytystä, milloin tikkejä katoaa ja mitä `wfi` muuttaa.

## DMI: suora muistiväylä

Jokainen `b_transport` kulkee väylän dekooderin läpi. Muistille se on
turhaa: data on vain tavutaulukossa, ja aloittaja voisi lukea sen
suoraan. DMI antaa aloittajalle osoittimen kohteen muistiin, osoitealueen
ja viiveet, jotka aloittajan pitää itse lisätä aikaansa.

Kohde kertoo DMI:n mahdollisuudesta vihjeellä `set_dmi_allowed(true)`
(luku 7), ja aloittaja pyytää osoittimen `get_direct_mem_ptr`-kutsulla:

```{.cpp tiedosto="esimerkit/mallit/muisti.hpp" osa="dmi"}
```

Väylän on muunnettava kohteen antama alue aloittajan osoitteiksi ja
lisättävä omat viiveensä, ja mitätöinnit kulkevat samaa reittiä
takaisin:

```{.cpp tiedosto="esimerkit/mallit/vayla.hpp" osa="dmi"}
```

Lukija käyttää osoitinta, jos osoite on voimassa olevan alueen sisällä,
ja muuten tavallista transaktiota:

```{.cpp tiedosto="esimerkit/12-dmi/main.cpp" osa="lukija"}
```

DMI-osoitin voi vanhentua: muistikartta muuttuu, muisti vaihdetaan
toiseen tai kohde haluaa taas nähdä jokaisen siirron (esimerkiksi
debuggerin vahtipisteen vuoksi). Silloin kohde kutsuu
`invalidate_direct_mem_ptr`ia, ja jokainen aloittaja, jonka osoitin osuu
alueelle, lakkaa käyttämästä sitä:

```{.cpp tiedosto="esimerkit/mallit/muisti.hpp" osa="mitatoi"}
```

Esimerkissä kaksi lukijaa laskee saman muistin summan kahdesti
1 µs:n kvantilla, toinen ilman DMI:tä ja toinen sen kanssa. Kolmas
aloittaja, hallinta, täyttää muistin ensin debug-kirjoituksilla ja
kutsuu 30 µs:n kohdalla muistin funktiota `mitatoi_dmi()`:

```{.cpp tiedosto="esimerkit/12-dmi/main.cpp" osa="main"}
```

```{.tuloste tiedosto="esimerkit/12-dmi/odotettu"}
```

Molemmat lukijat saavat saman summan ja päättyvät samalla
simulaatiohetkellä, koska DMI:n viiveet vastaavat väylän ja muistin
viiveitä. DMI-lukija tekee kuitenkin vain kaksi transaktiota 2048:n
sijaan: ensimmäisen, josta se saa vihjeen ja osoittimen, ja toisen
mitätöinnin jälkeen, jolloin se pyytää uuden osoittimen. Muut luvut ovat
pelkkiä `memcpy`-kutsuja. Todellisessa virtuaaliprototyypissä tämä
nopeuttaa käskynhakua kertaluokalla tai enemmän.

## Käytännössä

- **Kvantti on parametri, ei vakio.** Virtuaaliprototyypin käyttäjä
  valitsee kvantin tehtävän mukaan: ohjelmiston käynnistykseen suuri,
  ajurin ajoitusvirheen etsimiseen pieni. Tuloksen ei pidä muuttua
  kvantin mukana; jos muuttuu, malli tai ohjelmisto riippuu ajoituksesta,
  jota se ei saa olettaa.
- **Ajasta riippuva kohde käyttää annotoitua aikaa.** Ajastin, joka
  laskee `sc_time_stamp() + viive`, toimii kaikilla kvanteilla.
  Kohde, joka käyttää pelkkää `sc_time_stamp()`ia, toimii vain, kun
  kvantti on nolla.
- **DMI aina kun mahdollista.** Muistit ja muistinkaltaiset kohteet
  tarjoavat DMI:n ja ilmoittavat viiveet. Aloittaja lisää viiveet itse,
  jotta aikataulu ei muutu DMI:n käytöstä.
- **Mitätöinti on velvollisuus.** Kohde, joka antaa osoittimen, mitätöi
  sen aina, kun sen sisältöä ei enää saa käsitellä suoraan. Väylä
  välittää mitätöinnin kaikille aloittajille, ja aloittaja tarkistaa
  osoitealueen ennen jokaista käyttöä.

## Itsearviointi

- Osaat kirjoittaa ajallisesti irrotetun aloittajan
  `tlm_quantumkeeper`illa ja selittää paikallisen ajan, kvantin ja
  synkronoinnin.
- Osaat ennustaa, miten kvantin kasvattaminen vaikuttaa
  kontekstinvaihtojen määrään ja aloittajien välisen viestinnän
  tarkkuuteen.
- Osaat kirjoittaa kohteen, joka toimii oikein irrotetun aloittajan
  kanssa, kun sen vastaus riippuu ajasta.
- Osaat pyytää, käyttää ja mitätöidä DMI-osoittimen ja lisätä DMI:n
  viiveet aloittajan aikaan.
