// Oma pääohjelma Verilatorin mallille: sama kuin --binary-valitsimen
// tuottama, mutta lopuksi kattavuustiedot kirjoitetaan tiedostoon,
// jonka nimi annetaan argumenttina +kattavuus=polku.
#include <memory>
#include <string>

#include "verilated.h"
#include "verilated_cov.h"
#include "Vtestipenkki.h"

int main(int argc, char** argv) {
    const auto konteksti = std::make_unique<VerilatedContext>();
    konteksti->commandArgs(argc, argv);
    const auto malli = std::make_unique<Vtestipenkki>(konteksti.get());

    while (!konteksti->gotFinish()) {
        malli->eval();
        if (!malli->eventsPending()) break;
        konteksti->time(malli->nextTimeSlot());
    }
    malli->final();

    // commandArgsPlusMatch palauttaa koko argumentin, esim. "+kattavuus=x".
    const std::string arg = konteksti->commandArgsPlusMatch("kattavuus=");
    const std::string polku =
        arg.empty() ? "kattavuus.dat" : arg.substr(arg.find('=') + 1);
    konteksti->coveragep()->write(polku.c_str());
    return 0;
}
