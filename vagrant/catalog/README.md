# Item Catalog Project

## Project Overview
This project is about a catalog of items. All items in this project belong on or other category. User can view various items under different categories. User has feature to login / signup into the application. Once signed in, user can add new items or edit / delete previously created own items. User can also login using Google Account.

## Project Components

This project has various components.
	
	Folders and Files:
 1. static - it contains the css stylesheet file.
 2. templates - it contains all HTML code files for various screens.
 3. database_setup.py - this file contains structure of database and all tables to be added in database.
 4. dummy_data.py - this files contains some code to add dummy data in database before starting to work on project.
 5. application.py- this file contains all code and routes to navigate through project and perform all actions.

## How to run Google Sign in?
In order to make Google sign in work, you need to:

 - Create credentials for your app by going to Google Console.
 - Then after successful creation, you will get a `.json` file to download. 
 - After downloading it, change the name of the file to `client_secret_json.json`. 
 - Copy this file to parent directory `catalog` of project


## How to run Project?
In order to successfully run the project, you need to take following steps:

 - Run `database_setup.py` file to create a database with tables
 - Run `dummy_data.py` file to add dummy data to database
 - Run `application.py` file to start project and navigate through various screens.

The project runs on port `5000`

