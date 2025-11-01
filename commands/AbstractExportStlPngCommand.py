import adsk.core
from pathlib import Path
from typing import cast
from abc import ABC, abstractmethod 

from ..apper import apper
from . import export_helpers
from .. import app_context
from .. import config

# Input IDs
COMPONENTS_NAME_INPUT_ID = 'components_input_id'
EXPORT_PNG_INPUT_ID = 'export_png_files_input_id'
PNG_SUB_PATH_INPUT_ID = 'png_sub_path_input_id'
EXPORT_ZSB_INPUT_ID = 'export_zsb_filest_input_id'
ZSB_SUB_PATH_INPUT_ID = 'zsb_sub_path_input_id'
EXPORT_FULL_ZSB_INPUT_ID = 'export_full_zsb_input_id'
EXPORT_FULL_ZSB_NAME_INPUT_ID = 'export_full_zsb_name_input_id'
ROOT_COMPONENT_NAME_INPUT_ID = 'root_component_name_input_id'
EXPORT_STL_INPUT_ID = 'export_stl_filest_input_id'
STL_SUB_PATH_INPUT_ID = 'stl_sub_path_input_id'
FULLWIDTH_TEXTBOX_ID = 'fullWidth_textBox'
IMAGE_WIDTH_INPUT_ID = 'image_width_input_id'
IMAGE_HEIGHT_INPUT_ID = 'image_height_input_id'
INCLUDE_REFERENCED_COMPONENTS_INPUT_ID = 'transparency_input_id'
INCLUDE_FLAGGED_COMPONENTS_INPUT_ID = 'include_flagged_components_input_id'

