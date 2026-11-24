# Liukuhihna

Liukuhihna (*pipeline*) limittää käskyjen suorituksen: kun yksi käsky on
suoritusvaiheessa, seuraava on purussa ja sitä seuraava noudossa. Kukin
käsky vie yhä viisi vaihetta, mutta joka jakso valmistuu yksi käsky.
Ihanteellisesti viisivaiheinen liukuhihna on viisi kertaa yksijaksoista
nopeampi, koska jakso on viidesosa ja CPI on edelleen 1.

Käytännössä ihanne ei toteudu kolmesta syystä:

1. **Epätasaiset vaiheet.** Jakso on hitaimman vaiheen mittainen.
   Edellisen luvun viiveillä se on 200 ps eikä 800/5 = 160 ps.
2. **Vaiherekisterit.** Jokaisen vaiheen perään tulee rekisteri, jonka
   asettumis- ja viiveaika (noin 20–30 ps) lisätään jokaiseen jaksoon.
3. **Riippuvuudet** (*hazards*). Käsky ei aina voi edetä, koska sen
   tarvitsema arvo, laitteisto tai seuraavan käskyn osoite ei ole vielä
   valmis. Silloin liukuhihna pysähtyy, ja CPI kasvaa yli yhden.

Tämä luku käsittelee riippuvuudet ja niiden ratkaisut.

## Riippuvuuksien lajit

| Laji | Syy | Ratkaisu |
|------|-----|----------|
| Rakenteellinen | kaksi käskyä tarvitsee samaa laitetta | lisää laitteistoa (erilliset muistit, monta porttia) |
| Data (RAW) | käsky lukee arvon, jota edellinen ei ole kirjoittanut | eteenpäinkytkentä, pysähdys, uudelleenjärjestys |
| Ohjaus | seuraavan käskyn osoite riippuu haarasta | ennustus (luku 5), pysähdys |

Viisivaiheisessa järjestyksessä etenevässä liukuhihnassa (*in-order*)
rakenteellisia riippuvuuksia ei synny, koska käsky- ja datamuisti ovat
erilliset ja rekisteritiedostossa on kaksi lukuporttia ja yksi
kirjoitusportti. Rekisteritiedosto kirjoitetaan jakson alkupuoliskolla
ja luetaan loppupuoliskolla, joten WB- ja ID-vaihe voivat käsitellä
samaa rekisteriä samassa jaksossa.

Datariippuvuuksista vain RAW (*read after write*, todellinen riippuvuus)
haittaa tällaista liukuhihnaa. WAR- ja WAW-riippuvuudet (*write after
read*, *write after write*) syntyvät vasta, kun käskyjä suoritetaan
epäjärjestyksessä (luku 11).

## Ajoitusmalli

Simulaattorin liukuhihnamalli laskee jokaiselle käskylle jakson, jossa
se noudetaan, ja jakson, jossa se on EX-vaiheessa. Kaikki muu seuraa
näistä: purku on EX:ää edeltävä jakso, MEM ja WB kaksi seuraavaa.

```{.cpp tiedosto="esimerkit/yhteinen/liukuhihna.hpp" osa="malli"}
```

Malli toteuttaa kolme sääntöä:

1. Käsky noudetaan jaksoa edellisen jälkeen, ellei edellinen ollut
   väärin ennustettu haara tai hyppy, jolloin nouto alkaa vasta, kun
   kohde on tiedossa.
2. Käsky pääsee EX-vaiheeseen aikaisintaan kaksi jaksoa noudon jälkeen
   ja aikaisintaan jaksoa edellisen käskyn jälkeen (järjestys säilyy).
3. Käsky pääsee EX-vaiheeseen vasta, kun sen operandit ovat valmiit.
   Eteenpäinkytkennän kanssa laskutoimituksen tulos on valmis seuraavassa
   jaksossa ja latauksen tulos MEM-vaiheen jälkeen. Ilman kytkentää arvo
   kulkee rekisteritiedoston kautta: se kirjoitetaan WB:ssä ja luetaan
   samassa jaksossa ID:ssä, joten käyttäjän EX on aikaisintaan jaksoa WB:n
   jälkeen.

