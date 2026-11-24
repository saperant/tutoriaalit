# Virheet ja protokollatarkistus

Integroidussa järjestelmässä virheitä on kahta lajia. *Ajonaikaiset
virheet* johtuvat ohjelmistosta: osoite osuu tyhjään kohtaan, rekisteriin
kirjoitetaan väärällä leveydellä tai vain luettavaan rekisteriin
yritetään kirjoittaa. Järjestelmän on havaittava ne ja kerrottava niistä
ohjelmistolle. *Integrointivirheet* ovat laitteiston virheitä: lohko
rikkoo väyläprotokollaa, ja järjestelmä jumittuu tai siirtää väärää
dataa. Ne on löydettävä simulaatiossa ennen piitä.

## Väylävirheistä poikkeuksiksi

Pikku-SoC:ssa jokainen virhe muuttuu vastauskoodiksi, joka kulkee
isännälle:

| Tilanne | Havaitsija | Vastaus | Ytimen poikkeus |
|---------|------------|---------|-----------------|
| Osoitteessa ei ole orjaa | kytkimen oletusorja | DECERR | 5 tai 7 |
| Tyhjä APB-ikkuna | APB-silta | DECERR | 5 tai 7 |
| Osittainen kirjoitus oheislaitteeseen | oheislaite (PSLVERR) | SLVERR | 7 |
| Kirjoitus vain luettavaan rekisteriin | rekisterilohko (PSLVERR) | SLVERR | 7 |
| Kohdistamaton sanaviittaus | ydin itse | – | 4 tai 6 |

Ydin muuttaa virhevastauksen poikkeukseksi: lukemisen väylävirhe on
`mcause` 5 ja kirjoituksen 7, ja `mtval` sisältää osoitteen. Ohjelma
`virheet.c` aiheuttaa jokaisen tilanteen ja käsittelee poikkeuksen
ohittamalla aiheuttaneen käskyn:

```{.c tiedosto="esimerkit/sw/virheet.c" osa="poikkeus"}
```

```{.c tiedosto="esimerkit/sw/virheet.c" osa="kokeet"}
```

```{.tuloste tiedosto="esimerkit/odotettu/virheet.odotettu"}
```

Kohdistamaton sanaluku on kirjoitettu inline-assemblyllä, koska C-
kääntäjä näki osoitteen 0x102 ja jakoi luvun kahdeksi puolisanaluvuksi
(`lhu`), jotka ovat kohdistettuja. Kääntäjä saa tehdä niin, koska
kohdistamaton osoitin on C:ssä määrittelemätöntä käyttäytymistä.
Laitteiston virhepolkujen testaaminen vaatii usein juuri tällaisia
konekielisiä testejä.

Tuotantojärjestelmässä väylävirhe ei yleensä ole ohitettava: se kertoo
ohjelmointivirheestä, ja käyttöjärjestelmä lopettaa prosessin tai
ytimen virhekäsittelijä kirjaa virheen ja käynnistää järjestelmän
uudelleen. Tärkeintä on, että virhe *havaitaan* eikä ohjelmisto jatka
hiljaa väärällä datalla.

## Protokollatarkistin

Integrointivirheet etsitään tarkistimilla, jotka valvovat
väyläprotokollaa jokaisessa liitännässä simulaation ajan. Pikku-SoC:n
`axil_tarkistin.sv` valvoo AXI4-Liten tärkeimpiä sääntöjä:

```{.systemverilog tiedosto="esimerkit/rtl/axil_tarkistin.sv" osa="saanto"}
```

Tarkistin vertaa kunkin kanavan nykyistä tilaa edellisen jakson
tilaan: jos VALID oli ylhäällä ilman READYä, sen on oltava yhä
ylhäällä ja sisällön sama. Lisäksi se laskee avoimet pyynnöt ja
varmistaa, ettei vastaus tule ilman pyyntöä. Tarkistimet kytketään
SoC:n jokaiseen AXI-liitäntään, ja ne ovat mukana kaikissa
simulaatioissa:

