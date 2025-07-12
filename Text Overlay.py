#---------------------------------------------------------->
#                 BEGIN GPL LICENSE BLOCK
#---------------------------------------------------------->
#
# Created by Sangeeth Shyam
# This file is part of Show overlay text and it is free software; you can
# redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation;
# either version 3 of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA
# or see https://www.gnu.org<br>/licenses
#
#---------------------------------------------------------->
#                 END GPL LICENSE BLOCK
#---------------------------------------------------------->

# Copyright (C) 2025 Sangeeth shyam


bl_info = {
    "name": "Text Overlay",
    "author": "Sangeeth Shyam",
    "version": (1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > N-Panel(or press 'N' in keyboard) > Text Overlay",
    "description": "Crate Text overlays in View3D",
    "doc_url": "",
    "category": "Text",
}


import blf
import bpy


font_info = {
    "font_id": 0,
    "handler": None,
}


text_block = None
script_content = None

script_name = 'Text'

scroll_offset = 0
line_height = 14
length = 0

def get_text_block():
    global text_block
    text_block = bpy.data.texts.get(script_name)
    if not text_block:
        text_block = bpy.data.texts.new(name=script_name)
        text_block.use_fake_user = True
    return text_block


def add():
    """Add the draw handler"""

    # Prevent multiple handlers
    if font_info.get("handler"):
        bpy.types.SpaceView3D.draw_handler_remove(font_info["handler"], 'WINDOW')
        font_info["handler"] = None

    # Create a new window
    bpy.ops.wm.window_new()
    new_window = bpy.context.window_manager.windows[-1]
    new_screen = new_window.screen

    # Remove all areas except one
    while len(new_screen.areas) > 1:
        bpy.ops.screen.area_close({'window': new_window, 'screen': new_screen, 'area': new_screen.areas[-1]})

    area = new_screen.areas[0]
    area.type = 'TEXT_EDITOR'

    # Assign the text block to the editor
    for space in area.spaces:
        if space.type == 'TEXT_EDITOR':
            bpy.context.area.spaces.active.show_region_header = False
            textDatablock = get_text_block()
            space.text = textDatablock

            # Disable all checkboxes in View menu
            space.show_word_wrap = False
            space.show_line_numbers = False
            space.show_syntax_highlight = False
            space.show_margin = False
            space.show_line_highlight = False

    get_text_block()

    font_info["handler"] = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, (None, None), 'WINDOW', 'POST_PIXEL')


def remove():
    """Remove the draw handler"""

    if font_info["handler"]:
        bpy.types.SpaceView3D.draw_handler_remove(font_info["handler"], 'WINDOW')

        font_info["handler"] = None

        TextBlock = get_text_block()
        if TextBlock is not None:
            TextBlock.clear()

    else:
        return


def draw_callback_px(self, context):
    global scroll_offset, value, length
    
    """Draw on the viewports"""

    # BLF drawing routine
    font_id = font_info["font_id"]
    blf.size(font_id, 12.5) #change the size of text here
    blf.color(font_id, 1.0, 1.0, 1.0, 1.0) #change the color of text here

    text_overlay = bpy.data.texts.get(script_name)

    if not text_overlay or not text_overlay.use_fake_user:
        return

    text_content = text_overlay.as_string()
    textlines = text_content.split('\n')
    length = len(textlines)

    region = bpy.context.region
    x_margin = 10
    
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    value = space.show_region_toolbar

    if value:
        x_margin = 65
        
    else:
        x_margin = 10
        
    y_margin = 225
    posX = x_margin
    posY = region.height - y_margin

    vScroll = bpy.context.scene.get("visible_line_offset", 0)
    line_height = bpy.context.scene.line_spacing.text_space

    if vScroll == 47:
        visible_lines = (region.height - y_margin) // line_height
    else:
        visible_lines = ((region.height - y_margin) // line_height) - (47 - vScroll)

    # Read from Scene scroll property
    scroll = bpy.context.scene.get("text_scroll_offset", 0)
    
    max_scroll = len(textlines) - visible_lines
    
    if scroll >= max_scroll:
        scroll = max_scroll
            
    else:
        pass
    
    start_para = max(0, scroll)
    end_para = min(len(textlines), start_para + visible_lines)

    for i, line in enumerate(textlines[start_para:end_para]):
        blf.position(font_id, posX, posY - i * line_height, 0)
        blf.draw(font_id, line)


def load_text():
    # Prevent multiple handlers
    if font_info.get("handler"):
        bpy.types.SpaceView3D.draw_handler_remove(font_info["handler"], 'WINDOW')
        font_info["handler"] = None

    font_info["handler"] = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, (None, None), 'WINDOW',
                                                                  'POST_PIXEL')    


def text_length():
    global length
    return length                                           
                                                                  

# Bool property update function
def ToggleVisibility(self, context):
    
    if self.text_bool:
        load_text()
        
    else:
        if font_info.get("handler"):
            bpy.types.SpaceView3D.draw_handler_remove(font_info["handler"], 'WINDOW')
            font_info["handler"] = None
            
    return None


