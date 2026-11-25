// Liukulukujen toistettavuus (luku 13). Kääntäjä saa oletuksena
// yhdistää kerto- ja yhteenlaskun yhdeksi FMA-käskyksi, jos suoritin
// tukee sitä. Yhdistetty käsky pyöristää vain kerran, joten tulos voi
// poiketa viimeisessä bitissä kääntäjästä ja suorittimesta riippuen.
// Kielto tekee jokaisesta laskutoimituksesta erikseen pyöristetyn
// IEEE 754 -operaation.
#pragma once
// @alku fma
#if defined(SALLI_FMA)
// Kokeilua varten: make tiivisteet kääntää myös tällä valitsimella.
#elif defined(__clang__)
#pragma STDC FP_CONTRACT OFF
#elif defined(__GNUC__)
#pragma GCC optimize("fp-contract=off")
#endif
// @loppu fma
