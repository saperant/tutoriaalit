# CI/CD-putket palveluille

Putki (*pipeline*) vie muutoksen versionhallinnasta tuotantoon samoin
askelin joka kerta: testit, kuvan rakennus, julkaisu rekisteriin ja
käyttöönotto. *Jatkuva integraatio* (CI) tarkoittaa, että jokainen
muutos rakennetaan ja testataan heti; *jatkuva toimitus* (CD), että
jokainen pääkehityshaaraan yhdistetty muutos on valmis tuotantoon, ja
*jatkuva käyttöönotto*, että se myös viedään sinne automaattisesti.
Tämä luku rakentaa käyntilaskurille putken ja rajautuu siihen, mitä
kontit putkelta vaativat. Itse käytännöt (haarojen ikä, trunk-pohjainen
kehitys, ominaisuusliput, tietokantamuutokset ja toimituskyvyn mittarit)
ovat taidossa *Jatkuva integraatio ja toimitus*.

## Käyntilaskurin putki

Esimerkkien `ci/palvelu.yml` on GitHub Actions -putki. Se on
tarkistettu GitHub Actionsin skeemaa vasten, mutta sitä ei ajeta
tämän tutoriaalin testeissä, koska julkaisu ja käyttöönotto vaativat
rekisterin ja klusterin. Putkessa on kolme työtä; kaavio on tuotettu
putkitiedostosta (`ci/putki_verkko.py`), ja testi tarkistaa sen:

```{.dot tiedosto="esimerkit/ci/putki.dot" otsikko="Käyntilaskurin putken työt. Pull requestille ajetaan vain testit; kuva julkaistaan ja otetaan käyttöön vain päähaarasta, ja käyttöönotto kulkee tuotantoympäristön suojausten läpi."}
```

Ensimmäinen työ ajaa testit:

```{.yaml tiedosto="esimerkit/ci/palvelu.yml" osa="testit"}
```

Testit ajetaan samalla komennolla kuin kehittäjän koneella (luku 3):
kuvan `testit`-vaihe ja hadolint. Kun kehittäjän ja putken komennot
ovat samat, "toimii minun koneellani" -ongelmat vähenevät.

Toinen työ rakentaa ja julkaisee kuvan vain päähaarasta:

```{.yaml tiedosto="esimerkit/ci/palvelu.yml" osa="kuva"}
```

- **Tagi on commitin tunniste.** Jokainen kuva on jäljitettävissä
  lähdekoodiin, eikä samaa tagia kirjoiteta koskaan yli. `latest` ei
  kerro mitään.
- **Vähimmät oikeudet.** Putken oletusoikeus on vain lukeminen;
  `packages: write` annetaan vain työlle, joka julkaisee kuvan.
- **SBOM ja alkuperä** syntyvät rakennuksen yhteydessä (luku 4).

Kolmas työ vie kuvan tuotantoon Helmillä (luku 9):

```{.yaml tiedosto="esimerkit/ci/palvelu.yml" osa="kayttoonotto"}
```

`environment: tuotanto` liittää työn GitHubin ympäristöön, jolle voi
määrätä hyväksyjät ja omat salaisuudet. `--atomic` peruu käyttöönoton,
jos uusi versio ei tule valmiiksi.

## Rakenna kerran, ota käyttöön monesti

Sama kuva kulkee testiympäristöstä tuotantoon. Kuvaa ei rakenneta
uudelleen jokaiselle ympäristölle, koska silloin tuotantoon menisi eri
kuva kuin testattiin. Ympäristöjen erot tulevat asetuksista (luku 5)
ja arvotiedostoista (luku 9). Tarkimmillaan käyttöönotto viittaa kuvaan
digestillä, jolloin rekisterin tagin vaihtaminen ei voi muuttaa
ajettavaa kuvaa.

## Käyttöönottostrategiat

