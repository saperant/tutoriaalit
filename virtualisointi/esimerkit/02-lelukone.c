// Lelusuoritin, jolla näkyvät virtualisoinnin perusongelma ja sen kolme
// ratkaisua. Vieraana on käyttöjärjestelmän ytimen pätkä, joka kieltää
// keskeytykset, lukee keskeytyslipun ja palauttaa sen.
//
// Käskyistä CLI, STI, OUT ja HLT ovat etuoikeutettuja: käyttäjätilassa
// ne aiheuttavat ansan (trap). LUEIF ja ASETAIF ovat x86:n PUSHF- ja
// POPF-käskyjen kaltaisia: ne ovat sensitiivisiä (näkevät tai muuttavat
// koneen tilaa), mutta EIVÄT aiheuta ansaa käyttäjätilassa.
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>

// @alku kaskyt
enum koodi { LOAD, CLI, STI, LUEIF, ASETAIF, OUT, HLT, ANSA };

struct kasky {
    enum koodi koodi;
    int arg;
};

struct kone {
    int acc;            // akku
    bool keskeytykset;  // keskeytyslippu (IF)
    bool ytintila;      // true: etuoikeutettu tila (rengas 0)
    bool vierastila;    // laitteistotuki: ajetaan vierastilassa
};

enum tapahtuma { JATKA, ANSA_TAPAHTUI, PYSAHDY };

static bool etuoikeutettu(enum koodi k)
{
    return k == CLI || k == STI || k == OUT || k == HLT;
}
// @loppu kaskyt

// Vieraan ydin. Oikealla raudalla se tulostaa 0 ja jättää keskeytykset
// sallituiksi.
static const struct kasky vieras[] = {
    {CLI, 0},       // kiellä keskeytykset
    {LUEIF, 0},     // acc = IF (pitäisi olla 0)
    {OUT, 0},       // tulosta acc
    {ASETAIF, 1},   // palauta keskeytykset (kuten POPF)
    {HLT, 0},
};
enum { PITUUS = sizeof vieras / sizeof vieras[0] };

// @alku askel
// Suorittaa yhden käskyn kuten rauta. Palauttaa ANSA_TAPAHTUI, jos
// käsky on käyttäjätilassa kielletty (tai binäärikäännöksen lisäämä
// ANSA) tai jos vierastilassa suoritetaan I/O- tai HLT-käsky.
static enum tapahtuma askel(struct kone *k, struct kasky c)
{
    if (c.koodi == ANSA)
        return ANSA_TAPAHTUI;
    if (k->vierastila) {
        if (c.koodi == OUT || c.koodi == HLT)
            return ANSA_TAPAHTUI;          // VM exit
    } else if (!k->ytintila && etuoikeutettu(c.koodi)) {
        return ANSA_TAPAHTUI;
    }
    switch (c.koodi) {
    case LOAD:    k->acc = c.arg; break;
    case CLI:     k->keskeytykset = false; break;
    case STI:     k->keskeytykset = true; break;
    case LUEIF:   k->acc = k->keskeytykset; break;
    case ASETAIF:
        if (k->ytintila || k->vierastila)
            k->keskeytykset = c.arg != 0;
        break;      // käyttäjätilassa muutos ohitetaan hiljaa!
    case OUT:     printf(" %d", k->acc); break;
    case HLT:     return PYSAHDY;
    case ANSA:    break;
    }
    return JATKA;
}
// @loppu askel

struct tulos {
    bool keskeytykset;  // vieraan näkemä IF lopussa
    int ansoja;
};

// Suoraan raudalla: vieras on ytintilassa ja omistaa koneen.
static struct tulos raudalla(void)
{
    struct kone k = {.keskeytykset = true, .ytintila = true};
    for (size_t pc = 0; askel(&k, vieras[pc]) != PYSAHDY; pc++) {
    }
    return (struct tulos){k.keskeytykset, 0};
}

// @alku vmm
// Hypervisor: vieras ajetaan käyttäjätilassa. Ansan tullen VMM emuloi
// käskyn vieraan VIRTUAALISTA tilaa vasten (v_if). Oikea IF pysyy
// isännän hallussa ja on koko ajan 1.
static struct tulos hypervisor(const struct kasky *koodi, bool vt)
{
    struct kone k = {.keskeytykset = true, .vierastila = vt};
    bool v_if = true;
    int ansoja = 0;
    for (size_t pc = 0; pc < PITUUS; pc++) {
        enum tapahtuma t = askel(&k, koodi[pc]);
        if (t == PYSAHDY)
            break;
        if (t != ANSA_TAPAHTUI)
            continue;
        ansoja++;
        struct kasky alkup = vieras[pc];   // käskyn alkuperäinen muoto
        if (alkup.koodi == HLT)
            break;
        switch (alkup.koodi) {
        case CLI:     v_if = false; break;
        case STI:     v_if = true; break;
        case LUEIF:   k.acc = v_if; break;
        case ASETAIF: v_if = alkup.arg != 0; break;
        case OUT:     printf(" %d", k.acc); break;
        default:      break;
        }
    }
    // Laitteistotuessa IF kuuluu vieraan omaan tilaan (VMCS).
    return (struct tulos){vt ? k.keskeytykset : v_if, ansoja};
}
// @loppu vmm

// @alku kaannos
// Binäärikäännös: VMM käy vieraan koodin läpi ennen suoritusta ja
// korvaa sensitiiviset mutta ansoja aiheuttamattomat käskyt ANSAlla.
static void kaanna(struct kasky *kohde)
{
    for (size_t i = 0; i < PITUUS; i++) {
        kohde[i] = vieras[i];
        if (vieras[i].koodi == LUEIF || vieras[i].koodi == ASETAIF)
            kohde[i] = (struct kasky){ANSA, 0};
    }
}
// @loppu kaannos

static void raportti(struct tulos t)
{
    printf("   | IF lopussa %d | ansoja %d\n", t.keskeytykset, t.ansoja);
}

int main(void)
{
    struct kasky kaannetty[PITUUS];
    kaanna(kaannetty);

    printf("%-18s tuloste:", "suoraan raudalla");
    raportti(raudalla());
    printf("%-18s tuloste:", "trap-and-emulate");
    raportti(hypervisor(vieras, false));
    printf("%-18s tuloste:", "binaarikaannos");
    raportti(hypervisor(kaannetty, false));
    printf("%-18s tuloste:", "laitteistotuki");
    raportti(hypervisor(vieras, true));
    return 0;
}
