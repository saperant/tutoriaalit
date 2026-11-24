# Symbolittomat ohjelmat

Julkaistut ohjelmat on usein *riisuttu* (`strip`): symbolitaulu ja
virheenjäljitystieto on poistettu. Funktioilla ei ole nimiä, eikä edes
niiden rajoja ole kirjattu. Riisuminen ei kuitenkaan poista kaikkea:
dynaamiset tuonnit, poikkeustaulut ja käynnistyskoodin rakenne
säilyvät, ja tunnetut kirjastofunktiot voi tunnistaa tavuistaan.

Esimerkin ohjelma käyttää pientä apukirjastoa, joka linkitetään siihen
staattisesti, ja riisutaan:

```{.bash tiedosto="esimerkit/06-strip/aja.sh" osa="kaanna"}
```

## Mitä riisumisen jälkeen jää

```{.bash tiedosto="esimerkit/06-strip/aja.sh" osa="riisuttu"}
```

```{.tuloste tiedosto="esimerkit/06-strip/odotettu" osa="t1"}
```

Paikalliset ja globaalit symbolit ovat poissa, mutta *dynaaminen
symbolitaulu* (`.dynsym`) säilyy, koska lataaja tarvitsee sitä.
Tuonneista näkee heti paljon: ohjelma varaa muistia, kopioi sitä,
mittaa merkkijonoja ja tulostaa muotoillen. `_chk`-päätteiset
versiot kertovat, että ohjelma on käännetty `_FORTIFY_SOURCE`-tasolla,
ja `__stack_chk_fail` pinon suojauksesta. Jaettu kirjasto ei voi
riisua vientejään, joten sen rajapinta näkyy aina (`nm -D
--defined-only`).

## Funktioiden rajat .eh_frame-taulusta

Poikkeustaulu `.eh_frame` jää ohjelmaan, koska sitä tarvitaan
poikkeusten käsittelyyn ja pinon purkamiseen (myös C-ohjelmissa
esimerkiksi `backtrace`-funktiolle ja profiloijille). Siinä on jokaista
funktiota kohti *FDE*-tietue (*frame description entry*), jossa on
funktion osoitealue. Se on luotettavampi lähde funktioiden rajoille
kuin heuristiikat, jotka etsivät `push rbp`- tai `endbr64`-alkuja:

```text
readelf --debug-dump=frames ohjelma-s | grep FDE
... FDE cie=00000000 pc=00000000000010a0..0000000000001100
```

Kaikilla funktioilla ei ole FDE:tä: käsin kirjoitetulla assemblylla
ja osalla käynnistystiedostojen (`crt*.o`) funktioista sitä ei ole, ja
valitsin `-fno-asynchronous-unwind-tables` jättää taulun pois.

## main tulokohdasta

ELF-otsakkeen tulokohta (*entry point*) on glibc:n `_start`, joka
kutsuu funktiota `__libc_start_main` ja välittää sille `main`-funktion
osoitteen ensimmäisessä argumentissa. Riisumattomasta ohjelmasta se
näyttää tältä:

```{.tuloste tiedosto="esimerkit/06-strip/odotettu" osa="t2"}
```

`_start` on sama kaikissa glibc-ohjelmissa, joten riisutussakin
ohjelmassa `lea rdi` -käskyn kohde on `main`. `hlt` lopussa ei koskaan
suoriteta, koska `__libc_start_main` ei palaa. Muissa C-kirjastoissa (musl) ja kielissä
(Rust, Go) kuvio on erilainen, mutta yhtä vakio.

## Kirjastofunktioiden allekirjoitukset

Riisutussa ohjelmassa on usein staattisesti linkitettyä kirjastokoodia:
kryptografiaa, pakkausta, protokollapinoja. Sen analysointi on turhaa
työtä, jos kirjasto tunnetaan. *Allekirjoitus* on kirjaston funktion
tavujono, josta on peitetty kohdat, jotka linkkeri täyttää
(relokaatiot): kutsujen ja `rip`-suhteellisten viittausten siirtymät.
Jos ohjelman funktio vastaa allekirjoitusta peitettyjä kohtia lukuun
ottamatta, se on sama funktio. IDA:n FLIRT, Ghidran Function ID ja
radare2:n zignatures toimivat tällä periaatteella; skripti
`riisuttu.py` tekee saman pienessä mittakaavassa:

```{.python tiedosto="esimerkit/06-strip/riisuttu.py" osa="allekirjoitus"}
```

Skripti yhdistää kolme lähdettä: FDE-rajat, `main`-funktion
tulokohdasta ja allekirjoitukset objektitiedostosta `kirjasto.o`.
Tarkistusta varten se vertaa tulosta riisumattoman ohjelman
symbolitauluun:

```{.bash tiedosto="esimerkit/06-strip/aja.sh" osa="tunnistus"}
```

```{.tuloste tiedosto="esimerkit/06-strip/odotettu" osa="t3"}
```

Kaikki `.text`-osion funktiot tunnistettiin. `tulosta_tarkiste` puuttuu,
koska se on upotettu `main`-funktioon (luku 5). Allekirjoitus toimii
vain, jos kirjasto on käännetty samalla kääntäjällä ja samoilla
valitsimilla; käytännössä allekirjoituskirjastoon kootaan kirjaston
yleisimmät versiot, ja epävarmat osumat tarkistetaan käsin. Lyhyet
funktiot (muutama käsky) osuvat moneen, joten niille tarvitaan lisäehtoja,
kuten kutsuttujen funktioiden nimet.

Muita keinoja tunnistaa koodia ilman symboleita:

- **vakiot**: CRC-32:n `0xedb88320`, SHA-256:n alkuarvot
  `0x6a09e667…`, AES:n S-laatikko. Työkalut kuten `findcrypt` etsivät
  niitä.
- **merkkijonot**: virheilmoitukset ja versiotekstit, kuten
  `inflate 1.3 Copyright`, nimeävät kirjaston ja version.
- **tuonnit**: kutsuttujen kirjastofunktioiden yhdistelmä kertoo
  funktion tehtävän (`socket`, `connect`, `send` peräkkäin).

## Käytännössä

- **Katso tuonnit ja merkkijonot ennen purkua.** Ne kertovat ohjelman
  tehtävän ja käytetyt kirjastot nopeammin kuin koodi.
- **Käytä `.eh_frame`-taulua funktioiden rajoina**, kun symbolit
  puuttuvat; Ghidra ja radare2 käyttävät sitä myös.
- **Etsi `main` tulokohdasta.** Se on ohjelman logiikan alku, ja sen
  kutsumat funktiot ovat seuraavat analysoitavat.
- **Tunnista kirjastot ennen kuin analysoit niitä**: allekirjoitukset,
  vakiot ja versiomerkkijonot säästävät päiviä.
- **Riisu omat julkaisusi tietoisesti.** Riisuminen ei ole suojaus,
  mutta se poistaa sisäiset nimet; säilytä virheenjäljitystieto
  erillisessä tiedostossa (*Objektitiedostot, linkitys ja ABI*, luku
  14).

## Itsearviointi

- Osaat kertoa, mitä riisuminen poistaa ja mitä se jättää ohjelmaan.
- Osaat lukea funktioiden rajat `.eh_frame`-taulusta ja löytää
  `main`-funktion glibc-ohjelman tulokohdasta.
- Osaat selittää, miten allekirjoitukset tunnistavat kirjastofunktioita
  ja miksi relokaatioiden kohdat peitetään.
- Osaat käyttää vakioita, merkkijonoja ja tuonteja koodin
  tunnistamiseen.
