// Ensimmäinen ohjelma: OpenGL-konteksti ilman ikkunaa, oma
// kehyspuskuri, tyhjennys väriin ja tuloksen luku takaisin CPU:lle.
#include <cstring>
#include <print>

#include "gl.hpp"

int main() {
    // @alku paa
    GlKonteksti gl;
    GLint paa = 0, ali = 0;
    glGetIntegerv(GL_MAJOR_VERSION, &paa);
    glGetIntegerv(GL_MINOR_VERSION, &ali);
    const auto* renderoija =
        reinterpret_cast<const char*>(glGetString(GL_RENDERER));
    std::println("OpenGL {}.{}, ohjelmistorenderöijä: {}", paa, ali,
                 std::strstr(renderoija, "llvmpipe") ? "kyllä" : "ei");

    Kehys kehys(64, 48);
    glClearColor(0.2f, 0.4f, 0.8f, 1.0f);  // RGBA väliltä 0–1
    glClear(GL_COLOR_BUFFER_BIT);
    const Kuva kuva = kehys.lue();
    GlKonteksti::tarkista();
    std::println("kuva {}×{}, pikseli (0, 0) = {}", kuva.leveys,
                 kuva.korkeus, kuva.vari(0, 0));
    // @loppu paa
}
