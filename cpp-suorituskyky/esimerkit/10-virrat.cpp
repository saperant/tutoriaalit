// Virran tyhjennysten määrä: std::endl tyhjentää puskurin joka rivillä,
// '\n' vain lisää merkin. Tiedostovirrassa jokainen tyhjennys on
// järjestelmäkutsu.
#include <cstdio>
#include <ostream>
#include <sstream>

// @alku laskeva
// Puskuri, joka laskee tyhjennyspyynnöt (sync). Oikea tiedostopuskuri
// tekisi tässä kohdassa write-järjestelmäkutsun.
class LaskevaPuskuri : public std::stringbuf {
public:
    int tyhjennykset() const { return tyhjennykset_; }

protected:
    int sync() override
    {
        ++tyhjennykset_;
        return std::stringbuf::sync();
    }

private:
    int tyhjennykset_ = 0;
};
// @loppu laskeva

int main()
{
    // @alku testi
    LaskevaPuskuri endl_puskuri;
    std::ostream endl_virta{&endl_puskuri};
    for (int i = 0; i < 1000; ++i) {
        endl_virta << i << std::endl;      // rivinvaihto ja flush
    }

    LaskevaPuskuri rivinvaihto_puskuri;
    std::ostream rivinvaihto_virta{&rivinvaihto_puskuri};
    for (int i = 0; i < 1000; ++i) {
        rivinvaihto_virta << i << '\n';    // vain merkki puskuriin
    }
    rivinvaihto_virta.flush();             // yksi tyhjennys lopuksi

    std::printf("std::endl: tyhjennyksia %d\n", endl_puskuri.tyhjennykset());
    std::printf("'\\n':      tyhjennyksia %d\n",
                rivinvaihto_puskuri.tyhjennykset());
    std::printf("sama sisalto: %s\n",
                endl_puskuri.str() == rivinvaihto_puskuri.str() ? "kylla"
                                                                : "ei");
    // @loppu testi
}
