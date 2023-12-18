import bpy
from bpy.props import BoolProperty, EnumProperty
from bpy.types import Operator, Panel

class BDSM_Modifier_Subdivide(Operator):
    bl_idname = "view3d.bdsm_modifier_subdivide"
    bl_label = "BDSM Modifier Subdivide"
    bl_description = "BDSM Modifier Subdivide \nToggle/Set Subdivide Levels"
    bl_options = {'REGISTER', 'UNDO'}

    level_mode: EnumProperty(
        items=[("TOGGLE", "Toggle Subd", "PROPERTIES", "TOGGLE", 1),
               ("VIEWPORT", "Set Viewport Levels", "RESTRICT_VIEW_OFF", "VIEWPORT", 2),
               ("RENDER", "Set Render Levels", "RESTRICT_RENDER_OFF", "RENDER", 3)
               ],
        name="Level Mode",
        options={'HIDDEN'},
        default="TOGGLE")

    @classmethod
    def poll(cls, context):
        return context.object is not None

    @classmethod
    def description(cls, context, properties):
        if properties.level_mode == "VIEWPORT":
            return "Set Viewport SubD Level on selected Object(s) (using options value)"
        elif properties.level_mode == "RENDER":
            return "Set Render SubD Level on selected Object(s) (using options value)"
        else:
            return "Toggles (add if none exist) SubD modifier(s) on selected object(s), as defined by options"

    def execute(self, context):
        props = context.window_manager.BDSM_Context
        vp_level = props.vp_level
        render_level = props.render_level
        flat_edit = props.flat_edit
        limit_surface = props.limit_surface
        boundary_smooth = props.boundary_smooth
        optimal_display = props.optimal_display
        on_cage = props.on_cage
        use_autosmooth = props.subd_autosmooth

        mode = context.mode[:]
        if mode == "EDIT_MESH":
            mode = "EDIT"
        new_subd = []
        cat = {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'HAIR', 'GPENCIL'}
        sel_objects = [o for o in context.selected_objects if o.type in cat]
        mode_objects = [o for o in context.objects_in_mode if o.type in cat]
        if not sel_objects and mode_objects:
            sel_objects = mode_objects

        # APPLY NEW SUBSURF IF NONE (TOGGLE)
        if self.level_mode == "TOGGLE":
            subd_objects = []

            for o in sel_objects:
                for mod in o.modifiers:
                    if mod.type == "SUBSURF":
                        subd_objects.append(o)
                        break

            new = [o for o in sel_objects if o not in subd_objects]
            for obj in new:
                mod = obj.modifiers.new(name="Subdivison", type="SUBSURF")

                mod.levels = vp_level
                mod.render_levels = render_level
                mod.boundary_smooth = boundary_smooth
                mod.use_limit_surface = limit_surface
                mod.show_only_control_edges = optimal_display
                mod.show_on_cage = on_cage

                obj.data.use_auto_smooth = False

                if mode != "OBJECT":
                    bpy.ops.object.mode_set(mode="OBJECT")
                    bpy.ops.object.shade_smooth()
                    bpy.ops.object.mode_set(mode=mode)
                else:
                    bpy.ops.object.shade_smooth()
                new_subd.append(obj)

        # MAIN
        for obj in sel_objects:

            if obj not in new_subd:
                set_flat = False
                auto_smooth = False

                for mod in obj.modifiers:

                    if mod.type == "SUBSURF":

                        if self.level_mode == "VIEWPORT":
                            mod.levels = vp_level
                        elif self.level_mode == "RENDER":
                            mod.render_levels = render_level

                        elif self.level_mode == "TOGGLE":

                            if mod.show_viewport:
                                # TURN OFF
                                mod.show_viewport = False

                                # re-applying these for otherwise added subd modifiers
                                mod.boundary_smooth = boundary_smooth
                                mod.use_limit_surface = limit_surface
                                mod.show_only_control_edges = optimal_display
                                mod.show_on_cage = on_cage

                                if use_autosmooth:
                                    auto_smooth = True

                                if flat_edit:
                                    set_flat = True

                            elif not mod.show_viewport:
                                # TURN ON
                                mod.show_viewport = True

                if self.level_mode == "TOGGLE":
                    if use_autosmooth:
                        if auto_smooth:
                            obj.data.use_auto_smooth = True
                        else:
                            obj.data.use_auto_smooth = False

                    if flat_edit and set_flat:
                        if mode != "OBJECT":
                            bpy.ops.object.mode_set(mode="OBJECT")
                            bpy.ops.object.shade_flat()
                            bpy.ops.object.mode_set(mode=mode)
                        else:
                            bpy.ops.object.shade_flat()
                    elif flat_edit:
                        if mode != "OBJECT":
                            bpy.ops.object.mode_set(mode="OBJECT")
                            bpy.ops.object.shade_smooth()
                            bpy.ops.object.mode_set(mode=mode)
                        else:
                            bpy.ops.object.shade_smooth()

        return {"FINISHED"}

class BDSM_Modifier_Subdivide_Step(Operator):
    bl_idname = "view3d.bdsm_modifier_subdivide_step"
    bl_label = "BDSM Modifier Subdivide Step"
    bl_description = "BDSM Modifier Subdivide Step \nStep Subdivide Levels"
    bl_options = {'REGISTER', 'UNDO'}

    step_up: BoolProperty(default=True, options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return context.object is not None

    @classmethod
    def description(cls, context, properties):
        if properties.step_up:
            return "Step-up Viewport SubD Level +1 on selected Object(s)"
        else:
            return "Step-down Viewport SubD Level -1 on selected Object(s)"

    def execute(self, context):
        cat = {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'HAIR', 'GPENCIL'}
        sel_objects = [o for o in context.selected_objects if o.type in cat]
        mode_objects = [o for o in context.objects_in_mode if o.type in cat]
        if not sel_objects and mode_objects:
            sel_objects = mode_objects

        if sel_objects:
            for o in sel_objects:
                for mod in o.modifiers:
                    if mod.type == "SUBSURF":
                        if self.step_up:
                            mod.levels += 1
                        else:
                            mod.levels -= 1
        else:
            self.report({"INFO"}, "Invalid Type Selection")
            return {'CANCELLED'}
        return {'FINISHED'}

