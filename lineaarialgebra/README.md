# Lineaarialgebra

Tiivis suomenkielinen lineaarialgebran tutoriaali ohjelmoijalle ja
insinöörille: vektorit, matriisit ja lineaarikuvaukset, yhtälöryhmät,
LU-hajotelma, determinantti ja käänteismatriisi, kanta ja kannanvaihto,
ortogonaalisuus ja QR, pienimmän neliösumman sovitus, ominaisarvot,
singulaariarvohajotelma, homogeeniset koordinaatit sekä numeerinen
luotettavuus. Jokainen
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
   ratkaisujen määrä, herkkyys ja ehtoluku
5. LU-hajotelma – yksi hajotus, monta oikeaa puolta
6. Determinantti ja käänteismatriisi – geometrinen merkitys,
   Gaussin–Jordanin menetelmä
7. Aliavaruudet, kanta ja kannanvaihto – värikoordinaatit,
   nolla-avaruus ja reaktioyhtälö
8. Ortogonaalisuus – ortogonaaliset matriisit, Gram–Schmidt, QR
9. Pienimmän neliösumman sovitus – kalibrointi, normaaliyhtälöt ja QR,
   projektiomatriisi, ylisovitus
10. Ominaisarvot – karakteristinen yhtälö, potenssimenetelmä, Markovin
    ketju, diagonalisointi, positiivisesti definiitit matriisit,
    pääkomponentit
11. Singulaariarvohajotelma – kierto, venytys ja kierto, aste ja
    ehtoluku, pseudoinverssi, matala-asteinen approksimaatio
12. Homogeeniset koordinaatit – siirrot, kamera ja perspektiivi
13. Numeeriset näkökohdat – ehtoluku käytännössä, stabiilisuus, tuenta
14. Lopuksi – nyrkkisäännöt, jatkotaidot, lähteet

## Rakentaminen

```text
make testaa   # rakenne, ruff, mypy --strict ja esimerkkien ajot
make pdf      # lineaarialgebra.pdf ja pikaopas
make kuvat    # piirtää kuvat uudelleen (Matplotlib)
```

Esimerkit toimivat Python 3.12:lla ja uudemmilla; ne tarvitsevat
NumPyn. Tarkistukseen tarvitaan ruff ja mypy ja kuvien piirtämiseen
Matplotlib (kehityskontissa valmiina).
Esimerkkien avaaminen kehityskontissa ja ajaminen: ks.
[Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.

Lisenssi: CC BY-SA 4.0.
