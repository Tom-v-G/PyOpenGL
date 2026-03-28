#version 330 core

in vec2 TexCoords;
out vec4 FragColor;

uniform sampler2D text;
uniform vec3 textColor;

void main() {
    float alpha = texture(text, TexCoords).r;
    FragColor = vec4(textColor, alpha);
    // FragColor = vec4(texture(text, TexCoords).rrr, 1.0);
    // FragColor = vec4(texture(text, TexCoords).rrrr);
    // FragColor = vec4(TexCoords.x, TexCoords.y, 0.0, 1.0);
}