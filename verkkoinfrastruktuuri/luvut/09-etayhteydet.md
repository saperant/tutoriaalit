# VPN ja etäkäyttö

Toimipisteet yhdistetään toisiinsa ja etätyöntekijät organisaation
verkkoon salatuilla tunneleilla (VPN). Palvelimia ja verkkolaitteita
hallitaan etäyhteyksillä, jotka ovat hyökkääjän ensisijainen kohde:
ylläpitoyhteys on avain kaikkeen muuhun. Tässä luvussa rakennetaan
WireGuard-tunneli kahden toimipisteen välille ja hyppykoneen kautta
kulkeva SSH-ylläpitoyhteys.

## VPN-tyypit

- **Toimipisteiden välinen** (*site-to-site*): yhdyskäytävät muodostavat
  pysyvän tunnelin, ja lähiverkot reitittävät toisiinsa sen kautta.
  Laitteiden ei tarvitse tietää tunnelista.
- **Etäkäyttö** (*remote access*): käyttäjän laitteen asiakasohjelma
  avaa tunnelin organisaation yhdyskäytävälle.
- **Nollaluottamuksen pääsy** (*zero trust network access*, ZTNA):
  verkkoon ei päästetä ollenkaan, vaan jokaiseen sovellukseen
  pääsy myönnetään erikseen käyttäjän ja laitteen tilan perusteella.
  Tähän palataan taidossa *Palveluarkkitehtuurin tietoturva*.

Yleisimmät protokollat ovat **IPsec** (standardi, laaja tuki
verkkolaitteissa, monimutkainen), **WireGuard** (yksinkertainen,
nykyaikainen kryptografia, Linuxin ytimessä) ja TLS-pohjaiset ratkaisut
(OpenVPN, valmistajien SSL-VPN:t).

## WireGuard

WireGuard on tarkoituksella pieni: ei algoritmineuvottelua, ei
varmenteita, ei käyttäjätunnuksia. Jokaisella päällä on avainpari, ja
vastapuolet tunnetaan julkisista avaimistaan, kuten SSH:ssa.

```{.bash tiedosto="esimerkit/09-wireguard.sh" osa="avaimet"}
```

Tunnelin keskeinen käsite on **sallitut osoitteet** (*allowed IPs*).
Lähtevälle liikenteelle se on reititystaulu: mihin vastapäähän
lähetetään paketti tähän kohteeseen. Saapuvalle liikenteelle se on
suodatin: vastapäästä hyväksytään vain paketit, joiden lähdeosoite on
sen sallituissa osoitteissa. Yksi asetus ratkaisee siis sekä reitityksen
että kenen nimissä paketti saa tulla (*cryptokey routing*).

```{.bash tiedosto="esimerkit/09-wireguard.sh" osa="tunneli"}
```

```{.bash tiedosto="esimerkit/09-wireguard.sh" osa="tila"}
```

```{.tuloste tiedosto="esimerkit/09-wireguard.odotettu"}
```

Laboratoriossa käytetään käyttäjätilan toteutusta `wireguard-go`, koska
kaikkien testiympäristöjen ytimissä ei ole WireGuard-moduulia.
Asetukset ovat samat kuin ytimen toteutuksessa, jota tuotannossa
käytetään. Pysyvä asetus kirjoitetaan tavallisesti `wg-quick`-tiedostoon
tai systemd-networkdin asetuksiin.

`persistent-keepalive` pitää tunnelin auki NAT:n ja tilallisen palomuurin
läpi: ilman liikennettä palomuurin tila vanhenee, eikä vastapää pääse
enää aloittamaan yhteyttä.

## IPsec

IPsec on verkkolaitteiden yhteinen kieli: kun toimipiste yhdistetään
pilvipalvelun tai toisen organisaation verkkoon, toinen pää on yleensä
IPsec. Linuxissa sitä hallitaan strongSwanilla. Tunnelin asetukset
(IKEv2, varmenteet, sallitut verkot) näyttävät tältä; esimerkkiä ei ajeta
automaattisesti, koska testiympäristöjen ytimissä ei ole ESP-muunnosta:

```text
connections {
    toimipiste-b {
        version = 2
        remote_addrs = 198.51.100.2
        local {
            auth = pubkey
            certs = gwa.pem
            id = gwa.esimerkki.fi
        }
        remote {
            auth = pubkey
            id = gwb.esimerkki.fi
        }
        children {
            lan {
                local_ts = 10.1.0.0/24
                remote_ts = 10.2.0.0/24
                esp_proposals = aes256gcm16-x25519
                start_action = start
            }
        }
        proposals = aes256-sha256-x25519
    }
}
```

