#include <memory>
#include <print>
#include <string>
#include <utility>
#include <vector>

// @alku solmut
struct Lapsi;

struct Vanhempi {
    std::string nimi;
    std::vector<std::shared_ptr<Lapsi>> lapset;
    ~Vanhempi() { std::println("tuhotaan vanhempi {}", nimi); }
};

struct Lapsi {
    std::string nimi;
    std::weak_ptr<Vanhempi> vanhempi;   // ei omista
    ~Lapsi() { std::println("tuhotaan lapsi {}", nimi); }
};
// @loppu solmut

int main()
{
    // @alku laskuri
    auto a = std::make_shared<std::string>("jaettu");
    std::println("omistajia: {}", a.use_count());
    {
        auto b = a;
        std::println("omistajia: {}", a.use_count());
    }
    std::println("omistajia: {}", a.use_count());
    // @loppu laskuri

    // @alku kaytto
    {
        auto v = std::make_shared<Vanhempi>("Liisa");
        auto l = std::make_shared<Lapsi>("Eero");
        l->vanhempi = v;
        v->lapset.push_back(l);

        if (auto p = l->vanhempi.lock()) {
            std::println("lapsen {} vanhempi on {}", l->nimi, p->nimi);
        }
    }
    std::println("lohko päättyi");
    // @loppu kaytto
}
