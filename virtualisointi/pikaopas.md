---
title: Virtualisointi
subtitle: Pikaopas · QEMU/KVM · nimiavaruudet · cgroups v2 · Linux
---

# Käsitteet

| Käsite | Merkitys |
|--------|----------|
| Hypervisor (VMM) | jakaa koneen virtuaalikoneille; tyyppi 1 raudalla, tyyppi 2 isäntä-käyttöjärjestelmän päällä |
| Sensitiivinen käsky | lukee tai muuttaa hypervisorin tilaa; virtualisoitavissa, jos kaikki ovat etuoikeutettuja |
| VM exit | vieras pysähtyy, hypervisor käsittelee syyn (~1000 kellojaksoa + käsittelijä) |
| VMCS / VMCB | vieraan ja isännän tila sekä exit-säännöt (Intel / AMD) |
| EPT / NPT | laitteiston GPA → HPA -taulu; kävely $(n+1)(m+1)-1$ viittausta |
| virtio | paravirtualisoitu laite; virtqueue: kuvaajat, avail- ja used-rengas |
| IOMMU (VT-d) | laitteiden DMA-osoitteiden käännös ja suojaus läpiviennissä |
| Kontti | prosessi + nimiavaruudet + cgroups + kyvyt + seccomp + LSM + overlay |

# QEMU ja levykuvat

| Tehtävä | Komento |
|---------|---------|
| Käynnistys KVM:llä | `qemu-system-x86_64 -accel kvm -cpu host -m 4G -smp 4 …` |
| Ilman näyttöä | `-display none -serial stdio -monitor none` |
| Levy ja verkko | `-drive file=k.qcow2,if=virtio`, `-nic user,model=virtio-net-pci` |
| Hallinta | `-qmp unix:/run/vm.sock,server=on,wait=off` |
| Pysäytettynä | `-S`, QMP: `cont`, `stop`, `query-status` |
| Kerros | `qemu-img create -f qcow2 -b perus.qcow2 -F qcow2 k.qcow2` |
| Tiedot | `qemu-img info --backing-chain k.qcow2`, `qemu-img map k.qcow2` |
| Vedokset | `qemu-img snapshot -c/-l/-a/-d nimi k.qcow2` |
| Yhdistä | `qemu-img commit k.qcow2`, `qemu-img convert -O raw` |
| Siirto | lähde QMP `migrate uri=tcp:kohde:4444`, kohde `-incoming tcp:0:4444` |
| libvirt | `virsh list`, `virsh start/shutdown/migrate`, `virsh dumpxml` |

# KVM-rajapinta

| Vaihe | Kutsu |
|-------|-------|
| Avaa | `open("/dev/kvm")`, `KVM_GET_API_VERSION` |
| Kone | `KVM_CREATE_VM`, `KVM_SET_USER_MEMORY_REGION` |
| vCPU | `KVM_CREATE_VCPU`, `mmap(kvm_run)`, `KVM_SET_SREGS/REGS` |
| Silmukka | `KVM_RUN` → `exit_reason`: `KVM_EXIT_IO`, `_MMIO`, `_HLT` |

# Nimiavaruudet

| Komento | Tehtävä |
|---------|---------|
| `unshare --uts --pid --fork --mount-proc --net --ipc cmd` | uudet nimiavaruudet |
| `unshare --mount --propagation private` | liitokset eivät vuoda |
| `unshare --user --map-root-user` | root vain nimiavaruudessa |
| `unshare --root=hak` / `pivot_root` | uusi juuri |
| `nsenter --target PID --net --mount cmd` | liity olemassa oleviin |
| `ls -l /proc/PID/ns/`, `lsns` | prosessin nimiavaruudet |
| `mount -t overlay overlay -o lowerdir=a,upperdir=y,workdir=t juuri` | kerroksellinen juuri |

# cgroups v2

| Tiedosto | Esimerkki |
|----------|-----------|
| `cgroup.procs` | `echo $$ > /sys/fs/cgroup/r/cgroup.procs` |
| `cgroup.subtree_control` | `echo +memory +cpu +pids > …` |
| `memory.max`, `memory.high` | `512M`; ylitys → OOM-tappaja |
| `cpu.max` | `"50000 100000"` = puolikas ydin |
| `pids.max` | `100`; ylitys → `fork` palauttaa `EAGAIN` |
| `io.max` | `"8:0 rbps=10485760"` |

# Kyvyt ja seccomp

- `capsh --print`, `getpcaps PID`, `grep Cap /proc/PID/status`.
- Pudota: `capsh --drop=cap_chown --`, Docker `--cap-drop=ALL
  --cap-add=NET_BIND_SERVICE`.
- Ambient: `setpriv --inh-caps=+net_bind_service
  --ambient-caps=+net_bind_service cmd`.
- seccomp: `prctl(PR_SET_NO_NEW_PRIVS)` + BPF-suodatin; tarkista aina
  `seccomp_data.arch`; toiminnot `ALLOW`, `ERRNO`, `KILL_PROCESS`.
- Kubernetes: `securityContext.seccompProfile: RuntimeDefault`,
  `capabilities.drop: [ALL]`, `runAsNonRoot: true`.

# Eristyksen tasot

| Taso | Raja | Käynnistys |
|------|------|------------|
| Kontti | isännän ydin | ~10 ms |
| gVisor | käyttäjätilan ydin | ~100 ms |
| Mikro-VM (Firecracker, Kata) | hypervisor, muutama virtio-laite | ~125 ms |
| Virtuaalikone | hypervisor, koko PC | sekunteja |

# Sudenkuopat

- `--privileged` ja `CAP_SYS_ADMIN` kumoavat kontin eristyksen.
- PID 1 ei saa signaaleja ilman käsittelijää: `--init` tai `tini`.
- Läpivienti ilman IOMMU:ta ei ole eristystä.
- Siirto vaatii saman koneversion, suoritinmallin ja laitteet.
- qcow2-vedos samassa tiedostossa ei ole varmuuskopio.
- Peruskuvaan ei kirjoiteta, kun sen päällä on kerroksia.
