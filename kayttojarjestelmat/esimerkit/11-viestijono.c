// POSIX-viestijono: viestit säilyttävät rajansa ja tulevat ulos
// prioriteettijärjestyksessä.
#define _GNU_SOURCE
#include <fcntl.h>
#include <mqueue.h>
#include <unistd.h>

#include "tarkista.h"

int main(void) {
    // @alku jono
    char nimi[64];
    snprintf(nimi, sizeof nimi, "/kj-jono-%d", (int)getpid());
    // @alku ydin
    struct mq_attr ominaisuudet = {.mq_maxmsg = 4, .mq_msgsize = 64};
    mqd_t jono = (mqd_t)TARKISTA(mq_open(nimi, O_RDWR | O_CREAT | O_EXCL,
                                          0600, &ominaisuudet));
    TARKISTA(mq_unlink(nimi));
    // @loppu ydin

    struct { const char *teksti; unsigned prioriteetti; } viestit[] = {
        {"tavallinen", 1}, {"kiireellinen", 5}, {"normaali", 3},
        {"toinen tavallinen", 1},
    };
    // @alku ydin
    for (int i = 0; i < 4; i++) {
        TARKISTA(mq_send(jono, viestit[i].teksti,
                         strlen(viestit[i].teksti) + 1,
                         viestit[i].prioriteetti));
    }
    // @loppu ydin
    TARKISTA(mq_getattr(jono, &ominaisuudet));
    printf("jonossa %ld viestiä\n", ominaisuudet.mq_curmsgs);

    // Jono on täynnä: estämätön lähetys epäonnistuu heti.
    ominaisuudet.mq_flags = O_NONBLOCK;
    TARKISTA(mq_setattr(jono, &ominaisuudet, nullptr));
    if (mq_send(jono, "liikaa", 7, 1) == -1) {
        printf("täysi jono: %s\n", strerrorname_np(errno));
    }
    char puskuri[64];
    unsigned prioriteetti;
    // @alku ydin
    while (mq_receive(jono, puskuri, sizeof puskuri, &prioriteetti) > 0) {
        printf("prioriteetti %u: %s\n", prioriteetti, puskuri);
    }
    // @loppu ydin
    printf("tyhjä jono: %s\n", strerrorname_np(errno));
    TARKISTA(mq_close(jono));
    // @loppu jono
    return 0;
}
