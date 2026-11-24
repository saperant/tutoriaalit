# Virtuaalimuisti ja MMU

Tähän asti ohjelmat ovat viitanneet suoraan fyysisiin osoitteisiin.
Moniajojärjestelmässä se ei käy: jokainen prosessi olettaa omistavansa
osoitteen 0x10000, yksi virheellinen prosessi voisi kirjoittaa toisen
muistiin, ja ohjelmien yhteenlaskettu muisti saa olla suurempi kuin
fyysinen muisti. Virtuaalimuisti ratkaisee kaikki kolme: jokaisella
prosessilla on oma **virtuaalinen osoiteavaruus**, ja muistinhallintayksikkö
(MMU) muuntaa jokaisen viitteen fyysiseksi osoitteeksi käyttöjärjestelmän
ylläpitämän **sivutaulun** avulla.

Virtuaalimuisti on myös välimuisti: fyysinen muisti on välimuisti
levylle (tai pakatulle muistille). Sanasto on vain eri: lohko on
**sivu**, huti on **sivuvirhe** ja hutin käsittelee ohjelmisto, koska
levyn viive on miljoonia jaksoja.

## Sivut ja sivutaulu

Osoiteavaruus jaetaan kiinteän kokoisiin sivuihin, tavallisesti 4 KiB.
Virtuaalinen osoite on sivunumero (VPN) ja siirtymä; muunnos vaihtaa
VPN:n fyysiseksi sivunumeroksi (PPN) ja säilyttää siirtymän. Jokaisella
sivulla on oikeudet:

| Bitti | Nimi | Merkitys |
|-------|------|----------|
| V | valid | alkio on käytössä |
| R, W, X | read, write, execute | sallitut käyttötavat |
| U | user | U-tilan ohjelma saa käyttää sivua |
| G | global | kuvaus on kaikissa osoiteavaruuksissa (ydin) |
| A | accessed | sivuun on viitattu |
| D | dirty | sivuun on kirjoitettu |

A- ja D-bitit ovat käyttöjärjestelmän tietoa varten: A kertoo, mitkä
sivut ovat käytössä (sivunkorvausalgoritmi), D kertoo, onko sivu
kirjoitettava levylle ennen sen vapauttamista.

Yksitasoinen sivutaulu olisi suuri: 32-bittisessä avaruudessa on
miljoona 4 KiB:n sivua, ja taulu veisi 4 MiB prosessia kohden, vaikka
prosessi käyttäisi vain muutamaa sivua. Siksi sivutaulu on puu.

## Sv32

RISC-V:n 32-bittinen sivutus Sv32 jakaa osoitteen kahteen 10-bittiseen
VPN-kenttään ja 12-bittiseen siirtymään:

```text
 31          22 21          12 11              0
+--------------+--------------+-----------------+
|    VPN[1]    |    VPN[0]    |     siirtymä    |
+--------------+--------------+-----------------+
```

Juuritaulun fyysinen osoite on CSR-rekisterissä `satp`. VPN[1]
valitsee juuritaulusta alkion (PTE, *page table entry*). Jos alkiossa
R, W ja X ovat kaikki nollia, se osoittaa seuraavan tason tauluun,
josta VPN[0] valitsee lopullisen alkion. Jos taas R tai X on asetettu,
alkio on **lehti** jo ensimmäisellä tasolla: se kuvaa 4 MiB:n
**megasivun**. Alkion muoto ja apufunktiot:

```{.dot otsikko="Sv32:n kaksitasoinen osoitteenmuunnos"}
digraph {
  nodesep=0.4; ranksep=0.45;
  edge [fontsize=8];
  node [shape=record];
  va [label="{virtuaaliosoite|{<v1>VPN[1]|<v0>VPN[0]|<s>siirtymä}}"];
  satp [label="satp", shape=box];
  juuri [label="{<t>juuritaulu|…|<e>PTE (ei lehti)|…}"];
  taso0 [label="{<t>2. tason taulu|…|<e>PTE (lehti): PPN|…}"];
  pa [label="{fyysinen osoite|{<p>PPN|<s>siirtymä}}"];
  satp -> juuri:t;
  va:v1 -> juuri:e [label="indeksi"];
  juuri:e -> taso0:t;
  va:v0 -> taso0:e [label="indeksi"];
  taso0:e -> pa:p;
  va:s -> pa:s [label="sellaisenaan"];
}
```

