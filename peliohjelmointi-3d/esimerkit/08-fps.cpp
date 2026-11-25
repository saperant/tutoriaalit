// Ensimmäisen persoonan kamera: kääntö ja nyökkäys kulmina, liike
// vaakatasossa ja näkymämatriisi. Lopuksi virhe, jossa kiertoja
// kerrytetään kameran omien akselien ympäri.
#include "yhteinen/kvaternio.hpp"
#include "yhteinen/tulostus.hpp"

#include <algorithm>
#include <print>

// @alku fps
struct FpsKamera {
    Vec3 paikka{0, 1.7, 0};  // silmien korkeus
    double kaanto = 0, nyokkays = 0;  // radiaaneina; kallistusta ei ole

    // Hiiren liike pikseleinä. Nyökkäys rajataan, ettei kamera
    // käänny ylösalaisin eikä osu lukkiutumiskohtaan.
    void katso(double dx, double dy, double herkkyys) {
        kaanto -= dx * herkkyys;
        nyokkays = std::clamp(nyokkays - dy * herkkyys, -rad(89), rad(89));
    }
    Kvat asento() const { return eulerista(kaanto, nyokkays, 0); }
    Vec3 eteen() const { return kierra(asento(), {0, 0, -1}); }
    // Kävely: suunta riippuu vain käännöstä, ja vinoon liikutaan yhtä
    // nopeasti kuin suoraan.
    void liiku(double eteen, double sivulle, double nopeus, double dt) {
        Kvat k = akselikulma({0, 1, 0}, kaanto);
        Vec3 suunta = eteen * kierra(k, {0, 0, -1}) +
                      sivulle * kierra(k, {1, 0, 0});
        if (pituus(suunta) > 1) suunta = normalisoi(suunta);
        paikka = paikka + (nopeus * dt) * suunta;
    }
    // Näkymämatriisi on kameran maailmamuunnoksen käänteismuunnos.
    Mat4 nakyma() const {
        return matriisiksi(liitto(asento())) * siirto(-paikka);
    }
};
// @loppu fps

int main() {
    const double herkkyys = rad(0.1);  // 0,1 astetta pikseliä kohden
    const double dt = 1.0 / 60;

    // @alku kavely
    FpsKamera k;
    for (int i = 0; i < 60; ++i) k.liiku(1, 0, 4, dt);  // sekunti eteen
    std::println("sekunti eteen:      paikka {}", teksti(k.paikka));
    k.katso(-900, 0, herkkyys);  // 90 astetta vasemmalle
    for (int i = 0; i < 60; ++i) k.liiku(1, 1, 4, dt);  // vinoon
    std::println("käännös ja vinoon:  paikka {}", teksti(k.paikka));
    k.katso(0, 600, herkkyys);  // katse 60 astetta alas
    for (int i = 0; i < 60; ++i) k.liiku(1, 0, 4, dt);
    std::println("katse alas, eteen:  paikka {}  katse {}",
                 teksti(k.paikka), teksti(k.eteen()));
    k.katso(0, 5000, herkkyys);  // raju veto alas
    std::println("nyökkäys rajattu:   {} astetta", luku(aste(k.nyokkays), 1));
    // @loppu kavely

    // @alku nakyma
    Mat4 a = k.nakyma();
    Mat4 b = katse(k.paikka, k.paikka + k.eteen(), {0, 1, 0});
    double ero = 0;
    for (int i = 0; i < 4; ++i)
        for (int j = 0; j < 4; ++j)
            ero = std::max(ero, std::abs(a.m[i][j] - b.m[i][j]));
    std::println("näkymämatriisi kahdella tavalla, suurin ero {}",
                 luku(ero, 6));
    // @loppu nakyma

    // @alku kertyma
    // Hiiri kiertää kymmenen ympyrää. Oikea kamera tallentaa kulmat;
    // virheellinen kertoo asentoa pienillä kierroilla omien akseliensa
    // ympäri, jolloin horisontti alkaa kallistua.
    FpsKamera kulmat;
    Kvat kertyva;
    for (int i = 0; i < 600; ++i) {
        double dx = 40 * std::cos(2 * PII * i / 60);
        double dy = 40 * std::sin(2 * PII * i / 60);
        kulmat.katso(dx, dy, herkkyys);
        kertyva = normalisoi(kertyva *
                             akselikulma({0, 1, 0}, -dx * herkkyys) *
                             akselikulma({1, 0, 0}, -dy * herkkyys));
    }
    auto kallistus = [](Kvat q) {  // oikean käden suunnan kulma vaakatasoon
        return aste(std::asin(kierra(q, {1, 0, 0}).y));
    };
    std::println("horisontin kallistus: kulmina {} astetta, "
                 "kertyvänä kiertona {} astetta",
                 luku(kallistus(kulmat.asento()), 1),
                 luku(kallistus(kertyva), 1));
    // @loppu kertyma
}
