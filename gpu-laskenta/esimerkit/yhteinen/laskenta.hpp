// Laskentaputki: SPIR-V-moduuli, kuvaajajoukot varastopuskureille,
// push-vakiot ja erikoistusvakiot. Lisäksi esteet ja aikaleimat.
#pragma once

#include "vk.hpp"

#include <fstream>
#include <initializer_list>
#include <memory>
#include <type_traits>

// @alku ryhmia
// Työryhmien määrä, joka kattaa n säiettä: pyöristys ylöspäin.
constexpr std::uint32_t ryhmia(std::size_t n, std::uint32_t koko) {
    return static_cast<std::uint32_t>((n + koko - 1) / koko);
}
// @loppu ryhmia

inline std::vector<std::uint32_t> lue_spirv(const std::string& polku) {
    std::ifstream sisaan(polku, std::ios::binary | std::ios::ate);
    if (!sisaan) {
        throw std::runtime_error("ei voi lukea: " + polku);
    }
    std::vector<std::uint32_t> sanat(
        static_cast<std::size_t>(sisaan.tellg()) / 4);
    sisaan.seekg(0);
    sisaan.read(reinterpret_cast<char*>(sanat.data()),
                static_cast<std::streamsize>(sanat.size() * 4));
    return sanat;
}

// @alku ryhmat
// Työryhmien määrä kussakin suunnassa (vkCmdDispatch).
struct Ryhmat {
    std::uint32_t x, y = 1, z = 1;
};
// @loppu ryhmat

// Erikoistusvakio: varjostimen constant_id ja sen arvo putkessa.
struct Erikoistus {
    std::uint32_t id;
    std::uint32_t arvo;
};

// Laskentaputki, jonka varjostin lukee ja kirjoittaa varastopuskureita
// sidontapisteissä 0, 1, ... (set = 0). Push-vakioiden koko annetaan
// tavuina. Samalla putkella voi olla useita kuvaajajoukkoja, kun
// samaa varjostinta ajetaan eri puskureille (esim. vuorotellen).
class Putki {
public:
    Putki(const VkYmparisto& vk, const std::string& spv,
          std::uint32_t puskureita, std::uint32_t vakiotavuja = 0,
          std::initializer_list<Erikoistus> erikoistus = {})
        : laite_{vk.laite}, vakiotavuja_{vakiotavuja} {
        std::vector<VkDescriptorSetLayoutBinding> sidonnat;
        for (std::uint32_t i = 0; i < puskureita; ++i) {
            sidonnat.push_back(
                {.binding = i,
                 .descriptorType = VK_DESCRIPTOR_TYPE_STORAGE_BUFFER,
                 .descriptorCount = 1,
                 .stageFlags = VK_SHADER_STAGE_COMPUTE_BIT});
        }
        const VkDescriptorSetLayoutCreateInfo ji{
            .sType = VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO,
            .bindingCount = puskureita,
            .pBindings = sidonnat.data()};
        tarkista(vkCreateDescriptorSetLayout(laite_, &ji, nullptr,
                                             &joukon_asettelu_),
                 "vkCreateDescriptorSetLayout");
        const VkPushConstantRange vakiot{
            .stageFlags = VK_SHADER_STAGE_COMPUTE_BIT,
            .offset = 0,
            .size = vakiotavuja};
        const VkPipelineLayoutCreateInfo ai{
            .sType = VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO,
            .setLayoutCount = 1,
            .pSetLayouts = &joukon_asettelu_,
            .pushConstantRangeCount = vakiotavuja > 0 ? 1u : 0u,
            .pPushConstantRanges = &vakiot};
        tarkista(vkCreatePipelineLayout(laite_, &ai, nullptr, &asettelu_),
                 "vkCreatePipelineLayout");
        const VkDescriptorPoolSize koko{
            .type = VK_DESCRIPTOR_TYPE_STORAGE_BUFFER,
            .descriptorCount = enintaan_joukkoja * puskureita};
        const VkDescriptorPoolCreateInfo pi{
            .sType = VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO,
            .maxSets = enintaan_joukkoja,
            .poolSizeCount = 1,
            .pPoolSizes = &koko};
        tarkista(vkCreateDescriptorPool(laite_, &pi, nullptr, &allas_),
                 "vkCreateDescriptorPool");
        luo_putki(spv, erikoistus);
        puskureita_ = puskureita;
    }
    ~Putki() {
        vkDestroyPipeline(laite_, putki_, nullptr);
        vkDestroyDescriptorPool(laite_, allas_, nullptr);
        vkDestroyPipelineLayout(laite_, asettelu_, nullptr);
        vkDestroyDescriptorSetLayout(laite_, joukon_asettelu_, nullptr);
    }
    Putki(const Putki&) = delete;
    Putki& operator=(const Putki&) = delete;

