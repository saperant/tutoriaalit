/* Baron Samedit 2021, sudo: argumenttien kopiointi (periaate).
 * Kenoviiva ohittaa seuraavan merkin. Jos argumentti päättyy
 * kenoviivaan, seuraava merkki on loppunolla, ja kopiointi jatkuu
 * seuraavaan argumenttiin kirjoittaen yli varatun puskurin. */
for (const char *mista = argumentti; *mista != '\0'; mista++) {
    if (mista[0] == '\\' && mista[1] != '\0'    /* korjaus lisäsi */
        && !isspace((unsigned char)mista[1])) {
        mista++;
    }
    *mihin++ = *mista;
}
