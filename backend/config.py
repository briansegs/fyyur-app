import os
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

# Grabs the folder where the script runs.
# basedir = os.path.abspath(os.path.dirname(__file__))

