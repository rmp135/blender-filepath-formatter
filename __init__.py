bl_info = {
    "name": "Filepath Formatter",
    "author": "Ryan Poole",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "Output Properties > Filepath Formatter",
    "description": "Sets the format for ouput renders.",
    "category": "Render"
}

import bpy
import datetime
from bpy.app.handlers import persistent

@persistent
def update_filepath(self):
    if not bpy.context.scene.filepath_formatter_settings.use_filepath_formatter:
        return
    directory = replace_tokens(bpy.context.scene.filepath_formatter_settings.directory)
    filename = replace_tokens(bpy.context.scene.filepath_formatter_settings.filename)
    bpy.context.scene.render.filepath = directory + '\\' + filename
    if bpy.context.scene.use_nodes:
        for node in bpy.context.scene.node_tree.nodes:
            if node.type == "OUTPUT_FILE":
                node.base_path = directory
                for slot in node.file_slots:
                    slot.path = filename

def replace_tokens(base_path):
    base_path = base_path \
        .replace('%resx', str(bpy.context.scene.render.resolution_x)) \
        .replace('%resy', str(bpy.context.scene.render.resolution_y)) \
        .replace('%scene', bpy.context.scene.name) \
        .replace('%camera', bpy.context.scene.camera.name) \
        .replace('%filename', bpy.path.basename(bpy.context.blend_data.filepath).replace('.blend', ''))
    now = datetime.datetime.now()
    base_path = now.strftime(base_path)
    return base_path

class FilepathFormatterSettings(bpy.types.PropertyGroup):
    use_filepath_formatter: bpy.props.BoolProperty(name="Filepath formatter.",
                                                    description="Enable/disable generation of filepaths. When enabled, "
                                                                "this will use the path and filename for renders and "
                                                                "all File Output nodes.",
                                                    default=False)

    directory: bpy.props.StringProperty(name="Directory",
                                        description="Directory format.",
                                        default="//",
                                        maxlen=4096)

    filename: bpy.props.StringProperty(name="File Name",
                                        description="File name format.",
                                        default="#####",
                                        maxlen=4096)                                        


class FilepathFormatter_PT_panel(bpy.types.Panel):
    bl_label = "Filepath Formatter"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_idname = "OUTPUT_PT_filepath_formatter_panel"
    bl_context = "output"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        self.layout.prop(context.scene.filepath_formatter_settings, "use_filepath_formatter", text="")

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene.filepath_formatter_settings, "directory")
        layout.prop(context.scene.filepath_formatter_settings, "filename")


classes = [FilepathFormatterSettings, FilepathFormatter_PT_panel]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.filepath_formatter_settings = bpy.props.PointerProperty(type=FilepathFormatterSettings)
    if update_filepath not in bpy.app.handlers.render_pre:
        bpy.app.handlers.render_pre.append(update_filepath)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.filepath_formatter_settings
    if update_filepath in bpy.app.handlers.render_pre:
        bpy.app.handlers.render_pre.remove(update_filepath)

if __name__ == "__main__":
    register()