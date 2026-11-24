# Oma tiedostojärjestelmä

Edellisessä luvussa tiedostoja käytettiin ytimen rajapinnan kautta.
Tässä luvussa rakennetaan rajapinnan alla oleva kerros: *pikkufs*,
pieni Unix-tyyppinen tiedostojärjestelmä, joka tallentaa kaiken
tavalliseen 64 KiB:n levykuvatiedostoon. Rakenne on sama kuin ext2:ssa
ja sen esikuvassa, 1970-luvun Unixin tiedostojärjestelmässä:
superlohko, bittikartat, inodetaulu ja datalohkot. Toteutus on noin
700 riviä C:tä, ja se tukee hakemistoja, kovia linkkejä, epäsuoria
lohkoja ja tarkistusohjelmaa.

## Levyn asettelu

Levy on jono kiinteän kokoisia *lohkoja*. Pikkufs käyttää 512 tavun
lohkoja, mikä on perinteinen levysektorin koko; nykyiset
tiedostojärjestelmät käyttävät yleensä 4 KiB:n lohkoja.

| Lohkot | Sisältö |
|--------|---------|
| 0 | superlohko: taikaluku, lohkojen ja inodejen määrä |
| 1 | inodebittikartta: bitti $i$ = inode $i$ käytössä |
| 2 | lohkobittikartta: bitti $i$ = lohko $i$ käytössä |
| 3–6 | inodetaulu: 32 inodea × 64 tavua |
| 7–127 | datalohkot |

Asettelu ja tietueet ovat otsakkeessa. `static_assert` varmistaa, että
rakenteiden koot ovat täsmälleen levymuodon mukaiset, koska ne
kirjoitetaan levylle sellaisinaan:

```{.c tiedosto="esimerkit/09-pikkufs/pikkufs.h" osa="asettelu"}
```

Inode 0 on varattu tarkoittamaan "ei inodea", ja juurihakemisto on
inode 1. Samoin lohko 0 tarkoittaa lohko-osoittimessa "ei varattu",
mikä on turvallista, koska lohko 0 on aina superlohko. Rajapinta
muistuttaa POSIXia, mutta virheet palautetaan negatiivisina
`errno`-arvoina kuten ytimessä:

```{.c tiedosto="esimerkit/09-pikkufs/pikkufs.h" osa="rajapinta"}
```

## Lohkot ja bittikartat

Kaikki levyhaku kulkee kahden funktion kautta (`lue_lohko` ja
`kirjoita_lohko`), jotka lukevat ja kirjoittavat yhden kokonaisen
lohkon `pread`- ja `pwrite`-kutsuilla. Ytimessä samassa kohdassa olisi
lohkokerros ja puskurivälimuisti.

Vapaiden inodejen ja lohkojen kirjanpito on bittikartta: yksi bitti
kutakin kohti, ja varaus (`varaa_bitti`) etsii ensimmäisen nollabitin.
Todelliset tiedostojärjestelmät etsivät vapaata lohkoa läheltä
tiedoston aiempia lohkoja, jotta tiedosto olisi levyllä yhtenäinen.
Inodet luetaan ja kirjoitetaan inodetaulusta: inode $n$ on lohkossa
$3 + \lfloor n/8 \rfloor$ kohdassa $n \bmod 8$.

## Inodet ja lohkojen osoitus

Inodessa on 10 suoraa lohko-osoitinta ja yksi *epäsuora*: lohko,
joka sisältää 128 lisäosoitinta. Pienet tiedostot (enintään 5 KiB)
tarvitsevat vain suorat osoittimet, ja suurin tiedosto on
$(10 + 128) \cdot 512 = 70\,656$ tavua. ext2 lisää kaksin- ja
kolminkertaisesti epäsuorat lohkot, ja ext4 korvaa osoitinlistat
*laajuuksilla* (engl. extents): alkulohko ja pituus kuvaavat kerralla
pitkän yhtenäisen jakson.

