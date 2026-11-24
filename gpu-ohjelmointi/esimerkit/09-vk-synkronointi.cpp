// Synkronointi Vulkanissa: muistieste komentojen välillä, aikajana-
// semafori GPU:n ja CPU:n välillä sekä aita lopun odotukseen.
// Validointikerros etsii puuttuvat esteet (synkronoinnin validointi).
#include <cstdint>
#include <print>

#include "vk.hpp"

constexpr VkDeviceSize koko = 1024;

// @alku kopio
// Täyttää lähteen arvolla ja kopioi sen kohteeseen. Ilman estettä
// kopio voi lukea lähdettä ennen kuin täyttö on kirjoitettu.
static void tayta_ja_kopioi(const VkYmparisto& vk, const Puskuri& a,
                            const Puskuri& b, bool este) {
    VkCommandBuffer kp = vk.aloita();
    vkCmdFillBuffer(kp, a.puskuri, 0, koko, 0x2A2A2A2A);
    if (este) {
        const VkMemoryBarrier2 m{
            .sType = VK_STRUCTURE_TYPE_MEMORY_BARRIER_2,
            // Täyttö ja kopio ovat kumpikin siirtovaiheen työtä.
            .srcStageMask = VK_PIPELINE_STAGE_2_ALL_TRANSFER_BIT,
            .srcAccessMask = VK_ACCESS_2_TRANSFER_WRITE_BIT,
            .dstStageMask = VK_PIPELINE_STAGE_2_ALL_TRANSFER_BIT,
            .dstAccessMask = VK_ACCESS_2_TRANSFER_READ_BIT};
        const VkDependencyInfo r{
            .sType = VK_STRUCTURE_TYPE_DEPENDENCY_INFO,
            .memoryBarrierCount = 1,
            .pMemoryBarriers = &m};
        vkCmdPipelineBarrier2(kp, &r);
    }
    const VkBufferCopy alue{0, 0, koko};
    vkCmdCopyBuffer(kp, a.puskuri, b.puskuri, 1, &alue);
    vk.suorita(kp);
}
// @loppu kopio

int main() {
    VkYmparisto vk(true);  // synkronoinnin validointi päälle
    const auto kaytto = VK_BUFFER_USAGE_TRANSFER_SRC_BIT |
                        VK_BUFFER_USAGE_TRANSFER_DST_BIT;
    Puskuri a(vk, koko, kaytto), b(vk, koko, kaytto);

    // @alku vertailu
    for (const bool este : {false, true}) {
        Validointi::tunnisteet.clear();
        Validointi::viestit.clear();
        tayta_ja_kopioi(vk, a, b, este);
        const auto ensimmainen = static_cast<std::uint32_t*>(b.data)[0];
        std::println("este {}: tulos 0x{:08X}, ilmoitukset: {}",
                     este ? "on " : "ei", ensimmainen,
                     Validointi::tunnisteet.empty()
                         ? "ei yhtään"
                         : Validointi::tunnisteet.front());
    }
    // @loppu vertailu

    // @alku aikajana
    // Aikajanasemafori: GPU odottaa, kunnes CPU nostaa arvon 1:een,
    // ja nostaa itse arvon 2:een, kun kopio on valmis.
    VkSemaphoreTypeCreateInfo tyyppi{
        .sType = VK_STRUCTURE_TYPE_SEMAPHORE_TYPE_CREATE_INFO,
        .semaphoreType = VK_SEMAPHORE_TYPE_TIMELINE,
        .initialValue = 0};
    const VkSemaphoreCreateInfo si{
        .sType = VK_STRUCTURE_TYPE_SEMAPHORE_CREATE_INFO,
        .pNext = &tyyppi};
    VkSemaphore aikajana;
    tarkista(vkCreateSemaphore(vk.laite, &si, nullptr, &aikajana),
             "vkCreateSemaphore");

    VkCommandBuffer kp = vk.aloita();
    vkCmdFillBuffer(kp, b.puskuri, 0, koko, 0x07070707);
    tarkista(vkEndCommandBuffer(kp), "vkEndCommandBuffer");
    const VkSemaphoreSubmitInfo odota{
        .sType = VK_STRUCTURE_TYPE_SEMAPHORE_SUBMIT_INFO,
        .semaphore = aikajana, .value = 1,
        .stageMask = VK_PIPELINE_STAGE_2_ALL_COMMANDS_BIT};
    const VkSemaphoreSubmitInfo nosta{
        .sType = VK_STRUCTURE_TYPE_SEMAPHORE_SUBMIT_INFO,
        .semaphore = aikajana, .value = 2,
        .stageMask = VK_PIPELINE_STAGE_2_ALL_COMMANDS_BIT};
    const VkCommandBufferSubmitInfo kpi{
        .sType = VK_STRUCTURE_TYPE_COMMAND_BUFFER_SUBMIT_INFO,
        .commandBuffer = kp};
    const VkSubmitInfo2 lahetys{
        .sType = VK_STRUCTURE_TYPE_SUBMIT_INFO_2,
        .waitSemaphoreInfoCount = 1, .pWaitSemaphoreInfos = &odota,
        .commandBufferInfoCount = 1, .pCommandBufferInfos = &kpi,
        .signalSemaphoreInfoCount = 1, .pSignalSemaphoreInfos = &nosta};
    tarkista(vkQueueSubmit2(vk.jono, 1, &lahetys, VK_NULL_HANDLE),
             "vkQueueSubmit2");

    std::uint64_t arvo = 0;
    vkGetSemaphoreCounterValue(vk.laite, aikajana, &arvo);
    std::println("lähetetty, GPU odottaa; semaforin arvo {}", arvo);
    const VkSemaphoreSignalInfo signaali{
        .sType = VK_STRUCTURE_TYPE_SEMAPHORE_SIGNAL_INFO,
        .semaphore = aikajana, .value = 1};
    tarkista(vkSignalSemaphore(vk.laite, &signaali), "vkSignalSemaphore");
    const std::uint64_t odotettava = 2;
    const VkSemaphoreWaitInfo wi{
        .sType = VK_STRUCTURE_TYPE_SEMAPHORE_WAIT_INFO,
        .semaphoreCount = 1, .pSemaphores = &aikajana,
        .pValues = &odotettava};
    tarkista(vkWaitSemaphores(vk.laite, &wi, UINT64_MAX),
             "vkWaitSemaphores");
    vkGetSemaphoreCounterValue(vk.laite, aikajana, &arvo);
    std::println("CPU nosti 1, GPU valmis: arvo {}, tulos 0x{:08X}", arvo,
                 static_cast<std::uint32_t*>(b.data)[0]);
    // @loppu aikajana

    vkFreeCommandBuffers(vk.laite, vk.allas, 1, &kp);
    vkDestroySemaphore(vk.laite, aikajana, nullptr);
    Validointi::raportti();
}
