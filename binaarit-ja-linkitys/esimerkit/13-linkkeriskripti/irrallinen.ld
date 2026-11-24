/* @alku oma */
/* Kokonainen skripti ohjelmalle ilman C-kirjastoa: muistikartta ja
   aloituskohta määrätään itse, kuten sulautetuissa järjestelmissä. */
ENTRY(_start)
SECTIONS
{
  . = 0x400000;
  .text   : { *(.text .text.*) }
  .rodata : { *(.rodata .rodata.*) }
  . = ALIGN(4096);
  .data   : { *(.data .data.*) }
  .bss    : { __bss_alku = .; *(.bss .bss.*) *(COMMON) __bss_loppu = .; }
  /DISCARD/ : { *(.comment) *(.note.*) *(.eh_frame*) }
}
/* @loppu oma */
