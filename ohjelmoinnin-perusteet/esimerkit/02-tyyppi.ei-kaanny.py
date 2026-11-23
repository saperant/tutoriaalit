"""Merkkijono ja luku eivät summaudu."""

ika_teksti = "41"                    # input() palauttaa aina merkkijonon
ensi_vuonna = ika_teksti + 1         # @virhe
ensi_vuonna = int(ika_teksti) + 1    # muunnos ensin
print(f"Ensi vuonna olet {ensi_vuonna}-vuotias.")
