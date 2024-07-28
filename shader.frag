#version 330

uniform sampler2D inputTexture0;
uniform vec2 resolution;

in vec2 v_texcoord;
out vec4 fragColor;

void main() {
    vec4 color0 = texture(inputTexture0, v_texcoord);

    // Get pixel position 
    float x = v_texcoord.x;
    float y = v_texcoord.y;

    // Get color of next pixel to the right
    vec4 color1 = texture(inputTexture0, vec2(x + 1.0 / resolution.x, y));

    if (color0.r < color1.r + 0.005) {
        fragColor = vec4(0,0,0,0);
    } else {
        fragColor = color0;
    }
}