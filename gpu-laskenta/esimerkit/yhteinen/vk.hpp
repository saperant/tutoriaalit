// Vulkan laskentaan ilman ikkunaa: instanssi validointikerroksineen,
// laite laskentajonolla, kertakäyttöiset komentopuskurit ja puskurit.
// Rakenne on sama kuin GPU-ohjelmoinnin tutoriaalissa, mutta jono
// valitaan laskentaa varten ja laitteen ominaisuudet tallennetaan.
#pragma once

#include <vulkan/vulkan.h>

#include <cstdint>
#include <cstring>
#include <format>
#include <print>
#include <span>
#include <stdexcept>
#include <string>
#include <vector>

inline void tarkista(VkResult tulos, const char* mita) {
    if (tulos != VK_SUCCESS) {
        throw std::runtime_error(
            std::format("{}: VkResult {}", mita, static_cast<int>(tulos)));
    }
}

// Validointikerroksen varoitukset ja virheet. Esimerkin on päätyttävä
// ilman yhtään ilmoitusta; synkronointiesimerkki lukee tunnisteet.
struct Validointi {
    static inline std::vector<std::string> tunnisteet;
    static inline std::vector<std::string> viestit;

    // Tulostaa ilmoitusten määrän ja palauttaa ohjelman paluuarvon.
    static int raportti() {
        std::println("validointi-ilmoituksia: {}", tunnisteet.size());
        for (const auto& v : viestit) {
            std::println(stderr, "validointi: {}", v);
        }
        return tunnisteet.empty() ? 0 : 1;
    }
    static void tyhjenna() {
        tunnisteet.clear();
        viestit.clear();
    }
};

inline VKAPI_ATTR VkBool32 VKAPI_CALL validointiviesti(
    VkDebugUtilsMessageSeverityFlagBitsEXT vakavuus,
    VkDebugUtilsMessageTypeFlagsEXT,
    const VkDebugUtilsMessengerCallbackDataEXT* tiedot, void*) {
    if (vakavuus >= VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT) {
        Validointi::tunnisteet.emplace_back(
            tiedot->pMessageIdName ? tiedot->pMessageIdName : "?");
        Validointi::viestit.emplace_back(tiedot->pMessage);
    }
    return VK_FALSE;
}

class VkYmparisto {
public:
    VkInstance instanssi = VK_NULL_HANDLE;
    VkPhysicalDevice fyysinen = VK_NULL_HANDLE;
    VkDevice laite = VK_NULL_HANDLE;
    VkQueue jono = VK_NULL_HANDLE;
    std::uint32_t perhe = 0;
    VkCommandPool allas = VK_NULL_HANDLE;
    VkPhysicalDeviceProperties ominaisuudet{};
    VkPhysicalDeviceSubgroupProperties aliryhma{};
    std::uint32_t aikaleimabitit = 0;

    // synkronointi = true ottaa käyttöön synkronoinnin validoinnin,
    // joka löytää puuttuvat esteet (hitaampi).
    explicit VkYmparisto(bool synkronointi = false) {
        luo_instanssi(synkronointi);
        valitse_laite();
        luo_laite();
        const VkCommandPoolCreateInfo ai{
            .sType = VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO,
            .flags = VK_COMMAND_POOL_CREATE_TRANSIENT_BIT,
            .queueFamilyIndex = perhe};
        tarkista(vkCreateCommandPool(laite, &ai, nullptr, &allas),
                 "vkCreateCommandPool");
    }
    ~VkYmparisto() {
        vkDestroyCommandPool(laite, allas, nullptr);
        vkDestroyDevice(laite, nullptr);
        if (viestinvalittaja_ != VK_NULL_HANDLE) {
            auto tuhoa = reinterpret_cast<
                PFN_vkDestroyDebugUtilsMessengerEXT>(vkGetInstanceProcAddr(
                instanssi, "vkDestroyDebugUtilsMessengerEXT"));
            tuhoa(instanssi, viestinvalittaja_, nullptr);
        }
        vkDestroyInstance(instanssi, nullptr);
    }
    VkYmparisto(const VkYmparisto&) = delete;
    VkYmparisto& operator=(const VkYmparisto&) = delete;

