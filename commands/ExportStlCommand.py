import adsk.core
import adsk.fusion
#import adsk.cam

from pathlib import Path
from typing import cast

# Import the entire apper package
from ..apper import apper
from .. import config


# Command / input IDs (centralized constants)
EXPORT_BASE_FOLDER_INPUT_ID = 'export_base_folder_input_id'
ROOT_COMPONENT_INPUT_ID = 'root_component_input_id'
EXPORT_PNG_INPUT_ID = 'export_png_files_input_id'
PNG_SUB_PATH_INPUT_ID = 'png_sub_path_input_id'
EXPORT_STL_INPUT_ID = 'export_stl_filest_input_id'
STL_SUB_PATH_INPUT_ID = 'stl_sub_path_input_id'
FULLWIDTH_TEXTBOX_ID = 'fullWidth_textBox'
IMAGE_WIDTH_INPUT_ID = 'image_width_input_id'
IMAGE_HEIGHT_INPUT_ID = 'image_height_input_id'

# Class for a Fusion 360 Command
# Place your program logic here
# Delete the line that says "pass" for any method you want to use
class ExportStlCommand(apper.Fusion360CommandBase):

    # Run whenever a user makes any change to a value or selection in the addin UI
    # Commands in here will be run through the Fusion processor and changes will be reflected in  Fusion graphics area
    def on_preview(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs, args, input_values):
        pass

    # Run after the command is finished.
    # Can be used to launch another command automatically or do other clean up.
    def on_destroy(self, command: adsk.core.Command, inputs, reason, input_values):
        pass




    # Function to validate the current state of the inputs.
    #    Args:
    #        command: reference to the command object
    #        inputs: quick reference directly to the commandInputs object
    #        args: All of the args associated with the CommandEvent
    #        input_values: Opinionated dictionary of the useful values a user entered.  The key is the command_id.
    def validate_inputs(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs,
                        args: adsk.core.ValidateInputsEventArgs, input_values: dict) -> bool:
        

        is_stl_export_enabled: bool = input_values.get(EXPORT_STL_INPUT_ID, False)
        stl_sub_path: str = input_values.get(STL_SUB_PATH_INPUT_ID, "")
        stl_sub_path_input: adsk.core.StringValueCommandInput = cast(adsk.core.StringValueCommandInput, inputs.itemById(STL_SUB_PATH_INPUT_ID))
        stl_sub_path_input.isValueError = False
        if is_stl_export_enabled:
            if stl_sub_path is None or len(stl_sub_path.strip()) == 0 or not Path(stl_sub_path).resolve(strict=False):
                stl_sub_path_input.isValueError = True

        is_png_export_enabled: bool = input_values.get(EXPORT_PNG_INPUT_ID, False)
        png_sub_path: str = input_values.get(PNG_SUB_PATH_INPUT_ID, "")
        png_sub_path_input: adsk.core.StringValueCommandInput = cast(adsk.core.StringValueCommandInput, inputs.itemById(PNG_SUB_PATH_INPUT_ID))
        png_sub_path_input.isValueError = False
        if is_png_export_enabled:
            if png_sub_path is None or len(png_sub_path.strip()) == 0 or not Path(png_sub_path).resolve(strict=False):
                png_sub_path_input.isValueError = True

        # Either one need to be selected
        if (is_png_export_enabled is False) and (is_stl_export_enabled is False):
            return False

        image_width = input_values.get(IMAGE_WIDTH_INPUT_ID, None)
        if image_width is None:
            return False

        image_height = input_values.get(IMAGE_HEIGHT_INPUT_ID, None)
        if image_height is None:
            return False

        # check if at least one component is selected
        all_selections = input_values.get(ROOT_COMPONENT_INPUT_ID, None)
        selectionValid:bool = bool(all_selections and len(all_selections) > 0)
        return (selectionValid and not png_sub_path_input.isValueError and not stl_sub_path_input.isValueError)




    def check_folder_validity(self, path: Path) -> str:
        # 1. Prüfen, ob Pfad syntaktisch valide ist (z. B. keine ungültigen Zeichen)
        try:
            path.resolve(strict=False)
        except Exception as e:
            return f"Ungültiger Pfad: {e}"

        # 2. Prüfen, ob bereits eine Datei mit diesem Namen existiert
        if path.exists():
            if path.is_file():
                return "Eine Datei mit diesem Namen existiert bereits. Abbruch."

            elif not path.is_dir():
                return "Ist weder Verzeichnis noch Datei."

        # 3. Create folder if not existing
        else:
            try:
                path.mkdir(parents=True)
            except Exception as e:
                return f"Verzeichnis konnte nicht angelegt werden: {e}"

        # 5. Prüfen, ob Verzeichnis schreibbar ist (Testdatei-Methode)
        try:
            testfile = path / ".deleteme.tmp"
            with open(testfile, "w") as f:
                f.write("test")
            testfile.unlink()
        except Exception as e:
            return f"Verzeichnis ist nicht schreibbar: {e}"
        
        return None



    def exportStl(self, fileName: str, occ: adsk.fusion.Occurrence):
        # Get a reference to all relevant application objects in a dictionary
        ao = apper.AppObjects()

        # get active design  
        app: adsk.core.Application = ao.app      
        product: adsk.core.Product = app.activeProduct
        design: adsk.fusion.Design = adsk.fusion.Design.cast(product)

        # create a single exportManager instance
        exportMgr: adsk.fusion.ExportManager = design.exportManager

        # traverse all components and hide those not matching occ but assure occ is visible
        root_comp: adsk.fusion.Component = design.rootComponent
        for other_occ in root_comp.occurrences:
            self.set_occurrence_recursive(other_occ, predicate=lambda o: o == occ)

        # create stl exportOptions
        stlExportOptions: adsk.fusion.STLExportOptions = exportMgr.createSTLExportOptions(occ, fileName)                

        stlExportOptions = exportMgr.createSTLExportOptions(occ, fileName)                
        exportMgr.execute(stlExportOptions)


    
    def set_occurrence_recursive(self, occurrence, predicate):
        """
        Recursively set visibility for an occurrence and its children.

        Parameters:
        - occurrence: the occurrence to process
        - predicate: a callable that receives an occurrence and returns True to show it or False to hide it

        """
        
        occurrence.isLightBulbOn = bool(predicate(occurrence)) # Decide visibility using predicate
        # Rekursiv alle Unter-Occurrences durchlaufen
        for child_occ in occurrence.childOccurrences:
            self.set_occurrence_recursive(child_occ, predicate=predicate)



    def exportPng(self, fileName: str, occ: adsk.fusion.Occurrence, image_width: int, image_height: int):
        # Get a reference to all relevant application objects in a dictionary
        ao = apper.AppObjects()

        # get active design  
        app: adsk.core.Application = ao.app      
        product: adsk.core.Product = app.activeProduct
        design: adsk.fusion.Design = adsk.fusion.Design.cast(product) # Product has to be of type Design

        # traverse all components and hide those not matching occ but assure occ is visible
        root_comp: adsk.fusion.Component = design.rootComponent
        for other_occ in root_comp.occurrences:
            self.set_occurrence_recursive(other_occ, predicate=lambda o: o == occ)

        # Kamera auf BoundingBox der Komponente zentrieren
        view: adsk.core.Viewport = app.activeViewport
        #bbox = occ.boundingBox
        view.fit()

        # Exportieren
        view.saveAsImageFile(fileName, image_width, image_height)
        







    def export_components(self, components, image_width: int, image_height: int, is_png_export_enabled:bool, png_path:Path, is_stl_export_enabled:bool, stl_path:Path):

        # Get a reference to all relevant application objects in a dictionary
        ao = apper.AppObjects()

        # Set styles of progress dialog.
        progressDialog = ao.ui.createProgressDialog()
        progressDialog.cancelButtonText = 'Cancel'
        progressDialog.isBackgroundTranslucent = False
        progressDialog.isCancelButtonShown = True
        # Show dialog
        progressDialog.show('Progress Dialog', '%p (%v of %m components exported)', 0, len(components), 1)
        for occ in components:

            # Check if the user pressed the cancel button.
            if progressDialog.wasCancelled:
                break

            if is_stl_export_enabled:
                self.exportStl(str(stl_path / f"{occ.component.name}.stl"), occ)

            if is_png_export_enabled:
                self.exportPng(str(png_path / f"{occ.component.name}.png"), occ, image_width, image_height)

            # Update progress value of progress dialog
            progressDialog.progressValue += 1

        # Hide the progress dialog at the end.
        progressDialog.hide()

        ao.ui.messageBox(
            'Number of files exported: {} \n'.format(len(components)) +
            'PNG export active:  {} \n'.format(png_path if is_png_export_enabled else 'no') +
            'STL export active:  {} \n'.format(stl_path if is_stl_export_enabled else 'no'),
            "Export success", 
            adsk.core.MessageBoxButtonTypes.OKButtonType, 
            adsk.core.MessageBoxIconTypes.WarningIconType)




    # Run when the user presses OK
    # This is typically where your main program logic would go
    #    Args:
    #        command: reference to the command object
    #        inputs: quick reference directly to the commandInputs object
    #        args: All of the args associated with the CommandEvent
    #        input_values: Opinionated dictionary of the useful values a user entered.  The key is the command_id.
    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs,
                        args: adsk.core.ValidateInputsEventArgs, input_values: dict):
     

        # Get a reference to all relevant application objects in a dictionary
        ao = apper.AppObjects()
    
        # Set styles of file dialog.   
        folderDlg = ao.ui.createFolderDialog()
        folderDlg.title = 'Choose Export Folder' 
        folderDlg.initialDirectory = str(Path.home())  # Set initial directory to user's home folder

        # Show folder dialog
        dlgResult = folderDlg.showDialog()
        if dlgResult == adsk.core.DialogResults.DialogOK:

            path = Path(folderDlg.folder)
            base_path_validity:str = self.check_folder_validity(path)
            if base_path_validity is not None:
                ao.ui.messageBox('The selected base folder is not valid: {} \n'.format(base_path_validity))
                return

            is_png_export_enabled: bool = input_values.get(EXPORT_PNG_INPUT_ID, False)
            png_sub_path: str = input_values.get(PNG_SUB_PATH_INPUT_ID, "")
            png_path = Path(folderDlg.folder + png_sub_path)
            if is_png_export_enabled:
                png_path_validity:str = self.check_folder_validity(png_path)
                if png_path_validity is not None:
                    ao.ui.messageBox('The selected base folder is not valid: {} \n'.format(png_path_validity))
                    return

            is_stl_export_enabled: bool = input_values.get(EXPORT_STL_INPUT_ID, False)
            stl_sub_path: str = input_values.get(STL_SUB_PATH_INPUT_ID, "")
            stl_path = Path(folderDlg.folder + stl_sub_path)
            if is_stl_export_enabled:
                stl_path_validity:str = self.check_folder_validity(stl_path)
                if stl_path_validity is not None:
                    ao.ui.messageBox('The selected base folder is not valid: {} \n'.format(stl_path_validity))
                    return

            image_width = input_values.get(IMAGE_WIDTH_INPUT_ID, None)
            image_height = input_values.get(IMAGE_HEIGHT_INPUT_ID, None)
            components = input_values.get(ROOT_COMPONENT_INPUT_ID)

            self.export_components(components, image_width, image_height, is_png_export_enabled, png_path, is_stl_export_enabled, stl_path)

        else:
            ao.ui.messageBox(
                'Export aborted. No files written.',
                "Aborted", 
                adsk.core.MessageBoxButtonTypes.OKButtonType, 
                adsk.core.MessageBoxIconTypes.WarningIconType)






    # Run when the user selects your command icon from the Fusion 360 UI
    # Typically used to create and display a command dialog box
    # The following is a basic sample of a dialog UI
    #    Args:
    #        command: reference to the command object
    #        inputs: quick reference directly to the commandInputs object
    def on_create(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs):

        ao = apper.AppObjects()

        # Create a message that spans the entire width of the dialog by leaving out the "name" argument.
        message = '<div align=center>Exports all components in current project to file system for publishing them on Github</dic>' \
                  '<div align=left>1. Select all components you want to export</div>' \
                  '<div align=left>2. Select root folder to export to</div>' \
                  '<div align=left>3. Check STL and optionally enter a subfolder name for exporting meshes</div>' \
                  '<div align=left>4. Check PNG and optionally enter subfolder name for exporting previews</div>' \
                  '<div align=center>See <a href="http://github.com/smengerl/fusion_exporter">Github project</a> for more details</div>'
        inputs.addTextBoxCommandInput(FULLWIDTH_TEXTBOX_ID, '', message, 7, True)            


        # Select components to export...
        # Title: id, name, command prompt
        selectionCommand: adsk.core.SelectionCommandInput = inputs.addSelectionInput(ROOT_COMPONENT_INPUT_ID, 'Component to export', 'Select all the components to export')
        if (selectionCommand is not None):
            selectionCommand.addSelectionFilter(adsk.core.SelectionCommandInput.Occurrences)
            selectionCommand.addSelectionFilter(adsk.core.SelectionCommandInput.RootComponents)
            selectionCommand.setSelectionLimits(1, 0)  # Min 1, max unlimited selections


        # Select file path to export to...
        baseFolderInputCommand: adsk.core.BoolValueCommandInput = inputs.addBoolValueInput(EXPORT_BASE_FOLDER_INPUT_ID, 'Select folder', False, "", True)

        # Other Input types
        inputs.addBoolValueInput(EXPORT_PNG_INPUT_ID, 'Export PNG files', True, "", True)
        inputs.addStringValueInput(PNG_SUB_PATH_INPUT_ID, 'PNG file path:', '/png')

        inputs.addBoolValueInput(EXPORT_STL_INPUT_ID, 'Export STL files', True, "", True)
        inputs.addStringValueInput(STL_SUB_PATH_INPUT_ID, 'STL file path:', '/stl')

        inputs.addIntegerSpinnerCommandInput(IMAGE_WIDTH_INPUT_ID, 'Image width:', 100, 1000, 10, 800)
        inputs.addIntegerSpinnerCommandInput(IMAGE_HEIGHT_INPUT_ID, 'Image height:', 100, 1000, 10, 600)
