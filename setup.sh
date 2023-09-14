set -e

ROOT=$(dirname "$0")
VENV=$ROOT/env
JMDICT_VERSION=JMdict_e
JMDICT_DOWNLOAD_FOLDER=$ROOT/JMdict

# Create the virtual environment
echo "Creating virtual environment..."
python3 -m venv $VENV
source $VENV/bin/activate

# Install all dependencies
echo "Installing dependencies..."
python3 -m pip install -r $ROOT/requirements.txt

# Download and unzip the JMdict
echo "Downloading the dictionary..."
wget -c -P $JMDICT_DOWNLOAD_FOLDER http://ftp.edrdg.org/pub/Nihongo/$JMDICT_VERSION.gz
gzip -fdk $JMDICT_DOWNLOAD_FOLDER/$JMDICT_VERSION.gz

# Make migrations and migrate
echo "Setting up the DB..."
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py load_dictionary $JMDICT_DOWNLOAD_FOLDER/$JMDICT_VERSION
