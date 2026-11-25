# Laitteistotuki: VT-x, AMD-V ja EPT

Intelin VT-x ja AMD:n AMD-V tekivät x86:sta virtualisoitavan ilman
binäärikäännöstä. Muistin virtualisoinnin hinta laski vasta
toisen sukupolven tuella, kaksitasoisilla sivutauluilla (Intel EPT,
AMD NPT). Tämä luku käy läpi molemmat ja niiden hinnat.

## VMX-tilat ja VMCS

VT-x lisää suorittimeen kaksi tilaa:

- **VMX root** – hypervisor. Kaikki käskyt toimivat kuten ennenkin.
- **VMX non-root** – vieras. Vieraalla on oma rengas 0, joten sen ydin
  ajetaan etuoikeutetussa tilassa, mutta tietyt tapahtumat siirtävät
  suorituksen hypervisorille.

Siirtymiä on kaksi. **VM entry** (`vmlaunch`, `vmresume`) aloittaa tai
jatkaa vieraan suoritusta. **VM exit** palauttaa suorituksen
hypervisorille ja kertoo syyn. Vieraan ja isännän tila (rekisterit,
segmentit, ohjausrekisterit) sekä säännöt siitä, mitkä tapahtumat
aiheuttavat VM exitin, ovat muistissa rakenteessa **VMCS**
(Virtual Machine Control Structure). AMD:n vastaava on **VMCB**, ja
siirtymä tehdään käskyllä `vmrun`.

Luvun 2 lelusuorittimen viimeinen rivi mallinsi juuri tätä: vieraan
keskeytyslippu on vieraan omaa tilaa (VMCS:ssä), joten `CLI` ja `POPF`
eivät tarvitse hypervisoria lainkaan.

## VM exitin syyt

VMCS:n ohjauskentät valitsevat, mitkä tapahtumat aiheuttavat VM exitin.
Tavallisimmat syyt:

| Syy | Tyypillinen käsittelijä |
|-----|-------------------------|
| I/O-käsky (`in`, `out`) | emuloitu laite (QEMU) |
| EPT violation | muistiin kuvattu I/O tai sivu, jota ei vielä ole |
| `cpuid` | hypervisor näyttää valitsemansa suoritinominaisuudet |
| `hlt` | vCPU nukkuu, kunnes vieraalle tulee keskeytys |
| ulkoinen keskeytys | isännän laite tarvitsee isännän ydintä |
| MSR-luku tai -kirjoitus | esim. ajastimet ja virranhallinta |
| `vmcall` | vieraan hyperkutsu |

Yksi VM exit ja paluu vieraaseen vie nykysuorittimilla tyypillisesti
noin 1 000 kellojaksoa. Suurin osa ajasta ei kulu laitteistossa vaan
käsittelijässä, varsinkin jos käsittelijä on käyttäjätilan ohjelmassa
kuten QEMU:ssa: silloin matka kulkee vieras → isännän ydin (KVM) →
QEMU → KVM → vieras.

## Muistin virtualisointi

Vieraan käyttöjärjestelmä hallitsee omia sivutaulujaan, joissa
**vieraan virtuaaliosoite** (GVA) kuvautuu **vieraan fyysiseksi
osoitteeksi** (GPA). Vieraan fyysinen muisti on kuitenkin isännän
muistia jossain muualla, eli **isännän fyysisessä osoitteessa** (HPA).
Muunnoksia tarvitaan kaksi.

```{.dot otsikko="Kolme osoiteavaruutta ja kaksi muunnosta. Varjosivutaulu on oikotie, jonka hypervisor rakentaa ohjelmallisesti"}
digraph {
  rankdir=LR; nodesep=0.35; ranksep=0.3;
  edge [fontsize=8];
  node [fontsize=9];
  gva [label="GVA\nvieraan\nvirtuaaliosoite"];
  gpa [label="GPA\nvieraan\nfyysinen osoite"];
  hpa [label="HPA\nisännän\nfyysinen osoite"];
  gva -> gpa [label="vieraan\nsivutaulu\n(vieraan ydin)"];
  gpa -> hpa [label="EPT / NPT\n(hypervisor)"];
  gva -> hpa [label="varjosivutaulu",
              style=dashed, constraint=false];
}
```

**Varjosivutaulut** (shadow page tables) olivat ratkaisu ennen
laitteistotukea. Hypervisor rakentaa vieraan taulujen rinnalle omat
taulut, joissa GVA kuvautuu suoraan HPA:ksi, ja asettaa ne suorittimen
käyttöön. Suoritin kävelee vain yhden taulun, mutta jokainen vieraan
sivutaulun muutos on suojattava kirjoitukselta, jotta hypervisor saa
siitä ansan ja voi päivittää varjotaulun. Prosessien luonti ja
muistinhallinta aiheuttavat valtavasti VM exitejä.

