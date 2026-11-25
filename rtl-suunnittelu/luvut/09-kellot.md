# Kellot ja nollaukset

RTL-kuvaus olettaa, että kello on täydellinen ja että nollaus vie
piirin tunnettuun tilaan. Oikeassa piirissä kello saapuu kiikuille eri
aikaan, nollaussignaali on pitkä ja hidas verkko, ja nollauksen
vapautus on itsessään ajoitustapahtuma. Tämä luku kertoo, miten kellot
ja nollaukset kuvataan niin, että oletukset pitävät.

## Kellot

Kello kulkee piirissä erillistä, tasapainotettua *kellopuuta* pitkin,
jotta se saapuu kaikille kiikuille lähes samaan aikaan. FPGA:ssa
kellopuita on rajallinen määrä, ja kello on vietävä niihin erillisellä
puskurilla. Siksi RTL-suunnittelussa noudatetaan muutamaa sääntöä:

- **Kello tulee ulkoa tai kellonhallintayksiköstä.** PLL tai MMCM
  tuottaa tarvittavat taajuudet ja vaihesiirrot. Se instansioidaan
  valmistajan primitiivinä, eikä sitä kirjoiteta RTL:llä.
- **Logiikalla ei tuoteta kelloa.** Kiikulla jaettu kello on vinossa
  alkuperäiseen nähden, kulkee tavallisessa reitityksessä ja muodostaa
  uuden kellotusalueen. Hidas toiminta toteutetaan sallinnalla (luku 7).
- **Kelloa ei portiteta AND-portilla.** Portitettu kello tuottaa
  piikkejä, kun sallinta muuttuu kellon ollessa ylhäällä. ASIC:ssa
  tehonsäästöön käytetään kirjaston kellonportitussolua (integrated
  clock gating, ICG), jossa on salpa, ja synteesityökalu voi lisätä sen
  automaattisesti sallinnallisille rekistereille. FPGA:ssa käytetään
  kellopuskurin omaa sallintatuloa.

Ajoitusanalyysi tarvitsee tiedon jokaisesta kellosta: jakso, lähde ja
kellojen väliset suhteet. Ne annetaan rajoitetiedostossa (SDC tai XDC).
Se on taidon *FPGA-toteutus* aihe, mutta RTL-suunnittelijan on
tiedettävä, mitä kelloja suunnitelmassa on ja mitkä signaalit
ylittävät niiden rajat.

## Asynkroninen ja synkroninen nollaus

Nollaus voi olla asynkroninen tai synkroninen. Ero näkyy vain
herkkyyslistassa:

```{.systemverilog tiedosto="esimerkit/09-nollaus.sv" osa="tyylit"}
```

| Ominaisuus | Asynkroninen | Synkroninen |
|------------------|------------------|------------------|
| Toimii ilman kelloa | kyllä | ei |
| Nollaussignaalin ajoitus | vain vapautus on ajoitettava | tavallinen datapolku |
| Logiikka datapolussa | ei | multiplekseri tai kiikun nollaustulo |
| Piikkiherkkyys | piikki nollaa rekisterin | piikki suodattuu, jos se ei osu reunaan |
| Tyypillinen käyttö | ASIC, monet FPGA-suunnitelmat | Xilinxin suositus FPGA:ssa |

Testipenkki pysäyttää kellon ja kytkee nollauksen molempiin
rekistereihin. Asynkroninen nollautuu heti, synkroninen vasta, kun
kello käy taas:

```{.tuloste tiedosto="esimerkit/09-nollaus.odotettu" rivit="2-4"}
```

## Nollauksen tahdistin

Asynkronisen nollauksen *vapautus* on vaarallinen. Jos se osuu lähelle
kellon reunaa, osa kiikuista näkee vapautuksen tällä reunalla ja osa
seuraavalla, tai kiikku joutuu metastabiiliin tilaan. Tilakone voi
silloin lähteä liikkeelle laittomasta tilasta.

Ratkaisu on *nollauksen tahdistin*: nollaus kytkeytyy päälle heti,
mutta vapautuu kahden kiikun ketjun kautta kellon reunalla. Yleinen
nimi on *asynchronous assert, synchronous deassert*.

```{.systemverilog tiedosto="esimerkit/09-nollaus.sv" osa="tahdistin"}
```