    std::uint32_t muistityyppi(std::uint32_t sallitut,
                               VkMemoryPropertyFlags halutut) const {
        VkPhysicalDeviceMemoryProperties m;
        vkGetPhysicalDeviceMemoryProperties(fyysinen, &m);
        for (std::uint32_t i = 0; i < m.memoryTypeCount; ++i) {
            if ((sallitut & (1u << i)) != 0 &&
                (m.memoryTypes[i].propertyFlags & halutut) == halutut) {
                return i;
            }
        }
        throw std::runtime_error("sopivaa muistityyppiä ei ole");
    }

    // Kertakäyttöinen komentopuskuri: aloita, tallenna komennot ja
    // suorita, jolloin CPU odottaa aidalla GPU:n valmistumista.
    VkCommandBuffer aloita() const {
        const VkCommandBufferAllocateInfo vi{
            .sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_ALLOCATE_INFO,
            .commandPool = allas,
            .level = VK_COMMAND_BUFFER_LEVEL_PRIMARY,
            .commandBufferCount = 1};
        VkCommandBuffer kp;
        tarkista(vkAllocateCommandBuffers(laite, &vi, &kp),
                 "vkAllocateCommandBuffers");
        const VkCommandBufferBeginInfo ai{
            .sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_BEGIN_INFO,
            .flags = VK_COMMAND_BUFFER_USAGE_ONE_TIME_SUBMIT_BIT};
        tarkista(vkBeginCommandBuffer(kp, &ai), "vkBeginCommandBuffer");
        return kp;
    }

    void suorita(VkCommandBuffer kp) const {
        tarkista(vkEndCommandBuffer(kp), "vkEndCommandBuffer");
        const VkFenceCreateInfo ai{
            .sType = VK_STRUCTURE_TYPE_FENCE_CREATE_INFO};
        VkFence aita;
        tarkista(vkCreateFence(laite, &ai, nullptr, &aita),
                 "vkCreateFence");
        const VkCommandBufferSubmitInfo kpi{
            .sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_SUBMIT_INFO,
            .commandBuffer = kp};
        const VkSubmitInfo2 lahetys{
            .sType = VK_STRUCTURE_TYPE_SUBMIT_INFO_2,
            .commandBufferInfoCount = 1,
            .pCommandBufferInfos = &kpi};
        tarkista(vkQueueSubmit2(jono, 1, &lahetys, aita),
                 "vkQueueSubmit2");
        tarkista(vkWaitForFences(laite, 1, &aita, VK_TRUE, UINT64_MAX),
                 "vkWaitForFences");
        vkDestroyFence(laite, aita, nullptr);
        vkFreeCommandBuffers(laite, allas, 1, &kp);
    }

private:
    VkDebugUtilsMessengerEXT viestinvalittaja_ = VK_NULL_HANDLE;

    static bool kerros_saatavilla(const char* nimi) {
        std::uint32_t n = 0;
        vkEnumerateInstanceLayerProperties(&n, nullptr);
        std::vector<VkLayerProperties> kerrokset(n);
        vkEnumerateInstanceLayerProperties(&n, kerrokset.data());
        for (const auto& k : kerrokset) {
            if (std::strcmp(k.layerName, nimi) == 0) {
                return true;
            }
        }
        return false;
    }

