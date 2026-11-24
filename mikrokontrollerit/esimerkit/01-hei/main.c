/* Ensimmäinen bare-metal-ohjelma: tervehdys sarjaporttiin. */
#include "konsoli.h"

// @alku main
int main(void) {
    konsoli_alusta();
    konsoli_kirjoita("Hei, Cortex-M3!\n");
    tulosta("Kello %u Hz, vastaus %d, maski 0x%08x\n",
            25000000u, 42, 0x2au);
    return 0;   /* Reset_Handler välittää arvon QEMU:lle */
}
// @loppu main
