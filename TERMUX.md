# Termux paper-trading setup
pkg update -y
pkg install -y python
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env
python main.py
