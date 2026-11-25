# Linjakoodaus ja kehystys

Bitit eivät kulje siirtotiellä sellaisinaan. Ne muutetaan
signaalitasoiksi **linjakoodilla**, ja bittivirta jaetaan **kehyksiksi**,
jotta vastaanotin tietää, mistä viesti alkaa ja mihin se loppuu.
Molemmat ratkaisevat ongelman, jota bitti-ajattelussa ei näe:
vastaanottimella ei ole lähettäjän kelloa. Luku etenee kahden tason
koodeista usean tason symboleihin ja kantoaaltomodulaation
periaatteeseen ja päättyy kehystykseen.

## Linjakoodit

Yksinkertaisin koodi, **NRZ** (*non-return-to-zero*), lähettää ykkösen
positiivisena ja nollan negatiivisena tasona. Pitkä samojen bittien jono
on kuitenkin vastaanottimelle tasainen signaali: siitä ei näe, montako
bittiä jonossa on, eikä vastaanottimen kello pysy tahdissa. Lisäksi
tasainen jakso tuottaa tasajännitekomponentin, joka ei kulje
muuntajien ja kondensaattorien läpi.

Linjakoodit ratkaisevat ongelman eri hinnoin:

- **NRZI** vaihtaa tasoa jokaisella ykkösellä. Ykkösjonot tuottavat
  vaihtoja, nollajonot eivät.
- **Manchester** (10 Mbit/s Ethernet) koodaa jokaisen bitin
  tasonvaihtona bitin keskellä. Kello on aina signaalissa, mutta
  signaalin taajuus kaksinkertaistuu.
- **4B5B** (100 Mbit/s Ethernet) korvaa neljän bitin ryhmän viiden
  bitin koodisanalla, jossa ei ole pitkiä nollajonoja, ja lähettää sen
  NRZI:llä. Hinta on 25 %.

![Bittijono 00001101 neljällä linjakoodilla (esimerkin funktioilla
piirrettynä). NRZ ja NRZI pysyvät nollajonon ajan tasaisina.
Manchesterissa on tasonvaihto jokaisen bitin keskellä. 4B5B lähettää
samassa ajassa kymmenen lyhyempää koodibittiä (ylärivi), joissa
ykkösiä on tiheästi.](kuvat/linjakoodit.png){width=85%}

```{.python tiedosto="esimerkit/04-linjakoodit.py" osa="koodit"}
```

```{.python tiedosto="esimerkit/04-linjakoodit.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/04-linjakoodit.odotettu"}
```

NRZ ja NRZI jättävät vastaanottimen ilman tasonvaihtoja 32 bitin
ajaksi. Manchester tuottaa eniten vaihtoja ja nollan tasakomponentin,
mutta tarvitsee kaksi tasoa bittiä kohti. 4B5B pitää vaihtoja tiheästi
25 %:n lisäkustannuksella.

Nopeammissa Ethernet-tyypeissä käytetään tehokkaampia koodeja:
**8b10b** (gigabitin kuitu) valitsee kahdesta koodisanasta sen, joka
pitää ykkösten ja nollien juoksevan erotuksen (*running disparity*)
lähellä nollaa, ja **64b/66b** (10 Gbit/s ja nopeammat) lisää 64 bitin
lohkoon vain kahden bitin otsakkeen ja sekoittaa (*scramble*) datan
niin, että pitkät samanlaisten bittien jonot ovat epätodennäköisiä.
Kustannus on 3 %.

## Useampi bitti symbolissa: PAM4

Kun siirtotien kaista ei riitä nopeampiin symboleihin, symboliin
pakataan useampi bitti. PAM4 (pulssiamplitudimodulaatio neljällä
tasolla) kantaa kaksi bittiä symbolissa, ja sitä käyttävät 50, 100,
200 ja 400 Gbit/s:n Ethernet-yhteydet. Tasot numeroidaan
**Gray-koodilla**, jossa vierekkäiset tasot eroavat vain yhdessä
bitissä:

```{.python tiedosto="esimerkit/04-pam4.py" osa="pam4"}
```

![Esimerkin bittijono PAM4-symboleina. Jokainen symboli kantaa kaksi
bittiä, ja vierekkäisten tasojen bittiparit eroavat yhdellä
bitillä.](kuvat/pam4.png){width=68%}

```{.python tiedosto="esimerkit/04-pam4.py" osa="virhe"}
```

```{.tuloste tiedosto="esimerkit/04-pam4.odotettu"}
```

Symbolinopeus puolittuu bittinopeuteen nähden, mutta tasojen väli
pienenee kolmannekseen, joten sama kohina aiheuttaa enemmän virheitä
(noin 9,5 dB huonompi SNR-vaatimus kuin kahdella tasolla). PAM4-linkit
tarvitsevat siksi aina virheenkorjauksen (FEC).

## Kantoaalto ja konstellaatio

Tähänastiset koodit ovat **kantataajuisia**: signaali on jono
jännitetasoja, ja se sopii kaapeliin. Radiossa, kaapelimodeemissa ja
pitkän matkan kuidussa data siirretään **kantoaallolla**, sinimuotoisella
signaalilla, jonka taajuus määrää, millä kaistalla lähetys kulkee.
Bitit muuttavat kantoaallon amplitudia (ASK), vaihetta (PSK) tai
molempia (QAM, *quadrature amplitude modulation*).

