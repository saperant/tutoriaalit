# Testaus ja ylläpito

Dokumentaatio ei valmistu, se vanhenee. Jokainen koodin muutos voi
tehdä jostakin lauseesta valheen, eikä kukaan huomaa sitä ennen kuin
lukija toimii ohjeen mukaan ja epäonnistuu. Tässä luvussa kootaan
keinot, joilla vanheneminen huomataan koneellisesti, ja käytännöt
niihin osiin, joita kone ei näe.

## Mitä kone voi tarkistaa

Edellisten lukujen tarkistukset yhdessä taulukossa:

| Vika | Tarkistus | Luku |
|-------------------------------------|----------------------------------|------|
| esimerkki ei toimi | doctest, esimerkit tiedostoista | 4, 5, 7 |
| komennon tuloste on muuttunut | upotettujen tulosteiden vertailu | 6 |
| viittaus poistettuun funktioon | Sphinx `-W` ja `nitpicky` | 5 |
| rikkinäinen linkki tai ankkuri | MkDocs `--strict`, linkkitarkistin | 6, 12 |
| julkinen nimi ilman kuvausta | ruff `D`, Doxygenin varoitukset | 7, 8 |
| kuvauksen parametrit eivät vastaa koodia | Doxygen, kattavuustarkistin | 7, 8 |
| rajapintakuvaus ei vastaa toteutusta | esimerkkipyyntöjen ajo | 9 |
| kaavio ei vastaa koodia | generoidun kaavion vertailu | 11 |
| muutoslokin versio ei vastaa pakettia | muutoslokin tarkistin | 2 |
| sovitun termin vastainen sana | proosan tarkistin | 3 |

Yhteistä kaikille on, että dokumentaation väite sidotaan koodiin niin,
että ristiriita kaataa rakennuksen. Väite, jota mikään ei tarkista,
on totta vain kirjoitushetkellä.

## Linkit

Linkit ovat dokumentaation haurain osa: tiedosto siirretään, otsikko
muotoillaan uudelleen, ja linkki osoittaa tyhjään. Sivustogeneraattorit
tarkistavat omat sivunsa, mutta README ja muut repositorion
Markdown-tiedostot jäävät niiden ulkopuolelle. Esimerkkien tarkistin
käy läpi suhteelliset linkit:

```{.python tiedosto="esimerkit/tyokalut/linkit.py" osa="tarkista"}
```

Ankkuri on otsikosta johdettu tunniste, ja sen muodostussääntö riippuu
työkalusta:

```{.python tiedosto="esimerkit/tyokalut/linkit.py" osa="ankkuri"}
```

GitHub säilyttää ääkköset, MkDocs poistaa niistä oletuksena pisteet,
joten otsikon ”Ylläpito” ankkuri on toisessa `#ylläpito` ja toisessa
`#yllapito`. Tarkistimen pitää käyttää samaa sääntöä kuin työkalu,
jolla sivut julkaistaan. Luvun 2 sekavasta ohjeesta löytyy kaksi
vikaa:

```{.tuloste tiedosto="esimerkit/naytteet/sekava-ohje.linkit.odotettu"}
```

Ulkoiset linkit lasketaan mutta jätetään tarkistamatta. Niiden
tarkistus vaatii verkon, ja toisen sivuston hetkellinen katko kaataisi
oman rakennuksen. Ulkoiset linkit tarkistetaan siksi erillisessä
ajastetussa ajossa, jonka tulos on tehtävälista eikä este. Valmiita
työkaluja ovat lychee ja Sphinxin `linkcheck`-rakentaja.

## Mitä kone ei näe

Kone ei tiedä, onko ohje ymmärrettävä, puuttuuko jokin askel tai
vastaako dokumentaatio lukijan kysymykseen. Näihin on kolme keinoa.

**Katselmointi.** Dokumentaatio katselmoidaan kuten koodi, ja
katselmoijan tehtävä on olla lukija. Paras katselmoija on se, joka ei
tunne asiaa: jos hän ymmärtää ohjeen, ohje toimii. Katselmoinnin
tarkistuslistaan kuuluu kysymys ”muuttuuko jokin, mikä on dokumentoitu”:
uusi asetus, muuttunut oletusarvo, poistunut valitsin.

