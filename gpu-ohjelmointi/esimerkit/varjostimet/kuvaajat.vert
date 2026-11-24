#version 450
// Kuvaajajoukko 0, sidonta 0: koko piirron yhteinen data.
layout(set = 0, binding = 0, std140) uniform Kohtaus {
    vec2 skaala;
    float kirkkaus;
} kohtaus;

// Push-vakiot: pieni, piirtokohtainen data suoraan komentopuskurissa.
layout(push_constant, std430) uniform Piirto {
    vec2 siirto;
    vec4 vari;
} piirto;

layout(location = 0) out vec4 v_vari;

void main() {
    const vec2 k[6] = vec2[](vec2(-1, -1), vec2(1, -1), vec2(1, 1),
                             vec2(-1, -1), vec2(1, 1), vec2(-1, 1));
    vec2 p = k[gl_VertexIndex] * kohtaus.skaala + piirto.siirto;
    gl_Position = vec4(p, 0.0, 1.0);
    v_vari = vec4(piirto.vari.rgb * kohtaus.kirkkaus, 1.0);
}
