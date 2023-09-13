set -e

VENV_NAME=env
ROOT=$(dirname "$0")
JMDICT_VERSION=JMdict_e
JMDICT_DOWNLOAD_FOLDER=$ROOT/JMdict

python3 -m venv $VENV_NAME
source $VENV_NAME/bin/activate

# Install all dependencies
python3 -m pip install -r requirements.txt

# Download and unzip the JMdict
wget -c -P $JMDICT_DOWNLOAD_FOLDER http://ftp.edrdg.org/pub/Nihongo/$JMDICT_VERSION.gz
gzip -fdk $JMDICT_DOWNLOAD_FOLDER/$JMDICT_VERSION.gz

# Make migrations and migrate
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py load_dictionary $JMDICT_DOWNLOAD_FOLDER/$JMDICT_VERSION
