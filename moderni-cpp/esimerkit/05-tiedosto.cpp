#include <chrono>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <print>
#include <string>

int main()
{
    // @alku kirjoitus
    const std::filesystem::path polku = "mittaukset.txt";
    {
        std::ofstream ulos{polku};
        if (!ulos) {
            std::println(stderr, "ei voitu avata: {}", polku.string());
            return 1;
        }
        ulos << "21.5\n19.0\n23.5\n";
    }   // ulos tuhoutuu: tiedosto tyhjennetään levylle ja suljetaan
    // @loppu kirjoitus

    // @alku luku
    std::ifstream sisaan{polku};
    if (!sisaan) {
        std::println(stderr, "ei voitu avata: {}", polku.string());
        return 1;
    }
    std::string rivi;
    int rivinro = 0;
    while (std::getline(sisaan, rivi)) {
        ++rivinro;
        std::println("{}: {}", rivinro, rivi);
    }
    // @loppu luku

    // @alku polku
    std::println("pääte {}, koko {} tavua", polku.extension().string(),
                 std::filesystem::file_size(polku));
    std::println("puuttuu.txt on olemassa: {}",
                 std::filesystem::exists("puuttuu.txt"));

    using namespace std::chrono_literals;
    auto kesto = 2min + 30s;   // tyyppi std::chrono::seconds
    std::println("{}", kesto);
    // @loppu polku
}
