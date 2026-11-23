# Säikeet ja atomiset operaatiot

C11 lisäsi kieleen muistimallin, säikeet (`<threads.h>`) ja atomiset
tyypit (`<stdatomic.h>`). Sitä ennen säikeistys oli
käyttöjärjestelmäkohtaisten rajapintojen, kuten POSIX-säikeiden
(`pthread`), varassa. Standardin säikeet ovat ohut kerros näiden päällä,
ja ne ovat käytettävissä esimerkiksi glibc:ssä, muslissa ja uusissa
Windows-ympäristöissä. POSIX-säikeet ovat edelleen yleisiä, ja niiden
rajapinta on hyvin samankaltainen.

## Säikeen luominen

`thrd_create` käynnistää uuden säikeen, joka suorittaa annetun funktion.
Funktio saa yhden `void *`-argumentin ja palauttaa `int`-arvon.
`thrd_join` odottaa säikeen päättymistä. Jokainen säie on joko odotettava
tai irrotettava (`thrd_detach`), muuten sen resurssit eivät vapaudu.

Seuraava ohjelma laskee summan neljässä säikeessä. Jokainen säie saa
oman `Osa`-rakenteensa ja kirjoittaa tuloksen vain siihen, joten
säikeet eivät käsittele samaa muistia eikä lukitusta tarvita:

```{.c tiedosto="esimerkit/11-saikeet.c" osa="tehtava"}
```

```{.c tiedosto="esimerkit/11-saikeet.c" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/11-saikeet.odotettu"}
```

Esimerkissä taulukon pituus on jaollinen säikeiden määrällä.
Yleisessä tapauksessa viimeinen säie käsittelisi myös jakojäännöksen.
Nimetön `enum` on vanha tapa määritellä kokonaislukuvakioita, joita
voi käyttää taulukon kokona; C23:ssa sama onnistuu `constexpr`:llä.

## Kilpatilanteet ja lukot

Jos kaksi säiettä käsittelee samaa muistipaikkaa samanaikaisesti ja
ainakin toinen kirjoittaa, syntyy *kilpatilanne* (*data race*), joka on
määrittelemätöntä käyttäytymistä. Jopa `saldo += 1` koostuu lukemisesta,
lisäyksestä ja kirjoittamisesta, ja kahden säikeen operaatiot voivat
lomittua niin, että lisäyksiä katoaa.

Jaettu data suojataan *lukolla* (`mtx_t`). `mtx_lock` odottaa, kunnes
lukko on vapaa, ja varaa sen; `mtx_unlock` vapauttaa sen. Lukon sisällä
oleva koodi suoritetaan siis yksi säie kerrallaan. Yksittäisille
laskureille ja lipuille kevyempi vaihtoehto on *atominen* tyyppi, kuten
`atomic_int`, jonka operaatiot ovat jakamattomia:

```{.c tiedosto="esimerkit/11-lukitus.c" osa="jaettu"}
```

```{.c tiedosto="esimerkit/11-lukitus.c" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/11-lukitus.odotettu"}
```

Ilman lukkoa saldo jäisi satunnaisesti alle 40000:n. Jokainen
`mtx_lock`-kutsu on vapautettava täsmälleen kerran kaikilla
suorituspoluilla; C:ssä ei ole C++:n kaltaisia olioita, jotka tekisivät
sen automaattisesti. Kun lukkoja on useita, ne on aina varattava samassa
järjestyksessä, jotta säikeet eivät jää odottamaan toisiaan
(*lukkiutuminen*, *deadlock*).

Lukon kanssa käsitelty muuttuja ei tarvitse `volatile`-määrettä.
`volatile` on tarkoitettu laitteistorekistereille ja vastaaville, eikä
se tee operaatioista atomisia tai säieturvallisia.

## Testaaminen

Kilpatilanteet ilmenevät satunnaisesti, joten testi voi mennä läpi
tuhat kertaa ja epäonnistua tuhannes ensimmäisellä kerralla.
ThreadSanitizer (`-fsanitize=thread`) havaitsee kilpatilanteet ajon
aikana, vaikka ne eivät sillä kertaa aiheuttaisi väärää tulosta.
Tämän luvun esimerkit on kuitenkin testattu vain AddressSanitizerilla
ja UndefinedBehaviorSanitizerilla: ThreadSanitizer ei tue glibc:n
`<threads.h>`-toteutusta, vaan ohjelma kaatuu säikeen luonnissa.
POSIX-säikeitä käyttäville ohjelmille ThreadSanitizer toimii.