| Strategia | Miten | Hyöty | Hinta |
|-----------|-------|-------|-------|
| rullaava | podit vaihdetaan vähitellen (luku 7) | yksinkertainen, oletus | molemmat versiot ajossa yhtä aikaa |
| sininen–vihreä | uusi ympäristö rinnalle, liikenne vaihdetaan kerralla | nopea paluu | kaksinkertaiset resurssit hetken |
| kanarialintu | pieni osa liikenteestä uudelle versiolle, mittareiden mukaan lisää | virhe näkyy pienelle joukolle | vaatii mittarit ja liikenteenohjauksen |
| ominaisuusliput | koodi tuotannossa, ominaisuus päälle erikseen | käyttöönotto ja julkaisu erillään | lippujen ylläpito |

![Uuden version osuus liikenteestä käyttöönoton aikana. Rullaavassa päivityksessä osuus kasvaa pod kerrallaan, sinisessä–vihreässä kaikki vaihtuu kerralla, ja kanarialinnussa osuutta kasvatetaan portaittain mittareiden salliessa. Periaatekuva, ei mittaus.](kuvat/11-strategiat.png){width=85%}

Strategioiden vaikutus virheiden näkyvyyteen on simuloitu taidossa
*Jatkuva integraatio ja toimitus*.

Rullaava päivitys ja sininen–vihreä vaativat, että kaksi versiota
toimii yhtä aikaa: tietokannan skeemamuutokset tehdään
taaksepäin yhteensopivasti (*expand–contract*: ensin lisätään, sitten
siirretään käyttö, lopuksi poistetaan vanha). Kanarialintu ja
automaattinen peruminen mittareiden perusteella onnistuvat esimerkiksi
Argo Rolloutsilla tai Flaggerilla.

## Putken turvallisuus

Putkella on oikeudet rekisteriin ja tuotantoon, joten se on
houkutteleva kohde:

- **Lyhytaikaiset tunnukset.** OIDC-federaatiolla putki saa pilvestä
  tunnuksen, joka on voimassa vain ajon ajan, eikä pitkäikäisiä
  avaimia tallenneta salaisuuksiksi.
- **Toimintojen kiinnitys.** Kolmannen osapuolen toiminnot
  (`uses: …@v4`) kiinnitetään tuotannossa commitin tiivisteeseen, koska
  tagin voi siirtää. Esimerkin versiotagit pitävät sen luettavana.
- **Pull requestien rajaus.** Ulkopuolisten pull requestit eivät saa
  salaisuuksia eivätkä kirjoitusoikeuksia.
- **Ympäristöjen suojaus.** Tuotannon käyttöönotto vaatii hyväksynnän
  ja onnistuu vain päähaarasta.

Laajemmin aihe on taidossa *Tietoturva kehitystyössä*.

## Käytännössä

- **Sama komento kehittäjälle ja putkelle.** Make-kohde tai kuvan
  testivaihe, ei putkeen kirjoitettua erillistä logiikkaa.
- **Nopea palaute ensin.** Tarkistimet ja yksikkötestit minuuteissa;
  hitaat testit rinnakkain tai myöhemmässä vaiheessa.
- **Kuva tunnisteella, joka ei muutu.** Commitin tunniste tai
  semanttinen versio ja digest; ei `latest`.
- **Käyttöönotto, joka osaa perua itsensä.** `--atomic`, valmiuskoettimet
  ja mittareihin perustuva peruminen.
- **Pieniä muutoksia usein.** Pieni muutos on helppo katselmoida,
  testata ja perua; harvat suuret julkaisut keräävät riskin yhteen.

## Itsearviointi

- Osaat rakentaa putken, joka testaa, rakentaa ja julkaisee kuvan ja
  ottaa sen käyttöön.
- Osaat perustella periaatteen "rakenna kerran, ota käyttöön monesti"
  ja kuvien tunnisteiden valinnan.
- Osaat valita käyttöönottostrategian ja kertoa, mitä se vaatii
  sovellukselta ja tietokannalta.
- Osaat suojata putken: vähimmät oikeudet, lyhytaikaiset tunnukset ja
  kiinnitetyt toiminnot.
