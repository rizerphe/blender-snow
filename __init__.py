import bpy, bmesh, math, random, os
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from tkinter import Canvas, Button, Tk, PhotoImage

class Snowprint:
    def __init__(self, width=4096, height=4096):
        self.objects = []
        self.w, self.h = width, height
    def add_truckprint(self, x1, y1, x2, y2, scale=100):
        self.objects.append(['truck', (x1, y1), (x2, y2), scale])
    def add_footprints(self, x1, y1, x2, y2, scale=100):
        self.objects.append(['footprints', (x1, y1), (x2, y2), scale])
    def export(self, r=10):
        sharp = Image.new('RGB', (self.w, self.h), (127,127,127))
        for name, pos1, pos2, scale in self.objects:
            if name == 'truck':
                ox, oy = pos2
                dist = ((pos1[0]-pos2[0])**2+(pos1[1]-pos2[1])**2)**0.5
                for n in range(int(dist/scale), 0, -1):
                    x=int(pos1[0]+(pos2[0]-pos1[0])/(dist/scale)*n)
                    y=int(pos1[1]+(pos2[1]-pos1[1])/(dist/scale)*n)
                    dir = math.degrees(math.atan2(ox-x, oy-y))
                    figure = Image.open(os.path.dirname(__file__) + '/samples/truck_gray.png')
                    sharp.paste(figure.rotate(dir-90, fillcolor=(127,127,127)).resize((int(scale*2),int(scale*2))), (int(x-scale),int(y-scale)))
                    ox,oy = x,y
            if name == 'footprints':
                foot = 0
                ox, oy = pos2
                dist = ((pos1[0]-pos2[0])**2+(pos1[1]-pos2[1])**2)**0.5
                for n in range(int(dist/scale), 0, -1):
                    if foot == 1:
                        figure = Image.open(os.path.dirname(__file__) + '/samples/footprint1_gray.png')
                        foot = 0
                    else:
                        figure = Image.open(os.path.dirname(__file__) + '/samples/footprint2_gray.png')
                        foot = 1
                    x=int(pos1[0]+(pos2[0]-pos1[0])/(dist/scale)*n)
                    y=int(pos1[1]+(pos2[1]-pos1[1])/(dist/scale)*n)
                    dir = math.degrees(math.atan2(ox-x, oy-y))
                    sharp.paste(figure.rotate(dir-90, fillcolor=(127,127,127)).resize((int(scale),int(scale))), (int(x-scale/2),int(y-scale/2)))
                    ox,oy = x,y
        sharp = sharp.filter(ImageFilter.GaussianBlur(radius=int(r/4)))
        guassian = sharp.filter(ImageFilter.GaussianBlur(radius=int(r/2)))
        white = ImageEnhance.Brightness(sharp.filter(ImageFilter.GaussianBlur(radius=int(r*2))).filter(ImageFilter.FIND_EDGES())).enhance(40)
        white = ImageEnhance.Brightness(white.filter(ImageFilter.GaussianBlur(radius=r))).enhance(2)
        out = Image.blend(Image.blend(sharp, guassian, 0.9), white, 0.25)
        b = Image.new('RGB', (self.w, self.h), (127,127,127))
        p = white.load()
        d = ImageDraw.Draw(b)
        for x in range(self.w):
            for y in range(self.h):
                if p[x,y][0]>1 and random.randint(1, 500) == 10:
                    polygon = []
                    size = random.randint(r//2, r*2)
                    for f in range(3):
                        polygon.append((random.randint(x-size, x+size), random.randint(y-size, y+size)))
                    d.polygon(polygon,fill=(size*40-250,)*4)
        b = b.filter(ImageFilter.GaussianBlur(radius=5))
        out = Image.blend(out, b, 0.25)
        out.save(os.path.dirname(__file__) + '/snowDisplacement.png')

def main(size=1024, snow_out=10):
    tk = Tk()
    tk.title('paint something')
    s = Snowprint(size, size)
    canvas = Canvas(tk, width=size+100, height=size)
    data = {'toolwidth' : 10, 'd' : [], 'tool' : 0}
    tools=['truck_gray.gif', 'footprint_gray.gif']
    timg = []
    for t in tools:
        timg.append(PhotoImage(file=os.path.dirname(__file__) + '/samples/' + t, master=canvas))
    def update_sizeshelf():
        nonlocal data
        for x in data['d']:
            canvas.delete(x)
        data['d'] = []
        data['d'].append(canvas.create_rectangle(0, 0, 200, 1000, fill='white'))
        data['d'].append(canvas.create_rectangle(0, data['toolwidth']*10, 100, data['toolwidth']*10-100, fill='blue'))
        for y in range(10):
            ts = y*10+10
            data['d'].append(canvas.create_oval(50-ts/2, y*100+50-ts/2, 50+ts/2, y*100+50+ts/2, fill='yellow'))
        for t in range(len(tools)):
            data['d'].append(canvas.create_image(100, t*100, image=timg[t], anchor='nw'))
        data['d'].append(canvas.create_oval(140, 40+data['tool']*100, 160, 60+data['tool']*100, fill='yellow'))
        data['d'].append(canvas.create_text(150, 500, text="just close\nthe window\nwhen you've\nfinished"))
        canvas.update()
    update_sizeshelf()
    canvas.pack()
    x,y = 0,0
    sx,sy = 0,0
    def move(evt):
        nonlocal x,y
        x,y=evt.x-200,evt.y
    canvas.bind_all('<Motion>', move)
    def press(evt):
        nonlocal x,y,sx,sy
        if x < -100:
            data['toolwidth'] = 10*(y//100+1)
            return
        elif x < 0:
            data['tool'] = y//100
            return
        sx,sy=x,y
    canvas.bind_all('<ButtonPress-1>', press)
    def release(evt):
        nonlocal x,y,sx,sy,data
        if x<0:
            return
        canvas.create_line(x+200,y,sx+200,sy,width=data['toolwidth'])
        [s.add_truckprint, s.add_footprints][data['tool']](sx,sy,x,y,data['toolwidth'])
    canvas.bind_all('<ButtonRelease-1>', release)
    while True:
        try:
            update_sizeshelf()
        except:
            s.export(snow_out)
            break

bl_info = {
    "name": "Make snow",
    "category": "Mesh"
}
class AddSnowPlane(bpy.types.Operator):
    """Add a snowy plane"""
    bl_idname = "mesh.add_snow"
    bl_label = "Add some snow"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        size = context.scene.snow_plane_size
        main(size*128, context.scene.snow_out)

        bpy.ops.mesh.primitive_plane_add(radius=size)
        mat = bpy.data.materials.get("Snow")
        ob = bpy.context.active_object
        if mat is None:
            bpy.ops.wm.append(filename='Snow', directory=os.path.dirname(__file__) + '/material.blend\\Material\\', link=True)
        mat = bpy.data.materials.get("Snow")
        if ob.data.materials:
            ob.data.materials[0] = mat
        else:
            ob.data.materials.append(mat)

        subsurf = context.scene.snow_view_subdivisions
        render = context.scene.snow_render_subdivisions
        bpy.ops.object.modifier_add(type='SUBSURF')
        mod = bpy.context.object.modifiers["Subsurf"]
        mod.levels = subsurf
        mod.render_levels = render

        bpy.ops.object.modifier_add(type='DISPLACE')

        mat = bpy.data.materials['Material']
        tex = bpy.data.textures.new("SnowDisplacement", 'IMAGE')
        tex.name = "SnowDisplacement"
        slot = mat.texture_slots.add()
        slot.texture = tex
        slot.texture.image = bpy.data.images.load(os.path.dirname(__file__) + "/snowDisplacement.png")

        mod = bpy.context.object.modifiers["Displace"]
        mod.texture = bpy.data.textures['SnowDisplacement']
        mod.texture_coords = 'UV'

        bpy.ops.object.mode_set(mode='EDIT')
        context = bpy.context
        obj = context.edit_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        bmesh.ops.subdivide_edges(bm,
                edges=bm.edges,
                use_grid_fill=True,
                cuts=64)
        me.update()
        bpy.ops.mesh.select_all(action = 'SELECT')
        bpy.ops.uv.unwrap()
        bpy.ops.mesh.select_all(action = 'DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'} 

class CreateObjectPanel(bpy.types.Panel):
    bl_label = "Add snow"
    bl_idname = "create_snow"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Create"
    bl_context = (("objectmode"))
     
    # Menu and input:
    def draw(self, context):
         obj = context.object
         scene = context.scene
          
         layout = self.layout
          
         row = layout.row()
         row.label("view")
         row.prop(scene, "snow_view_subdivisions")
         row = layout.row()
         row.label("render")
         row.prop(scene, "snow_render_subdivisions")
         row = layout.row()
         row.label("size")
         row.prop(scene, "snow_plane_size")
         row = layout.row()
         row.label("outline")
         row.prop(scene, "snow_out")

         layout.operator(AddSnowPlane.bl_idname)
 
def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.snow_view_subdivisions = bpy.props.IntProperty(
        name = "Snow view subdivisions",
        description = "How detailed should your snow be?",
        default = 1,
        min = 1,
        max = 50)
    bpy.types.Scene.snow_render_subdivisions = bpy.props.IntProperty(
        name = "Snow render subdivisions",
        description = "How detailed should your snow be?",
        default = 3,
        min = 1,
        max = 50)
    bpy.types.Scene.snow_plane_size = bpy.props.IntProperty(
        name = "Snow plane radius",
        description = "radius",
        default = 8,
        min = 1,
        max = 50)
    bpy.types.Scene.snow_out = bpy.props.IntProperty(
        name = "Snow outline radius",
        description = "outline radius",
        default = 10,
        min = 1,
        max = 50)
 
def unregister():
    del bpy.types.Scene.snow_view_subdivisions
    del bpy.types.Scene.snow_render_subdivisions
    del bpy.types.Scene.snow_plane_size
    bpy.utils.unregister_module(__name__)
