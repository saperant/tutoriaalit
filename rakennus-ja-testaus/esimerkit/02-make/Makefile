# Tilasto-ohjelma: ensimmäinen, tarkoituksella yksinkertainen Makefile.
# Kääntäjä tulee muuttujasta CC (ympäristöstä tai make CC=clang-20).

CFLAGS = -std=c17 -Wall -Wextra -O2
LDLIBS = -lm

# @alku saannot
tilasto: main.o tilasto.o
	$(CC) $(LDFLAGS) $^ $(LDLIBS) -o $@

main.o: lahde/main.c
	$(CC) $(CFLAGS) -c $< -o $@

tilasto.o: lahde/tilasto.c
	$(CC) $(CFLAGS) -c $< -o $@
# @loppu saannot

# @alku phony
.PHONY: testaa siivoa

testaa: tilasto
	./tilasto < lahde/mittaukset.txt

siivoa:
	rm -f tilasto *.o
# @loppu phony
