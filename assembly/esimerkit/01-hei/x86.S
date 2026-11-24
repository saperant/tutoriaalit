# Ensimmäinen ohjelma x86-64:llä ilman C-kirjastoa: tulostetaan rivi
# järjestelmäkutsulla write ja lopetetaan kutsulla exit.
# @alku ohjelma
    .globl _start
    .text
_start:
    mov $1, %edi                # 1. argumentti: tiedosto 1 (stdout)
    lea viesti(%rip), %rsi      # 2. argumentti: puskurin osoite
    mov $pituus, %edx           # 3. argumentti: tavujen määrä
    mov $1, %eax                # järjestelmäkutsu 1 = write
    syscall
    xor %edi, %edi              # paluuarvo 0
    mov $60, %eax               # järjestelmäkutsu 60 = exit
    syscall

    .section .rodata
viesti:
    .ascii "Hei, konekieli!\n"
    .set pituus, . - viesti
# @loppu ohjelma
    .section .note.GNU-stack,"",@progbits
