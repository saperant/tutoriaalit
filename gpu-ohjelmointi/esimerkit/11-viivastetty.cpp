// Viivästetty varjostus: geometriavaihe kirjoittaa pintojen tiedot
// G-puskuriin (useaan väriliitäntään), ja valaistusvaihe laskee valot
// kerran pikseliä kohden koko ruudun kattavalla kolmiolla.
#include <algorithm>
#include <array>
#include <cstdint>
#include <numbers>
#include <print>
#include <vector>

#include "gl.hpp"
#include "matriisi.hpp"

// @alku geometria
constexpr const char* geometria_vs = R"(#version 450 core
layout(location = 0) in vec3 sijainti;
layout(location = 1) in vec3 normaali;
layout(location = 2) in vec3 vari;
layout(location = 0) uniform mat4 kamera;
out vec3 v_sijainti, v_normaali, v_vari;
void main() {
    v_sijainti = sijainti;
    v_normaali = normaali;
    v_vari = vari;
    gl_Position = kamera * vec4(sijainti, 1.0);
}
)";

constexpr const char* geometria_fs = R"(#version 450 core
in vec3 v_sijainti, v_normaali, v_vari;
layout(location = 0) out vec4 g_vari;       // RGBA8
layout(location = 1) out vec4 g_normaali;   // RGBA16F
layout(location = 2) out vec4 g_sijainti;   // RGBA16F
void main() {
    g_vari = vec4(v_vari, 1.0);
    g_normaali = vec4(normalize(v_normaali), 0.0);
    g_sijainti = vec4(v_sijainti, 1.0);
}
)";
// @loppu geometria

// @alku valaistus
constexpr const char* valaistus_vs = R"(#version 450 core
void main() {
    vec2 p = vec2((gl_VertexID << 1) & 2, gl_VertexID & 2);
    gl_Position = vec4(p * 2.0 - 1.0, 0.0, 1.0);
}
)";

constexpr const char* valaistus_fs = R"(#version 450 core
layout(binding = 0) uniform sampler2D g_vari;
layout(binding = 1) uniform sampler2D g_normaali;
layout(binding = 2) uniform sampler2D g_sijainti;
struct Valo { vec3 sijainti; vec3 vari; };
layout(location = 0) uniform Valo valot[3];
layout(location = 0) out vec4 tulos;
void main() {
    ivec2 xy = ivec2(gl_FragCoord.xy);   // sama pikseli G-puskurista
    vec4 p = texelFetch(g_sijainti, xy, 0);
    if (p.w == 0.0) { tulos = vec4(0.0, 0.0, 0.0, 1.0); return; }
    vec3 n = texelFetch(g_normaali, xy, 0).xyz;
    vec3 albedo = texelFetch(g_vari, xy, 0).rgb;
    vec3 summa = 0.05 * albedo;                  // ympäristövalo
    for (int i = 0; i < 3; ++i) {
        vec3 l = valot[i].sijainti - p.xyz;
        float d2 = dot(l, l);
        float diffuusi = max(dot(n, normalize(l)), 0.0);
        summa += albedo * valot[i].vari * diffuusi / (1.0 + d2);
    }
    tulos = vec4(summa, 1.0);
}
)";
// @loppu valaistus

// Lattia (normaali ylös) ja takaseinä z = −1 (normaali kameraan päin).
struct V {
    float x, y, z, nx, ny, nz, r, g, b;
};
constexpr std::array<V, 12> kohtaus{{
    {-2, 0, -2, 0, 1, 0, .8f, .8f, .8f}, {2, 0, -2, 0, 1, 0, .8f, .8f, .8f},
    {2, 0, 2, 0, 1, 0, .8f, .8f, .8f},   {-2, 0, -2, 0, 1, 0, .8f, .8f, .8f},
    {2, 0, 2, 0, 1, 0, .8f, .8f, .8f},   {-2, 0, 2, 0, 1, 0, .8f, .8f, .8f},
    {-2, 0, -1, 0, 0, 1, .9f, .9f, .6f}, {2, 0, -1, 0, 0, 1, .9f, .9f, .6f},
    {2, 2, -1, 0, 0, 1, .9f, .9f, .6f},  {-2, 0, -1, 0, 0, 1, .9f, .9f, .6f},
    {2, 2, -1, 0, 0, 1, .9f, .9f, .6f},  {-2, 2, -1, 0, 0, 1, .9f, .9f, .6f},
}};

