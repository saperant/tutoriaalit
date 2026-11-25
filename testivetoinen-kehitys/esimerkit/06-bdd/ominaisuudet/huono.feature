# language: fi
Ominaisuus: Toimitusmaksu

  Tapaus: Testaa toimitusmaksu
    Oletetaan että käyttäjä avaa sivun "/kori"
    Ja käyttäjä kirjoittaa kenttään "paino" arvon "1500"
    Ja käyttäjä kirjoittaa kenttään "summa" arvon "2000"
    Kun käyttäjä painaa nappia "Laske"
    Niin elementissä "#toimitus" lukee "5,90"
    Kun käyttäjä kirjoittaa kenttään "summa" arvon "5000"
    Ja käyttäjä painaa nappia "Laske"
    Niin elementissä "#toimitus" lukee "0,00"
