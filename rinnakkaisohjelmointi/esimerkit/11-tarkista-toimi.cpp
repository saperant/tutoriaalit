// TSAN
// Atomisuusvirhe, jota ThreadSanitizer ei näe: jokainen operaatio on
// atominen, mutta tarkistus ja toiminta eivät ole yhtenä operaationa.
// Este pakottaa pahimman lomituksen, joten tulos on aina sama.
#include <atomic>
#include <barrier>
#include <print>
#include <thread>

// @alku virheellinen
bool nosta_virheellisesti(std::atomic<int>& saldo, int summa,
                          std::barrier<>& este)
{
    if (saldo.load() < summa) {        // tarkista...
        return false;
    }
    este.arrive_and_wait();            // (molemmat ehtivät tarkistaa)
    saldo.fetch_sub(summa);            // ...ja toimi: tarkistus vanhentui
    return true;
}
// @loppu virheellinen

// @alku oikea
bool nosta(std::atomic<int>& saldo, int summa, std::barrier<>& este)
{
    int nyt = saldo.load();
    este.arrive_and_wait();            // sama lomitus kuin yllä
    do {
        if (nyt < summa) {
            return false;
        }
    } while (!saldo.compare_exchange_weak(nyt, nyt - summa));
    return true;                       // tarkistus ja vähennys yhdessä
}
// @loppu oikea

template <class Nosto>
void kokeile(const char* nimi, Nosto nosto)
{
    std::atomic<int> saldo{100};
    std::barrier<> este{2};
    std::atomic<int> onnistui{0};
    {
        std::jthread a{[&] { onnistui += nosto(saldo, 100, este); }};
        std::jthread b{[&] { onnistui += nosto(saldo, 100, este); }};
    }
    std::println("{}: nostoja {}, saldo {}", nimi, onnistui.load(),
                 saldo.load());
}

int main()
{
    kokeile("tarkista ja toimi", nosta_virheellisesti);
    kokeile("compare_exchange", nosta);
}
