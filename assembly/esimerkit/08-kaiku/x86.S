# Kaiku isoilla kirjaimilla ilman C-kirjastoa: lukee syötettä 64
# tavun paloina, muuttaa ASCII-pienaakkoset isoiksi ja kirjoittaa.
    .globl _start
    .text
_start:
# @alku silmukka
1:  xor %edi, %edi              # tiedosto 0 (stdin)
    lea puskuri(%rip), %rsi
    mov $64, %edx
    xor %eax, %eax              # järjestelmäkutsu 0 = read
    syscall
    test %rax, %rax
    jle 4f                      # 0 = syöte loppui, < 0 = virhe
    mov %rax, %rdx              # write kirjoittaa luetun määrän
    xor %ecx, %ecx              # i = 0
2:  movzbl (%rsi,%rcx), %r8d
    lea -97(%r8), %r9d          # merkki - 'a'
    cmp $25, %r9d
    ja 3f                       # ei a–z (etumerkitön vertailu)
    sub $32, %r8d               # 'a' - 'A' = 32
    mov %r8b, (%rsi,%rcx)
3:  inc %rcx
    cmp %rdx, %rcx
    jb 2b
    mov $1, %edi                # tiedosto 1 (stdout)
    mov $1, %eax                # järjestelmäkutsu 1 = write
    syscall                     # (rsi ja rdx ovat jo paikallaan)
    jmp 1b
# @loppu silmukka
4:  xor %edi, %edi
    test %rax, %rax
    setl %dil                   # paluuarvo 1, jos read epäonnistui
    mov $60, %eax               # järjestelmäkutsu 60 = exit
    syscall

    .bss
puskuri:
    .space 64
    .section .note.GNU-stack,"",@progbits