    // @alku aja
    // Kuvaajajoukko, joka sitoo puskurit järjestyksessä 0, 1, ...
    VkDescriptorSet joukko(std::initializer_list<VkBuffer> puskurit) {
        if (puskurit.size() != puskureita_) {
            throw std::logic_error("väärä määrä puskureita");
        }
        const VkDescriptorSetAllocateInfo vi{
            .sType = VK_STRUCTURE_TYPE_DESCRIPTOR_SET_ALLOCATE_INFO,
            .descriptorPool = allas_,
            .descriptorSetCount = 1,
            .pSetLayouts = &joukon_asettelu_};
        VkDescriptorSet j;
        tarkista(vkAllocateDescriptorSets(laite_, &vi, &j),
                 "vkAllocateDescriptorSets");
        std::vector<VkDescriptorBufferInfo> tiedot;
        for (VkBuffer p : puskurit) {
            tiedot.push_back({p, 0, VK_WHOLE_SIZE});
        }
        std::vector<VkWriteDescriptorSet> kirjoitukset;
        for (std::uint32_t i = 0; i < puskureita_; ++i) {
            kirjoitukset.push_back(
                {.sType = VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET,
                 .dstSet = j,
                 .dstBinding = i,
                 .descriptorCount = 1,
                 .descriptorType = VK_DESCRIPTOR_TYPE_STORAGE_BUFFER,
                 .pBufferInfo = &tiedot[i]});
        }
        vkUpdateDescriptorSets(laite_, puskureita_, kirjoitukset.data(),
                               0, nullptr);
        return j;
    }

    // Tallentaa ajon: putken ja joukon sidonta, push-vakiot ja
    // vkCmdDispatch annetulle määrälle työryhmiä.
    template <typename Vakiot>
    void aja(VkCommandBuffer kp, VkDescriptorSet j, const Vakiot& v,
             Ryhmat r) const {
        static_assert(std::is_trivially_copyable_v<Vakiot>);
        if (sizeof(Vakiot) != vakiotavuja_) {
            throw std::logic_error("push-vakioiden koko ei täsmää");
        }
        sido(kp, j);
        vkCmdPushConstants(kp, asettelu_, VK_SHADER_STAGE_COMPUTE_BIT, 0,
                           vakiotavuja_, &v);
        vkCmdDispatch(kp, r.x, r.y, r.z);
    }
    void aja(VkCommandBuffer kp, VkDescriptorSet j, Ryhmat r) const {
        if (vakiotavuja_ != 0) {
            throw std::logic_error("push-vakiot puuttuvat");
        }
        sido(kp, j);
        vkCmdDispatch(kp, r.x, r.y, r.z);
    }

    // @loppu aja
    static constexpr std::uint32_t enintaan_joukkoja = 8;

private:
    VkDevice laite_;
    std::uint32_t vakiotavuja_;
    std::uint32_t puskureita_ = 0;
    VkDescriptorSetLayout joukon_asettelu_ = VK_NULL_HANDLE;
    VkPipelineLayout asettelu_ = VK_NULL_HANDLE;
    VkDescriptorPool allas_ = VK_NULL_HANDLE;
    VkPipeline putki_ = VK_NULL_HANDLE;

    void sido(VkCommandBuffer kp, VkDescriptorSet j) const {
        vkCmdBindPipeline(kp, VK_PIPELINE_BIND_POINT_COMPUTE, putki_);
        vkCmdBindDescriptorSets(kp, VK_PIPELINE_BIND_POINT_COMPUTE,
                                asettelu_, 0, 1, &j, 0, nullptr);
    }

    // @alku luo
    void luo_putki(const std::string& spv,
                   std::initializer_list<Erikoistus> erikoistus) {
        const auto sanat = lue_spirv(spv);
        const VkShaderModuleCreateInfo mi{
            .sType = VK_STRUCTURE_TYPE_SHADER_MODULE_CREATE_INFO,
            .codeSize = sanat.size() * 4,
            .pCode = sanat.data()};
        VkShaderModule moduuli;
        tarkista(vkCreateShaderModule(laite_, &mi, nullptr, &moduuli),
                 "vkCreateShaderModule");
        // Erikoistusvakiot: kukin 4 tavua peräkkäin taulukossa.
        std::vector<VkSpecializationMapEntry> kohdat;
        std::vector<std::uint32_t> arvot;
        for (const auto& e : erikoistus) {
            kohdat.push_back({e.id,
                              static_cast<std::uint32_t>(arvot.size() * 4),
                              4});
            arvot.push_back(e.arvo);
        }
        const VkSpecializationInfo ei{
            .mapEntryCount = static_cast<std::uint32_t>(kohdat.size()),
            .pMapEntries = kohdat.data(),
            .dataSize = arvot.size() * 4,
            .pData = arvot.data()};
        const VkComputePipelineCreateInfo ai{
            .sType = VK_STRUCTURE_TYPE_COMPUTE_PIPELINE_CREATE_INFO,
            .stage = {
                .sType =
                    VK_STRUCTURE_TYPE_PIPELINE_SHADER_STAGE_CREATE_INFO,
                .stage = VK_SHADER_STAGE_COMPUTE_BIT,
                .module = moduuli,
                .pName = "main",
                .pSpecializationInfo = kohdat.empty() ? nullptr : &ei},
            .layout = asettelu_};
        tarkista(vkCreateComputePipelines(laite_, VK_NULL_HANDLE, 1, &ai,
                                          nullptr, &putki_),
                 "vkCreateComputePipelines");
        vkDestroyShaderModule(laite_, moduuli, nullptr);
    }
    // @loppu luo
};