    void luo_instanssi(bool synkronointi) {
        const VkApplicationInfo sovellus{
            .sType = VK_STRUCTURE_TYPE_APPLICATION_INFO,
            .pApplicationName = "gpu-laskenta",
            .apiVersion = VK_API_VERSION_1_3};
        const char* kerros = "VK_LAYER_KHRONOS_validation";
        const char* laajennus = VK_EXT_DEBUG_UTILS_EXTENSION_NAME;
        const bool validoi = kerros_saatavilla(kerros);
        const VkDebugUtilsMessengerCreateInfoEXT viestit{
            .sType =
                VK_STRUCTURE_TYPE_DEBUG_UTILS_MESSENGER_CREATE_INFO_EXT,
            .messageSeverity =
                VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT |
                VK_DEBUG_UTILS_MESSAGE_SEVERITY_ERROR_BIT_EXT,
            .messageType = VK_DEBUG_UTILS_MESSAGE_TYPE_VALIDATION_BIT_EXT,
            .pfnUserCallback = validointiviesti};
        const VkValidationFeatureEnableEXT lisat[] = {
            VK_VALIDATION_FEATURE_ENABLE_SYNCHRONIZATION_VALIDATION_EXT};
        const VkValidationFeaturesEXT piirteet{
            .sType = VK_STRUCTURE_TYPE_VALIDATION_FEATURES_EXT,
            .enabledValidationFeatureCount = 1,
            .pEnabledValidationFeatures = lisat};
        const VkInstanceCreateInfo ai{
            .sType = VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
            .pNext = validoi && synkronointi ? &piirteet : nullptr,
            .pApplicationInfo = &sovellus,
            .enabledLayerCount = validoi ? 1u : 0u,
            .ppEnabledLayerNames = &kerros,
            .enabledExtensionCount = validoi ? 1u : 0u,
            .ppEnabledExtensionNames = &laajennus};
        tarkista(vkCreateInstance(&ai, nullptr, &instanssi),
                 "vkCreateInstance");
        if (validoi) {
            auto luo = reinterpret_cast<PFN_vkCreateDebugUtilsMessengerEXT>(
                vkGetInstanceProcAddr(instanssi,
                                      "vkCreateDebugUtilsMessengerEXT"));
            tarkista(luo(instanssi, &viestit, nullptr, &viestinvalittaja_),
                     "vkCreateDebugUtilsMessengerEXT");
        }
    }

    // @alku laite
    // Ensimmäinen laite ja sen ensimmäinen jonoperhe, joka osaa
    // laskennan. Aliryhmän tiedot kysytään ketjutetulla rakenteella.
    void valitse_laite() {
        std::uint32_t n = 0;
        vkEnumeratePhysicalDevices(instanssi, &n, nullptr);
        if (n == 0) {
            throw std::runtime_error("Vulkan-laitetta ei löydy");
        }
        std::vector<VkPhysicalDevice> laitteet(n);
        vkEnumeratePhysicalDevices(instanssi, &n, laitteet.data());
        fyysinen = laitteet[0];
        aliryhma.sType =
            VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_SUBGROUP_PROPERTIES;
        VkPhysicalDeviceProperties2 p2{
            .sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_PROPERTIES_2,
            .pNext = &aliryhma};
        vkGetPhysicalDeviceProperties2(fyysinen, &p2);
        ominaisuudet = p2.properties;

        std::uint32_t m = 0;
        vkGetPhysicalDeviceQueueFamilyProperties(fyysinen, &m, nullptr);
        std::vector<VkQueueFamilyProperties> perheet(m);
        vkGetPhysicalDeviceQueueFamilyProperties(fyysinen, &m,
                                                 perheet.data());
        for (std::uint32_t i = 0; i < m; ++i) {
            if ((perheet[i].queueFlags & VK_QUEUE_COMPUTE_BIT) != 0) {
                perhe = i;
                aikaleimabitit = perheet[i].timestampValidBits;
                return;
            }
        }
        throw std::runtime_error("laskentajonoa ei löydy");
    }
    // @loppu laite

