/* Linkkeriskripti: Cortex-M3, QEMU mps2-an385. */
ENTRY(Reset_Handler)

MEMORY
{
    FLASH (rx)  : ORIGIN = 0x00000000, LENGTH = 256K
    RAM   (rwx) : ORIGIN = 0x20000000, LENGTH = 64K
}

PINON_KOKO = 4K;
INCLUDE osiot.ld
