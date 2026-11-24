// Resurssien sidonta Vulkanissa: kuvaajajoukon asettelu, allas ja
// joukko uniform-puskurille sekä push-vakiot piirtokohtaiselle datalle.
#include <array>
#include <cstring>
#include <print>

#include "vk.hpp"

// @alku rakenteet
struct Kohtaus {          // std140: vec2 (8) + float (4) → 16 tavua
    float skaala[2];
    float kirkkaus;
    float tayte;
};
struct Piirto {           // std430: vec2 (8), tasaus vec4:lle (16)
    float siirto[2];
    float tayte[2];
    float vari[4];
};
static_assert(sizeof(Piirto) == 32);
// @loppu rakenteet

constexpr std::uint32_t L = 96, K = 32;

int main() {
    VkYmparisto vk;
    VkDevice d = vk.laite;

    // @alku asettelu
    // Asettelu kertoo putkelle, millaisia resursseja varjostimet
    // odottavat: joukossa 0 sidonnassa 0 uniform-puskuri.
    const VkDescriptorSetLayoutBinding sidonta{
        .binding = 0,
        .descriptorType = VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER,
        .descriptorCount = 1,
        .stageFlags = VK_SHADER_STAGE_VERTEX_BIT};
    const VkDescriptorSetLayoutCreateInfo jai{
        .sType = VK_STRUCTURE_TYPE_DESCRIPTOR_SET_LAYOUT_CREATE_INFO,
        .bindingCount = 1, .pBindings = &sidonta};
    VkDescriptorSetLayout joukon_asettelu;
    tarkista(vkCreateDescriptorSetLayout(d, &jai, nullptr,
                                         &joukon_asettelu),
             "vkCreateDescriptorSetLayout");
    const VkPushConstantRange vakiot{VK_SHADER_STAGE_VERTEX_BIT, 0,
                                     sizeof(Piirto)};
    const VkPipelineLayoutCreateInfo pai{
        .sType = VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO,
        .setLayoutCount = 1, .pSetLayouts = &joukon_asettelu,
        .pushConstantRangeCount = 1, .pPushConstantRanges = &vakiot};
    VkPipelineLayout asettelu;
    tarkista(vkCreatePipelineLayout(d, &pai, nullptr, &asettelu),
             "vkCreatePipelineLayout");
    // @loppu asettelu

    // @alku joukko
    // Allas, joukko ja joukon osoitus puskuriin.
    const VkDescriptorPoolSize koko{VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER, 1};
    const VkDescriptorPoolCreateInfo aai{
        .sType = VK_STRUCTURE_TYPE_DESCRIPTOR_POOL_CREATE_INFO,
        .maxSets = 1, .poolSizeCount = 1, .pPoolSizes = &koko};
    VkDescriptorPool allas;
    tarkista(vkCreateDescriptorPool(d, &aai, nullptr, &allas),
             "vkCreateDescriptorPool");
    const VkDescriptorSetAllocateInfo vai{
        .sType = VK_STRUCTURE_TYPE_DESCRIPTOR_SET_ALLOCATE_INFO,
        .descriptorPool = allas,
        .descriptorSetCount = 1, .pSetLayouts = &joukon_asettelu};
    VkDescriptorSet joukko;
    tarkista(vkAllocateDescriptorSets(d, &vai, &joukko),
             "vkAllocateDescriptorSets");

    Puskuri ubo(vk, sizeof(Kohtaus), VK_BUFFER_USAGE_UNIFORM_BUFFER_BIT);
    const Kohtaus kohtaus{{0.12f, 0.6f}, 0.5f, 0.0f};
    std::memcpy(ubo.data, &kohtaus, sizeof kohtaus);
    const VkDescriptorBufferInfo pi{ubo.puskuri, 0, sizeof(Kohtaus)};
    const VkWriteDescriptorSet kirjoitus{
        .sType = VK_STRUCTURE_TYPE_WRITE_DESCRIPTOR_SET,
        .dstSet = joukko, .dstBinding = 0, .descriptorCount = 1,
        .descriptorType = VK_DESCRIPTOR_TYPE_UNIFORM_BUFFER,
        .pBufferInfo = &pi};
    vkUpdateDescriptorSets(d, 1, &kirjoitus, 0, nullptr);
    // @loppu joukko

    VkShaderModule vs = lue_varjostin(d, "bin/kuvaajat.vert.spv");
    VkShaderModule fs = lue_varjostin(d, "bin/kuvaajat.frag.spv");
    const VkPipelineVertexInputStateCreateInfo ei_syotetta{
        .sType =
            VK_STRUCTURE_TYPE_PIPELINE_VERTEX_INPUT_STATE_CREATE_INFO};
    VkPipeline putki = luo_putki(d, asettelu, vs, fs, {L, K},
                                 VK_FORMAT_R8G8B8A8_UNORM, ei_syotetta);

    // @alku piirto
    const std::array<Piirto, 3> piirrot{{
        {{-0.6f, 0.0f}, {}, {1.0f, 0.0f, 0.0f, 1.0f}},
        {{0.0f, 0.0f}, {}, {0.0f, 1.0f, 0.0f, 1.0f}},
        {{0.6f, 0.0f}, {}, {0.0f, 0.0f, 1.0f, 1.0f}},
    }};
    const Kuva kuva = renderoi(vk, L, K, [&](VkCommandBuffer kp) {
        vkCmdBindPipeline(kp, VK_PIPELINE_BIND_POINT_GRAPHICS, putki);
        vkCmdBindDescriptorSets(kp, VK_PIPELINE_BIND_POINT_GRAPHICS,
                                asettelu, 0, 1, &joukko, 0, nullptr);
        for (const Piirto& p : piirrot) {  // sama putki ja joukko
            vkCmdPushConstants(kp, asettelu, VK_SHADER_STAGE_VERTEX_BIT,
                               0, sizeof p, &p);
            vkCmdDraw(kp, 6, 1, 0, 0);
        }
    });
    // @loppu piirto

    std::println("vasen (19, 16): {}", kuva.vari(19, 16));
    std::println("keski (48, 16): {}", kuva.vari(48, 16));
    std::println("oikea (77, 16): {}", kuva.vari(77, 16));
    std::println("väli  (33, 16): {}", kuva.vari(33, 16));
    Validointi::raportti();

    vkDestroyPipeline(d, putki, nullptr);
    vkDestroyShaderModule(d, vs, nullptr);
    vkDestroyShaderModule(d, fs, nullptr);
    vkDestroyDescriptorPool(d, allas, nullptr);  // vapauttaa joukon
    vkDestroyPipelineLayout(d, asettelu, nullptr);
    vkDestroyDescriptorSetLayout(d, joukon_asettelu, nullptr);
}