**Kaksitasoiset sivutaulut** (Intel EPT, AMD NPT) siirtävät
jälkimmäisen muunnoksen laitteistolle. Hypervisor ylläpitää yhtä
taulua (GPA → HPA), ja vieras muuttaa omia taulujaan vapaasti. Hinta
maksetaan TLB-hudissa: jokainen vieraan sivutaulun alkio sijaitsee
vieraan fyysisessä muistissa, joten senkin osoite on käännettävä
EPT:llä.

## Kaksiulotteinen kävely

Seuraava ohjelma rakentaa vieraan sivutaulun ja EPT:n oikeasti ja
laskee muistiviittaukset yhdessä osoitemuunnoksessa. Jokainen
sivutaulun alkion luku on yksi viittaus:

```{.c tiedosto="esimerkit/03-sivutaulut.c" osa="lue"}
```

Vieraan kävelyssä jokaisen tason osoite käännetään ensin EPT:llä:

```{.c tiedosto="esimerkit/03-sivutaulut.c" osa="kavely"}
```

```{.tuloste tiedosto="esimerkit/03-sivutaulut.odotettu"}
```

```{.dot otsikko="Kävelyn 24 muistiviittausta suoritusjärjestyksessä, kun kummassakin taulussa on neljä tasoa. Jokainen vieraan taulun alkio (oikea sarake) on vieraan fyysisessä osoitteessa, joka on ensin käännettävä EPT:n neljän tason läpi"}
digraph {
  node [shape=plaintext, fontsize=9];
  t [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0"></td><td colspan="4" bgcolor="#d9d9d9">EPT:n tasot (GPA → HPA)</td><td bgcolor="#f3e6c8">vieraan taulun alkio</td></tr>
    <tr><td border="0"></td><td>4</td><td>3</td><td>2</td><td>1</td><td border="0"></td></tr>
    <tr><td align="left">vieraan taso 4 (juuri)</td><td>1</td><td>2</td><td>3</td><td>4</td><td bgcolor="#f3e6c8">5</td></tr>
    <tr><td align="left">vieraan taso 3</td><td>6</td><td>7</td><td>8</td><td>9</td><td bgcolor="#f3e6c8">10</td></tr>
    <tr><td align="left">vieraan taso 2</td><td>11</td><td>12</td><td>13</td><td>14</td><td bgcolor="#f3e6c8">15</td></tr>
    <tr><td align="left">vieraan taso 1</td><td>16</td><td>17</td><td>18</td><td>19</td><td bgcolor="#f3e6c8">20</td></tr>
    <tr><td align="left">datasivun GPA</td><td>21</td><td>22</td><td>23</td><td>24</td><td border="0">→ data</td></tr>
  </table>>];
}
```

Kun vieraan taulussa on $n$ tasoa ja EPT:ssä $m$, kävely vaatii
pahimmillaan $(n+1)(m+1)-1$ viittausta: neljällä tasolla 24 eikä 4.
Viisitasoisella sivutuksella lukema on 35. Siksi virtuaalikoneet
hyötyvät suurista sivuista (2 MiB ja 1 GiB) enemmän kuin
tavalliset ohjelmat: suuri sivu poistaa tason sekä vieraan taulusta
että EPT:stä, ja TLB kattaa enemmän muistia.

## Muistin ylivaraus

EPT tekee vieraan muistista isännälle tavallista virtuaalimuistia, ja
siksi hypervisor voi luvata vieraille yhteensä enemmän muistia kuin
koneessa on (*memory overcommit*). Useimmat vieraat eivät käytä koko
muistiaan yhtä aikaa. Kun muisti käy vähiin, hypervisorilla on kolme
keinoa, pehmeimmästä kovimpaan:

- **Ilmapalloajuri** (*balloon driver*, virtio-balloon). Vieraassa
  ajettava ajuri varaa vieraan ytimeltä sivuja ja kertoo
  hypervisorille, mitkä sivut se sai. Hypervisor vapauttaa niiden
  taustalla olevan isännän muistin. Vieraan oma ydin päättää, mistä
  se luopuu (ensin välimuisteista), joten keino on yhteistyötä eikä
  pakkoa.
- **Sivujen yhdistäminen** (KSM, *kernel samepage merging*). Isännän
  ydin etsii sisällöltään samat sivut ja kuvaa ne yhteen fyysiseen
  sivuun kopioi kirjoitettaessa -periaatteella. Kun kymmenen vierasta
  ajaa samaa käyttöjärjestelmää, säästö on suuri. Hinta on sivukanava:
  kirjoitus yhdistettyyn sivuun on hitaampi, joten vieras voi
  mittaamalla päätellä, onko toisella vieraalla sama sivu. Eri
  asiakkaiden koneiden välillä KSM pidetään siksi pois päältä.
- **Isännän heittovaihto.** Isäntä voi siirtää vieraan sivuja levylle
  vieraan tietämättä. Tämä on viimeinen keino, koska isäntä ei tiedä,
  mitkä sivut ovat vieraalle tärkeitä, ja vieras voi itse yrittää
  siirtää levylle sivun, jonka isäntä on jo siirtänyt: sivu luetaan
  levyltä vain, jotta se voidaan kirjoittaa sinne uudelleen.