# Property group
class VIEW3D_OT_VisibilityTextOverlay(bpy.types.PropertyGroup):
    text_bool: bpy.props.BoolProperty(
        name="Toggle Visibility",
        description="Show or Hide text",
        default=True,
        update=ToggleVisibility
    )


class VIEW3D_OT_SpacingTextOverlay(bpy.types.PropertyGroup):
    text_space: bpy.props.IntProperty(
        name="Leading",
        description="Set the vertical spacing between lines of text",
        default=14,
        min=14,
        max=100
    )
    

# Operators
class VIEW3D_OT_AddTextOverlay(bpy.types.Operator):
    bl_idname = "view3d.add_text_overlay"
    bl_label = "Add Text"
    bl_description = "Add the overlay text"

    def execute(self, context):
        add()
        bpy.context.scene.text_bool_props.text_bool = True
        return {'FINISHED'}
    

class VIEW3D_OT_EditTextOverlay(bpy.types.Operator):
    bl_idname = "view3d.edit_text_overlay"
    bl_label = "Edit Text"
    bl_description = "Edit the overlay text"

    def execute(self, context):
        if font_info.get("handler"):
            bpy.types.SpaceView3D.draw_handler_remove(font_info["handler"], 'WINDOW')
            font_info["handler"] = None
        add()
        return {'FINISHED'}
    

class VIEW3D_OT_RemoveTextOverlay(bpy.types.Operator):
    bl_idname = "view3d.remove_text_overlay"
    bl_label = "Delete Text"
    bl_description = "Remove the overlay text"

    def execute(self, context):
        remove()
        return {'FINISHED'}


# Panel
class VIEW3D_PT_TextOverlayPanel(bpy.types.Panel):
    bl_label = "Text Overlay"
    bl_idname = "VIEW3D_PT_text_overlay"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Text Overlay'

    def draw(self, context):
        global script_content

        layout = self.layout
        scene = context.scene
        
        layout.prop(scene, "text_scroll_offset", slider=True)

        # Prevent crashing on reload if the property group is missing
        if not hasattr(scene, "text_bool_props"):
            layout.label(text="Property not found (reload script).")
            return
        
        text_overlay = bpy.data.texts.get(script_name)

        if text_overlay is not None:
            script_content = text_overlay.as_string()

        is_active = False
        if script_content:
            is_active = font_info["handler"] is not None

        props = scene.text_bool_props
        row = layout.row(align=True)
        row.prop(props, "text_bool", text="", icon='HIDE_ON' if not is_active else 'HIDE_OFF', emboss=False)
        row.label(text="Toggle Visibility")

        row = layout.row()
        row.enabled = not is_active
        row.operator("view3d.add_text_overlay", icon='ADD')

        row = layout.row()
        row.enabled = is_active
        row.operator("view3d.edit_text_overlay", icon='EDITMODE_HLT')

        layout.prop(scene, "visible_line_offset", slider=True)

        row = layout.row()
        row.prop(scene.line_spacing, "text_space")

        row = layout.row()
        row.enabled = is_active
        row.operator("view3d.remove_text_overlay", icon='CANCEL')
        

# Registration
classes = (
    VIEW3D_OT_VisibilityTextOverlay,
    VIEW3D_OT_SpacingTextOverlay,
    VIEW3D_OT_AddTextOverlay,
    VIEW3D_OT_EditTextOverlay,
    VIEW3D_OT_RemoveTextOverlay,
    VIEW3D_PT_TextOverlayPanel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.text_bool_props = bpy.props.PointerProperty(
        type=VIEW3D_OT_VisibilityTextOverlay
    )
    
    load_text()
    
    bpy.types.Scene.text_scroll_offset = bpy.props.IntProperty(
    name="Scroll",
    default=0,
    min=0,
    max=1000,  
    description="Scroll through the overlay text"
    )

    bpy.types.Scene.visible_line_offset = bpy.props.IntProperty(
    name="Length",
    default=47,
    min=0,
    max=47,
    description="Set how many overlay text lines should drawn"
    )

    bpy.types.Scene.line_spacing = bpy.props.PointerProperty(type=VIEW3D_OT_SpacingTextOverlay)
    

def unregister():
    if hasattr(bpy.types.Scene, "text_bool_props"):
        del bpy.types.Scene.text_bool_props
        
    if hasattr(bpy.types.Scene, "text_scroll_offset"):
        del bpy.types.Scene.text_scroll_offset

    if hasattr(bpy.types.Scene, "visible_line_offset"):
        del bpy.types.Scene.visible_line_offset

    del bpy.types.Scene.line_spacing

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
        
    if font_info.get("handler"):
        bpy.types.SpaceView3D.draw_handler_remove(font_info["handler"], 'WINDOW')
        font_info["handler"] = None
        
        

if __name__ == "__main__":
    register()  
    
    