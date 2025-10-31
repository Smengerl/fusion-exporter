import adsk.core
import traceback

from ..apper import apper

from .ExportVisibleStlPngCommand import ExportVisibleStlPngCommand
from .ExportAllStlPngCommand import ExportAllStlPngCommand

class ExportDocumentSavedEvent(apper.Fusion360DocumentEvent):

    def document_event_received(self, event_args, document):
        ao = apper.AppObjects()

        # Prompt the user whether to export components after save
        prompt = f"Document '{document.name}' was saved. Export all components? (No=visible ones only)?"

        # Use Yes/No/Cancel style: we'll map Yes = Export visible, No = Export all, Cancel = Skip
        # Create a custom set of buttons by using messageBox with YesNoCancelButtonType
        res = ao.ui.messageBox(prompt,
                            'Export on save',
                            adsk.core.MessageBoxButtonTypes.YesNoCancelButtonType,
                            adsk.core.MessageBoxIconTypes.QuestionIconType)

        # DialogResults: DialogYes, DialogNo, DialogCancel
        if res == adsk.core.DialogResults.DialogCancel:
            # User chose Skip
            return
        try:
            
            raw_cmd_id = ExportAllStlPngCommand.CMD_ID if res == adsk.core.DialogResults.DialogNo else ExportVisibleStlPngCommand.CMD_ID

            # Get addin instance from shared app_context registry to avoid
            # importing AutoExporter (circular import). If not available fall
            # back to notifying the user.
            from .. import app_context
            addin: apper.FusionApp = app_context.get_app()
            if not addin:
                ao.ui.messageBox('Add-in instance not available to run export command.')
                return
            
            cmd_id = addin.command_id_from_name(raw_cmd_id)
            if cmd_id:
                # Get ui from AppObjects instance (ao) instead of module-level ui
                cmd_def: adsk.core.CommandDefinition = ao.ui.commandDefinitions.itemById(cmd_id)
                if cmd_def:
                    cmd_def.execute()
                else:
                    ao.ui.messageBox(f'Command definition not found: {cmd_id}')
            else:
                ao.ui.messageBox(f'Command ID id could not be resolved: {raw_cmd_id}, {addin.command_dict}')
        except Exception:
            ui.messageBox('Export on save failed: {}'.format(__import__('traceback').format_exc()))
