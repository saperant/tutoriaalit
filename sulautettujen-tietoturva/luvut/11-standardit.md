# Standardit ja sääntely

Sulautettujen laitteiden tietoturva on siirtymässä hyvästä tavasta
lakisääteiseksi. EU:ssa radiolaitteiden tietoturvavaatimukset ovat
olleet voimassa elokuusta 2025, ja kyberkestävyyssäädös koskee
kaikkia digitaalisia tuotteita joulukuusta 2027. Tämä luku kertoo,
mitä keskeiset standardit ja säädökset vaativat ja miten edellisten
lukujen tekniikat kytkeytyvät niihin. Lakitekstit muuttuvat ja niitä
tulkitaan; tarkista aina voimassa oleva versio.

## ETSI EN 303 645

Kuluttajalaitteiden (*consumer IoT*) kyberturvallisuuden
perusstandardi. Sen luvun 5 kolmetoista kohtaa ovat käytännönläheisiä:

```{.python tiedosto="esimerkit/11-vaatimukset.py" osa="etsi"}
```

Esimerkki jäljittää laitteen ominaisuudet kohtiin ja luettelee
puutteet:

```{.python tiedosto="esimerkit/11-vaatimukset.py" osa="laite"}
```

Suomessa Traficomin Kyberturvallisuusmerkki perustuu tähän
standardiin, ja EN 18031 viittaa samoihin periaatteisiin.

## EN 18031 ja radiolaitedirektiivi

Radiolaitedirektiivin (2014/53/EU) delegoitu asetus (EU) 2022/30 tuli
sovellettavaksi 1.8.2025. Se vaatii, että internetiin kytkeytyvät
radiolaitteet suojaavat verkkoa, henkilötietoja ja rahaliikennettä.
Harmonisoidut standardit EN 18031-1, -2 ja -3 kuvaavat vaatimukset:
pääsynhallinta, todennus, turvallinen päivitys, turvallinen tallennus ja
viestintä, kestävyys ja lokitus. Harmonisoidun standardin
noudattaminen antaa olettaman vaatimustenmukaisuudesta.

## IEC 62443

Teollisuusautomaation standardisarja. Laitevalmistajaa koskevat
erityisesti kaksi osaa:

- **IEC 62443-4-1** määrittelee turvallisen kehitysprosessin
  kahdeksana käytäntönä: tietoturvan hallinta, vaatimukset, turvallinen
  suunnittelu, turvallinen toteutus, testaus, haavoittuvuuksien
  käsittely, päivitysten hallinta ja käyttäjän ohjeistus.
- **IEC 62443-4-2** määrittelee komponenttien (sulautetut laitteet,
  verkkolaitteet, ohjelmistot) tekniset vaatimukset seitsemän
  perusvaatimuksen alle (tunnistus ja todennus, käytön hallinta,
  eheys, luottamuksellisuus, tietovirtojen rajaus, reagointi
  tapahtumiin, saatavuus) ja turvatasoille SL 1–4. Korkeampi taso
  olettaa kyvykkäämmän hyökkääjän.

## EU:n kyberkestävyyssäädös

Kyberkestävyyssäädös (*Cyber Resilience Act*, CRA, asetus (EU)
2024/2847) tuli voimaan 10.12.2024. Haavoittuvuuksien ja vakavien
poikkeamien **ilmoitusvelvollisuus** on ollut voimassa 11.9.2026
alkaen, ja muita velvoitteita sovelletaan 11.12.2027 alkaen. Se koskee kaikkia EU:ssa myytäviä tuotteita,
joissa on digitaalisia osia, ja edellyttää CE-merkintää.

Keskeiset vaatimukset valmistajalle:

- **Olennaiset tietoturvavaatimukset** (liite I): ei tunnettuja
  hyödynnettäviä haavoittuvuuksia julkaisuhetkellä, turvalliset
  oletusasetukset, suojaus luvattomalta pääsyltä, tietojen
  luottamuksellisuus ja eheys, minimaalinen hyökkäyspinta,
  tietoturvapäivitykset ja lokitus.
- **Haavoittuvuuksien käsittely**: ohjelmistoluettelo (SBOM),
  koordinoidun julkistamisen käytäntö, maksuttomat tietoturvapäivitykset.
- **Tukiaika**, jonka on vastattava odotettua käyttöaikaa ja oltava
  vähintään viisi vuotta, ellei tuotetta käytetä lyhyemmin.
- **Ilmoitukset** aktiivisesti hyödynnetyistä haavoittuvuuksista ja
  vakavista poikkeamista CSIRT-viranomaiselle ja ENISAlle yhteisen
  ilmoitusalustan kautta.

```{.python tiedosto="esimerkit/11-vaatimukset.py" osa="cra"}
```

```{.tuloste tiedosto="esimerkit/11-vaatimukset.odotettu"}
```

Määräajat ovat lyhyitä: varhainen varoitus 24 tunnin kuluessa siitä,
kun valmistaja sai tiedon hyödyntämisestä. Se onnistuu vain, jos
prosessi ja yhteystiedot ovat valmiina ennen ensimmäistä tapausta.
Tuotteet jaetaan luokkiin: useimmat arvioi valmistaja itse, mutta
tärkeille ja kriittisille tuotteille (esim. käyttöjärjestelmät,
verkkolaitteet, turvaelementit) vaaditaan standardin mukainen arviointi
tai kolmannen osapuolen sertifiointi.

## Sertifioinnit

**SESIP** (GlobalPlatform) ja **PSA Certified** ovat IoT-laitteiden ja
piirien sertifiointimalleja, joissa arvioinnin laajuus kasvaa tasoittain.
Turvaelementeille ja älykorteille käytetään **Common Criteria**
-arviointia (esim. EAL5+ ja AVA_VAN.5 eli korkean tason
hyökkääjä). Sertifioidun piirin käyttö ei tee tuotteesta sertifioitua,
mutta kattaa osan vaatimuksista.

## Käytännössä

- **Rakenna vaatimustenmukaisuus prosessiin.** CRA:n ja IEC 62443-4-1:n
  vaatimukset (uhkamalli, SBOM, haavoittuvuusprosessi, päivitykset) ovat
  samoja, joita tässä ja tutoriaalissa *Tietoturva kehitystyössä* on
  käyty läpi; dokumentoi ne kehityksen aikana.
- **Pidä ilmoitusprosessi valmiina.** Velvoite on jo voimassa:
  vastuuhenkilöt, yhteystiedot ja ilmoituspohjat ovat olemassa, ja
  prosessia on harjoiteltu ennen ensimmäistä oikeaa tapausta.
- **Päätä tukiaika tuotesuunnittelussa.** Se vaikuttaa komponenttien,
  kryptografian ja päivitysmekanismin valintaan.
- **Jäljitä vaatimukset.** Vaatimus–ratkaisu–testi-taulukko on
  vaatimustenmukaisuusarvioinnin perusta.

## Itsearviointi

- Osaat kertoa, mitä ETSI EN 303 645, EN 18031 ja IEC 62443 kattavat
  ja kenelle ne on tarkoitettu.
- Osaat luetella kyberkestävyyssäädöksen keskeiset velvoitteet ja
  aikataulun.
- Osaat jäljittää laitteen ominaisuudet standardin vaatimuksiin ja
  tunnistaa puutteet.
