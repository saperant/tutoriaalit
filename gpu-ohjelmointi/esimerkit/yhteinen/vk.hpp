// Vulkan ilman ikkunaa: instanssi validointikerroksineen, laite, jono,
// komentopuskurit sekä puskurit ja kuvat muisteineen.
#pragma once

#include <vulkan/vulkan.h>

#include <array>
#include <cstdint>
#include <functional>
#include <cstring>
#include <format>
#include <fstream>
#include <print>
#include <stdexcept>
#include <string>
#include <vector>

#include "kuva.hpp"

// @alku tarkista
inline void tarkista(VkResult tulos, const char* mita) {
    if (tulos != VK_SUCCESS) {
        throw std::runtime_error(
            std::format("{}: VkResult {}", mita, static_cast<int>(tulos)));
    }
}
// @loppu tarkista

// Validointikerroksen ilmoitukset. Jokaisen esimerkin on päätyttävä
// ilman yhtään virhettä; tarkoituksellisen virheen esimerkki lukee
// ilmoitusten tunnisteet (VUID).
struct Validointi {
    static inline std::vector<std::string> tunnisteet;
    static inline std::vector<std::string> viestit;

    // Tulostaa ilmoitusten määrän; itse viestit virhetulosteeseen.
    static void raportti() {
        std::println("validointi-ilmoituksia: {}", tunnisteet.size());
        for (const auto& v : viestit) {
            std::println(stderr, "validointi: {}", v);
        }
    }
};

// @alku viestit
inline VKAPI_ATTR VkBool32 VKAPI_CALL validointiviesti(
    VkDebugUtilsMessageSeverityFlagBitsEXT vakavuus,
    VkDebugUtilsMessageTypeFlagsEXT,
    const VkDebugUtilsMessengerCallbackDataEXT* tiedot, void*) {
    if (vakavuus >= VK_DEBUG_UTILS_MESSAGE_SEVERITY_WARNING_BIT_EXT) {
        Validointi::tunnisteet.emplace_back(
            tiedot->pMessageIdName ? tiedot->pMessageIdName : "?");
        Validointi::viestit.emplace_back(tiedot->pMessage);
    }
    return VK_FALSE;  // kutsua ei keskeytetä
}
// @loppu viestit

class VkYmparisto {
public:
    VkInstance instanssi = VK_NULL_HANDLE;
    VkPhysicalDevice fyysinen = VK_NULL_HANDLE;
    VkDevice laite = VK_NULL_HANDLE;
    VkQueue jono = VK_NULL_HANDLE;
    std::uint32_t perhe = 0;
    VkCommandPool allas = VK_NULL_HANDLE;

    // synkronointi = true ottaa käyttöön validointikerroksen
    // synkronoinnin tarkistuksen (hitaampi, löytää puuttuvat esteet).
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

    // @alku muistityyppi
    // Ensimmäinen muistityyppi, jonka resurssi sallii ja jolla on
    // halutut ominaisuudet (esim. CPU:lle näkyvä ja koherentti).
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
    // @loppu muistityyppi

    // @alku komennot
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
    // @loppu komennot

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

