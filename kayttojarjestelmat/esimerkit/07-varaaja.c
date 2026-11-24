// Oma muistinvaraaja kiinteän kokoisessa keossa: implisiittinen
// lohkolista, first fit ja best fit, lohkon pilkkominen ja vapaiden
// naapurien yhdistäminen.
#include <stddef.h>
#include <stdio.h>

// @alku rakenne
enum { KEON_KOKO = 1024, TASAUS = 16, PIENIN = 32 };

typedef struct {
    alignas(TASAUS) size_t koko;     // koko lohko otsakkeineen
    bool vapaa;
} otsake_t;                          // 16 tavua: hyötykuorma tasattu

alignas(TASAUS) static unsigned char keko[KEON_KOKO];

static otsake_t *ensimmainen(void) { return (otsake_t *)keko; }

static otsake_t *seuraava(otsake_t *o) {
    unsigned char *s = (unsigned char *)o + o->koko;
    return s < keko + KEON_KOKO ? (otsake_t *)s : nullptr;
}
// @loppu rakenne

typedef enum { FIRST_FIT, BEST_FIT } strategia_t;

static void alusta(void) {
    *ensimmainen() = (otsake_t){.koko = KEON_KOKO, .vapaa = true};
}

// @alku varaa
static void *varaa(size_t n, strategia_t s) {
    size_t tarve = sizeof(otsake_t) + (n + TASAUS - 1) / TASAUS * TASAUS;
    otsake_t *valittu = nullptr;
    for (otsake_t *o = ensimmainen(); o; o = seuraava(o)) {
        if (!o->vapaa || o->koko < tarve) {
            continue;
        }
        if (s == FIRST_FIT) {            // ensimmäinen riittävä
            valittu = o;
            break;
        }
        if (!valittu || o->koko < valittu->koko) {
            valittu = o;                 // pienin riittävä
        }
    }
    if (!valittu) {
        return nullptr;
    }
    if (valittu->koko - tarve >= PIENIN) {   // pilkotaan loppu irti
        otsake_t *loppu = (otsake_t *)((unsigned char *)valittu + tarve);
        *loppu = (otsake_t){.koko = valittu->koko - tarve, .vapaa = true};
        valittu->koko = tarve;
    }
    valittu->vapaa = false;
    return valittu + 1;                  // hyötykuorma otsakkeen perässä
}
// @loppu varaa

// @alku vapauta
static void vapauta(void *p) {
    if (p == nullptr) {
        return;
    }
    ((otsake_t *)p - 1)->vapaa = true;
    // Yhdistetään vierekkäiset vapaat lohkot. Implisiittisessä listassa
    // edeltäjää ei löydä suoraan, joten käydään koko lista läpi.
    for (otsake_t *o = ensimmainen(); o; o = seuraava(o)) {
        otsake_t *s;
        while (o->vapaa && (s = seuraava(o)) && s->vapaa) {
            o->koko += s->koko;
        }
    }
}
// @loppu vapauta

// @alku kartta
static void kartta(const char *otsikko) {
    size_t vapaata = 0, suurin = 0;
    printf("%-14s", otsikko);
    for (otsake_t *o = ensimmainen(); o; o = seuraava(o)) {
        printf(" %c%zu", o->vapaa ? 'V' : 'K', o->koko);
        if (o->vapaa) {
            vapaata += o->koko;
            suurin = o->koko > suurin ? o->koko : suurin;
        }
    }
    printf("\n%14s vapaata %zu, suurin %zu, ulkoinen pirstoutuminen "
           "%zu %%\n", "", vapaata, suurin,
           vapaata ? 100 - 100 * suurin / vapaata : 0);
}
// @loppu kartta

// @alku skenaario
static void skenaario(strategia_t s) {
    alusta();
    void *a = varaa(300, s), *b = varaa(40, s);
    void *c = varaa(100, s), *d = varaa(40, s);
    vapauta(a);
    vapauta(c);
    kartta("a ja c pois:");
    void *e = varaa(100, s);
    kartta("varaa(100):");
    void *f = varaa(280, s);
    kartta("varaa(280):");
    void *g = varaa(400, s);
    printf("%-14s %s\n", "varaa(400):", g ? "onnistui" : "EPÄONNISTUI");
    void *kaikki[] = {b, d, e, f, g};
    for (size_t i = 0; i < sizeof kaikki / sizeof kaikki[0]; i++) {
        vapauta(kaikki[i]);
    }
    kartta("kaikki pois:");
}
// @loppu skenaario

int main(void) {
    printf("== first fit\n");
    skenaario(FIRST_FIT);
    printf("== best fit\n");
    skenaario(BEST_FIT);
    return 0;
}
