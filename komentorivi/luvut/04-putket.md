# Putket ja uudelleenohjaukset

Jokaisella prosessilla on kolme avointa virtaa: vakiosyöte (0,
*stdin*), vakiotuloste (1, *stdout*) ja virhetuloste (2, *stderr*).
Oletuksena kaikki kolme ovat pääte. Kuori voi ohjata ne tiedostoihin
tai toisten prosessien virtoihin ennen komennon käynnistämistä.
Komennon ei tarvitse tietää mitään siitä, mistä sen syöte tulee tai
minne tuloste menee. Tämä on komentorivin tärkein suunnitteluperiaate.

## Uudelleenohjaukset

| Merkintä | Merkitys |
|----------|----------|
| `> tiedosto` | Tuloste tiedostoon; olemassa oleva tyhjennetään |
| `>> tiedosto` | Tuloste tiedoston loppuun |
| `2> tiedosto` | Virhetuloste tiedostoon |
| `2>&1` | Virhetuloste samaan paikkaan kuin tuloste *tällä hetkellä* |
| `&> tiedosto` | Molemmat tiedostoon (Bash) |
| `< tiedosto` | Syöte tiedostosta |
| `<<< "teksti"` | Syöte merkkijonosta (Bash) |
| `> /dev/null` | Tuloste roskiin |

Erottelu on hyödyllistä, koska data ja virheet ovat eri asioita:
tuloste jatkaa putkessa seuraavalle komennolle, ja virheet näkyvät
käyttäjälle.

```{.bash tiedosto="esimerkit/04-ohjaukset.sh" osa="erikseen"}
```

```{.bash tiedosto="esimerkit/04-ohjaukset.sh" osa="yhdessa"}
```

Uudelleenohjaukset käsitellään vasemmalta oikealle. `2>&1` kopioi
virran 1 *nykyisen* kohteen virralle 2. Siksi järjestyksellä on
väliä: `> tiedosto 2>&1` vie molemmat tiedostoon, mutta `2>&1 >
tiedosto` vie virheet sinne, minne tuloste oli menossa ennen
ohjausta, tässä putkeen:

```{.dot otsikko="Ohjausten järjestys: 2>&1 kopioi virran 1 senhetkisen kohteen"}
digraph {
  rankdir=LR; nodesep=0.2; ranksep=0.5;
  subgraph cluster_a {
    label="komento > tiedosto 2>&1"; color="#D9E0E3";
    a1 [label="1 tuloste"]; a2 [label="2 virheet"];
    at [label="tiedosto", shape=note]; ap [label="pääte tai putki"];
    a1 -> at; a2 -> at; a2 -> ap [style=invis];
  }
  subgraph cluster_b {
    label="komento 2>&1 > tiedosto"; color="#D9E0E3";
    b1 [label="1 tuloste"]; b2 [label="2 virheet"];
    bt [label="tiedosto", shape=note]; bp [label="pääte tai putki"];
    b1 -> bt; b2 -> bp;
  }
}
```

```{.bash tiedosto="esimerkit/04-ohjaukset.sh" osa="jarjestys"}
```

```{.tuloste tiedosto="esimerkit/04-ohjaukset.odotettu"}
```

Viimeinen muoto on hyödyllinen, kun halutaan käsitellä putkessa vain
virheilmoituksia. `|| true` rivien lopussa kuittaa epäonnistumisen,
jottei esimerkkiskripti pysähdy siihen (luku *Virheiden käsittely*
taidossa *Bash-skriptaus*).

## Putket

Putki `a | b` yhdistää komennon `a` tulosteen komennon `b` syötteeseen.
Komennot käynnistyvät samanaikaisesti ja käsittelevät dataa virtana:
`b` saa ensimmäiset rivit ennen kuin `a` on valmis, eikä välitulosta
tarvitse mahtua muistiin. Jos `b` lopettaa aikaisin (esim. `head`),
`a` saa signaalin `SIGPIPE` ja lopettaa myös. Putkeen kulkee vain
vakiotuloste; virhetulosteet menevät edelleen päätteelle:

```{.dot otsikko="Putki a | b yhdistää vain vakiotulosteen seuraavan komennon syötteeseen"}
digraph {
  rankdir=LR; nodesep=0.3;
  a [label="a"]; b [label="b"];
  paate [label="pääte"];
  a -> b [label="tuloste (1) → syöte (0)"];
  a -> paate [label="virheet (2)", style=dashed];
  b -> paate [label="tuloste (1)"];
  b -> paate [label="virheet (2)", style=dashed];
}
```

`tee` haaroittaa virran: se kirjoittaa syötteensä tiedostoon ja
tulosteeseen, joten välituloksen voi tallentaa putken keskeltä:

```{.bash tiedosto="esimerkit/04-tee.sh" osa="tee"}
```

```{.tuloste tiedosto="esimerkit/04-tee.odotettu"}
```

`tee` on myös tapa kirjoittaa tiedostoon, johon tarvitaan pääkäyttäjän
oikeudet: `echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf`.

