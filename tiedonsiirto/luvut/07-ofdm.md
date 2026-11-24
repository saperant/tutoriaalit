# OFDM

Kun symbolinopeus kasvaa, monitiekanavan viive-erot ylittävät
symbolin keston, ja jokainen symboli vuotaa seuraaviin. Yhden
kantoaallon järjestelmä tarvitsee silloin pitkän ja laskennallisesti
raskaan taajuuskorjaimen. **OFDM** (*orthogonal frequency division
multiplexing*) ratkaisee ongelman toisin: se jakaa datavirran satoihin
tai tuhansiin hitaisiin alikantoaaltoihin. Kukin alikantoaalto näkee
kanavan yhtenä kompleksisena kertoimena. Taito *Tietoliikennetekniikka*
esitteli OFDM:n multipleksointina. Tässä luvussa se toteutetaan ja
nähdään, miksi syklinen etuliite tekee taajuuskorjauksesta helppoa.

## IFFT ja syklinen etuliite

OFDM-lähetin sijoittaa $N$ konstellaatiopistettä taajuustasoon ja tekee
niistä IFFT:llä yhden aikatason OFDM-symbolin. Alikantoaallot ovat
ortogonaalisia, koska niiden taajuusero on täsmälleen $1/(NT_s)$, missä
$T_s$ on näyteväli. Vastaanotin palauttaa pisteet FFT:llä.

Monitiekanava konvoloi signaalin kanavan impulssivasteella.
Konvoluutio muuttuu taajuustasossa kertolaskuksi vain, jos se on
**syklinen**. Siksi symbolin eteen kopioidaan sen loppuosa,
**syklinen etuliite** (CP, *cyclic prefix*). Jos etuliite on vähintään
yhtä pitkä kuin kanavan impulssivaste, vastaanotin heittää etuliitteen
pois, ja jäljelle jäävä osa on lähetetyn symbolin syklinen konvoluutio
kanavan kanssa. Silloin FFT:n jälkeen jokainen alikantoaalto on vain
kerrottu kanavan taajuusvasteella $H[k]$.

```{.python tiedosto="esimerkit/07-ofdm.py" osa="lahetin"}
```

Kanava on kahdeksan näytteen pituinen monitie. Vastaanotin tuntee
kanavan (käytännössä se estimoidaan tunnetuista pilottisymboleista) ja
jakaa kunkin alikantoaallon arvon sen kanavakertoimella: **yhden
kertoimen taajuuskorjain**.

```{.python tiedosto="esimerkit/07-ofdm.py" osa="kanava"}
```

```{.tuloste tiedosto="esimerkit/07-ofdm.odotettu"}
```

Ilman etuliitettä edellinen symboli vuotaa seuraavaan, ja
alikantoaallot häiritsevät toisiaan: virheitä on satoja hyvästä
signaali-kohinasuhteesta huolimatta. Neljän näytteen etuliite poistaa
suurimman osan häiriöstä, mutta EVM jää suureksi, koska kanavan häntä
on etuliitettä pidempi. Kahdeksan näytteen etuliitteellä
symbolienvälinen häiriö katoaa kokonaan, eikä pidempi etuliite enää
paranna tulosta: jäljelle jää kohina. Etuliite maksaa
spektritehokkuutta, sillä se ei kuljeta tietoa. WLAN käyttää
etuliitettä, joka on 25 % symbolin pituudesta, ja LTE noin 7 %.

## Taajuusselektiivisyys ja kohinan vahvistuminen

Kanavan vaste vaihtelee alikantoaaltojen välillä 17 dB. Heikoimmilla
alikantoaalloilla taajuuskorjaus jakaa signaalin pienellä luvulla ja
vahvistaa samalla kohinaa, minkä vuoksi EVM jää 4,6 %:iin, vaikka
lähetettyä kohinaa vastaava taso olisi 3 %. Ilman kanavakoodausta
OFDM:n bittivirhesuhteen ratkaisevat heikoimmat alikantoaallot.
Koodaus ja lomitus alikantoaaltojen yli muuttavat
taajuusselektiivisyyden diversiteetiksi: heikkojen alikantoaaltojen
bitit korjataan vahvojen avulla. Siksi kaikki OFDM-järjestelmät
käyttävät koodausta.

## Kanavan estimointi piloteista

Edellä vastaanotin tunsi kanavan. Todellisuudessa osa alikantoaalloista
on **pilotteja**, joiden arvo tunnetaan, ja kanava estimoidaan niiden
kohdalla jakamalla: $\hat H[k] = Y[k]/X[k]$. Muiden alikantoaaltojen
kanava interpoloidaan. Kokeessa joka neljäs alikantoaalto on pilotti,
ja signaali-kohinasuhde on 25 dB.

```{.python tiedosto="esimerkit/07-pilotit.py" osa="pilotit"}
```

