# Synkronointi

Kun kaksi säiettä tai prosessia käyttää samaa dataa ja ainakin toinen
kirjoittaa, lopputulos riippuu suoritusjärjestyksestä. Tällainen
*kilpatilanne* (engl. race condition) syntyy jo yksinkertaisesta
`laskuri++`-lauseesta, joka on kolme konekäskyä: luku, lisäys ja
kirjoitus. Jos kaksi säiettä lukee saman arvon ennen kuin kumpikaan
kirjoittaa, toinen lisäys katoaa. C-kielen taidossa ilmiö nähtiin
ThreadSanitizerin avulla ja korjattiin mutexilla. Tässä luvussa
katsotaan synkronoinnin perusvälineitä käyttöjärjestelmän kannalta ja
ratkaistaan niillä kaksi klassista ongelmaa.

Koodin osaa, jossa jaettua dataa käytetään, kutsutaan *kriittiseksi
alueeksi*. Ratkaisun on täytettävä kolme ehtoa:

1. **Poissulkeminen:** enintään yksi säie kerrallaan kriittisellä
   alueella.
2. **Eteneminen:** jos alue on vapaa ja joku haluaa sinne, joku
   pääsee – päätöstä ei lykätä loputtomiin.
3. **Rajattu odotus:** kukaan ei odota loputtomasti muiden ohittaessa.

## Lukkojen toteutus

Käytännössä lukot rakennetaan laitteiston *atomisista
käskyistä*: vertaa ja vaihda (CAS), RISC-V:n `lr`/`sc`-pari tai
x86:n `lock cmpxchg`. Spinlukko pyörii CAS-silmukassa, kunnes lukko
vapautuu. Se on hyvä, kun odotus on lyhyt ja säikeitä on vähemmän kuin
suorittimia – ytimessä keskeytyskäsittelijöiden välillä – mutta
tuhlaa suoritinta, jos lukon haltija on estynyt tai vuorontaja on
keskeyttänyt sen.

Linuxin pthread-mutex on *futex* (fast userspace mutex): lukitus
yrittää ensin atomisella käskyllä käyttäjätilassa, ja vasta kilpailun
sattuessa säie pyytää ydintä nukuttamaan sen `futex`-kutsulla.
Kilpailematon lukitus ei siis vaadi järjestelmäkutsua lainkaan. Sama
mekanismi on ehtomuuttujien, semaforien ja esteiden pohjana.
Muistimallit ja lukottomat rakenteet ovat taidon
*Rinnakkaisohjelmointi* aihe.

## Mutex ja ehtomuuttuja

Mutex antaa poissulkemisen. Ehtomuuttuja antaa *odottamisen*: säie voi
nukkua, kunnes jokin ehto jaetussa datassa muuttuu. `pthread_cond_wait`
vapauttaa mutexin ja nukahtaa *atomisesti*, jolloin herätys ei voi
mennä ohi lukituksen ja nukahtamisen välissä, ja lukitsee mutexin
uudelleen ennen paluuta. Ehto tarkistetaan aina `while`-silmukassa,
koska

- herätys voi olla *aiheeton* (engl. spurious wakeup): POSIX sallii
  sen, ja futex-toteutuksissa se on mahdollista,
- toinen säie voi ehtiä muuttaa tilaa herätyksen ja lukituksen välissä,
- `broadcast` herättää kaikki, vaikka vain yksi saa työtä.

### Tuottaja–kuluttaja

Rajattu puskuri on rengaspuskuri, jota tuottajat täyttävät ja
kuluttajat tyhjentävät. Täysi puskuri pysäyttää tuottajat, tyhjä
kuluttajat. Kaksi ehtomuuttujaa – "ei tyhjä" ja "ei täysi" – herättää
vain sen osapuolen, jota tilan muutos koskee. Lopetusta varten jono
suljetaan: kuluttajat tyhjentävät jäljellä olevat ja palaavat:

```{.c tiedosto="esimerkit/13-tuottaja.c" osa="jono"}
```

Kolme tuottajaa laittaa kukin 10 000 lukua, ja kaksi kuluttajaa ottaa
niitä silmukassa `for (int x; ota(&jono, &x);)`, kunnes jono on
suljettu ja tyhjä. Pääsäie sulkee jonon, kun kaikki tuottajat ovat
valmiita:

```{.tuloste tiedosto="esimerkit/13-tuottaja.odotettu"}
```

Tuotteiden jakautuminen kuluttajien kesken vaihtelee joka ajossa,
mutta summa ja määrä eivät. Esimerkki tulostaa vain ne. Testi
ajetaan myös ThreadSanitizerilla, joka tarkistaa, ettei puskuria
käytetä ilman lukkoa. Signaalin lähetys (`pthread_cond_signal`) lukon
sisällä on yksinkertaisin oikea tapa; sen voi siirtää lukon
vapautuksen jälkeen, jolloin herätetty ei heti törmää lukittuun
mutexiin, mutta silloin on varmistettava, ettei ehtomuuttuja tuhoudu
välissä.

