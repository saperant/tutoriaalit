// TSAN
// Kopioi ja vaihda: lukijat saavat muuttumattoman tilannekuvan
// std::atomic<std::shared_ptr>:n kautta; viittauslaskenta hoitaa
// vanhojen versioiden vapauttamisen.
#include <atomic>
#include <memory>
#include <print>
#include <string>
#include <thread>
#include <vector>

// @alku reititys
struct Reitit {
    int versio;
    std::vector<std::string> palvelimet;
};

class Reititin {
public:
    std::shared_ptr<const Reitit> nykyiset() const
    {
        return reitit_.load();       // lukija pitää versiota elossa
    }

    void lisaa(const std::string& palvelin)
    {
        auto vanha = reitit_.load();
        for (;;) {
            auto uusi = std::make_shared<Reitit>(*vanha);   // kopio
            ++uusi->versio;
            uusi->palvelimet.push_back(palvelin);
            // Vaihto vain, jos kukaan ei ehtinyt väliin.
            if (reitit_.compare_exchange_weak(vanha, std::move(uusi))) {
                return;
            }
        }
    }

private:
    std::atomic<std::shared_ptr<const Reitit>> reitit_{
        std::make_shared<const Reitit>(Reitit{0, {}})};
};
// @loppu reititys

int main()
{
    // @alku kaytto
    Reititin reititin;
    std::atomic<int> rikki{0};
    std::atomic<bool> valmis{false};
    {
        std::vector<std::jthread> saikeet;
        for (int l = 0; l < 2; ++l) {
            saikeet.emplace_back([&] {
                while (!valmis.load()) {
                    const auto r = reititin.nykyiset();
                    if (r->palvelimet.size() !=
                        static_cast<std::size_t>(r->versio)) {
                        ++rikki;
                    }
                }
            });
        }
        {
            std::vector<std::jthread> kirjoittajat;
            for (int k = 0; k < 2; ++k) {
                kirjoittajat.emplace_back([&reititin, k] {
                    for (int i = 0; i < 300; ++i) {
                        reititin.lisaa("p" + std::to_string(k * 1000 + i));
                    }
                });
            }
        }
        valmis = true;
    }
    const auto lopuksi = reititin.nykyiset();
    std::println("versio {}, palvelimia {}, rikkinaisia nakymia {}",
                 lopuksi->versio, lopuksi->palvelimet.size(), rikki.load());
    // @loppu kaytto
}
