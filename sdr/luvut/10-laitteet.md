# Laitteet ja radiolupasäännöt

Edelliset luvut käsittelivät näytteitä, ja tässä luvussa siirrytään
niiden lähteisiin. Laitteen valinta riippuu taajuusalueesta,
kaistanleveydestä, dynamiikasta ja siitä, tarvitaanko lähetystä.
Lähetys tuo mukaan myös lain: radiotaajuudet ovat jaettu luonnonvara,
ja niiden käyttöä säännellään tarkasti.

## Yleisiä laitteita

| Laite | Taajuusalue | ADC | Kaista | Lähetys |
|----------------------|------------------|------|----------------------|--------------------|
| RTL-SDR (RTL2832U) | noin 24–1766 MHz | 8 bit | 2,4 MS/s | ei |
| Airspy R2 | 24–1800 MHz | 12 bit | 10 MS/s | ei |
| HackRF One | 1 MHz – 6 GHz | 8 bit | 20 MS/s | kyllä, puolidupleksi |
| ADALM-PLUTO (AD9363) | 325–3800 MHz | 12 bit | 61,44 MS/s, USB 2.0 rajaa | kyllä, dupleksi |
| USRP B210 | 70 MHz – 6 GHz | 12 bit | 56 MHz, USB 3.0 | kyllä, 2×2 dupleksi |

Arvot ovat suuntaa-antavia ja vaihtelevat mallin ja version mukaan.
Tarkista ne valmistajan tiedoista. RTL-SDR on alun perin
DVB-T-televisiotikku, jonka piirin saa raakanäytetilaan. Se on
edullisin tapa aloittaa, ja tämän tutoriaalin vastaanottimet on
mitoitettu sille. HackRF ja Pluto ovat opetuksen ja kehityksen
lähetinkykyisiä laitteita, USRP tutkimuksen ja tuotekehityksen.

Ohjelmistorajapintoja on muutama. Laitekohtaiset kirjastot ovat
`librtlsdr`, `libhackrf` ja Pluton `libiio`. **SoapySDR** tarjoaa
yhteisen rajapinnan useimmille laitteille, ja GNU Radion
`soapy`-lohkot käyttävät sitä. Komentorivityökalut, kuten `rtl_sdr`,
`hackrf_transfer` ja `iio_readdev`, tallentavat raakanäytteitä
tiedostoon tai putkeen (luku 8).

## Herkkyys

Vastaanottimen **herkkyys** on pienin tuloteho, jolla haluttu laatu
saavutetaan. Termisen kohinan tehotiheys on huoneenlämmössä
$kT = -174$ dBm/Hz. Kaistalla $B$ kohinalattia on
$-174 + 10\log_{10}B$ dBm. Vastaanottimen **kohinaluku** NF kertoo,
kuinka paljon etuaste lisää kohinaa. Kun ilmaisin vaatii tietyn
signaali-kohinasuhteen, herkkyys on

$$P_\text{min} = -174 + 10\log_{10} B + \text{NF} + \text{SNR}_\text{vaadittu}
\quad \text{dBm}.$$

```{.python tiedosto="esimerkit/10-herkkyys.py" osa="herkkyys"}
```

Kaista on herkkyyden tärkein tekijä. Kapea signaali havaitaan
kymmeniä desibelejä heikompana kuin leveä, ja kohinaluvun 5 dB:n ero
näkyy suoraan herkkyydessä. Edullisen SDR:n kohinaluku vaihtelee
taajuuden mukaan ja on usein selvästi huonompi kuin erillisen
etuvahvistimen. Siksi antennin viereen asennettu pienikohinainen
vahvistin (LNA) parantaa heikkojen signaalien vastaanottoa.
Vahvistin parantaa kuitenkin vain kohinalukua, ei voimakkaiden
signaalien kestoa. Kaupunkiympäristössä voimakas FM- tai
matkapuhelinsignaali voi ylikuormittaa vahvistimen ja koko laitteen
(luku 2), jolloin kaistanpäästösuodin antennin ja vahvistimen välissä
on tärkeämpi kuin lisävahvistus.

## Näytevirta ja väylä

Laitteen näytetaajuus ei ole ainoa raja. Näytteiden on myös siirryttävä
tietokoneelle:

```{.python tiedosto="esimerkit/10-herkkyys.py" osa="vayla"}
```

```{.tuloste tiedosto="esimerkit/10-herkkyys.odotettu"}
```

HackRF:n 20 MS/s mahtuu USB 2.0:aan juuri ja juuri. Pluton AD9363
pystyy 61,44 MS/s:iin, mutta USB 2.0:n kautta jatkuva virta rajoittuu
muutamaan megahertsiin. Laajakaistainen käsittely tehdään siksi
laitteen FPGA:ssa, joka desimoi ennen väylää. Sama ajatus toistuu
kaikkialla: kanavan valinta (luku 4) tehdään mahdollisimman lähellä
ADC:tä.

