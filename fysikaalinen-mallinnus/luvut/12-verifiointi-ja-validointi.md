# Verifiointi ja validointi

Jokainen edellisten lukujen tulos tarkistettiin jotain vasten: tarkkaa
ratkaisua, tasetta, toista toteutusta tai kirjallisuusarvoa. Tämä luku
kokoaa tarkistukset järjestelmäksi ja lisää kolme menetelmää, joita
tarvitaan, kun tarkkaa ratkaisua ei ole. Kysymyksiä on kaksi, ja ne
pidetään erillään:

- **Verifiointi:** ratkaistaanko yhtälöt oikein? Tämä on matematiikkaa
  ja ohjelmointia. Vertailukohta on yhtälön tarkka ratkaisu.
- **Validointi:** ratkaistaanko oikeat yhtälöt? Tämä on fysiikkaa.
  Vertailukohta on mittaus.

Järjestyksellä on väliä. Jos validoimaton koodi osuu mittaukseen,
syynä voi olla kahden virheen kumoutuminen, ja seuraavassa tapauksessa
ne eivät enää kumoudu.

```{.dot otsikko="Virhelähteet todellisuuden ja lasketun luvun välillä ja tarkistus, joka kohdistuu kuhunkin."}
digraph {
  node [shape=box];
  ranksep=0.2;
  tod [label="todellisuus"];
  malli [label="matemaattinen malli"];
  disk [label="diskreetti malli"];
  koodi [label="ohjelma"];
  tulos [label="tulos"];
  tod -> malli [label="  mallivirhe (oletukset, parametrit)"];
  malli -> disk [label="  diskretointivirhe"];
  disk -> koodi [label="  ohjelmointivirhe"];
  koodi -> tulos [label="  pyöristys, ratkaisijan toleranssi"];
  node [shape=plaintext];
  v1 [label="validointi:\nvertailu mittaukseen"];
  v2 [label="ratkaisun verifiointi:\nverkkosuppeneminen"];
  v3 [label="koodin verifiointi:\nvalmistettu ratkaisu"];
  {rank=same; v1; malli}
  {rank=same; v2; disk}
  {rank=same; v3; koodi}
  v1 -> malli [style=dotted, arrowhead=none];
  v2 -> disk [style=dotted, arrowhead=none];
  v3 -> koodi [style=dotted, arrowhead=none];
}
```

## Koodin verifiointi: valmistettu ratkaisu

Kertaluvun mittaaminen on ollut tutoriaalin tärkein tarkistus, mutta se
vaatii tehtävän, jonka ratkaisu tunnetaan. Tarkkoja ratkaisuja on vain
yksinkertaisille tapauksille: vakiokertoimet, suorakulmainen alue,
siistit reunaehdot. Juuri niissä ohjelman mutkikkaimmat osat jäävät
käyttämättä.

**Valmistetun ratkaisun menetelmä** (*method of manufactured
solutions*) kääntää asetelman. Ratkaisu keksitään ensin, ja siitä
lasketaan, millainen lähdetermi sen tuottaisi:

1. Valitaan ratkaisu $u_m$. Sen pitää olla sileä ja riittävän
   monimutkainen, jotta mikään termi ei häviä: ei polynomi, jonka
   menetelmä esittää tarkasti.
2. Sijoitetaan $u_m$ yhtälön vasempaan puoleen ja lasketaan
   lähdetermi $f$ symbolisesti. Reunaehdot otetaan samasta funktiosta.
3. Ajetaan ohjelma lähteellä $f$ usealla verkolla ja mitataan virheen
   kertaluku.

Ratkaisun ei tarvitse olla fysikaalisesti mielekäs. Ohjelma ei tiedä,
onko lähde luonnollinen, ja jos se ratkaisee tämän tehtävän oikealla
kertaluvulla, se käsittelee jokaisen termin oikein.