Jälkiohjattu malli on yksinkertainen, koska se ei tarvitse oikeita
vaiherekisterejä eikä dataa. Se tuottaa silti samat jaksot kuin
RTL-tason toteutus, kunhan säännöt vastaavat laitteiston pysäytys- ja
kytkentälogiikkaa. Tämä on yleinen tapa tutkia suunnitteluvaihtoehtoja
ennen kuin mitään rakennetaan.

## Eteenpäinkytkentä

Ilman eteenpäinkytkentää jokainen RAW-riippuvuus vierekkäisten käskyjen
välillä maksaa kaksi jaksoa. Kaavio näyttää `summa`-ohjelman
summaussilmukan ensimmäisen kierroksen:

```{.cpp tiedosto="esimerkit/04-kaavio.cpp" osa="kaavio"}
```

```{.tuloste tiedosto="esimerkit/04-kaavio.odotettu"}
```

`**` tarkoittaa, että käsky odottaa. ID:n jälkeen se odottaa
dekoodausvaiheessa operandiaan, ennen ID:tä se odottaa noudossa, koska
edellinen käsky on vielä ID:ssä. Ilman kytkentää kierros vie
21 jaksoa, ja jokainen silmukan käsky riippuu edellisestä: `add t2`
tarvitsee `slli`:n tuloksen, `lw` `add`:n tuloksen ja niin edelleen.

Eteenpäinkytkentä (*forwarding*, *bypassing*) vie tuloksen suoraan
ALU:n ulostulosta seuraavan käskyn ALU:n sisäänmenoon, ohi
rekisteritiedoston. Laitteistossa se on kaksi multiplekseriä ALU:n
eteen ja vertailijat, jotka tarkistavat, onko EX/MEM- tai
MEM/WB-vaiherekisterissä oleva rd sama kuin EX-vaiheen käskyn rs1 tai
rs2:

```text
jos EX/MEM.kirjoittaa ja EX/MEM.rd != 0 ja EX/MEM.rd == ID/EX.rs1:
    A-operandi = EX/MEM.tulos          (edellisen käskyn tulos)
muuten jos MEM/WB.kirjoittaa ja MEM/WB.rd != 0 ja MEM/WB.rd == ID/EX.rs1:
    A-operandi = MEM/WB.tulos          (kahden käskyn takaa)
muuten:
    A-operandi = ID/EX.rs1-arvo        (rekisteritiedostosta)
```

Järjestys on tärkeä: tuoreempi arvo voittaa. Ehto `rd != 0` estää
x0:aan "kirjoitetun" arvon kytkemisen.

Kytkennän kanssa sama kierros vie 14 jaksoa, ja ainoa pysähdys on
latauksen ja sen käytön välissä. Lisäksi `blt` toteutuu, mutta malli
ennusti sen toteutumattomaksi, joten seuraava `slli` noudetaan vasta,
kun haara on ratkennut EX-vaiheessa: kaksi jaksoa hukkaan. Siitä
luvussa 5.

## Latauksen käyttö

Latauksen tulos on valmis vasta MEM-vaiheen lopussa, kun seuraava käsky
on jo EX-vaiheessa. Kytkentä ei voi viedä arvoa ajassa taaksepäin, joten
*load–use*-riippuvuus maksaa yhden jakson silloinkin. Laitteistossa
riippuvuuden havaitsee *hazard detection unit* ID-vaiheessa: jos
ID/EX-rekisterissä on lataus, jonka rd on purettavan käskyn rs1 tai rs2,
PC:n ja IF/ID-rekisterin päivitys estetään yhdeksi jaksoksi ja EX:ään
syötetään kupla (nop).

Pysähdyksen voi välttää siirtämällä latauksen ja käytön väliin
riippumattoman käskyn. Kääntäjät tekevät tätä *käskyjen ajoituksena*
(instruction scheduling). Esimerkki vertaa kolmea versiota samasta
silmukasta:

```{.cpp tiedosto="esimerkit/04-jarjestys.cpp" osa="versiot"}
```

```{.tuloste tiedosto="esimerkit/04-jarjestys.odotettu"}
```

