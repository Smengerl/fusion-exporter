import adsk.core
import traceback

import os

from . import app_context

try:
    from . import config
    from .apper import apper
    
    # ************Samples**************
    # Basic Fusion 360 Command Base samples
    from .commands.ExportVisibleStlPngCommand import ExportVisibleStlPngCommand
    from .commands.ExportAllStlPngCommand import ExportAllStlPngCommand

    # Various Application event samples
    from .commands.ExportDocumentSavedEvents import ExportDocumentSavedEvent

    # Create our addin definition object
    my_addin: apper.FusionApp = apper.FusionApp(config.app_name, config.company_name, config.DEBUG)
    my_addin.root_path = config.app_path



    my_addin.add_command(
        'Export to STL/PNG with options',
        ExportVisibleStlPngCommand,
        {
            'cmd_description': 'Export all visible components as STL and PNGs',
            'workspace': 'FusionSolidEnvironment', # Add to solid modeling environment
            # 'toolbar_panel_id': 'SolidScriptsAddinsPanel', #'Commands',
            # 'toolbar_tab_id': 'ToolsTab',
            # 'toolbar_tab_name': 'ToolsTab',
            'cmd_resources': 'visibility', # Path to icon resources
            # 'cmd_ctrl_id',
            # 'add_to_drop_down': False,
            # 'drop_down_cmd_id': 'Default_DC_CmdId',
            # 'drop_down_name': 'Drop Name',
            # 'command_in_nav_bar': True,
            'command_in_qat_bar': True,
            # 'command_promoted': True, # Promoted means it shows directly on the toolbar
            # 'command_visible': True,
            # 'command_enabled': True,
            # 'help_file': False,
            'cmd_id': ExportVisibleStlPngCommand.CMD_ID,
            'debug': config.DEBUG,
        }
    )

    my_addin.add_command(
        'Export all to STL/PNG',
        ExportAllStlPngCommand,
        {
            'cmd_description': 'Export all components in current file as STL and PNGs',
            'workspace': 'FusionSolidEnvironment', # Add to solid modeling environment
            'toolbar_tab_id': 'ToolsTab', # Add to default tools tab
            'toolbar_panel_id': 'SolidScriptsAddinsPanel', # Add to Add in section in tools tab
            'cmd_resources': 'cards', # Path to icon resources
            'command_promoted': True, # Promoted means it shows directly on the toolbar
            'cmd_id': ExportAllStlPngCommand.CMD_ID,
            'debug': config.DEBUG,
        }
    )
    my_addin.add_command(
        'Export STL/PNG',
        ExportVisibleStlPngCommand,
        {
            'cmd_description': 'Export all visible components as STL and PNGs',
            'workspace': 'FusionSolidEnvironment', # Add to solid modeling environment
            'toolbar_tab_id': 'ToolsTab', # Add to default tools tab
            'toolbar_panel_id': 'SolidScriptsAddinsPanel', # Add to Add in section in tools tab
            'cmd_resources': 'visibility', # Path to icon resources
            'command_promoted': True, # Promoted means it shows directly on the toolbar
            'cmd_id': ExportVisibleStlPngCommand.CMD_ID,
            'debug': config.DEBUG,
        }
    )


    app = adsk.core.Application.cast(adsk.core.Application.get())
    ui = app.userInterface

    my_addin.add_document_event("auto_exporter_save_event", app.documentSaved, ExportDocumentSavedEvent)
    app_context.set_app(my_addin)



except:
    app = adsk.core.Application.get()
    ui = app.userInterface
    if ui:
        ui.messageBox('Initialization Failed: {}'.format(traceback.format_exc()))


def run(context):
    try:
        my_addin = app_context.get_app()
        pref: dict = my_addin.get_group_preferences(config.GROUP_PREFERENCES)

        if not config.EXPORT_STL_KEY in pref:
            pref[config.EXPORT_STL_KEY] = config.EXPORT_STL_DEFAULT_VALUE
        if not config.STL_SUB_PATH_KEY in pref:
            pref[config.STL_SUB_PATH_KEY] = config.STL_SUB_PATH_DEFAULT_VALUE
        if not config.EXPORT_PNG_KEY in pref:
            pref[config.EXPORT_PNG_KEY] = config.EXPORT_PNG_DEFAULT_VALUE
        if not config.PNG_SUB_PATH_KEY in pref:
            pref[config.PNG_SUB_PATH_KEY] = config.PNG_SUB_PATH_DEFAULT_VALUE
        if not config.IMAGE_WIDTH_KEY in pref:
            pref[config.IMAGE_WIDTH_KEY] = config.IMAGE_WIDTH_DEFAULT_VALUE
        if not config.IMAGE_HEIGHT_KEY in pref:
            pref[config.IMAGE_HEIGHT_KEY] = config.IMAGE_HEIGHT_DEFAULT_VALUE
        if not config.INCLUDE_FLAGGED_COMPONENTS_KEY in pref:
            pref[config.INCLUDE_FLAGGED_COMPONENTS_KEY] = config.INCLUDE_FLAGGED_COMPONENTS_DEFAULT_VALUE
        if not config.INCLUDE_REFERENCED_COMPONENTS_KEY in pref:
            pref[config.INCLUDE_REFERENCED_COMPONENTS_KEY] = config.INCLUDE_REFERENCED_COMPONENTS_DEFAULT_VALUE

        app_context.set_preferences(pref)
    
        my_addin.run_app()
    except Exception:
        app = adsk.core.Application.get()
        ui = app.userInterface
        if ui:
            ui.messageBox('Error starting application: {}'.format(traceback.format_exc()))





def stop(context):
    try:
        my_addin = app_context.get_app()
        pref: dict = app_context.get_preferences()

        my_addin.stop_app()
        my_addin.save_preferences(config.GROUP_PREFERENCES, pref, False)
    except Exception:
        app = adsk.core.Application.get()
        ui = app.userInterface
        if ui:
            ui.messageBox('Error stopping add-in: {}'.format(traceback.format_exc()))
    app_context.set_app(None)