    // @alku instanssi
    void luo_instanssi(bool synkronointi) {
        const VkApplicationInfo sovellus{
            .sType = VK_STRUCTURE_TYPE_APPLICATION_INFO,
            .pApplicationName = "gpu-ohjelmointi",
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
        const VkValidationFeaturesEXT ominaisuudet{
            .sType = VK_STRUCTURE_TYPE_VALIDATION_FEATURES_EXT,
            .enabledValidationFeatureCount = 1,
            .pEnabledValidationFeatures = lisat};
        const VkInstanceCreateInfo ai{
            .sType = VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO,
            .pNext = validoi && synkronointi ? &ominaisuudet : nullptr,
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
    // @loppu instanssi

    void valitse_laite() {
        std::uint32_t n = 0;
        vkEnumeratePhysicalDevices(instanssi, &n, nullptr);
        if (n == 0) {
            throw std::runtime_error("Vulkan-laitetta ei löydy");
        }
        std::vector<VkPhysicalDevice> laitteet(n);
        vkEnumeratePhysicalDevices(instanssi, &n, laitteet.data());
        fyysinen = laitteet[0];
        std::uint32_t m = 0;
        vkGetPhysicalDeviceQueueFamilyProperties(fyysinen, &m, nullptr);
        std::vector<VkQueueFamilyProperties> perheet(m);
        vkGetPhysicalDeviceQueueFamilyProperties(fyysinen, &m,
                                                 perheet.data());
        for (std::uint32_t i = 0; i < m; ++i) {
            if ((perheet[i].queueFlags & VK_QUEUE_GRAPHICS_BIT) != 0) {
                perhe = i;
                return;
            }
        }
        throw std::runtime_error("grafiikkajonoa ei löydy");
    }

    // @alku laite
    void luo_laite() {
        // Vulkan 1.3:n dynaaminen renderöinti ja synchronization2.
        VkPhysicalDeviceVulkan13Features v13{
            .sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_3_FEATURES,
            .synchronization2 = VK_TRUE,
            .dynamicRendering = VK_TRUE};
        VkPhysicalDeviceVulkan12Features v12{
            .sType = VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_VULKAN_1_2_FEATURES,
            .pNext = &v13,
            .timelineSemaphore = VK_TRUE};
        const float prioriteetti = 1.0f;
        const VkDeviceQueueCreateInfo jonot{
            .sType = VK_STRUCTURE_TYPE_DEVICE_QUEUE_CREATE_INFO,
            .queueFamilyIndex = perhe,
            .queueCount = 1,
            .pQueuePriorities = &prioriteetti};
        const VkDeviceCreateInfo ai{
            .sType = VK_STRUCTURE_TYPE_DEVICE_CREATE_INFO,
            .pNext = &v12,
            .queueCreateInfoCount = 1,
            .pQueueCreateInfos = &jonot};
        tarkista(vkCreateDevice(fyysinen, &ai, nullptr, &laite),
                 "vkCreateDevice");
        vkGetDeviceQueue(laite, perhe, 0, &jono);
    }
    // @loppu laite
};

// @alku puskuri
// Puskuri muisteineen. CPU:lle näkyvä muisti kuvataan pysyvästi
// osoitteeseen data, jotta sitä voi lukea ja kirjoittaa suoraan.
struct Puskuri {
    VkDevice laite;
    VkBuffer puskuri = VK_NULL_HANDLE;
    VkDeviceMemory muisti = VK_NULL_HANDLE;
    void* data = nullptr;

    Puskuri(const VkYmparisto& vk, VkDeviceSize koko,
            VkBufferUsageFlags kaytto)
        : laite{vk.laite} {
        const VkBufferCreateInfo ai{
            .sType = VK_STRUCTURE_TYPE_BUFFER_CREATE_INFO,
            .size = koko,
            .usage = kaytto,
            .sharingMode = VK_SHARING_MODE_EXCLUSIVE};
        tarkista(vkCreateBuffer(laite, &ai, nullptr, &puskuri),
                 "vkCreateBuffer");
        VkMemoryRequirements vaatimus;
        vkGetBufferMemoryRequirements(laite, puskuri, &vaatimus);
        const VkMemoryAllocateInfo mi{
            .sType = VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO,
            .allocationSize = vaatimus.size,
            .memoryTypeIndex = vk.muistityyppi(
                vaatimus.memoryTypeBits,
                VK_MEMORY_PROPERTY_HOST_VISIBLE_BIT |
                    VK_MEMORY_PROPERTY_HOST_COHERENT_BIT)};
        tarkista(vkAllocateMemory(laite, &mi, nullptr, &muisti),
                 "vkAllocateMemory");
        tarkista(vkBindBufferMemory(laite, puskuri, muisti, 0),
                 "vkBindBufferMemory");
        tarkista(vkMapMemory(laite, muisti, 0, VK_WHOLE_SIZE, 0, &data),
                 "vkMapMemory");
    }
    ~Puskuri() {
        vkDestroyBuffer(laite, puskuri, nullptr);
        vkFreeMemory(laite, muisti, nullptr);  // vapautus purkaa kuvauksen
    }
    Puskuri(const Puskuri&) = delete;
    Puskuri& operator=(const Puskuri&) = delete;
};
// @loppu puskuri

// @alku kuva
// Kuva laitteen muistissa ja sen näkymä (image view).
struct VkKuva {
    VkDevice laite;
    VkImage kuva = VK_NULL_HANDLE;
    VkDeviceMemory muisti = VK_NULL_HANDLE;
    VkImageView nakyma = VK_NULL_HANDLE;

    VkKuva(const VkYmparisto& vk, std::uint32_t l, std::uint32_t k,
           VkFormat muoto, VkImageUsageFlags kaytto,
           VkImageAspectFlags osa)
        : laite{vk.laite} {
        const VkImageCreateInfo ai{
            .sType = VK_STRUCTURE_TYPE_IMAGE_CREATE_INFO,
            .imageType = VK_IMAGE_TYPE_2D,
            .format = muoto,
            .extent = {l, k, 1},
            .mipLevels = 1,
            .arrayLayers = 1,
            .samples = VK_SAMPLE_COUNT_1_BIT,
            .tiling = VK_IMAGE_TILING_OPTIMAL,
            .usage = kaytto,
            .initialLayout = VK_IMAGE_LAYOUT_UNDEFINED};
        tarkista(vkCreateImage(laite, &ai, nullptr, &kuva),
                 "vkCreateImage");
        VkMemoryRequirements vaatimus;
        vkGetImageMemoryRequirements(laite, kuva, &vaatimus);
        const VkMemoryAllocateInfo mi{
            .sType = VK_STRUCTURE_TYPE_MEMORY_ALLOCATE_INFO,
            .allocationSize = vaatimus.size,
            .memoryTypeIndex = vk.muistityyppi(
                vaatimus.memoryTypeBits,
                VK_MEMORY_PROPERTY_DEVICE_LOCAL_BIT)};
        tarkista(vkAllocateMemory(laite, &mi, nullptr, &muisti),
                 "vkAllocateMemory");
        tarkista(vkBindImageMemory(laite, kuva, muisti, 0),
                 "vkBindImageMemory");
        const VkImageViewCreateInfo ni{
            .sType = VK_STRUCTURE_TYPE_IMAGE_VIEW_CREATE_INFO,
            .image = kuva,
            .viewType = VK_IMAGE_VIEW_TYPE_2D,
            .format = muoto,
            .subresourceRange = {osa, 0, 1, 0, 1}};
        tarkista(vkCreateImageView(laite, &ni, nullptr, &nakyma),
                 "vkCreateImageView");
    }
    ~VkKuva() {
        vkDestroyImageView(laite, nakyma, nullptr);
        vkDestroyImage(laite, kuva, nullptr);
        vkFreeMemory(laite, muisti, nullptr);
    }
    VkKuva(const VkKuva&) = delete;
    VkKuva& operator=(const VkKuva&) = delete;
};
// @loppu kuva

// @alku siirtyma
// Kuvan asettelun vaihto ja muistiriippuvuus yhdellä esteellä
// (synchronization2): mitkä aiemmat vaiheet ja kirjoitukset on
// saatava valmiiksi ennen kuin mitkä myöhemmät vaiheet saavat jatkaa.
inline void kuvan_siirtyma(VkCommandBuffer kp, VkImage kuva,
                           VkImageLayout vanha, VkImageLayout uusi,
                           VkPipelineStageFlags2 lahde_vaihe,
                           VkAccessFlags2 lahde_kaytto,
                           VkPipelineStageFlags2 kohde_vaihe,
                           VkAccessFlags2 kohde_kaytto,
                           VkImageAspectFlags osa =
                               VK_IMAGE_ASPECT_COLOR_BIT) {
    const VkImageMemoryBarrier2 este{
        .sType = VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER_2,
        .srcStageMask = lahde_vaihe,
        .srcAccessMask = lahde_kaytto,
        .dstStageMask = kohde_vaihe,
        .dstAccessMask = kohde_kaytto,
        .oldLayout = vanha,
        .newLayout = uusi,
        .srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
        .dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED,
        .image = kuva,
        .subresourceRange = {osa, 0, 1, 0, 1}};
    const VkDependencyInfo riippuvuus{
        .sType = VK_STRUCTURE_TYPE_DEPENDENCY_INFO,
        .imageMemoryBarrierCount = 1,
        .pImageMemoryBarriers = &este};
    vkCmdPipelineBarrier2(kp, &riippuvuus);
}
// @loppu siirtyma

// @alku putki
// Grafiikkaputki yhdelle väriliitännälle ilman syvyyttä ja sekoitusta.
// Kaikki tila on kiinteää; vain verteksien muoto annetaan.
inline VkPipeline luo_putki(
    VkDevice laite, VkPipelineLayout asettelu, VkShaderModule vs,
    VkShaderModule fs, VkExtent2D koko, VkFormat muoto,
    const VkPipelineVertexInputStateCreateInfo& syote) {
    const std::array<VkPipelineShaderStageCreateInfo, 2> vaiheet{{
        {.sType = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,
         .stage = VK_SHADER_STAGE_VERTEX_BIT, .module = vs, .pName = "main"},
        {.sType = VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,
         .stage = VK_SHADER_STAGE_FRAGMENT_BIT, .module = fs,
         .pName = "main"},
    }};
    const VkPipelineInputAssemblyStateCreateInfo kokoonpano{
        .sType =
            VK_STRUCTURE_TYPE_PIPELINE_INPUT_ASSEMBLY_STATE_CREATE_INFO,
        .topology = VK_PRIMITIVE_TOPOLOGY_TRIANGLE_LIST};
    const VkViewport nakyma{0, 0, static_cast<float>(koko.width),
                            static_cast<float>(koko.height), 0, 1};
    const VkRect2D leikkaus{{0, 0}, koko};
    const VkPipelineViewportStateCreateInfo nakymat{
        .sType = VK_STRUCTURE_TYPE_PIPELINE_VIEWPORT_STATE_CREATE_INFO,
        .viewportCount = 1, .pViewports = &nakyma,
        .scissorCount = 1, .pScissors = &leikkaus};
    const VkPipelineRasterizationStateCreateInfo rasterointi{
        .sType =
            VK_STRUCTURE_TYPE_PIPELINE_RASTERIZATION_STATE_CREATE_INFO,
        .polygonMode = VK_POLYGON_MODE_FILL,
        .cullMode = VK_CULL_MODE_NONE,
        .lineWidth = 1.0f};
    const VkPipelineMultisampleStateCreateInfo naytteet{
        .sType = VK_STRUCTURE_TYPE_PIPELINE_MULTISAMPLE_STATE_CREATE_INFO,
        .rasterizationSamples = VK_SAMPLE_COUNT_1_BIT};
    const VkPipelineColorBlendAttachmentState liitos{
        .colorWriteMask = 0xF};  // R, G, B ja A ilman sekoitusta
    const VkPipelineColorBlendStateCreateInfo sekoitus{
        .sType = VK_STRUCTURE_TYPE_PIPELINE_COLOR_BLEND_STATE_CREATE_INFO,
        .attachmentCount = 1, .pAttachments = &liitos};
    // Dynaaminen renderöinti: liitäntöjen muodot kerrotaan putkelle
    // suoraan, ilman render pass -oliota.
    const VkPipelineRenderingCreateInfo renderointi{
        .sType = VK_STRUCTURE_TYPE_PIPELINE_RENDERING_CREATE_INFO,
        .colorAttachmentCount = 1,
        .pColorAttachmentFormats = &muoto};
    const VkGraphicsPipelineCreateInfo ai{
        .sType = VK_STRUCTURE_TYPE_GRAPHICS_PIPELINE_CREATE_INFO,
        .pNext = &renderointi,
        .stageCount = 2, .pStages = vaiheet.data(),
        .pVertexInputState = &syote,
        .pInputAssemblyState = &kokoonpano,
        .pViewportState = &nakymat,
        .pRasterizationState = &rasterointi,
        .pMultisampleState = &naytteet,
        .pColorBlendState = &sekoitus,
        .layout = asettelu};
    VkPipeline putki;
    tarkista(vkCreateGraphicsPipelines(laite, VK_NULL_HANDLE, 1, &ai,
                                       nullptr, &putki),
             "vkCreateGraphicsPipelines");
    return putki;
}
// @loppu putki

// SPIR-V-tiedosto (glslc:n tuottama) varjostinmoduuliksi.
inline VkShaderModule lue_varjostin(VkDevice laite,
                                    const std::string& polku) {
    std::ifstream sisaan(polku, std::ios::binary | std::ios::ate);
    if (!sisaan) {
        throw std::runtime_error("ei voi lukea: " + polku);
    }
    std::vector<std::uint32_t> sanat(
        static_cast<std::size_t>(sisaan.tellg()) / 4);
    sisaan.seekg(0);
    sisaan.read(reinterpret_cast<char*>(sanat.data()),
                static_cast<std::streamsize>(sanat.size() * 4));
    const VkShaderModuleCreateInfo ai{
        .sType = VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO,
        .codeSize = sanat.size() * 4,
        .pCode = sanat.data()};
    VkShaderModule moduuli;
    tarkista(vkCreateShaderModule(laite, &ai, nullptr, &moduuli),
             "vkCreateShaderModule");
    return moduuli;
}

// @alku renderoi
// Piirtää kuvaan L×K (RGBA8) ja lukee tuloksen CPU:lle. Kutsujan
// funktio tallentaa piirtokomennot dynaamisen renderöinnin sisälle.
inline Kuva renderoi(const VkYmparisto& vk, std::uint32_t L,
                     std::uint32_t K,
                     const std::function<void(VkCommandBuffer)>& piirra) {
    VkKuva kohde(vk, L, K, VK_FORMAT_R8G8B8A8_UNORM,
                 VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT |
                     VK_IMAGE_USAGE_TRANSFER_SRC_BIT,
                 VK_IMAGE_ASPECT_COLOR_BIT);
    Puskuri luku(vk, L * K * 4, VK_BUFFER_USAGE_TRANSFER_DST_BIT);
    VkCommandBuffer kp = vk.aloita();
    kuvan_siirtyma(kp, kohde.kuva, VK_IMAGE_LAYOUT_UNDEFINED,
                   VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL,
                   VK_PIPELINE_STAGE_2_NONE, VK_ACCESS_2_NONE,
                   VK_PIPELINE_STAGE_2_COLOR_ATTACHMENT_OUTPUT_BIT,
                   VK_ACCESS_2_COLOR_ATTACHMENT_WRITE_BIT);
    const VkRenderingAttachmentInfo vari{
        .sType = VK_STRUCTURE_TYPE_RENDERING_ATTACHMENT_INFO,
        .imageView = kohde.nakyma,
        .imageLayout = VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL,
        .loadOp = VK_ATTACHMENT_LOAD_OP_CLEAR,
        .storeOp = VK_ATTACHMENT_STORE_OP_STORE,
        .clearValue = {.color = {{0.0f, 0.0f, 0.0f, 1.0f}}}};
    const VkRenderingInfo ri{
        .sType = VK_STRUCTURE_TYPE_RENDERING_INFO,
        .renderArea = {{0, 0}, {L, K}},
        .layerCount = 1,
        .colorAttachmentCount = 1,
        .pColorAttachments = &vari};
    vkCmdBeginRendering(kp, &ri);
    piirra(kp);
    vkCmdEndRendering(kp);
    kuvan_siirtyma(kp, kohde.kuva,
                   VK_IMAGE_LAYOUT_COLOR_ATTACHMENT_OPTIMAL,
                   VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
                   VK_PIPELINE_STAGE_2_COLOR_ATTACHMENT_OUTPUT_BIT,
                   VK_ACCESS_2_COLOR_ATTACHMENT_WRITE_BIT,
                   VK_PIPELINE_STAGE_2_COPY_BIT,
                   VK_ACCESS_2_TRANSFER_READ_BIT);
    const VkBufferImageCopy kopio{
        .imageSubresource = {VK_IMAGE_ASPECT_COLOR_BIT, 0, 0, 1},
        .imageExtent = {L, K, 1}};
    vkCmdCopyImageToBuffer(kp, kohde.kuva,
                           VK_IMAGE_LAYOUT_TRANSFER_SRC_OPTIMAL,
                           luku.puskuri, 1, &kopio);
    vk.suorita(kp);
    Kuva kuva(static_cast<int>(L), static_cast<int>(K));
    std::memcpy(kuva.rgba.data(), luku.data, kuva.rgba.size());
    return kuva;
}
// @loppu renderoi
