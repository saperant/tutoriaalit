// Tyyppien pyyhinnän muistinvaraukset: std::function, move_only_function
// ja std::any. Pieni olio mahtuu säiliön sisään (small buffer
// optimization), suuri varataan keosta.
#include <any>
#include <array>
#include <cstdio>
#include <functional>
#include <string>

#include "laskuri.hpp"

// @alku apu
// Rakentaa olion lausekkeesta ja kertoo, montako varausta tarvittiin.
template <typename Tee>
void varaukset(const char* nimi, Tee tee)
{
    laskuri::Jakso j;
    auto olio = tee();
    std::printf("  %-34s %zu\n", nimi, j.varaukset());
}
// @loppu apu

int main()
{
    // @alku function
    std::array<double, 4> kertoimet{1, 2, 3, 4};   // 32 tavua
    double kerroin = 2;                             // 8 tavua

    std::printf("std::function<double(double)>:\n");
    varaukset("lambda ilman sieppausta", [] {
        return std::function<double(double)>{[](double x) { return x; }};
    });
    varaukset("sieppaa double (8 tavua)", [&] {
        return std::function<double(double)>{
            [kerroin](double x) { return kerroin * x; }};
    });
    varaukset("sieppaa taulukon (32 tavua)", [&] {
        return std::function<double(double)>{
            [kertoimet](double x) { return kertoimet[0] * x; }};
    });
    varaukset("sieppaa viittauksen taulukkoon", [&] {
        return std::function<double(double)>{
            [&kertoimet](double x) { return kertoimet[0] * x; }};
    });
    // @loppu function

    // @alku kopio
    std::function<double(double)> iso =
        [kertoimet](double x) { return kertoimet[3] * x; };
    varaukset("kopio isosta", [&] { return iso; });
    varaukset("siirto isosta", [&] { return std::move(iso); });
    // @loppu kopio

    // @alku muut
    std::printf("std::move_only_function<double(double)>:\n");
    varaukset("sieppaa taulukon (32 tavua)", [&] {
        return std::move_only_function<double(double)>{
            [kertoimet](double x) { return kertoimet[0] * x; }};
    });
    std::printf("std::any:\n");
    varaukset("int", [] { return std::any{42}; });
    varaukset("std::array<int, 4>", [] {
        return std::any{std::array<int, 4>{}};
    });
    varaukset("lyhyt std::string", [] {
        return std::any{std::string{"lyhyt"}};
    });
    // @loppu muut
}
