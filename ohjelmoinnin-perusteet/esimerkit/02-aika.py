"""Muuntaa sekunteina annetun keston tunneiksi, minuuteiksi ja
sekunneiksi."""

SEKUNTIA_MINUUTISSA = 60
SEKUNTIA_TUNNISSA = 60 * SEKUNTIA_MINUUTISSA

kesto = 10_000  # esim. juoksulenkin kesto sekunteina

tunnit = kesto // SEKUNTIA_TUNNISSA          # kokonaislukujako
jaljella = kesto % SEKUNTIA_TUNNISSA         # jakojäännös
minuutit = jaljella // SEKUNTIA_MINUUTISSA
sekunnit = jaljella % SEKUNTIA_MINUUTISSA

print(f"{kesto} s = {tunnit} h {minuutit} min {sekunnit} s")
print(f"Kellona: {tunnit}:{minuutit:02d}:{sekunnit:02d}")
print(f"Tunteina: {kesto / SEKUNTIA_TUNNISSA:.2f} h")
print(type(kesto), type(kesto / SEKUNTIA_TUNNISSA))
