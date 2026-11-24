/* Tapahtumaloki, joka kirjaa käyttäjän antamat viestit. Tarkoituksella
 * haavoittuva: viesti annetaan printf:lle muotoilumerkkijonona. */
#include <stdio.h>
#include <string.h>

// @alku kirjaa
static void kirjaa(const char *viesti)
{
    printf("[loki] ");
#ifdef KORJATTU
    printf("%s", viesti);               /* viesti on dataa */
#else
    printf(viesti);                     /* VIRHE: viesti on muotoilua */
#endif
    printf("\n");
}
// @loppu kirjaa

// @alku kasittele
static void kasittele(void)
{
    /* Salaisuus, jonka ei pitäisi koskaan päätyä lokiin. */
    volatile unsigned long istuntoavain = 0x1d2c3b4a59687706UL;
    char rivi[128];
    while (fgets(rivi, sizeof rivi, stdin) != NULL) {
        rivi[strcspn(rivi, "\n")] = '\0';
        kirjaa(rivi);
    }
    (void)istuntoavain;
}
// @loppu kasittele

int main(void)
{
    kasittele();
    return 0;
}
