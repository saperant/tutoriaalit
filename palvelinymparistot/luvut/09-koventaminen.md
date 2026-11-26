# Koventaminen ja päivitykset

Koventaminen (hardening) pienentää hyökkäyspintaa: palvelimella on vain
tarvittavat palvelut, ne ovat ajan tasalla, oletusasetukset on
tiukennettu ja kaikesta jää jälki. Koventaminen ei ole kertatyö vaan
tila, jota valvotaan, koska asennukset, käsin tehdyt muutokset ja uudet
haavoittuvuudet siirtävät konetta jatkuvasti pois siitä.

## Perusasiat

| Alue | Toimenpide |
|------|------------|
| Ohjelmistot | Vain tarvittavat paketit ja palvelut; `ss -tlnp` näyttää kuuntelevat portit |
| SSH | Ei pääkäyttäjän kirjautumista, ei salasanoja (vain avaimet), kirjautuminen ryhmiin rajattuna |
| Oikeudet | sudo yksittäisiin komentoihin ja lokiin, ei jaettuja tunnuksia |
| Palomuuri | Oletuksena esto, sallitaan vain tarvittava (ks. *Verkkoinfrastruktuuri*) |
| Päivitykset | Tietoturvapäivitykset automaattisesti, ytimen päivitys ja uudelleenkäynnistys hallitusti |
| Tiedostot | Kriittisten tiedostojen oikeudet, ei kaikkien kirjoitettavia tiedostoja |
| Kirjaus | Kirjautumiset ja sudo-käyttö keskitettyyn lokiin, auditd tärkeille tapahtumille |
| Palvelut | Jokainen palvelu omalla tunnuksellaan ja rajattuna yksikössään (luku *Palvelut ja systemd*) |

Tiukennuksille on valmiita tarkistuslistoja: **CIS Benchmarks**
käyttöjärjestelmittäin ja Suomessa **Kyberturvallisuuskeskuksen**
ohjeet. Ne numeroivat säännöt, jotta tarkastuksen tulos on vertailtava
ja poikkeukset voi dokumentoida säännön tunnisteella.

## Tarkastus koodina

Tarkastusskripti tekee jokaisesta säännöstä yhden tarkistuksen. Sille
annetaan juurihakemisto, joten samaa skriptiä voi käyttää
palvelimella, levykuvalla tai kontin tiedostojärjestelmällä:

```{.bash tiedosto="esimerkit/09-kovennus/tarkastus.sh" osa="saannot"}
```

```{.bash tiedosto="esimerkit/09-kovennus/tarkastus.sh" osa="tarkastus"}
```

Testi rakentaa kaksi järjestelmää, kovennetun ja kovennettamattoman, ja
ajaa tarkastuksen molemmille:

```{.bash tiedosto="esimerkit/09-kovennus/main.sh" osa="testi"}
```

```{.tuloste tiedosto="esimerkit/09-kovennus.odotettu"}
```

Paluuarvo kertoo tuloksen, joten tarkastus voidaan ajaa CI-putkessa
konekuvalle ennen käyttöönottoa ja valvonnassa ajossa oleville
koneille. Oikeassa ympäristössä käytetään usein valmista työkalua
(OpenSCAP, Lynis), mutta periaate on sama: koneellisesti tarkistettavat
säännöt ja niiden tulos raporttina.

Koventaminen tehdään konfiguraationhallinnalla (luku *Konfiguraationhallinta
Ansiblella*), ja tarkastus todentaa sen. Näin rooli kuvaa halutun
tilan ja tarkastus osoittaa, että tila pitää.

## Päivitykset

Useimmat murrot hyödyntävät tunnettuja haavoittuvuuksia, joihin on jo
korjaus. Päivitysprosessi:

- **Tietoturvapäivitykset automaattisesti.** Ubuntussa
  `unattended-upgrades` asentaa tietoturvakorjaukset päivittäin.
- **Uudelleenkäynnistys hallitusti.** Uusi ydin, C-kirjasto tai
  OpenSSL ei ole käytössä ennen uudelleenkäynnistystä tai palvelun
  käynnistystä. Ubuntu merkitsee tarpeen tiedostoon
  `/var/run/reboot-required`, ja `needrestart` kertoo palvelut, jotka
  käyttävät vanhoja kirjastoja.
- **Erissä.** Ensin testiympäristö, sitten pieni osa tuotannosta,
  sitten loput, jotta rikkova päivitys ei kaada kaikkea kerralla.
- **Tukiaika.** Käyttöjärjestelmäversion tuen päättyminen on
  suunniteltava projekti, ei yllätys.

