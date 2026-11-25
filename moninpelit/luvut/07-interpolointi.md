# Interpolointi ja ekstrapolointi

Muiden pelaajien liikettä ei voi ennustaa luotettavasti, koska heidän
syötteensä ovat tuntemattomia. Asiakas saa heistä vedoksen esimerkiksi
20 kertaa sekunnissa, epätasaisin välein ja osa hukattuna. Jos uusin
vedos piirretään sellaisenaan, hahmot nykivät: sama paikka useamman
ruudun ajan, sitten hyppy.

## Puskuroinnin viive

*Entiteettien interpolointi* näyttää muut pelaajat hieman menneisyydessä,
hetkellä *nyt − puskuri*. Puskuri valitaan niin, että näyttöhetken
molemmin puolin on yleensä jo saapunut vedos, ja paikka interpoloidaan
niiden välistä:

```{.cpp tiedosto="esimerkit/07-interpolointi.cpp" osa="interpoloi"}
```

Vaihtoehto on *ekstrapolointi* (dead reckoning): uusimmasta vedoksesta
jatketaan viimeisellä tunnetulla nopeudella nykyhetkeen. Esimerkki
vertaa tapoja yhteydellä, jonka viive on 50–90 ms ja häviö 3 %:

```{.cpp tiedosto="esimerkit/07-interpolointi.cpp" osa="tavat"}
```

```{.tuloste tiedosto="esimerkit/07-interpolointi.odotettu"}
```

![Kaksi sekuntia samasta ajosta. Renkaat ovat vedoksia sillä hetkellä,
kun ne saapuvat. Uusin vedos etenee portain ja on aina jäljessä.
Ekstrapolointi seuraa todellista paikkaa, kunnes suunta vaihtuu, ja
ampuu silloin yli. Interpolointi toistaa todellisen liikkeen tarkasti
mutta 150 ms myöhässä.](kuvat/interpolointi.png){width=95%}

- **Uusin vedos** on keskimäärin 9 cm väärässä paikassa ja nykii.
- **Ekstrapolointi** osuu tasaisessa liikkeessä hyvin (1,4 cm), mutta
  jokaisessa suunnanmuutoksessa hahmo jatkaa hetken väärään suuntaan ja
  hyppää takaisin. Ihmisen liike on täynnä suunnanmuutoksia.
- **Interpolointi 150 ms:n puskurilla** näyttää liikkeen täsmälleen
  oikein, mutta 150 ms myöhässä. Puskuri tyhjenee vain prosentissa
  ruuduista.
- **Liian lyhyt puskuri** (50 tai 100 ms) tyhjenee usein, ja hahmo
  jähmettyy odottamaan seuraavaa vedosta.

Puskurin nyrkkisääntö on kaksi vedosväliä ja värinän varmuusvara: 20 Hz:n
vedoksilla ja 40 ms:n värinällä noin 140 ms. Kaksi väliä tarvitaan,
jotta yksi kadonnut vedos ei tyhjennä puskuria.

## Kumpi ja milloin

Useimmat toimintapelit interpoloivat muut pelaajat ja hyväksyvät
viiveen, koska oikea liike on tärkeämpi kuin tuoreus; viiveen
haittaa korjataan osumantarkistuksessa (luku *Viiveen kompensointi*).
Ekstrapolointi sopii ennustettaville kappaleille, kuten ajoneuvoille,
lentokoneille ja ammuksille, joiden liike noudattaa fysiikkaa.
Interpoloinnin puskuria voi säätää yhteyden mukaan: mitattu värinä
kasvattaa puskuria, tasainen yhteys pienentää sitä hitaasti.

Kun puskuri tyhjenee, hahmo voi jatkaa lyhyen aikaa ekstrapoloiden
(esimerkiksi enintään 250 ms) ja sitten pysähtyä. Pitkä ekstrapolointi
johtaa hahmoihin, jotka juoksevat seinien läpi.

## Käytännössä

- **Oma hahmo ennustettuna, muut interpoloituina.** Pelaaja elää siis
  kahdessa ajassa: itse nykyhetkessä, muut menneisyydessä.
- **Puskuri kaksi vedosväliä plus värinä**, mieluiten mukautuvana.
- **Interpoloi myös kierto ja animaation vaihe**, ei vain sijaintia.
  Kierron interpolointi kulkee lyhintä reittiä (359° → 1°).
- **Teleportit ja syntymiset ohittavat interpoloinnin**, muuten hahmo
  liukuu kartan poikki.
- **Hinta:** jokainen millisekunti puskuria on viivettä, jonka pelaaja
  näkee vastustajissa. 60 Hz:n vedokset puolittavat puskurin 20 Hz:iin
  verrattuna mutta kolminkertaistavat kaistan.

## Itsearviointi

- Osaat toteuttaa entiteettien interpoloinnin puskuroinnin viiveellä.
- Osaat valita puskurin pituuden vedosvälin ja värinän perusteella.
- Osaat verrata interpolointia ja ekstrapolointia virheen ja viiveen
  kannalta.
- Osaat käsitellä puskurin tyhjenemisen ja teleportit.
