#define NELIO(x) ((x) * (x))
#define RAJA 100

// Neliön pinta-ala; -1, jos sivu on yli rajan.
int pinta_ala(int sivu)
{
    return sivu > RAJA ? -1 : NELIO(sivu);
}
