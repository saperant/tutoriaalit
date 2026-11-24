// OpenGL ilman ikkunaa: EGL-konteksti, varjostinohjelmat ja
// kehyspuskuri, jonka sisältö luetaan kuvaksi.
#pragma once

#define GL_GLEXT_PROTOTYPES
#include <EGL/egl.h>
#include <EGL/eglext.h>
#include <GL/glcorearb.h>

#include <stdexcept>
#include <string>

#include "kuva.hpp"

// @alku konteksti
// OpenGL 4.5 -ydinprofiilin konteksti ilman näyttöä ja ikkunaa
// (EGL_MESA_platform_surfaceless). Piirretään aina omaan
// kehyspuskuriin, joten ikkunan pintaa ei tarvita.
class GlKonteksti {
public:
    GlKonteksti() {
        auto hae_naytto = reinterpret_cast<PFNEGLGETPLATFORMDISPLAYEXTPROC>(
            eglGetProcAddress("eglGetPlatformDisplayEXT"));
        if (hae_naytto == nullptr) {
            throw std::runtime_error("EGL_EXT_platform_base puuttuu");
        }
        naytto_ = hae_naytto(EGL_PLATFORM_SURFACELESS_MESA,
                             EGL_DEFAULT_DISPLAY, nullptr);
        if (eglInitialize(naytto_, nullptr, nullptr) == EGL_FALSE) {
            throw std::runtime_error("eglInitialize epäonnistui");
        }
        eglBindAPI(EGL_OPENGL_API);
        const EGLint ominaisuudet[] = {
            EGL_CONTEXT_MAJOR_VERSION, 4,
            EGL_CONTEXT_MINOR_VERSION, 5,
            EGL_CONTEXT_OPENGL_PROFILE_MASK,
            EGL_CONTEXT_OPENGL_CORE_PROFILE_BIT,
            EGL_CONTEXT_OPENGL_DEBUG, EGL_TRUE,
            EGL_NONE};
        konteksti_ = eglCreateContext(naytto_, EGL_NO_CONFIG_KHR,
                                      EGL_NO_CONTEXT, ominaisuudet);
        if (konteksti_ == EGL_NO_CONTEXT ||
            eglMakeCurrent(naytto_, EGL_NO_SURFACE, EGL_NO_SURFACE,
                           konteksti_) == EGL_FALSE) {
            throw std::runtime_error("OpenGL 4.5 -kontekstia ei saatu");
        }
        // Ajuri kertoo virheet takaisinkutsulla heti syntykohdassa.
        glEnable(GL_DEBUG_OUTPUT_SYNCHRONOUS);
        glDebugMessageCallback(virheilmoitus, nullptr);
    }

    // Heittää poikkeuksen, jos ajuri on ilmoittanut virheestä.
    // (Takaisinkutsusta ei saa heittää: se kulkisi ajurin C-koodin läpi.)
    static void tarkista() {
        if (!virhe().empty()) {
            throw std::runtime_error("GL: " + virhe());
        }
    }
    ~GlKonteksti() {
        eglMakeCurrent(naytto_, EGL_NO_SURFACE, EGL_NO_SURFACE,
                       EGL_NO_CONTEXT);
        eglDestroyContext(naytto_, konteksti_);
        eglTerminate(naytto_);
    }
    GlKonteksti(const GlKonteksti&) = delete;
    GlKonteksti& operator=(const GlKonteksti&) = delete;

private:
    static void APIENTRY virheilmoitus(GLenum, GLenum tyyppi, GLuint,
                                         GLenum vakavuus, GLsizei,
                                         const GLchar* viesti,
                                         const void*) {
        if ((tyyppi == GL_DEBUG_TYPE_ERROR ||
             vakavuus == GL_DEBUG_SEVERITY_HIGH) && virhe().empty()) {
            virhe() = viesti;
        }
    }
    static std::string& virhe() {
        static std::string ensimmainen;
        return ensimmainen;
    }
    EGLDisplay naytto_ = EGL_NO_DISPLAY;
    EGLContext konteksti_ = EGL_NO_CONTEXT;
};
// @loppu konteksti

