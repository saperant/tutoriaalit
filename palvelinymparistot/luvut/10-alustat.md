# Virtualisointialustat ja klusterit

Harva palvelu ajetaan nykyään suoraan fyysisellä palvelimella.
Virtualisointialusta (VMware vSphere, Proxmox, Hyper-V, OpenStack) tai
Kubernetes-klusteri jakaa laitteiston palveluille ja siirtää kuorman
muualle, kun kone hajoaa tai sitä huolletaan. Virtualisoinnin tekniikka
(hypervisorit, laitteistotuki, kontit ytimen keinoin) on taidon
*Virtualisointi* aihe, ja Kubernetesin käyttö taidon *Kontit ja
pilvi-infrastruktuuri*.
Tämä luku käsittelee ylläpitäjän näkökulmaa: kapasiteettia, huoltoa ja
vikasietoisuutta.

## N+1: kestääkö klusteri yhden koneen menetyksen

Klusterin kapasiteetti ei ole koneiden summa. Jos yksi isäntä hajoaa
tai otetaan huoltoon, sen virtuaalikoneiden on mahduttava muille.
Mitoitusperiaate on **N+1**: klusterissa on yksi isäntä enemmän kuin
kuorma vaatii (suurissa klustereissa N+2).

Pelkkä kokonaistilan laskeminen ei riitä, koska virtuaalikone ei voi
jakautua usealle isännälle. Tarkistus kokeilee jokaisen isännän
poistamista ja sijoittaa sen koneet muille:

```{.python tiedosto="esimerkit/10-n-plus-1.py" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/10-n-plus-1.odotettu"}
```

Klusterissa on vapaata muistia yhteensä yli 800 Gt, mutta kun `esx3`
kaatuu, sen 448 Gt:n analytiikkakone ei mahdu millekään yksittäiselle
isännälle. Suuret virtuaalikoneet ovat klusterin mitoituksen yleisin
sudenkuoppa. Ratkaisuja ovat kapasiteetin varaaminen
korkean saatavuuden tarpeisiin (VMware HA:n admission control), suuren
koneen pilkkominen tai sen sijoittaminen klusteriin, jossa on
riittävästi isoja isäntiä.

Suorittimia voi ylivarata (esimerkissä 4 virtuaalista ydintä fyysistä
kohti), koska koneet harvoin kuormittavat kaikkia ytimiään yhtä aikaa.
Muistin ylivaraus on vaarallisempaa: sen loppuessa hypervisor alkaa
sivuttaa, ja kaikki koneet hidastuvat.

## Huoltokatkot ilman palvelukatkoa

Virtualisointialustalla isäntä huolletaan siirtämällä sen koneet ensin
muualle käynnissä (*live migration*, vMotion) ja asettamalla se
huoltotilaan. Kubernetes-klusterissa vastaava on solmun tyhjennys
(`kubectl drain`), joka siirtää podit muille solmuille.

Tyhjennys ei saa pudottaa sovellusta alle sen tarvitseman
kopiomäärän. Kubernetesissa sovelluksen omistaja ilmaisee tarpeen
*PodDisruptionBudgetilla* (PDB), esimerkiksi `minAvailable: 2`; tässä
katsotaan, mitä budjetti tekee ylläpitäjän huollolle. Tyhjennys odottaa, kunnes
budjetti sallii podin poistamisen:

```{.python tiedosto="esimerkit/10-huolto.py" osa="tyhjennys"}
```

```{.tuloste tiedosto="esimerkit/10-huolto.odotettu"}
```

Hakusovelluksella on kaksi kopiota ja vaatimus kahdesta käytettävästä.
Mitään solmua, jolla on hakukopio, ei voi tyhjentää, ja huolto jumittuu.
Kolmas kopio tekee huollon mahdolliseksi. PDB:n kanssa pätee sama kuin
N+1:n kanssa: vikasietoisuus vaatii aina yhden ylimääräisen.

## Klusterin ylläpito

Toistuvat ylläpitotehtävät:

| Tehtävä | Huomioitavaa |
|---------|--------------|
| Isäntien ja solmujen päivitys | Yksi kerrallaan: tyhjennys, päivitys, uudelleenkäynnistys, palautus |
| Klusterin version päivitys | Kubernetes tukee kolmea viimeisintä versiota; päivitys versio kerrallaan, ohjaustaso ennen solmuja |
| Varmuuskopiot | Kubernetes: etcd-tietokanta ja pysyvien taltioiden data; virtualisointi: alustan asetukset ja koneiden kuvat |
| Kapasiteetti | N+1 jokaisen muutoksen jälkeen; resurssipyynnöt (requests) Kubernetesissa vastaavat varattua tilaa |
| Sertifikaatit | Klusterin sisäiset varmenteet vanhenevat (Kubernetes: oletuksena vuosi) |

Hallittu Kubernetes (EKS, AKS, GKE) siirtää ohjaustason ylläpidon
palveluntarjoajalle, mutta solmujen päivitykset, kapasiteetti ja
sovellusten PDB:t jäävät käyttäjälle.

## Käytännössä

- **Mitoita N+1 ja tarkista se automaattisesti** jokaisen muutoksen
  jälkeen, ei vain hankinnan yhteydessä.
- **Varo suuria virtuaalikoneita.** Suurimman koneen on mahduttava
  yksittäiselle isännälle vian jälkeen.
- **PDB jokaiselle tuotantosovellukselle**, ja vähintään yksi kopio
  enemmän kuin PDB vaatii.
- **Huolto rutiiniksi.** Isäntä tai solmu, jota ei voi huoltaa ilman
  katkoa, on yksittäinen vikaantumispiste.
- **Kokeile vikaa.** Isännän sammuttaminen hallitusti testiympäristössä
  paljastaa, toimiiko korkea saatavuus.

## Itsearviointi

- Osaat selittää N+1-periaatteen ja tarkistaa, kestääkö klusteri
  yhden isännän menetyksen.
- Osaat kertoa, miksi suuret virtuaalikoneet ja muistin ylivaraus
  vaikeuttavat mitoitusta.
- Osaat selittää, miten live migration ja solmun tyhjennys mahdollistavat
  huollon ilman katkoa ja miten PodDisruptionBudget rajoittaa sitä.
- Osaat luetella klusterin toistuvat ylläpitotehtävät.
