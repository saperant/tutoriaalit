// VIENTI merkitsee kirjaston julkisen rajapinnan: se näkyy aina, myös
// kun muu kirjasto käännetään valitsimella -fvisibility=hidden.
#define VIENTI __attribute__((visibility("default")))

// @alku mittari
int kutsuja = 0;                      // kirjaston globaali muuttuja

int pyorista(int arvo)                // apufunktio
{
    return (arvo + 5) / 10 * 10;
}

VIENTI int mittaa(int raaka)          // julkinen rajapinta
{
    ++kutsuja;
    return pyorista(raaka * 3);
}
// @loppu mittari
