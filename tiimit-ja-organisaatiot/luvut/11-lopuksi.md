# Lopuksi {.runko-lahteet}

Tutoriaali kävi läpi, miten organisaation rakenne ja ohjelmiston
rakenne kytkeytyvät toisiinsa ja mitä siitä seuraa tiimeille,
omistajuudelle, tuotantovastuulle ja päätöksenteolle. Yhteinen lanka
on johdannon ajatus: tiimiraja on rajapinta, ja organisaation
suunnittelu on sen päättämistä, mitkä muutokset saavat olla halpoja.

## Nyrkkisäännöt

1. Järjestelmän rakenne seuraa viestintärakennetta. Suunnittele ne
   yhdessä.
2. Tiimijaon hyvyys mitataan muutoksista: kuinka moni pysyy yhden
   tiimin sisällä.
3. Sykli tiimien välillä tarkoittaa, että raja on väärässä paikassa
   tai rajapinta puuttuu.
4. Luovutuksen hinta on odotus rajalla. Mittaa se ennen kuin siirrät
   ihmisiä.
5. Useimmat tiimit omistavat virran alusta tuotantoon. Muut tiimit
   ovat olemassa keventämässä niiden kuormaa.
6. Tiivis yhteistyö kahden tiimin välillä on väliaikaista. Pysyvä
   suhde on palvelusuhde.
7. Rajaa tiimin vastuut sen mukaan, mitä se pystyy pitämään
   mielessään, ei sen mukaan, mitä kalenteriin mahtuu.
8. Jokaisella osalla on yksi omistajatiimi, ja omistajuus sisältää
   tuotannon.
9. Alusta on tuote. Jos sitä käytetään vain pakosta, se on
   epäonnistunut.
10. Kehityksellä ja ylläpidolla on sama tavoite ja sama luku.
11. Päivystys mitoitetaan ihmisten, ei palvelujen mukaan.
12. Virheestä kysytään, miten järjestelmä salli sen, ei kuka sen teki.
13. Peruttava päätös tehdään lähellä työtä, ja perustelut kirjataan.
14. Riippuvuus poistetaan, jos voidaan, ja hallitaan vain, jos ei
    voida.
15. Organisaatiota muutetaan kuten koodia: pienin askelin ja mitaten.

## Mallien rajat

Tämän alan tieto on epävarmempaa kuin algoritmien tai tietoverkkojen.
Organisaatioilla ei voi tehdä kontrolloituja kokeita, joten näyttö on
korrelaatioita, tapaustutkimuksia ja kokeneiden ihmisten nyrkkisääntöjä.
Conwayn laista ja toimituskyvyn yhteydestä löyhään kytkentään on
kertynyt eniten tutkimusta. Team Topologies, skaalausmallit ja
kognitiivisen kuorman soveltaminen tiimeihin ovat perusteltuja
ajattelun välineitä, mutta eivät testattuja teorioita.

Sama varaus koskee tämän tutoriaalin esimerkkejä. Jonomallien ja
laskelmien parametrit on valittu havainnollistamaan ilmiötä. Ne
kertovat suunnan ja syyn, eivät oman organisaatiosi lukuja. Omat
luvut saa mittaamalla: Git-historiasta, työjonon aikaleimoista ja
kysymällä tiimeiltä.

Lopulta kyse on ihmisistä. Rakenne voi estää hyvän työn tai tehdä sen
mahdolliseksi, mutta se ei korvaa luottamusta, osaamista eikä selkeää
tavoitetta.

## Jatkotaidot

- *Jatkuva integraatio ja toimitus* käsittelee toimitusputken ja
  mittarit, joilla tämän tutoriaalin muutosten vaikutusta arvioidaan.
- *Tekninen dokumentaatio* opettaa kirjoittamaan ADR:t, tiimin
  rajapinnan ja arkkitehtuurikuvaukset.
- *Palveluarkkitehtuurit* käsittelee järjestelmän jakamisen tekniseltä
  puolelta, *Skaalautuvien järjestelmien suunnittelu*
  palvelutasotavoitteet ja virhebudjetin.
- *Tietoturva kehitystyössä* tuo tietoturvan samaan vastuunjakoon.

## Lähteet

**Conwayn laki ja sosiotekniset järjestelmät**

- Conway, M. E. (1968). *How Do Committees Invent?* Datamation 14(4).
- Trist, E. L. & Bamforth, K. W. (1951). *Some Social and
  Psychological Consequences of the Longwall Method of Coal-Getting*.
  Human Relations 4(1).
- MacCormack, A., Baldwin, C. & Rusnak, J. (2012). *Exploring the
  Duality between Product and Organizational Architectures: A Test of
  the ”Mirroring” Hypothesis*. Research Policy 41(8).
- Colfer, L. J. & Baldwin, C. Y. (2016). *The Mirroring Hypothesis:
  Theory, Evidence, and Exceptions*. Industrial and Corporate Change
  25(5).
- Nagappan, N., Murphy, B. & Basili, V. (2008). *The Influence of
  Organizational Structure on Software Quality: An Empirical Case
  Study*. ICSE 2008.