```{.cpp tiedosto="esimerkit/08-sivutus.cpp" osa="pte"}
```

Muunnos on muutaman rivin silmukka, joka seuraa spesifikaation
algoritmia:

```{.cpp tiedosto="esimerkit/08-sivutus.cpp" osa="kaanna"}
```

Laitteistossa tämä on **sivutaulukävelijä** (*page table walker*), pieni
tilakone MMU:ssa. x86:ssa ja ARMissa kävely on samoin laitteistossa,
mutta MIPS ja vanhat SPARCit käsittelivät jokaisen TLB-hudin
ohjelmistolla. Esimerkki rakentaa sivutaulun ja kokeilee viittä
viitettä:

```{.cpp tiedosto="esimerkit/08-sivutus.cpp" osa="kartta"}
```

```{.tuloste tiedosto="esimerkit/08-sivutus.odotettu"}
```

Käskyn nouto koodisivulta ja talletus datasivulle kävelevät kaksi tasoa.
Megasivun lataus päättyy jo ensimmäiseen tasoon, ja siirtymä on
22-bittinen. Talletus koodisivulle hylätään, koska W-bitti puuttuu
(sivuvirhe 15, *store page fault*), ja kuvaamaton sivu antaa latauksen
sivuvirheen 13. Lopuksi data-PTE:hen on asetettu A ja D, koska siihen
kirjoitettiin.

Sivuvirhe ei ole virhe vaan pyyntö käyttöjärjestelmälle. Ydin voi:

- tuoda sivun levyltä tai pakatusta muistista (*demand paging*),
- varata nollatun sivun, kun prosessi koskee ensimmäistä kertaa
  `malloc`illa varattuun muistiin,
- kopioida sivun, joka oli jaettu `fork`in jälkeen vain luettavana
  (*copy-on-write*),
- lähettää prosessille signaalin `SIGSEGV`, jos viite oli todella
  laiton.

Sivuvirheen jälkeen käsky suoritetaan uudelleen. Siksi poikkeusten on
oltava **tarkkoja** (*precise*): kaikki edeltävät käskyt ovat
valmistuneet, eikä mikään seuraava ole muuttanut tilaa (luku 9).

## Sv39 ja suuremmat avaruudet

64-bittisessä RISC-V:ssä Sv39 käyttää kolmea 9-bittistä VPN-kenttää
(512 alkiota, yksi 4 KiB:n taulu tasoa kohden). Virtuaalinen osoite on 39
bittiä, ja bittien 63..39 on oltava bitin 38 kopioita. Tällainen
**kanoninen** osoite jakaa avaruuden kahteen puoliskoon: alaosa
käyttäjälle ja yläosa ytimelle.

```{.cpp tiedosto="esimerkit/08-sivutus.cpp" osa="sv39"}
```

Tuloste on edellisen jatkona. Sv48 ja Sv57 lisäävät neljännen ja
viidennen tason (vastaavasti x86-64:n nelitasoinen ja viisitasoinen
sivutus). Jokainen taso pidentää kävelyä yhdellä muistiviitteellä.
Sv39:ssä lehti voi olla myös 2 MiB:n tai 1 GiB:n sivu.

## TLB

Jos jokainen latauskäsky vaatisi kolme tai neljä ylimääräistä
muistiviitettä sivutaulun kävelyyn, virtuaalimuisti olisi
käyttökelvoton. **TLB** (*translation lookaside buffer*) on välimuisti
käännöksille: sen avain on VPN ja arvo PPN oikeuksineen. L1-TLB:ssä on
tyypillisesti 32–96 alkiota ja se on täysin assosiatiivinen, L2-TLB:ssä
1 000–3 000 alkiota.

Koska TLB on välimuisti, sitä voi mallintaa samalla luokalla kuin
datavälimuistia: lohko on sivu.

```{.cpp tiedosto="esimerkit/08-tlb.cpp" osa="tlb"}
```

```{.tuloste tiedosto="esimerkit/08-tlb.odotettu"}
```