**Kokeilu.** Opas ja asennusohje ajetaan säännöllisesti alusta loppuun
puhtaassa ympäristössä. Uusi tiimiläinen on tähän paras mahdollinen
testaaja, ja hänen ensimmäinen tehtävänsä on korjata ohjeesta kohdat,
joissa hän jäi jumiin.

**Palaute.** Lukija, joka löytää virheen, kertoo siitä vain, jos se
on helppoa. ”Muokkaa tätä sivua” -linkki ja tieto siitä, mihin
vikailmoitus tehdään, tuottavat korjauksia, joita ei muuten saataisi.
Tukipyynnöt ovat dokumentaation vikailmoituksia: kysymys, joka
esitetään kolmesti, kuuluu ohjeisiin.

## Omistajuus ja elinkaari

Dokumentti, jolla ei ole omistajaa, vanhenee. Omistaja ei kirjoita
kaikkea itse, mutta hän vastaa siitä, että sivu pitää paikkansa:

- Koodin vieressä olevan dokumentaation omistaa koodin omistaja.
  Repositorion omistajatiedosto (`CODEOWNERS`) voi nimetä
  dokumentaatiohakemistolle katselmoijat.
- Toimintaohjeen omistaa se tiimi, joka päivystää. Ohje tarkistetaan
  jokaisen häiriön jälkikäsittelyssä.
- Arkkitehtuurikuvauksen omistaa tiimi yhdessä, ja se käydään läpi
  esimerkiksi neljännesvuosittain.

Dokumentaatiota myös poistetaan. Vanhentunut sivu on huonompi kuin
puuttuva, koska siihen luotetaan. Sivu, jota ei voi pitää ajan tasalla,
merkitään vanhentuneeksi tai poistetaan, ja osoitteesta jätetään
uudelleenohjaus.

Ominaisuus on valmis vasta, kun se on dokumentoitu. Kun tämä kirjataan
tiimin valmiin määritelmään ja katselmoija pitää siitä kiinni,
dokumentaatiosta tulee osa työtä eikä erillinen tehtävä, joka
tehdään, jos ehditään. Työtapojen sopimista käsittelee taito
*Ohjelmistoprojektin hallinta*.

## Kaikki yhdessä

Esimerkkien `make` ajaa kaikki tämän tutoriaalin tarkistukset, ja sama
komento ajetaan jatkuvan integraation palvelussa jokaisesta
muutoksesta. Kokonaisuus kestää alle minuutin, koska jokainen
tarkistus on pieni. Dokumentaation tarkistus, joka kestää kymmenen
minuuttia, jätetään ajamatta paikallisesti, ja virheet löytyvät vasta
putkesta.

Tarkistuksia ei tarvitse ottaa käyttöön kerralla. Hyödyllisin
järjestys olemassa olevalle projektille on yleensä: rakennus
varoitukset virheinä, esimerkkien ajo, linkit, ja vasta sitten
kattavuus ja proosa.

## Käytännössä

- **Jokaisella tarkistuksella on viallinen näyte.** Tarkistus, jonka
  ei ole nähty epäonnistuvan, voi olla pois päältä (luku 6).
- **Varoitukset virheiksi yksi kerrallaan.** Vanhassa projektissa
  varoituksia on satoja. Korjaa yksi laji, tee siitä virhe ja siirry
  seuraavaan.
- **Ulkoiset linkit ajastettuun ajoon.** Oma rakennus ei saa kaatua
  toisen palvelimen katkoon.
- **Mittaa sitä, mikä auttaa lukijaa.** Sivumäärä ja kattavuusprosentti
  eivät kerro laadusta. Tukipyyntöjen aiheet ja haut, jotka eivät
  tuota tulosta, kertovat.
- **Poista rohkeasti.** Versionhallinta muistaa. Dokumentaation arvo
  on siinä, että siihen voi luottaa, ei sen määrässä.
- **Dokumentaatio valmiin määritelmään.** Muuten se on aina se työ,
  joka jää seuraavaan sprinttiin.

## Itsearviointi

- Osaat luetella dokumentaation viat, jotka kone voi löytää, ja
  tarkistuksen kullekin.
- Osaat selittää, miksi sisäiset linkit tarkistetaan jokaisessa
  rakennuksessa ja ulkoiset erikseen.
- Osaat kuvata, miten katselmointi, kokeilu ja palaute täydentävät
  koneellisia tarkistuksia.
- Osaat nimetä dokumentille omistajan ja perustella, milloin sivu
  kannattaa poistaa.