// @alku este
// Laskennasta laskentaan: edellisen ajon kirjoitukset on tehtävä
// näkyviksi ennen kuin seuraava ajo lukee tai kirjoittaa samaa dataa.
inline void laskentaeste(VkCommandBuffer kp) {
    const VkMemoryBarrier2 este{
        .sType = VK_STRUCTURE_TYPE_MEMORY_BARRIER_2,
        .srcStageMask = VK_PIPELINE_STAGE_2_COMPUTE_SHADER_BIT,
        .srcAccessMask = VK_ACCESS_2_SHADER_STORAGE_WRITE_BIT,
        .dstStageMask = VK_PIPELINE_STAGE_2_COMPUTE_SHADER_BIT,
        .dstAccessMask = VK_ACCESS_2_SHADER_STORAGE_READ_BIT |
                         VK_ACCESS_2_SHADER_STORAGE_WRITE_BIT};
    const VkDependencyInfo riippuvuus{
        .sType = VK_STRUCTURE_TYPE_DEPENDENCY_INFO,
        .memoryBarrierCount = 1,
        .pMemoryBarriers = &este};
    vkCmdPipelineBarrier2(kp, &riippuvuus);
}
// @loppu este

// Yleinen muistieste kahden vaiheen välille (esim. kopio → laskenta).
inline void este(VkCommandBuffer kp, VkPipelineStageFlags2 lahde,
                 VkAccessFlags2 lahde_kaytto, VkPipelineStageFlags2 kohde,
                 VkAccessFlags2 kohde_kaytto) {
    const VkMemoryBarrier2 e{
        .sType = VK_STRUCTURE_TYPE_MEMORY_BARRIER_2,
        .srcStageMask = lahde,
        .srcAccessMask = lahde_kaytto,
        .dstStageMask = kohde,
        .dstAccessMask = kohde_kaytto};
    const VkDependencyInfo riippuvuus{
        .sType = VK_STRUCTURE_TYPE_DEPENDENCY_INFO,
        .memoryBarrierCount = 1,
        .pMemoryBarriers = &e};
    vkCmdPipelineBarrier2(kp, &riippuvuus);
}

// @alku ajastin
// Aikaleimat GPU:n kellosta: merkitse(i) kirjoittaa leiman, kun kaikki
// sitä ennen tallennetut komennot ovat valmiita. Leima 0 nollaa ensin
// kyselyt, koska kyselyä ei saa kirjoittaa kahdesti ilman nollausta.
// lue() palauttaa leimojen erotukset nanosekunteina.
class Ajastin {
public:
    Ajastin(const VkYmparisto& vk, std::uint32_t leimoja)
        : laite_{vk.laite}, n_{leimoja},
          jakso_ns_{vk.ominaisuudet.limits.timestampPeriod} {
        if (vk.aikaleimabitit == 0) {
            throw std::runtime_error("jono ei tue aikaleimoja");
        }
        const VkQueryPoolCreateInfo ai{
            .sType = VK_STRUCTURE_TYPE_QUERY_POOL_CREATE_INFO,
            .queryType = VK_QUERY_TYPE_TIMESTAMP,
            .queryCount = leimoja};
        tarkista(vkCreateQueryPool(laite_, &ai, nullptr, &allas_),
                 "vkCreateQueryPool");
    }
    ~Ajastin() { vkDestroyQueryPool(laite_, allas_, nullptr); }
    Ajastin(const Ajastin&) = delete;
    Ajastin& operator=(const Ajastin&) = delete;

    void merkitse(VkCommandBuffer kp, std::uint32_t i) const {
        if (i == 0) {
            vkCmdResetQueryPool(kp, allas_, 0, n_);
        }
        vkCmdWriteTimestamp2(kp, VK_PIPELINE_STAGE_2_ALL_COMMANDS_BIT,
                             allas_, i);
    }
    std::vector<double> lue() {
        std::vector<std::uint64_t> leimat(n_);
        tarkista(vkGetQueryPoolResults(
                     laite_, allas_, 0, n_, n_ * sizeof(std::uint64_t),
                     leimat.data(), sizeof(std::uint64_t),
                     VK_QUERY_RESULT_64_BIT | VK_QUERY_RESULT_WAIT_BIT),
                 "vkGetQueryPoolResults");
        std::vector<double> erot;
        for (std::uint32_t i = 1; i < n_; ++i) {
            erot.push_back(static_cast<double>(leimat[i] - leimat[i - 1]) *
                           jakso_ns_);
        }
        return erot;
    }

private:
    VkDevice laite_;
    std::uint32_t n_;
    float jakso_ns_;
    VkQueryPool allas_ = VK_NULL_HANDLE;
};
// @loppu ajastin
