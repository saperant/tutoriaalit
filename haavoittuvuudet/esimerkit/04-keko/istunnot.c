/* Istuntojen hallinta keossa. Tarkoituksella haavoittuva: jokainen
 * komentoriviltä valittava tapaus sisältää yhden yleisen kekovirheen.
 * Käyttö: istunnot ylivuoto | vapautettu | uudelleenkaytto | tupla */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct istunto {
    char kayttaja[16];
    int oikeudet;                       /* 0 = tavallinen, 1 = ylläpito */
    int avoinna;
};

static struct istunto *avaa(const char *kayttaja)
{
    struct istunto *uusi = malloc(sizeof *uusi);
    if (uusi == NULL) {
        exit(1);
    }
    memset(uusi, 0, sizeof *uusi);
    snprintf(uusi->kayttaja, sizeof uusi->kayttaja, "%s", kayttaja);
    uusi->avoinna = 1;
    return uusi;
}

// @alku ylivuoto
/* VIRHE: kopioi koko muistiinpanon, vaikka varaus on 16 tavua. */
static void ylivuoto(void)
{
    const char *muistiinpano = "muistiinpano, joka ei mahdu kenttaan";
    char *kentta = malloc(16);
    struct istunto *seuraava = avaa("vieras");
    if (kentta == NULL) {
        exit(1);
    }
    memcpy(kentta, muistiinpano, strlen(muistiinpano) + 1);
    free(seuraava);
    free(kentta);
}
// @loppu ylivuoto

// @alku vapautettu
/* VIRHE: istunto vapautetaan uloskirjautuessa, mutta osoitin jää
 * talteen ja sitä käytetään myöhemmin. */
static void vapautettu(void)
{
    struct istunto *istunto = avaa("aino");
    struct istunto *viimeisin = istunto;  /* toinen viittaus */
    free(istunto);                         /* uloskirjautuminen */
    printf("viimeisin käyttäjä: %s\n", viimeisin->kayttaja);
}
// @loppu vapautettu

// @alku uudelleenkaytto
/* Miksi käyttö vapautuksen jälkeen on vaarallinen: vapautettu muisti
 * annetaan seuraavalle samankokoiselle varaukselle. Vanha osoitin
 * osoittaa nyt toisen käyttäjän istuntoon. */
static void uudelleenkaytto(void)
{
    struct istunto *vanha = avaa("vieras");
    free(vanha);
    struct istunto *uusi = avaa("yllapitaja");
    uusi->oikeudet = 1;
    printf("sama muisti uudelleen: %s\n", (void *)vanha == (void *)uusi
           ? "kyllä" : "ei");
}
// @loppu uudelleenkaytto

// @alku tupla
/* VIRHE: virhepolku vapauttaa istunnon, ja siivous vapauttaa sen
 * uudelleen. */
static void tupla(void)
{
    struct istunto *istunto = avaa("aino");
    if (istunto->oikeudet == 0) {
        free(istunto);                  /* virhepolku */
    }
    free(istunto);                      /* siivous */
}
// @loppu tupla

int main(int argc, char *argv[])
{
    const char *tapaus = argc > 1 ? argv[1] : "";
    if (strcmp(tapaus, "ylivuoto") == 0) {
        ylivuoto();
    } else if (strcmp(tapaus, "vapautettu") == 0) {
        vapautettu();
    } else if (strcmp(tapaus, "uudelleenkaytto") == 0) {
        uudelleenkaytto();
    } else if (strcmp(tapaus, "tupla") == 0) {
        tupla();
    } else {
        fprintf(stderr, "tuntematon tapaus\n");
        return 2;
    }
    return 0;
}
