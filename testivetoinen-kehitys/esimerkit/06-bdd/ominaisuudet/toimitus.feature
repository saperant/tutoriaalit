# language: fi
Ominaisuus: Toimitusmaksu kassalla
  Asiakas näkee toimitusmaksun ennen tilauksen vahvistamista,
  jotta kokonaishinta ei yllätä.

  Tapaus: Kevyt tilaus lähetetään pienenä pakettina
    Oletetaan että korin arvo on 20,00 euroa
    Ja korin paino on 1,5 kg
    Kun asiakas siirtyy kassalle
    Niin toimitusmaksu on 5,90 euroa

  Tapausaihio: Ilmaisen toimituksen raja on 50 euroa
    Oletetaan että korin arvo on <arvo> euroa
    Ja korin paino on 1,5 kg
    Kun asiakas siirtyy kassalle
    Niin toimitusmaksu on <maksu> euroa

    Tapaukset:
      | arvo  | maksu |
      | 49,99 | 5,90  |
      | 50,00 | 0,00  |

  Tapaus: Rahtina kulkeva tilaus ei ole ilmainen
    Oletetaan että korin arvo on 120,00 euroa
    Ja korin paino on 14 kg
    Kun asiakas siirtyy kassalle
    Niin toimitusmaksu on 19,90 euroa

  Tapaus: Liian painavaa tilausta ei voi lähettää
    Oletetaan että korin arvo on 80,00 euroa
    Ja korin paino on 31 kg
    Kun asiakas siirtyy kassalle
    Niin asiakas näkee ilmoituksen "yli 30 kg:n lähetyksiä ei toimiteta"
