source venv/bin/activate
source .env
pip install -r requirements.txt
uvicorn main:app --reload 