Lineaarinen interpolointi pilottien välillä on yksinkertaisin
vaihtoehto. Parempi on käyttää tietoa siitä, että kanavan
impulssivaste on lyhyt: pilottien IFFT antaa impulssivasteen, kun
pilotteja on enemmän kuin vasteessa on näytteitä. Vasteen
ylimääräiset näytteet ovat pelkkää kohinaa, ja ne nollataan ennen kuin
vaste muunnetaan takaisin taajuustasoon. Jos kanava pysyy samana,
estimaatteja voi lisäksi keskiarvoistaa symbolien yli.

```{.python tiedosto="esimerkit/07-pilotit.py" osa="estimoi"}
```

```{.tuloste tiedosto="esimerkit/07-pilotit.odotettu"}
```

Lineaarinen interpolointi epäonnistuu, koska kanava muuttuu nopeasti
taajuuden mukana: kanavan viive on seitsemän näytettä, joten vaste
kiertää usean kierroksen alikantoaaltojen yli, eikä suora viiva neljän
alikantoaallon välillä seuraa sitä. Lisäksi viimeiset alikantoaallot
jäävät viimeisen pilotin ulkopuolelle. Aikatason rajaus käyttää
kanavan rakennetta ja on lähes yhtä hyvä kuin tunnettu kanava.
Keskiarvo 200 symbolin yli poistaa estimaatin kohinan kokonaan.
Pilottien tiheys mitoitetaan kanavan viiveen mukaan taajuussuunnassa
ja kanavan muutosnopeuden (Doppler) mukaan aikasuunnassa.

## Huipputeho

Monen itsenäisen alikantoaallon summa on keskeisen raja-arvolauseen
mukaan lähes normaalijakautunut, joten aikatason näytteissä on suuria
huippuja.

```{.python tiedosto="esimerkit/07-ofdm.py" osa="papr"}
```

Noin joka 600. näyte on yli 8 dB keskitehon yläpuolella. Tehovahvistimen
on toistettava huiput lineaarisesti, joten sen keskiteho on pidettävä
selvästi kyllästymistason alapuolella. Siksi LTE:n nousevalla siirtotiellä
(päätelaitteesta tukiasemaan) käytetään SC-FDMA:ta, joka on
DFT-esikoodattu OFDM pienemmillä huipuilla.

## Muut käytännön haasteet

OFDM on herkkä taajuusvirheelle: jo pieni osa alikantoaaltovälistä
rikkoo ortogonaalisuuden, ja alikantoaallot vuotavat toisiinsa.
Taajuusvirhe estimoidaan tavallisesti toistuvasta alkuosasta samaan
tapaan kuin luvussa 11. Ajoitukselle OFDM on sen sijaan armollinen: kun
ikkuna osuu etuliitteen sisään, ajoitusvirhe näkyy vain lineaarisena
vaiheena alikantoaaltojen yli ja korjautuu kanavaestimaatissa.

## Käytännössä

- **Mitoita etuliite kanavan viiveen mukaan.** Etuliitteen on oltava
  pidempi kuin kanavan impulssivasteen merkittävä osa, ja sen osuus
  maksaa suoraan nopeutta. Sisätiloissa viiveet ovat satoja
  nanosekunteja, ulkona ja yleisradiossa mikrosekunteja.
- **Taajuuskorjaus on yksi kerroin alikantoaaltoa kohti.** Se on
  OFDM:n suurin etu yhden kantoaallon taajuuskorjaimiin verrattuna.
  Kanava estimoidaan piloteista ja interpoloidaan alikantoaaltojen ja
  ajan yli.
- **Käytä koodausta ja lomitusta alikantoaaltojen yli.** Ilman niitä
  taajuusselektiivinen kanava hävittää heikoimpien alikantoaaltojen
  bitit.
- **Huomioi huipputeho ja taajuusvirhe.** Ne ovat OFDM:n hinta:
  vahvistimelle tarvitaan varaa, ja taajuussynkronoinnin on oltava
  tarkka.

## Itsearviointi

- Osaat toteuttaa OFDM-lähettimen ja -vastaanottimen IFFT:llä, FFT:llä
  ja syklisellä etuliitteellä.
- Osaat selittää, miksi syklinen etuliite muuttaa monitiekanavan yhdeksi
  kertoimeksi alikantoaaltoa kohti, ja mitoittaa sen.
- Osaat selittää kohinan vahvistumisen heikoilla alikantoaalloilla ja
  koodauksen merkityksen OFDM:ssä.
- Osaat estimoida kanavan piloteista ja selittää, miksi aikatason
  rajaus voittaa lineaarisen interpoloinnin taajuusselektiivisessä
  kanavassa.
- Osaat selittää OFDM:n huipputeho-ongelman ja taajuusvirheherkkyyden.
