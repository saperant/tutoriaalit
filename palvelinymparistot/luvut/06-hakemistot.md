# Käyttäjähallinta ja hakemistot

Yhdellä koneella käyttäjät ovat tiedostoissa `/etc/passwd` ja
`/etc/shadow`. Sadalla koneella paikalliset käyttäjät tarkoittavat
sataa paikkaa, joista lähtevän työntekijän tunnus on poistettava, ja
sataa eri salasanaa. Siksi käyttäjät ja ryhmät keskitetään
*hakemistopalveluun*, ja koneet kysyvät sieltä, kuka käyttäjä on ja
mihin ryhmiin hän kuuluu.

## LDAP-hakemisto

LDAP (lightweight directory access protocol) on hakemistojen
standardiprotokolla. Hakemisto on puu, jonka jokaisella merkinnällä on
yksilöivä nimi (DN, distinguished name):

```text
dc=esimerkki,dc=fi
├── ou=ihmiset
│   ├── uid=aino      (inetOrgPerson, posixAccount)
│   └── uid=olli
└── ou=ryhmat
    └── cn=yllapito   (posixGroup)
```

Merkinnän attribuutit määrää sen objektiluokka (objectClass):
`inetOrgPerson` antaa nimen ja sähköpostin, `posixAccount` Linux-koneen
tarvitsemat UID:n, kotihakemiston ja kuoren. Merkinnät kirjoitetaan
LDIF-muodossa:

```{.ldif tiedosto="esimerkit/06-ldap/hakemisto.ldif" osa="kayttaja"}
```

```{.ldif tiedosto="esimerkit/06-ldap/hakemisto.ldif" osa="ryhma"}
```

Esimerkki käynnistää OpenLDAP-palvelimen (`slapd`) tilapäishakemistoon
vapaaseen porttiin. Ubuntun AppArmor-profiili sallii slapd:lle
hakemiston `/var/tmp`, joten tilapäishakemisto luodaan sinne:

```{.bash tiedosto="esimerkit/06-ldap/main.sh" osa="kaynnistys"}
```

Hakemistoon lisätään merkinnät ylläpitäjän tunnuksilla, ja niitä
haetaan suodattimilla. Suodatin `(&(objectClass=posixGroup)(cn=yllapito))`
on LDAP:n kyselykieltä: etuliitemuotoinen JA-ehto.

```{.bash tiedosto="esimerkit/06-ldap/main.sh" osa="lisays"}
```

```{.bash tiedosto="esimerkit/06-ldap/main.sh" osa="haku"}
```

## Todennus ja pääsynhallinta

Kirjautuminen LDAP:iin on *bind*-operaatio: asiakas lähettää DN:n ja
salasanan, ja palvelin vertaa salasanaa merkinnän tallennettuun
tiivisteeseen. Hakemiston pääsynhallintasäännöt (ACL) päättävät, mitä
kukin saa lukea ja muuttaa:

```{.text tiedosto="esimerkit/06-ldap/slapd.conf" osa="acl"}
```

```{.bash tiedosto="esimerkit/06-ldap/main.sh" osa="kirjautuminen"}
```

```{.bash tiedosto="esimerkit/06-ldap/main.sh" osa="oikeudet"}
```

```{.tuloste tiedosto="esimerkit/06-ldap.odotettu"}
```

Aino näkee Ollin sähköpostin, mutta ei hänen salasanatiivistettään,
eikä anonyymi käyttäjä näe mitään. Tuotannossa yhteydet salataan aina
(`ldaps://` tai StartTLS), koska simple bind lähettää salasanan
sellaisenaan.

## Kerberos

LDAP-bind lähettää salasanan palvelimelle joka kirjautumisella.
Kerberos välttää sen: käyttäjä todentaa itsensä kerran avainjakelukeskukselle
(KDC) ja saa *lipun* (ticket-granting ticket), jolla hän hakee
palvelukohtaisia lippuja. Palvelu tarkistaa lipun omalla avaimellaan
(*keytab*), eikä salasana kulje verkossa. Todennin sisältää aikaleiman,
joten kellojen on oltava tahdissa:

```{.python tiedosto="esimerkit/06-kerberos.py" osa="palvelu"}
```

```{.python tiedosto="esimerkit/06-kerberos.py" osa="kokeet"}
```

```{.tuloste tiedosto="esimerkit/06-kerberos.odotettu"}
```

Esimerkki on yksinkertaistettu: liput on allekirjoitettu HMAC:lla
mutta ei salattu, ja KDC:n vaiheet on yhdistetty. Periaatteet ovat
samat kuin oikeassa Kerberoksessa: lipun voimassaoloaika, todentimen
aikaleima ja toistojen esto. Viiden minuutin raja selittää, miksi
toimialueen koneiden NTP-tahdistus on kriittinen palvelu: kellon
ajautuminen estää kaikki kirjautumiset.

## Active Directory ja SSSD

Microsoftin **Active Directory** (AD) on LDAP-hakemisto, Kerberos-KDC
ja DNS yhdessä, ja lisäksi ryhmäkäytännöt (group policy) Windows-koneiden
hallintaan. Useimmissa organisaatioissa Linux-palvelimet liitetään
olemassa olevaan AD:hen eikä niille rakenneta omaa hakemistoa.

Linux-koneella yhteys hakemistoon hoidetaan **SSSD**-palvelulla (system
security services daemon). Se:

- liittää koneen toimialueeseen (`realm join esimerkki.fi`) ja
  hakee koneelle keytabin,
- tarjoaa käyttäjät ja ryhmät järjestelmälle (NSS: `getent passwd
  aino`) ja todennuksen PAMille,
- tallentaa tunnistetiedot välimuistiin, jotta kirjautuminen toimii
  hetken myös hakemistoyhteyden katketessa,
- rajaa kirjautumisen ryhmiin (`simple_allow_groups = yllapito`).

SSSD:n asetukset ovat tiedostossa `/etc/sssd/sssd.conf`, ja niiden
oikeuksien on oltava `600`, muuten palvelu ei käynnisty.

## Käytännössä

- **Yksi lähde käyttäjille.** Lähtevän työntekijän tunnus suljetaan
  yhdestä paikasta, ja se lakkaa toimimasta kaikkialla.
- **Ryhmät oikeuksien perustaksi.** Oikeudet annetaan ryhmille
  (`yllapito`, `tietokanta-luku`), ei henkilöille.
- **Salaa yhteydet** ja tallenna salasanat vain tiivisteinä.
- **Palvelutunnukset erikseen.** Sovellukset tunnistautuvat omilla
  tunnuksillaan, joilla on vain tarvittavat oikeudet.
- **Ajan tahdistus** kaikille koneille; Kerberos ja lokien vertailu
  vaativat sitä.
- **Hätätunnus.** Paikallinen, valvottu hätätunnus koneille, joille
  pitää päästä hakemiston ollessa alhaalla.

## Itsearviointi

- Osaat kuvata LDAP-hakemiston rakenteen, objektiluokat ja LDIF-muodon
  ja tehdä hakuja suodattimilla.
- Osaat selittää LDAP-bindin ja pääsynhallintasääntöjen toiminnan.
- Osaat kertoa, miten Kerberos-lippu toimii ja miksi kellojen
  tahdistus on välttämätön.
- Osaat kuvata Active Directoryn osat ja SSSD:n tehtävän Linux-koneen
  liittämisessä hakemistoon.
