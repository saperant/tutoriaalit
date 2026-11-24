/* Linkkeriskripti: Cortex-M33, QEMU mps2-an505. Ohjelma ajetaan
 * turvallisessa tilassa, joten käytetään muistien turvallisia
 * aliaksia: koodi SSRAM1:ssä ja data SSRAM2:ssa. */
ENTRY(Reset_Handler)

MEMORY
{
    FLASH (rx)  : ORIGIN = 0x10000000, LENGTH = 256K
    RAM   (rwx) : ORIGIN = 0x38000000, LENGTH = 64K
}

PINON_KOKO = 4K;
INCLUDE osiot.ld