IPsecin yleisimmät viat ovat ristiriitaiset ehdotukset (algoritmit ja
elinajat eri päissä), väärin määritetyt liikenteen valitsimet (`local_ts`,
`remote_ts`) ja NAT:n takana unohtunut NAT-T (UDP 4500).

## Ylläpitoyhteydet hyppykoneen kautta

Palvelinten ja verkkolaitteiden hallintaliitäntöihin ei avata suoraa
yhteyttä käyttäjäverkosta saati internetistä. Ylläpitäjä yhdistää
**hyppykoneelle** (*bastion*, *jump host*), joka on ainoa reitti
hallintaverkkoon ja jonka kaikki istunnot kirjataan. Hyppykone ei
reititä: sisäverkkoon pääsee vain sen SSH-palvelun kautta.

```{.bash tiedosto="esimerkit/09-hyppykone.sh" osa="palvelimet"}
```

Asiakkaan asetuksissa `ProxyJump` avaa yhteyden kohteeseen hyppykoneen
läpi. Yhteys salataan päästä päähän ylläpitäjän koneelta kohteeseen, ja
myös kohteen palvelinavain tarkistetaan; hyppykone näkee vain salatun
virran. Ylläpitäjän yksityinen avain ei koskaan käy hyppykoneella, toisin
kuin agentin välityksessä (`ForwardAgent`), jota ei siksi käytetä.

```{.bash tiedosto="esimerkit/09-hyppykone.sh" osa="asiakas"}
```

```{.bash tiedosto="esimerkit/09-hyppykone.sh" osa="kokeilu"}
```

```{.tuloste tiedosto="esimerkit/09-hyppykone.odotettu"}
```

`StrictHostKeyChecking yes` ja ennalta jaettu `known_hosts` estävät
välimieshyökkäyksen. Kun palvelinavainten jakelu on keskitetty,
käytetään SSH-varmenteita: varmentaja allekirjoittaa palvelinten ja
käyttäjien avaimet, ja luottamus perustuu varmentajaan.

## RDP ja graafinen etäkäyttö

Windows-työpöydän etäkäyttö (RDP, TCP 3389) on yksi
kiristyshaittaohjelmien yleisimmistä sisääntuloreiteistä. RDP:tä ei
koskaan julkaista internetiin. Etäkäyttö kulkee VPN:n tai RD Gatewayn
(RDP HTTPS:n sisällä, monivaiheinen tunnistus) kautta, ja
verkkotason todennus (NLA) on pakollinen. Sama koskee kaikkia graafisia
hallintakäyttöliittymiä: ne ovat hallintaverkossa.

## Käytännössä

- **Ei hallintaliitäntöjä internetiin.** SSH, RDP, verkkolaitteiden
  web-käyttöliittymät ja palvelinten BMC:t (IPMI, iDRAC, iLO) ovat
  hallintaverkossa, johon pääsee VPN:n ja hyppykoneen kautta.
- **Vain avaintodennus ja monivaiheinen tunnistus.** SSH:ssa
  salasanakirjautuminen pois, VPN:ssä varmenne tai avain ja toinen
  tekijä.
- **Hyppykone kirjaa istunnot** ja on itse kovennettu, päivitetty ja
  valvottu. Se on verkon arvokkain kohde.
- **Tunnelin sallitut verkot tarkasti.** VPN, joka päästää etäkäyttäjän
  koko sisäverkkoon, siirtää käyttäjän laitteen riskit sisäverkkoon.
- **Avainten kierto.** Avaimet ja varmenteet vanhenevat ja vaihdetaan
  automaattisesti; lähtevän työntekijän avaimet poistetaan heti.
- **Tunnelin valvonta.** Viimeisimmän kättelyn aika ja siirretyt tavut
  kertovat, onko tunneli käytössä ja toimiiko se.

## Itsearviointi

- Osaat erottaa toimipisteiden välisen VPN:n, etäkäytön VPN:n ja
  sovelluskohtaisen nollaluottamuksen pääsyn.
- Osaat rakentaa WireGuard-tunnelin kahden verkon välille ja selittää
  sallittujen osoitteiden kaksoisroolin.
- Osaat lukea IPsec-tunnelin asetukset ja tunnistaa yleisimmät
  yhteensopivuusviat.
- Osaat järjestää ylläpitoyhteydet hyppykoneen kautta ProxyJumpilla,
  avaintodennuksella ja palvelinavainten tarkistuksella.
