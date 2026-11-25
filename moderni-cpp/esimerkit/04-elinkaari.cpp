#include <cstdio>
#include <print>
#include <stdexcept>
#include <string>

// @alku luokka
class Lokitiedosto {
public:
    explicit Lokitiedosto(const std::string& polku)
        : tiedosto_{std::fopen(polku.c_str(), "w")}, polku_{polku}
    {
        if (tiedosto_ == nullptr) {
            throw std::runtime_error{"tiedostoa ei voitu avata: " + polku};
        }
        std::println("  avattu {}", polku_);
    }

    ~Lokitiedosto()   // hajotin: suoritetaan, kun olio tuhoutuu
    {
        std::fclose(tiedosto_);
        std::println("  suljettu {}, rivejä {}", polku_, riveja_);
    }

    // Kopio sulkisi saman tiedoston kahdesti, joten kopiointi estetään.
    Lokitiedosto(const Lokitiedosto&) = delete;
    Lokitiedosto& operator=(const Lokitiedosto&) = delete;

    void kirjoita(const std::string& rivi)
    {
        std::fputs((rivi + "\n").c_str(), tiedosto_);
        ++riveja_;
    }

private:
    std::FILE* tiedosto_;
    std::string polku_;
    int riveja_ = 0;
};
// @loppu luokka

// @alku funktio
bool kirjaa(int arvo)
{
    Lokitiedosto loki{"arvot.log"};
    if (arvo < 0) {
        return false;   // hajotin sulkee tiedoston tässäkin
    }
    loki.kirjoita(std::to_string(arvo));
    return true;
}
// @loppu funktio

int main()
{
    // @alku lohko
    std::println("lohko alkaa");
    {
        Lokitiedosto a{"a.log"};
        Lokitiedosto b{"b.log"};
        a.kirjoita("käynnistys");
        a.kirjoita("valmis");
        std::println("lohko päättyy");
    }   // b tuhotaan ensin, sitten a
    std::println("lohkon jälkeen");
    // @loppu lohko

    // @alku kutsut
    std::println("kirjaa(5):");
    kirjaa(5);
    std::println("kirjaa(-1):");
    kirjaa(-1);
    // @loppu kutsut
}
