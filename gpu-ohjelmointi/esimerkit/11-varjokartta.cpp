// Varjokartta: kohtaus piirretään ensin valon näkökulmasta pelkkään
// syvyyspuskuriin. Toisessa vaiheessa kameran näkymän jokainen
// pikseli muunnetaan valon koordinaatteihin ja verrataan karttaan.
#include <array>
#include <numbers>
#include <print>

#include "gl.hpp"
#include "matriisi.hpp"

// @alku glsl
constexpr const char* verteksivarjostin = R"(#version 450 core
layout(location = 0) in vec3 sijainti;
layout(location = 0) uniform mat4 kamera;   // projektio · näkymä
layout(location = 1) uniform mat4 valo;     // valon projektio · näkymä
out vec4 v_valossa;                         // sijainti valon avaruudessa
void main() {
    v_valossa = valo * vec4(sijainti, 1.0);
    gl_Position = kamera * vec4(sijainti, 1.0);
}
)";

constexpr const char* fragmenttivarjostin = R"(#version 450 core
in vec4 v_valossa;
layout(location = 2) uniform vec3 vari;
// Vertailunäytteistin: palauttaa 1, jos syvyys ≤ kartan arvo.
layout(binding = 0) uniform sampler2DShadow kartta;
layout(location = 0) out vec4 tulos;
void main() {
    vec3 p = v_valossa.xyz / v_valossa.w * 0.5 + 0.5;  // 0…1
    float bias = 0.002;          // estää pinnan varjostamasta itseään
    float valoisa = texture(kartta, vec3(p.xy, p.z - bias));
    tulos = vec4(vari * mix(0.3, 1.0, valoisa), 1.0);
}
)";
// @loppu glsl

// Lattia y = 0 ja sen yläpuolella leijuva levy y = 1.
constexpr std::array<float, 36> kohtaus{
    -2, 0, -2,   2, 0, -2,   2, 0, 2,    -2, 0, -2,   2, 0, 2,  -2, 0, 2,
    -.5f, 1, -.5f, .5f, 1, -.5f, .5f, 1, .5f,
    -.5f, 1, -.5f, .5f, 1, .5f, -.5f, 1, .5f};

int main() {
    GlKonteksti gl;
    const GLuint ohjelma =
        luo_ohjelma(verteksivarjostin, fragmenttivarjostin);
    GLuint vbo = 0, vao = 0;
    glCreateBuffers(1, &vbo);
    glNamedBufferStorage(vbo, sizeof kohtaus, kohtaus.data(), 0);
    glCreateVertexArrays(1, &vao);
    glVertexArrayVertexBuffer(vao, 0, vbo, 0, 3 * sizeof(float));
    glEnableVertexArrayAttrib(vao, 0);
    glVertexArrayAttribFormat(vao, 0, 3, GL_FLOAT, GL_FALSE, 0);
    glVertexArrayAttribBinding(vao, 0, 0);

    const Mat4 valo = orto(3.0f, 0.1f, 10.0f) *
                      katse({1, 4, 1}, {0, 0, 0}, {0, 1, 0});
    const Mat4 kamera =
        perspektiivi(std::numbers::pi_v<float> / 4, 1.5f, 0.1f, 20.0f) *
        katse({0, 4, 5}, {0, 0, 0}, {0, 1, 0});

    // @alku kartta
    // Vaihe 1: syvyyskartta 256×256 valon näkökulmasta.
    GLuint kartta = 0, kartan_fbo = 0;
    glCreateTextures(GL_TEXTURE_2D, 1, &kartta);
    glTextureStorage2D(kartta, 1, GL_DEPTH_COMPONENT24, 256, 256);
    glTextureParameteri(kartta, GL_TEXTURE_COMPARE_MODE,
                        GL_COMPARE_REF_TO_TEXTURE);
    glTextureParameteri(kartta, GL_TEXTURE_COMPARE_FUNC, GL_LEQUAL);
    glCreateFramebuffers(1, &kartan_fbo);
    glNamedFramebufferTexture(kartan_fbo, GL_DEPTH_ATTACHMENT, kartta, 0);
    glNamedFramebufferDrawBuffer(kartan_fbo, GL_NONE);  // ei väriä

    glUseProgram(ohjelma);
    glBindVertexArray(vao);
    glEnable(GL_DEPTH_TEST);
    glBindFramebuffer(GL_FRAMEBUFFER, kartan_fbo);
    glViewport(0, 0, 256, 256);
    glClear(GL_DEPTH_BUFFER_BIT);
    glProgramUniformMatrix4fv(ohjelma, 0, 1, GL_FALSE, valo.m.data());
    glDrawArrays(GL_TRIANGLES, 0, 12);
    // @loppu kartta

    // @alku kamera
    // Vaihe 2: kameran näkymä; kartta luetaan tekstuurina.
    Kehys kehys(144, 96);  // sitoo kehyksen ja asettaa näkymäalueen
    glClearColor(0.1f, 0.1f, 0.15f, 1.0f);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glProgramUniformMatrix4fv(ohjelma, 0, 1, GL_FALSE, kamera.m.data());
    glProgramUniformMatrix4fv(ohjelma, 1, 1, GL_FALSE, valo.m.data());
    glBindTextureUnit(0, kartta);
    glProgramUniform3f(ohjelma, 2, 0.8f, 0.8f, 0.8f);   // lattia
    glDrawArrays(GL_TRIANGLES, 0, 6);
    glProgramUniform3f(ohjelma, 2, 1.0f, 0.55f, 0.1f);  // levy
    glDrawArrays(GL_TRIANGLES, 6, 6);
    // @loppu kamera

    const Kuva kuva = kehys.lue();
    GlKonteksti::tarkista();
    kuva.tallenna_ppm("bin/11-varjokartta.ppm");
    // @alku raportti
    // Varjo osuu levyn alle valon suunnassa: (−0,25; 0; −0,25).
    for (const auto& [nimi, p] :
         {std::pair{"varjossa", Vec3{-0.25f, 0.0f, -0.25f}},
          std::pair{"valossa ", Vec3{1.5f, 0.0f, 1.0f}},
          std::pair{"levyllä ", Vec3{0.3f, 1.0f, 0.3f}}}) {
        const auto [x, y] = pikseliksi(kamera, p, 144, 96);
        std::println("{} ({:3}, {:2}): {}", nimi, x, y, kuva.vari(x, y));
    }
    // @loppu raportti

    glDeleteFramebuffers(1, &kartan_fbo);
    glDeleteTextures(1, &kartta);
    glDeleteVertexArrays(1, &vao);
    glDeleteBuffers(1, &vbo);
    glDeleteProgram(ohjelma);
}