// Lukee liitännän liukulukuina ja tallentaa sen kuvana: arvo * kerroin
// + siirto välille 0–1.
static void tallenna_liitanta(GLuint tekstuuri, int l, int k, float kerroin,
                              float siirto, const char* polku) {
    std::vector<float> arvot(static_cast<std::size_t>(l * k * 4));
    glGetTextureImage(tekstuuri, 0, GL_RGBA, GL_FLOAT,
                      static_cast<GLsizei>(arvot.size() * sizeof(float)),
                      arvot.data());
    Kuva kuva(l, k);
    for (int y = 0; y < k; ++y) {
        for (int x = 0; x < l; ++x) {
            const auto lahde =
                static_cast<std::size_t>(((k - 1 - y) * l + x) * 4);
            const auto kohde = static_cast<std::size_t>((y * l + x) * 4);
            // Tyhjennetty pikseli (ei geometriaa) on kokonaan nolla.
            const bool tyhja =
                arvot[lahde] == 0.0f && arvot[lahde + 1] == 0.0f &&
                arvot[lahde + 2] == 0.0f && arvot[lahde + 3] == 0.0f;
            for (std::size_t c = 0; c < 3; ++c) {
                const float v = tyhja ? 0.0f
                                      : arvot[lahde + c] * kerroin + siirto;
                kuva.rgba[kohde + c] = static_cast<std::uint8_t>(
                    std::clamp(v, 0.0f, 1.0f) * 255.0f + 0.5f);
            }
        }
    }
    kuva.tallenna_ppm(polku);
}

