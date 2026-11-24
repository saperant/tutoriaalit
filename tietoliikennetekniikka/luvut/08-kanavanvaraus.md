# Kanavanvaraus

Kun monta asemaa jakaa saman siirtotien – radiotaajuuden tai vanhan
Ethernetin koaksiaalikaapelin –, on sovittava, kuka saa lähettää.
Kanavanvarausmenetelmät (*medium access control*, MAC) jakautuvat
kahteen ryhmään: **satunnaispääsy**, jossa asemat lähettävät, kun
haluavat, ja selvittävät törmäykset, sekä **hallittu pääsy**, jossa
vuorot jaetaan etukäteen.

## ALOHA

Havaijin yliopiston ALOHAnet (1971) oli ensimmäinen pakettiradioverkko.
Asema lähetti, kun sillä oli dataa, ja jos kuittausta ei tullut, se
yritti satunnaisen ajan kuluttua uudelleen. Kaksi kehystä törmää, jos
ne alkavat alle kehysajan päässä toisistaan, joten kehyksen
haavoittuva aika on kaksi kehysaikaa. Kun aika jaetaan viipaleisiin
ja lähetys sallitaan vain viipaleen alussa (**viipaloitu ALOHA**),
haavoittuva aika puolittuu.

Merkitään kuormaa $G$:llä (yrityksiä kehysaikaa kohti). Onnistuneiden
kehysten osuus on puhtaassa ALOHAssa $S = G e^{-2G}$ ja viipaloidussa
$S = G e^{-G}$:

```{.python tiedosto="esimerkit/08-aloha.py" osa="viipaloitu"}
```

```{.python tiedosto="esimerkit/08-aloha.py" osa="puhdas"}
```

```{.tuloste tiedosto="esimerkit/08-aloha.odotettu"}
```

Simulaatio osuu teoriaan. Paras läpäisy on vain 18 % (puhdas) tai
37 % (viipaloitu) kanavan kapasiteetista, ja liian suuri kuorma romahduttaa
läpäisyn, koska lähes kaikki kehykset törmäävät.

## CSMA/CD ja binäärinen eksponentiaalinen perääntyminen

**CSMA** (*carrier sense multiple access*) parantaa ALOHAa yhdellä
säännöllä: kuuntele ennen kuin lähetät. Jaetun väylän Ethernet lisäsi
**törmäyksen havaitsemisen** (CD): lähettäjä kuuntelee lähettäessään
ja keskeyttää heti, jos joku muu lähettää samaan aikaan. Törmäyksen
jälkeen asema odottaa satunnaisen määrän aikaviipaleita väliltä
$0 \ldots 2^k - 1$, missä $k$ on törmäysten määrä (enintään 10).
Jokainen törmäys kaksinkertaistaa odotusvälin, jolloin asemat
levittäytyvät ajallisesti sitä enemmän, mitä enemmän niitä on:

```{.python tiedosto="esimerkit/08-csma-cd.py" osa="beb"}
```

```{.tuloste tiedosto="esimerkit/08-csma-cd.odotettu"}
```

Kilpailuun kuluva aika kasvaa asemien määrän mukana, mutta
kohtuullisesti: menetelmä mukautuu kuormaan tietämättä, montako
asemaa verkossa on. Nykyinen kytketty Ethernet toimii
täysdupleksina, jolloin törmäyksiä ei ole lainkaan, mutta sama
perääntymisen periaate elää kaikkialla, missä uudelleenyrityksiä
ajastetaan: Wi-Fissä, TCP:n uudelleenlähetyksissä ja
sovellusten uudelleenyrityksissä (taito *Palveluarkkitehtuurit*).

## CSMA/CA langattomassa verkossa

