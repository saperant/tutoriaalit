# Katkaisukohdat, argumentit rekistereistä ja muistin lukeminen.
# @alku argumentit
break laske_hinta
commands
    silent
    printf "> laske_hinta(n=%d, asiakasluokka=%d)\n", $esi, $edx
    set $i = 0
    while $i < $esi
        set $r = (int *)($rdi + 12 * $i)
        printf ">   rivi %d: tuote %d, määrä %d, hinta %d\n", \
            $i, $r[0], $r[1], $r[2]
        set $i = $i + 1
    end
    continue
end
break alennus if $rsi > 10000
commands
    silent
    printf "> ehto täyttyi: alennus(%d, %ld)\n", $edi, $rsi
    continue
end
run > ohjelma.txt
# @loppu argumentit