## Semafori

Dijkstran semafori (1965) on kokonaislukulaskuri kahdella
operaatiolla. *P* (`sem_wait`) vähentää laskuria ja odottaa, jos se
menisi negatiiviseksi; *V* (`sem_post`) kasvattaa sitä ja herättää
odottajan. Binäärinen semafori (alkuarvo 1) on lukko. Laskeva
semafori, jonka alkuarvo on $n$, päästää $n$ säiettä yhtä aikaa: se
sopii rajallisen resurssin, kuten tietokantayhteyksien tai
puskuripaikkojen, laskemiseen.

```{.c tiedosto="esimerkit/13-semafori.c" osa="semafori"}
```

Kahdeksan säiettä kilpailee kolmesta paikasta 50 kierroksen ajan:

```{.tuloste tiedosto="esimerkit/13-semafori.odotettu"}
```

Samanaikaisuuden enimmäismäärä mitataan atomisilla laskureilla:
`atomic_fetch_add` kasvattaa ja palauttaa vanhan arvon yhtenä
jakamattomana operaationa, ja CAS-silmukka päivittää maksimin vain, jos
oma arvo on suurempi. Semaforin etu ehtomuuttujaan verrattuna on, että
`sem_post` on async-signal-safe ja muistaa herätyksen, vaikka kukaan ei
vielä odottaisi. Haittana on, että semafori ei tiedä, kuka sen "omistaa":
kuka tahansa voi kutsua `sem_post`, joten virheet ovat vaikeampia
löytää kuin mutexilla.

## Lukijat ja kirjoittajat

Usein jaettua dataa luetaan paljon useammin kuin muutetaan.
Lukijat eivät häiritse toisiaan, joten niiden kannattaa antaa olla
sisällä yhtä aikaa; kirjoittajan on oltava yksin. Toteutuksessa on
valittava, kumpaa suositaan. Jos lukijat pääsevät aina sisään, kun
toinen lukija on jo sisällä, jatkuva lukijavirta näännyttää
kirjoittajat. Esimerkin lukko suosii kirjoittajia: uusi lukija odottaa,
jos yksikin kirjoittaja odottaa:

```{.c tiedosto="esimerkit/13-lukijat.c" osa="lukko"}
```

Testissä kirjoittajat siirtävät rahaa tililtä toiselle kahdessa
vaiheessa, ja välitilassa tilien summa on väärä. Jos lukija pääsisi
sisään kirjoittajan kanssa yhtä aikaa, se näkisi rikkinäisen tilan
ja kasvattaisi rikkomuslaskuriaan. Neljä lukijaa ja kaksi kirjoittajaa
tekevät kukin 2000 kierrosta:

```{.tuloste tiedosto="esimerkit/13-lukijat.odotettu"}
```

POSIXin valmis `pthread_rwlock_t` jättää suosimissäännön
toteutukselle. Linuxin ytimen *RCU* (read-copy-update) poistaa
lukijoiden lukituksen kokonaan: kirjoittaja vaihtaa osoittimen
muutettuun kopioon ja vapauttaa vanhan, kun lukijat ovat ohi.

## Käytännössä

- **Pidä kriittinen alue lyhyenä:** älä tee I/O:ta tai kutsu
  tuntematonta koodia lukon sisällä.
- **Odota aina `while`-silmukassa:** aiheettomat herätykset ja
  ohittajat ovat todellisia.
- **Sido ehto dataan, ei herätykseen:** ehtomuuttuja ei muista
  signaalia; tila on jaetussa muuttujassa, jonka mutex suojaa.
- **Sulje jono lopettaaksesi:** lopetuslippu ja `broadcast` ovat
  luotettavampia kuin säikeiden peruuttaminen.
- **Aja ThreadSanitizerilla:** kilpatilanteet ja lukitsemattomat
  käytöt löytyvät ensimmäisellä ajolla.

## Itsearviointi

- Osaat selittää kilpatilanteen ja kriittisen alueen ratkaisun kolme
  ehtoa.
- Osaat kertoa, miten mutex toteutetaan atomisilla käskyillä ja
  futexilla, ja milloin spinlukko on perusteltu.
- Osaat toteuttaa rajatun tuottaja–kuluttaja-jonon mutexilla ja
  kahdella ehtomuuttujalla sekä selittää, miksi odotus on silmukassa.
- Osaat käyttää laskevaa semaforia rajallisen resurssin hallintaan.
- Osaat toteuttaa lukijat–kirjoittajat-lukon ja selittää, miten
  suosimissääntö vaikuttaa nääntymiseen.