Radiossa asema ei kuule omaa lähetystään vastaanottaessaan, joten
törmäystä ei voi havaita. Lisäksi kaksi asemaa voi kuulla tukiaseman
mutta ei toisiaan (**piilotetun aseman ongelma**). Wi-Fi käyttää siksi
törmäysten välttämistä (CA): asema odottaa kanavan vapautumisen jälkeen
satunnaisen ajan ennen lähetystä, vastaanottaja kuittaa jokaisen
kehyksen, ja pitkille kehyksille voidaan varata kanava ensin lyhyillä
RTS- ja CTS-viesteillä, jotka myös piilotettu asema kuulee
tukiasemalta. Wi-Fi 6 lisäsi päälle OFDMA:n, jolla tukiasema jakaa
vuoroja itse matkaviestinverkkojen tapaan.

## Hallittu pääsy: Token Ring ja TDMA

Hallitussa pääsyssä törmäyksiä ei synny. **Token Ring** kierrätti
asemien renkaassa vuoromerkkiä (*token*); vain merkin haltija sai
lähettää, ja tyhjä asema antoi merkin heti eteenpäin. **TDMA** jakaa
jokaiselle asemalle kiinteän aikavälin, jota käytetään tai ei.
Vertaillaan niitä vaihtelevalla kuormalla:

```{.python tiedosto="esimerkit/08-vuorottelu.py" osa="vuorot"}
```

```{.tuloste tiedosto="esimerkit/08-vuorottelu.odotettu"}
```

Molemmat siirtävät kaiken tarjotun liikenteen, mutta TDMA:n viive on
moninkertainen, koska kehys odottaa oman aikavälinsä, vaikka muiden
välit olisivat tyhjiä. Vuoromerkki ohittaa tyhjät asemat nopeasti.
Hallitun pääsyn etu satunnaispääsyyn nähden on **ennustettavuus**:
pahin viive on rajattu, mikä kelpaa teollisuuden ohjausväylille.
Token Ring hävisi kuitenkin Ethernetille, koska kytketty Ethernet oli
halvempi ja yksinkertaisempi, kun törmäykset katosivat kytkimien myötä.
TDMA elää GSM:ssä, Bluetoothissa ja matkaviestinverkkojen
resurssiruudukossa.

## Käytännössä

- **Satunnaispääsy kevyelle, hallittu raskaalle kuormalle.**
  ALOHA-tyyppinen pääsy on yksinkertainen ja toimii hyvin, kun kuorma
  on pieni (IoT-laitteiden harvat viestit, LoRaWAN). Kuorman kasvaessa
  tarvitaan kuuntelua, perääntymistä tai keskitettyä vuorojakoa.
- **Eksponentiaalinen perääntyminen ja satunnaisuus kuuluvat
  jokaiseen uudelleenyritykseen.** Ilman satunnaisuutta kaikki
  yrittävät yhtä aikaa uudelleen ja törmäävät taas.
- **Wi-Fi on jaettu kanava.** Yksi hidas asema varaa kanavaa pitkään
  ja hidastaa kaikkia; tukiasemien sijoittelu ja kanavasuunnittelu
  (taito *Verkkoinfrastruktuuri*) ratkaisevat kapasiteetin.
- **Deterministisyys maksaa.** Hallittu pääsy takaa viiveen ylärajan
  mutta tuhlaa kapasiteettia tyhjiin vuoroihin; ajastettu Ethernet
  (TSN) tuo samat takuut kytkettyyn verkkoon.

## Itsearviointi

- Osaat johtaa viipaloidun ja puhtaan ALOHAn läpäisyn ja selittää,
  miksi läpäisy romahtaa liian suurella kuormalla.
- Osaat kuvata CSMA/CD:n ja binäärisen eksponentiaalisen
  perääntymisen toiminnan.
- Osaat selittää piilotetun aseman ongelman ja CSMA/CA:n keinot sitä
  vastaan.
- Osaat vertailla TDMA:ta, vuoromerkkiä ja satunnaispääsyä läpäisyn,
  viiveen ja ennustettavuuden kannalta.
