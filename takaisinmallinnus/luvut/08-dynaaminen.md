# Dynaaminen analyysi

Dynaaminen analyysi havainnoi ohjelmaa, kun se ajetaan. Staattinen
analyysi kattaa kaikki polut mutta vaatii tulkintaa; dynaaminen näyttää
todelliset arvot ja vain ajetut polut. Linuxissa kolme työkalua riittää
pitkälle: gdb muuttaa ohjelman tilaa ja lukee muistia, strace näyttää
järjestelmäkutsut ja ltrace kirjastokutsut. Kohde on tilauksen
hinnoittelu:

```{.c tiedosto="esimerkit/07-gdb/tilaus.c" osa="funktiot"}
```

## gdb eräajona

Takaisinmallinnuksessa gdb:tä ajetaan usein eräajona: `-batch` ja `-x
skripti` ajavat komennot ja lopettavat, `-nx` ohittaa käyttäjän
asetukset. Näin analyysi on toistettava. Skriptin katkaisukohtaan voi
liittää komentoja ja Python-koodia. Ensimmäinen esimerkki pysäyttää
hinnoittelufunktion, tulostaa sen argumentit ja lukee tilausrivit
muistista:

```{.text tiedosto="esimerkit/07-gdb/argumentit.gdb" osa="argumentit"}
```

```{.tuloste tiedosto="esimerkit/07-gdb/odotettu" osa="t1"}
```

`break laske_hinta` pysäyttää funktion alkuun, missä argumentit ovat
vielä rekistereissä: `$esi` on `n` ja `$edx` asiakasluokka. `$rdi` on
osoitin tilausriveihin, ja silmukka lukee 12 tavun tietueet muistista
(`rivi` on `{int, int, int}`). Toinen katkaisukohta on *ehdollinen*:
`break alennus if $rsi > 10000` pysäyttää vain, kun summa ylittää
rajan. Ehdollinen katkaisu on dynaamisen analyysin tehokkaimpia keinoja:
sen avulla voi napata juuri sen kutsun tuhansista, jossa jokin ehto
täyttyy.

## Tilan muuttaminen

gdb ei vain tarkkaile vaan myös muuttaa ohjelman tilaa. Tavallinen
tarve on nähdä, mitä ohjelma tekisi, jos jokin tarkistus menisi toisin.
Tässä `FinishBreakpoint` pysäyttää funktion paluuseen ja muuttaa
paluuarvon:

```{.text tiedosto="esimerkit/07-gdb/muuta.gdb" osa="muuta"}
```

```{.tuloste tiedosto="esimerkit/07-gdb/odotettu" osa="t2"}
```

Alennuskoodin tarkistus palauttaa nollan (hylätty), mutta kun paluuarvo
`rax` asetetaan ykköseksi, ohjelma jatkaa kuin koodi olisi kelvannut.
Tämä on analyysikeino: näin selviää, mitä hyväksytyn koodin polulla
tapahtuu, ilman että algoritmia tarvitsee vielä ratkaista. Kohde on
paketin oma ohjelma. Toisen ohjelman lisenssi- tai kopiosuojauksen
kiertämiseen keinoa ei ole tarkoitettu, eikä laki sitä salli (luku 1).
Suunnittelijalle koe näyttää, miksi asiakkaan koneella tehty,
paluuarvoon nojaava tarkistus on heikko suojaus; luku 10 jatkaa
aiheesta.

## Kutsujen jäljitys

Python-skriptillä gdb:stä saa kevyen jäljittimen, joka tulostaa
funktioiden argumentit ja paluuarvot sisennettynä kutsusyvyyden mukaan:

```{.text tiedosto="esimerkit/07-gdb/jaljita.gdb" osa="jaljita"}
```

```{.tuloste tiedosto="esimerkit/07-gdb/odotettu" osa="t3"}
```

Jäljitys yhdistää staattisen ja dynaamisen analyysin: kun purusta on
päätelty funktioiden argumentit, jäljitin näyttää niiden todelliset
arvot ajossa. Isommassa ohjelmassa samalla tekniikalla voi lokittaa
esimerkiksi kaikki `malloc`- ja `free`-kutsut tai kaikki kutsut
tiettyyn moduuliin.

## Vahtipisteet

*Vahtipiste* (*watchpoint*) pysäyttää ohjelman, kun muistipaikka
muuttuu. Se vastaa kysymykseen, kuka kirjoittaa muuttujaan:

```{.text tiedosto="esimerkit/07-gdb/vahti.gdb" osa="vahti"}
```

```{.tuloste tiedosto="esimerkit/07-gdb/odotettu" osa="t4"}
```