    // @alku piirteet
    // Vulkan 1.3:n piirteet: synchronization2 esteisiin ja maintenance4,
    // jota työryhmän koon antaminen erikoistusvakioina edellyttää.
    void luo_laite() {
        VkPhysicalDeviceVulkan13Features v13{
            .sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_3_FEATURES,
            .synchronization2 = VK_TRUE,
            .maintenance4 = VK_TRUE};
        const float prioriteetti = 1.0f;
        const VkDeviceQueueCreateInfo jonot{
            .sType = VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO,
            .queueFamilyIndex = perhe,
            .queueCount = 1,
            .pQueuePriorities = &prioriteetti};
        const VkDeviceCreateInfo ai{
            .sType = VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO,
            .pNext = &v13,
            .queueCreateInfoCount = 1,
            .pQueueCreateInfos = &jonot};
        tarkista(vkCreateDevice(fyysinen, &ai, nullptr, &laite),
                 "vkCreateDevice");
        vkGetDeviceQueue(laite, perhe, 0, &jono);
    }
    // @loppu piirteet
};

// @alku puskuri
// Tyypitetty varastopuskuri (storage buffer). Oletuksena muisti on
// CPU:lle näkyvää ja koherenttia, ja se kuvataan pysyvästi, joten
// alkiot luetaan ja kirjoitetaan suoraan näkymän kautta. Erillisen
// näytönohjaimen omaa muistia varten on lippu laitteen_muisti.
template <typename T>
class Puskuri {
public:
    Puskuri(const VkYmparisto& vk, std::size_t n,
            bool laitteen_muisti = false)
        : laite_{vk.laite}, n_{n} {
        const VkBufferCreateInfo ai{
            .sType = VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO,
            .size = tavuja(),
            .usage = VK_BUFFER_USAGE_STORAGE_BUFFER_BIT |
                     VK_BUFFER_USAGE_TRANSFER_SRC_BIT |
                     VK_BUFFER_USAGE_TRANSFER_DST_BIT,
            .sharingMode = VK_SHARING_MODE_EXCLUSIVE};
        tarkista(vkCreateBuffer(laite_, &ai, nullptr, &puskuri),
                 "vkCreateBuffer");
        VkMemoryRequirements vaatimus;
        vkGetBufferMemoryRequirements(laite_, puskuri, &vaatimus);
        const VkMemoryPropertyFlags halutut =
            laitteen_muisti ? VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT
                            : VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT |
                                  VK_MEMORY_PROPERTY_HOST_COHERENT_BIT;
        const VkMemoryAllocateInfo mi{
            .sType = VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO,
            .allocationSize = vaatimus.size,
            .memoryTypeIndex =
                vk.muistityyppi(vaatimus.memoryTypeBits, halutut)};
        tarkista(vkAllocateMemory(laite_, &mi, nullptr, &muisti_),
                 "vkAllocateMemory");
        tarkista(vkBindBufferMemory(laite_, puskuri, muisti_, 0),
                 "vkBindBufferMemory");
        if (!laitteen_muisti) {
            void* p = nullptr;
            tarkista(vkMapMemory(laite_, muisti_, 0, VK_WHOLE_SIZE, 0, &p),
                     "vkMapMemory");
            data_ = static_cast<T*>(p);
        }
    }
    ~Puskuri() {
        vkDestroyBuffer(laite_, puskuri, nullptr);
        vkFreeMemory(laite_, muisti_, nullptr);
    }
    Puskuri(const Puskuri&) = delete;
    Puskuri& operator=(const Puskuri&) = delete;

    std::span<T> alkiot() {
        if (data_ == nullptr) {
            throw std::logic_error("puskuri ei näy CPU:lle");
        }
        return {data_, n_};
    }
    std::size_t koko() const { return n_; }
    VkDeviceSize tavuja() const { return n_ * sizeof(T); }

    VkBuffer puskuri = VK_NULL_HANDLE;

private:
    VkDevice laite_;
    std::size_t n_;
    VkDeviceMemory muisti_ = VK_NULL_HANDLE;
    T* data_ = nullptr;
};
// @loppu puskuri
