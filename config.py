import os.path

app_name = 'Auto GitHub Exporter'
company_name = "smengerl"



# Flag that indicates to run in Debug mode or not. When running in Debug mode
# more information is written to the Text Command window. Generally, it's useful
# to set this to True while developing an add-in and set it to False when you
# are ready to distribute it.
DEBUG = True



# ***Ignore Below this line unless you are sure***
lib_dir = 'lib'
app_path = os.path.dirname(os.path.abspath(__file__))
lib_path = os.path.join(app_path, lib_dir, '')