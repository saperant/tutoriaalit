# Moderni C++ -tutoriaalin esimerkit.
#
#   make                       kääntää kaikki esimerkit hakemistoon bin/
#   make 01-hei                kääntää yhden esimerkin
#   make aja-01-hei            kääntää ja ajaa esimerkin
#   make virhe-02-kaventaminen näyttää .ei-kaanny-esimerkin käännösvirheen
#   make siivoa                poistaa käännetyt ohjelmat
#
# Ohjelmat käännetään AddressSanitizerin ja UndefinedBehaviorSanitizerin
# kanssa, kuten tutoriaalin testeissä. .ei-kaanny-esimerkit käännetään
# korjattuina (-DKORJATTU).

CXX      := $(shell command -v g++-14 >/dev/null 2>&1 && echo g++-14 || echo g++)
CXXFLAGS := -std=c++23 -Wall -Wextra -Wpedantic -g \
            -fsanitize=address,undefined -fno-sanitize-recover=all

TAVALLISET := $(basename $(filter-out %.ei-kaanny.cpp %.kaatuu.cpp,$(wildcard *.cpp)))
KAATUVAT   := $(patsubst %.kaatuu.cpp,%,$(wildcard *.kaatuu.cpp))
KORJATUT   := $(patsubst %.ei-kaanny.cpp,%,$(wildcard *.ei-kaanny.cpp))
HAKEMISTOT := $(sort $(patsubst %/,%,$(dir $(wildcard */*.cpp))))
OHJELMAT   := $(sort $(TAVALLISET) $(KAATUVAT) $(KORJATUT) $(HAKEMISTOT))

.PHONY: kaikki siivoa $(OHJELMAT)

kaikki: $(addprefix bin/,$(OHJELMAT))

$(OHJELMAT): %: bin/%

bin:
	mkdir -p bin

bin/%: %.cpp | bin
	$(CXX) $(CXXFLAGS) $< -o $@

bin/%: %.kaatuu.cpp | bin
	$(CXX) $(CXXFLAGS) $< -o $@

bin/%: %.ei-kaanny.cpp | bin
	$(CXX) $(CXXFLAGS) -DKORJATTU $< -o $@

define HAKEMISTO
bin/$(1): $(wildcard $(1)/*.cpp $(1)/*.hpp $(1)/*.h) | bin
	$$(CXX) $$(CXXFLAGS) $(wildcard $(1)/*.cpp) -o $$@
endef
$(foreach h,$(HAKEMISTOT),$(eval $(call HAKEMISTO,$(h))))

aja-%: bin/%
	./bin/$* $(if $(wildcard $*.argumentit),$$(cat $*.argumentit)) \
	    < $(if $(wildcard $*.syote),$*.syote,/dev/null)

virhe-%:
	-$(CXX) $(CXXFLAGS) -Werror -fsyntax-only $*.ei-kaanny.cpp

siivoa:
	rm -rf bin
