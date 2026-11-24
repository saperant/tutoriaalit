# Kide-kääntäjän rakentaminen ja testaus.
#
#   make           kääntää kääntäjän GCC:llä ja Clangilla sanitoijin ja
#                  ajaa kaikki testit (ks. testaa.sh)
#   make naytteet  kirjoittaa tekstissä näytetyt tulosteet uudelleen
#   make siivoa    poistaa build/-hakemiston

# @alku liput
CXXFLAGS := -std=c++23 -O1 -g -Wall -Wextra -Werror -Wshadow \
            -Wno-missing-field-initializers \
            -fsanitize=address,undefined -fno-sanitize-recover=all
# @loppu liput
LAHTEET  := $(wildcard kide/*.cpp)
OTSIKOT  := $(wildcard kide/*.hpp)
GCC_O    := $(LAHTEET:kide/%.cpp=build/gcc/%.o)
CLANG_O  := $(LAHTEET:kide/%.cpp=build/clang/%.o)
# Tarkoituksella rikottu kääntäjä: testien on löydettävä vika.
VIKA_O   := $(filter-out build/gcc/koodigen.o,$(GCC_O)) build/vika/koodigen.o

.PHONY: kaikki naytteet siivoa

kaikki: build/gcc/kide build/clang/kide build/vika/kide build/ajonaikainen.o
	./testaa.sh

naytteet: build/gcc/kide build/ajonaikainen.o
	./testaa.sh --naytteet

build/gcc/%.o: kide/%.cpp $(OTSIKOT)
	@mkdir -p $(@D)
	g++-14 $(CXXFLAGS) -c $< -o $@

build/clang/%.o: kide/%.cpp $(OTSIKOT)
	@mkdir -p $(@D)
	clang++-20 $(CXXFLAGS) -c $< -o $@

build/vika/koodigen.o: kide/koodigen.cpp $(OTSIKOT)
	@mkdir -p $(@D)
	g++-14 $(CXXFLAGS) -DKIDE_VIKA -c $< -o $@

build/vika/kide: $(VIKA_O)
	g++-14 $(CXXFLAGS) $^ -o $@

build/gcc/kide: $(GCC_O)
	g++-14 $(CXXFLAGS) $^ -o $@

build/clang/kide: $(CLANG_O)
	clang++-20 $(CXXFLAGS) $^ -o $@

build/ajonaikainen.o: ajonaikainen.c
	@mkdir -p $(@D)
	riscv64-linux-gnu-gcc -O2 -Wall -Wextra -Werror -c $< -o $@

siivoa:
	rm -rf build