Ylivaraus sopii ympäristöihin, joissa tiheys on tärkeämpää kuin
tasainen vasteaika (kehitys, testaus, työpöydät). Viiveherkille
tuotantokuormille muisti varataan kiinteästi ja isännän suurista
sivuista, jolloin mikään yllä olevista ei osu niihin.

## Muut arkkitehtuurit

Tämä luku käyttää Intelin nimiä, mutta rakenne on kaikissa nykyisissä
arkkitehtuureissa sama: oma suoritustila hypervisorille, vieraan tila
muistirakenteessa ja toinen osoitteenmuunnoksen taso.

| | Hypervisorin tila | Vieraan tila | Toinen muunnostaso |
|---|---|---|---|
| Intel VT-x | VMX root | VMX non-root, VMCS | EPT |
| AMD-V | isäntätila | vierastila, VMCB | NPT |
| Arm (AArch64) | EL2 | EL1 ja EL0 | stage 2 -muunnos |
| RISC-V (H-laajennus) | HS-tila | VS- ja VU-tilat | G-vaiheen muunnos (`hgatp`) |

RISC-V:n nimet jatkavat taidon *Tietokonearkkitehtuuri* M-, S- ja
U-tasoja: H-laajennus tekee S-tilasta hypervisorin tilan (HS) ja lisää
sen alle vieraan virtuaalisen S- ja U-tilan.

## TLB ja vaihdot

Kun suoritin vaihtaa vieraasta toiseen, TLB:n merkinnät eivät enää
päde. Vanhimmat toteutukset tyhjensivät TLB:n jokaisessa VM entryssä ja
exitissä. **VPID** (Intel) ja **ASID** (AMD) merkitsevät
TLB-merkinnät virtuaalikonekohtaisesti, joten tyhjennystä ei tarvita.
Sama ajatus on isännän prosesseilla nimellä PCID.

## Laitteistotuen tarkistaminen

Linuxissa suorittimen liput näkyvät tiedostossa `/proc/cpuinfo`
(`vmx` Intel, `svm` AMD), ja KVM:n käytettävyyden näkee laitteesta
`/dev/kvm`:

```text
grep -cwE 'vmx|svm' /proc/cpuinfo   # > 0: suoritin tukee
ls -l /dev/kvm                       # KVM-moduuli ladattu
```

Pilvipalvelun virtuaalikoneessa liput puuttuvat yleensä, ellei
**sisäkkäistä virtualisointia** (nested virtualization) ole sallittu.
Silloin hypervisor emuloi vieraalle VT-x:n, ja jokainen sisemmän
vieraan VM exit kulkee molempien hypervisorien kautta. Sisäkkäinen
virtualisointi toimii esimerkiksi CI-ajoissa ja kehitysympäristöissä,
mutta sen hinta on selvästi suurempi kuin yhden tason.

## Käytännössä

- **Mittaa VM exitit.** `perf kvm stat` ja KVM:n jäljityspisteet
  (`kvm:kvm_exit`) kertovat, mikä aiheuttaa exitit. Hidas
  virtuaalikone johtuu usein yhdestä syystä: emuloidusta ajastimesta,
  emuloidusta levyohjaimesta tai `hlt`-silmukasta.
- **Suuret sivut isännälle.** Kun virtuaalikoneiden muisti varataan
  isännän suurista sivuista (`hugetlbfs` tai läpinäkyvät suuret sivut),
  EPT-kävely lyhenee ja TLB-osumat lisääntyvät. Tietokannat ja
  muistipainotteiset kuormat hyötyvät eniten.
- **Älä paljasta kaikkea.** Hypervisor valitsee, mitä
  suoritinominaisuuksia vieras näkee (`cpuid`). Elävä siirto (luku 9)
  vaatii, että kohdekone tukee samoja ominaisuuksia, joten
  klustereissa vieraalle näytetään yhteinen suoritinmalli
  (esim. QEMU:n `-cpu` nimetty malli eikä `host`).
- **Sisäkkäinen virtualisointi on vara, ei oletus.** Se toimii, mutta
  jokainen exit maksaa moninkertaisesti. Testeihin se kelpaa,
  tuotantokuormaan harvoin.

## Itsearviointi

- Osaat selittää VMX root- ja non-root-tilan, VM entryn ja VM exitin
  sekä VMCS:n tehtävän.
- Osaat luetella tavallisimmat VM exitin syyt ja arvioida niiden
  hinnan.
- Osaat verrata varjosivutauluja ja EPT:tä ja laskea kaksiulotteisen
  sivutaulukävelyn muistiviittaukset.
- Osaat selittää ilmapalloajurin, sivujen yhdistämisen ja isännän
  heittovaihdon erot ja sen, miksi KSM on sivukanava.
- Osaat perustella, miksi suuret sivut ja VPID parantavat
  virtuaalikoneen suorituskykyä.
