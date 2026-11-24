# Lineaarialgebra

Tiivis suomenkielinen lineaarialgebran tutoriaali ohjelmoijalle ja
insinöörille: vektorit, matriisit ja lineaarikuvaukset, yhtälöryhmät,
LU-hajotelma, determinantti ja käänteismatriisi, kanta ja kannanvaihto,
ortogonaalisuus ja QR, pienimmän neliösumman sovitus, ominaisarvot,
homogeeniset koordinaatit sekä numeerinen luotettavuus. Jokainen
menetelmä toteutetaan ensin puhtaalla Pythonilla ja tarkistetaan
NumPylla. Valmiit dokumentit:
[lineaarialgebra.pdf](https://saperant.github.io/tutoriaalit/materiaalit/lineaarialgebra.pdf)
ja pikaopas
[lineaarialgebra-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/lineaarialgebra-pikaopas.pdf).

## Sisältö

1. Johdanto – lineaarialgebra koodina, ostoskori, merkinnät
2. Vektorit – summa, normit, pistetulo, projektio, ristitulo
3. Matriisit ja lineaarikuvaukset – kierto, skaalaus, leikkaus,
   matriisitulo ja transpoosi
4. Lineaariset yhtälöryhmät – Gaussin eliminointi, aste ja
   ratkaisujen määrä
5. LU-hajotelma – yksi hajotus, monta oikeaa puolta
6. Determinantti ja käänteismatriisi – geometrinen merkitys,
   Gaussin–Jordanin menetelmä
7. Aliavaruudet, kanta ja kannanvaihto – värikoordinaatit,
   nolla-avaruus ja reaktioyhtälö
8. Ortogonaalisuus – ortogonaaliset matriisit, Gram–Schmidt, QR
9. Pienimmän neliösumman sovitus – kalibrointi, normaaliyhtälöt ja QR,
   ylisovitus
10. Ominaisarvot – potenssimenetelmä, Markovin ketju, diagonalisointi,
    pääkomponentit
11. Homogeeniset koordinaatit – siirrot, kamera ja perspektiivi
12. Numeeriset näkökohdat – kuntoluku, vakaus, tuenta
13. Lopuksi – nyrkkisäännöt, jatkotaidot, lähteet

## Rakentaminen

```text
make testaa   # rakenne, ruff, mypy --strict ja esimerkkien ajot
make pdf      # lineaarialgebra.pdf ja pikaopas
```

Esimerkit toimivat Python 3.12:lla ja uudemmilla; ne tarvitsevat
NumPyn. Tarkistukseen tarvitaan ruff ja mypy (kehityskontissa valmiina).

Lisenssi: CC BY-SA 4.0.
