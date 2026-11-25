# GPU-ohjelmoinnin esimerkit. paketti.mk ajaa tämän osana "make testaa"
# -kohdetta.
#
#   make             kääntää varjostimet ja ohjelmat, ajaa ne ja vertaa
#                    tulosteet tiedostoihin <nimi>.odotettu
#   make aja-NIMI    kääntää ja ajaa yhden esimerkin
#   make kuvat       kokoaa ajojen kuvat PNG:ksi (../kuvat/kokoa.py)
#   make siivoa      poistaa käännöstuotteet
#
# Ajot käyttävät Mesan ohjelmistorenderöijiä, joten näytönohjainta tai
# näyttöä ei tarvita: OpenGL llvmpipellä EGL:n kautta ja Vulkan
# lavapipellä. Validointikerros on päällä, jos se on asennettu.

CXX      := $(shell command -v g++-14 || echo g++)
# Vulkan-rakenteet alustetaan nimetyin kentin (.sType = …), ja loput
# kentät nollautuvat tarkoituksella; siitä ei varoiteta.
CXXFLAGS := -std=c++23 -O2 -g -Wall -Wextra -Wpedantic -Werror \
            -Wshadow -Wconversion -Wno-missing-field-initializers \
            -Iyhteinen
GLLIBS   := -lEGL -lOpenGL
VKLIBS   := -lvulkan

export EGL_PLATFORM           := surfaceless
export LIBGL_ALWAYS_SOFTWARE  := 1
export GALLIUM_DRIVER         := llvmpipe
export VK_DRIVER_FILES        := /usr/share/vulkan/icd.d/lvp_icd.json
export VK_ICD_FILENAMES       := $(VK_DRIVER_FILES)
export MESA_SHADER_CACHE_DISABLE := true

LAHTEET   := $(wildcard *.cpp)
OHJELMAT  := $(patsubst %.cpp,bin/%,$(LAHTEET))
VARJOSTIMET := $(patsubst varjostimet/%,bin/%.spv,\
                 $(wildcard varjostimet/*.vert varjostimet/*.frag))
AJOT      := $(patsubst %.cpp,aja-%,$(LAHTEET))

.PHONY: kaikki $(AJOT) kuvat siivoa

kaikki: $(AJOT)

# @alku spirv
# GLSL → SPIR-V: esim. varjostimet/kolmio.vert → bin/kolmio.vert.spv
bin/%.spv: varjostimet/% | bin
	glslc --target-env=vulkan1.3 -Werror -O $< -o $@
# @loppu spirv

bin/%: %.cpp yhteinen/*.hpp | bin
	$(CXX) $(CXXFLAGS) $< -o $@ $(if $(findstring vk,$*),$(VKLIBS),$(GLLIBS))

# Ohjelma ajetaan tässä hakemistossa; kuvat menevät hakemistoon bin/.
$(AJOT): aja-%: bin/% $(VARJOSTIMET)
	@./bin/$* > bin/$*.tuloste && diff -u $*.odotettu bin/$*.tuloste \
	    && echo "OK: $*"

bin:
	mkdir -p bin

KUVAT := 03-kolmio 05-tekstuurit 06-syvyys 11-varjokartta 11-viivastetty
kuvat: $(addprefix aja-,$(KUVAT))
	python3 ../kuvat/kokoa.py

siivoa:
	rm -rf bin
