import adsk.core
from pathlib import Path
from typing import cast

from ..apper import apper
from . import export_helpers


# Input IDs
ROOT_COMPONENT_INPUT_ID = 'root_component_input_id'
EXPORT_PNG_INPUT_ID = 'export_png_files_input_id'
PNG_SUB_PATH_INPUT_ID = 'png_sub_path_input_id'
EXPORT_STL_INPUT_ID = 'export_stl_filest_input_id'
STL_SUB_PATH_INPUT_ID = 'stl_sub_path_input_id'
FULLWIDTH_TEXTBOX_ID = 'fullWidth_textBox'
IMAGE_WIDTH_INPUT_ID = 'image_width_input_id'
IMAGE_HEIGHT_INPUT_ID = 'image_height_input_id'
TRANSPARENCY_INPUT_ID = 'transparency_input_id'

class ExportStlPngCommand(apper.Fusion360CommandBase):
    """UI command: collect inputs and delegate export work to export_helpers."""

    def on_preview(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        return

    def on_destroy(self, command: adsk.core.Command, inputs, reason, input_values):
        return

    def validate_inputs(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs,
                        args: adsk.core.ValidateInputsEventArgs, input_values: dict) -> bool:
        # Keep existing lightweight validation: paths present when enabled, image sizes, selection
        is_stl = input_values.get(EXPORT_STL_INPUT_ID, False)
        stl_sub = input_values.get(STL_SUB_PATH_INPUT_ID, "")
        stl_input = cast(adsk.core.StringValueCommandInput, inputs.itemById(STL_SUB_PATH_INPUT_ID))
        stl_input.isValueError = False
        if is_stl and (stl_sub is None or len(stl_sub.strip()) == 0):
            stl_input.isValueError = True

        is_png = input_values.get(EXPORT_PNG_INPUT_ID, False)
        png_sub = input_values.get(PNG_SUB_PATH_INPUT_ID, "")
        png_input = cast(adsk.core.StringValueCommandInput, inputs.itemById(PNG_SUB_PATH_INPUT_ID))
        png_input.isValueError = False
        if is_png and (png_sub is None or len(png_sub.strip()) == 0):
            png_input.isValueError = True

        if not (is_png or is_stl):
            return False

        w = input_values.get(IMAGE_WIDTH_INPUT_ID, None)
        h = input_values.get(IMAGE_HEIGHT_INPUT_ID, None)
        if w is None or h is None:
            return False

        sels = input_values.get(ROOT_COMPONENT_INPUT_ID, None)
        if not (sels and len(sels) > 0):
            return False

        return not (png_input.isValueError or stl_input.isValueError)

    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values: dict):
        ao = apper.AppObjects()

        folder_dlg = ao.ui.createFolderDialog()
        folder_dlg.title = 'Choose Export Folder'
        folder_dlg.initialDirectory = str(Path.home())
        result = folder_dlg.showDialog()
        if result != adsk.core.DialogResults.DialogOK:
            ao.ui.messageBox('Export aborted by user')  # type: ignore
            return

        base = Path(folder_dlg.folder)
        err = export_helpers.check_folder_validity(base)
        if err:
            ao.ui.messageBox(f'Invalid base folder: {err}')  # type: ignore
            return

        export_png = input_values.get(EXPORT_PNG_INPUT_ID, False)
        png_sub = input_values.get(PNG_SUB_PATH_INPUT_ID, '')
        png_path = (base / png_sub.lstrip('/')) if export_png else base
        if export_png:
            err = export_helpers.check_folder_validity(png_path)
            if err:
                ao.ui.messageBox(f'Invalid PNG folder: {err}')  # type: ignore
                return

        export_stl = input_values.get(EXPORT_STL_INPUT_ID, False)
        stl_sub = input_values.get(STL_SUB_PATH_INPUT_ID, '')
        stl_path = (base / stl_sub.lstrip('/')) if export_stl else base
        if export_stl:
            err = export_helpers.check_folder_validity(stl_path)
            if err:
                ao.ui.messageBox(f'Invalid STL folder: {err}')  # type: ignore
                return

        width = input_values.get(IMAGE_WIDTH_INPUT_ID, None)
        height = input_values.get(IMAGE_HEIGHT_INPUT_ID, None)
        if width is None or height is None:
            ao.ui.messageBox('Image size not specified')  # type: ignore
            return

        components = input_values.get(ROOT_COMPONENT_INPUT_ID)
        if components is None:
            ao.ui.messageBox('No components selected')  # type: ignore
            return

        try:
            w = int(width)
            h = int(height)
        except Exception:
            ao.ui.messageBox('Invalid image size values')  # type: ignore
            return

        transparency = input_values.get(TRANSPARENCY_INPUT_ID, False)
        if transparency is None:
            ao.ui.messageBox('Invalid transparency option')  # type: ignore
            return
        
        # Delegate actual export logic to helper module
        export_helpers.export_components(components, export_stl, stl_path, export_png, png_path, w, h, transparency)


    def selectComponents(self, selection_input: adsk.core.SelectionCommandInput):
        # Pre-select all currently visible occurrences
        try:
            app = ao.app
            product = app.activeProduct
            design = adsk.fusion.Design.cast(product)
            root = design.rootComponent
            occs = root.occurrences
            for i in range(occs.count):
                occ = occs.item(i)
                # Only add occurrences that are visible (light bulb on)
                if getattr(occ, 'isLightBulbOn', True):
                    sel.addSelection(occ)
        except Exception:
            # Best-effort: if anything fails, leave selection empty and continue
            pass


    def on_create(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs):
        ao = apper.AppObjects()

        msg = (
            '<div align=center>Exports components for publishing to GitHub</div>'
            '<div align=left>1. Select components to export</div>'
            '<div align=left>2. Choose options</div>'
            '<div align=left>3. Hit OK and select target folder</div>'
        )
        inputs.addTextBoxCommandInput(FULLWIDTH_TEXTBOX_ID, '', msg, 6, True)

        sel = inputs.addSelectionInput(ROOT_COMPONENT_INPUT_ID, 'Components', 'Select components to export')
        if sel:
            sel.addSelectionFilter(adsk.core.SelectionCommandInput.Occurrences)
            sel.setSelectionLimits(1, 0)

            selectComponents(sel)

        
        inputs.addBoolValueInput(EXPORT_STL_INPUT_ID, 'Export STL files', True, '', True)
        inputs.addStringValueInput(STL_SUB_PATH_INPUT_ID, 'STL subpath:', '/stl')

        inputs.addBoolValueInput(EXPORT_PNG_INPUT_ID, 'Export PNG files', True, '', True)
        inputs.addStringValueInput(PNG_SUB_PATH_INPUT_ID, 'PNG subpath:', '/png')
        inputs.addIntegerSpinnerCommandInput(IMAGE_WIDTH_INPUT_ID, 'Image width:', 100, 2000, 1, 800)
        inputs.addIntegerSpinnerCommandInput(IMAGE_HEIGHT_INPUT_ID, 'Image height:', 100, 2000, 1, 600)
        inputs.addBoolValueInput(TRANSPARENCY_INPUT_ID, 'Transparent background:', True, '', True)

