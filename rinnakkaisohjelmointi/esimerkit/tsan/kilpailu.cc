// Datakilpailu: kaksi säiettä kasvattaa tavallista laskuria.
// ThreadSanitizer raportoi kilpailun, vaikka tulos sattuisi olemaan
// oikea: se seuraa tapahtumisjärjestystä, ei ajoitusta.
#include <print>
#include <thread>

// @alku kilpailu
int osumia = 0;                      // ei atominen, ei lukkoa

void laske()
{
    for (int i = 0; i < 1'000; ++i) {
        ++osumia;                    // luku + kirjoitus
    }
}

int main()
{
    {
        std::jthread a{laske};
        std::jthread b{laske};
    }
    std::println("osumia {}", osumia);
}
// @loppu kilpailu
