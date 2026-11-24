/* Osiot: koodi ja vakiot flashissa, muuttujat ja pino RAMissa. */
SECTIONS
{
    .text :
    {
        KEEP(*(.vektorit))      /* vektoritaulu osoitteeseen 0 */
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
