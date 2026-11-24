#include <stdio.h>
#include <stdlib.h>

void kirjasto_kaytossa(void);

// @alku jarjestys
// Prioriteetit 101-65535 ovat sovelluksen käytössä; pienempi ajetaan
// ensin alussa ja viimeisenä lopussa.
__attribute__((constructor(101))) static void asetukset(void)
{
    puts("2. ohjelman konstruktori (101)");
}

__attribute__((constructor(200))) static void rekisteri(void)
{
    puts("3. ohjelman konstruktori (200)");
}

static void siivous(void) { puts("6. atexit-käsittelijä"); }

__attribute__((destructor)) static void loppu(void)
{
    puts("7. ohjelman destruktori");
}

int main(void)
{
    atexit(siivous);
    kirjasto_kaytossa();
    puts("5. main palaa");
    return 0;
}
// @loppu jarjestys
