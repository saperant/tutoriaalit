#version 450
layout(location = 0) in vec3 v_vari;
layout(location = 0) out vec4 tulos;

void main() {
    tulos = vec4(v_vari, 1.0);
}
