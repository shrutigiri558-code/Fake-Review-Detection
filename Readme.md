This project has 2 parts:-
React - Frontend
Flask - Backend

Step 1: git clone https://github.com/sneha123sg/Fake-Review-Detection.git  
then open project in vscode  
Open Terminal 1 (Backend)  
cd backend  
Create a virtual environment - python -m venv venv  
Activate it- 
- Windows - venv\Scripts\activate  
- Mac/Linux - source venv/bin/activate  
Install required packages   - 
- pip install flask flask-cors pandas scikit-learn numpy  

Step 2: Check Model Files  
Your app.py expects these files inside the backend folder:  
- lr_model.pkl  
- nb_model.pkl  
- rf_model.pkl  
- vectorizer.pkl  
If they already exist:  
- python app.py  
If they do not exist, first train the models:  
- python train_model.py  
Note: train_model.py requires a dataset file named:  
- fake_reviews.csv  
with columns:  
> review,label  
> "This product is amazing",0  
> "Best purchase ever",0  
> "Excellent quality",0  
> "Fake review example",1  

After training completes:  
- python app.py  
You should see something like:  
* Running on http://127.0.0.1:5000  

Step 3: Open Terminal 2 (Frontend)  
Go back to the project root:  
- cd ..  
Install Node modules:  
- cd frontend  
- npm install  
Run React app:  
- npm run dev  

Step 4: Open Browser  
React application: http://localhost:3000  
Flask API:  http://localhost:5000  
If you get errors-  
- Check Python version  
- python --version  
Recommended:  Python 3.10 – 3.12  
Check Node version - node -v  
Recommended: v18 or v20  
Check npm version - npm -v  

Quick Run Commands  
Terminal 1 - 
cd backend  
python -m venv venv  
venv\Scripts\activate  
pip install flask flask-cors pandas scikit-learn numpy  
python app.py  
Terminal 2 -  
npm install  
npm run dev


if everything is installed, just want to run   
after installing everything  - 
in terminal of vscode - 
- cd frontend
- npm run dev
in another terminal of vscode - 
- cd backend 
- python app.py