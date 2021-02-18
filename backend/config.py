import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
# basedir = os.path.abspath(os.path.dirname(__file__))

template_dir = os.path.abspath('../frontend/templates')