## Radiolupasäännöt

Suomessa radiotaajuuksien käyttöä valvoo Liikenne- ja viestintävirasto
**Traficom**. Säännöt muuttuvat, joten alla on vain yleiskuva.
Tarkista ajantasaiset määräykset Traficomin verkkosivuilta ja
lainsäädäntö Finlexistä ennen kuin lähetät mitään.

**Lähettäminen vaatii luvan.** Radiolähettimen käyttöön tarvitaan
radiolupa, ellei lähetin ole luvasta vapaa. Luvasta vapaita ovat
Traficomin määräyksessä luetellut käytöt, esimerkiksi tietyt
ISM-kaistojen lyhyen kantaman laitteet. Niillä on tarkat ehdot
taajuudelle, teholle ja käyttöasteelle. SDR-laite, joka pystyy
lähettämään, ei ole itsessään luvasta vapaa, vaan ehdot koskevat
lähetystä: taajuutta, tehoa, kaistaa ja käyttöastetta. Radioamatöörit
saavat pätevyystodistuksella lähettää amatöörikaistoilla
amatööriradiotoiminnan ehdoin. Luvaton lähettäminen voi häiritä
esimerkiksi ilmailun, merenkulun ja hätäpalvelujen radioliikennettä,
ja se on rangaistavaa.

**Vastaanottaminen on yleensä sallittua, mutta viestit ovat
suojattuja.** Radiovastaanottimen käyttö ei Suomessa yleensä vaadi
lupaa. Laki sähköisen viestinnän palveluista suojaa kuitenkin
luottamuksellisia viestejä: jos vastaanotat viestin, jota ei ole
tarkoitettu sinulle tai yleisön vastaanotettavaksi, et saa ilman
lupaa hyödyntää sitä tai kertoa sen sisällöstä tai olemassaolosta
muille. Yleisradiolähetysten, kuten FM-asemien, kuuntelu on sallittua,
mutta niiden ohjelmasisältöä suojaa tekijänoikeus. Kun tallennat
oikeaa radioliikennettä esimerkiksi testiaineistoksi, tallenna
mieluummin omia lähetyksiäsi tai yleisradiolähetyksiä, äläkä julkaise
toisten viestejä.

**Kehitä ilman radiotietä.** Lähetin- ja vastaanotinketjun voi
kehittää kokonaan tallenteilla, kuten tässä tutoriaalissa. Laitteen
lähetintä testataan kaapelilla ja riittävällä vaimentimella suoraan
vastaanottimeen tai suojakotelossa, jolloin radiotietä ei käytetä.
Laitteiden markkinointia ja vaatimustenmukaisuutta koskee lisäksi
EU:n radiolaitedirektiivi (2014/53/EU).

## Käytännössä

- **Aloita vastaanotosta.** RTL-SDR ja tallenteet riittävät kaikkeen
  tämän tutoriaalin sisältöön. Lähetinkykyinen laite tarvitaan vasta,
  kun lähetintä testataan kaapelilla.
- **Laske herkkyys ennen laitehankintaa.** Kaista, kohinaluku ja
  vaadittu SNR kertovat, riittääkö edullinen laite vai tarvitaanko
  etuvahvistin.
- **Suodata ennen vahvistinta.** Voimakas signaali kaistan
  ulkopuolelta ylikuormittaa etuasteen. Kaistanpäästösuodin on usein
  hyödyllisempi kuin lisävahvistus.
- **Desimoi lähellä ADC:tä.** Väylän kaista on usein laitteen
  ADC:tä pienempi. Laitteen FPGA tai sulautettu prosessori desimoi
  ennen väylää.
- **Tarkista säännöt aina uudelleen.** Määräykset, taajuusjaot ja
  luvasta vapaiden käyttöjen ehdot muuttuvat. Katso Traficomin
  ajantasaiset määräykset ennen jokaista lähetystä.

## Itsearviointi

- Osaat valita SDR-laitteen taajuusalueen, kaistan, ADC:n bittimäärän
  ja lähetystarpeen perusteella.
- Osaat laskea vastaanottimen herkkyyden kohinalattiasta,
  kohinaluvusta ja vaaditusta signaali-kohinasuhteesta.
- Osaat arvioida, mahtuuko näytevirta väylään, ja selittää, miksi
  desimointi tehdään laitteessa.
- Osaat selittää lähettämisen ja vastaanottamisen sääntelyn
  pääperiaatteet Suomessa ja kertoa, mistä ajantasaiset säännöt
  löytyvät.