Funktio `lohko` muuntaa tiedoston sisäisen lohkonumeron levyn
lohkonumeroksi ja varaa puuttuvan lohkon kirjoitettaessa. Se on
tiedostojärjestelmän "sivutaulu":

```{.c tiedosto="esimerkit/09-pikkufs/pikkufs.c" osa="lohko"}
```

Luku ja kirjoitus (`lue_data`, `kirjoita_data`) käsittelevät
tiedoston lohko kerrallaan `lohko`-funktion avulla. Kirjoitus lohkon
keskelle on *luku–muokkaus–kirjoitus*: koko lohko luetaan, muutetaan
ja kirjoitetaan takaisin. Varaamaton lohko tiedoston keskellä on
aukko, ja se luetaan nollina kuten harvassa tiedostossa.

## Hakemistot ja polut

Hakemisto on tiedosto, jonka data on 32 tavun tietueiden taulukko:
inoden numero ja enintään 27-merkkinen nimi. Poistettu tietue
merkitään nollainodella, ja uusi nimi täyttää ensimmäisen vapaan
paikan. Nimen haku käy tietueet läpi järjestyksessä:

```{.c tiedosto="esimerkit/09-pikkufs/pikkufs.c" osa="etsi"}
```

Polku `/docs/muistio.txt` selvitetään osa kerrallaan juuresta alkaen
(`selvita`): jokainen välivaihe on hakemistohaku, ja välivaiheen on
oltava hakemisto, muuten tulos on `ENOTDIR`.

Haku on lineaarinen; ext4 käyttää suurissa hakemistoissa
hajautettua puuta, ja ytimen hakemistovälimuisti pitää selvitetyt
polut muistissa.

Alustus (`pfs_alusta`) kirjoittaa tyhjän levyn: superlohkon,
bittikartat, joissa metatietolohkot on merkitty käytetyiksi, ja
juurihakemiston, jossa on vain `.` ja `..`. Juuren `..` osoittaa
juureen itseensä. Uuden hakemiston linkkilaskuri on 2: nimi
vanhemmassa ja oma `.`. Jokainen alihakemisto kasvattaa vanhempansa
laskuria, koska sen `..` osoittaa vanhempaan. Siksi hakemiston
linkkimäärä on 2 + alihakemistojen määrä.

## Linkit ja poisto

Kova linkki lisää nimen ja kasvattaa laskuria. Hakemistoille kovia
linkkejä ei sallita, koska ne voisivat tehdä hakemistopuusta syklisen
graafin. Poisto tekee kaksi asiaa järjestyksessä: ensin nimi
poistetaan hakemistosta, sitten – jos se oli viimeinen nimi – inode
ja lohkot vapautetaan. Järjestys on tärkeä kaatumisen kannalta, kuten
kohta näytetään:

```{.c tiedosto="esimerkit/09-pikkufs/pikkufs.c" osa="poista"}
```

## Käyttö

Esittely alustaa levyn, luo hakemiston `/docs`, tiedoston
`/docs/muistio.txt` ja sille kovan linkin `/m` sekä 6000 tavun
tiedoston `/iso.bin`, joka tarvitsee 12 lohkoa ja siksi epäsuoran
lohkon. Jokainen kutsu tulostaa tuloksensa:

```{.c tiedosto="esimerkit/09-pikkufs/main.c" osa="tulos"}
```

Sen jälkeen levy suljetaan ja liitetään uudelleen, ja tiedostot
luetaan takaisin. Kaikki tieto on luettava levykuvasta, joten tämä
todistaa, että rakenteet todella tallentuvat. Lopuksi kokeillaan
virhetilanteita – ne palauttavat samat koodit, joita POSIX käyttää –
ja poistetaan tiedostot. Tuloste on luvun lopussa.

## Kaatuminen ja tarkistus

