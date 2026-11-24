// Ylipiirto: kuinka monta kertaa fragmenttivarjostin ajetaan pikseliä
// kohden. Mitataan putken tilastokyselyllä ja sapluunapuskurilla.
// Sama kohtaus piirretään takaa eteen ja edestä taakse.
#include <cstdint>
#include <map>
#include <print>
#include <vector>

#include "gl.hpp"

#ifndef GL_FRAGMENT_SHADER_INVOCATIONS
#define GL_FRAGMENT_SHADER_INVOCATIONS 0x82F4  // ARB_pipeline_statistics
#endif

// @alku glsl
constexpr const char* verteksivarjostin = R"(#version 450 core
layout(location = 0) uniform int kerroksia;
layout(location = 1) uniform bool takaa_eteen;
void main() {
    // Kerros i on neliö syvyydellä z; kerrokset limittäin.
    const vec2 k[6] = vec2[](vec2(-1, -1), vec2(1, -1), vec2(1, 1),
                             vec2(-1, -1), vec2(1, 1), vec2(-1, 1));
    int i = gl_InstanceID;
    float z = takaa_eteen ? 0.9 - 0.1 * i : 0.9 - 0.1 * (kerroksia - 1 - i);
    vec2 siirto = vec2(0.08 * i - 0.2, 0.0);
    gl_Position = vec4(k[gl_VertexID] * 0.6 + siirto, z, 1.0);
}
)";

constexpr const char* fragmenttivarjostin = R"(#version 450 core
layout(location = 0) out vec4 tulos;
void main() {
    // Raskas varjostin: ylipiirron hinta kasvaa varjostimen mukana.
    float s = 0.0;
    for (int i = 0; i < 64; ++i) { s += sin(float(i) + gl_FragCoord.x); }
    tulos = vec4(0.5 + 0.001 * s, 0.4, 0.2, 1.0);
}
)";
// @loppu glsl

int main() {
    GlKonteksti gl;
    Kehys kehys(64, 64);
    const GLuint ohjelma =
        luo_ohjelma(verteksivarjostin, fragmenttivarjostin);
    GLuint vao = 0, kysely = 0;
    glCreateVertexArrays(1, &vao);
    glGenQueries(1, &kysely);  // tyyppi määräytyy glBeginQueryssä
    glUseProgram(ohjelma);
    glBindVertexArray(vao);
    constexpr int kerroksia = 6;
    glProgramUniform1i(ohjelma, 0, kerroksia);

    // @alku mittaus
    for (const bool takaa_eteen : {true, false}) {
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT |
                GL_STENCIL_BUFFER_BIT);
        glEnable(GL_DEPTH_TEST);
        glDepthFunc(GL_LESS);
        // Sapluuna laskee, montako kertaa pikseliin kirjoitettiin.
        glEnable(GL_STENCIL_TEST);
        glStencilFunc(GL_ALWAYS, 0, 0xFF);
        glStencilOp(GL_KEEP, GL_KEEP, GL_INCR);  // syvyystesti läpi: +1
        glProgramUniform1i(ohjelma, 1, takaa_eteen);

        glBeginQuery(GL_FRAGMENT_SHADER_INVOCATIONS, kysely);
        glDrawArraysInstanced(GL_TRIANGLES, 0, 6, kerroksia);  // 1 kutsu
        glEndQuery(GL_FRAGMENT_SHADER_INVOCATIONS);
        GLuint64 ajoja = 0;
        glGetQueryObjectui64v(kysely, GL_QUERY_RESULT, &ajoja);

        std::vector<std::uint8_t> sapluuna(64 * 64);
        glReadPixels(0, 0, 64, 64, GL_STENCIL_INDEX, GL_UNSIGNED_BYTE,
                     sapluuna.data());
        std::map<int, int> jakauma;   // kirjoituksia → pikseleitä
        for (auto s : sapluuna) {
            ++jakauma[s];
        }
        std::println("{}: varjostin ajettiin {} kertaa",
                     takaa_eteen ? "takaa eteen" : "edestä taakse", ajoja);
        for (const auto& [n, pikseleita] : jakauma) {
            std::println("  {} kirjoitusta: {:4} pikseliä", n, pikseleita);
        }
    }
    // @loppu mittaus
    GlKonteksti::tarkista();
    glDeleteQueries(1, &kysely);
    glDeleteVertexArrays(1, &vao);
    glDeleteProgram(ohjelma);
}