```{.systemverilog tiedosto="esimerkit/rtl/soc.sv" osa="tarkistimet"}
```

Tarkistimen on myös itse toimittava. Testipenkki `huono_orja.sv` tekee
tahallaan yleisen virheen: orja laskee RVALIDin ennen kuin isäntä on
kuitannut vastauksen.

```{.systemverilog tiedosto="esimerkit/tb/huono_orja.sv" osa="virhe"}
```

Simulaation on päätyttävä virheeseen. Esimerkkien `Makefile`
tarkistaa, että ajo epäonnistuu ja että ilmoitus nimeää rikotun säännön:

```{.tuloste tiedosto="esimerkit/odotettu/tarkistin.odotettu"}
```

Tällainen *negatiivinen testi* on tarkistimen tärkein testi. Tarkistin,
joka ei koskaan laukea, voi olla rikki, eikä sitä huomaa ennen kuin
virhe pääsee piihin.

## Formaali tarkistus ja varmennus-IP

Simulaatiossa tarkistin näkee vain ne tilanteet, joihin testit sattuvat
johtamaan. Kaksi tekniikkaa laajentaa kattavuutta:

- **Formaali tarkistus.** Samat säännöt kirjoitetaan SystemVerilogin
  samanaikaisina väittäminä (`assert property`), ja formaali työkalu
  (esimerkiksi SymbiYosys tai kaupalliset JasperGold ja VC Formal)
  todistaa, ettei mikään syötesarja riko niitä. Pienille lohkoille,
  kuten väyläsilloille ja välittäjille, formaali tarkistus on usein
  tehokkaampi kuin simulaatio.
- **Varmennus-IP (VIP).** Väyläprotokollille on valmiita tarkistimia,
  malleja ja kattavuuskeräimiä, jotka testaavat lohkon kaikilla
  määrittelyn sallimilla tavoilla: satunnaiset odotusajat, takaisinpaine,
  purskeiden reunatapaukset. Armin AMBA-määrittelyihin on lisäksi
  julkaistu tarkistussäännöt, joita VIP:t toteuttavat.

## Käytännössä

- **Tarkistin jokaiseen liitäntään.** Protokollatarkistimet ovat
  halpoja ja löytävät integrointivirheet heti siitä liitännästä, jossa
  ne syntyvät, eivätkä vasta jumittuneen järjestelmän oireista.
- **Testaa tarkistin.** Jokaisella tarkistimella on vähintään yksi
  testi, jossa sen on lauettava.
- **Virhepolut ovat toimintoja.** DECERR, SLVERR, aikakatkaisut ja
  virhekeskeytykset testataan kuten muukin toiminta. Ne ovat polkuja,
  joita tavallinen ohjelmisto ei kulje, ja siksi niissä on piilossa
  eniten virheitä.
- **Aikakatkaisu väylään.** Orja, joka ei vastaa, jumittaa isännän.
  Kytkimeen tai siltaan lisätty vahtiajastin vastaa virheellä, jos
  vastausta ei kuulu, ja kirjaa jumittuneen osoitteen.
- **Virheen tiedot talteen.** Väylävirheen osoite, isäntä ja
  siirron tyyppi tallennetaan rekisteriin. Kun virhe tapahtuu
  kentällä, se on ainoa tieto, josta syyn voi päätellä.

## Itsearviointi

- Osaat kertoa, miten DECERR ja SLVERR syntyvät ja miten ne näkyvät
  ohjelmistolle poikkeuksina.
- Osaat kirjoittaa poikkeuskäsittelijän, joka tulkitsee `mcause`- ja
  `mtval`-arvot.
- Osaat kirjoittaa väyläprotokollan tarkistimen, joka valvoo VALIDin
  pysyvyyttä ja vastausten järjestystä.
- Osaat perustella, miksi tarkistimella on oltava negatiivinen testi.
- Osaat kertoa, mitä formaali tarkistus ja varmennus-IP lisäävät
  simulaatioon.
