#version 450
// Verteksivarjostin: sijainti ja väri verteksipuskurista.
layout(location = 0) in vec2 sijainti;
layout(location = 1) in vec3 vari;
layout(location = 0) out vec3 v_vari;

void main() {
    v_vari = vari;
    // Vulkanin leikkausavaruudessa y kasvaa alaspäin.
    gl_Position = vec4(sijainti.x, -sijainti.y, 0.0, 1.0);
}
