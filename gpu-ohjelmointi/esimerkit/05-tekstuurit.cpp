// Tekstuurit: suodatus suurennettaessa (lähin vs. lineaarinen) ja
// pienennettäessä (ilman ja kanssa mip-tasojen). Koko ruudun kattava
// kolmio näytteistää tekstuurin jokaiseen pikseliin.
#include <algorithm>
#include <format>
#include <print>
#include <string>
#include <vector>

#include "gl.hpp"

// @alku glsl
constexpr const char* verteksivarjostin = R"(#version 450 core
out vec2 uv;
void main() {
    // Yksi kolmio, joka peittää koko ruudun: (-1,-1), (3,-1), (-1,3).
    vec2 p = vec2((gl_VertexID << 1) & 2, gl_VertexID & 2);
    uv = p;
    gl_Position = vec4(p * 2.0 - 1.0, 0.0, 1.0);
}
)";

constexpr const char* fragmenttivarjostin = R"(#version 450 core
in vec2 uv;
layout(binding = 0) uniform sampler2D kuva;   // tekstuuriyksikkö 0
layout(location = 0) out vec4 tulos;
void main() { tulos = texture(kuva, uv); }
)";
// @loppu glsl

// @alku tekstuuri
// Harmaasävytekstuuri RGBA8-muodossa; mip-tasot valinnaisesti.
static GLuint luo_tekstuuri(int l, int k, const std::vector<GLubyte>& g,
                            bool mipit) {
    std::vector<GLubyte> rgba;
    for (GLubyte v : g) {
        rgba.insert(rgba.end(), {v, v, v, 255});
    }
    GLuint t = 0;
    glCreateTextures(GL_TEXTURE_2D, 1, &t);
    int tasoja = 1;
    for (int koko = std::max(l, k); mipit && koko > 1; koko /= 2) {
        ++tasoja;
    }
    glTextureStorage2D(t, tasoja, GL_RGBA8, l, k);
    glTextureSubImage2D(t, 0, 0, 0, l, k, GL_RGBA, GL_UNSIGNED_BYTE,
                        rgba.data());
    if (mipit) {
        glGenerateTextureMipmap(t);  // keskiarvot pienemmille tasoille
    }
    glTextureParameteri(t, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
    glTextureParameteri(t, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
    return t;
}
// @loppu tekstuuri

static std::string luettelo(const std::vector<int>& arvot) {
    std::string s;
    for (int v : arvot) {
        s += std::format("{:4}", v);
    }
    return s;
}

// Piirtää tekstuurin koko kehykseen ja palauttaa rivin y harmaasävyt.
static std::vector<int> piirra(GLuint t, GLenum pienennys,
                               GLenum suurennus, int y, int askel) {
    glTextureParameteri(t, GL_TEXTURE_MIN_FILTER,
                        static_cast<GLint>(pienennys));
    glTextureParameteri(t, GL_TEXTURE_MAG_FILTER,
                        static_cast<GLint>(suurennus));
    glBindTextureUnit(0, t);
    glDrawArrays(GL_TRIANGLES, 0, 3);
    GLint vp[4];
    glGetIntegerv(GL_VIEWPORT, vp);
    std::vector<GLubyte> rivi(static_cast<std::size_t>(vp[2] * 4));
    glReadPixels(0, y, vp[2], 1, GL_RGBA, GL_UNSIGNED_BYTE, rivi.data());
    std::vector<int> arvot;
    for (int x = 0; x < vp[2]; x += askel) {
        arvot.push_back(rivi[static_cast<std::size_t>(x * 4)]);
    }
    return arvot;
}

int main() {
    GlKonteksti gl;
    const GLuint ohjelma =
        luo_ohjelma(verteksivarjostin, fragmenttivarjostin);
    GLuint vao = 0;
    glCreateVertexArrays(1, &vao);
    glUseProgram(ohjelma);
    glBindVertexArray(vao);

    // @alku suurennus
    {
        // 2×2-ruudukko venytetään 64×64 pikseliin (suurennus 32×).
        Kehys kehys(64, 64);
        const GLuint t = luo_tekstuuri(2, 2, {0, 255, 255, 0}, false);
        std::println("suurennus, rivi 16 joka 8. pikseli:");
        std::println("  lähin:      {}",
                     luettelo(piirra(t, GL_NEAREST, GL_NEAREST, 16, 8)));
        std::println("  lineaarinen:{}",
                     luettelo(piirra(t, GL_LINEAR, GL_LINEAR, 16, 8)));
        kehys.lue().tallenna_ppm("bin/05-tekstuurit.ppm");
        glDeleteTextures(1, &t);
    }
    // @loppu suurennus

    // @alku pienennys
    {
        // 256×256 pystyraitaa (musta, valkoinen, …) 32×32 pikseliin:
        // kahdeksan tekseliä yhteen pikseliin.
        Kehys kehys(32, 32);
        std::vector<GLubyte> raidat(256 * 256);
        for (std::size_t i = 0; i < raidat.size(); ++i) {
            raidat[i] = (i % 2 == 0) ? 0 : 255;
        }
        const GLuint ilman = luo_tekstuuri(256, 256, raidat, false);
        const GLuint mip = luo_tekstuuri(256, 256, raidat, true);
        const auto a = piirra(ilman, GL_NEAREST, GL_NEAREST, 16, 1);
        const auto b =
            piirra(mip, GL_LINEAR_MIPMAP_LINEAR, GL_LINEAR, 16, 1);
        std::println("pienennys, rivin 16 pienin ja suurin arvo:");
        std::println("  ilman mip-tasoja: {}–{}",
                     *std::ranges::min_element(a),
                     *std::ranges::max_element(a));
        std::println("  mip-tasoilla:     {}–{}",
                     *std::ranges::min_element(b),
                     *std::ranges::max_element(b));
        glDeleteTextures(1, &ilman);
        glDeleteTextures(1, &mip);
    }
    // @loppu pienennys
    GlKonteksti::tarkista();
    glDeleteVertexArrays(1, &vao);
    glDeleteProgram(ohjelma);
}
