# Ajoitusanalyysi FPGA:lla

Staattinen ajoitusanalyysi laskee jokaisen rekisteristä rekisteriin
kulkevan polun viiveen ja vertaa sitä kellojaksoon. Menetelmä on sama
kuin ASIC-vuossa (taito *ASIC-toteutus*). FPGA:lla polun viive
koostuu kuitenkin muista osista, ja sen pienentämisen keinot ovat
osittain toiset.

## Polun viive FPGA:lla

Polku alkaa kiikun kellosta ja päättyy seuraavan kiikun tuloon:

$$t_{\text{kello}\to\text{lähtö}} + \sum (t_{\text{LUT}} + t_{\text{reititys}}) + t_{\text{asetus}} \le T_{\text{kello}}$$

iCE40:ssä LUT:n viive on alle nanosekunnin, mutta reititys LUT:ien
välillä vie usein enemmän: tyypillisesti 50–70 % polun viiveestä on
johtimissa. Siksi FPGA:lla *logiikkatasojen määrä* (montako LUT:ia
peräkkäin) ennustaa Fmax:ia paremmin kuin yksittäisten porttien viive.
Kantoketju on poikkeus: se on nopea erillisreitti, ja pitkäkin
summain on nopea.

nextpnr raportoi jokaisen kellon kriittisen polun solu solulta. Alla on
alku yksivaiheisen kertojan (seuraava kohta) polusta, solujen pitkät
nimet lyhennettyinä. Sarakkeet ovat vaiheen viive ja kertynyt aika
nanosekunteina, ja suluissa ovat solujen koordinaatit piirillä:

```text
Info: Critical path report for clock 'clk$SB_IO_IN_$glb_clk'
Info: curr total
Info:  1.4  1.4  Source ra_SB_DFF_Q_2_DFFLC.O
Info:  3.0  4.3    Net ra[5] budget 12.426000 ns (9,3) -> (11,4)
Info:  1.2  5.5  Source tulo_..._LC.O
Info:  1.8  7.3    Net tulo_...[0] budget 12.426000 ns (11,4) -> (11,4)
...
Info: 10.9 ns logic, 14.2 ns routing
```

Polku on 25,1 ns (40 MHz), ja siitä 57 % on reititystä.

## Liukuhihnoitus

Pitkää kombinatorista polkua lyhennetään lisäämällä rekisterejä
väliin. Luvun 4 kertoja logiikkasoluilla on hyvä esimerkki: 8 × 8 bitin
kertolasku on syvä summainpuu. Jaetaan se kahteen vaiheeseen: ensin
kaksi 8 × 4 bitin osatuloa, seuraavalla jaksolla niiden summa.

```{.systemverilog tiedosto="esimerkit/06-liukuhihna/kertoja_lh.sv" osa="kertoja_lh"}
```

Testipenkki ajaa molemmat versiot rinnakkain ja tarkistaa, että
kaksivaiheinen antaa saman tuloksen jaksoa myöhemmin:

```{.systemverilog tiedosto="esimerkit/06-liukuhihna/testipenkki.sv" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/06-liukuhihna.odotettu"}
```

Vuo ajaa molemmat versiot ja lisäksi yksivaiheisen version
**uudelleenajoituksella** (retiming), jossa synteesi saa siirtää
rekistereitä logiikan läpi:

```{.makefile tiedosto="esimerkit/Makefile" osa="liukuhihna"}
```

```{.tuloste tiedosto="esimerkit/raportit/liukuhihna-1.odotettu"}
```

```{.tuloste tiedosto="esimerkit/raportit/liukuhihna-2.odotettu"}
```

```{.tuloste tiedosto="esimerkit/raportit/liukuhihna-1-retime.odotettu"}
```

| Versio | Fmax | Logiikkasoluja | Latenssi |
|--------|------|----------------|----------|
| 1 vaihe | 40,0 MHz | 173 | 2 jaksoa |
| 2 vaihetta | 49,4 MHz | 148 | 3 jaksoa |
| 1 vaihe, uudelleenajoitus | 55,8 MHz | 192 | 2 jaksoa |

