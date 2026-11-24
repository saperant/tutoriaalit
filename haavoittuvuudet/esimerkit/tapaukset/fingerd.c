/* Morrisin mato 1988, fingerd: periaate (yksinkertaistettu). */
char rivi[512];

gets(rivi);                          /* ennen: pituutta ei rajata */

fgets(rivi, sizeof rivi, stdin);     /* jälkeen: koko kulkee mukana */
