# U-Bootin käynnistysskripti. Käännetään U-Bootin luettavaan muotoon:
#   mkimage -A arm64 -T script -C none -d boot.cmd boot.scr
setenv bootargs "console=ttyAMA0 loglevel=1 panic=-1 kaynnistys=skripti"
load virtio 0:1 ${kernel_addr_r} /Image
load virtio 0:1 ${ramdisk_addr_r} /initramfs.cpio.gz
booti ${kernel_addr_r} ${ramdisk_addr_r}:${filesize} ${fdtcontroladdr}
