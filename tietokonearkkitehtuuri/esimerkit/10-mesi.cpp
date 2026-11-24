// MESI-koherenssiprotokolla nuuskivalla väylällä: tilat ja
// väylätapahtumat viite viitteeltä, MSI vs. MESI ja väärä jakaminen.
#include <array>
#include <map>
#include <print>
#include <string>
#include <vector>

// @alku protokolla
enum class Tila { I, S, E, M };

struct Laskurit { int vayla = 0, mitatoinnit = 0, takaisin = 0; };

template <int YTIMET>
class Koherenssi {
public:
    explicit Koherenssi(bool mesi, unsigned lohko = 64)
        : mesi_(mesi), lohko_(lohko) {}

    // Palauttaa väylätapahtuman nimen ("" = osuma, ei väylää).
    std::string lue(int y, unsigned osoite) {
        auto& t = tilat_[osoite / lohko_];
        if (t[y] != Tila::I) return "";
        bool muilla = false;
        for (int i = 0; i < YTIMET; ++i) {
            if (i == y || t[i] == Tila::I) continue;
            muilla = true;
            if (t[i] == Tila::M) ++l_.takaisin;  // likainen data muistiin
            t[i] = Tila::S;
        }
        t[y] = muilla || !mesi_ ? Tila::S : Tila::E;
        ++l_.vayla;
        return "BusRd";
    }

    std::string kirjoita(int y, unsigned osoite) {
        auto& t = tilat_[osoite / lohko_];
        const Tila ennen = t[y];
        if (ennen == Tila::M) return "";
        if (ennen == Tila::E) { t[y] = Tila::M; return ""; }  // hiljaa
        for (int i = 0; i < YTIMET; ++i) {
            if (i == y || t[i] == Tila::I) continue;
            if (t[i] == Tila::M) ++l_.takaisin;
            t[i] = Tila::I;
            ++l_.mitatoinnit;
        }
        t[y] = Tila::M;
        ++l_.vayla;
        return ennen == Tila::S ? "BusUpgr" : "BusRdX";
    }

    std::string tilat(unsigned osoite) {
        std::string s;
        for (Tila x : tilat_[osoite / lohko_])
            s += "ISEM"[static_cast<int>(x)];
        return s;
    }
    const Laskurit& laskurit() const { return l_; }

private:
    bool mesi_;
    unsigned lohko_;
    std::map<unsigned, std::array<Tila, YTIMET>> tilat_;
    Laskurit l_;
};
// @loppu protokolla

int main() {
    // @alku jono
    Koherenssi<3> k(true);
    struct Op { int ydin; char laji; };
    std::println("op      väylä    ytimet 0 1 2");
    for (const Op op : {Op{0, 'R'}, {1, 'R'}, {1, 'W'}, {2, 'R'},
                        {0, 'W'}, {0, 'R'}, {2, 'W'}}) {
        const std::string v = op.laji == 'R' ? k.lue(op.ydin, 0x40)
                                             : k.kirjoita(op.ydin, 0x40);
        const std::string t = k.tilat(0x40);
        std::println("Y{} {}    {:<8}        {} {} {}", op.ydin, op.laji,
                     v.empty() ? "osuma" : v, t[0], t[1], t[2]);
    }
    // @loppu jono
    // @alku msi
    // Yksityinen laskuri: ydin lukee ja kirjoittaa omaa dataansa.
    for (const bool mesi : {false, true}) {
        Koherenssi<2> c(mesi);
        for (unsigned i = 0; i < 100; ++i) {
            c.lue(0, 64 * i);       // 100 eri lohkoa
            c.kirjoita(0, 64 * i);
        }
        std::println("{}: {} väylätapahtumaa", mesi ? "MESI" : "MSI ",
                     c.laskurit().vayla);
    }
    // @loppu msi
    // @alku vaara
    // Kaksi säiettä kasvattaa kumpikin omaa laskuriaan 1000 kertaa.
    for (const unsigned vali : {4u, 64u}) {
        Koherenssi<2> c(true);
        for (int i = 0; i < 1000; ++i)
            for (int y = 0; y < 2; ++y) {
                c.lue(y, y * vali);
                c.kirjoita(y, y * vali);
            }
        const Laskurit& l = c.laskurit();
        std::println("väli {:2} B: väylä {:4}, mitätöinnit {:4}, "
                     "takaisinkirjoitukset {:4}", vali, l.vayla,
                     l.mitatoinnit, l.takaisin);
    }
    // @loppu vaara
}
