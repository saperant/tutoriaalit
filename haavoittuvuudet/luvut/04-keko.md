# Kekovirheet

Keko on dynaamisen muistin alue, jota `malloc` ja `free` hallitsevat.
Sen virheet ovat pinovirheitä vaikeampia löytää, koska seuraus näkyy
usein kaukana syystä: ylivuoto korruptoi naapurivarauksen, joka
käytetään vasta myöhemmin, ja vapautettu muisti annetaan uudelleen
jollekin toiselle. Tämä luku käsittelee kolme yleisintä virhettä:
ylivuodon, käytön vapautuksen jälkeen (*use-after-free*) ja
kaksoisvapautuksen (*double free*).

## Ylivuoto keossa

Istunnolle varataan 16 tavun muistiinpanokenttä, mutta kopiointi ottaa
koko merkkijonon:

```{.c tiedosto="esimerkit/04-keko/istunnot.c" osa="ylivuoto"}
```

```{.tuloste tiedosto="esimerkit/04-keko/odotettu" osa="t2"}
```

Raportti kertoo varauksen koon ja paikan, joten virheellinen oletus
löytyy suoraan: kenttä on 16 tavua, mutta siihen kopioidaan 37.

## Keon metatiedot

glibc:n varaaja pitää jokaisen varauksen edellä 8 tavun kenttää, jossa
on lohkon koko ja tilabittejä. Kenttää ei näe C:stä, mutta gdb:llä sen
voi lukea:

```{.text tiedosto="esimerkit/04-keko/metatiedot.gdb" osa="metatiedot"}
```

```{.tuloste tiedosto="esimerkit/04-keko/odotettu" osa="t5"}
```

```{.dot otsikko="Kaksi peräkkäistä 32 tavun lohkoa ennen kopiointia ja sen jälkeen. 37 tavun kopiointi täyttää oman lohkonsa ja jatkaa naapurin koko-kenttään ja dataan (punaiset)."}
digraph {
  nodesep=0.35;
  node [shape=plain, style=""];
  ennen [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
    <tr><td border="0" align="left" colspan="4"><i>ennen</i></td></tr>
    <tr><td bgcolor="#EEF1F6" width="70">koko 0x21<br/><font point-size="8">8 tavua</font></td><td width="90">kentta<br/><font point-size="8">pyydetty 16, käytössä 24</font></td><td bgcolor="#EEF1F6" width="70">koko 0x21<br/><font point-size="8">8 tavua</font></td><td width="90">seuraava (istunto)<br/><font point-size="8">24 tavua</font></td></tr>
    <tr><td border="0" colspan="2"><font point-size="8">lohko 1: 32 tavua</font></td><td border="0" colspan="2"><font point-size="8">lohko 2: 32 tavua</font></td></tr>
  </table>>];
  jalkeen [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
    <tr><td border="0" align="left" colspan="4"><i>37 tavun kopioinnin jälkeen</i></td></tr>
    <tr><td bgcolor="#EEF1F6" width="70">koko 0x21<br/><font point-size="8">ennallaan</font></td><td bgcolor="#F6D5D5" width="90">muistiinpanon alku<br/><font point-size="8">24 tavua</font></td><td bgcolor="#F6D5D5" width="70">"hdu kent"<br/><font point-size="8">koko-kenttä tuhottu</font></td><td bgcolor="#F6D5D5" width="90">5 tavua tekstiä + vanha data<br/><font point-size="8">istunnon alku tuhottu</font></td></tr>
  </table>>];
  ennen -> jalkeen [style=invis];
}
```

16 tavun pyyntö saa 32 tavun lohkon (`0x20`): 8 tavua metatietoa ja
tasaus 16 tavuun. Alin bitti (`0x1`) kertoo, että edellinen lohko on
käytössä. Seuraava varaus alkaa 32 tavun päästä, ja kopiointi
ylikirjoitti sen koko-kentän tekstillä. Kun varaaja myöhemmin käsittelee
tätä lohkoa, se luottaa kenttään. Juuri siksi keon ylivuoto on
vaarallinen: se ei korruptoi vain dataa vaan varaajan omaa
kirjanpitoa, ja varaaja tekee sen perusteella omia kirjoituksiaan.

Varaajat puolustautuvat: glibc tarkistaa koko-kentän järkevyyden,
vapaiden lohkojen listojen eheyden ja salaa vapaiden lohkojen
osoittimet (*safe-linking*, glibc 2.32). Tarkistukset havaitsevat osan
korruptiosta ja lopettavat ohjelman, mutta eivät kaikkea. Ainoa varma
suoja on, ettei ylivuotoa tapahdu.

## Käyttö vapautuksen jälkeen

Uloskirjautuminen vapauttaa istunnon, mutta toinen osoitin jää
talteen:

```{.c tiedosto="esimerkit/04-keko/istunnot.c" osa="vapautettu"}
```

GCC huomaa näin yksinkertaisen tapauksen jo käännöksessä:

```{.bash tiedosto="esimerkit/04-keko/aja.sh" osa="varoitus"}
```

```{.tuloste tiedosto="esimerkit/04-keko/odotettu" osa="t1"}
```

