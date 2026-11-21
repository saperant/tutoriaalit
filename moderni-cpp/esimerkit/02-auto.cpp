#include <print>
#include <string>
#include <vector>

int main()
{
    // @alku paattely
    auto luku = 42;                  // int
    auto pii = 3.14159;              // double
    auto nimi = std::string{"Ada"};  // std::string
    auto sana = "C++";               // const char*, ei std::string
    // @loppu paattely
    std::println("{} {} {} {}", luku, pii, nimi, sana);

    // @alku viittaus
    std::vector<int> luvut{1, 2, 3};

    for (auto x : luvut) {    // x on kopio alkiosta
        x *= 10;              // muuttaa vain kopiota
        std::print("{} ", x);
    }
    std::println("| alkiot: {} {} {}", luvut[0], luvut[1], luvut[2]);

    for (auto& x : luvut) {   // x on viittaus alkioon
        x *= 10;
    }
    std::println("alkiot: {} {} {}", luvut[0], luvut[1], luvut[2]);

    // const auto& välttää kopion, mutta estää muuttamisen.
    std::vector<std::string> nimet{"Ada", "Bjarne", "Grace"};
    for (const auto& n : nimet) {
        std::print("{} ", n.size());
    }
    std::println("");
    // @loppu viittaus
}