Lisävaihe nosti Fmax:ia neljänneksellä ja jopa pienensi solumäärää,
koska kaksi kapeaa osatuloa on edullisempi rakentaa kuin yksi leveä.
Uudelleenajoitus pääsi vielä pidemmälle siirtämällä tulorekisterit
kertojan sisään, mutta kasvatti solumäärää: rekisteri, joka siirretään
haarautuvan signaalin yli, monistuu.

Liukuhihnoituksen hinta on latenssi. Kun tulos tarvitaan heti
seuraavalla jaksolla, esimerkiksi takaisinkytkennässä (laskuri,
kertymä, tilakone), lisärekisteri muuttaa toimintaa. Silloin polkua
lyhennetään muuten: kevyemmällä logiikalla tai rakenteella, jossa
takaisinkytkentä on lyhyt.

## Muita keinoja

- **Rekisteröi IO.** Tulo- ja lähtörekisterit IO-lohkoissa poistavat
  nastojen ja sisälogiikan välisen reitityksen kriittisiltä poluilta.
- **Kopioi rekisteri.** Suuri tuulettuvuus pidentää reititystä; kaksi
  kopiota samasta rekisteristä puolittaa kuorman.
- **Kantoketju tai DSP.** Aritmetiikka erikoislohkoihin, jotka ovat
  nopeampia kuin LUT-toteutus.
- **One-hot-tilakoodaus.** Tilakone, jossa jokaisella tilalla on oma
  kiikku, on FPGA:lla usein nopeampi kuin binäärikoodattu, koska
  seuraavan tilan logiikka on matalampi. Kiikkuja FPGA:ssa riittää.

## Ajoitus, joka ei näy

Staattinen ajoitusanalyysi tarkistaa vain polut, joille on annettu
vaatimus. nextpnr:n iCE40-tuessa vaatimus on vain kellotaajuus, joten
tarkistamatta jäävät

- polut IO-nastoista ja niihin: nextpnr raportoi niiden viiveen
  (`<async>`), mutta ulkoisen piirin ajoitus on tarkistettava erikseen
  datalehdistä;
- polut kellotusalueiden välillä: nextpnr raportoi niidenkin viiveen,
  mutta ne on suunniteltava tahdistimilla (luku 8), ei ajoitettava;
- polut DSP-lohkon sisällä, joille nextpnr 0.6:n iCE40-malli ei
  raportoi Fmax:ia (luvun 4 DSP-kertojan raportissa ei ole
  ajoitusriviä).

Suurten valmistajien työkaluissa IO-viiveet ja kellojen suhteet
annetaan SDC/XDC-rajoitteina, ja raportti listaa myös rajoittamattomat
polut. Rajoittamaton polku on aina tarkistettava: se on joko oikeasti
merkityksetön tai piilevä vika.

## Käytännössä

- **Lue kriittinen polku.** Fmax kertoo, ettei suunnitelma riitä;
  kriittinen polku kertoo miksi. Logiikkatasojen määrä ja reitityksen
  osuus ohjaavat korjausta.
- **Liukuhihnoita datapolku, ei takaisinkytkentää.** Lisärekisteri
  suoraan kulkevaan datapolkuun on lähes ilmainen; silmukkaan se
  muuttaa toimintaa.
- **Uudelleenajoitus on apu, ei korvike.** Se toimii, kun rekistereitä
  on jo ylimäärin oikeassa kohdassa. Arkkitehtuurin ongelmia se ei
  korjaa.
- **Marginaali tavoitteeseen.** Tavoitetaajuus `--freq` hieman
  todellista korkeammaksi, jotta työkalu optimoi tosissaan, ja
  tulokseen vähintään 10 %:n vara.

## Itsearviointi

- Osaat lukea nextpnr:n ajoitusraportista Fmax:n ja kriittisen polun
  ja kertoa, miksi reititys hallitsee FPGA:n viiveitä.
- Osaat liukuhihnoittaa datapolun ja arvioida sen vaikutuksen Fmax:iin,
  latenssiin ja solumäärään.
- Osaat kertoa, mitä uudelleenajoitus tekee ja milloin se auttaa.
- Osaat luetella polut, joita ajoitusanalyysi ei tarkista, ja miten ne
  varmistetaan.
