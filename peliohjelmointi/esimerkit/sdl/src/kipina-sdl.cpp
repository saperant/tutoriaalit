// Kipinän SDL2-etupää: ikkuna, näppäimistö ja kiinteän aika-askeleen
// pelisilmukka oikealla kellolla. Pelilogiikka ja piirto ovat samat
// kuin ikkunattomassa versiossa (../../11-kipina).
//
//   kipina-sdl            pelaa ikkunassa (nuolinäppäimet, Esc lopettaa)
//   kipina-sdl --testi    ajaa ilman näyttöä ja tarkistaa piirron
#include "../../11-kipina/peli.hpp"
#include "../../11-kipina/piirto.hpp"

#include <SDL.h>

#include <cstdint>
#include <cstdlib>
#include <print>
#include <string_view>

namespace {

// @alku syote
// Näppäimet kuvataan toiminnoiksi tapahtumista; pelilogiikka näkee
// vain Syote-rakenteen.
void kasittele(const SDL_Event& e, Syote& s, bool& kaynnissa) {
    if (e.type == SDL_QUIT) {
        kaynnissa = false;
        return;
    }
    if (e.type != SDL_KEYDOWN && e.type != SDL_KEYUP) {
        return;
    }
    const bool alas = e.type == SDL_KEYDOWN;
    switch (e.key.keysym.scancode) {
    case SDL_SCANCODE_LEFT: case SDL_SCANCODE_A: s.vasen = alas; break;
    case SDL_SCANCODE_RIGHT: case SDL_SCANCODE_D: s.oikea = alas; break;
    case SDL_SCANCODE_UP: case SDL_SCANCODE_W: s.ylos = alas; break;
    case SDL_SCANCODE_DOWN: case SDL_SCANCODE_S: s.alas = alas; break;
    case SDL_SCANCODE_ESCAPE: kaynnissa = false; break;
    default: break;
    }
}
// @loppu syote

void nappain(SDL_Scancode koodi, bool alas) {
    SDL_Event e{};
    e.type = alas ? SDL_KEYDOWN : SDL_KEYUP;
    e.key.keysym.scancode = koodi;
    SDL_PushEvent(&e);
}

// Ikkunaton testi: piirretään SDL:n ohjelmistorenderöijällä muistissa
// olevaan pintaan ja verrataan pikseleitä omaan kuvapuskuriin.
int testi() {
    SDL_Surface* pinta = SDL_CreateRGBSurfaceWithFormat(
        0, Kuvapuskuri::W, Kuvapuskuri::H, 32, SDL_PIXELFORMAT_XRGB8888);
    SDL_Renderer* r = SDL_CreateSoftwareRenderer(pinta);
    SDL_Texture* tekstuuri = SDL_CreateTexture(
        r, SDL_PIXELFORMAT_XRGB8888, SDL_TEXTUREACCESS_STREAMING,
        Kuvapuskuri::W, Kuvapuskuri::H);
    if (!pinta || !r || !tekstuuri) {
        std::println("SDL-virhe: {}", SDL_GetError());
        return 1;
    }
    Peli peli(2026);
    Kuvapuskuri kuva;
    Syote syote;
    bool kaynnissa = true;
    for (int ruutu = 0; ruutu < 120; ++ruutu) {
        // Simuloitu pelaaja: oikealle 60 ruutua, sitten alas.
        if (ruutu == 0) {
            nappain(SDL_SCANCODE_RIGHT, true);
        }
        if (ruutu == 60) {
            nappain(SDL_SCANCODE_RIGHT, false);
            nappain(SDL_SCANCODE_DOWN, true);
        }
        SDL_Event e;
        while (SDL_PollEvent(&e)) {
            kasittele(e, syote, kaynnissa);
        }
        peli.paivita(syote);
        // @alku esitys
        piirra(peli, kuva);
        SDL_UpdateTexture(tekstuuri, nullptr, kuva.pikselit.data(),
                          Kuvapuskuri::W * 4);
        SDL_RenderClear(r);
        SDL_RenderCopy(r, tekstuuri, nullptr, nullptr);
        SDL_RenderPresent(r);
        // @loppu esitys
    }
    bool sama = true;
    for (int y = 0; y < Kuvapuskuri::H; ++y) {
        const auto* rivi = reinterpret_cast<const std::uint32_t*>(
            static_cast<const std::uint8_t*>(pinta->pixels) +
            y * pinta->pitch);
        for (int x = 0; x < Kuvapuskuri::W; ++x) {
            const std::uint32_t odotettu = kuva.pikselit[
                static_cast<std::size_t>(y * Kuvapuskuri::W + x)];
            sama = sama && (rivi[x] & 0xffffffu) == odotettu;
        }
    }
    std::println("ruutuja {}, pisteet {}, elämiä {}", peli.ruutu,
                 peli.pisteet, peli.elamat);
    std::println("SDL:n pinta vastaa kuvapuskuria: {}",
                 sama ? "kyllä" : "ei");
    SDL_DestroyTexture(tekstuuri);
    SDL_DestroyRenderer(r);
    SDL_FreeSurface(pinta);
    return sama ? 0 : 1;
}

// @alku ikkuna
int pelaa() {
    SDL_Window* ikkuna = SDL_CreateWindow(
        "Kipinä", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
        Kuvapuskuri::W * 4, Kuvapuskuri::H * 4, SDL_WINDOW_RESIZABLE);
    SDL_Renderer* r = SDL_CreateRenderer(
        ikkuna, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC);
    if (!ikkuna || !r) {
        std::println("SDL-virhe: {}", SDL_GetError());
        return 1;
    }
    // Looginen koko: SDL skaalaa 160x120-kuvan ikkunaan.
    SDL_RenderSetLogicalSize(r, Kuvapuskuri::W, Kuvapuskuri::H);
    SDL_Texture* tekstuuri = SDL_CreateTexture(
        r, SDL_PIXELFORMAT_XRGB8888, SDL_TEXTUREACCESS_STREAMING,
        Kuvapuskuri::W, Kuvapuskuri::H);

    Peli peli(static_cast<std::uint64_t>(SDL_GetPerformanceCounter()));
    Kuvapuskuri kuva;
    Syote syote;
    bool kaynnissa = true;
    const std::uint64_t taajuus = SDL_GetPerformanceFrequency();
    const auto askel = static_cast<std::uint64_t>(taajuus * DT);
    std::uint64_t edellinen = SDL_GetPerformanceCounter();
    std::uint64_t kertyma = 0;
    while (kaynnissa) {
        SDL_Event e;
        while (SDL_PollEvent(&e)) {
            kasittele(e, syote, kaynnissa);
        }
        const std::uint64_t nyt = SDL_GetPerformanceCounter();
        kertyma += std::min(nyt - edellinen, taajuus / 4);
        edellinen = nyt;
        while (kertyma >= askel) {
            peli.paivita(syote);
            kertyma -= askel;
        }
        piirra(peli, kuva);
        SDL_UpdateTexture(tekstuuri, nullptr, kuva.pikselit.data(),
                          Kuvapuskuri::W * 4);
        SDL_RenderClear(r);
        SDL_RenderCopy(r, tekstuuri, nullptr, nullptr);
        SDL_RenderPresent(r);  // odottaa pystytahdistusta
    }
    SDL_DestroyTexture(tekstuuri);
    SDL_DestroyRenderer(r);
    SDL_DestroyWindow(ikkuna);
    return 0;
}
// @loppu ikkuna

}  // namespace

int main(int argc, char** argv) {
    const bool on_testi = argc > 1 && std::string_view(argv[1]) == "--testi";
    if (on_testi) {
        SDL_setenv("SDL_VIDEODRIVER", "dummy", 1);  // ei näyttöä
    }
    if (SDL_Init(SDL_INIT_VIDEO | SDL_INIT_EVENTS) != 0) {
        std::println("SDL_Init: {}", SDL_GetError());
        return 1;
    }
    const int tulos = on_testi ? testi() : pelaa();
    SDL_Quit();
    return tulos;
}
