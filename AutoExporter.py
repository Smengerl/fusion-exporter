import adsk.core
import traceback

import os

try:
    from . import config
    from .apper import apper

    # ************Samples**************
    # Basic Fusion 360 Command Base samples
    from .commands.ExportStlCommand import ExportStlCommand
    from .commands.ExportPngCommand import ExportPngCommand

    # Various Application event samples
    from .commands.ExportDocumentSavedEvents import ExportDocumentSavedEvent
    from .commands.ExportWorkspaceActivatedEventHandler import ExportWorkspaceActivatedEventHandler

    # Create our addin definition object
    my_addin = apper.FusionApp(config.app_name, config.company_name, False)
    my_addin.root_path = config.app_path

    # Register an icon in the toolbar and make this the defaulit from its dropdown
    my_addin.add_command(
        'Export to STL',
        ExportStlCommand,
        {
            # Description used in hover hint
            'cmd_description': 'Export all components in current file as separate STL',
            
            'cmd_id': 'sample_cmd_1',
            
            # List of workspace to add the command to. 
            # # in this case this is only the workspace to add this command to is "Konstruktion" = FusionSolidEnvironment
            # See Workspace.id Property
            'workspace': 'FusionSolidEnvironment', 
            
            
            'toolbar_panel_id': 'Commands',

            # Path to icon resources
            'cmd_resources': 'export_stl_icons',

            # Command visibility
            'command_visible': True,

            # Promoted means it shows directly on the toolbar
            'command_promoted': True, 
        }
    )

    # Add another entry to the same dropdown
    my_addin.add_command(
        'Export to PNG',
        ExportPngCommand,
        {
            # Description used in hover hint
            'cmd_description': 'Export all components in current file as images to separate PNG files',

            'cmd_id': 'sample_cmd_2',

            # List of workspace to add the command to. 
            # # in this case this is only the workspace to add this command to is "Konstruktion" = FusionSolidEnvironment
            # See Workspace.id Property
            'workspace': 'FusionSolidEnvironment', 

            'toolbar_panel_id': 'Commands',

            # Path to icon resources
            'cmd_resources': 'export_png_icons',

            # Command visibility
            'command_visible': True,
                        
            # Promoted means it shows directly on the toolbar
            'command_promoted': False,
        }
    )

    app = adsk.core.Application.cast(adsk.core.Application.get())
    ui = app.userInterface

    # Uncomment as necessary.  Running all at once can be overwhelming :)
    # my_addin.add_custom_event("Auto GitHub Exporter_message_system", SampleCustomEvent)
    # my_addin.add_document_event("Auto GitHub Exporter_open_event", app.documentActivated, SampleDocumentEvent1)
    my_addin.add_document_event("Auto GitHub Exporter_save_event", app.documentSaved, ExportDocumentSavedEvent)
    my_addin.add_workspace_event("Auto GitHub Exporter_workspace_event", ui.workspaceActivated, ExportWorkspaceActivatedEventHandler)
    # my_addin.add_web_request_event("Auto GitHub Exporter_web_request_event", app.openedFromURL, SampleWebRequestOpened)
    # my_addin.add_command_event("Auto GitHub Exporter_command_event", app.userInterface.commandStarting, SampleCommandEvent)
    # my_addin.add_command_event("Auto GitHub Exporter_active_selection_event", ui.activeSelectionChanged, SampleActiveSelectionEvent)

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
