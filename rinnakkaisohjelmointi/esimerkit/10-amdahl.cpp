// Amdahlin ja Gustafsonin lait: odotettavissa oleva nopeutus, kun osa
// työstä on sarjallista.
#include <print>

// @alku lait
// Amdahl: kiinteä tehtävä, sarjallinen osuus s, p suoritinta.
double amdahl(double s, int p)
{
    return 1.0 / (s + (1.0 - s) / p);
}

// Gustafson: tehtävä kasvaa suorittimien mukana; s on sarjallinen osuus
// rinnakkaisen koneen ajasta.
double gustafson(double s, int p)
{
    return s + (1.0 - s) * p;
}
// @loppu lait

int main()
{
    // @alku taulukko
    std::println("{:>7} {:>6} {:>6} {:>6} {:>6} {:>9}", "sarja", "p=4",
                 "p=16", "p=64", "raja", "G, p=64");
    for (double s : {0.01, 0.05, 0.10, 0.25}) {
        std::println("{:5.0f} % {:6.2f} {:6.2f} {:6.2f} {:6.1f} {:9.1f}",
                     s * 100, amdahl(s, 4), amdahl(s, 16), amdahl(s, 64),
                     1.0 / s, gustafson(s, 64));
    }
    // @loppu taulukko
}
