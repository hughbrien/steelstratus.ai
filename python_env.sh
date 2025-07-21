python3 -m venv .venv 
 
source .venv/bin/activate 

pip install -r requirements.txt

flask run

#To listen on any IP Address use the following
flask run --host=0.0.0.0 
