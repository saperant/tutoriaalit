# GPU-laskennan esimerkit. paketti.mk ajaa tämän osana "make testaa"
# -kohdetta.
#
#   make             kääntää varjostimet ja ohjelmat, ajaa ne ja vertaa
#                    tulosteet tiedostoihin <nimi>.odotettu
#   make aja-NIMI    kääntää ja ajaa yhden esimerkin
#   make mittaa      ajaa esimerkit valitsimella --mittaa (ajat
#                    vaihtelevat koneittain, eikä niitä verrata)
#   make siivoa      poistaa käännöstuotteet
#
# Varjostimet ajetaan Mesan lavapipe-ajurilla CPU:lla, joten
# näytönohjainta ei tarvita. Validointikerros on päällä, jos se on
# asennettu, ja jokaisen ajon on päätyttävä ilman ilmoituksia.

CXX      := $(shell command -v g++-14 || echo g++)
CLANGXX  := $(shell command -v clang++-20 || command -v clang++)
# Vulkan-rakenteet alustetaan nimetyin kentin (.sType = …), ja loput
# kentät nollautuvat tarkoituksella; siitä ei varoiteta.
CXXFLAGS := -std=c++23 -O2 -g -Wall -Wextra -Wpedantic -Werror \
            -Wshadow -Wconversion -Wno-missing-field-initializers \
            -D_GLIBCXX_ASSERTIONS -Iyhteinen
LIBS     := -lvulkan

# @alku ymparisto
# Lavapipe ilman näytönohjainta. Vektorileveys 256 bittiä tekee
# aliryhmästä 8 kaistan levyisen kaikilla x86-64-koneilla, joten
# aliryhmistä riippuvat tulosteet ovat samat kaikkialla.
export VK_DRIVER_FILES        := /usr/share/vulkan/icd.d/lvp_icd.json
export VK_ICD_FILENAMES       := $(VK_DRIVER_FILES)
export LP_NATIVE_VECTOR_WIDTH := 256
export MESA_SHADER_CACHE_DISABLE := true
# @loppu ymparisto

LAHTEET     := $(wildcard *.cpp)
OHJELMAT    := $(patsubst %.cpp,bin/%,$(LAHTEET))
VARJOSTIMET := $(patsubst varjostimet/%.comp,bin/%.spv,\
                 $(wildcard varjostimet/*.comp))
AJOT        := $(patsubst %.cpp,aja-%,$(LAHTEET))
MITTAUKSET  := $(patsubst %.cpp,mittaa-%,$(LAHTEET))

.PHONY: kaikki $(AJOT) mittaa $(MITTAUKSET) siivoa

kaikki: $(AJOT)

# @alku spirv
# GLSL → SPIR-V: varjostimet/saxpy.comp → bin/saxpy.spv. Varoitukset
# ovat virheitä, ja spirv-val tarkistaa tuloksen, jos se on asennettu.
bin/%.spv: varjostimet/%.comp | bin
	glslc --target-env=vulkan1.3 -Werror -O $< -o $@
	if command -v spirv-val > /dev/null; then \
	    spirv-val --target-env vulkan1.3 $@; fi
# @loppu spirv

# Ohjelma käännetään GCC:llä, ja Clang tarkistaa saman lähteen
# varoitusten osalta.
bin/%: %.cpp yhteinen/*.hpp | bin
	$(CXX) $(CXXFLAGS) $< -o $@ $(LIBS)
	if [ -n "$(CLANGXX)" ]; then \
	    $(CLANGXX) $(CXXFLAGS) -fsyntax-only $<; fi

$(AJOT): aja-%: bin/% $(VARJOSTIMET)
	@./bin/$* > bin/$*.tuloste && diff -u $*.odotettu bin/$*.tuloste \
	    && echo "OK: $*"

mittaa: $(MITTAUKSET)
$(MITTAUKSET): mittaa-%: bin/% $(VARJOSTIMET)
	@echo "== $*" && ./bin/$* --mittaa

bin:
	mkdir -p bin

siivoa:
	rm -rf bin
