// Uniform-puskuri (UBO) ja std140-asettelu: C++-rakenteen on
// vastattava GLSL:n lohkoa tavulleen. Asettelu kysytään ajurilta ja
// tarkistetaan; sitten piirretään muunnettu neliö ilman verteksidataa.
#include <cmath>
#include <cstddef>
#include <numbers>
#include <print>

#include "gl.hpp"

// @alku glsl
constexpr const char* verteksivarjostin = R"(#version 450 core
layout(std140, binding = 0) uniform Kehysdata {
    mat4 muunnos;
    vec3 vari;
    float kirkkaus;      // pakkautuu vec3:n jälkeiseen tilaan
    float painot[3];     // taulukon askel std140:ssä on 16 tavua
    vec2 siirto;
} kd;
out vec3 v_vari;
void main() {
    // Neliön kulmat verteksin indeksistä: ei verteksipuskuria lainkaan.
    const vec2 kulmat[6] = vec2[](vec2(-1, -1), vec2(1, -1), vec2(1, 1),
                                  vec2(-1, -1), vec2(1, 1), vec2(-1, 1));
    vec4 p = kd.muunnos * vec4(kulmat[gl_VertexID], 0.0, 1.0);
    gl_Position = p + vec4(kd.siirto, 0.0, 0.0);
    v_vari = kd.vari * kd.kirkkaus *
             (kd.painot[0] + kd.painot[1] + kd.painot[2]);
}
)";
// @loppu glsl

constexpr const char* fragmenttivarjostin = R"(#version 450 core
in vec3 v_vari;
layout(location = 0) out vec4 tulos;
void main() { tulos = vec4(v_vari, 1.0); }
)";

// @alku cpp
// Sama lohko C++:ssa. std140: vec3 ja vec4 tasataan 16 tavuun, mat4
// on neljä vec4-saraketta, ja taulukon jokainen alkio vie 16 tavua.
struct Taulukkoalkio {
    float arvo;
    float tayte[3];
};
struct alignas(16) Kehysdata {
    float muunnos[16];          // sarakkeittain, kuten GLSL
    float vari[3];
    float kirkkaus;
    Taulukkoalkio painot[3];
    float siirto[2];
};
static_assert(offsetof(Kehysdata, vari) == 64);
static_assert(offsetof(Kehysdata, kirkkaus) == 76);
static_assert(offsetof(Kehysdata, painot) == 80);
static_assert(offsetof(Kehysdata, siirto) == 128);
// @loppu cpp

// @alku kysely
static void tulosta_siirtymat(GLuint ohjelma) {
    for (const char* nimi : {"Kehysdata.muunnos", "Kehysdata.vari",
                             "Kehysdata.kirkkaus", "Kehysdata.painot[0]",
                             "Kehysdata.siirto"}) {
        const GLuint i =
            glGetProgramResourceIndex(ohjelma, GL_UNIFORM, nimi);
        const GLenum kysytyt[] = {GL_OFFSET, GL_ARRAY_STRIDE};
        GLint arvot[2] = {};
        glGetProgramResourceiv(ohjelma, GL_UNIFORM, i, 2, kysytyt, 2,
                               nullptr, arvot);
        std::println("{:20} siirtymä {:3}, taulukon askel {}", nimi,
                     arvot[0], arvot[1]);
    }
}
// @loppu kysely

int main() {
    GlKonteksti gl;
    Kehys kehys(96, 96);
    const GLuint ohjelma =
        luo_ohjelma(verteksivarjostin, fragmenttivarjostin);
    tulosta_siirtymat(ohjelma);

    // @alku paivitys
    // Kierto 45°, skaalaus 0,5 ja siirto oikealle.
    const float a = std::numbers::pi_v<float> / 4.0f;
    const float c = 0.5f * std::cos(a), s = 0.5f * std::sin(a);
    const Kehysdata data{
        .muunnos = {c, s, 0, 0, -s, c, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1},
        .vari = {1.0f, 0.5f, 0.0f},
        .kirkkaus = 0.8f,
        .painot = {{0.5f, {}}, {0.25f, {}}, {0.25f, {}}},
        .siirto = {0.25f, 0.0f}};
    GLuint ubo = 0;
    glCreateBuffers(1, &ubo);
    glNamedBufferStorage(ubo, sizeof data, &data, 0);
    glBindBufferBase(GL_UNIFORM_BUFFER, 0, ubo);  // binding = 0
    // @loppu paivitys

    GLuint vao = 0;  // ydinprofiili vaatii VAO:n, vaikka se on tyhjä
    glCreateVertexArrays(1, &vao);
    glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
    glClear(GL_COLOR_BUFFER_BIT);
    glUseProgram(ohjelma);
    glBindVertexArray(vao);
    glDrawArrays(GL_TRIANGLES, 0, 6);

    const Kuva kuva = kehys.lue();
    GlKonteksti::tarkista();
    std::println("neliön keskikohta (60, 48): {}", kuva.vari(60, 48));
    std::println("vasen kärki (30, 48):       {}", kuva.vari(30, 48));
    std::println("kärjen ohi (22, 48):        {}", kuva.vari(22, 48));
    std::println("kulma (60, 18):             {}", kuva.vari(60, 18));
    std::println("peitetyt pikselit: {}", kuva.peitetyt({0, 0, 0}));

    glDeleteVertexArrays(1, &vao);
    glDeleteBuffers(1, &ubo);
    glDeleteProgram(ohjelma);
}
