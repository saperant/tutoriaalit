# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. **VM exit on virtualisoinnin hinta.** Suorituskyky on sitä, kuinka
   harvoin vieras pysähtyy. Erät, paravirtualisointi ja laitteistotuki
   ovat kaikki tapoja vähentää pysähdyksiä.
2. **Kontti on prosessi.** Sen raja on isännän ydin, ja sen
   suorituskyky on natiivi. Eristys tulee kerroksista: nimiavaruudet,
   cgroups, kyvyt, seccomp ja LSM.
3. **Valitse raja uhkamallin mukaan.** Luotetulle koodille kontit,
   vieraalle koodille mikro-VM tai gVisor, eri ytimille ja vahvalle
   erottelulle virtuaalikone.
4. **virtio oletuksena, läpivienti nopeuden vuoksi.** Emuloidut
   laitteet ovat yhteensopivuutta varten, ja jokainen niistä on
   hyökkäyspintaa.
5. **Suuret sivut ja yhteinen suoritinmalli.** Ensimmäinen lyhentää
   kaksiulotteista sivutaulukävelyä, jälkimmäinen mahdollistaa siirron.
6. **Rajat aina.** Muisti-, CPU- ja prosessirajat jokaiselle kontille
   ja koneelle. Yksi karannut kuorma ei saa kaataa isäntää.
7. **Ei `--privileged`-kontteja tuotannossa.** Ne kumoavat kaiken
   eristyksen. Anna vain tarvittavat kyvyt.
8. **Peruskuvat vain luettaviksi.** Sekä qcow2-peruskuvat että
   konttikuvat jaetaan monen koneen kesken, ja muutokset kuuluvat
   kerroksiin.
9. **Vedos ei ole varmuuskopio.** Varmuuskopio on toisessa paikassa ja
   sen palautus on testattu.

## Mihin tästä eteenpäin

- *Kontit ja pilvi*: Docker, konttikuvien rakentaminen ja Kubernetes.
- *Palvelinympäristöt*: virtualisointialustojen ylläpito, tallennus ja
  varmuuskopiointi.
- *Käyttöjärjestelmät* ja *Tietokonearkkitehtuuri*: virtuaalimuisti,
  keskeytykset ja suojaustasot tämän luvun pohjana.
- *Tietoverkot*: verkkonimiavaruudet, sillat ja veth-parit, joilla
  konttien verkot rakennetaan.
- *Palveluarkkitehtuurin tietoturva*: eristys osana pilvipalvelun
  tietoturvaa.

## Lähteet ja lisämateriaali

### Perusteokset ja määrittelyt

- Popek, G. J. & Goldberg, R. P. (1974). *Formal Requirements for
  Virtualizable Third Generation Architectures*. Communications of the
  ACM 17(7).
- Adams, K. & Agesen, O. (2006). *A Comparison of Software and Hardware
  Techniques for x86 Virtualization*. ASPLOS.
- Intel. *Intel 64 and IA-32 Architectures Software Developer's
  Manual*, Volume 3C: VMX.
- AMD. *AMD64 Architecture Programmer's Manual*, Volume 2: Secure
  Virtual Machine.
- OASIS. *Virtual I/O Device (VIRTIO) Version 1.3*.
- Agache, A. ym. (2020). *Firecracker: Lightweight Virtualization for
  Serverless Applications*. NSDI.

### Dokumentaatio

- Linuxin ytimen dokumentaatio: *KVM API* (`Documentation/virt/kvm/api.rst`),
  *Control Group v2* (`Documentation/admin-guide/cgroup-v2.rst`) ja
  *Seccomp BPF* (`Documentation/userspace-api/seccomp_filter.rst`).
- Linuxin man-sivut: `namespaces(7)`, `cgroups(7)`,
  `capabilities(7)`, `seccomp(2)`, `unshare(1)`, `nsenter(1)`.
- QEMU-dokumentaatio: <https://www.qemu.org/docs/master/>, erityisesti
  QMP-viitteet, `qemu-img` ja siirto.
- Open Container Initiative: *Runtime Specification* ja *Image
  Specification*.
- LWN.net: *Using the KVM API* (2015) ja *Namespaces in operation*
  -artikkelisarja.

### Työkalut

- QEMU, libvirt, Firecracker, Cloud Hypervisor, Kata Containers,
  gVisor, runc, crun, CRIU.

## Lisenssi

Tämä teos on lisensoitu Creative Commons Nimeä–JaaSamoin 4.0
Kansainvälinen -lisenssillä (CC BY-SA 4.0). Esimerkkien koodia saa
käyttää samoin ehdoin.