Samantaajuinen kosini ja sini ovat ortogonaaliset, joten ne kantavat
kaksi toisistaan riippumatonta amplitudia. Symboli on siksi piste
tasossa: vaaka-akselilla on kosinikomponentin amplitudi (I) ja
pystyakselilla sinikomponentin (Q). Käytössä olevien pisteiden joukko
on **konstellaatio**. BPSK:ssa pisteitä on kaksi (yksi bitti), QPSK:ssa
neljä (kaksi bittiä), ja $M$-QAM asettaa $M$ pistettä ruudukkoon. Kumpikin
akseli on oma PAM-signaalinsa, ja tasot numeroidaan Gray-koodilla kuten
PAM4:ssä:

```{.python tiedosto="esimerkit/04-konstellaatio.py" osa="qam"}
```

Kanavan kohina siirtää vastaanotettua pistettä, ja vastaanotin
päättää, mikä konstellaation piste on lähinnä:

```{.python tiedosto="esimerkit/04-konstellaatio.py" osa="kanava"}
```

```{.tuloste tiedosto="esimerkit/04-konstellaatio.odotettu"}
```

Kun lähetysteho pidetään samana, pisteiden lisääminen tuo ne lähemmäs
toisiaan. Jokainen kahden bitin lisäys noin puolittaa lyhimmän välin ja
vaatii noin 6 dB paremman signaali-kohinasuhteen: 16-QAM tekee
16 dB:ssä saman verran virheitä kuin 64-QAM 22 dB:ssä. Tämä on
Shannonin kaavan logaritmi käytännössä.

![QPSK, 16-QAM ja 64-QAM samalla lähetysteholla ja samalla kohinalla
(SNR 16 dB). Tummat pisteet ovat lähetetyt symbolit bittikuvioineen,
harmaat vastaanotetut. QPSK:n pilvet pysyvät kaukana toisistaan,
64-QAM:n pilvet sulautuvat yhteen.](kuvat/konstellaatio.png){width=100%}

Radio valitsee konstellaation mitatun signaalin mukaan (adaptiivinen
modulaatio, luku Kanavan kapasiteetti): Wi-Fi ja 5G käyttävät
tukiaseman lähellä 256- tai 1024-QAM:ia ja solun reunalla QPSK:ta.
Modulaattorin ja vastaanottimen toteutus, pulssinmuokkaus ja
synkronointi kuuluvat taitoon *Digitaalinen tiedonsiirto*.

## Kehystys

Vastaanottimen on löydettävä kehyksen alku bittivirrasta. Tapoja on
kolme:

1. **Tahdistekuvio ja pituuskenttä.** Ethernet aloittaa kehyksen
   7 tavun vuorottelevalla kuviolla (*preamble*), jolla vastaanotin
   lukittuu kelloon, ja tavulla SFD (*start frame delimiter*).
   Kehyksen pituus selviää otsakkeesta tai siitä, että signaali loppuu.
2. **Erikoismerkki ja täyttö.** HDLC- ja PPP-yhteydet merkitsevät
   kehyksen alun ja lopun lippukuviolla 01111110. Jotta kuvio ei voi
   esiintyä datassa, lähettäjä lisää nollan aina viiden peräkkäisen
   ykkösen jälkeen, ja vastaanottaja poistaa sen (**bittitäyttö**).
3. **Linjakoodin varatut sanat.** 4B5B:ssä ja 8b10b:ssä on
   koodisanoja, jotka eivät koskaan esiinny datassa, ja niillä
   merkitään kehyksen rajat.

```{.python tiedosto="esimerkit/04-bittitaytto.py" osa="taytto"}
```

```{.tuloste tiedosto="esimerkit/04-bittitaytto.odotettu"}
```

Bittitäytön kustannus riippuu datasta: pahimmillaan ykkösiä täynnä
oleva data kasvaa viidenneksellä. Tavupohjaiset protokollat käyttävät
samaa ideaa tavuina (PPP:n tavutäyttö, COBS-koodaus sarjayhteyksillä).

## Käytännössä

- **Linjakoodi on osa nopeutta.** Linjan symbolinopeus on suurempi
  kuin datanopeus: 100BASE-X lähettää 125 Mbaud kuljettaakseen
  100 Mbit/s. Kun luet spesifikaatiota, erota bittinopeus,
  symbolinopeus ja hyötykuorman nopeus.
- **Sekoitus korvaa koodin.** Nykyiset nopeat linkit käyttävät
  vähän lisäbittejä vaativaa koodausta ja sekoitusta. Kehittäjä näkee
  sen harvoin, mutta se selittää esimerkiksi, miksi 10GBASE-R:n
  linjanopeus on 10,3125 Gbaud.
- **Gray-koodi aina, kun tasot ovat järjestyksessä.** Sama periaate
  toistuu QAM-konstellaatioissa, kulma-anturien koodilevyissä ja
  kellotusalueiden välisissä laskureissa (RTL-suunnittelu).
- **Kehystys on suunnittelupäätös myös omissa protokollissa.**
  Sarjaväylää tai tavuvirtaa käyttävä protokolla tarvitsee
  yksiselitteisen tavan löytää viestin alku virheen jälkeen;
  pituuskenttä yksin ei riitä, jos yksikin tavu katoaa.

## Itsearviointi

- Osaat selittää, miksi NRZ ei yksin riitä ja miten Manchester ja
  4B5B säilyttävät kellotiedon.
- Osaat laskea linjakoodin lisäkustannuksen ja symbolinopeuden
  datanopeudesta.
- Osaat selittää, miksi PAM4-tasot koodataan Gray-koodilla ja mitä
  neljä tasoa maksavat SNR:nä.
- Osaat selittää, mitä konstellaation piste tarkoittaa, ja arvioida,
  paljonko parempaa signaalia tiheämpi konstellaatio vaatii.
- Osaat toteuttaa bittitäytön ja selittää, miten vastaanotin löytää
  kehyksen rajat.
