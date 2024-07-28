import sys
import os
import pygame
import moderngl
import numpy as np
from PIL import Image

class ShaderViewer:
    def __init__(self, width, height):
        pygame.init()
        self.width, self.height = width, height
        self.screen = pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF)
        self.ctx = moderngl.create_context()
        
        self.quad_buffer = self.ctx.buffer(data=np.array([
            -1.0, -1.0, 0.0, 1.0,
             1.0, -1.0, 1.0, 1.0,
            -1.0,  1.0, 0.0, 0.0,
             1.0,  1.0, 1.0, 0.0,
        ], dtype='f4'))
        
        self.shader_files = {
            'vertex': 'shader.vert',
            'fragment': 'shader.frag'
        }
        self.shader_mod_times = {}
        self.load_shader()
        self.load_texture('inputTexture0.jpg')

    def load_shader(self):
        try:
            with open(self.shader_files['vertex'], 'r') as file:
                vertex_shader = file.read()
            with open(self.shader_files['fragment'], 'r') as file:
                fragment_shader = file.read()

            self.prog = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
            self.vao = self.ctx.vertex_array(self.prog, [(self.quad_buffer, '2f 2f', 'in_vert', 'in_texcoord')])

            self.shader_mod_times = {
                'vertex': os.path.getmtime(self.shader_files['vertex']),
                'fragment': os.path.getmtime(self.shader_files['fragment'])
            }
            print("Shaders loaded successfully.")
        except Exception as e:
            print(f"Error loading shaders: {e}")

    def load_texture(self, filename):
        img = Image.open(filename).convert('RGBA')
        self.texture = self.ctx.texture(img.size, 4, img.tobytes())
        self.texture.filter = (moderngl.LINEAR, moderngl.LINEAR)

    def check_shader_files(self):
        for shader_type, shader_file in self.shader_files.items():
            try:
                mod_time = os.path.getmtime(shader_file)
                if mod_time != self.shader_mod_times.get(shader_type):
                    print(f"Detected changes in {shader_file}. Reloading shaders...")
                    self.load_shader()
                    break
            except OSError:
                print(f"Error checking {shader_file}")

    def render(self):
        self.ctx.clear(0.0, 0.0, 0.0)
        self.texture.use(0)
        self.prog['inputTexture0'].value = 0
        self.prog['resolution'].value = (float(self.width), float(self.height))
        self.vao.render(moderngl.TRIANGLE_STRIP)
        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.ACTIVEEVENT:
                    if event.gain == 1:  # Window gained focus
                        self.check_shader_files()
            self.render()
            clock.tick(60)
        pygame.quit()

def process_image(input_path, output_path):
    viewer = ShaderViewer(800, 600)
    viewer.load_texture(input_path)
    
    fbo = viewer.ctx.framebuffer(color_attachments=[viewer.ctx.texture(viewer.texture.size, 4)])
    fbo.use()
    
    viewer.render()
    
    output_data = np.frombuffer(fbo.read(), dtype=np.uint8).reshape(*viewer.texture.size, 4)
    output_img = Image.fromarray(output_data, 'RGBA')
    output_img.save(output_path)
    print(f"Processed image saved to {output_path}")

if __name__ == '__main__':
    if len(sys.argv) > 2:
        process_image(sys.argv[1], sys.argv[2])
    else:
        viewer = ShaderViewer(800, 600)
        viewer.run()