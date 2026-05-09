#version 330 core

uniform sampler2D tex;
uniform vec2 resolution;
uniform int cell_width;
uniform int cell_height;

uniform sampler2D atlas_tex;
uniform int atlas_col;
uniform int atlas_row;

in vec2 uvs;
out vec4 f_colour;

void main(){
	vec2 pixel_coord = vec2(uvs.x*resolution.x,uvs.y*resolution.y);
	vec3 converter =  vec3(0.2126,0.7152,0.0722);
	vec2 cell_index = vec2(floor(pixel_coord.x/cell_width),floor(pixel_coord.y/cell_height));
	vec2 cell_origin = vec2((cell_index.x * cell_width),(cell_index.y*cell_height));
	vec2 cell_center = vec2((cell_origin.x + (cell_width*0.5)),(cell_origin.y + (cell_height*0.5)));
	vec2 cell_center_uvs = vec2((cell_center.x/resolution.x),(cell_center.y/resolution.y));
	vec3 temp_colour = texture(tex, cell_center_uvs).rgb;

	float light_intensity = dot(temp_colour,converter);
    int num_chars = atlas_col * atlas_row;
	int ascii_index = int(floor(light_intensity * float(num_chars -1)));

	int tile_x = int(mod(ascii_index,atlas_col));
	int tile_y = int(ascii_index / atlas_col);

	vec2 local_coord = (pixel_coord - cell_origin);
	vec2 local_uv = local_coord / vec2(float(cell_width), float(cell_height));

	vec2 atlas_uv;
	atlas_uv.x = (float(tile_x) + local_uv.x) / float(atlas_col);
        atlas_uv.y = (float(tile_y) + local_uv.y) / float(atlas_row);
        
	float glyph = (texture(atlas_tex, atlas_uv).r);
	f_colour = vec4(temp_colour*glyph,1.0);
}
