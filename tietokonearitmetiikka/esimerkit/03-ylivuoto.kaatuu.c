// Myyntien summa senteissä 32-bittisessä int-muuttujassa.
#include <stdio.h>

int main(void)
{
    // @alku summa
    int myynnit[] = {900000000, 900000000, 900000000};  // sentteinä
    int summa = 0;
    for (int i = 0; i < 3; i++) {
        summa += myynnit[i];      // kolmas lisäys ylittää INT_MAX:n
    }
    // @loppu summa
    printf("%d\n", summa);
    return 0;
}