Tilannekuva kerätään kaikilta koneilta:

```{.python tiedosto="esimerkit/09-paivitykset.py" osa="tilanne"}
```

```{.tuloste tiedosto="esimerkit/09-paivitykset.odotettu"}
```

Kone `web2` on päivitetty, mutta se ajaa yhä vanhaa ydintä: korjaus ei
suojaa ennen uudelleenkäynnistystä. Kone `vanha-ftp` on tuen
ulkopuolella, eikä siihen tule enää korjauksia lainkaan.

## Varmenteiden elinkaari

TLS-varmenne on kovennuksen osa, joka vanhenee itsestään. Palvelinten
välinen liikenne (hakemistoyhteydet, valvonta, tietokantayhteydet)
suojataan usein organisaation oman *sisäisen varmentajan* (CA)
myöntämillä varmenteilla, ja vanhentunut varmenne on yleinen
itse aiheutetun katkon syy. Hallinta noudattaa samoja periaatteita kuin
muukin tässä luvussa:

- **Inventaario.** Jokaisesta varmenteesta tiedetään, missä se on,
  kuka sen myönsi ja milloin se vanhenee.
- **Automaattinen uusiminen.** Lyhytikäiset varmenteet (viikkoja, ei
  vuosia) uusitaan protokollalla (ACME) tai konfiguraationhallinnalla,
  ei kalenterimuistutuksella. Lyhyt voimassaolo rajaa myös vuotaneen
  avaimen käyttöajan.
- **Valvonta.** Hälytys laukeaa, kun voimassaoloa on jäljellä alle
  sovitun rajan, ja se mittaa palvelun todella tarjoamaa varmennetta
  eikä levyllä olevaa tiedostoa.
- **Juuriavain erillään.** Varmentajan juuriavain pidetään irti
  verkosta, ja päivittäiset varmenteet myöntää välivarmentaja.

Varmenneketjut ja PKI:n rakenne ovat taidossa *Kryptografia*.

## Auditointi

Linuxin auditd kirjaa ytimen tasolla tapahtumat, joita sovellusloki ei
näe: kuka luki tiedoston `/etc/shadow`, kuka muutti sudo-asetuksia tai
ajoi ohjelman pääkäyttäjänä. Säännöt ovat tiedostossa
`/etc/audit/rules.d/`, esimerkiksi:

```text
-w /etc/sudoers -p wa -k sudo-muutos
-w /etc/ssh/sshd_config -p wa -k ssh-asetukset
-a always,exit -F arch=b64 -S execve -F euid=0 -k pääkäyttäjänä
```

Kirjaukset siirretään keskitettyyn lokipalveluun, jotta murtautuja ei
voi poistaa jälkiään koneelta (ks. luku *Valvonta ja palvelutasot*).

## Käytännössä

- **Perustaso koodina.** Koventaminen on rooli konfiguraationhallinnassa,
  ja jokainen uusi kone saa sen automaattisesti.
- **Tarkastus koneellisesti.** Säännöt tarkistetaan CI:ssä ja
  ajossa olevilta koneilta; poikkeukset dokumentoidaan säännön
  tunnisteella ja perusteluineen.
- **Päivitykset rutiiniksi.** Automaattiset tietoturvapäivitykset,
  aikataulutetut uudelleenkäynnistykset ja hälytys koneista, jotka
  odottavat uudelleenkäynnistystä.
- **Vähemmän on turvallisempaa.** Jokainen poistettu paketti ja
  suljettu portti on asia, jota ei tarvitse päivittää eikä valvoa.
- **Varmenteet uusiutuvat itse.** Voimassaoloa valvotaan, ja
  uusiminen on automatisoitu; käsin uusittava varmenne unohtuu.
- **Jäljet talteen muualle.** Lokit ja auditointi keskitettyyn
  palveluun, jonne kohdekoneelta voi vain kirjoittaa.

## Itsearviointi

- Osaat luetella palvelimen koventamisen keskeiset osa-alueet ja
  perustella ne.
- Osaat kirjoittaa koventamisen tarkastuksen, jonka säännöt tuottavat
  vertailtavan raportin ja paluuarvon.
- Osaat suunnitella päivitysprosessin, joka huomioi uudelleenkäynnistykset
  ja vaiheittaisen käyttöönoton.
- Osaat kertoa, mitä auditd kirjaa ja miksi kirjaukset siirretään pois
  koneelta.
- Osaat kuvata sisäisten varmenteiden elinkaaren: inventaario,
  automaattinen uusiminen ja vanhenemisen valvonta.
