// ABA-ongelma askel askeleelta. Pino on indekseihin perustuva (solmut
// kierrätetään taulukosta), ja kahden säikeen lomitus ajetaan yhdessä
// säikeessä käsin, jotta lopputulos on aina sama.
#include <array>
#include <atomic>
#include <cstdint>
#include <print>
#include <string>

// @alku pino
constexpr std::uint32_t tyhja = 0xFFFF'FFFF;

// Pään 64 bittiä: ylempi puolisko on versiolaskuri, alempi indeksi.
struct Pino {
    std::array<std::uint32_t, 4> seuraava{};
    std::atomic<std::uint64_t> paa{tyhja};
    bool versioi;

    static std::uint32_t indeksi(std::uint64_t p)
    {
        return static_cast<std::uint32_t>(p);
    }
    std::uint64_t uusi_paa(std::uint64_t vanha, std::uint32_t i) const
    {
        const std::uint64_t versio = versioi ? (vanha >> 32) + 1 : 0;
        return versio << 32 | i;
    }
    void laita(std::uint32_t i)
    {
        std::uint64_t p = paa.load();
        do {
            seuraava[i] = indeksi(p);
        } while (!paa.compare_exchange_weak(p, uusi_paa(p, i)));
    }
    // Poiston viimeinen vaihe: CAS havaittuun päähän.
    bool vaihda(std::uint64_t havaittu, std::uint32_t uusi)
    {
        return paa.compare_exchange_strong(havaittu,
                                           uusi_paa(havaittu, uusi));
    }
    std::uint32_t ota()
    {
        std::uint64_t p = paa.load();
        while (!vaihda(p, seuraava[indeksi(p)])) {
            p = paa.load();
        }
        return indeksi(p);
    }
};
// @loppu pino

std::string sisalto(const Pino& pino)
{
    std::string s;
    for (std::uint32_t i = Pino::indeksi(pino.paa.load()); i != tyhja;
         i = pino.seuraava[i]) {
        s += static_cast<char>('A' + i);
        if (s.size() > 6) {
            return s + "... (silmukka)";
        }
    }
    return s.empty() ? "tyhja" : s;
}

void kokeile(bool versioi)
{
    // @alku lomitus
    Pino pino{.versioi = versioi};
    pino.laita(2);  // C
    pino.laita(1);  // B
    pino.laita(0);  // A  -> pino A B C
    // Säie 1 aloittaa poiston: lukee pään (A) ja sen seuraajan (B)...
    const std::uint64_t havaittu = pino.paa.load();
    const std::uint32_t seuraaja = pino.seuraava[Pino::indeksi(havaittu)];
    // ...ja keskeytyy. Säie 2 ottaa A:n ja B:n ja palauttaa A:n.
    const std::uint32_t a = pino.ota();
    const std::uint32_t b = pino.ota();
    pino.laita(a);                       // pino A C, B on säikeellä 2
    // Säie 1 jatkaa: pää on taas A, joten pelkkä osoitin ei paljasta
    // muutosta.
    const bool onnistui = pino.vaihda(havaittu, seuraaja);
    // @loppu lomitus
    std::println("{}: saikeen 1 CAS {}, pino nyt {}, B saikeella 2: {}",
                 versioi ? "versiolaskurilla" : "ilman versiota",
                 onnistui ? "onnistui" : "epaonnistui", sisalto(pino),
                 b == 1 ? "kylla" : "ei");
}

int main()
{
    kokeile(false);
    kokeile(true);
}
