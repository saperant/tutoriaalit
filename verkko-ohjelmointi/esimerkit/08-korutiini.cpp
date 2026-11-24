// Sama palvelinlogiikka C++20-korutiineina: istunto kirjoitetaan
// peräkkäisenä koodina, ja co_await luovuttaa vuoron tapahtumasilmukalle,
// kunnes soketti on valmis. Silmukka jatkaa korutiinia epollin
// ilmoituksesta.
#include <sys/epoll.h>

#include <coroutine>
#include <cstdio>
#include <exception>

#include "nelio.h"

namespace {

constexpr int asiakkaita = 20;
constexpr int kierroksia = 10;
uint16_t portti;

// @alku tehtava
// Itsenäinen tehtävä: käynnistyy heti ja vapauttaa kehyksensä
// päättyessään. Paluuarvoa ei odoteta.
struct Tehtava {
    struct promise_type {
        Tehtava get_return_object() { return {}; }
        std::suspend_never initial_suspend() noexcept { return {}; }
        std::suspend_never final_suspend() noexcept { return {}; }
        void return_void() {}
        void unhandled_exception() { std::terminate(); }
    };
};
// @loppu tehtava

// @alku reaktori
class Reaktori {
public:
    Reaktori() : ep_(static_cast<int>(TARKISTA(epoll_create1(0)))) {}
    ~Reaktori() { close(ep_); }
    Reaktori(const Reaktori &) = delete;
    Reaktori &operator=(const Reaktori &) = delete;

    // Odotettava: co_await r.luettavissa(fd) keskeyttää korutiinin, ja
    // epoll jatkaa sitä, kun fd on luettavissa (EPOLLONESHOT: kerran).
    struct Luettavissa {
        Reaktori &r;
        int fd;
        bool await_ready() const noexcept { return false; }
        void await_suspend(std::coroutine_handle<> jatko) const {
            epoll_event e{};
            e.events = EPOLLIN | EPOLLONESHOT;
            e.data.ptr = jatko.address();
            if (epoll_ctl(r.ep_, EPOLL_CTL_MOD, fd, &e) == -1) {
                TARKISTA(epoll_ctl(r.ep_, EPOLL_CTL_ADD, fd, &e));
            }
        }
        void await_resume() const noexcept {}
    };
    Luettavissa luettavissa(int fd) { return {*this, fd}; }

    void aja() {
        while (kaynnissa > 0) {
            epoll_event valmiit[16];
            int n = static_cast<int>(TARKISTA(epoll_wait(ep_, valmiit, 16,
                                                         -1)));
            for (int i = 0; i < n; i++) {
                std::coroutine_handle<>::from_address(valmiit[i].data.ptr)
                    .resume();
            }
        }
    }
    int kaynnissa = 0;                   // keskeneräiset korutiinit

private:
    int ep_;
};
// @loppu reaktori

// @alku istunto
Tehtava istunto(Reaktori &r, int fd) {
    r.kaynnissa++;
    yhteys y{};
    y.fd = fd;
    for (;;) {
        co_await r.luettavissa(fd);
        ssize_t n = recv(fd, y.sisaan + y.n, sizeof y.sisaan - y.n, 0);
        if (n == -1 && errno == EAGAIN) {
            continue;
        }
        if (n <= 0) {
            break;
        }
        y.n += static_cast<size_t>(n);
        if (kasittele_rivit(&y) < 0) {
            break;
        }
    }
    close(fd);                           // poistaa myös epollista
    r.kaynnissa--;
}

Tehtava hyvaksyja(Reaktori &r, int kuuntelija, int maara) {
    r.kaynnissa++;
    for (int i = 0; i < maara; i++) {
        co_await r.luettavissa(kuuntelija);
        int fd = accept4(kuuntelija, nullptr, nullptr, SOCK_NONBLOCK);
        if (fd >= 0) {
            istunto(r, fd);              // käynnistyy ja keskeytyy heti
        }
    }
    r.kaynnissa--;
}
// @loppu istunto

int kuormittaja(void *) {
    return kuormita(portti, asiakkaita, kierroksia) == 0 ? 0 : 1;
}

}  // namespace

int main() {
    vahtikoira();
    int kuuntelija = kuuntele(&portti);
    pid_t pid = kaynnista(kuormittaja, nullptr);
    Reaktori r;
    hyvaksyja(r, kuuntelija, asiakkaita);
    r.aja();
    close(kuuntelija);
    int tulos = odota(pid);
    std::printf("korutiinit: %d asiakasta palveltu, virheitä: %s\n",
                asiakkaita, tulos == 0 ? "ei" : "on");
    return tulos;
}
