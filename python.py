 To show this app works fine, we need to create a RDS instance at first.
# Import Flask modules
# As we know, we are gonna import necessary libraries. We've also imported
from flask import Flask, request, render_template
from flaskext.mysql import MySQL
# Create an object named app
app = Flask(__name__)
# The hardest part of this project is to get endpoint of RDS instances. Since our RDS is created within cloudformation template, we need to get RDS endpoint and paste it here as environmental variable using Launch templates user data.
db_endpoint = open("/home/ec2-user/phonebook/dbserver.endpoint", 'r', encoding='UTF-8')
# Configure mysql database
# Once we are done with the database, we are going to create database.
# we need to configure our database. I've explained this part before. Lets have a look at these configuration.
app.config['MYSQL_DATABASE_HOST'] = db_endpoint.readline().strip()
app.config['MYSQL_DATABASE_USER'] = 'admin'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Oliver_1'
app.config['MYSQL_DATABASE_DB'] = 'phonebook'
app.config['MYSQL_DATABASE_PORT'] = 3306
db_endpoint.close()
mysql = MySQL() # We are using this function to initialize mysql
mysql.init_app(app)
connection = mysql.connect()
connection.autocommit(True)
cursor = connection.cursor()
# Write a function named `init_todo_db` create phonebook table within clarusway_phonebook db, if it doesn't exist
# Lets paste Because of the id is auto_incremental, I don't need to worry about to id column. mysql is going to give id on behalf of us.
def init_phonebook_db():
    phonebook_table = """
    CREATE TABLE IF NOT EXISTS phonebook.phonebook(
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    number VARCHAR(100) NOT NULL,
    PRIMARY KEY (id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    cursor.execute(phonebook_table) # This is the connection to our database.
# Write a function named `find_persons` which finds persons' record using the keyword from the phonebook table in the db,and returns result as list of dictionary
# `[{'id': 1, 'name':'XXXX', 'number': 'XXXXXX'}]`.
# This function is to find my results that has "keyword" into database
def find_persons(keyword):
    # You are very familiar with this query. This query will select all columns where the name like keyword. strip will remove all the white spaces, and lower will turn uppercase into lowercase.
    query = f"""
    SELECT * FROM phonebook WHERE name like '%{keyword.strip().lower()}%';
    """
    cursor.execute(query) # We've executed query first
    result = cursor.fetchall() # I've got the result and assign them result variable.
    persons =[{'id':row[0], 'name':row[1].strip().title(), 'number':row[2]} for row in result] # this is a list comprehension, if there is a result coming from database, They are located these results one by one into the list and assigned it to the person variable. title makes the first letter capital
    if len(persons) == 0: # if there is no result, thanks to this if condition, No result massages is assigned to the persons variable.
        persons = [{'name':'No Result', 'number':'No Result'}]
    return persons
# Write a function named `insert_person` which inserts person into the phonebook table in the db,
# and returns text info about result of the operation
# We've defined insert_person function. at this time, I'll put name and number as parameter.
def insert_person(name, number):
    # We've first checked if there is a same person in my database. Thats why, I need to use exact name here with strip and lower methods.
    query = f"""
    SELECT * FROM phonebook WHERE name like '{name.strip().lower()}';
    """
    cursor.execute(query)
    row = cursor.fetchone()
    if row is not None: # If the row is not none, it means, I have a row that has same name given by a user, We'll return user with a massage
        return f'Person with name {row[1].title()} already exits.'
    # If our database doesn't have any name given by user, we can add that name into it.
    insert = f"""
    INSERT INTO phonebook (name, number)
    VALUES ('{name.strip().lower()}', '{number}');
    """
    cursor.execute(insert)
    result = cursor.fetchall()
    return f'Person {name.strip().title()} added to Phonebook successfully' # person given by user added to phonebook
