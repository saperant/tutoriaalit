"""Lukee lämpötilan Celsius-asteina ja tulostaa sen Fahrenheit-asteina."""

teksti = input("Lämpötila (°C): ")
celsius = float(teksti.replace(",", "."))   # hyväksyy myös 21,5
fahrenheit = celsius * 9 / 5 + 32

print()
print(f"{celsius:.1f} °C on {fahrenheit:.1f} °F")
if celsius < 0:
    print("Pakkasta: liukkaat kelit mahdollisia.")
