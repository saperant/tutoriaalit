# Kello-, nollaus- ja tehoalueet

Pikku-SoC:ssa on yksi kello, yksi nollaus ja yksi virransyöttö, joten
kaikki lohkot ovat samassa alueessa. Oikeassa järjestelmäpiirissä alueita
on useita: suoritin käy eri kellolla kuin oheislaitteet, USB-ohjain
tarvitsee oman 60 MHz:n kellonsa, ja käyttämättömät lohkot sammutetaan
virran säästämiseksi. Alueiden rajat ovat integroijan vastuulla.

## Kellotusalueet

Kellotusalue (clock domain) on joukko kiikkuja, joilla on sama kello.
Signaali, joka kulkee alueelta toiselle, on tahdistettava, koska
vastaanottava kiikku voi näytteistää sen muuttumishetkellä ja jäädä
metastabiiliin tilaan. Tekniikat (kahden kiikun tahdistin, kättely,
asynkroninen FIFO, Gray-koodatut osoittimet) käsitellään taidossa
*RTL-suunnittelu SystemVerilogilla*. SoC-tasolla kysymykset ovat:

- **Missä rajat ovat?** Jokainen kellotusalueen ylitys luetellaan, ja
  ylitykset kootaan muutamaan tunnettuun lohkoon: väyläsiltoihin,
  FIFOihin ja keskeytysten tahdistimiin.
- **Kuka tarkistaa?** CDC-tarkistustyökalu (clock domain crossing)
  etsii tahdistamattomat ylitykset koko piiristä. Simulaatio ei löydä
  niitä, koska simulaattorissa metastabiiliutta ei ole.

## Kellon portitus

Kello kuluttaa tehoa, vaikka lohko ei tekisi mitään: jokainen kiikku ja
kellopuun puskuri latautuu ja purkautuu joka jaksolla. Kellon portitus
(clock gating) pysäyttää käyttämättömän lohkon kellon. Portitus tehdään
*kellon portitussolulla* (integrated clock gating, ICG):

```{.systemverilog tiedosto="esimerkit/rtl/tehoalue.sv" osa="icg"}
```

Pelkkä JA-portti kellon ja sallinnan välissä ei kelpaa: jos sallinta
muuttuu kellon ollessa ylhäällä, portitettuun kelloon syntyy lyhyt
pulssi (glitch), joka voi kellottaa osan kiikuista. Salpa pitää
sallinnan vakaana koko korkean puolijakson ajan. Synteesikirjastossa ICG
on valmis solu, ja synteesityökalu voi lisätä portitusta automaattisesti
rekistereihin, joilla on sallintasignaali.

## Nollausalueet ja järjestys

Nollaus on tahdistettava jokaisen kellotusalueen kelloon: nollaus
asetetaan asynkronisesti mutta vapautetaan synkronisesti (luku 9 taidossa
*RTL-suunnittelu SystemVerilogilla*). SoC-tasolla nollausten
*järjestys* on yhtä tärkeä:

1. Virransyöttö ja kellot vakaiksi (PLL lukittuu) ennen kuin mitään
   nollausta vapautetaan.
2. Muistiohjain ja väylät ennen isäntiä: suoritin ei saa aloittaa
   hakuja ennen kuin väylä vastaa.
3. Suoritin vapautetaan viimeisenä, tai käynnistysydin ensin ja muut
   ytimet ohjelmiston käskystä.

Myös nollauksen *syy* tallennetaan rekisteriin (virta päälle,
vahtikoira, ohjelmiston pyyntö), jotta ohjelmisto voi toimia sen mukaan.

## Tehoalueet

Kellon pysäyttäminen säästää dynaamisen tehon, mutta transistorien
vuotovirta (staattinen teho) kuluu yhä. Pienissä valmistusprosesseissa
vuoto on merkittävä osa kulutuksesta, joten käyttämätön lohko
sammutetaan kokonaan *tehoalueena* (power domain). Sammuttaminen ja
käynnistäminen vaativat tarkan järjestyksen:

```{.systemverilog tiedosto="esimerkit/rtl/tehoalue.sv" osa="ohjain"}
```

Sammutettaessa alueen lähdöt *eristetään* ensin. Virrattoman alueen
lähtö kelluu, ja aina päällä olevan alueen logiikka voisi tulkita sen
mielivaltaiseksi arvoksi tai jopa kuluttaa oikosulkuvirtaa. Eristyssolu
pakottaa lähdön tunnettuun arvoon:

```{.systemverilog tiedosto="esimerkit/rtl/tehoalue.sv" osa="eristys"}
```

