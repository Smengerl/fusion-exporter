import adsk.core
#import adsk.fusion
#import adsk.cam

from pathlib import Path
from typing import Optional

# Import the entire apper package
from ..apper import apper
from .. import config

# Command / input IDs (centralized constants)
SELECTION_INPUT_ID = 'selection_input_id'
TEXT_BOX_INPUT_ID = 'text_box_input_id'
ROOT_COMPONENT_INPUT_ID = 'root_component_input_id'
EXPORT_PNG_INPUT_ID = 'export_png_files_input_id'
PNG_SUB_PATH_INPUT_ID = 'png_sub_path_input_id'
EXPORT_STL_INPUT_ID = 'export_stl_filest_input_id'
STL_SUB_PATH_INPUT_ID = 'stl_sub_path_input_id'
FULLWIDTH_TEXTBOX_ID = 'fullWidth_textBox'
STRING_INPUT_ID = 'string_input_id'


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

    # Run when any input is changed.
    # Can be used to check a value and then update the add-in UI accordingly
    #    Args:
    #        adsk.core.Command command: reference to the command object
    #        adsk.core.CommandInputs inputs: quick reference directly to the commandInputs object
    #        adsk.core.ValidateInputsEventArgs args: All of the args associated with the CommandEvent
    #        dict input_values: Opinionated dictionary of the useful values a user entered.  The key is the command_id.
    def on_input_changed(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs,
                        args: adsk.core.ValidateInputsEventArgs, input_values: dict):

        all_selections = input_values.get(SELECTION_INPUT_ID, None)
        text_box_input: Optional[adsk.core.CommandInput] = inputs.itemById(TEXT_BOX_INPUT_ID) if inputs else None

        if all_selections is not None and len(all_selections) > 0:
            # Update the text of the string value input to show the type of object selected
            the_first_selection = all_selections[0]
            if text_box_input is not None:
                # use getattr to avoid attribute errors on selection proxies
                text_box_input.text = getattr(the_first_selection, 'objectType', str(the_first_selection))
        else:
            # No selection -> clear or set a default message
            if text_box_input is not None:
                text_box_input.text = 'Nothing Selected'



    # Function to validate the current state of the inputs.
    #    Args:
    #        command: reference to the command object
    #        inputs: quick reference directly to the commandInputs object
    #        args: All of the args associated with the CommandEvent
    #        input_values: Opinionated dictionary of the useful values a user entered.  The key is the command_id.
    def validate_inputs(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs,
                        args: adsk.core.ValidateInputsEventArgs, input_values: dict) -> bool:

        all_selections = input_values.get(ROOT_COMPONENT_INPUT_ID, None)
        return bool(all_selections and len(all_selections) > 0)


    # Run when the user presses OK
    # This is typically where your main program logic would go
    #    Args:
    #        command: reference to the command object
    #        inputs: quick reference directly to the commandInputs object
    #        args: All of the args associated with the CommandEvent
    #        input_values: Opinionated dictionary of the useful values a user entered.  The key is the command_id.
    def on_execute(self, command: adsk.core.Command, inputs: adsk.core.CommandInputs,
                        args: adsk.core.ValidateInputsEventArgs, input_values: dict):
        # Get the values from the user input
        # the_value = input_values.get('value_input_id')
        png_export_active = input_values.get(EXPORT_PNG_INPUT_ID)
        stl_export_active = input_values.get(EXPORT_STL_INPUT_ID)
        all_selections = input_values.get(ROOT_COMPONENT_INPUT_ID)
        string_input = input_values.get(STRING_INPUT_ID)



        # Selections are returned as a list so lets get the first one and its name
        if all_selections is not None and len(all_selections) > 0:
            the_first_selection = all_selections[0]
            the_selection_type = getattr(the_first_selection, 'objectType', str(the_first_selection))
        else:
            the_selection_type = 'Nothing Selected'


        # Get a reference to all relevant application objects in a dictionary
        ao = apper.AppObjects()

        #converted_value = ao.units_manager.formatInternalValue(the_value, 'in', True)

        ao.ui.messageBox(
                            'PNG export active:  {} \n'.format(png_export_active) +
                            'STL export active:  {} \n'.format(stl_export_active) +
                            'The string you typed was:  {} \n'.format(string_input) +
                            'The type of the first object you selected is:  {} \n'.format(the_selection_type),
    #                     'The drop down item you selected is:  {}'.format(the_drop_down)
                            "Title")

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
            selectionCommand.addSelectionFilter("Occurrences")
            selectionCommand.addSelectionFilter("RootComponents")
            selectionCommand.setSelectionLimits(1, 0)  # Min 1, max unlimited selections


        # Select file path to export to...



        # Create a default value using a string
        # default_value = adsk.core.ValueInput.createByString('1.0 in')

        # Get teh user's current units
        # default_units = ao.units_manager.defaultLengthUnits

        # Create a value input.  This will respect units and user defined equation input.
        # inputs.addValueInput('value_input_id', '*Sample* Value Input', default_units, default_value)

        # Other Input types
        inputs.addBoolValueInput(EXPORT_PNG_INPUT_ID, 'Export PNG files', True, "", True)
        inputs.addStringValueInput(PNG_SUB_PATH_INPUT_ID, 'PNG file path:', 'Some Default Value')

        inputs.addBoolValueInput(EXPORT_STL_INPUT_ID, 'Export STL files', True, "", True)
        inputs.addStringValueInput(STL_SUB_PATH_INPUT_ID, 'STL file path:', 'Some Default Value')




        # Create a string value input.
        inputs.addStringValueInput(STRING_INPUT_ID, 'Path', 'Some Default Value')

        # Read Only Text Box
        #inputs.addTextBoxCommandInput(TEXT_BOX_INPUT_ID, 'Selection Type: ', 'Nothing Selected', 1, True)

        # Create a Drop Down
        #drop_style = adsk.core.DropDownStyles.TextListDropDownStyle
        #drop_down_input = inputs.addDropDownCommandInput('drop_down_input_id', '*Sample* Drop Down', drop_style)
        #drop_down_items = drop_down_input.listItems
        #drop_down_items.add('List_Item_1', True, '')
        #drop_down_items.add('List_Item_2', False, '')

