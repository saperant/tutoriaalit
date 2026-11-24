// Piirtokutsujen määrä: 100 pientä neliötä sadalla piirtokutsulla ja
// tilamuutoksella tai yhdellä instanssipiirrolla, jossa sijainnit
// luetaan varastopuskurista (SSBO). Kuvien on oltava samat.
#include <array>
#include <print>
#include <vector>

#include "gl.hpp"

// @alku glsl
constexpr const char* verteksivarjostin = R"(#version 450 core
layout(std430, binding = 0) readonly buffer Sijainnit {
    vec2 sijainnit[];          // yksi alkio instanssia kohden
};
layout(location = 0) uniform int yksittainen;   // −1: instanssipiirto
void main() {
    const vec2 k[6] = vec2[](vec2(0, 0), vec2(1, 0), vec2(1, 1),
                             vec2(0, 0), vec2(1, 1), vec2(0, 1));
    int i = yksittainen >= 0 ? yksittainen : gl_InstanceID;
    vec2 p = sijainnit[i] + k[gl_VertexID] * 0.12;
    gl_Position = vec4(p, 0.0, 1.0);
}
)";
// @loppu glsl

constexpr const char* fragmenttivarjostin = R"(#version 450 core
layout(location = 0) out vec4 tulos;
void main() { tulos = vec4(0.9, 0.9, 0.3, 1.0); }
)";

int main() {
    GlKonteksti gl;
    Kehys kehys(128, 128);
    const GLuint ohjelma =
        luo_ohjelma(verteksivarjostin, fragmenttivarjostin);
    std::vector<std::array<float, 2>> sijainnit;
    for (int y = 0; y < 10; ++y) {
        for (int x = 0; x < 10; ++x) {
            sijainnit.push_back({-0.95f + 0.19f * static_cast<float>(x),
                                 -0.95f + 0.19f * static_cast<float>(y)});
        }
    }
    GLuint ssbo = 0, vao = 0;
    glCreateBuffers(1, &ssbo);
    glNamedBufferStorage(ssbo,
                         static_cast<GLsizeiptr>(sijainnit.size() * 8),
                         sijainnit.data(), 0);
    glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, ssbo);
    glCreateVertexArrays(1, &vao);
    glUseProgram(ohjelma);
    glBindVertexArray(vao);

    // @alku vertailu
    // Tapa 1: yksi piirtokutsu ja uniform-päivitys neliötä kohden.
    glClear(GL_COLOR_BUFFER_BIT);
    int kutsuja = 0;
    for (GLint i = 0; i < 100; ++i) {
        glProgramUniform1i(ohjelma, 0, i);
        glDrawArrays(GL_TRIANGLES, 0, 6);
        ++kutsuja;
    }
    const Kuva erikseen = kehys.lue();
    std::println("erikseen:      {} piirtokutsua", kutsuja);

    // Tapa 2: yksi instanssipiirto, sijainnit puskurista.
    glClear(GL_COLOR_BUFFER_BIT);
    glProgramUniform1i(ohjelma, 0, -1);
    glDrawArraysInstanced(GL_TRIANGLES, 0, 6, 100);
    const Kuva instanssit = kehys.lue();
    std::println("instansseina:  1 piirtokutsu");
    std::println("kuvat samat:   {}",
                 erikseen.rgba == instanssit.rgba ? "kyllä" : "ei");
    // @loppu vertailu
    std::println("peitetyt pikselit: {}", instanssit.peitetyt({0, 0, 0}));
    GlKonteksti::tarkista();
    glDeleteVertexArrays(1, &vao);
    glDeleteBuffers(1, &ssbo);
    glDeleteProgram(ohjelma);
}
