/* LT-100:n sovellus: flashissa otsakkeen (0x10000) jälkeen, ennen
 * asetuslohkoa (0x3F000). Alustettujen muuttujien alkuarvot ovat
 * flashissa, ja käynnistyskoodi kopioi ne RAMiin (ks. kaynnistys.c). */

ENTRY(Reset_Handler)

MEMORY
{
    FLASH (rx)  : ORIGIN = 0x00010100, LENGTH = 0x2EF00
    RAM   (rwx) : ORIGIN = 0x20000000, LENGTH = 64K
}

PINON_KOKO = 4K;

SECTIONS
{
    .text :
    {
        KEEP(*(.vektorit))      /* vektoritaulu alkuun */
        *(.text*)
        *(.rodata*)
        . = ALIGN(4);
    } > FLASH

    .data :
    {
        _data_alku = .;         /* ajonaikainen osoite (VMA) RAMissa */
        *(.data*)
        . = ALIGN(4);
        _data_loppu = .;
    } > RAM AT> FLASH           /* latausosoite (LMA) flashissa */
    _data_lataus = LOADADDR(.data);

    .bss (NOLOAD) :
    {
        _bss_alku = .;
        *(.bss*)
        *(COMMON)
        . = ALIGN(4);
        _bss_loppu = .;
    } > RAM

    /* Ei nollata eikä alusteta: säilyy ohjelmallisen resetin yli. */
    .noinit (NOLOAD) :
    {
        *(.noinit*)
    } > RAM

    .pino (NOLOAD) :
    {
        . = ALIGN(8);
        _pinon_pohja = .;
        . += PINON_KOKO;
        _pinon_huippu = .;      /* pino kasvaa alaspäin */
    } > RAM
}