class AbstractExportStlPngCommand(ABC, apper.Fusion360CommandBase):
    """UI command: collect inputs and delegate export work to export_helpers."""


    @abstractmethod
    def selectComponents(self, selection_input: adsk.core.SelectionCommandInput):
        pass



    def on_preview(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        return

    def on_destroy(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, reason, input_values):
        return

    def validate_inputs(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs,
                        args: adsk.core.ValidateInputsEventArgs, input_values: dict) -> bool:
        # Keep existing lightweight validation: paths present when enabled, image sizes, selection
        is_stl = input_values.get(EXPORT_STL_INPUT_ID, config.EXPORT_STL_DEFAULT_VALUE)
        stl_sub = input_values.get(STL_SUB_PATH_INPUT_ID, config.STL_SUB_PATH_DEFAULT_VALUE)
        stl_input = cast(adsk.core.StringValueCommandInput, inputs.itemById(STL_SUB_PATH_INPUT_ID))
        stl_input.isValueError = False
        if is_stl and (stl_sub is None or len(stl_sub.strip()) == 0):
            stl_input.isValueError = True

        is_png = input_values.get(EXPORT_PNG_INPUT_ID, config.EXPORT_PNG_DEFAULT_VALUE)
        png_sub = input_values.get(PNG_SUB_PATH_INPUT_ID, config.PNG_SUB_PATH_DEFAULT_VALUE)
        png_input = cast(adsk.core.StringValueCommandInput, inputs.itemById(PNG_SUB_PATH_INPUT_ID))
        png_input.isValueError = False
        if is_png and (png_sub is None or len(png_sub.strip()) == 0):
            png_input.isValueError = True

        if not (is_png or is_stl or is_): 
            return False
        

        root_name = input_values.get(ROOT_COMPONENT_NAME_INPUT_ID, config.ROOT_COMPONENT_NAME_DEFAULT_VALUE)
        root_name_input = cast(adsk.core.StringValueCommandInput, inputs.itemById(ROOT_COMPONENT_NAME_INPUT_ID))
        root_name_input.isValueError = False
        if root_name is None or len(root_name.strip()) == 0: # Error if not specified
            root_name_input.isValueError = True



        w = input_values.get(IMAGE_WIDTH_INPUT_ID, None)
        h = input_values.get(IMAGE_HEIGHT_INPUT_ID, None)
        if w is None or h is None:
            return False

        sels = input_values.get(COMPONENTS_NAME_INPUT_ID, None)
        if not (sels and len(sels) > 0):
            return False

        return not (png_input.isValueError or stl_input.isValueError)

    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values: dict):
        ao = apper.AppObjects()

        folder_dlg = ao.ui.createFolderDialog()
        folder_dlg.title = 'Choose Export Folder'
        folder_dlg.initialDirectory = str(Path.home())
        result = folder_dlg.showDialog()

        base = Path(folder_dlg.folder)
        err = export_helpers.check_folder_validity(base)
        if err:
            ao.ui.messageBox(f'Invalid base folder: {base} - {err}')  # type: ignore
            return

        export_png = input_values.get(EXPORT_PNG_INPUT_ID, config.EXPORT_PNG_DEFAULT_VALUE)
        png_sub = input_values.get(PNG_SUB_PATH_INPUT_ID, config.PNG_SUB_PATH_DEFAULT_VALUE)
        png_path = (base / png_sub.lstrip('/')) if export_png else base
        if export_png:
            err = export_helpers.check_folder_validity(png_path)
            if err:
                ao.ui.messageBox(f'Invalid PNG folder: {png_path} - {err}')  # type: ignore
                return

        export_zsb = input_values.get(EXPORT_ZSB_INPUT_ID, config.EXPORT_ZSB_DEFAULT_VALUE)
        zsb_sub = input_values.get(ZSB_SUB_PATH_INPUT_ID, config.ZSB_SUB_PATH_DEFAULT_VALUE)
        zsb_path = (base / zsb_sub.lstrip('/')) if export_zsb else base
        if export_zsb:
            err = export_helpers.check_folder_validity(zsb_path)
            if err:
                ao.ui.messageBox(f'Invalid ZSB folder: {zsb_path} - {err}')  # type: ignore
                return
            
        full_zsb_export = input_values.get(EXPORT_FULL_ZSB_INPUT_ID, config.EXPORT_FULL_ZSB_DEFAULT_VALUE)
        full_zsb_name = input_values.get(EXPORT_FULL_ZSB_NAME_INPUT_ID, config.EXPORT_FULL_ZSB_NAME_DEFAULT_VALUE)
        full_zsb_path = base / full_zsb_name
        if full_zsb_export:
            err = export_helpers.check_folder_validity(full_zsb_path)
            if err:
                ao.ui.messageBox(f'Invalid full ZSB folder: {full_zsb_path} - {err}')  # type: ignore
                return

        export_stl = input_values.get(EXPORT_STL_INPUT_ID, config.EXPORT_STL_DEFAULT_VALUE)
        stl_sub = input_values.get(STL_SUB_PATH_INPUT_ID, config.STL_SUB_PATH_DEFAULT_VALUE)
        stl_path = (base / stl_sub.lstrip('/')) if export_stl else base
        if export_stl:
            err = export_helpers.check_folder_validity(stl_path)
            if err:
                ao.ui.messageBox(f'Invalid STL folder: {stl_path} -  {err}')  # type: ignore
                return

        width = input_values.get(IMAGE_WIDTH_INPUT_ID, config.IMAGE_WIDTH_DEFAULT_VALUE)
        height = input_values.get(IMAGE_HEIGHT_INPUT_ID, config.IMAGE_HEIGHT_DEFAULT_VALUE)
        if width is None or height is None:
            ao.ui.messageBox('Image size not specified')  # type: ignore
            return

        components: adsk.core.Occurence = input_values.get(COMPONENTS_NAME_INPUT_ID)
        if components is None:
            ao.ui.messageBox('No components selected')  # type: ignore
            return
        
        try:
            w = int(width)
            h = int(height)
        except Exception:
            ao.ui.messageBox('Invalid image size values')  # type: ignore
            return

        include_referenced_components = input_values.get(INCLUDE_REFERENCED_COMPONENTS_INPUT_ID, config.INCLUDE_REFERENCED_COMPONENTS_DEFAULT_VALUE)
        if not isinstance(include_referenced_components, bool):
            ao.ui.messageBox(f'Invalid option to include referenced components: {include_referenced_components}: {type(include_referenced_components).__name__}')  # type: ignore
            return
        include_flagged_components = input_values.get(INCLUDE_FLAGGED_COMPONENTS_INPUT_ID, config.INCLUDE_FLAGGED_COMPONENTS_DEFAULT_VALUE)
        if not isinstance(include_flagged_components, bool):
            ao.ui.messageBox(f'Invalid option to include flagged components {include_flagged_components}: {type(include_flagged_components).__name__}')  # type: ignore
            return
        
        root_name = input_values.get(ROOT_COMPONENT_NAME_INPUT_ID, config.ROOT_COMPONENT_NAME_DEFAULT_VALUE)
 

        # Save preferences for next time
        pref = app_context.get_preferences()
        pref[config.EXPORT_STL_KEY] = export_stl
        pref[config.STL_SUB_PATH_KEY] = stl_path
        pref[config.EXPORT_ZSB_KEY] = export_zsb
        pref[config.ZSB_SUB_PATH_KEY] = zsb_path
        pref[config.EXPORT_FULL_ZSB_KEY] = full_zsb_export
        pref[config.EXPORT_FULL_ZSB_NAME_KEY] = full_zsb_name
        pref[config.EXPORT_PNG_KEY] = export_png
        pref[config.PNG_SUB_PATH_KEY] = png_path
        pref[config.INCLUDE_REFERENCED_COMPONENTS_KEY] = include_referenced_components
        pref[config.INCLUDE_FLAGGED_COMPONENTS_KEY] = include_flagged_components
        pref[config.IMAGE_WIDTH_KEY] = w
        pref[config.IMAGE_HEIGHT_KEY] = h
        pref[config.ROOT_COMPONENT_NAME_KEY] = root_name

        # Delegate actual export logic to helper module
        export_helpers.export_components(
            components, 
            include_referenced_components, include_flagged_components,
            root_name,
            export_stl, stl_path, 
            export_zsb, zsb_path, 
            full_zsb_export, full_zsb_name,
            export_png, png_path, 
            w, h)




    def on_create(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs):
        ao = apper.AppObjects()

        sel = inputs.addSelectionInput(COMPONENTS_NAME_INPUT_ID, 'Components', 'Select components to export')
        if sel:
            sel.addSelectionFilter(adsk.core.SelectionCommandInput.Occurrences)
            sel.setSelectionLimits(1, 0)
            self.selectComponents(sel)

        pref: dict = app_context.get_preferences()
            
        inputs = command.commandInputs

        inputs.addBoolValueInput(INCLUDE_REFERENCED_COMPONENTS_INPUT_ID, 'Include screws and referenced components:', True, '', pref[config.INCLUDE_REFERENCED_COMPONENTS_KEY])
        inputs.addBoolValueInput(INCLUDE_FLAGGED_COMPONENTS_INPUT_ID, 'Include "_*" components:', True, '', pref[config.INCLUDE_FLAGGED_COMPONENTS_KEY])

        inputs.addIntegerSpinnerCommandInput(IMAGE_WIDTH_INPUT_ID, 'Picture width:', 100, 2000, 1, pref[config.IMAGE_WIDTH_KEY])
        inputs.addIntegerSpinnerCommandInput(IMAGE_HEIGHT_INPUT_ID, 'Picture height:', 100, 2000, 1, pref[config.IMAGE_HEIGHT_KEY])
        inputs.addStringValueInput(ROOT_COMPONENT_NAME_INPUT_ID, 'Root compoent name:', pref[config.ROOT_COMPONENT_NAME_KEY])

        stl_group = inputs.addGroupCommandInput('stl_group_id', 'Component STL Export')
        stl_group.children.addBoolValueInput(EXPORT_STL_INPUT_ID, 'Export STLs', True, '', pref[config.EXPORT_STL_KEY])
        stl_group.children.addStringValueInput(STL_SUB_PATH_INPUT_ID, 'Subfolder:', pref[config.STL_SUB_PATH_KEY])

        zsb_group = inputs.addGroupCommandInput('zsb_group_id', 'Assembly pictures (PNG) = Components containing further compoenents')
        zsb_group.children.addBoolValueInput(EXPORT_ZSB_INPUT_ID, 'Export assembly pictures:', True, '', pref[config.EXPORT_ZSB_KEY])
        zsb_group.children.addStringValueInput(ZSB_SUB_PATH_INPUT_ID, 'Subfolder:', pref[config.ZSB_SUB_PATH_KEY])
        zsb_group.children.addBoolValueInput(EXPORT_FULL_ZSB_INPUT_ID, 'Include export of full assembly', True, '', pref[config.EXPORT_FULL_ZSB_KEY])
        zsb_group.children.addStringValueInput(EXPORT_FULL_ZSB_NAME_INPUT_ID, 'Full assembly name:', pref[config.EXPORT_FULL_ZSB_NAME_KEY])

        png_group = inputs.addGroupCommandInput('png_group_id', 'Component pictures (PNG)')
        png_group.children.addBoolValueInput(EXPORT_PNG_INPUT_ID, 'Export component pictures', True, '', pref[config.EXPORT_PNG_KEY])
        png_group.children.addStringValueInput(PNG_SUB_PATH_INPUT_ID, 'Subfolder:', pref[config.PNG_SUB_PATH_KEY])
        