// @alku ohjelma
// Kääntää varjostimen; virhetilanteessa poikkeus kääntäjän lokin kera.
inline GLuint kaanna_varjostin(GLenum laji, const char* lahde) {
    const GLuint v = glCreateShader(laji);
    glShaderSource(v, 1, &lahde, nullptr);
    glCompileShader(v);
    GLint ok = GL_FALSE;
    glGetShaderiv(v, GL_COMPILE_STATUS, &ok);
    if (ok == GL_FALSE) {
        char loki[1024] = {};
        glGetShaderInfoLog(v, sizeof loki, nullptr, loki);
        glDeleteShader(v);
        throw std::runtime_error(std::string("varjostin: ") + loki);
    }
    return v;
}

// Kääntää ja linkittää verteksi- ja fragmenttivarjostimen ohjelmaksi.
inline GLuint luo_ohjelma(const char* verteksi, const char* fragmentti) {
    const GLuint vs = kaanna_varjostin(GL_VERTEX_SHADER, verteksi);
    const GLuint fs = kaanna_varjostin(GL_FRAGMENT_SHADER, fragmentti);
    const GLuint ohjelma = glCreateProgram();
    glAttachShader(ohjelma, vs);
    glAttachShader(ohjelma, fs);
    glLinkProgram(ohjelma);
    glDeleteShader(vs);  // ohjelma pitää varjostimet elossa
    glDeleteShader(fs);
    GLint ok = GL_FALSE;
    glGetProgramiv(ohjelma, GL_LINK_STATUS, &ok);
    if (ok == GL_FALSE) {
        char loki[1024] = {};
        glGetProgramInfoLog(ohjelma, sizeof loki, nullptr, loki);
        throw std::runtime_error(std::string("linkitys: ") + loki);
    }
    return ohjelma;
}
// @loppu ohjelma

// @alku kehys
// Kehyspuskuri: väri RGBA8 ja syvyys+sapluuna 24+8 bittiä.
struct Kehys {
    GLuint fbo = 0, vari = 0, syvyys = 0;
    int leveys, korkeus;

    Kehys(int l, int k) : leveys{l}, korkeus{k} {
        glCreateTextures(GL_TEXTURE_2D, 1, &vari);
        glTextureStorage2D(vari, 1, GL_RGBA8, l, k);
        glCreateRenderbuffers(1, &syvyys);
        glNamedRenderbufferStorage(syvyys, GL_DEPTH24_STENCIL8, l, k);
        glCreateFramebuffers(1, &fbo);
        glNamedFramebufferTexture(fbo, GL_COLOR_ATTACHMENT0, vari, 0);
        glNamedFramebufferRenderbuffer(fbo, GL_DEPTH_STENCIL_ATTACHMENT,
                                       GL_RENDERBUFFER, syvyys);
        if (glCheckNamedFramebufferStatus(fbo, GL_FRAMEBUFFER) !=
            GL_FRAMEBUFFER_COMPLETE) {
            throw std::runtime_error("kehyspuskuri ei ole valmis");
        }
        glBindFramebuffer(GL_FRAMEBUFFER, fbo);
        glViewport(0, 0, l, k);
    }
    ~Kehys() {
        glDeleteFramebuffers(1, &fbo);
        glDeleteRenderbuffers(1, &syvyys);
        glDeleteTextures(1, &vari);
    }
    Kehys(const Kehys&) = delete;
    Kehys& operator=(const Kehys&) = delete;

    // Lukee värikuvan CPU:lle. OpenGL:n rivit alkavat alhaalta, joten
    // järjestys käännetään kuvatiedostojen tapaan ylhäältä alas.
    Kuva lue() const {
        Kuva kuva(leveys, korkeus);
        std::vector<std::uint8_t> rivit(kuva.rgba.size());
        glPixelStorei(GL_PACK_ALIGNMENT, 1);
        glGetTextureImage(vari, 0, GL_RGBA, GL_UNSIGNED_BYTE,
                          static_cast<GLsizei>(rivit.size()),
                          rivit.data());
        const auto rivi = static_cast<std::size_t>(leveys * 4);
        for (int y = 0; y < korkeus; ++y) {
            const auto lahde = static_cast<std::size_t>(korkeus - 1 - y);
            std::copy_n(rivit.begin() + lahde * rivi, rivi,
                        kuva.rgba.begin() + y * rivi);
        }
        return kuva;
    }
};
// @loppu kehys