Käynnistyksessä järjestys on päinvastainen: virta päälle, jännitteen
annetaan asettua, alue nollataan kellon käydessä, nollaus vapautetaan ja
vasta lopuksi eristys poistetaan. Testipenkki käy sekvenssin läpi:

```{.tuloste tiedosto="esimerkit/odotettu/tehoalue.odotettu"}
```

Saman ajon ajoituskaavio näyttää järjestyksen yhdellä silmäyksellä.
Vaiheet ovat ohjaimen tilan numeroita: 0 PAALLA, 1 ERISTA, 2
KELLO_POIS, 3 POIS, 4 VIRTA_PAALLE, 5 NOLLAUS ja 6 VAPAUTA. Kun virta
katkeaa, alueen sisäinen arvo muuttuu mielivaltaiseksi (`A5`), mutta
eristetty lähtö `lahto` pysyy nollassa.

```{.ajoituskaavio tiedosto="esimerkit/kaaviot/tehoalue.json" otsikko="Tehoalueen sammutus ja käynnistys simulaatiosta"}
```

Tulosteesta näkyvät tehoalueiden perussäännöt:

- Eristys nousee ennen kuin kello pysähtyy ja virta katkeaa, joten
  eristetty lähtö on nolla koko sammutuksen ajan.
- Virran katkettua alueen tila tuhoutuu (`0xa5` simuloi mielivaltaista
  arvoa). Laskurin arvo `0x0b` ei säily ilman säilytysrekistereitä.
- Käynnistyksessä alue nollataan ennen eristyksen poistoa, joten aina
  päällä oleva puoli ei koskaan näe alustamatonta arvoa.

## Säilytys ja tasonsiirto

Tehoalueisiin liittyy muitakin soluja:

- **Säilytysrekisterit** (retention registers) säilyttävät tilansa
  erillisellä pienellä virransyötöllä, kun alue on sammutettu. Alue
  jatkaa heräämisen jälkeen siitä, mihin jäi, ilman ohjelmiston
  tallennusta ja palautusta.
- **Tasonsiirtimet** (level shifters) tarvitaan, kun alueilla on eri
  käyttöjännite (dynaaminen jännitteen ja taajuuden säätö, DVFS).
- **Virtakytkimet** (power switches) ovat transistoreita, jotka
  kytkevät alueen syöttöjännitteen. Ne kytketään päälle porrastetusti,
  jotta käynnistysvirtapiikki ei pudota muiden alueiden jännitettä.

Tehoalueet, eristys, säilytys ja tasonsiirto kuvataan RTL:n rinnalla
erillisessä tehoaikomustiedostossa (UPF, Unified Power Format, IEEE
1801). Synteesi lisää solut sen perusteella, ja simulaattori, joka
ymmärtää UPF:ää, mallintaa virrattomien alueiden käyttäytymisen.

## Käytännössä

- **Jokainen ylitys tunnettuun lohkoon.** Kellotus-, nollaus- ja
  tehoalueiden ylitykset kootaan sovittuihin soluihin ja lohkoihin.
  Hajallaan olevaa ylitystä ei löydä kukaan ennen piitä.
- **Sekvenssi tilakoneeseen.** Sammutuksen ja käynnistyksen järjestys
  toteutetaan laitteiston ohjaimessa. Ohjelmisto pyytää tilaa, mutta ei
  ohjaa yksittäisiä signaaleja, koska väärä järjestys voi rikkoa
  piirin.
- **Simuloi virrattomuus.** Tavallinen RTL-simulaatio olettaa kaikki
  alueet päälle. UPF-tietoinen simulaatio tai tämän luvun tapainen
  malli (tila tuhoutuu, lähdöt eristetään) paljastaa puuttuvat
  eristykset.
- **Sammuttaminen maksaa.** Herääminen vie aikaa ja energiaa
  (jännitteen asettuminen, nollaus, tilan palautus). Lyhyeksi ajaksi
  kannattaa pysäyttää vain kello.
- **Herätyslogiikka aina päällä.** Keskeytys, joka herättää sammutetun
  alueen, on toteutettava aina päällä olevalla alueella.

## Itsearviointi

- Osaat luetella SoC:n kellotusalueiden ylitykset ja kertoa, miten ne
  tarkistetaan.
- Osaat selittää, miksi kellon portitukseen tarvitaan salvallinen
  portitussolu.
- Osaat kuvata nollausten vapautusjärjestyksen järjestelmässä, jossa on
  PLL, väylät ja suoritin.
- Osaat kuvata tehoalueen sammutus- ja käynnistyssekvenssin ja
  eristyksen tehtävän.
- Osaat kertoa, mitä säilytysrekisterit, tasonsiirtimet ja UPF ovat.
