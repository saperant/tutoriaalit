# Disassemblointi ja dekompilointi

*Disassembleri* muuntaa konekielen tavut käskyiksi, *dekompilaattori*
käskyt C:tä muistuttavaksi koodiksi. Kumpikaan tehtävä ei ole
yksiselitteinen: ELF-tiedosto ei kerro, mitkä tavut ovat koodia ja
mitkä dataa, eikä konekielestä voi palauttaa muuttujien nimiä,
tyyppejä tai rakenteita. Työkalut arvaavat, ja analyytikon on
tiedettävä, miten ne arvaavat.

## Lineaarinen ja rekursiivinen läpikäynti

*Lineaarinen läpikäynti* (*linear sweep*) purkaa osion alusta loppuun:
käsky kerrallaan, seuraava alkaa siitä, mihin edellinen loppui.
`objdump -d` toimii näin. Menetelmä on nopea ja kattaa kaiken, mutta
se sekoaa, jos koodin seassa on dataa: x86-64:n käskyt ovat 1–15 tavun
mittaisia, ja väärästä kohdasta aloitettu purku tuottaa uskottavan
näköisiä mutta vääriä käskyjä.

*Rekursiivinen läpikäynti* (*recursive descent*) seuraa ohjausvuota:
se purkaa käskyn, jatkaa hypyn kohteesta ja ohittaa ehdottoman hypyn
jälkeiset tavut, ellei mikään hyppää niihin. radare2, Ghidra ja IDA
toimivat näin. Menetelmä ei sekoa dataan, mutta se ei löydä koodia,
johon hypätään vain epäsuorasti (funktio-osoittimet, hyppytaulut),
ellei se osaa ratkaista kohdetta.

Ero näkyy pienessä assembly-funktiossa, jonka ehdottoman hypyn jälkeen
on yksi tavu, joka ei ole käsky:

```{.gnuassembler tiedosto="esimerkit/02-purku/sekaannus.S" osa="sekaannus"}
```

```{.bash tiedosto="esimerkit/02-purku/aja.sh" osa="lineaarinen"}
```

```{.tuloste tiedosto="esimerkit/02-purku/odotettu" osa="t1"}
```

Tavu `0xe8` on `call`-käskyn ensimmäinen tavu, joten `objdump` lukee sen
ja neljä seuraavaa tavua (`mov eax,1`:n alun) kutsuna ohjelman
ulkopuolelle. Loput tavut tulkitaan käskyksi `add bl,al`, ja
paluukäsky katoaa. Rekursiivinen purku seuraa hyppyä ja näyttää oikean
koodin:

```{.bash tiedosto="esimerkit/02-purku/aja.sh" osa="rekursiivinen"}
```

```{.tuloste tiedosto="esimerkit/02-purku/odotettu" osa="t2"}
```

