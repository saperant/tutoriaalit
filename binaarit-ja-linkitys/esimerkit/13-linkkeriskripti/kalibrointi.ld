/* @alku insert */
/* Lisäys oletusskriptiin: oma tulostusosio .rodata-osion jälkeen,
   sivun rajalle tasattuna, ja rajasymbolit sen ympärille. */
SECTIONS
{
  .kalibrointi : ALIGN(4096)
  {
    __kalibrointi_alku = .;
    KEEP(*(.kalibrointi))
    __kalibrointi_loppu = .;
  }
}
INSERT AFTER .rodata;

/* Skriptissä määritelty vakio: symbolin arvo, ei muuttuja. */
KALIBROINTI_VERSIO = 3;
/* @loppu insert */
