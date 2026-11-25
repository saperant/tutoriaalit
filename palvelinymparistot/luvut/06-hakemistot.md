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

```{.dot otsikko="Esimerkin hakemistopuu. Merkinnän DN luetaan lehdestä juureen: `uid=aino,ou=ihmiset,dc=esimerkki,dc=fi`."}
digraph {
  rankdir=TB; nodesep=0.3; ranksep=0.35;
  j [label="dc=esimerkki,dc=fi"];
  i [label="ou=ihmiset"]; r [label="ou=ryhmat"];
  a [label="uid=aino\ninetOrgPerson,\nposixAccount"]; o [label="uid=olli\ninetOrgPerson,\nposixAccount"];
  y [label="cn=yllapito\nposixGroup"];
  j -> i; j -> r; i -> a; i -> o; r -> y;
}
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
vapaaseen porttiin. Ubuntun AppArmor-profiili rajaa järjestelmän
`slapd`-ohjelman tiedostot sen omiin hakemistoihin. Profiili liittyy
ohjelman polkuun, joten harjoitus ajaa ohjelmasta kopion; tuotannossa
käytetään järjestelmän palvelua ja sen profiilia:

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

```{.dot otsikko="Kerberos-todennuksen vaiheet. Käyttäjä kirjautuu KDC:lle kerran (1–2) ja hakee sen jälkeen lipun jokaista palvelua varten (3–4). Palvelu ei kysy KDC:ltä mitään, vaan tarkistaa lipun omalla avaimellaan (5–6)."}
digraph {
  layout=neato; splines=false;
  node [shape=point, width=0.01, height=0.01, style=invis];
  edge [arrowsize=0.7];
  a0 [label="asiakas (aino)", shape=box, style="rounded,filled", width=0, height=0.3, pos="0.00,0!"];
  aL [pos="0.00,-2.56!"];
  a0 -> aL [arrowhead=none, style=dotted];
  k0 [label="KDC", shape=box, style="rounded,filled", width=0, height=0.3, pos="2.90,0!"];
  kL [pos="2.90,-2.56!"];
  k0 -> kL [arrowhead=none, style=dotted];
  p0 [label="palvelu (tiedostot)", shape=box, style="rounded,filled", width=0, height=0.3, pos="5.80,0!"];
  pL [pos="5.80,-2.56!"];
  p0 -> pL [arrowhead=none, style=dotted];
  a1 [pos="0.00,-0.51!"]; k1_ [pos="2.90,-0.51!"];
  a1 -> k1_ [];
  t1 [shape=plain, style="", fontsize=9, label="1. kirjautuminen (salasana ei kulje verkossa)", pos="1.45,-0.41!"];
  k2 [pos="2.90,-0.87!"]; a2_ [pos="0.00,-0.87!"];
  k2 -> a2_ [];
  t2 [shape=plain, style="", fontsize=9, label="2. TGT (voimassa esim. 10 h)", pos="1.45,-0.77!"];
  a3 [pos="0.00,-1.23!"]; k3_ [pos="2.90,-1.23!"];
  a3 -> k3_ [];
  t3 [shape=plain, style="", fontsize=9, label="3. TGT + pyyntö: palvelu", pos="1.45,-1.13!"];
  k4 [pos="2.90,-1.59!"]; a4_ [pos="0.00,-1.59!"];
  k4 -> a4_ [];
  t4 [shape=plain, style="", fontsize=9, label="4. palvelulippu", pos="1.45,-1.49!"];
  a5 [pos="0.00,-1.95!"]; p5_ [pos="5.80,-1.95!"];
  a5 -> p5_ [];
  t5 [shape=plain, style="", fontsize=9, label="5. palvelulippu + todennin (aikaleima)", pos="1.45,-1.85!"];
  p6 [pos="5.80,-2.31!"]; a6_ [pos="0.00,-2.31!"];
  p6 -> a6_ [];
  t6 [shape=plain, style="", fontsize=9, label="6. pääsy, jos lippu ja aika kelpaavat", pos="4.35,-2.21!"];
}
```

Alla oleva esimerkki mallintaa vaiheet 4–6: KDC:n myöntämän
palvelulipun ja sen tarkistuksen palvelussa.

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
