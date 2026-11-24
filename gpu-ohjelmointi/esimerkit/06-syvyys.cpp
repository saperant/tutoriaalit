// Syvyyspuskuri ja sekoitus: piirtojärjestys ratkaisee ilman
// syvyystestiä, ja läpinäkyvien pintojen sekoitus ei ole vaihdannainen.
#include <print>

#include "gl.hpp"

// @alku glsl
constexpr const char* verteksivarjostin = R"(#version 450 core
layout(location = 0) uniform vec4 alue;   // x0, y0, x1, y1
layout(location = 1) uniform float z;     // syvyys −1 (lähin) … 1
void main() {
    const vec2 k[6] = vec2[](vec2(0, 0), vec2(1, 0), vec2(1, 1),
                             vec2(0, 0), vec2(1, 1), vec2(0, 1));
    vec2 p = mix(alue.xy, alue.zw, k[gl_VertexID]);
    gl_Position = vec4(p, z, 1.0);
}
)";

constexpr const char* fragmenttivarjostin = R"(#version 450 core
layout(location = 2) uniform vec4 vari;
layout(location = 0) out vec4 tulos;
void main() { tulos = vari; }
)";
// @loppu glsl

static GLuint ohjelma = 0;

// @alku suorakulmio
static void suorakulmio(float x0, float y0, float x1, float y1, float z,
                        float r, float g, float b, float a = 1.0f) {
    glProgramUniform4f(ohjelma, 0, x0, y0, x1, y1);
    glProgramUniform1f(ohjelma, 1, z);
    glProgramUniform4f(ohjelma, 2, r, g, b, a);
    glDrawArrays(GL_TRIANGLES, 0, 6);
}
// @loppu suorakulmio

int main() {
    GlKonteksti gl;
    Kehys kehys(96, 48);
    ohjelma = luo_ohjelma(verteksivarjostin, fragmenttivarjostin);
    GLuint vao = 0;
    glCreateVertexArrays(1, &vao);
    glUseProgram(ohjelma);
    glBindVertexArray(vao);
    glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
    glClearDepth(1.0);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

    // @alku syvyys
    // Vasen puolisko ilman syvyystestiä, oikea syvyystestin kanssa.
    // Kummassakin piirretään ensin lähempi vihreä, sitten kauempi
    // punainen, joka on osittain vihreän takana.
    for (const bool testi : {false, true}) {
        const float x = testi ? 0.0f : -1.0f;
        if (testi) {
            glEnable(GL_DEPTH_TEST);
            glDepthFunc(GL_LESS);  // pienempi syvyys voittaa
        }
        suorakulmio(x + 0.1f, -0.2f, x + 0.6f, 0.6f, -0.5f,
                    0.0f, 1.0f, 0.0f);  // lähellä
        suorakulmio(x + 0.4f, -0.6f, x + 0.9f, 0.2f, 0.5f,
                    1.0f, 0.0f, 0.0f);  // kaukana
    }
    glDisable(GL_DEPTH_TEST);
    // @loppu syvyys

    const Kuva syvyys = kehys.lue();
    std::println("päällekkäinen alue ilman testiä: {}",
                 syvyys.vari(24, 24));
    std::println("päällekkäinen alue testin kanssa: {}",
                 syvyys.vari(72, 24));

    // @alku sekoitus
    // Läpinäkyvä sininen ja keltainen (alfa 0,5) eri järjestyksissä
    // mustan päälle: tulos = alfa · lähde + (1 − alfa) · kohde.
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    suorakulmio(-1.0f, -1.0f, -0.6f, -0.7f, 0, 0, 0, 1, 0.5f);
    suorakulmio(-1.0f, -1.0f, -0.6f, -0.7f, 0, 1, 1, 0, 0.5f);
    suorakulmio(0.6f, -1.0f, 1.0f, -0.7f, 0, 1, 1, 0, 0.5f);
    suorakulmio(0.6f, -1.0f, 1.0f, -0.7f, 0, 0, 0, 1, 0.5f);
    glDisable(GL_BLEND);
    // @loppu sekoitus

    const Kuva kuva = kehys.lue();
    GlKonteksti::tarkista();
    kuva.tallenna_ppm("bin/06-syvyys.ppm");
    std::println("sininen, sitten keltainen: {}", kuva.vari(4, 46));
    std::println("keltainen, sitten sininen: {}", kuva.vari(92, 46));

    glDeleteVertexArrays(1, &vao);
    glDeleteProgram(ohjelma);
}