Putken paluuarvo on oletuksena viimeisen komennon paluuarvo, joten
`puuttuva-komento | sort` onnistuu. Skripteissä tämä korjataan
asetuksella `set -o pipefail`, ja Bashin taulukko `PIPESTATUS` kertoo
kaikkien komentojen paluuarvot. Molemmat käsitellään taidossa
*Bash-skriptaus*.

## Prosessikorvaus

Monet komennot vertailevat kahta *tiedostoa* (`diff`, `comm`, `join`).
Kun vertailtavat ovat komentojen tulosteita, Bashin prosessikorvaus
`<(komento)` antaa tulosteen tiedostonimenä, eikä väliaikaisia
tiedostoja tarvita.

Esimerkki on käyttöoikeuksien tarkastus: kenellä on tunnus, vaikka hän
ei ole enää henkilöstölistalla? `comm` vaatii lajitellut syötteet ja
tulostaa kolme saraketta: vain ensimmäisessä, vain toisessa ja
molemmissa. Valitsimet `-1`, `-2` ja `-3` piilottavat sarakkeita:

```{.bash tiedosto="esimerkit/04-vertailu.sh" osa="comm"}
```

```{.bash tiedosto="esimerkit/04-vertailu.sh" osa="diff"}
```

```{.tuloste tiedosto="esimerkit/04-vertailu.odotettu"}
```

`diff` kertoo muutokset muokkauskomentoina: `2d1` tarkoittaa, että
ensimmäisen tiedoston rivi 2 poistetaan, ja `3a3`, että rivin 3
jälkeen lisätään. Ihmiselle luettavampi muoto on `diff -u`, jota myös
versionhallinta käyttää.

## Paluuarvot ja komentojen ketjutus

Jokainen komento palauttaa päättyessään *paluuarvon*, luvun 0–255.
Arvo 0 tarkoittaa onnistumista ja muu arvo epäonnistumista. Kuori
tallettaa edellisen komennon paluuarvon muuttujaan `$?`, ja sen varaan
rakentuvat ketjutukset `&&` ja `||`:

```{.bash tiedosto="esimerkit/04-paluuarvo.sh" osa="paluuarvo"}
```

```{.tuloste tiedosto="esimerkit/04-paluuarvo.odotettu"}
```

`grep` palauttaa 1, kun osumia ei ole, ja 2 virheessä. `ls` palauttaa
2 vakavassa virheessä. Arvot on dokumentoitu kunkin komennon
ohjesivulla, ja niiden varaan voi rakentaa ehtoja. Komentoja voi
yhdistää samalle riville usealla tavalla:

- `a; b`: `b` ajetaan aina `a`:n jälkeen.
- `a && b`: `b` vain, jos `a` onnistui.
- `a || b`: `b` vain, jos `a` epäonnistui.
- `a &`: `a` taustalle (luku *Prosessit ja signaalit*).
- `( cd x && a )`: alikuori; hakemiston vaihto ei vaikuta kutsujaan.
- `$(komento)`: komennon tuloste argumentiksi.

Tavallinen idiomi: `make && ./ohjelma` ajaa ohjelman vain, jos käännös
onnistui. `cd hakemisto && rm -r *` on turvallisempi kuin
`cd hakemisto; rm -r *`, joka poistaa väärän hakemiston sisällön, jos
`cd` epäonnistuu.

## Käytännössä

- **Data tulosteeseen, viestit virhetulosteeseen.** Kun kirjoitat omia
  työkaluja, noudata samaa sopimusta, niin ne toimivat putkissa.
- **`> tiedosto 2>&1`, ei toisin päin.** Lue uudelleenohjaukset
  vasemmalta oikealle sijoituksina.
- **`> /dev/null` vain, kun tiedät, mitä hukkaat.** Virheiden
  vaientaminen (`2> /dev/null`) piilottaa myös odottamattomat virheet.
  Vaienna mieluummin yksittäinen tunnettu ilmoitus.
- **Vältä väliaikaistiedostoja** prosessikorvauksella ja putkilla.
  Jos niitä tarvitaan, luo ne komennolla `mktemp`, ei kiinteällä
  nimellä hakemistoon `/tmp`.
- **Tarpeeton `cat`**: `cat tiedosto | grep x` toimii, mutta `grep x
  tiedosto` tai `< tiedosto grep x` säästää prosessin ja antaa
  komennolle tiedostonimen virheilmoituksiin.
- **Pitkä putki kehitetään vaiheittain**: lisää yksi vaihe kerrallaan
  ja katso välitulos (`| head`), ennen kuin jatkat.

## Itsearviointi

- Osaat ohjata tulosteen ja virhetulosteen erikseen tai yhdessä
  tiedostoon ja selittää, miksi uudelleenohjausten järjestys vaikuttaa.
- Osaat rakentaa putken, tallentaa välituloksen `tee`-komennolla ja
  kirjoittaa pääkäyttäjän tiedostoon `sudo tee`-muodolla.
- Osaat vertailla kahden komennon tulosteita prosessikorvauksella
  `comm`- ja `diff`-komennoilla.
- Osaat ketjuttaa komentoja paluuarvon perusteella `&&`- ja
  `||`-operaattoreilla.
