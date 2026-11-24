/* Debianin OpenSSL 2006-2008: satunnaislukualtaan päivitys
 * (md_rand.c, yksinkertaistettu). Debianin paikka kommentoi rivin pois,
 * koska Valgrind varoitti alustamattoman muistin käytöstä. */
static void satunnaisuutta_lisaa(const void *puskuri, int maara)
{
    /* ... */
    /* MD_Update(&m, puskuri, j); */  /* poistettu: entropia katosi */
    /* ... */
}
