#ifndef LOKI_H
#define LOKI_H

// Kirjoittaa lokirivin. Sovellus voi korvata kohteen määrittelemällä
// oman loki_kohde-funktion.
void loki(const char *viesti);
void loki_kohde(const char *rivi);

#endif
