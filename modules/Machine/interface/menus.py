from .... icons.icons import get_icon_id
def extrude_menu(self, context):
    self.layout.operator_context = 'INVOKE_DEFAULT'
    self.layout.operator("mesh.bdsm_mesh_extrude_punchit", text="Punch It", icon_value=get_icon_id('PUNCHit'))

def menu_func(self, context):
    self.layout.operator_context = "INVOKE_DEFAULT";
    self.layout.operator('view3d.bdsm_draw_test')