Ketjun ensimmäinen kiikku voi joutua metastabiiliksi, mutta toinen
saa kokonaisen kellojakson aikaa asettua. Testipenkissä ulkoinen
nollaus vapautuu hetkellä 23, keskellä jaksoa. Tahdistettu nollaus
vapautuu toisella nousevalla reunalla, hetkellä 35:

```{.tuloste tiedosto="esimerkit/09-nollaus.odotettu" rivit="1-1"}
```

Jokaisella kellotusalueella on oma tahdistimensa.

Alla sama tahdistin on simuloitu puolen jakson tarkkuudella. Ulkoinen
vapautus tulee keskellä kellon alatilaa, mutta piirin sisäinen `rst_n`
vapautuu vasta toisella nousevalla reunalla sen jälkeen. Päälle
kytkeytyminen on silti välitöntä: kaavion lopussa ulkoinen nollaus
laskee keskellä kellon ylätilaa, ja `rst_n` seuraa heti, koska ketjun
kiikkujen nollaus on asynkroninen.

```{.ajoituskaavio tiedosto="esimerkit/kaaviot/09-nollaus.json" otsikko="Nollauksen tahdistin: tahdistettu vapautus, välitön kytkentä"}
```

## Mitä nollataan

Nollaus maksaa: jokainen nollattava kiikku on kytkettävä nollausverkkoon,
joka on suunnitelman suurin verkko kellon jälkeen. Nollaus kannattaa
siis rajata siihen, mikä sitä tarvitsee:

- **Nollataan:** tilakoneiden tilat, kelvollisuusbitit, laskurit, joiden
  arvo vaikuttaa ohjaukseen, ja ohjausrekisterit, joilla on
  dokumentoitu nollausarvo.
- **Ei nollata:** datapolun rekisterit, liukuhihnan data, muistit ja
  siirtorekisterien sisältö. Niiden arvolla ei ole merkitystä ennen
  kuin kelvollisuusbitti sanoo niin.

FPGA:ssa kiikuille voi antaa alkuarvon konfiguraatiossa
(`logic q = 1'b0;` tai `initial`). Se on synteesikelpoista FPGA:ssa,
mutta ei ASIC:ssa. Alkuarvo ei myöskään korvaa nollausta, jos piiri
on voitava nollata ilman uudelleenkonfigurointia.

## Käytännössä

- **Yksi nollaustyyli projektissa.** Asynkroninen aktiivinen nolla
  (`rst_n`) on ASIC-maailman ja monien IP-kirjastojen oletus.
  Synkroninen aktiivinen ykkönen on Xilinxin suositus. Sekoittaminen
  johtaa virheisiin rajapinnoissa. Tämän tutoriaalin esimerkit
  käyttävät asynkronista `rst_n`-nollausta.
- **Nollauksen tahdistin jokaiselle kellolle.** Ulkoinen nollaus
  (nappi, PLL:n lukittumissignaali, ohjelmistonollaus) kulkee aina
  tahdistimen kautta kunkin kellotusalueen omaksi nollaukseksi.
  Vapautuksen ajoitus tarkistetaan ajoitusanalyysissä (recovery- ja
  removal-tarkistukset).
- **Älä sekoita nollausta logiikkaan.** Nollaussignaaliin ei lisätä
  ehtoja (`if (!rst_n || tyhjenna)` asynkronisessa haarassa). Ohjelmallinen
  tyhjennys on synkroninen sallinta, ja se kirjoitetaan `else`-haaraan.
- **Ei nollausta datalle.** Nollauksettomat datarekisterit pienentävät
  nollausverkkoa ja antavat synteesille vapauden käyttää siirtorekisteri-
  ja DSP-rakenteita, joissa ei ole nollaustuloa.
- **Kello ei ole data.** Kellosignaalia ei käytetä logiikan syötteenä,
  eikä datasignaalia kellona. Molemmat sekoittavat ajoitusanalyysin.

## Itsearviointi

- Osaat kuvata asynkronisen ja synkronisen nollauksen ja vertailla
  niiden ominaisuuksia.
- Osaat toteuttaa nollauksen tahdistimen ja selittää, miksi
  vapautus on tahdistettava.
- Osaat selittää, miksi kelloa ei jaeta eikä portiteta tavallisella
  logiikalla, ja mitä käytetään sen sijaan.
- Osaat päättää, mitkä rekisterit nollataan ja mitkä eivät.
