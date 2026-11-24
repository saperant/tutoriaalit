// Vulkan-laitteen tiedot: jonoperheet ja muistityypit. Sama ohjelma
// kertoo oikeasta näytönohjaimesta saman, mutta luvut ovat toiset.
#include <print>
#include <string>
#include <vector>

#include "vk.hpp"

// @alku liput
static std::string jonon_kyvyt(VkQueueFlags liput) {
    std::string s;
    if (liput & VK_QUEUE_GRAPHICS_BIT) s += " grafiikka";
    if (liput & VK_QUEUE_COMPUTE_BIT) s += " laskenta";
    if (liput & VK_QUEUE_TRANSFER_BIT) s += " siirto";
    if (liput & VK_QUEUE_SPARSE_BINDING_BIT) s += " harva";
    return s;
}

static std::string muistin_ominaisuudet(VkMemoryPropertyFlags liput) {
    std::string s;
    if (liput & VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT) s += " laitteen";
    if (liput & VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT) s += " CPU-näkyvä";
    if (liput & VK_MEMORY_PROPERTY_HOST_COHERENT_BIT) s += " koherentti";
    if (liput & VK_MEMORY_PROPERTY_HOST_CACHED_BIT) s += " välimuisti";
    return s;
}
// @loppu liput

int main() {
    // @alku paa
    VkYmparisto vk;
    VkPhysicalDeviceProperties p;
    vkGetPhysicalDeviceProperties(vk.fyysinen, &p);
    std::println("laitetyyppi: {}",
                 p.deviceType == VK_PHYSICAL_DEVICE_TYPE_CPU
                     ? "CPU (ohjelmistototeutus)"
                     : "näytönohjain");
    std::println("Vulkan {}.{}", VK_API_VERSION_MAJOR(p.apiVersion),
                 VK_API_VERSION_MINOR(p.apiVersion));

    std::uint32_t n = 0;
    vkGetPhysicalDeviceQueueFamilyProperties(vk.fyysinen, &n, nullptr);
    std::vector<VkQueueFamilyProperties> perheet(n);
    vkGetPhysicalDeviceQueueFamilyProperties(vk.fyysinen, &n,
                                             perheet.data());
    for (std::uint32_t i = 0; i < n; ++i) {
        std::println("jonoperhe {}: {} jonoa,{}", i,
                     perheet[i].queueCount,
                     jonon_kyvyt(perheet[i].queueFlags));
    }

    VkPhysicalDeviceMemoryProperties m;
    vkGetPhysicalDeviceMemoryProperties(vk.fyysinen, &m);
    for (std::uint32_t i = 0; i < m.memoryTypeCount; ++i) {
        std::println("muistityyppi {} (keko {}):{}", i,
                     m.memoryTypes[i].heapIndex,
                     muistin_ominaisuudet(m.memoryTypes[i].propertyFlags));
    }
    // @loppu paa
    Validointi::raportti();
}
