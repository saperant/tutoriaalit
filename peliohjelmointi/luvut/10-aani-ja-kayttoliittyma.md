# Ääni ja käyttöliittymä

Ääni ja käyttöliittymä ovat pelissä omia järjestelmiään, joissa on
omat sudenkuoppansa. Tässä luvussa käsitellään kummastakin keskeinen
periaate: äänen miksaus ja välitön käyttöliittymä.

## Äänen miksaus

Äänilaite pyytää näytteitä omassa säikeessään tasaisin välein, esim.
480 näytettä kymmenen millisekunnin välein 48 kHz:llä. Jos puskuri ei
valmistu ajoissa, kuuluu napsahdus. Siksi äänisäikeessä ei varata
muistia, lueta levyä eikä odoteta lukkoja.

Useat samanaikaiset äänet *miksataan* laskemalla näytteet yhteen.

```{.cpp tiedosto="esimerkit/10-miksaus.cpp" osa="aani"}
```

```{.cpp tiedosto="esimerkit/10-miksaus.cpp" osa="miksaus"}
```

```{.tuloste tiedosto="esimerkit/10-miksaus.odotettu"}
```

Kun kolme ääntä soi yhtä aikaa voimakkuudella 0,6, summa ylittää
täyden voimakkuuden, ja yli 3000 näytettä joudutaan leikkaamaan. Se
kuulostaa säröltä. Summa lasketaan liukulukuina ja rajataan vasta
lopuksi; jos 16-bittiset näytteet laskettaisiin suoraan yhteen,
ylivuoto kääntäisi etumerkin ja kuuluisi pamauksena. Pelien äänimoottorit
(FMOD, Wwise, miniaudio, SDL_mixer) käyttävät kompressoria tai
limitteriä ja priorisoivat ääniä: samaa ääntä ei soiteta kymmentä kertaa
päällekkäin.

Lisäksi esimerkki loiventaa äänen loppua (verho), koska äkillinen
katkaisu kuuluu napsahduksena. Vaihe pidetään välillä [0, 1), jotta
liukuluvun tarkkuus ei heikkene pitkässä äänessä.

## Välitön käyttöliittymä

Perinteisessä (*säilyttävässä*, retained mode) käyttöliittymässä
painikkeet ovat olioita, joiden tila synkronoidaan pelin tilan kanssa.
*Välittömässä* (immediate mode) käyttöliittymässä käyttöliittymä
kuvataan koodissa joka ruudulla, ja painikkeen funktio palauttaa,
painettiinko sitä.

```{.cpp tiedosto="esimerkit/10-kayttoliittyma.cpp" osa="valiton"}
```

```{.cpp tiedosto="esimerkit/10-kayttoliittyma.cpp" osa="valikko"}
```

```{.tuloste tiedosto="esimerkit/10-kayttoliittyma.odotettu"}
```

Painike laukeaa, kun hiiren nappi *vapautetaan* sen päällä, kuten
työpöytäohjelmissa: painalluksen voi perua siirtämällä hiiren pois.
Välitön tyyli on suosittu kehitystyökaluissa ja debug-näkymissä (Dear
ImGui), koska käyttöliittymä ei voi olla ristiriidassa pelin tilan
kanssa. Pelaajalle näkyvät valikot tehdään usein säilyttävällä
mallilla, jossa asettelu, animaatiot ja lokalisointi ovat helpompia.

## Käytännössä

- **Äänisäie ei odota.** Pelisilmukka lähettää äänikomennot jonolla
  (lukoton rengaspuskuri), ja äänisäie miksaa.
- **Miksaa liukuluvuin ja rajaa lopuksi.** Käytä äänikanavaryhmiä
  (musiikki, efektit, puhe) ja pelaajan säädettäviä voimakkuuksia.
- **Ääni maailmassa:** voimakkuus ja panorointi lasketaan kuulijan ja
  lähteen etäisyydestä ja suunnasta.
- **Käyttöliittymä omassa koordinaatistossaan** ja skaalautuvana
  resoluution mukaan; ohjaimella käytettävä valikko tarvitsee fokuksen
  ja navigoinnin, ei vain hiirtä.
- **Saavutettavuus:** tekstityskoko, värisokeustilat ja syötteen
  uudelleenmääritys ovat osa käyttöliittymää.

## Itsearviointi

- Osaat miksata useita ääniä ja välttää leikkautumisen ja ylivuodon.
- Osaat kertoa, miksi äänisäikeessä ei varata muistia eikä odoteta
  lukkoja.
- Osaat toteuttaa välittömän käyttöliittymän painikkeen ja verrata
  välitöntä ja säilyttävää mallia.
