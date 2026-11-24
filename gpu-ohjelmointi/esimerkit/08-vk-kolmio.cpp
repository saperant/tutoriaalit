// Sama kolmio Vulkanilla: putki, dynaaminen renderöinti kuvaan,
// kopio CPU:lle näkyvään puskuriin ja tuloksen tarkistus.
#include <array>
#include <cstring>
#include <print>

#include "kuva.hpp"
#include "vk.hpp"

struct Verteksi {
    float x, y, r, g, b;
};
constexpr std::array<Verteksi, 3> kolmio{{
    {-0.8f, -0.8f, 1.0f, 0.0f, 0.0f},
    {0.8f, -0.8f, 0.0f, 1.0f, 0.0f},
    {0.0f, 0.8f, 0.0f, 0.0f, 1.0f},
}};
constexpr std::uint32_t L = 96, K = 96;
constexpr VkFormat muoto = VK_FORMAT_R8G8B8A8_UNORM;


int main() {
    VkYmparisto vk;
    // @alku resurssit
    Puskuri vertekset(vk, sizeof kolmio,
                      VK_BUFFER_USAGE_VERTEX_BUFFER_BIT);
    std::memcpy(vertekset.data, kolmio.data(), sizeof kolmio);
    VkKuva kohde(vk, L, K, muoto,
                 VK_IMAGE_USAGE_COLOR_ATTACHMENT_BIT |
                     VK_IMAGE_USAGE_TRANSFER_SRC_BIT,
                 VK_IMAGE_ASPECT_COLOR_BIT);
    Puskuri luku(vk, L * K * 4, VK_BUFFER_USAGE_TRANSFER_DST_BIT);
    // @loppu resurssit

    const VkPipelineLayoutCreateInfo ai{
        .sType = VK_STRUCTURE_TYPE_PIPELINE_LAYOUT_CREATE_INFO};
    VkPipelineLayout asettelu;
    tarkista(vkCreatePipelineLayout(vk.laite, &ai, nullptr, &asettelu),
             "vkCreatePipelineLayout");
    VkShaderModule vs = lue_varjostin(vk.laite, "bin/kolmio.vert.spv");
    VkShaderModule fs = lue_varjostin(vk.laite, "bin/kolmio.frag.spv");
    // @alku syote
    // Verteksin muoto: yksi puskuri, kaksi attribuuttia.
    const VkVertexInputBindingDescription sidonta{
        0, sizeof(Verteksi), VK_VERTEX_INPUT_RATE_VERTEX};
    const std::array<VkVertexInputAttributeDescription, 2> attribuutit{{
        {0, 0, VK_FORMAT_R32G32_SFLOAT, offsetof(Verteksi, x)},
        {1, 0, VK_FORMAT_R32G32B32_SFLOAT, offsetof(Verteksi, r)},
    }};
    const VkPipelineVertexInputStateCreateInfo syote{
        .sType = VK_STRUCTURE_TYPE_PIPELINE_VERTEX_INPUT_STATE_CREATE_INFO,
        .vertexBindingDescriptionCount = 1,
        .pVertexBindingDescriptions = &sidonta,
        .vertexAttributeDescriptionCount = 2,
        .pVertexAttributeDescriptions = attribuutit.data()};
    VkPipeline putki =
        luo_putki(vk.laite, asettelu, vs, fs, {L, K}, muoto, syote);
    // @loppu syote

    // @alku komennot
    VkCommandBuffer kp = vk.aloita();
    // Kuva piirtokohteeksi: sisältö saa hävitä (UNDEFINED).
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
    const VkRenderingInfo renderointi{
        .sType = VK_STRUCTURE_TYPE_RENDERING_INFO,
        .renderArea = {{0, 0}, {L, K}},
        .layerCount = 1,
        .colorAttachmentCount = 1,
        .pColorAttachments = &vari};
    vkCmdBeginRendering(kp, &renderointi);
    vkCmdBindPipeline(kp, VK_PIPELINE_BIND_POINT_GRAPHICS, putki);
    const VkDeviceSize alku = 0;
    vkCmdBindVertexBuffers(kp, 0, 1, &vertekset.puskuri, &alku);
    vkCmdDraw(kp, 3, 1, 0, 0);
    vkCmdEndRendering(kp);
    // Piirto valmiiksi ennen kopiota, ja kuva kopioinnin lähteeksi.
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
    vk.suorita(kp);  // lähetys ja odotus aidalla
    // @loppu komennot

    // Vulkanin kuvan rivit alkavat ylhäältä, kuten kuvatiedostoissa.
    Kuva kuva(L, K);
    std::memcpy(kuva.rgba.data(), luku.data, kuva.rgba.size());
    kuva.tallenna_ppm("bin/08-vk-kolmio.ppm");
    std::println("keskikohta (48, 52): {}", kuva.vari(48, 52));
    std::println("vasen ala (12, 84): {}", kuva.vari(12, 84));
    std::println("nurkka (2, 2):      {}", kuva.vari(2, 2));
    std::println("peitetyt pikselit:  {} / {}", kuva.peitetyt({0, 0, 0}),
                 L * K);
    Validointi::raportti();

    vkDestroyPipeline(vk.laite, putki, nullptr);
    vkDestroyShaderModule(vk.laite, vs, nullptr);
    vkDestroyShaderModule(vk.laite, fs, nullptr);
    vkDestroyPipelineLayout(vk.laite, asettelu, nullptr);
}
