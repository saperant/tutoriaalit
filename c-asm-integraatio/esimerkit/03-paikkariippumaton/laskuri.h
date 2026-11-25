// C:n ja assemblyn yhteinen rajapinta: globaali muuttuja, C-funktio ja
// assembly-funktio, joka käyttää molempia.
#ifndef LASKURI_H
#define LASKURI_H

// @alku rajapinta
extern long laskuri;            // määritelty C:ssä (main.c)
long tuplaa(long x);            // C-funktio, jota assembly kutsuu
// Assembly: laskuri += maara; return tuplaa(laskuri);
long lisaa_ja_tuplaa(long maara);
// @loppu rajapinta

#endif