Monet operaatiot muuttavat useaa lohkoa: tiedoston kasvatus kirjoittaa
lohkobittikartan, datalohkon ja inoden. Jos virta katkeaa kesken, levy
jää *epäjohdonmukaiseen* tilaan. Seuraukset riippuvat siitä, mikä
ehdittiin kirjoittaa:

| Ehdittiin kirjoittaa | Seuraus |
|------------------------------|------------------------------------------|
| bittikartta, ei inodea | lohko vuotaa: varattu, mutta ei kenenkään |
| inode, ei bittikarttaa | lohko on käytössä, mutta voidaan varata toiselle |
| nimi poistettu, laskuria ei vähennetty | inode jää orvoksi |
| laskuri vähennetty, nimeä ei poistettu | nimi osoittaa vapautettuun inodeen |

Kaksi ensimmäistä ja viimeinen ovat vakavia, koska ne voivat sekoittaa
kahden tiedoston datan. Tiedostojärjestelmät järjestävät kirjoitukset
niin, että keskeytys jättää vain vaarattomia virheitä – vuotavia
lohkoja tai orpoja inodeja – ja korjaavat ne käynnistyksessä
tarkistusohjelmalla.

Tarkistus (`fsck`) käy koko hakemistopuun läpi, laskee jokaisen inoden
viittaukset ja merkitsee käytössä olevat lohkot:

```{.c tiedosto="esimerkit/09-pikkufs/pikkufs.c" osa="kaylapi"}
```

Tuloksia verrataan inodejen linkkilaskureihin sekä inode- ja
lohkobittikarttoihin. Jokainen ero tulostetaan, ja korjaustilassa
levy kirjoitetaan laskennan mukaiseksi.

Esittely simuloi kaatumista kirjoittamalla levykuvaan suoraan: lohko
100 merkitään varatuksi ilman omistajaa, ja juuren linkkilaskuri
turmellaan:

```{.c tiedosto="esimerkit/09-pikkufs/main.c" osa="kaatuminen"}
```

```{.tuloste tiedosto="esimerkit/09-pikkufs.odotettu"}
```

Tarkistus on hidas, koska se lukee koko levyn metatiedot: teratavun
levyllä se voi kestää tunteja. Siksi nykyiset tiedostojärjestelmät
käyttävät *journalointia*. Ennen kuin metatietoja muutetaan
paikoillaan, muutokset kirjoitetaan peräkkäin journaliin ja perään
kirjoitetaan sitoumusmerkintä. Kaatumisen jälkeen journal toistetaan:
valmiit tapahtumat tehdään loppuun, keskeneräiset hylätään. Btrfs ja ZFS käyttävät sen sijaan
copy-on-write-puita: mitään ei kirjoiteta paikoilleen, vaan uusi
versio kirjoitetaan muualle ja juuriosoitin vaihdetaan atomisesti.
Ytimessä tiedostojärjestelmät toteuttavat VFS-rajapinnan, jonka
operaatioita (`lookup`, `mkdir`, `link`, `unlink`) pikkufs:n
funktiot vastaavat.

## Käytännössä

- **Metatieto on tiedostojärjestelmän ydin:** data on helppoa, mutta
  bittikarttojen, inodejen ja hakemistojen johdonmukaisuus on se,
  mikä tekee järjestelmästä luotettavan.
- **Mieti kirjoitusjärjestys kaatumisen kannalta:** jokaisen
  välivaiheen on oltava joko oikea tai vaarattomasti korjattava.

## Itsearviointi

- Osaat kuvata Unix-tyyppisen tiedostojärjestelmän asettelun:
  superlohko, bittikartat, inodetaulu ja datalohkot.
- Osaat laskea suurimman tiedostokoon suorista ja epäsuorista
  osoittimista ja selittää laajuuksien edun.
- Osaat selittää, miten polku selvitetään hakemistotietueista ja miksi
  hakemiston linkkimäärä on 2 + alihakemistot.
- Osaat luetella, mitä epäjohdonmukaisuuksia kaatuminen voi jättää,
  ja miten `fsck` ja journalointi ne hoitavat.