radare2 merkitsee ohitetun tavun kahdella pisteellä (`..`). Vasemman
reunan viivat ovat hyppyjen nuolia: `,=<` lähtee, `` `-> `` saapuu.
Kääntäjä ei tuota tällaista koodia, mutta käsin kirjoitettu assembly,
obfuskaattorit ja jotkin laiteohjelmistot tuottavat; lisäksi
hyppytaulut ja vakiot voivat olla koodiosiossa ARM-arkkitehtuurilla.

## radare2 eräajona

radare2 on avoimen lähdekoodin takaisinmallinnuskehys (LGPL), jonka
komennot ovat lyhyitä kirjainyhdistelmiä. Interaktiivisen käytön lisäksi
se toimii eräajona: `r2 -q -c 'komennot' ohjelma` ajaa komennot ja
lopettaa. Tämän tutoriaalin apufunktio `r2` lisää valitsimet, jotka
poistavat värit ja konekielen tavut. Esimerkkinä on pieni
varastokirjanpito:

```{.c tiedosto="esimerkit/02-purku/varasto.c" osa="etsi"}
```

| Komento | Merkitys |
|---------|----------|
| `aaa` | analysoi kaiken: funktiot, viittaukset, argumentit |
| `afl` | funktiot: osoite, peruslohkot, koko, nimi |
| `pdf @ f` | funktion purku (*print disassembly function*) |
| `iz` | merkkijonot data-osioista |
| `axt @ x` | viittaukset kohteeseen x (*xrefs to*) |
| `axf @ x` | viittaukset kohteesta x |
| `agf @ f` | funktion ohjausvuograafi ASCII-kuvana |
| `pdc @ f` | karkea pseudokoodi |
| `afn nimi @ x` | nimeä funktio |
| `s x` | siirry kohtaan x (*seek*) |

Ensimmäinen kysymys on, mitä funktioita ohjelmassa on:

```{.bash tiedosto="esimerkit/02-purku/aja.sh" osa="afl"}
```

```{.tuloste tiedosto="esimerkit/02-purku/odotettu" osa="t3"}
```

Peruslohkojen määrä ja koko kertovat, mistä kannattaa aloittaa: pieni
yhden lohkon funktio on kääre, monta lohkoa sisältävä tekee päätöksiä.
Merkkijonot ovat usein nopein vihje ohjelman tarkoitukseen:

```{.tuloste tiedosto="esimerkit/02-purku/odotettu" osa="t4"}
```

Sarakkeet ovat pituus, koko tavuina, osio, koodaus ja merkkijono.
`.data`-osion merkkijonot ovat alustetun taulukon kenttiä
(`varasto[i].koodi`), `.rodata`:n merkkijonot vakioita. Muotoilumerkkijono
`TILAA: %s (saldo %d)` kertoo tulostettavat tyypit.

## Ristiviittaukset

*Ristiviittaukset* (*cross-references*, xrefs) yhdistävät koodin ja
datan: mikä funktio käyttää tätä merkkijonoa, kuka kutsuu tätä
funktiota, missä tätä muuttujaa luetaan. Ne ovat analyysin tärkein
navigointikeino:

```{.bash tiedosto="esimerkit/02-purku/aja.sh" osa="axt"}
```

```{.tuloste tiedosto="esimerkit/02-purku/odotettu" osa="t5"}
```

Merkkijonosta päästään funktioon `raportoi`, joka siis tulostaa
tilaushälytyksen. `etsi`-funktiota kutsuu vain `ota`, ja taulukkoa
`varasto` käyttävät `etsi` ja `raportoi`. Riisutussa ohjelmassa
funktioiden nimet ovat muotoa `fcn.00001189`, mutta sama päättely
toimii, ja kun funktion tarkoitus selviää, se nimetään (`afn`). Hyvä
nimeäminen on puolet takaisinmallinnuksesta.

## Dekompilointi

Dekompilaattori kokoaa peruslohkoista rakenteisia lauseita (`if`,
`while`), muuttaa pinopaikat muuttujiksi ja päättelee tyypit. Ghidran
dekompilaattori on avoimista paras; radare2:n oma `pdc` on karkea:

```{.bash tiedosto="esimerkit/02-purku/aja.sh" osa="pdc"}
```

```{.tuloste tiedosto="esimerkit/02-purku/odotettu" osa="t6"}
```

Tulos on lähinnä käskyjen uudelleenkirjoitus: parametrit ovat väärin
(`int esi, int edx`, vaikka funktiolla on yksi osoitinargumentti),
käskynimiä katkeaa (`endbr6`) ja silmukka näkyy hyppyinä. Paremmatkin
dekompilaattorit erehtyvät tyypeissä ja rakenteissa, kun koodi on
optimoitua. Dekompilaattorin tuloste on hypoteesi, joka tarkistetaan
konekielestä.

radare2:n `r2ghidra`-laajennus tuo Ghidran dekompilaattorin radare2:een;
Cutter on radare2:n graafinen käyttöliittymä ja Rizin sen haara.
Ghidraa käsitellään luvussa 12.

## Käytännössä

- **Aloita merkkijonoista, tuonneista ja ristiviittauksista**, ei
  ensimmäisestä funktiosta. Merkkijono `TILAA:` ja `axt` vievät suoraan
  oikeaan kohtaan.
- **Älä luota yhteen purkuun.** Jos käskyt näyttävät oudoilta
  (harvinaiset käskyt, `add` muistiin ilman syytä, kutsut ohjelman
  ulkopuolelle), purku on todennäköisesti alkanut väärästä kohdasta.
- **Nimeä ja kommentoi heti**: funktiot, muuttujat, rakenteiden kentät.
  Ghidran ja radare2:n projektitiedostot säilyttävät nimet.
- **Käytä dekompilaattoria kartoitukseen, konekieltä totuuteen.**
  Tarkista erityisesti ehtojen suunnat, etumerkit ja osoitinaritmetiikka.
- **Skriptaa toistuvat kyselyt.** `r2 -q -c` ja Ghidran headless-tila
  tekevät analyysista toistettavan.

## Itsearviointi

- Osaat selittää lineaarisen ja rekursiivisen läpikäynnin eron ja
  tunnistaa purun, joka on alkanut väärästä kohdasta.
- Osaat listata radare2:lla funktiot, merkkijonot ja ristiviittaukset
  eräajona.
- Osaat edetä merkkijonosta sitä käyttävään funktioon ja sen
  kutsujiin.
- Osaat arvioida dekompilaattorin tulosteen luotettavuutta.
