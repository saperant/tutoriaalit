#!/usr/bin/env bats
# Hinnoittelukirjaston yksikkötestit. Aja: bats hinta.bats

setup() {
    load hinta.sh
}

@test "euroiksi muotoilee sentit kahdella desimaalilla" {
    [ "$(euroiksi 1234)" = "12,34" ]
    [ "$(euroiksi 5)" = "0,05" ]
    [ "$(euroiksi -250)" = "-2,50" ]
}

@test "senteiksi hyväksyy pilkun, pisteen ja kokonaisluvun" {
    [ "$(senteiksi 12,34)" = 1234 ]
    [ "$(senteiksi 12.5)" = 1250 ]
    [ "$(senteiksi 08)" = 800 ]
}

@test "senteiksi hylkää virheellisen syötteen" {
    run senteiksi 12,345
    [ "$status" -eq 1 ]
    [ "$output" = "virheellinen summa: 12,345" ]
}

@test "alennus pyöristää lähimpään senttiin" {
    run alennus 999 15
    [ "$status" -eq 0 ]
    [ "$output" = 849 ]
}
