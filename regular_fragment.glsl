#version 330 core

uniform sampler2D tex;

in vec2 uvs;
out vec4 f_colour;

void main(){
	vec2 sample_pos = vec2(uvs.x,uvs.y);
	vec3 temp_colour = vec3(texture(tex,sample_pos));
	f_colour = vec4(temp_colour.rg,temp_colour.b*1,1.0);
}