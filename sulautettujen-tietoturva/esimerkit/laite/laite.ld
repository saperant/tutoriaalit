/* Käynnistin ROM-alueella. QEMU lataa ELF-segmentit suoraan
 * osoitteisiinsa, joten .data- ja .bss-osiot ovat RAMissa valmiina;
 * oikeassa laitteessa käynnistyskoodi kopioi ja nollaa ne. */
MEMORY {
    ROM (rx)  : ORIGIN = 0x00000000, LENGTH = 1M
    RAM (rwx) : ORIGIN = 0x20000000, LENGTH = 128K
}
SECTIONS {
    .text : { KEEP(*(.vektorit)) *(.text*) *(.rodata*) } > ROM
    .data : { *(.data*) } > RAM
    .bss  : { *(.bss*) *(COMMON) } > RAM
    _pino = ORIGIN(RAM) + LENGTH(RAM);
}