Riveittäin luettuna jokainen sivu käydään läpi kerralla, ja TLB hutii
kerran 1 024 viitettä kohden. Sarakkeittain jokainen kahden rivin pari
on omalla sivullaan, ja 32-alkioinen TLB ei riitä 256 sivuun: joka
toinen viite hutii, ja jos kävely maksaa 30 jaksoa, jokainen viite
maksaa keskimäärin 15 jaksoa lisää. Megasivulla koko 1 MiB:n matriisi on
yhden TLB-alkion takana.

**TLB:n ulottuvuus** (*TLB reach*) on alkioiden määrä kertaa sivukoko:
64 × 4 KiB = 256 KiB. Jos työjoukko on suurempi, TLB-hudit voivat
maksaa enemmän kuin välimuistihudit. Suuret sivut (Linuxissa
*transparent huge pages* ja `hugetlbfs`) ovat tietokantojen,
virtuaalikoneiden ja tieteellisen laskennan tavallinen optimointi.

## Osoiteavaruuden vaihto

Kun käyttöjärjestelmä vaihtaa prosessia, se kirjoittaa `satp`-rekisteriin
uuden juuritaulun. TLB:n vanhat käännökset ovat silloin vääriä. Ilman
lisätietoa koko TLB on tyhjennettävä (`sfence.vma`), mikä tekee
prosessinvaihdosta kalliin. Siksi `satp` sisältää myös
**ASID**-kentän (*address space identifier*): TLB-alkioon tallennetaan
ASID, ja käännös kelpaa vain samalle ASID:lle. G-bitillä merkityt
ytimen sivut kelpaavat kaikille.

Virtualisoinnissa (taito *Virtualisointi*) muunnoksia on kaksi
sisäkkäin: vieraan virtuaalinen → vieraan fyysinen → isännän fyysinen.
Pahimmillaan nelitasoinen kävely kummallakin tasolla vaatii 24
muistiviitettä, ja TLB-osumien merkitys kasvaa entisestään.

## Välimuisti ja käännös yhtä aikaa

L1-välimuistin pitäisi saada fyysinen osoite, mutta TLB-haku vie oman
aikansa. Tavallinen ratkaisu on **VIPT** (*virtually indexed,
physically tagged*): välimuistin indeksi otetaan virtuaalisen osoitteen
siirtymäbiteistä, jotka eivät muutu käännöksessä, ja tagi verrataan
fyysiseen osoitteeseen, kun TLB on vastannut. Haku ja käännös tapahtuvat
rinnakkain. Rajoitus: indeksi ja lohkon siirtymä yhdessä saavat olla
enintään 12 bittiä, joten L1:n koko on enintään teiden määrä × 4 KiB.
Tästä johtuu, että 32 KiB:n L1 on tyypillisesti 8-tiinen ja 48 KiB:n
12-tiinen. Applen M-sarjan 16 KiB:n sivut sallivat 128 KiB:n L1:n.

## Käytännössä

- **Varattu muisti ei ole vielä muistia.** `malloc` ja `mmap` varaavat
  vain virtuaalisia osoitteita. Fyysinen sivu syntyy ensimmäisessä
  sivuvirheessä. Tästä johtuvat suuren taulukon ensikosketuksen
  hitaus ja ylivaraus (*overcommit*).
- **Suuret sivut suurille työjoukoille.** Jos `perf stat -e
  dTLB-load-misses` näyttää paljon huteja, kokeile `madvise(...,
  MADV_HUGEPAGE)` tai käännöksen ajaksi THP:n pakottamista.
- **Sivuvirheet ovat kalliita.** Pieni sivuvirhe maksaa mikrosekunnin,
  suuri (levyltä) millisekunteja; `perf stat -e page-faults` kertoo määrän.
- **NUMA ja sivut.** Fyysinen sivu sijoitetaan sen solmun muistiin, jonka
  ydin koskee siihen ensin (*first touch*, luku 10).

## Itsearviointi

- Osaat kävellä Sv32-sivutaulun käsin: jakaa osoitteen kenttiin, laskea
  PTE:n osoitteet ja koota fyysisen osoitteen.
- Osaat kertoa, mitä käyttöjärjestelmä tekee sivuvirheessä, ja selittää
  copy-on-write-mekanismin.
- Osaat laskea TLB:n ulottuvuuden ja perustella suurten sivujen hyödyn.
- Osaat selittää VIPT-välimuistin ja sen kokorajoituksen.
