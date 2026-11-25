# TLS 1.3

TLS (*Transport Layer Security*) on verkon yleisin
kryptografinen protokolla: HTTPS, sähköpostin siirto, tietokantayhteydet
ja palvelujen väliset kutsut käyttävät sitä. TLS 1.3 (RFC 8446, 2018)
yksinkertaisti protokollaa voimakkaasti: vanhat algoritmit poistettiin,
kättely lyheni yhteen edestakaiseen matkaan, ja kaikki yhteydet saavat
eteenpäin salaisuuden.

## Kättely

TLS 1.3 -kättely yhdistää edellisten lukujen palikat. Kaaviossa
aaltosulkeissa olevat viestit on salattu kättelyavaimilla ja
hakasulkeissa olevat sovellusdatan avaimilla (merkintä on RFC 8446:n):

```{.dot otsikko="TLS 1.3 -kättely. Vain kaksi ensimmäistä viestiä kulkee selväkielisenä."}
digraph {
  nodesep=0.5; ranksep=0.3;
  node [shape=point, width=0.04, color="#5B6B70"];
  edge [arrowhead=none, style=dashed, color="#B8C4C8", weight=100];
  t0 [shape=box, width=1.0, label="asiakas"];
  t0 -> t0_0 -> t0_1 -> t0_2 -> t0_3 -> t0_4 -> t0_5 -> t0_6 -> t0_7 -> t0_8 -> t0_9;
  t1 [shape=box, width=1.0, label="palvelin"];
  t1 -> t1_0 -> t1_1 -> t1_2 -> t1_3 -> t1_4 -> t1_5 -> t1_6 -> t1_7 -> t1_8 -> t1_9;
  {rank=same; t0 -> t1 [style=invis, weight=1];}
  {rank=same; t0_0; t1_0;}
  {rank=same; t0_1; t1_1;}
  {rank=same; t0_2; t1_2;}
  {rank=same; t0_3; t1_3;}
  {rank=same; t0_4; t1_4;}
  {rank=same; t0_5; t1_5;}
  {rank=same; t0_6; t1_6;}
  {rank=same; t0_7; t1_7;}
  {rank=same; t0_8; t1_8;}
  {rank=same; t0_9; t1_9;}
  edge [style=solid, arrowhead=normal, color="#1F2A2E", constraint=false, weight=1];
  t0_0 -> t1_1 [label="ClientHello: salausjoukot, avainosuus, palvelimen nimi"];
  t1_1 -> t0_2 [label="ServerHello: valittu salausjoukko, avainosuus"];
  t1_2 -> t0_3 [label="{EncryptedExtensions}"];
  t1_3 -> t0_4 [label="{Certificate}: varmenneketju"];
  t1_4 -> t0_5 [label="{CertificateVerify}: allekirjoitus kättelystä"];
  t1_5 -> t0_6 [label="{Finished}: MAC kättelystä"];
  t0_6 -> t1_7 [label="{Finished}"];
  t0_7 -> t1_8 [label="[sovellusdata]"];
  t1_8 -> t0_9 [label="[sovellusdata]"];
}
```

Viestit vaiheittain:

1. **ClientHello**: asiakas lähettää tukemansa salausjoukot ja
   avaintenvaihdon julkisen avaimen (*key share*, esim. X25519 tai
   hybridi X25519MLKEM768) sekä palvelimen nimen (SNI).
2. **ServerHello**: palvelin valitsee salausjoukon ja lähettää oman
   julkisen avaimensa. Molemmat laskevat jaetun salaisuuden, ja tästä
   eteenpäin kaikki on salattua.
3. **Certificate** ja **CertificateVerify**: palvelin lähettää
   varmenneketjunsa ja allekirjoittaa siihenastisen kättelyn
   tiivisteen. Allekirjoitus todentaa avaintenvaihdon ja estää
   välimieshyökkäyksen.
4. **Finished**: molemmat lähettävät MAC:n koko kättelystä. Se
   paljastaa, jos joku on muuttanut kättelyviestejä.

Salausjoukkoja on vain viisi, ja ne kertovat vain AEAD:n ja
tiivistefunktion: `TLS_AES_128_GCM_SHA256`, `TLS_AES_256_GCM_SHA384` ja
`TLS_CHACHA20_POLY1305_SHA256` ovat käytössä. Avaintenvaihto ja
allekirjoitus neuvotellaan erikseen.

## Avainaikataulu

Kaikki TLS 1.3:n avaimet johdetaan HKDF:llä. Jokainen johdettu avain
sidotaan nimikkeeseen ja kättelyn tiivisteeseen, joten eri
tarkoituksiin ja eri yhteyksiin syntyy eri avaimet:

```{.python tiedosto="esimerkit/10-avainaikataulu.py" osa="label"}
```

```{.python tiedosto="esimerkit/10-avainaikataulu.py" osa="aikataulu"}
```

```{.tuloste tiedosto="esimerkit/10-avainaikataulu.odotettu"}
```

Arvot täsmäävät RFC 8448:n esimerkkikättelyyn. Aikataulu etenee
kolmessa vaiheessa: *early secret* (esijaettu avain tai nollat),
*handshake secret* (lisätään avaintenvaihdon tulos) ja *master secret*,
josta johdetaan sovellusdatan avaimet kumpaankin suuntaan.