Prosessori tukee vahtipisteitä laitteistorekistereillä, joten ne ovat
nopeita. Ne ovat korvaamattomia, kun globaali tila muuttuu odottamatta:
vahtipiste näyttää heti kirjoittavan funktion ja kutsupinon.

## strace ja ltrace

gdb vaatii ohjelman pysäyttämistä; strace ja ltrace näyttävät
ulospäin näkyvän käytöksen puuttumatta siihen. strace tallentaa
järjestelmäkutsut, ltrace kirjastokutsut. Kohteena on kirjautuja, joka
lukee asetukset ja tarkistaa salasanan:

```{.bash tiedosto="esimerkit/08-jaljitys/aja.sh" osa="strace"}
```

```{.tuloste tiedosto="esimerkit/08-jaljitys/odotettu" osa="t2"}
```

strace paljastaa, mitä tiedostoja ohjelma avaa, mitä se lukee ja
kirjoittaa ja mihin se ottaa yhteyttä (`openat`, `read`, `write`,
`connect`). Se on nopein tapa nähdä, mitä ohjelma tekee ympäristölleen.
ltrace näyttää kirjastorajapinnan, ja usein salaisuudet näkyvät siinä
selkokielisinä:

```{.bash tiedosto="esimerkit/08-jaljitys/aja.sh" osa="ltrace"}
```

```{.tuloste tiedosto="esimerkit/08-jaljitys/odotettu" osa="t3"}
```

`strcmp("arvaus", "Lumi-2026")` paljastaa oikean salasanan, vaikka sitä
ei näy `strings`-työkalulla: ohjelma kokoaa sen ajon aikana. Monet
suojaukset havaitsevat strace- ja ltrace-ajon ja muuttavat käytöstään
(luku 10), joten tulokset varmistetaan toisella menetelmällä.

## LD_PRELOAD-koukutus

Dynaamisesti linkitetyn funktion voi korvata omalla
`LD_PRELOAD`-kirjastolla (*Objektitiedostot, linkitys ja ABI*, luku
10). Koukku kirjaa kutsun ja välittää sen eteenpäin oikealle
funktiolle, jonka se hakee `dlsym`-kutsulla:

```{.c tiedosto="esimerkit/08-jaljitys/koukku.c" osa="koukku"}
```

```{.bash tiedosto="esimerkit/08-jaljitys/aja.sh" osa="preload"}
```

```{.tuloste tiedosto="esimerkit/08-jaljitys/odotettu" osa="t4"}
```

Koukutus on ltracea joustavampi: koukku näkee ja voi muuttaa
argumentteja ja paluuarvoja, kerätä tilastoja tai tallentaa dataa
tiedostoon. Sillä jäljitetään esimerkiksi salausrajapintoja (`EVP_*`),
muistinvarausta ja verkkokutsuja. Staattisesti linkitettyihin tai
suoriin järjestelmäkutsuihin se ei pure; niihin käytetään gdb:tä tai
`seccomp`-pohjaisia työkaluja. *Dynaaminen instrumentointi* (Frida,
DynamoRIO, Valgrind) yleistää koukutuksen: työkalu lisää omaa koodiaan
mihin tahansa ohjelman kohtaan ajon aikana, ei vain kirjastofunktioiden
rajalle.

## Käytännössä

- **Aloita stracella ja ltracella.** Ne näyttävät minuutissa, mitä
  ohjelma tekee tiedostoille, verkolle ja kirjastoille, ennen kuin
  yhtään käskyä on luettu.
- **Käytä ehdollisia katkaisuja ja vahtipisteitä.** Ne vievät suoraan
  kiinnostavaan tilaan tuhansien kutsujen tai ison muistialueen seasta.
- **Muuta tilaa kysymyksen tutkimiseksi**, älä vain ohjelman
  pakottamiseksi: "mitä tällä polulla tapahtuu" on analyysikysymys.
- **Skriptaa gdb** (`-batch -x`, Python-rajapinta), jotta ajo on
  toistettava ja liitettävissä muuhun analyysiin.
- **Varmista havainnot kahdella menetelmällä.** Suojattu ohjelma voi
  valehdella jäljittimelle; staattinen ja dynaaminen analyysi
  tarkistavat toisensa.

## Itsearviointi

- Osaat asettaa gdb:ssä katkaisukohtia, ehdollisia katkaisuja ja
  vahtipisteitä sekä lukea argumentit ja muistin eräajona.
- Osaat muuttaa paluuarvon tai muistin gdb:ssä ja perustella, miksi se
  on analyysikeino.
- Osaat lukea strace- ja ltrace-tulosteen ja päätellä niistä ohjelman
  käytöksen.
- Osaat kirjoittaa `LD_PRELOAD`-koukun, joka kirjaa kutsun ja välittää
  sen eteenpäin.
