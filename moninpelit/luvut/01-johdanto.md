# Johdanto {.runko-johdanto}

Reaaliaikaisessa moninpelissä usea pelaaja jakaa saman maailman, vaikka
jokaisen kone näkee sen omalla viiveellään. Valo kulkee valokuidussa
Helsingistä Frankfurtiin noin 8 millisekunnissa suuntaansa, mobiiliverkon
kiertoviive on usein 50–100 ms ja kotiverkon langaton yhteys hukkaa
paketteja. Peli pyörii silti 60 ruudun sekuntivauhtia, eli 16 ms:n
välein. Moninpeliohjelmointi on näiden kahden aikaskaalan
sovittamista: miten maailma pidetään yhtenäisenä ja reiluna, kun tieto
on aina hieman vanhaa ja osa siitä katoaa.

Tutoriaali olettaa taidon *Peliohjelmointi*: kiinteä aika-askel,
kokonaislukuaika, oma satunnaislukugeneraattori ja deterministinen
simulaatio ovat tämän tutoriaalin perusta, eikä niitä käydä uudelleen
läpi. Verkon peruskäsitteet (IP, UDP, TCP, portit, MTU) ovat taidossa
*Tietoverkot*, ja sokettiohjelmointi syvemmin taidossa
*Verkko-ohjelmointi*.

## Mitä tutoriaali kattaa

Luvut etenevät verkon todellisuudesta kohti pelaajan kokemusta:

1. **Arkkitehtuurit**: vertaisverkko, asiakas–palvelin ja isäntä,
   palvelimen auktoriteetti.
2. **Verkon todellisuus**: viive, värinä, häviö ja kaistanleveys; miksi
   pelit käyttävät UDP:tä.
3. **Luotettavuuskerros**: yhteyden muodostus, sekvenssinumerot,
   kuittauskentät ja uudelleenlähetys vain sille, mikä sitä tarvitsee.
4. **Tilan synkronointi**: tilannevedokset, delta-pakkaus,
   kiinnostusalueet, kvantisointi ja bittitason pakkaus.
5. **Asiakkaan ennustus ja täsmäytys**: oma hahmo liikkuu heti;
   asiakkaan ja palvelimen tikkien tahdistus.
6. **Interpolointi ja ekstrapolointi**: muut pelaajat liikkuvat
   sulavasti.
7. **Viiveen kompensointi**: osumat ratkaistaan ampujan näkemässä
   menneisyydessä.
8. **Lukitusaskel ja rollback**: koko pelin simulointi kaikilla
   koneilla.
9. **Auktoriteetti ja huijaamisen esto**.
10. **Lukitusaskel oikean UDP:n yli**: palvelin ja kaksi asiakasta
    erillisinä prosesseina.
11. **Pelipalvelimet ja otteluiden muodostus**.

## Simuloitu verkko

Oikea verkko on testissä hankala: viive ja häviöt vaihtelevat ajosta
toiseen, eikä tulosta voi verrata odotettuun. Siksi useimmat esimerkit
käyttävät prosessin sisäistä simuloitua yhteyttä. Viesti saapuu
perusviiveen ja satunnaisen värinän jälkeen tai katoaa, ja satunnaisuus
tulee kiinteällä siemenellä alustetusta PCG32-generaattorista. Sama
ajo tuottaa aina saman tuloksen GCC:llä ja Clangilla.

```{.cpp tiedosto="esimerkit/yhteinen/verkko.hpp" osa="linkki"}
```

Värinä muuttaa järjestystä: myöhemmin lähetetty viesti voi saapua ensin,
kuten oikeassakin verkossa. Aika etenee millisekunnin askelin, ja
esimerkki päättää itse, milloin se lähettää ja vastaanottaa. Ensimmäinen
esimerkki mittaa kiertoviiveen:

```{.cpp tiedosto="esimerkit/01-ping.cpp" osa="ping"}
```

```{.tuloste tiedosto="esimerkit/01-ping.odotettu"}
```

![Saman ajon kiertoviiveet. Jokainen pylväs on yksi ping; rastin
kohdalla kysely tai vastaus katosi matkalla.](kuvat/ping.png){width=75%}

Jo tässä näkyvät tutoriaalin perusongelmat: kiertoviive on 67–82 ms
eikä vakio, ja kaksi pingiä (9 ja 11) katosi kokonaan.

## Esimerkit ja työkalut

Esimerkit ovat hakemistossa `esimerkit/` ja kirjoitettu C++23:lla.
Testeissä jokainen käännetään GCC 14:llä ja Clang 20:llä
AddressSanitizerin ja UndefinedBehaviorSanitizerin kanssa, ja molempien
tulosteen on oltava sama. Yhteiset osat ovat hakemistossa
`esimerkit/yhteinen/`. Oikea UDP-peli (luku *Lukitusaskel oikean UDP:n
yli*) ajetaan
esimerkkihakemiston Makefilellä, koska siinä on kolme erillistä
prosessia:

```text
make -C esimerkit          # UDP-palvelin ja kaksi asiakasta
make testaa                # kaikki testit
make pdf                   # tutoriaalin ja pikaoppaan PDF:t
```

Aikajanat ja kuvaajat on piirretty esimerkkien omista lokeista:
argumentilla käynnistetty esimerkki tulostaa tapahtumansa, ja
`make kuvat` piirtää niistä kuvat. Kuva näyttää siis saman ajon, jonka
tuloste on tekstissä.

Kehityskontissa (`.devcontainer/moninpelit`) on kääntäjät,
verkkotyökalut ja kuvien piirtoon Matplotlib.
