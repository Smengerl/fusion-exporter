import adsk.core
import traceback

import os

EXPORT_STL_PMG_COMMAND_ID = 'export_stl_png_cmd_id'
EXPORT_ALL_STL_PMG_COMMAND_ID = 'export_all_stl_png_cmd_id'

try:
    from . import config
    from .apper import apper

    # ************Samples**************
    # Basic Fusion 360 Command Base samples
    from .commands.ExportStlPngCommand import ExportStlPngCommand
    from .commands.ExportAllStlPngCommand import ExportAllPngStlCommand

    # Various Application event samples
    from .commands.ExportDocumentSavedEvents import ExportDocumentSavedEvent

    # Create our addin definition object
    my_addin = apper.FusionApp(config.app_name, config.company_name, config.DEBUG)
    my_addin.root_path = config.app_path

    # Register an icon in the toolbar and make this the defaulit from its dropdown
    my_addin.add_command(
        'Export to STL/PNG with options',
        ExportStlPngCommand,
        {
            # Description used in hover hint
            'cmd_description': 'Export all components in current file as separate STL and PNG files',
            
            'cmd_id': EXPORT_STL_PMG_COMMAND_ID,
            
            # List of workspace to add the command to. 
            # # in this case this is only the workspace to add this command to is "Konstruktion" = FusionSolidEnvironment
            # See Workspace.id Property
            'workspace': 'FusionSolidEnvironment', 
            
            
            'toolbar_panel_id': 'Commands',

            # Path to icon resources
            'cmd_resources': 'export_selected_icons',

            # Command visibility
            'command_visible': True,

            # Promoted means it shows directly on the toolbar
            'command_promoted': True, 
        }
    )

    # Add another entry to the same dropdown
    my_addin.add_command(
        'Export all components to STL/PNG',
        ExportAllPngStlCommand,
        {
            # Description used in hover hint
            'cmd_description': 'Export all components in current file as STL and PNGs',

            'cmd_id': EXPORT_ALL_STL_PMG_COMMAND_ID,

            # List of workspace to add the command to. 
            # # in this case this is only the workspace to add this command to is "Konstruktion" = FusionSolidEnvironment
            # See Workspace.id Property
            'workspace': 'FusionSolidEnvironment', 

            'toolbar_panel_id': 'Commands',

            # Path to icon resources
            'cmd_resources': 'export_all_icons',

            # Command visibility
            'command_visible': True,
                        
            # Promoted means it shows directly on the toolbar
            'command_promoted': False,
        }
    )

    app = adsk.core.Application.cast(adsk.core.Application.get())
    ui = app.userInterface

    my_addin.add_document_event("auto_exporter_save_event", app.documentSaved, ExportDocumentSavedEvent)

except:
    app = adsk.core.Application.get()
    ui = app.userInterface
    if ui:
        ui.messageBox('Initialization Failed: {}'.format(traceback.format_exc()))

# Set to True to display various useful messages when debugging your app
debug = False


def run(context):
#    my_addin.get_all_preferences(self)
    my_addin.run_app()


def stop(context):
    my_addin.stop_app()
#    my_addin.save_preferences(self, group_name: str, new_group_preferences: dict, merge: bool):
