#include <print>
#include <stdexcept>
#include <string>
#include <vector>

// @alku tyyppi
class TilinVirhe : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;   // peritään muodostimet
};

class Tili {
public:
    void nosta(int summa)
    {
        if (summa <= 0) {
            throw std::invalid_argument{"summan on oltava positiivinen"};
        }
        if (summa > saldo_) {
            throw TilinVirhe{"kate ei riitä: saldo " +
                             std::to_string(saldo_)};
        }
        saldo_ -= summa;
    }

    int saldo() const noexcept { return saldo_; }

private:
    int saldo_ = 100;
};
// @loppu tyyppi

int main()
{
    // @alku kaytto
    Tili tili;
    for (int summa : {30, -5, 500, 70}) {
        try {
            tili.nosta(summa);
            std::println("nostettu {}, saldo {}", summa, tili.saldo());
        } catch (const TilinVirhe& e) {
            std::println("tilin virhe: {}", e.what());
        } catch (const std::exception& e) {
            std::println("muu virhe: {}", e.what());
        }
    }
    // @loppu kaytto

    // @alku vahva
    std::vector<int> v{1, 2, 3};
    try {
        v.at(10) = 5;   // at() tarkistaa rajat
    } catch (const std::out_of_range&) {
        std::println("indeksi rajojen ulkopuolella, koko {}", v.size());
    }
    // @loppu vahva
}
