// Indeksoitu piirto: nelikulmio neljällä kärjellä ja kuudella
// indeksillä. Kuva on sama kuin kuudella kärjellä ilman indeksejä,
// mutta verteksivarjostin ajetaan vain neljästi.
#include <array>
#include <cstdint>
#include <print>

#include "gl.hpp"

#ifndef GL_VERTEX_SHADER_INVOCATIONS
#define GL_VERTEX_SHADER_INVOCATIONS 0x82F0  // ARB_pipeline_statistics
#endif

constexpr const char* verteksivarjostin = R"(#version 450 core
layout(location = 0) in vec2 sijainti;
layout(location = 1) in vec3 vari;
out vec3 v_vari;
void main() {
    v_vari = vari;
    gl_Position = vec4(sijainti, 0.0, 1.0);
}
)";

constexpr const char* fragmenttivarjostin = R"(#version 450 core
in vec3 v_vari;
layout(location = 0) out vec4 tulos;
void main() {
    tulos = vec4(v_vari, 1.0);
}
)";

struct Verteksi {
    float x, y;
    float r, g, b;
};

// @alku data
// Neljä kärkeä. Kolmiot (0, 1, 2) ja (0, 2, 3) jakavat lävistäjän
// kärjet 0 ja 2, jotka tallennetaan vain kerran.
constexpr std::array<Verteksi, 4> karjet{{
    {-0.75f, -0.5f, 1.0f, 0.0f, 0.0f},  // 0: vasen ala
    {0.75f, -0.5f, 0.0f, 1.0f, 0.0f},   // 1: oikea ala
    {0.75f, 0.5f, 0.0f, 0.0f, 1.0f},    // 2: oikea ylä
    {-0.75f, 0.5f, 1.0f, 1.0f, 0.0f},   // 3: vasen ylä
}};
constexpr std::array<std::uint16_t, 6> indeksit{0, 1, 2, 0, 2, 3};
// @loppu data

// Verteksitaulukko kuten luvun kolmiossa: sijainti ja väri samasta
// puskurista.
static GLuint luo_vao(GLuint vbo) {
    GLuint vao = 0;
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
    return vao;
}

int main() {
    GlKonteksti gl;
    const GLuint ohjelma =
        luo_ohjelma(verteksivarjostin, fragmenttivarjostin);
    glUseProgram(ohjelma);
    glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
    GLuint kysely = 0;
    glGenQueries(1, &kysely);
    GLuint64 ajot_indeksoitu = 0, ajot_purettu = 0;

    // @alku indeksoitu
    GLuint vbo = 0, ibo = 0;
    glCreateBuffers(1, &vbo);
    glNamedBufferStorage(vbo, sizeof karjet, karjet.data(), 0);
    glCreateBuffers(1, &ibo);
    glNamedBufferStorage(ibo, sizeof indeksit, indeksit.data(), 0);
    const GLuint vao = luo_vao(vbo);
    glVertexArrayElementBuffer(vao, ibo);  // indeksipuskuri kuuluu VAO:hon

    Kehys kehys(96, 64);
    glClear(GL_COLOR_BUFFER_BIT);
    glBindVertexArray(vao);
    glBeginQuery(GL_VERTEX_SHADER_INVOCATIONS, kysely);
    glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_SHORT, nullptr);
    glEndQuery(GL_VERTEX_SHADER_INVOCATIONS);
    glGetQueryObjectui64v(kysely, GL_QUERY_RESULT, &ajot_indeksoitu);
    const Kuva indeksoitu = kehys.lue();
    // @loppu indeksoitu

    // @alku purettu
    // Sama ilman indeksejä: jokainen kolmio saa omat kolme kärkeään.
    std::array<Verteksi, 6> puretut{};
    for (std::size_t i = 0; i < indeksit.size(); ++i) {
        puretut[i] = karjet[indeksit[i]];
    }
    GLuint vbo2 = 0;
    glCreateBuffers(1, &vbo2);
    glNamedBufferStorage(vbo2, sizeof puretut, puretut.data(), 0);
    const GLuint vao2 = luo_vao(vbo2);

    Kehys kehys2(96, 64);
    glClear(GL_COLOR_BUFFER_BIT);
    glBindVertexArray(vao2);
    glBeginQuery(GL_VERTEX_SHADER_INVOCATIONS, kysely);
    glDrawArrays(GL_TRIANGLES, 0, 6);
    glEndQuery(GL_VERTEX_SHADER_INVOCATIONS);
    glGetQueryObjectui64v(kysely, GL_QUERY_RESULT, &ajot_purettu);
    const Kuva purettu = kehys2.lue();
    // @loppu purettu

    GlKonteksti::tarkista();
    indeksoitu.tallenna_ppm("bin/03-indeksit.ppm");
    // @alku raportti
    std::println("indeksoitu: {} kärkeä + {} indeksiä = {} tavua, "
                 "verteksivarjostin {} kertaa",
                 karjet.size(), indeksit.size(),
                 sizeof karjet + sizeof indeksit, ajot_indeksoitu);
    std::println("purettu:    {} kärkeä = {} tavua, "
                 "verteksivarjostin {} kertaa",
                 puretut.size(), sizeof puretut, ajot_purettu);
    std::println("peitetyt pikselit: {} / {}",
                 indeksoitu.peitetyt({0, 0, 0}),
                 indeksoitu.leveys * indeksoitu.korkeus);
    std::println("kuvat samat: {}",
                 indeksoitu.rgba == purettu.rgba ? "kyllä" : "ei");
    // @loppu raportti

    glDeleteQueries(1, &kysely);
    glDeleteProgram(ohjelma);
    glDeleteVertexArrays(1, &vao);
    glDeleteVertexArrays(1, &vao2);
    glDeleteBuffers(1, &vbo);
    glDeleteBuffers(1, &ibo);
    glDeleteBuffers(1, &vbo2);
}
