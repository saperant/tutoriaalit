// Äänen miksaus: äänet summataan liukulukuina, ja vasta lopuksi tulos
// rajoitetaan ja muunnetaan 16-bittisiksi näytteiksi. Ylivuotava
// kokonaislukusumma napsahtaisi kuuluvasti.
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <numbers>
#include <print>
#include <vector>

constexpr int TAAJUUS = 48'000;  // näytettä sekunnissa

// @alku aani
struct Aani {
    double taajuus;    // Hz
    double voimakkuus; // 0..1
    double alku, kesto;
    double vaihe = 0.0;

    // Seuraava näyte; vaihe pidetään välillä [0, 1), jotta tarkkuus
    // ei heikkene pitkässä äänessä.
    double nayte(double aika) {
        if (aika < alku || aika >= alku + kesto) {
            return 0.0;
        }
        vaihe += taajuus / TAAJUUS;
        vaihe -= std::floor(vaihe);
        const double verho = std::min(1.0, (alku + kesto - aika) * 50.0);
        return voimakkuus * verho *
               std::sin(2.0 * std::numbers::pi * vaihe);
    }
};
// @loppu aani

// @alku miksaus
std::vector<std::int16_t> miksaa(std::vector<Aani>& aanet, double kesto,
                                 int& leikattuja) {
    std::vector<std::int16_t> puskuri;
    leikattuja = 0;
    for (int i = 0; i < static_cast<int>(kesto * TAAJUUS); ++i) {
        const double aika = static_cast<double>(i) / TAAJUUS;
        double summa = 0.0;
        for (Aani& a : aanet) {
            summa += a.nayte(aika);
        }
        if (std::abs(summa) > 1.0) {
            ++leikattuja;  // pääkanava ylikuormittuu
        }
        summa = std::clamp(summa, -1.0, 1.0);
        puskuri.push_back(static_cast<std::int16_t>(summa * 32767.0));
    }
    return puskuri;
}
// @loppu miksaus

void tallenna_wav(const char* nimi, const std::vector<std::int16_t>& n) {
    std::ofstream f(nimi, std::ios::binary);
    auto kirjoita = [&](std::uint32_t arvo, int tavuja) {
        for (int i = 0; i < tavuja; ++i) {
            f.put(static_cast<char>((arvo >> (8 * i)) & 0xff));
        }
    };
    const auto data = static_cast<std::uint32_t>(n.size() * 2);
    f << "RIFF";
    kirjoita(36 + data, 4);
    f << "WAVEfmt ";
    kirjoita(16, 4);
    kirjoita(1, 2);  // PCM
    kirjoita(1, 2);  // mono
    kirjoita(TAAJUUS, 4);
    kirjoita(TAAJUUS * 2, 4);
    kirjoita(2, 2);
    kirjoita(16, 2);
    f << "data";
    kirjoita(data, 4);
    for (std::int16_t s : n) {
        kirjoita(static_cast<std::uint16_t>(s), 2);
    }
}

int main(int argc, char**) {
    for (double voimakkuus : {0.6, 0.3}) {
        std::vector<Aani> aanet = {
            {440.0, voimakkuus, 0.0, 0.5},   // laukaus
            {660.0, voimakkuus, 0.1, 0.3},   // osuma
            {220.0, voimakkuus, 0.2, 0.3},   // räjähdys
        };
        int leikattuja = 0;
        auto puskuri = miksaa(aanet, 0.6, leikattuja);
        tallenna_wav("aanet.wav", puskuri);
        if (argc > 1) {  // käyrätila kuvitusta varten: 20 ms näytteitä
            for (int i = 10'080; i < 11'040; ++i) {
                std::println("{} {} {}", voimakkuus, i,
                             puskuri[static_cast<std::size_t>(i)]);
            }
            continue;
        }
        std::println("voimakkuus {:.1f}: {} näytettä, leikattuja {}",
                     voimakkuus, puskuri.size(), leikattuja);
    }
}