```{.dot otsikko="TLS 1.3:n avainaikataulu. Vasemmalta tulee uutta salaista syötettä ja oikealle johdetaan liikenneavaimet. Jokainen johdettu avain sidotaan kättelyn siihenastisiin viesteihin."}
digraph {
  nodesep=0.3; ranksep=0.3;
  node [width=1.5];
  early [label="early secret"]; hs [label="handshake secret"];
  master [label="master secret"];
  node [shape=plain, style="", width=0];
  psk [label="esijaettu avain\rtai nollat\r"]; dhe [label="avaintenvaihdon\rtulos\r"];
  nollat [label="nollat"];
  chs [label="kättelyn liikenneavaimet\l(asiakas ja palvelin)\l"];
  cap [label="sovellusdatan avaimet\l(asiakas ja palvelin)\l"];
  res [label="istunnon jatkamisen\nsalaisuus"];
  early -> hs [label="derived"]; hs -> master [label="derived"];
  { rank=same; psk -> early; }
  { rank=same; dhe -> hs -> chs; }
  { rank=same; nollat -> master -> cap; }
  master -> res;
}
```

Kummallakin suunnalla on oma liikenneavaimensa, ja tietueen nonce
muodostetaan järjestysnumerosta. Nämä ovat luvun 4 turvallisen kanavan
kaksi keinoa toistoa, järjestyksen vaihtoa ja palautusta vastaan.

## TLS Pythonilla

Esimerkki luo testivarmentajan ja palvelinvarmenteen (luku 9),
käynnistää TLS-palvelimen ja yhdistää siihen kolmesti:

```{.python tiedosto="esimerkit/10-tls.py" osa="palvelin"}
```

```{.python tiedosto="esimerkit/10-tls.py" osa="asiakas"}
```

```{.python tiedosto="esimerkit/10-tls.py" osa="kokeet"}
```

```{.tuloste tiedosto="esimerkit/10-tls.odotettu"}
```

`ssl.create_default_context()` tarkistaa varmenneketjun ja nimen
oletuksena. Ilman `cafile`-parametria se käyttää käyttöjärjestelmän
juurivarmenteita, joihin testivarmentaja ei kuulu, joten yhteys
hylätään.

## Muuta TLS 1.3:sta

- **0-RTT** (*early data*): asiakas voi lähettää dataa jo
  ensimmäisessä viestissä, kun yhteys jatkaa aiempaa istuntoa. Data
  voidaan kuitenkin toistaa (*replay*), joten 0-RTT sopii vain
  idempotenteille pyynnöille.
- **Molemminpuolinen TLS (mTLS)**: myös asiakas esittää varmenteen.
  Sitä käytetään palvelujen välisessä liikenteessä ja laitteiden
  tunnistuksessa (taito *Palveluarkkitehtuurin tietoturva*).
- **ECH** (*Encrypted Client Hello*) salaa myös palvelimen nimen, joka
  muuten näkyy verkossa selväkielisenä.
- **QUIC** ja HTTP/3 käyttävät TLS 1.3:n kättelyä UDP:n päällä.

Samat palikat löytyvät muistakin protokollista. **SSH** tekee
avaintenvaihdon (nykyään Curve25519, hybridinä ML-KEM:n kanssa),
todentaa palvelimen allekirjoituksella ja suojaa liikenteen AEAD:lla.
Ero on avaimen alkuperän varmistamisessa: SSH ei oletuksena käytä
varmentajia, vaan asiakas tallentaa palvelimen julkisen avaimen
ensimmäisellä yhteydellä tiedostoon `known_hosts` ja varoittaa, jos se
myöhemmin muuttuu (*trust on first use*). Ensimmäisen yhteyden
sormenjälki on siksi tarkistettava muuta kanavaa pitkin, tai
organisaatio ottaa käyttöön SSH-varmenteet. WireGuard puolestaan
kiinnittää algoritmit kokonaan eikä neuvottele mistään.

## Käytännössä

- **TLS 1.2 ja 1.3, ei vanhempia.** TLS 1.0 ja 1.1 on poistettu
  (RFC 8996). TLS 1.2:ssa sallitaan vain AEAD-salausjoukot ja
  ECDHE-avaintenvaihto.
- **Asetukset valmiista lähteestä.** Mozillan SSL Configuration
  Generator antaa palvelinasetukset; ohjelmointikielissä kirjaston
  oletuskonteksti on yleensä paras.
- **TLS päättyy kuormantasaajaan?** Silloin kuormantasaajan ja
  palvelun välinen liikenne on suojaamatonta, ellei sitä salata
  erikseen. Nollaluottamuksen mallissa salataan myös sisäverkko.
- **Testaus:** `openssl s_client -connect palvelu:443 -servername
  palvelu` näyttää ketjun ja neuvotellut algoritmit, `testssl.sh` ja
  SSL Labs arvioivat asetukset.
- **Hinta:** TLS 1.3 -kättely vie yhden edestakaisen matkan ja muutaman
  millisekunnin laskentaa; istunnon jatkaminen poistaa senkin.
  Salauksen hinta on nykylaitteistolla mittausvirheen luokkaa.

## Itsearviointi

- Osaat kuvata TLS 1.3 -kättelyn vaiheet ja mihin kunkin vaiheen
  kryptografia perustuu.
- Osaat selittää, miten avainaikataulu johtaa avaimet HKDF:llä.
- Osaat muodostaa TLS-yhteyden omalla varmentajalla ja tulkita
  varmennevirheet.
- Osaat arvioida 0-RTT:n ja mTLS:n käyttökohteet ja riskit.
