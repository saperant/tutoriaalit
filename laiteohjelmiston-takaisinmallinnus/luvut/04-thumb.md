# ARM- ja Thumb-koodin lukeminen

*Takaisinmallinnus*-taidossa koodi oli x86-64:ää; sulautetuissa
laitteissa se on lähes aina ARMia, ja Cortex-M:ssä nimenomaan
*Thumb-2*-käskykantaa. Käskyt ovat 16- tai 32-bittisiä, ja koodi on
tiiviimpää kuin x86-64:ssä. Lukemisen periaatteet ovat samat
(rekisterit, kutsukonventio, pinokehys), mutta yksityiskohdat eroavat.

## Thumb-2 ja AAPCS

Cortex-M:ssä on 16 rekisteriä: `r0`–`r12`, pino `sp` (`r13`),
paluuosoite `lr` (`r14`) ja ohjelmalaskuri `pc` (`r15`). Kutsukonventio
on AAPCS: argumentit tulevat rekistereihin `r0`–`r3`, paluuarvo on
`r0`, ja kutsuttu funktio säilyttää rekisterit `r4`–`r11`. Funktio
kutsutaan `bl`-käskyllä (paluuosoite `lr`:ään) ja palataan `bx lr`-
tai `pop {..., pc}` -käskyllä. Thumb-tila näkyy osoitteiden
parittomuutena: funktio-osoittimen ja vektoritaulun alin bitti on 1.

Prosessori lataa vakiot *literaalivarannosta* (*literal pool*):
`ldr r3, [pc, #n]` lukee sanan koodin seasta, tyypillisesti funktion
lopusta. Tämän tutoriaalin `pura`-työkalu lisää kommentin, joka näyttää
ladatun sanan ja merkkijonon, johon se osoittaa. Sovelluksen
Reset-käsittelijä:

```{.bash tiedosto="esimerkit/04-thumb/aja.sh" osa="reset"}
```

```{.tuloste tiedosto="esimerkit/04-thumb/odotettu" osa="s1"}
```

Reset kopioi alustetun datan flashista RAMiin (kaksi osoiteväliä
literaalivarannosta) ja nollaa `.bss`-alueen; se on sama koodi, joka
*Mikrokontrollerit*-taidossa kirjoitettiin C:llä. Funktion perässä
oleva literaalivaranto näkyy pelkkinä sanoina:

```{.bash tiedosto="esimerkit/04-thumb/aja.sh" osa="varanto"}
```

```{.tuloste tiedosto="esimerkit/04-thumb/odotettu" osa="s2"}
```

Osoitteet `0x200000..` ovat RAM-rajoja ja `0x112b0` flashissa oleva
sana. Disassemblerin on tiedettävä, että nämä ovat dataa, ei käskyjä;
lineaarinen purku tulkitsisi ne vääriksi käskyiksi (ks.
*Takaisinmallinnus*-taidon luku lineaarisesta ja rekursiivisesta
purusta).

## radare2 ARM-koodille

radare2 purkaa myös raa'an binäärin, kun sille kertoo arkkitehtuurin
(`-a arm`), sanan leveyden (`-b 16` Thumb) ja latausosoitteen (`-m`).
Analyysin jälkeen `pdf` näyttää funktion ohjausvuon nuolineen:

```{.bash tiedosto="esimerkit/04-thumb/aja.sh" osa="r2"}
```

```{.tuloste tiedosto="esimerkit/04-thumb/odotettu" osa="s3"}
```

Funktio `0x104fc` vertaa muistin arvoa vakioon `0x54455341` (`ASET`),
lukee puolisanan siirtymästä 6 ja kutsuu funktiota `0x109c0`; jo tästä
arvaa, että se tarkistaa asetuslohkon taikaluvun ja tarkisteen (luku 5
vahvistaa). Vasemman reunan nuolet näyttävät haarat.

## Capstone Pythonista

Kun analyysi halutaan skriptata, Capstone purkaa tavut käskyiksi
Pythonista. Tämän tutoriaalin `thumb`-moduuli kääri Capstonen niin,
että se tunnistaa haarat, literaalivarannon luvut ja `movw`/`movt`-
vakiot; muut työkalut (funktioiden etsintä, oheislaitekartta) rakentuvat
sen päälle. Kutsutun funktion `0x109c0` alku:

```{.bash tiedosto="esimerkit/04-thumb/aja.sh" osa="kutsuttu"}
```

```{.tuloste tiedosto="esimerkit/04-thumb/odotettu" osa="s4"}
```

Funktio lataa literaalivarannosta RAM-osoitteita ja vakion
`0xedb88320`. Tuo vakio on CRC-32:n heijastettu polynomi (luku 5
tunnistaa algoritmit vakioista), joten funktio laskee tarkisteen.

## Käytännössä

- **Tunnista Thumb-tila paritosta osoitteesta.** Vektoritaulun ja
  funktio-osoittimien alin bitti on 1. Purussa on kerrottava
  `-b 16`/Thumb, tai käskyt menevät sekaisin.
- **Seuraa literaalivarantoja.** `ldr rX, [pc, #n]` lataa vakion tai
  osoitteen funktion lopusta. Kommentoi ladattu arvo heti; osoitteet
  merkkijonoihin ja oheislaitteisiin paljastavat funktion tehtävän.
- **Käytä AAPCS:ää lukuapuna.** `r0`–`r3` ovat argumentit, `r0`
  paluuarvo. Funktion prologi (`push {..., lr}`) ja epilogi
  (`pop {..., pc}`) rajaavat sen.
- **Skriptaa toistuva työ Capstonella.** Käsin luku kannattaa vain
  avainkohdista; funktioiden etsintä, ristiviittaukset ja vakioiden
  keruu ovat skriptattavia ja toistettavia.

## Itsearviointi

- Osaat lukea Thumb-2-koodia: rekisterit, AAPCS-argumentit, prologin ja
  epilogin.
- Osaat tunnistaa literaalivarannon luvun ja selittää, miksi se on
  dataa eikä käsky.
- Osaat purkaa raa'an Thumb-binäärin radare2:lla oikealla
  arkkitehtuurilla ja latausosoitteella.
- Osaat purkaa koodin Capstonella Pythonista ja poimia käskyn haaran
  kohteen ja ladatun vakion.
