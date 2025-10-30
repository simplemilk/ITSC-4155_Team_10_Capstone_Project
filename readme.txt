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

0.0.1 10.23/25 - First Sprint Completed
  - Implemented User registration and login pages.
  - Implemented User password change options.
  - Implemented the Main UI and ability to add in expense categories.

0.0.2 10/30/25 - Second Sprint Completed
  - Scrapped the idea of using React.js to move to Flask for convenience.
  - Translated previous sprint to second sprint while adding in improvements.

Installation Guide:

  To start the project, start two terminals with both terminals starting a virtual environment and locate the terminal to be on the project folder.

  The virtual environment should be located outside of the repository and to start the virtual environment write the following command:

    python -m venv venv

  Next, install the flask framework:

    pip install Flask

  Once completed go into the niner_repo repository and start the following files based on the circumstances:

    python3 app.py - To start the flask environment

    python3 db.py - To start the database

  To open the pages, look at the terminal and copy paste the link that links you to the localhost that it works with.

  Turning off the App:

  To exit the environment, just press ctrl + c.

Turning on the App from where you left off:

  If you want to start where you left off, locate the venv file and place the terminal in a repository just outside the venv folder then type the following:

    source venv/bin/activate

  or for Windows Users

    venv\Scripts\activate

  The webpages should load as well as the database and backend afterwards!!! 

Common problems:

If there is an issue with some library not being installed type the following command:

pip3 install <module>