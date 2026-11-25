# Peliohjelmoinnin esimerkit, joita yhteinen testaaja ei aja.
#
#   make          SDL2-etupään testi ja suorituskykymittaus
#   make sdl      kääntää Kipinän SDL2-version (bin/kipina-sdl)
#   make pelaa    käynnistää Kipinän ikkunassa
#   make mittaa   oliot vastaan taulukot -mittaus (-O2)
#   make siivoa   poistaa käännökset
#
# Muut esimerkit käännetään ja ajetaan kuten tutoriaalin testeissä:
#   g++ -std=c++23 -Wall -Wextra -fsanitize=address,undefined x.cpp

CXX      := $(shell command -v g++-14 >/dev/null 2>&1 \
                    && echo g++-14 || echo g++)
CXXFLAGS := -std=c++23 -Wall -Wextra -Wpedantic -Werror
SDL      := $(shell sdl2-config --cflags --libs 2>/dev/null)
KIPINA   := 12-kipina/peli.cpp 12-kipina/piirto.cpp

.PHONY: kaikki sdl sdl-testi pelaa mittaa siivoa

kaikki: sdl-testi mittaa

bin:
	mkdir -p bin

# @alku sdl
bin/kipina-sdl: sdl/src/kipina-sdl.cpp $(KIPINA) \
                $(wildcard 12-kipina/*.hpp) | bin
	@test -n "$(SDL)" || { echo "SDL2 puuttuu (libsdl2-dev)"; exit 1; }
	$(CXX) $(CXXFLAGS) -g -fsanitize=address,undefined \
	    sdl/src/kipina-sdl.cpp $(KIPINA) $(SDL) -o $@
# @loppu sdl

sdl: bin/kipina-sdl

sdl-testi: bin/kipina-sdl
	./bin/kipina-sdl --testi | diff -u sdl/kipina-sdl.odotettu -
	@echo "OK: SDL2-etupää"

pelaa: bin/kipina-sdl
	./bin/kipina-sdl

bin/oliot-vs-taulukot: mittaus/src/oliot-vs-taulukot.cpp | bin
	$(CXX) $(CXXFLAGS) -O2 $< -o $@

mittaa: bin/oliot-vs-taulukot
	./bin/oliot-vs-taulukot | diff -u mittaus/oliot-vs-taulukot.odotettu -
	@echo "OK: oliot vastaan taulukot"

siivoa:
	rm -rf bin
