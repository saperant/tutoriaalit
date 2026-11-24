/* Vieras ladataan 1 MiB:n osoitteeseen, kuten Multiboot edellyttää. */
ENTRY(_start)
SECTIONS {
    . = 1M;
    .text   : { *(.multiboot) *(.text*) }
    .rodata : { *(.rodata*) }
    .data   : { *(.data*) }
    .bss    : { *(.bss*) *(COMMON) }
}
