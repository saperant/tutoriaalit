// getaddrinfo muuntaa nimen ja palvelun osoiterakenteiksi
// osoiteperheestä riippumatta. Asiakas kokeilee osoitteita järjestyksessä,
// kunnes yhteys syntyy.
#define _GNU_SOURCE
#include <netdb.h>

#include "verkko.h"

// @alku nayta
static void nayta(const char *isanta) {
    struct addrinfo vihjeet = {};
    vihjeet.ai_flags = AI_NUMERICHOST | AI_NUMERICSERV;  // ei DNS:ää
    vihjeet.ai_family = AF_UNSPEC;       // IPv4 tai IPv6
    vihjeet.ai_socktype = SOCK_STREAM;
    struct addrinfo *tulos;
    int virhe = getaddrinfo(isanta, "8080", &vihjeet, &tulos);
    if (virhe != 0) {                    // ei errno: oma virhekoodi
        printf("%-14s virhe: %s\n", isanta, gai_strerror(virhe));
        return;
    }
    for (struct addrinfo *a = tulos; a != nullptr; a = a->ai_next) {
        char nimi[NI_MAXHOST], palvelu[NI_MAXSERV];
        getnameinfo(a->ai_addr, a->ai_addrlen, nimi, sizeof nimi,
                    palvelu, sizeof palvelu,
                    NI_NUMERICHOST | NI_NUMERICSERV);
        printf("%-14s %s, %2u tavua: [%s]:%s\n", isanta,
               a->ai_family == AF_INET6 ? "AF_INET6" : "AF_INET ",
               (unsigned)a->ai_addrlen, nimi, palvelu);
    }
    freeaddrinfo(tulos);
}
// @loppu nayta

// @alku yhdista
// Yhdistää palveluun kokeillen jokaista osoitetta. Palauttaa soketin tai
// -1. Jos IPv6 puuttuu (socket: EAFNOSUPPORT) tai osoitteessa ei ole
// kuuntelijaa (ECONNREFUSED), kokeillaan seuraavaa.
static int yhdista_palveluun(const char *isanta, const char *palvelu) {
    struct addrinfo vihjeet = {};
    vihjeet.ai_family = AF_UNSPEC;
    vihjeet.ai_socktype = SOCK_STREAM;
    struct addrinfo *tulos;
    if (getaddrinfo(isanta, palvelu, &vihjeet, &tulos) != 0) {
        return -1;
    }
    int fd = -1;
    for (struct addrinfo *a = tulos; a != nullptr; a = a->ai_next) {
        fd = socket(a->ai_family, a->ai_socktype, a->ai_protocol);
        if (fd == -1) {
            continue;
        }
        if (connect(fd, a->ai_addr, a->ai_addrlen) == 0) {
            break;                       // onnistui
        }
        fprintf(stderr, "ohitetaan: %s\n", strerrorname_np(errno));
        close(fd);
        fd = -1;
    }
    freeaddrinfo(tulos);
    return fd;
}
// @loppu yhdista

int main(void) {
    vahtikoira();
    const char *isannat[] = {"127.0.0.1", "::1", "2001:db8::42",
                             "192.0.2.300", "esimerkki.fi"};
    for (size_t i = 0; i < 5; i++) {
        nayta(isannat[i]);
    }

    // @alku kaytto
    uint16_t portti;
    int kuuntelija = kuuntele(&portti);  // vain 127.0.0.1
    char palvelu[8];
    snprintf(palvelu, sizeof palvelu, "%u", portti);
    // Isäntä nullptr: silmukkaosoitteet ::1 ja 127.0.0.1.
    int fd = yhdista_palveluun(nullptr, palvelu);
    // @loppu kaytto
    if (fd == -1) {
        return 1;
    }
    struct sockaddr_storage vertainen;  // mahtuu mikä tahansa osoite
    socklen_t pituus = sizeof vertainen;
    TARKISTA(getpeername(fd, (struct sockaddr *)&vertainen, &pituus));
    char nimi[NI_MAXHOST];
    getnameinfo((struct sockaddr *)&vertainen, pituus, nimi, sizeof nimi,
                nullptr, 0, NI_NUMERICHOST);
    printf("yhteys syntyi osoitteeseen %s\n", nimi);
    close(fd);
    close(kuuntelija);
    return 0;
}
