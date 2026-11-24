// Pienin mahdollinen hypervisor KVM-rajapinnalla. Vieraana on 12 tavun
// 16-bittinen ohjelma, joka laskee 2 + 2, tulostaa tuloksen porttiin
// 0x3f8 ja pysähtyy. Jokainen out-käsky aiheuttaa VM exitin, jonka
// tämä ohjelma käsittelee kuten QEMU käsittelee laitteiden I/O:n.
//
// Vaatii laitteistotuen ja oikeuden laitteeseen /dev/kvm. Esimerkkien
// Makefile ajaa ohjelman vain, jos laite on käytettävissä.
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <linux/kvm.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <unistd.h>

// @alku vieras
static const uint8_t koodi[] = {
    0xba, 0xf8, 0x03,   // mov dx, 0x3f8
    0x00, 0xd8,         // add al, bl
    0x04, '0',          // add al, '0'
    0xee,               // out dx, al
    0xb0, '\n',         // mov al, '\n'
    0xee,               // out dx, al
    0xf4,               // hlt
};
// @loppu vieras

static int virhe(const char *mita)
{
    perror(mita);
    return 1;
}

int main(void)
{
    // @alku vm
    int kvm = open("/dev/kvm", O_RDWR | O_CLOEXEC);
    if (kvm < 0)
        return virhe("/dev/kvm");
    if (ioctl(kvm, KVM_GET_API_VERSION, NULL) != KVM_API_VERSION)
        return virhe("KVM_GET_API_VERSION");
    int vm = ioctl(kvm, KVM_CREATE_VM, 0UL);
    if (vm < 0)
        return virhe("KVM_CREATE_VM");

    // Vieraan "fyysinen muisti" on tavallista prosessin muistia.
    size_t koko = 0x1000;
    uint8_t *muisti = mmap(NULL, koko, PROT_READ | PROT_WRITE,
                           MAP_SHARED | MAP_ANONYMOUS, -1, 0);
    if (muisti == MAP_FAILED)
        return virhe("mmap");
    memcpy(muisti, koodi, sizeof koodi);
    struct kvm_userspace_memory_region alue = {
        .slot = 0,
        .guest_phys_addr = 0x1000,
        .memory_size = koko,
        .userspace_addr = (uint64_t)(uintptr_t)muisti,
    };
    if (ioctl(vm, KVM_SET_USER_MEMORY_REGION, &alue) < 0)
        return virhe("KVM_SET_USER_MEMORY_REGION");
    // @loppu vm

    // @alku vcpu
    int vcpu = ioctl(vm, KVM_CREATE_VCPU, 0UL);
    int mmap_koko = ioctl(kvm, KVM_GET_VCPU_MMAP_SIZE, NULL);
    if (vcpu < 0 || mmap_koko < 0)
        return virhe("KVM_CREATE_VCPU");
    struct kvm_run *ajo = mmap(NULL, (size_t)mmap_koko,
                               PROT_READ | PROT_WRITE, MAP_SHARED,
                               vcpu, 0);
    if (ajo == MAP_FAILED)
        return virhe("mmap vcpu");

    // Reaalitila: koodisegmentti alkaa nollasta, suoritus osoitteesta
    // 0x1000. Rekisterit al = 2 ja bl = 2.
    struct kvm_sregs sregs;
    if (ioctl(vcpu, KVM_GET_SREGS, &sregs) < 0)
        return virhe("KVM_GET_SREGS");
    sregs.cs.base = 0;
    sregs.cs.selector = 0;
    if (ioctl(vcpu, KVM_SET_SREGS, &sregs) < 0)
        return virhe("KVM_SET_SREGS");
    struct kvm_regs regs = {.rip = 0x1000, .rax = 2, .rbx = 2,
                            .rflags = 0x2};
    if (ioctl(vcpu, KVM_SET_REGS, &regs) < 0)
        return virhe("KVM_SET_REGS");
    // @loppu vcpu

    // @alku silmukka
    int exiteja = 0;
    for (;;) {
        if (ioctl(vcpu, KVM_RUN, NULL) < 0)
            return virhe("KVM_RUN");
        exiteja++;
        switch (ajo->exit_reason) {
        case KVM_EXIT_IO:
            if (ajo->io.direction == KVM_EXIT_IO_OUT &&
                ajo->io.port == 0x3f8 && ajo->io.size == 1) {
                char *data = (char *)ajo + ajo->io.data_offset;
                putchar(*data);             // "emuloitu sarjaportti"
            }
            break;
        case KVM_EXIT_HLT:
            printf("KVM_EXIT_HLT %d VM exitin jälkeen\n", exiteja);
            return 0;
        default:
            fprintf(stderr, "odottamaton exit %u\n", ajo->exit_reason);
            return 1;
        }
    }
    // @loppu silmukka
}
