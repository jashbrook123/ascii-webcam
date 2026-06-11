import cv2
import pygame
import moderngl
import sys
from array import array
import numpy as np
import pyvirtualcam
import hand_detection as hd


def redefine():
    video = cv2.VideoCapture(0)
    return video

def get_frame(video):
    ret, frame = video.read()
    if ret:
        yaw,fist = hd.get_image(frame)
        try:
            if yaw <0 : yaw = int(yaw*-1)
            else: yaw = int(yaw)
        except: pass
        frame = cv_to_py(frame)
        frame, wh = resolution(frame)
    else:
        pygame.quit()
        video.release()
        cv2.destroyAllWindows()
        sys.exit()
    return frame, wh, video,yaw,fist

def cv_to_py(frame):
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
    return frame_surface

def resolution(img):
    w = img.get_width()
    h = img.get_height()
    if w > h:
        scalar = w / h
        wh = (int(1440 * scalar), 1440)
        img = pygame.transform.scale(img, wh)
    elif h > w:
        scalar = h / w
        wh = (2560, int(2560 * scalar))
        img = pygame.transform.scale(img, wh)
    else:
        wh = (2560, 1440)
        img = pygame.transform.scale(img, wh)
    return img, wh


v = open("vertex_shader.glsl")
f = open("fragment_shader.glsl")

video = redefine()
fps = video.get(cv2.CAP_PROP_FPS)
if fps <= 0 or fps > 120:
    fps = 30  # fallback

img, wh, video,yaw,fist = get_frame(video)
img.set_colorkey((255, 255, 255))
img, wh = resolution(img)

screen_width, screen_height = wh[0], wh[1]
cell_width, cell_height = 8, 8

ascii_chars = " .:-=+*#%@"
char_len = len(ascii_chars)
atlas_row = 1
atlas_col = 10
glyph_width, glyph_height = cell_width, cell_height

pygame.init()
screen = pygame.display.set_mode(wh, pygame.OPENGL | pygame.DOUBLEBUF)
display = pygame.Surface(wh)

ctx = moderngl.create_context()

atlas_surface = pygame.image.load("ascii_atlas_big.png").convert()
atlas_bytes = pygame.image.tostring(atlas_surface, "RGB")
atlas_tex = ctx.texture(
    (atlas_surface.get_width(), atlas_surface.get_height()),
    3,
    atlas_bytes
)

clock = pygame.time.Clock()

quad_buffer = ctx.buffer(data=array("f", [
    -1.0,  1.0, 0.0, 0.0,
     1.0,  1.0, 1.0, 0.0,
    -1.0, -1.0, 0.0, 1.0,
     1.0, -1.0, 1.0, 1.0,
]))

program = ctx.program(
    vertex_shader=v.read(),
    fragment_shader=f.read()
)
render_object = ctx.vertex_array(program, [(quad_buffer, "2f 2f", "vert", "texcoord")])

def surf_to_texture(surf):
    tex = ctx.texture(surf.get_size(), 4)
    tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
    tex.swizzle = "BGRA"
    tex.write(surf.get_view("1"))
    return tex

def output(ctx):
            data = ctx.screen.read(components=3, alignment=1)
            frame = np.frombuffer(data, dtype=np.uint8).reshape((screen_height, screen_width, 3))
            frame = np.flipud(frame)  # OpenGL origin is bottom-left

            cam.send(frame)
            cam.sleep_until_next_frame()

def tick(time):
    global timer
    time += 1
    if time == 500:
        time = 0
        timer = False
    print(time)
    return time

def swap_render(typ):
    if typ == "norm":return "ascii"
    elif typ == "ascii": return "norm"

with pyvirtualcam.Camera(width=screen_width, height=screen_height, fps=int(fps)) as cam:

    rend = "norm"
    wait_time = 0
    timer = False
    while True:

        img, wh, video,yaw,fist = get_frame(video)
        if fist == True and timer == False:
            rend = swap_render(rend)
            timer = True
            print("swap")
        try:
            if timer == False and yaw <90:
                cell_width += 2
                cell_height += 2
                timer = True
            elif timer == False and yaw > 90:
                cell_width -= 2
                cell_height -= 2
                timer = True
        except: pass
        if timer == True:
            wait_time += 1
            if wait_time >10:
                timer = False
                wait_time = 0

        display.fill((0, 0, 0))
        display.blit(img, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                video.release()
                cv2.destroyAllWindows()
                sys.exit()

        if rend == "ascii":
            v = open("vertex_shader.glsl")
            f = open("fragment_shader.glsl")
            program = ctx.program(
                vertex_shader=v.read(),
                fragment_shader=f.read()
            )
            render_object = ctx.vertex_array(program, [(quad_buffer, "2f 2f", "vert", "texcoord")])
            display_flipped = pygame.transform.flip(display, True, False)
            frame_tex = surf_to_texture(display_flipped)
            frame_tex.use(0)
            atlas_tex.use(1)
            program["tex"] = 0
            program["atlas_tex"] = 1
            program["resolution"] = wh
            program["cell_width"] = cell_width
            program["cell_height"] = cell_height
            program["atlas_col"] = atlas_col
            program["atlas_row"] = atlas_row
        else: 
            v = open("regular_vertex.glsl")
            f = open("regular_fragment.glsl")
            program = ctx.program(
                vertex_shader=v.read(),
                fragment_shader=f.read()
            )
            render_object = ctx.vertex_array(program, [(quad_buffer, "2f 2f", "vert", "texcoord")])
            display_flipped = pygame.transform.flip(display, True, False)
            frame_tex = surf_to_texture(display_flipped)
            frame_tex.use(0)
            program["tex"] = 0

        render_object.render(mode=moderngl.TRIANGLE_STRIP)

        pygame.display.flip()
        output(ctx)

        frame_tex.release()
        clock.tick(fps)