/* LT-100:n käynnistyslatain: flashin ensimmäiset 64 kt.
 *
 * Koodi ja vakiot ovat flashissa (FLASH), muuttujat ja pino RAMissa.
 * Alustettujen muuttujien alkuarvot tallennetaan flashiin, ja
 * käynnistyskoodi kopioi ne RAMiin (ks. boot.c). */

ENTRY(Reset_Handler)

MEMORY
{
    FLASH (rx)  : ORIGIN = 0x00000000, LENGTH = 64K
    RAM   (rwx) : ORIGIN = 0x20000000, LENGTH = 64K
}

PINON_KOKO = 4K;

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
