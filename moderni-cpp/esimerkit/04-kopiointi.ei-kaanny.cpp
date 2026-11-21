#include <print>
#include <string>
#include <utility>

class Yhteys {
public:
    explicit Yhteys(std::string osoite) : osoite_{std::move(osoite)} {}
    Yhteys(const Yhteys&) = delete;             // ei kopiointia
    Yhteys& operator=(const Yhteys&) = delete;  // ei sijoitusta

    const std::string& osoite() const { return osoite_; }

private:
    std::string osoite_;
};

int main()
{
    Yhteys a{"palvelin:8080"};
#ifndef KORJATTU
    Yhteys b = a;   // virhe: kopiomuodostin on poistettu
    std::println("{}", b.osoite());
#endif
    std::println("Yhteys: {}", a.osoite());
}
