// Kolmio OpenGL:llä: verteksipuskuri, verteksitaulukko (VAO),
// varjostinohjelma ja piirtokutsu. Kärkien värit interpoloidaan.
#include <array>
#include <print>

#include "gl.hpp"

// @alku varjostimet
constexpr const char* verteksivarjostin = R"(#version 450 core
layout(location = 0) in vec2 sijainti;   // attribuutti 0
layout(location = 1) in vec3 vari;       // attribuutti 1
out vec3 v_vari;                         // interpoloidaan
void main() {
    v_vari = vari;
    gl_Position = vec4(sijainti, 0.0, 1.0);  // leikkausavaruus
}
)";

constexpr const char* fragmenttivarjostin = R"(#version 450 core
in vec3 v_vari;
layout(location = 0) out vec4 tulos;     // väriliitäntä 0
void main() {
    tulos = vec4(v_vari, 1.0);
}
)";
// @loppu varjostimet

// @alku data
struct Verteksi {
    float x, y;     // normalisoidut laitekoordinaatit −1…1
    float r, g, b;
};

constexpr std::array<Verteksi, 3> kolmio{{
    {-0.8f, -0.8f, 1.0f, 0.0f, 0.0f},  // vasen ala: punainen
    {0.8f, -0.8f, 0.0f, 1.0f, 0.0f},   // oikea ala: vihreä
    {0.0f, 0.8f, 0.0f, 0.0f, 1.0f},    // ylä: sininen
}};
// @loppu data

int main() {
    GlKonteksti gl;
    Kehys kehys(96, 96);

    // @alku puskurit
    GLuint vbo = 0, vao = 0;
    glCreateBuffers(1, &vbo);
    glNamedBufferStorage(vbo, sizeof kolmio, kolmio.data(), 0);

    glCreateVertexArrays(1, &vao);
    glVertexArrayVertexBuffer(vao, 0, vbo, 0, sizeof(Verteksi));
    glEnableVertexArrayAttrib(vao, 0);
    glVertexArrayAttribFormat(vao, 0, 2, GL_FLOAT, GL_FALSE,
                              offsetof(Verteksi, x));
    glVertexArrayAttribBinding(vao, 0, 0);
    glEnableVertexArrayAttrib(vao, 1);
    glVertexArrayAttribFormat(vao, 1, 3, GL_FLOAT, GL_FALSE,
                              offsetof(Verteksi, r));
    glVertexArrayAttribBinding(vao, 1, 0);
    // @loppu puskurit

    // @alku piirto
    const GLuint ohjelma =
        luo_ohjelma(verteksivarjostin, fragmenttivarjostin);
    glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
    glClear(GL_COLOR_BUFFER_BIT);
    glUseProgram(ohjelma);
    glBindVertexArray(vao);
    glDrawArrays(GL_TRIANGLES, 0, 3);
    // @loppu piirto

    const Kuva kuva = kehys.lue();
    GlKonteksti::tarkista();
    kuva.tallenna_ppm("bin/03-kolmio.ppm");
    // @alku raportti
    std::println("keskikohta (48, 52): {}", kuva.vari(48, 52));
    std::println("vasen ala (12, 84): {}", kuva.vari(12, 84));
    std::println("nurkka (2, 2):      {}", kuva.vari(2, 2));
    std::println("peitetyt pikselit:  {} / {}", kuva.peitetyt({0, 0, 0}),
                 kuva.leveys * kuva.korkeus);
    // @loppu raportti

    glDeleteProgram(ohjelma);
    glDeleteVertexArrays(1, &vao);
    glDeleteBuffers(1, &vbo);
}
