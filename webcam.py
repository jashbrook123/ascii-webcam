import cv2
import pygame
import moderngl
import sys
from array import array
import cv2

def redefine():
    video = cv2.VideoCapture(0)
    return video

def get_frame(video):
    ret,frame = video.read()
    if ret == True:
        frame = cv_to_py(frame)
        frame,wh = resolution(frame)
    else:
        sys.quit()
    return frame,wh,video

def cv_to_py(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
    return frame_surface

def resolution(img):
    w = img.get_width()
    h = img.get_height()
    if w > h:
        scalar = w/h
        wh = (1440*scalar,1440)
        img = pygame.transform.scale(img, wh)
    elif h > w:
        scalar = h/w
        wh = (2560,2560*scalar)
        img = pygame.transform.scale(img, wh)
    else:
        wh = (2560,1440)
        img = pygame.transform.scale(img, wh)
    return img,wh

v = open("vertex_shader.glsl")
f = open("fragment_shader.glsl")

video = redefine()
fps = video.get(cv2.CAP_PROP_FPS)

img,wh,video = get_frame(video)
img.set_colorkey((255,255,255))
img = resolution(img)

screen_width,screen_height = wh[0],wh[1]
cell_width,cell_height = 8,8

ascii_chars = " .:-=+*#%@"
char_len = len(ascii_chars)
atlas_row = 1
atlas_col = 10
glyph_width,glyph_height = cell_width,cell_height

screen= pygame.display.set_mode(wh, pygame.OPENGL | pygame.DOUBLEBUF)
display = pygame.Surface(wh)

ctx = moderngl.create_context()

atlas_surface = pygame.image.load("ascii_atlas_big.png").convert()
atlas_bytes = pygame.image.tostring(atlas_surface,"RGB")
atlas_tex = ctx.texture(
    (atlas_surface.get_width(), atlas_surface.get_height()),
    3,  # grayscale
    atlas_bytes
)



clock = pygame.time.Clock()

        
quad_buffer = ctx.buffer(data=array("f",[
    -1.0,1.0,0.0,0.0,
    1.0,1.0,1.0,0.0,
    -1.0,-1.0,0.0,1.0,
    1.0,-1.0,1.0,1.0,
]))    
program  = ctx.program(vertex_shader = v.read(),
                       fragment_shader = f.read()
                       )
render_object = ctx.vertex_array(program,[(quad_buffer, "2f 2f", "vert","texcoord")])

def surf_to_texture(surf):
    tex = ctx.texture(surf.get_size(), 4)
    tex.filter = (moderngl.NEAREST,moderngl.NEAREST)
    tex.swizzle = "BGRA"
    tex.write(surf.get_view("1"))
    return tex

t = 0
rend = "norm" 
while True:
    img,wh,video = get_frame(video)
    
    display.fill((0,0,0))

    display.blit(img,(0,0))
    
    t+=1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            video.release()
            cv2.destroyAllWindows()

            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                rend = "ascii"     
            if event.key == pygame.K_a:
                rend = "norm"
            if event.key == pygame.K_w:
                cell_width += 2
                cell_height += 2
            if event.key == pygame.K_s:
                cell_width -= 2
                cell_height -= 2
    if rend == "ascii":
        v = open("vertex_shader.glsl")
        f = open("fragment_shader.glsl")
        program  = ctx.program(vertex_shader = v.read(),
                       fragment_shader = f.read()
                       )
        render_object = ctx.vertex_array(program,[(quad_buffer, "2f 2f", "vert","texcoord")])
        display = pygame.transform.flip(display,True,False)
        frame_tex = surf_to_texture(display)
        frame_tex.use(0)
        atlas_tex.use(1)
        program["tex"] = 0
        program["atlas_tex"] = 1
        program["resolution"] = wh
        program["cell_width"] = cell_width
        program["cell_height"] = cell_height
        program["atlas_col"] = atlas_col
        program["atlas_row"] = atlas_row
    elif rend == "norm":
        v = open("regular_vertex.glsl")
        f = open("regular_fragment.glsl")
        program  = ctx.program(vertex_shader = v.read(),
                       fragment_shader = f.read()
                       )
        render_object = ctx.vertex_array(program,[(quad_buffer, "2f 2f", "vert","texcoord")])
        display = pygame.transform.flip(display,True,False)
        frame_tex = surf_to_texture(display)
        frame_tex.use(0)
        program["tex"] = 0
    
    render_object.render(mode=moderngl.TRIANGLE_STRIP)
    
    
    pygame.display.flip()
    frame_tex.release()
    clock.tick(fps)
