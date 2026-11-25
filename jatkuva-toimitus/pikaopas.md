---
title: Jatkuva integraatio ja toimitus
subtitle: Pikaopas · integraatio, putki, julkaisu, mittarit
---

# Käsitteet

| Käsite | Tarkoittaa |
|------------------------|------------------------------------------------|
| jatkuva integraatio | kaikki yhdistävät runkoon päivittäin; jokainen yhdistys testataan; punainen korjataan heti |
| jatkuva toimitus | runko on aina julkaisukelpoinen; julkaisu on liiketoiminnan päätös |
| jatkuva käyttöönotto | jokainen putken läpäissyt muutos menee tuotantoon |
| käyttöönotto | uusi versio on käynnissä tuotannossa |
| julkaisu | käyttäjä saa ominaisuuden |

# Integraatio ja haarat

| Sääntö | Peruste |
|------------------------|------------------------------------------------|
| haaran ikä enintään 1–2 pv | ristiriidat kasvavat iän neliössä |
| testaa yhdistetty tulos | siisti yhdistys voi olla rikki (semanttinen ristiriita) |
| peru ensin, tutki sitten | punainen runko estää kaikkia |
| korjaus runkoon, poiminta julkaisuhaaraan | korjaus ei unohdu seuraavasta julkaisusta |
| julkaisuhaaraa ei yhdistetä takaisin | haara on päätepiste |

Keskeneräisen työn piilottaminen: käytöstä muuttamattomat askelet ·
sisäänkäynti viimeisenä · ominaisuuslippu · haarautuminen abstraktiolla
(abstraktio, uusi toteutus rinnalle, valinta, vanhan poisto).

# Toimitusputki

| Vaihe | Sisältö | Tavoite |
|-----------------|--------------------------------------|---------------|
| commit-vaihe | käännös, yksikkötestit, analyysi, paketti | alle 10 min |
| hyväksymisvaihe | artefakti tuotannon kaltaisessa ympäristössä, hyväksymistestit | kymmeniä minuutteja |
| muut | kuorma, tietoturva, tutkiva testaus | tarpeen mukaan |
| käyttöönotto | sama artefakti tuotantoon, seuranta | automaattinen |

- Halvin tarkistus ensin, riippumattomat rinnakkain.
- Rikkinäisestä muutoksesta ei synny artefaktia.
- Savutesti kohdistuu pakettiin, ei lähdekoodiin.
- Putki on ainoa tie tuotantoon.

Epävakaat testit: läpimenon todennäköisyys on $(1-p)^n$. Sata testiä
0,5 %:n häiriöllä: putki läpi 61 %. Tunnista, eristä määräajaksi,
korjaa tai poista. Uudelleenajo piilottaa myös oikeat viat.

# Artefaktit ja ympäristöt

| Sääntö | Käytännössä |
|------------------------|------------------------------------------------|
| rakenna kerran | sama tiedosto jokaiseen ympäristöön, tiiviste tarkistetaan |
| muuttumaton | korjaus on uusi artefakti; ei liikkuvia tunnisteita |
| toistettava | ei aikaleimoja, kiinteä järjestys, kiinnitetyt riippuvuudet |
| versio sisällä | ohjelma kertoo versionsa; versiosta pääsee commitiin |
| asetukset ulkoa | luetaan yhdessä paikassa, tarkistetaan käynnistyksessä |
| peruminen | edellinen versio tallessa, vaihto atominen |

# Putki koodina

- Ohut putki: työ skripteissä, putkitiedosto kutsuu niitä.
- Tarkista putkitiedoston syntaksi ja skeema; näe uusi tarkistus
  ensin punaisena.
- Muutoksiin perustuva testaus: epävarmassa tapauksessa kaikki,
  täysi ajo säännöllisesti, vertailukohtana viimeisin vihreä ajo.
- Välimuistin avain kaikesta, mistä tulos riippuu. Väärä osuma on
  pahempi kuin turha huti. Putki toimii myös ilman välimuistia.

# Ominaisuusliput

| Laji | Elinikä | Huomio |
|-----------------|-----------------|--------------------------------------|
| julkaisulippu | päiviä, viikkoja | poisto kuuluu työhön |
| koelippu | kokeen ajan | jako riippumaton muista lipuista |
| operointilippu | pysyvä | toimittava häiriössä |
| oikeuslippu | pysyvä | kuuluu usein käyttöoikeuksiin |

Lokero = tiiviste(lipun nimi, käyttäjä) mod 100: tasainen, pysyvä,
lipuittain riippumaton. Jokaisella lipulla omistaja, luontipäivä ja
turvallinen oletus. Nimeä ei käytetä uudelleen.

# Julkaisustrategiat

| Strategia | Altistuu | Peruminen | Vaatii |
|---------------|---------------|-------------------|---------------------------|
| kerralla | kaikki | uusi asennus | katkon sietoa |
| rullaava | kasvava osa | kierros takaisin | versiot yhteensopivia |
| sinivihreä | kaikki | liikenne takaisin | kaksinkertaisen kapasiteetin |
| kanarialintu | pieni osa | osuus nollaan | mittarit, riittävä liikenne |

Kanarialintu: mittari, joka näkee vian · vertailu vanhaan versioon
samaan aikaan · vähimmäisnäyte · vähimmäisaika.

# Tietokantamuutokset

Laajenna–supista: (1) lisää uusi rakenne, (2) kirjoita molempiin,
(3) täytä vanhat rivit erissä, (4) lue uudesta, (5) lopeta kirjoitus
vanhaan, (6) poista vanha. Jokainen askel on oma käyttöönottonsa.
Supistus on ainoa peruuttamaton askel: tee se viimeisenä ja vasta,
kun on mitattu, ettei vanhaa käytetä.

# Infrastruktuuri koodina ja GitOps

| Periaate | Sisältö |
|------------------------|------------------------------------------------|
| deklaratiivinen | kuvataan lopputila, työkalu päättelee toimet |
| idempotentti | sama kuvaus uudelleen ajettuna ei muuta mitään |
| suunnitelma | muutokset nähdään ja katselmoidaan ennen toteutusta |
| ajautuma | käsin tehty muutos näkyy erona |
| GitOps | versioitu haluttu tila, agentti hakee ja täsmäyttää jatkuvasti |

Ympäristöt hakemistoina, ei haaroina. Peruminen on `git revert`.
Git kertoo halutun tilan, ei todellista. Data ei palaudu perumalla.

# Mittarit

| Mittari | Laji |
|----------------------------------------|---------------------|
| julkaisutiheys | nopeus |
| muutoksen läpimenoaika | nopeus |
| epäonnistuneiden muutosten osuus | vakaus |
| palautumisaika | vakaus |

Lue yhdessä, seuraa suuntaa, laske järjestelmistä. Ei tavoitteiksi,
ei tiimien vertailuun, ei henkilöille.
