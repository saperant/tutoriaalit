#include <print>
#include <string>

// @alku parametrit
struct Mittaus {
    std::string anturi;
    double arvo;
};

// Arvoparametri: funktio saa oman kopionsa.
void nollaa_kopio(Mittaus m) { m.arvo = 0.0; }

// Viittausparametri: funktio muuttaa kutsujan oliota.
void nollaa(Mittaus& m) { m.arvo = 0.0; }

// Vakioviittaus: ei kopiota, eikä funktio voi muuttaa oliota.
void tulosta(const Mittaus& m)
{
    std::println("{}: {}", m.anturi, m.arvo);
}
// @loppu parametrit

int main()
{
    // @alku alias
    int luku = 1;
    int& viittaus = luku;   // toinen nimi samalle muuttujalle
    viittaus = 2;
    std::println("luku = {}", luku);

    int toinen = 10;
    viittaus = toinen;      // sijoittaa arvon; ei siirrä viittausta
    std::println("luku = {}, toinen = {}", luku, toinen);
    // @loppu alias

    // @alku kutsut
    Mittaus m{"T1", 21.5};
    nollaa_kopio(m);
    tulosta(m);
    nollaa(m);
    tulosta(m);
    // @loppu kutsut
}
