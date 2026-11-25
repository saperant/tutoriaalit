# Lopuksi {.runko-lahteet}

Tutoriaali kävi läpi ohjelmistoprojektin hallinnan ytimen: vaatimukset,
prosessimallit, arvioinnin ja ennustamisen, virtauksen, riskit ja
teknisen velan sekä ihmisten välisen työn. Yhteinen lanka oli
epävarmuus. Hyvä projektinhallinta ei poista sitä vaan tekee sen
näkyväksi ja pitää päätökset niin pieninä ja palautteen niin tiheänä,
että väärä suunta huomataan ajoissa.

## Nyrkkisäännöt

1. **Arvio on jakauma.** Todennäköisimpien kestojen summa ei ole
   todennäköinen kesto. Kerro väli ja varmuustaso.
2. **Arvio, tavoite ja sitoumus ovat eri asioita.** Arvioi ensin,
   sitoudu sitten.
3. **Hae palautetta niin usein kuin se on halpaa, ja tee siitä
   halvempaa.** Erän koko on taloudellinen valinta.
4. **Riskialtein asia ensin.** Epävarmuus pienenee tekemällä, ei
   odottamalla.
5. **Rajaa keskeneräistä työtä.** Läpimenoaika on keskeneräinen työ
   jaettuna läpäisyllä.
6. **Älä tavoittele täyttä käyttöastetta.** Jonot kasvavat jyrkästi,
   kun kuormitus lähestyy täyttä.
7. **Vahvista pullonkaulaa.** Muualla tehty parannus lisää vain
   keskeneräistä työtä.
8. **Ennusta historiasta ja testaa ennusteesi.** Oma läpäisy on paras
   vertailuluokka niin kauan kuin tiimi ja työ pysyvät samanlaisina.
9. **Velka on päätös, jolla on korko.** Kirjaa se ja maksa
   korkeakorkoisin ensin.
10. **Valmiin määritelmästä ei tingitä.** Kiireessä karsitaan laajuutta.
11. **Lisää väkeä ajoissa tai älä lainkaan.**
12. **Huonot uutiset heti.** Ne ovat halvimmillaan tuoreina, ja ne
    saadaan kuulla vain, jos niiden kertominen on turvallista.
13. **Mittarit ovat tiimin työkaluja.** Tavoitteeksi muutettu mittari
    lakkaa mittaamasta.

## Mallien rajat

Tutoriaalin simulaatiot ovat tarkoituksella pieniä. Niiden parametrit
(vaihtohäviö, väärinymmärrysten osuus, velan korko, perehdytysaika) on
valittu havainnollisiksi, eikä niistä saatuja lukuja pidä siirtää omaan
projektiin. Mallien arvo on mekanismeissa: ne näyttävät, miksi sääntö
pätee ja milloin se lakkaa pätemästä. WIP-raja lyhentää läpimenoaikaa,
jos rinnakkaisuus maksaa. Pieni erä kannattaa, jos palaute on halpaa.
Kappalemäärä riittää ennusteeseen, jos työt ovat samankokoisia.

Omassa projektissa mallit korvataan mittauksilla. Läpäisy,
läpimenoajat ja arvioiden osuvuus saadaan omasta historiasta, ja
tutoriaalin esimerkkiohjelmat toimivat sellaisinaan, kun niihin
vaihdetaan oma aineisto.

Menetelmiin kannattaa suhtautua samoin. Scrum, Kanban ja muut ovat
kokemuksesta tiivistettyjä ratkaisuja tiettyihin ongelmiin. Ne toimivat,
kun ongelma on sama, ja niiden soveltaminen ilman ymmärrystä siitä,
mitä ne ratkaisevat, tuottaa rituaaleja. Alan kirjallisuudessa on
vähän kontrolloituja kokeita ja paljon kokemusta ja mielipiteitä, joten
omat mittaukset ja kokeilut ovat usein paras käytettävissä oleva näyttö.

## Mihin tästä jatketaan

- *Testivetoinen kehitys ja testisuunnittelu* tekee
  hyväksymiskriteereistä suoritettavia ja käsittelee testauksen
  tekniikat.
- *Jatkuva integraatio ja toimitus* laskee palautekierroksen hintaa:
  toimitusputki, julkaisustrategiat ja toimituskyvyn mittarit.
- *Tekninen dokumentaatio* käsittelee arkkitehtuurikuvaukset ja
  päätöslokit.
- *Tiimit ja organisaatiomallit* jatkaa organisaation tasolle: Conwayn
  laki, tiimityypit ja skaalausmallit.
- *Tietoturva kehitystyössä* tuo tietoturvan osaksi samaa prosessia.

## Lähteet

Alkuperäislähteet ja alan perusteokset aiheittain. Verkossa vapaasti
luettavat on merkitty.

**Prosessimallit ja ketterä kehitys**

- Royce, W. W. (1970). *Managing the Development of Large Software
  Systems*. Proceedings of IEEE WESCON. Artikkeli, johon vesiputousmalli
  yhdistetään.
- Boehm, B. W. (1988). *A Spiral Model of Software Development and
  Enhancement*. IEEE Computer 21(5).