- Cataldo, M., Herbsleb, J. D. & Carley, K. M. (2008).
  *Socio-Technical Congruence: A Framework for Assessing the Impact of
  Technical and Work Dependencies on Software Development
  Productivity*. ESEM 2008.

**Tiimit ja tiimirakenteet**

- Skelton, M. & Pais, M. (2019). *Team Topologies: Organizing Business
  and Technology Teams for Fast Flow*. IT Revolution.
- Brooks, F. P. (1995). *The Mythical Man-Month: Essays on Software
  Engineering*, juhlapainos. Addison-Wesley. Alkuperäinen 1975.
- DeMarco, T. & Lister, T. (2013). *Peopleware: Productive Projects
  and Teams*, 3. painos. Addison-Wesley. Alkuperäinen 1987.
- Schwaber, K. & Sutherland, J. (2020). *The Scrum Guide*.
  scrumguides.org.
- Tuckman, B. W. (1965). *Developmental Sequence in Small Groups*.
  Psychological Bulletin 63(6).
- Huckman, R. S., Staats, B. R. & Upton, D. M. (2009). *Team
  Familiarity, Role Experience, and Performance: Evidence from Indian
  Software Services*. Management Science 55(1).
- Sweller, J. (1988). *Cognitive Load During Problem Solving: Effects
  on Learning*. Cognitive Science 12(2).
- Dunbar, R. I. M. (1992). *Neocortex Size as a Constraint on Group
  Size in Primates*. Journal of Human Evolution 22(6).
- Lindenfors, P., Wartel, A. & Lind, J. (2021). *”Dunbar's Number”
  Deconstructed*. Biology Letters 17(5).

**Omistajuus ja alustat**

- Bird, C., Nagappan, N., Murphy, B., Gall, H. & Devanbu, P. (2011).
  *Don't Touch My Code! Examining the Effects of Ownership on Software
  Quality*. ESEC/FSE 2011.
- Fowler, M. (2006). *CodeOwnership*. Julkaistu sivustolla
  martinfowler.com.
- Avelino, G., Passos, L., Hora, A. & Valente, M. T. (2016). *A Novel
  Approach for Estimating Truck Factors*. ICPC 2016.
- Vogels, W. (2006). *A Conversation with Werner Vogels*. ACM Queue
  4(4). Periaatteen ”you build it, you run it” lähde.

**DevOps, SRE ja kulttuuri**

- Allspaw, J. & Hammond, P. (2009). *10+ Deploys Per Day: Dev and Ops
  Cooperation at Flickr*. Esitys Velocity-konferenssissa.
- Skelton, M. & Pais, M. *DevOps Topologies*. Verkossa julkaistu
  luettelo vastuunjaon malleista; ensimmäinen versio 2013.
- Forsgren, N., Humble, J. & Kim, G. (2018). *Accelerate: The Science
  of Lean Software and DevOps*. IT Revolution.
- Beyer, B., Jones, C., Petoff, J. & Murphy, N. R. (toim.) (2016).
  *Site Reliability Engineering: How Google Runs Production Systems*.
  O'Reilly. Luettavissa verkossa osoitteessa sre.google.
- Allspaw, J. (2012). *Blameless PostMortems and a Just Culture*.
  Etsyn blogi Code as Craft.
- Dekker, S. (2012). *Just Culture*, 2. painos. Ashgate.
- Westrum, R. (2004). *A Typology of Organisational Cultures*. Quality
  and Safety in Health Care 13(suppl 2).

**Päätöksenteko ja arkkitehtuurityö**

- Nygard, M. (2011). *Documenting Architecture Decisions*.
  Blogikirjoitus, josta ADR-muoto on peräisin.
- Laloux, F. (2014). *Reinventing Organizations*. Nelson Parker.
- Harmel-Law, A. (2021). *Scaling the Practice of Architecture,
  Conversationally*. Julkaistu sivustolla martinfowler.com.
- Hohpe, G. (2020). *The Software Architect Elevator*. O'Reilly.
- Wenger, E. (1998). *Communities of Practice: Learning, Meaning, and
  Identity*. Cambridge University Press.

**Skaalausmallit**

- Sutherland, J. (2001). *Agile Can Scale: Inventing and Reinventing
  SCRUM in Five Companies*. Cutter IT Journal 14(12).
- Scaled Agile, Inc. *SAFe*. Kuvaus: scaledagileframework.com.
- Larman, C. & Vodde, B. (2016). *Large-Scale Scrum: More with LeSS*.
  Addison-Wesley.
- Kniberg, H. & Ivarsson, A. (2012). *Scaling Agile @ Spotify with
  Tribes, Squads, Chapters & Guilds*.
- Dikert, K., Paasivaara, M. & Lassenius, C. (2016). *Challenges and
  Success Factors for Large-Scale Agile Transformations: A Systematic
  Literature Review*. Journal of Systems and Software 119.

**Hajautettu työ**

- Allen, T. J. (1977). *Managing the Flow of Technology*. MIT Press.
- Herbsleb, J. D. & Mockus, A. (2003). *An Empirical Study of Speed
  and Communication in Globally Distributed Software Development*.
  IEEE Transactions on Software Engineering 29(6).
