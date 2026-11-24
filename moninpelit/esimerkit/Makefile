# Moninpeliesimerkit, joita yhteinen testaaja ei aja.
#
#   make          UDP-lukitusaskelpeli: palvelin ja kaksi asiakasta
#   make siivoa   poistaa käännökset
#
# Muut esimerkit käännetään ja ajetaan kuten tutoriaalin testeissä:
#   g++ -std=c++23 -Wall -Wextra -fsanitize=address,undefined x.cpp

CXX      := $(shell command -v g++-14 >/dev/null 2>&1 \
                    && echo g++-14 || echo g++)
CXXFLAGS := -std=c++23 -Wall -Wextra -Wpedantic -Werror -g \
            -fsanitize=address,undefined -fno-sanitize-recover=all
OTSAKKEET := udp/src/protokolla.hpp $(wildcard yhteinen/*.hpp)

.PHONY: kaikki udp siivoa

kaikki: udp

bin:
	mkdir -p bin

bin/%: udp/src/%.cpp $(OTSAKKEET) | bin
	$(CXX) $(CXXFLAGS) $< -o $@

# @alku udp
udp: bin/palvelin bin/asiakas
	./udp/aja.sh bin | diff -u udp/udp.odotettu -
	@echo "OK: UDP-lukitusaskel"
# @loppu udp

siivoa:
	rm -rf bin