int main() {
    GlKonteksti gl;
    constexpr int L = 144, K = 96;
    const GLuint geometria = luo_ohjelma(geometria_vs, geometria_fs);
    const GLuint valaistus = luo_ohjelma(valaistus_vs, valaistus_fs);

    // @alku gpuskuri
    // G-puskuri: kolme väriliitäntää ja syvyys samaan kehykseen.
    const std::array<GLenum, 3> muodot{GL_RGBA8, GL_RGBA16F, GL_RGBA16F};
    std::array<GLuint, 3> g{};
    GLuint g_syvyys = 0, g_fbo = 0;
    glCreateFramebuffers(1, &g_fbo);
    glCreateTextures(GL_TEXTURE_2D, 3, g.data());
    for (GLuint i = 0; i < 3; ++i) {
        glTextureStorage2D(g[i], 1, muodot[i], L, K);
        glNamedFramebufferTexture(g_fbo, GL_COLOR_ATTACHMENT0 + i, g[i], 0);
    }
    glCreateRenderbuffers(1, &g_syvyys);
    glNamedRenderbufferStorage(g_syvyys, GL_DEPTH_COMPONENT24, L, K);
    glNamedFramebufferRenderbuffer(g_fbo, GL_DEPTH_ATTACHMENT,
                                   GL_RENDERBUFFER, g_syvyys);
    const GLenum kohteet[] = {GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1,
                              GL_COLOR_ATTACHMENT2};
    glNamedFramebufferDrawBuffers(g_fbo, 3, kohteet);  // MRT
    // @loppu gpuskuri

    GLuint vbo = 0, vao = 0;
    glCreateBuffers(1, &vbo);
    glNamedBufferStorage(vbo, sizeof kohtaus, kohtaus.data(), 0);
    glCreateVertexArrays(1, &vao);
    glVertexArrayVertexBuffer(vao, 0, vbo, 0, sizeof(V));
    for (GLuint i = 0; i < 3; ++i) {
        glEnableVertexArrayAttrib(vao, i);
        glVertexArrayAttribFormat(vao, i, 3, GL_FLOAT, GL_FALSE,
                                  i * 3 * sizeof(float));
        glVertexArrayAttribBinding(vao, i, 0);
    }
    const Mat4 kamera =
        perspektiivi(std::numbers::pi_v<float> / 4, 1.5f, 0.1f, 20.0f) *
        katse({0, 3, 5}, {0, 0.5f, 0}, {0, 1, 0});

    // @alku vaiheet
    // Geometriavaihe: ei valaistusta, vain pintojen ominaisuudet.
    glBindFramebuffer(GL_FRAMEBUFFER, g_fbo);
    glViewport(0, 0, L, K);
    glClearColor(0, 0, 0, 0);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glEnable(GL_DEPTH_TEST);
    glUseProgram(geometria);
    glProgramUniformMatrix4fv(geometria, 0, 1, GL_FALSE, kamera.m.data());
    glBindVertexArray(vao);
    glDrawArrays(GL_TRIANGLES, 0, 12);
    glDisable(GL_DEPTH_TEST);

    // Valaistusvaihe: jokainen pikseli kerran, kaikki valot.
    Kehys kehys(L, K);
    glUseProgram(valaistus);
    const std::array<std::array<float, 6>, 3> valot{{
        {-1.2f, 0.3f, 0.5f, 3, 0, 0},   // punainen vasemmalla
        {0.0f, 0.3f, -0.5f, 0, 3, 0},   // vihreä seinän edessä
        {1.2f, 0.3f, 0.5f, 0, 0, 3}}};  // sininen oikealla
    for (GLint i = 0; i < 3; ++i) {
        glProgramUniform3fv(valaistus, 2 * i, 1, &valot[i][0]);
        glProgramUniform3fv(valaistus, 2 * i + 1, 1, &valot[i][3]);
    }
    for (GLuint i = 0; i < 3; ++i) {
        glBindTextureUnit(i, g[i]);
    }
    glDrawArrays(GL_TRIANGLES, 0, 3);
    // @loppu vaiheet

    const Kuva kuva = kehys.lue();
    GlKonteksti::tarkista();
    kuva.tallenna_ppm("bin/11-viivastetty.ppm");
    // Kuvitus (make kuvat): G-puskurin liitännät väreinä. Normaali ja
    // sijainti skaalataan välille 0–1.
    tallenna_liitanta(g[0], L, K, 1.0f, 0.0f, "bin/11-g-albedo.ppm");
    tallenna_liitanta(g[1], L, K, 0.5f, 0.5f, "bin/11-g-normaali.ppm");
    tallenna_liitanta(g[2], L, K, 0.25f, 0.5f, "bin/11-g-sijainti.ppm");
    // @alku raportti
    for (const auto& v : valot) {
        const auto [x, y] =
            pikseliksi(kamera, {v[0], 0.0f, v[2]}, L, K);
        std::println("lattia valon alla ({:3}, {:2}): {}", x, y,
                     kuva.vari(x, y));
    }
    const int tavuja = 4 + 8 + 8 + 3;  // RGBA8 + 2 × RGBA16F + syvyys
    std::println("G-puskuri {} tavua/pikseli, 1920×1080: {:.1f} MiB",
                 tavuja, tavuja * 1920.0 * 1080.0 / (1 << 20));
    // @loppu raportti

    glDeleteVertexArrays(1, &vao);
    glDeleteBuffers(1, &vbo);
    glDeleteRenderbuffers(1, &g_syvyys);
    glDeleteTextures(3, g.data());
    glDeleteFramebuffers(1, &g_fbo);
    glDeleteProgram(geometria);
    glDeleteProgram(valaistus);
}
