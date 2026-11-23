"""Kysyy arvosanaa 1–5, kunnes käyttäjä antaa kelvollisen."""

while True:
    vastaus = input("Arvosana (1-5): ").strip()
    if not vastaus.isdigit():
        print(f"'{vastaus}' ei ole kokonaisluku.")
        continue
    arvosana = int(vastaus)
    if 1 <= arvosana <= 5:
        break
    print(f"{arvosana} ei ole välillä 1-5.")

print(f"Kiitos! Annoit arvosanan {arvosana}.")
