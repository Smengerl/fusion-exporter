import os.path

app_name = 'Auto GitHub Exporter'
company_name = "smengerl on github"



# Flag that indicates to run in Debug mode or not. When running in Debug mode
# more information is written to the Text Command window. Generally, it's useful
# to set this to True while developing an add-in and set it to False when you
# are ready to distribute it.
DEBUG = True

GROUP_PREFERENCES = 'AutoExporterPreferences'

EXPORT_STL_KEY = 'export_stl'
STL_SUB_PATH_KEY = 'stl_sub_path'
EXPORT_PNG_KEY = 'export_png'
PNG_SUB_PATH_KEY = 'png_sub_path'
EXPORT_ZSB_KEY = 'export_zsb'
ZSB_SUB_PATH_KEY = 'zsb_sub_path'
IMAGE_WIDTH_KEY = 'image_width'
IMAGE_HEIGHT_KEY = 'image_height'
INCLUDE_REFERENCED_COMPONENTS_KEY = 'include_referenced_components'
INCLUDE_FLAGGED_COMPONENTS_KEY = 'include_flagged_components'


EXPORT_STL_DEFAULT_VALUE = True
STL_SUB_PATH_DEFAULT_VALUE = '/stl'
EXPORT_ZSB_DEFAULT_VALUE = True
ZSB_SUB_PATH_DEFAULT_VALUE = '/zsb'
EXPORT_PNG_DEFAULT_VALUE = True
PNG_SUB_PATH_DEFAULT_VALUE = '/png'
IMAGE_WIDTH_DEFAULT_VALUE = 800
IMAGE_HEIGHT_DEFAULT_VALUE = 600
INCLUDE_REFERENCED_COMPONENTS_DEFAULT_VALUE = False
INCLUDE_FLAGGED_COMPONENTS_DEFAULT_VALUE = False



# ***Ignore Below this line unless you are sure***
lib_dir = 'lib'
app_path = os.path.dirname(os.path.abspath(__file__))
lib_path = os.path.join(app_path, lib_dir, '')