Esimerkin yhtälössä $-(k u')' + c\,u = f$ johtavuus riippuu paikasta.
SymPy laskee lähdetermin:

```{.python tiedosto="esimerkit/12-valmistettu.py" osa="valmistus"}
```

Ratkaisija on luvun 3 säilyvä differenssikaava. Siihen on tehty
tahallinen virhe, jonka voi kytkeä päälle: oikeanpuoleisen rajapinnan
johtavuus luetaan solmusta eikä välin keskipisteestä. Kyse on puolen
hilavälin indeksivirheestä, jollaisia syntyy helposti.

```{.python tiedosto="esimerkit/12-valmistettu.py" osa="ratkaisija"}
```

```{.python tiedosto="esimerkit/12-valmistettu.py" osa="kertaluku"}
```

```{.tuloste tiedosto="esimerkit/12-valmistettu.odotettu"}
```

Oikea koodi on toista kertalukua. Virheellisen koodin virhe on
karkeimmalla hilalla 0,06, kun ratkaisun arvot ovat ykkösen luokkaa:
tulos näyttäisi kuvaajassa järkevältä, eikä yksittäinen ajo paljastaisi
mitään. Kertaluku paljastaa. Virhe ei pienene hilaa tihentämällä, vaan
jää arvon 0,036 tuntumaan, koska ohjelma ratkaisee tarkasti väärää
yhtälöä.

Menetelmän voima on tässä: se muuttaa kysymyksen "näyttääkö tulos
oikealta" kysymykseksi "onko kaltevuus kaksi", johon on yksiselitteinen
vastaus. Kertaluvun pitää olla täsmälleen teorian mukainen. Arvo 1,7
ei ole "melkein kaksi" vaan merkki siitä, että jokin termi tai
reunaehto on väärää kertalukua.

## Ratkaisun verifiointi: Richardsonin ekstrapolointi

Kun koodi on verifioitu, jäljelle jää kysymys, kuinka suuri
diskretointivirhe on juuri tässä laskussa, jonka tarkkaa ratkaisua ei
tunneta. Vastaus saadaan kolmesta verkosta.

Oletetaan, että kiinnostava suure $Q$ käyttäytyy kuten $Q(h) = Q_0 +
Ch^p$. Kolme tuntematonta ($Q_0$, $C$, $p$) ratkeavat kolmesta
laskusta. Kun verkot on tihennetty suhteessa 2 ja tulokset ovat
$Q_1$, $Q_2$ ja $Q_3$ karkeimmasta tiheimpään,

$$p = \log_2\frac{Q_2 - Q_1}{Q_3 - Q_2}, \qquad
  Q_0 \approx Q_3 + \frac{Q_3 - Q_2}{2^p - 1}.$$

Ensimmäinen kaava on **havaittu kertaluku** ja toinen **Richardsonin
ekstrapolointi**. Insinöörikäytössä virhearvio ilmoitetaan
**verkkosuppenemisindeksinä** (*grid convergence index*, GCI), joka on
ekstrapoloidun ja tiheimmän tuloksen suhteellinen ero kerrottuna
varmuuskertoimella 1,25 (Roache, 1994).

```{.python tiedosto="esimerkit/12-gci.py" osa="gci"}
```

Esimerkkitehtävä on L-alue, jossa on tasainen lähde ja nollareuna.
Tarkkaa ratkaisua ei ole. Suureita on kaksi: ratkaisun integraali
alueen yli ja suurin gradientti.

```{.python tiedosto="esimerkit/12-gci.py" osa="suureet"}
```

```{.python tiedosto="esimerkit/12-gci.py" osa="koe"}
```

```{.tuloste tiedosto="esimerkit/12-gci.odotettu"}
```

![Ratkaisun integraali neljällä verkolla ja ekstrapolointi nollaan.
Katkoviiva on kolmeen tiheimpään pisteeseen sovitettu
malli.](kuvat/richardson.png){width=62%}

Integraali suppenee. Havaittu kertaluku on noin 1,7 eikä 2, mikä
kertoo nurkan singulariteetista, mutta arvio toimii silti: kahdesta eri
verkkokolmikosta ekstrapoloidut arvot ovat samat neljän numeron
tarkkuudella, ja tiheimmän verkon arvioitu virhe on 0,13 prosenttia.
Tulos voidaan raportoida muodossa 0,2140 ± 0,0003.

Suurin gradientti ei suppene. Arvot kasvavat joka tihennyksellä
suunnilleen samalla kertoimella, ja ohjelma kieltäytyy antamasta
arviota. Tämä on oikea käytös: suure on singulaarinen, eikä sillä ole
raja-arvoa. Luvun 9 ulokepalkin kiinnitysjännitys käyttäytyi samoin.

Menetelmällä on kolme ehtoa, jotka kannattaa tarkistaa joka kerta.
Verkkojen pitää olla **asymptoottisella alueella** eli niin tiheitä,
että virhe todella käyttäytyy kuten $h^p$: merkki on, että kahdesta
kolmikosta saadaan sama kertaluku. Tihennyksen pitää olla
systemaattinen, eli jokaisen verkon pitää olla edellisen tihennys
kaikkialla. Ja muiden virheiden (ratkaisijan toleranssi, pyöristys,
aika-askel) pitää olla selvästi pienempiä kuin erot verkkojen välillä.

## Validointi: malli vastaan mittaus

Verifioitu ratkaisu vastaa tarkasti yhtälöihin. Validointi kysyy,
kuvaavatko yhtälöt kappaletta. Siihen tarvitaan mittaus, ja
vertailussa on kolme virhelähdettä, jotka pitää erottaa toisistaan:
diskretointivirhe, parametrien epävarmuus ja mallin muodon virhe.

Esimerkin koe on terästanko, jonka toinen pää pidetään 100 asteessa
ja johon on kiinnitetty kuusi lämpötila-anturia. Oikeaa koetta ei
tässä ole käytettävissä, joten mittaustulokset on tuotettu
ohjelmallisesti rikkaammasta mallista, jossa on konvektion lisäksi
lämpösäteily, ja niihin on lisätty kohinaa. Kokeen tekijä tietää
tämän, mallintaja ei.

```{.python tiedosto="esimerkit/12-validointi.py" osa="koe"}
```

Mallintajan malli on johdannon jäähdytysripa: pelkkä konvektio,
lämmönsiirtokerroin käsikirjasta.

```{.python tiedosto="esimerkit/12-validointi.py" osa="malli"}
```

```{.python tiedosto="esimerkit/12-validointi.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/12-validointi.odotettu" rivit="1-9"}
```

Ensimmäinen rivi sulkee pois diskretointivirheen: se on kymmenestuhannesosa
astetta, eikä verkon tihentäminen muuta mitään. Tämä on tehtävä ensin,
jotta numeerista virhettä ei sekoiteta muihin.

Toinen vaihe kuljettaa parametrin epävarmuuden mallin läpi. Käsikirjan
lämmönsiirtokerroin on tyypillisesti tarkka ehkä kolmenkymmenen
prosentin sisällä, ja se tuottaa ennusteeseen useiden asteiden
vaihteluvälin. Silti jokainen mittaus on välin alapuolella, ja ero on
samaan suuntaan kaikissa antureissa. Systemaattinen poikkeama, joka ei
mahdu parametrien epävarmuuteen, viittaa **mallin muodon virheeseen**:
tangosta poistuu lämpöä tavalla, jota mallissa ei ole.

Houkutteleva korjaus on sovittaa parametri mittauksiin.

```{.python tiedosto="esimerkit/12-validointi.py" osa="kalibrointi"}
```

```{.tuloste tiedosto="esimerkit/12-validointi.odotettu" alkaen="3. sovitettu"}
```

![Vasemmalla mittaukset, käsikirja-arvon vaihteluväli ja sovitettu
malli. Oikealla sama sovitettu malli uudessa tilanteessa, jossa tyvi
on 300 °C.](kuvat/validointi.png){width=95%}

Sovitettu kerroin 14,3 toistaa mittaukset kohinan tarkkuudella, ja
malli näyttää validoidulta. Se ei ole. Sovitus on piilottanut puuttuvan
säteilyn parametriin, jonka arvo ei enää vastaa mitään fysikaalista
suuretta. Kun samaa mallia käytetään uudessa tilanteessa, tyven ollessa
300-asteinen, se ennustaa keskimäärin seitsemän astetta liian kuumaa.
Säteilyn osuus häviöstä on kasvanut 43 prosentista 64 prosenttiin, koska
säteily riippuu lämpötilan neljännestä potenssista, ja vakiokertoiminen
malli ei voi seurata sitä.

Tästä seuraa validoinnin perussääntö: **kalibrointi ja validointi
tehdään eri aineistoilla**. Malli, joka on sovitettu mittauksiin,
toistaa ne määritelmän mukaan. Validointia on vain ennuste, joka
tehdään ennen vertailua tilanteessa, jota sovituksessa ei käytetty. Ja
malli on validoitu vain sillä alueella, jolla sitä on verrattu
mittauksiin: tässä 100 asteessa, ei 300:ssa.

## Käytännössä

- **Verifioi ennen kuin validoit.** Ensin koodi (valmistettu ratkaisu,
  kertaluku), sitten laskun diskretointivirhe (kolme verkkoa), vasta
  sitten vertailu mittaukseen.
- **Rakenna tarkistukset testeiksi.** Kertalukutesti, paikkatesti ja
  tasetesti ajetaan automaattisesti jokaisen muutoksen jälkeen.
  Tämän tutoriaalin esimerkit ovat sellaisia testejä.
- **Ilmoita tulos virhearvion kanssa.** Luku ilman tietoa siitä,
  kuinka paljon se muuttuu verkkoa tihennettäessä, ei ole tulos.
- **Epäile sopivaa tulosta.** Hyvä osuma mittaukseen yhdellä verkolla
  ja sovitetuilla parametreilla ei kerro mitään. Kysy, mitä mallia
  sovitettiin mihin aineistoon.
- **Pidä kirjaa oletuksista.** Jokainen malli on voimassa vain
  oletustensa alueella: lineaarinen aine, pienet siirtymät, vakio
  lämmönsiirtokerroin. Kirjaa ne tuloksen viereen.
- **Parametrien epävarmuus on usein suurin virhe.** Lämmönsiirtokertoimet,
  kitkat, liitosten jäykkyydet ja kuormat tunnetaan huonosti. Verkon
  hiominen promillen tarkkuuteen on turhaa, jos lähtötieto on
  kymmenen prosentin tarkkuudella.
- **Herkkyystarkastelu kertoo, mihin kannattaa panostaa.** Muuta
  yhtä parametria kerrallaan epävarmuutensa verran ja katso, mikä
  liikuttaa tulosta eniten. Mittaa se tarkemmin.

## Itsearviointi

- Osaat erottaa verifioinnin ja validoinnin ja kertoa, miksi ne
  tehdään tässä järjestyksessä.
- Osaat laatia valmistetun ratkaisun, johtaa siitä lähdetermin ja
  käyttää kertalukua koodin virheen etsimiseen.
- Osaat laskea kolmesta verkosta havaitun kertaluvun, ekstrapoloidun
  arvon ja virhearvion sekä tunnistaa suureen, joka ei suppene.
- Osaat erottaa vertailussa diskretointivirheen, parametrien
  epävarmuuden ja mallin muodon virheen.
- Osaat selittää, miksi mittauksiin sovitettu malli ei ole validoitu
  ja miten validointi tehdään oikein.