Oikeissa ohjelmissa vapautus ja käyttö ovat eri funktioissa, eri
säikeissä tai eri tapahtumankäsittelijöissä, eikä kääntäjä näe niitä
yhdessä. ASan näkee: vapautettu muisti merkitään käyttökelvottomaksi ja
pidetään karanteenissa, jottei sitä anneta heti uudelleen.

```{.tuloste tiedosto="esimerkit/04-keko/odotettu" osa="t3"}
```

Raportissa on kolme pinoa: missä vapautettua muistia luettiin, missä se
vapautettiin ja missä se alun perin varattiin. Ne kertovat yhdessä,
kenen olisi pitänyt tietää, että muisti ei ole enää käytettävissä.

Miksi virhe on vakava, vaikka luettu arvo olisi vain roskaa? Varaaja
antaa vapautetun lohkon seuraavalle samankokoiselle pyynnölle:

```{.c tiedosto="esimerkit/04-keko/istunnot.c" osa="uudelleenkaytto"}
```

```{.tuloste tiedosto="esimerkit/04-keko/odotettu" osa="t6"}
```

```{.dot otsikko="Käyttö vapautuksen jälkeen aikajanana: vanha osoitin jää osoittamaan lohkoon, jonka varaaja antaa seuraavalle pyytäjälle."}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.25;
  a [label="1. varaus\nvanha → lohko\n(vieraan istunto)"];
  b [label="2. free(vanha)\nlohko vapaa, vanha\nosoittaa siihen yhä"];
  c [label="3. uusi varaus\nsama lohko\n(ylläpitäjän istunto)"];
  d [label="4. vanha->…\nlukee tai muuttaa\nylläpitäjän istuntoa"];
  a -> b -> c -> d;
}
```

Vanha osoitin osoittaa nyt ylläpitäjän istuntoon. Jos ohjelma kirjoittaa
vanhan osoittimen kautta, se muuttaa uutta oliota; jos olio sisältää
funktio-osoittimen, vanha koodipolku voi kutsua jotain aivan muuta kuin
luuli. Käyttö vapautuksen jälkeen on siksi tyypillisesti yhtä vakava
kuin ylivuoto, ja selaimissa ja ytimissä se on yksi yleisimmistä
vakavista virheluokista.

## Kaksoisvapautus

Virhepolku vapauttaa istunnon, ja yhteinen siivous vapauttaa sen
uudelleen:

```{.c tiedosto="esimerkit/04-keko/istunnot.c" osa="tupla"}
```

```{.tuloste tiedosto="esimerkit/04-keko/odotettu" osa="t4"}
```

Ilman sanitoijaa glibc:n välimuisti (*tcache*) havaitsee saman lohkon
toisen vapautuksen ja lopettaa ohjelman:

```{.tuloste tiedosto="esimerkit/04-keko/odotettu" osa="t7"}
```

Havaitseminen on kuitenkin rajallista: jos väliin vapautetaan toinen
lohko, yksinkertainen tarkistus ei aina huomaa toistoa. Kaksoisvapautus
voi silloin johtaa siihen, että sama muisti annetaan kahdelle
varaukselle, eli samaan tilanteeseen kuin käyttö vapautuksen jälkeen.

## Rakenteelliset ratkaisut

Kekovirheet korjataan yksittäin, mutta niitä *ehkäistään* rakenteella:

- **Selvä omistajuus.** Jokaisella varauksella on yksi omistaja, joka
  vapauttaa sen. Muut saavat lainata osoitinta vain omistajan elinajan
  sisällä. Sama ajatus on C++:n `std::unique_ptr` ja Rustin
  omistajuusmalli.
- **Yksi siivouspolku.** `goto`-siivous funktion lopussa, jossa jokainen
  resurssi vapautetaan kerran, poistaa kaksoisvapautukset virhepoluilta.
- **Nollaa osoitin vapautuksen jälkeen**, kun se säilyy rakenteessa:
  `free(p->kentta); p->kentta = NULL;`. Se ei auta kopioituihin
  osoittimiin, mutta tekee kaksoisvapautuksesta vaarattoman.
- **Kovennettu varaaja** testaukseen ja tuotantoon: glibc:n
  virheenjäljitysvaraaja (`libc_malloc_debug.so` ja asetus
  `glibc.malloc.check`) tai erilliset varaajat kuten hardened_malloc tai
  Scudo (LLVM:n osa ja Androidin oletusvaraaja).

## Käytännössä

- **Aja testit ASanilla.** Kekovirheet näkyvät ilman sitä vain
  satunnaisesti, usein kaukana syystä.
- **Lue raportin kaikki pinot.** Vapautus- ja varauspino kertovat,
  missä omistajuus hukattiin.
- **Pidä vapautettu muisti vaarallisena**, vaikka luettu arvo näyttäisi
  harmittomalta: muisti annetaan pian jollekin toiselle.
- **Suunnittele omistajuus** ja yksi siivouspolku funktiota kohden.

## Itsearviointi

- Osaat selittää, miten keon ylivuoto voi korruptoida varaajan
  metatiedot, ja lukea lohkon koko-kentän gdb:llä.
- Osaat tulkita ASanin raportin käytöstä vapautuksen jälkeen ja nimetä
  sen kolme pinoa.
- Osaat perustella, miksi käyttö vapautuksen jälkeen on vakava, vaikka
  luettu arvo olisi roskaa.
- Osaat ehkäistä kaksoisvapautukset omistajuudella ja yhdellä
  siivouspolulla.
