import adsk.core
import adsk.fusion
from pathlib import Path
from typing import Callable, Optional, List

from ..apper import apper


def check_folder_validity(path: Path) -> Optional[str]:
    """Ensure path exists (or can be created) and is writable.

    Returns None on success, otherwise an error message string.
    """
    try:
        path.resolve(strict=False)
    except Exception as e:
        return f"Invalid path: {e}"

    if path.exists():
        if path.is_file():
            return "A file with this name already exists."
        if not path.is_dir():
            return "Path exists but is not a directory."
    else:
        try:
            path.mkdir(parents=True)
        except Exception as e:
            return f"Could not create directory: {e}"

    try:
        testfile = path / ".deleteme.tmp"
        with open(testfile, "w") as f:
            f.write("test")
        testfile.unlink()
    except Exception as e:
        return f"Directory is not writable: {e}"

    return None


def set_occurrence_recursive(occurrence: adsk.fusion.Occurrence, predicate: Callable[[adsk.fusion.Occurrence], bool]):
    """Set visibility for an occurrence and all children based on predicate."""
    occurrence.component.isJointsFolderLightBulbOn = False
    occurrence.component.isOriginFolderLightBulbOn = False
    occurrence.component.isSketchFolderLightBulbOn = False
    occurrence.component.isBodiesFolderLightBulbOn = True
    occurrence.component.isConstructionFolderLightBulbOn = True

    occurrence.isLightBulbOn = bool(predicate(occurrence))

    children = occurrence.childOccurrences
    for i in range(children.count):
        child = children.item(i)
        set_occurrence_recursive(child, predicate)

def is_parent_of(potential_parent: adsk.fusion.Occurrence, occurrence: adsk.fusion.Occurrence) -> bool:
    if (occurrence == potential_parent):
        return True
    else:
        children = potential_parent.childOccurrences
        for i in range(children.count):
            child = children.item(i)
            if is_parent_of(child, occurrence):
                return True
    return False



def sanitize_filename(name: str, replacement: str = '_') -> str:
    """Return a filesystem-safe filename by replacing unsafe characters.

    This is a conservative sanitizer: it replaces characters that are invalid
    in common filesystems and strips control characters. It also trims
    whitespace from ends. Keeps file extensions if present (caller should
    include extension separately).
    """
    # Keep only a whitelist of safe characters plus dot and dash
    import re
    name = name.strip()
    # Replace path separators and control characters
    name = re.sub(r'[\\/\x00-\x1f]', replacement, name)
    # Replace other unsafe chars
    name = re.sub(r'[:\*\?"<>\|]', replacement, name)
    # Collapse multiple replacements
    name = re.sub(re.escape(replacement) + r'+', replacement, name)
    # Trim leading/trailing dots or spaces
    name = name.strip(' .')
    if len(name) == 0:
        return 'unnamed'
    return name


def export_stl_to_file(file_name: str, occ: adsk.fusion.Occurrence):
    """Export the given occurrence to an STL file.
    """
    ao = apper.AppObjects()
    app: adsk.core.Application = ao.app
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    export_mgr = design.exportManager

    root = design.rootComponent
    occs = root.occurrences
    for i in range(occs.count):
        other = occs.item(i)
        set_occurrence_recursive(other, lambda o: is_parent_of(o, occ)) # Make the current occurence and all its parents visible

    opts = export_mgr.createSTLExportOptions(occ, file_name)
    export_mgr.execute(opts)


def export_root_component_image(file_name: str, width: int, height: int):
    """Export a viewport snapshot of the root to an PNG file.
    """
    ao = apper.AppObjects()
    viewport = ao.app.activeViewport

    root = ao.root_comp
    root.isJointsFolderLightBulbOn = False
    root.isOriginFolderLightBulbOn = False
    root.isSketchFolderLightBulbOn = False
    root.isBodiesFolderLightBulbOn = True
    root.isConstructionFolderLightBulbOn = True
    
    occs = root.occurrences
    for i in range(occs.count):
        other = occs.item(i)
        set_occurrence_recursive(other, lambda o: True) # Make all elements visible

    viewport.fit()
    viewport.saveAsImageFile(file_name, width, height)


def export_png_to_file(file_name: str, occ: adsk.fusion.Occurrence, width: int, height: int):
    """Export a viewport snapshot of the given occurrence to an PNG file.
    """
    ao = apper.AppObjects()
    viewport = ao.app.activeViewport

    root = ao.root_comp
    occs = root.occurrences
    for i in range(occs.count):
        other = occs.item(i)
        set_occurrence_recursive(other, lambda o: is_parent_of(o, occ)) # Make the current occurence and all its parents visible

    set_occurrence_recursive(occ, lambda o: True) # Ensure all children of occurence are also visible

    viewport.fit()
    viewport.saveAsImageFile(file_name, width, height)

#    export_options = adsk.fusion.ImageExportOptions.create(file_name)
#    export_options.width = width
#    export_options.height = height
#    export_options.isBackgroundTransparent = transparency
#    export_options.imageType = adsk.core.ImageFileTypes.PNGImageFileType
#    view.saveAsImageFileWithOptions(export_options)


def is_zsb(occ: adsk.fusion.Occurrence) -> bool:
    return occ.childOccurrences.count > 0

def export_components(components: List[adsk.fusion.Occurrence], 
                      include_referenced_components: bool,
                      include_flagged_components: bool,
                      export_stl: bool, stl_path: Path,
                      export_zsb: bool, zsb_path: Path, full_zsb_export: bool,
                      export_png: bool, png_path: Path, 
                      width: int, height: int):
    ao = apper.AppObjects()

    dlg = ao.ui.createProgressDialog()
    dlg.cancelButtonText = 'Cancel'
    dlg.isBackgroundTranslucent = False
    dlg.isCancelButtonShown = True
    dlg.show('Exporting', '%p%% (%v of %m components exported)', 0, len(components), 1)
    
    exported_components = set()


    ao.ui.activeSelections.clear() # Make sure no components are selected
    ao.design.activateRootComponent() # Ensure root component is active = no component is selected and hence blue
    
    

    skippedItems = 0
    zsb_exported = 0
    stl_exported = 0
    png_exported = 0

    if full_zsb_export:
        full_zsb = str((zsb_path / f"full.png").resolve())
        export_root_component_image(full_zsb, width, height)
        zsb_exported += 1

    for occ in components:
        dlg.progressValue += 1
        if occ.isReferencedComponent and not include_referenced_components:
            skippedItems += 1
            continue
        if occ.name.startswith('_') and not include_flagged_components:
            skippedItems += 1
            continue

        if occ.component.id in exported_components:
            skippedItems += 1
            continue
        else:
            exported_components.add(occ.component.id)

        if dlg.wasCancelled:
            break

        safe = sanitize_filename(occ.component.name)
        if is_zsb(occ):
            if export_zsb:
                out_zsb = str((zsb_path / f"{safe}.png").resolve())
                export_png_to_file(out_zsb, occ, width, height)
                zsb_exported += 1
        else:
            if export_stl:
                out_stl = str((stl_path / f"{safe}.stl").resolve())
                export_stl_to_file(out_stl, occ)
                stl_exported += 1
            if export_png:
                out_png = str((png_path / f"{safe}.png").resolve())
                export_png_to_file(out_png, occ, width, height)
                png_exported += 1


    dlg.hide()
    ao.ui.messageBox(f"Export finished.\n{len(components)} items processed of which {skippedItems} were skipped.\n\n{stl_exported} STL exported.\n{zsb_exported} ZSB exported.\n{png_exported} PNG exported.")  # type: ignore