- Larman, C. & Basili, V. R. (2003). *Iterative and Incremental
  Development: A Brief History*. IEEE Computer 36(6).
- Beck, K. ym. (2001). *Manifesto for Agile Software Development*.
  Luettavissa osoitteessa agilemanifesto.org, myös suomeksi.
- Schwaber, K. & Sutherland, J. (2020). *The Scrum Guide*. Luettavissa
  osoitteessa scrumguides.org, myös suomeksi.
- Beck, K. & Andres, C. (2004). *Extreme Programming Explained: Embrace
  Change*, 2. painos. Addison-Wesley.
- Anderson, D. J. (2010). *Kanban: Successful Evolutionary Change for
  Your Technology Business*. Blue Hole Press.
- Poppendieck, M. & Poppendieck, T. (2003). *Lean Software Development:
  An Agile Toolkit*. Addison-Wesley.

**Vaatimukset**

- Cohn, M. (2004). *User Stories Applied: For Agile Software
  Development*. Addison-Wesley.
- Patton, J. (2014). *User Story Mapping*. O'Reilly.
- ISO/IEC 25010. *Systems and software Quality Requirements and
  Evaluation (SQuaRE) – Product quality model*.
- ISO/IEC/IEEE 29148. *Systems and software engineering – Life cycle
  processes – Requirements engineering*.

**Arviointi ja ennustaminen**

- Brooks, F. P. (1995). *The Mythical Man-Month: Essays on Software
  Engineering*, juhlapainos. Addison-Wesley. Alkuperäinen 1975.
- Boehm, B. W. (1981). *Software Engineering Economics*. Prentice-Hall.
- McConnell, S. (2006). *Software Estimation: Demystifying the Black
  Art*. Microsoft Press. Arvio, tavoite ja sitoumus; epävarmuuskartio.
- Cohn, M. (2005). *Agile Estimating and Planning*. Prentice Hall.
- Kahneman, D. (2011). *Thinking, Fast and Slow*. Farrar, Straus and
  Giroux. Suunnitteluharha ja ulkopuolinen näkökulma.
- Flyvbjerg, B. & Gardner, D. (2023). *How Big Things Get Done*.
  Currency. Vertailuluokat.
- Vacanti, D. S. (2015). *Actionable Agile Metrics for Predictability:
  An Introduction*.
- Duarte, V. (2015). *NoEstimates: How to Measure Project Progress
  Without Estimating*.
- Hofstadter, D. R. (1979). *Gödel, Escher, Bach: An Eternal Golden
  Braid*. Basic Books.

**Virtaus**

- Reinertsen, D. G. (2009). *The Principles of Product Development
  Flow: Second Generation Lean Product Development*. Celeritas.
- Goldratt, E. M. & Cox, J. (1984). *The Goal: A Process of Ongoing
  Improvement*. North River Press. Rajoitteiden teoria.
- Goldratt, E. M. (1997). *Critical Chain*. North River Press.
- Little, J. D. C. (1961). *A Proof for the Queuing Formula: L = λW*.
  Operations Research 9(3).
- Weinberg, G. M. (1992). *Quality Software Management, Volume 1:
  Systems Thinking*. Dorset House. Tehtävien vaihdon hinta.
- Forsgren, N., Humble, J. & Kim, G. (2018). *Accelerate: The Science
  of Lean Software and DevOps*. IT Revolution.

**Riskit, velka ja laatu**

- DeMarco, T. & Lister, T. (2003). *Waltzing with Bears: Managing Risk
  on Software Projects*. Dorset House.
- Klein, G. (2007). *Performing a Project Premortem*. Harvard Business
  Review 85(9).
- Cunningham, W. (1992). *The WyCash Portfolio Management System*.
  OOPSLA '92 Experience Report. Teknisen velan vertauksen alkuperä.
- Fowler, M. (2009). *Technical Debt Quadrant*. Luettavissa
  osoitteessa martinfowler.com.
- Crosby, P. B. (1979). *Quality Is Free*. McGraw-Hill.

**Ihmiset ja tiimit**

- DeMarco, T. & Lister, T. (2013). *Peopleware: Productive Projects and
  Teams*, 3. painos. Addison-Wesley. Alkuperäinen 1987.
- Edmondson, A. (1999). *Psychological Safety and Learning Behavior in
  Work Teams*. Administrative Science Quarterly 44(2).
- Derby, E. & Larsen, D. (2006). *Agile Retrospectives: Making Good
  Teams Great*. Pragmatic Bookshelf.
- Kerth, N. L. (2001). *Project Retrospectives: A Handbook for Team
  Reviews*. Dorset House.

**Sopimukset ja hankinnat** (tarkista voimassa oleva versio)

- JIT 2015: Julkisen hallinnon IT-hankintojen yleiset sopimusehdot.
- IT-alan yleiset sopimusehdot (IT2018 ja sitä uudemmat).
- Laki julkisista hankinnoista ja käyttöoikeussopimuksista (1397/2016).

**Työkalut**

- Pythonin moduulit `random` ja `statistics`: docs.python.org.
- Gitin komento `git log` muotoiluvalitsimineen: git-scm.com.
