/* Cloudbleed 2017: puskurin lopun tarkistus (periaate). Jäsennin
 * saattoi siirtää osoitinta yli lopun, jolloin yhtäsuuruus ei
 * koskaan toteutunut ja luku jatkui puskurin ulkopuolelle. */
if (++p == pe)          /* ennen: ohittaa lopun, jos p hyppää yli */
    goto loppu;

if (++p >= pe)          /* jälkeen: pysähtyy myös yli mentäessä */
    goto loppu;
