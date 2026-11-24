/* Pikku-SoC:n linkkeriskripti: kaikki osiot 16 KiB:n RAMiin.
 *
 * Nollauksen jälkeen ydin hakee ensimmäisen käskyn osoitteesta 0, joten
 * .alku (start.S) sijoitetaan muistin alkuun. Pino kasvaa muistin
 * lopusta alaspäin. */
OUTPUT_ARCH("riscv")
ENTRY(_start)

MEMORY
{
    RAM (rwx) : ORIGIN = 0x00000000, LENGTH = 16K
}

SECTIONS
{
    .text : {
        KEEP(*(.alku))
        *(.text .text.*)
    } > RAM

    .rodata : ALIGN(4) {
        *(.rodata .rodata.* .srodata .srodata.*)
    } > RAM

    .data : ALIGN(4) {
        *(.data .data.* .sdata .sdata.*)
    } > RAM

    .bss (NOLOAD) : ALIGN(4) {
        _bss_alku = .;
        *(.bss .bss.* .sbss .sbss.* COMMON)
        . = ALIGN(4);
        _bss_loppu = .;
    } > RAM

    _pino_loppu = ORIGIN(RAM) + LENGTH(RAM);
}