Alkuperäinen versio pysähtyy 200 kertaa, kerran jokaisella kierroksella.
Kun `addi t0, t0, 1` siirretään latauksen ja käytön väliin, pysähdykset
katoavat ja CPI laskee 1,08:sta 1,01:een. Osoitinversio vähentää lisäksi
käskyjä: indeksin kertominen neljällä ja lisääminen kantaosoitteeseen
korvataan osoittimen kasvatuksella. Tämä *voiman vähennys* (strength
reduction) on rautalain toinen tekijä: CPI pysyy samana, mutta
käskymäärä laskee 14 %. Ohjauspysähdykset (12 jaksoa) ovat kuusi
ennustusvirhettä: kaksibittinen ennustin (luku 5) erehtyy kummankin
silmukan haarassa kahdesti alussa ja kerran lopussa.

## Liukuhihnan syvyys

Jos viisi vaihetta on hyvä, eikö kaksikymmentä olisi parempi? Jakso
lyhenee, mutta kolme asiaa huononee:

- Vaiherekisterien kiinteä viive muodostaa yhä suuremman osan jaksosta.
- Haaran väärän ennusteen hinta kasvaa, koska haara ratkeaa
  myöhemmässä vaiheessa. 20-vaiheisessa liukuhihnassa virhe maksaa
  15–20 jaksoa.
- Latausten ja muiden monijaksoisten operaatioiden viive jaksoina
  kasvaa, joten riippuvuudet maksavat enemmän.

Intel Pentium 4 (2000–2008) vei syvyyden äärimmilleen: Prescott-ytimessä
oli 31 vaihetta, ja tavoitteena oli 10 GHz. Kellotaajuus jäi alle
4 GHz:n tehonkulutuksen vuoksi, ja IPC oli huonompi kuin edeltäjällä.
Seuraava Core-arkkitehtuuri palasi noin 14 vaiheeseen. Nykyiset
suorituskykyiset ytimet ovat 10–20 vaiheen välillä, energiatehokkaat
sulautetut ytimet 2–8.

Optimaalinen syvyys on kompromissi: jos $t$ on logiikan kokonaisviive,
$o$ vaiherekisterin viive ja $p$ pysähdysten määrä per käsky
vaihetta kohden, jakso on $t/n + o$ ja CPI noin $1 + p \cdot n$.
Tulo minimoituu, kun $n = \sqrt{t / (o \cdot p)}$: halpa vaiherekisteri
ja harvat pysähdykset sallivat syvemmän liukuhihnan.

## Käytännössä

- **Load–use on kaikkialla.** Jokainen ydin, myös suurin
  epäjärjestyksessä suorittava, maksaa latauksen viiveen, jos tulosta
  tarvitaan heti. L1-osuman viive on nykyisissä x86-ytimissä 4–5 jaksoa.
  Kääntäjä ajoittaa käskyt piilottaakseen sen, ja silmukoiden
  avaaminen (*loop unrolling*) antaa sille enemmän siirreltävää.
- **Älä optimoi käsin, mitä kääntäjä tekee.** `-O2` ajoittaa käskyt
  kohdeprosessorin mallin mukaan (`-mtune`). Käsin kirjoitetussa
  assemblyssä ajoitus on sinun tehtäväsi.
- **Riippuvuusketjut ratkaisevat.** Silmukka, jonka jokainen kierros
  riippuu edellisestä (summa, osoitinjahti), ei nopeudu leveämmällä
  laitteistolla. Useampi riippumaton akku (`summa1 += a[i]; summa2 +=
  a[i+1]`) katkaisee ketjun.
- **Haaraviiveaukot olivat virhe.** MIPS ja SPARC suorittivat haaran
  jälkeisen käskyn aina (*delay slot*), jotta yksi jakso ei menisi
  hukkaan. Se sitoi käskykannan viisivaiheiseen liukuhihnaan, ja
  myöhemmille toteutuksille siitä oli vain haittaa. RISC-V:ssä
  viiveaukkoja ei ole.

## Itsearviointi

- Osaat piirtää viisivaiheisen liukuhihnan kaavion käskyjonolle ja
  merkitä pysähdykset ilman eteenpäinkytkentää ja sen kanssa.
- Osaat kirjoittaa eteenpäinkytkennän ja load–use-havainnon ehdot
  vaiherekisterien kentillä.
- Osaat järjestää käskyt uudelleen niin, että latauksen käytön pysähdys
  katoaa, ja arvioida muutoksen CPI:hin.
- Osaat perustella, miksi liukuhihnan syventäminen ei kasvata
  suorituskykyä rajattomasti.
