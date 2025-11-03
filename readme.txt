Project Description:

  Finance Tracker Webpage tracker that allows the user to be able to make sure they can keep up to date information of their spending habits through game elements and with visual reports.
Some of the functionalities include:

1) Visual Aid with the usage of Num.py/Tableau
2) An achievement tracker to celebrate small milestones
3) Ability to link to your bank account to have real-time spending tracking

Project Running Requirements:

  The software doesn't require much of a strong processor using a simple 2010 macbook air or dell inspiron 2010 would be enough.

Version Updates:

0.0.0 10/16/25 - Project Started

0.0.1 10/23/25 - First Sprint Completed
  - Implemented User registration and login pages.
  - Implemented User password change options.
  - Implemented the Main UI and ability to add in expense categories.

0.0.2 10/30/25 - Second Sprint Completed
  - Changed framework to Flask in order to complete the project requirements.
  - Changed database to SQLAlchemy due to previous database having problems logging in.
  - Implemented Profile Page
  - Implemented Main UI that would include user being able to see changes in the expense categories
  - Implemented Financial Goals Section

Installation Guide:

Make sure to have the following programs installed prior to launching the app:
  - Latest Version of Python
  - Latest Version of Pip

When installing the app, make sure to set up a virtual environment before starting which can be done by having to change to the directory of the app then having to type in the following command in command prompt or terminal:

python -m venv venv

The virtual environment should start and you should see it in the beginning portion of the terminal with the following words "venv".

If you already have the virtual environment installed then all you have to do is the following command:

source venv/bin/activate

Assuming you are in the base repository it should start up the virtual environment.

Then type in the following command:

pip install -r requirements.txt

Change into the niner_repo then type in the following command:

python3 setup_db.py (This is in order to make sure you have the right database information set up prior to launching the app)
python3 app.py

If there are errors found in python3 app.py this is due to some of the files missing as sometimes the requirements are outdated based on PC to PC in this case make sure to type the following command:

pip3 install flask              
pip3 install flask-cors
pip3 install werkzeug
pip3 install flask-sqlalchemy
pip3 install flask-login
pip3 install flask-wtf
pip3 install flask-bcrypt

If there are any resources mentioning that they need to be updated follow the instructions found in the terminal.
