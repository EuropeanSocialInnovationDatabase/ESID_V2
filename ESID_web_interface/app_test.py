#This file has been created to run the app file on a different port, because the server is running the other file
#constantly now.
import time
import datetime
import hashlib
from flask import Flask, jsonify, request, render_template
from database_access import *
from extensions import mysql
import os



app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = username
app.config['MYSQL_DATABASE_PASSWORD'] = password
app.config['MYSQL_DATABASE_DB'] = database
app.config['MYSQL_DATABASE_HOST'] = host
mysql.init_app(app)
from webpages import webpage
app.register_blueprint(webpage)


#this function performs the registration of users
@app.route("/register", methods=['POST'])
def register():
    conn = mysql.connect()
    cursor = conn.cursor()
    user = request.json['user']
    password = request.json['pass']
    first_name = request.json['first_n']
    last_name = request.json['last_n']
    organization = request.json['organization']
    city = request.json['city']
    country = request.json['country']

    # Check whether user already exists
    #this sql select query selects all from the Users table and where the user is the same as
    #the user in question
    cursor.execute("SELECT * FROM Users WHERE username='{0}'".format(user))
    #declare a variable - has_user, which takes the result fetched by the cursor
    has_user = cursor.fetchone()
    #if the user does exist, then return that the user already exists
    if has_user is not None and has_user[0] == user:
        print("User already exists")
        return "User already exists"
    # make hashes
    #assign this to salt - I need to find out what this salt entails
    salt = "hdhswrnbjJhs32)"
    #this creates the password. What is used here is hashlib. sha256 is a function of that
    #I need to read more on this if needed
    pass_for_storing = hashlib.sha256(
        (password + salt).encode("utf-8")).hexdigest()
    #insert the details of the new user into the Users table in the database. These details
    #are those entered from the webform online, shown above
    cursor.execute("INSERT INTO Users (username,Password,FirstName,LastName,City,Country,Institution)"
                   "VALUES (%s,%s,%s,%s,%s,%s,%s)",
                   (user, pass_for_storing, first_name,last_name,city,country,organization))
    #commit and close the connection; print out success message
    conn.commit()
    cursor.close()
    conn.close()
    print("Successfully created user")
    return "Successfully created user"

#this funtion gets/generates the token
@app.route('/get_token', methods=['POST'])
def get_token():
    #connect mysl
    conn = mysql.connect()
    cursor = conn.cursor()
    #take in the user, password, salt and the hashed_pass generated above
    user = request.json['user']
    password = request.json['pass']
    salt = "hdhswrnbjJhs32)"
    hashed_pass = hashlib.sha256(
        (password + salt).encode("utf-8")).hexdigest()
    #select all from the Users table, where the password matches the password passed in, and IsApproved is
    #equal to 1
    select_query = "SELECT * FROM Users WHERE username='{0}' and Password='{1}' and IsApproved=1".format(user,hashed_pass)
    #execute the query
    cursor.execute(select_query)
    #assign the fetched entry to a variable - has_user
    has_user = cursor.fetchone()
    #if the has_user is not empty, meaning the user does exist
    if has_user is not None:
        #declare a variable - millis which is calculated as below
        millis = int(round(time.time() * 1000))
        #assign a string to a variable token_salt
        token_salt = "dsagggse"
        #set the variable - expiry_time to be equal to time, converted to a string, displayed in the format specified
        expiry_time = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.gmtime(time.time() + 86400))
        #generate a token with these elements below and assign it to variable - token
        token = hashlib.sha256(
            (user + str(millis) + token_salt).encode("utf-8")).hexdigest()
        #execute the cursor below and insert User as User_username, token as Token, expiry_time as ExpiryTime,
        #and LastUsed set to NOW()
        cursor.execute("INSERT INTO UserToken (User_username,Token,ExpiryTime,LastUsed) VALUES (%s, %s, %s, NOW() );",
                       (user, token, expiry_time))
        #commit and close the connection and print out the token
        conn.commit()
        cursor.close()
        conn.close()
        print(token)
        return token
    #if the user was not found, then print out the error - User does not exist
    else:
        cursor.close()
        print("ERROR: User does not exist")
        return "ERROR: User does not exist"


#this function validates the user
#the function takes in parameters - user, token
def validate_user(user, token):
    #establish database connection
    conn = mysql.connect()
    cursor = conn.cursor()
    #execute the select statement below, which selects all from the UserToken table where the User_Username
    #matches the user parameter entered, and the Token matches the token entered into the function
    cursor.execute(
        "SELECT * FROM UserToken WHERE User_Username=%s and Token=%s", (user, token))
    #assign the fetched data to the variable - has_user
    has_user = cursor.fetchone()
    #execute the sql query and close the connection
    cursor.close()
    conn.close()
    #if has_user is None, that means the user is not in the fetched data, then return False
    if has_user is None:
        return False
    #return the Expriry time converted to timestamp > the time
    #still have to clarify this. This could mean that the token Expiry time has not yet been reached
    return has_user[2].timestamp() > time.time()


@app.route('/is_logged', methods=['POST'])
#this fuction checks if the user is logged in. If the validate_user function returns true
#meaning that the last return there gives true- expiry_time is greater than the time of access
#this function returns Yes if the validate_user fucntion returns True, and No, if it returns false
def is_logged():
    user = request.json['user']
    token = request.json['token']
    if validate_user(user, token):
        return "Yes"
    else:
        return "No"


#this fucntion checks to see if the user is an admin or not
@app.route('/is_admin', methods=['POST'])
def is_admin():
    #connect to the database
    conn = mysql.connect()
    cursor = conn.cursor()
    # Validate that user is admin
    #receive user and token from the request form
    user = request.json['user']
    token = request.json['token']
    #execute the sql select query to  select the IsAdmin column from the table - Users
    #where the username is the same as that user put into the form
    cursor.execute("SELECT IsAdmin FROM Users WHERE username=%s", (user,))
    #assign all the retrieved data to the variable - user_is_admin
    user_is_admin = cursor.fetchone()

    #if user_is_admin, converted to boolean is true, and the validate_user function also evaluates to true, then close
    # the connection and return "Yes" user_is_admin would return 0 or 1, hence the conversion to bool
    if bool(user_is_admin[0]) and validate_user(user, token):
        cursor.close()
        conn.close()
        return "Yes"
    #else, return No
    else:
        cursor.close()
        conn.close()
        return "No"


@app.route('/logout', methods=['POST'])
#logout function
def logout():
    #connect to the database
    conn = mysql.connect()
    cursor = conn.cursor()
    #take the user and token entered from the webpage
    user = request.json['user']
    token = request.json['token']
    #if not validate user, meaning the user is not validated, then return that User is not logged in
    if not validate_user(user, token):
        return "User not logged in"
    #this executes the Delete sql query, deleting the user from the UserToken table, where the user matches this user
    cursor.execute("DELETE from UserToken WHERE User_Username=%s", (user,))
    #commit and close and also log out
    conn.commit()
    cursor.close()
    conn.close()
    return "Logged out"


@app.route('/classify_text', methods=['POST'])
# this function is a classify function
def classify():
    #this function accepts the user, text and token from the request form on the webpage
    user = request.json['user']
    token = request.json['token']
    text = request.json['text']
    #if the validate_user is false, then return that the User is not logged in; and return an empty string
    if not validate_user(user, token):
        return "User not logged in"
    return ""

@app.route('/submit_project', methods=['POST'])
#this function submits new project
def submit_new_project():
    #connection to the database is established
    conn = mysql.connect()
    cursor = conn.cursor()
    #receive the values for the variables below from the web request form
    Project_name = request.form['project_name']
    user = request.form['user']
    knowmak_ready = request.form.getlist('knowmak_checkbox')
    topics_to_add = request.form.getlist('topic_added_checkbox')
    Project_website = request.form['project_website']
    Project_facebook = request.form['project_facebook']
    Project_twitter = request.form['project_twitter']
    Address= request.form['project_address']
    City = request.form['project_city']
    Country = request.form['project_country']
    Objectives = request.form['objectives_satisfy']
    Actors = request.form['actors_satisfy']
    Outputs = request.form['outputs_satisfy']
    Innovativeness= request.form['innovativeness_satisfy']
    ProjectType = request.form['project_type']
    StartDate = request.form['project_date_start']
    EndDate = request.form['project_date_end']
    Description = request.form['project_description']
    Comment = request.form['project_comment']
    #return an error if the Project_name, Country or Project_website is left blank; an empty string
    if Project_name =='' or Country=='' or Project_website=='':
        return render_template('error.htm')
    #create an empty list - actors_list
    actors_list = []
    #receive the value for actor_count from the request form, a counter
    actor_count = int(request.form['counter'])
    #if actor_count is greater than 0
    if actor_count>0:
        #then iterate though actor_count with range
        for i in range(0,actor_count):
            #create an empty dictionary
            Actor_e = {}
            #create an empty dictionary called Actor_e; fill in the following variables from the request form and assign them
            #as values to the dictionary elements below
            Actor_e['Name'] = request.form['actor_name_'+str(i)]
            Actor_e['Website'] = request.form['actor_website_' + str(i)]
            Actor_e['City'] = request.form['actor_city_' + str(i)]
            Actor_e['Country'] = request.form['actor_country_' + str(i)]
            #append the dictionary to the list actor_list, and hence this will be a dictionary in a list
            actors_list.append(Actor_e)
    #if the start date and end date are not listed, then assign them the value 'Null'
    if StartDate == '':
        StartDate = 'Null'
    if EndDate =='':
        EndDate = 'Null'
    # project_sql = "Insert into Projects (ProjectName,Type,DateStart,DateEnd,ProjectWebpage,FacebookPage,ProjectTwitter,Suggestions,DataSources_idDataSources) VALUES ('{0}','{1}',{2},{3},'{4}','{5}','{6}','{7}',{8})"\
    #     .format(Project_name,ProjectType,StartDate,EndDate,Project_website,Project_facebook,Project_twitter,1,'57')

    #implement the sql query below; project_sql, which inserts the following into the Projects table; Puts in 1 for Suggestions and '57' for DataSources_idDataSources
    #Looked up the 'Suggestions' column and it appears to have 1s and 0s. Suggestion = 1 appears to mean True for being a Suggestion
    project_sql = "Insert into Projects (ProjectName,Type,DateStart,DateEnd,ProjectWebpage,FacebookPage,ProjectTwitter,Suggestions,DataSources_idDataSources) VALUES ('%s','%s',%s,%s,'%s','%s','%s','%s',%s)" \
                  % (
                  Project_name, ProjectType, StartDate, EndDate, Project_website, Project_facebook, Project_twitter, 1,
                  '57')

    #execute the sql query
    cursor.execute(project_sql)
    #assign the lastrowid, which is an automatically generated number for that column, to the project_id variable
    project_id = cursor.lastrowid
    #assign an Insert sql query to a variable - location_sql, which Inserts the following into the Project Location table, and enters 'Main'
    #as Type
    location_sql = "Insert into ProjectLocation (Type,Address,City,Country,Projects_idProjects,Original_idProjects) Values ('{0}','{1}','{2}','{3}','{4}','{5}')".format('Main',Address,City,Country,project_id,project_id)
    #execute the sql query
    cursor.execute(location_sql)
    #assign an Insert query to a variable, si_marks, which inserts into the TypesofSocialInnovation table the following, from the webform
    #and sets the value of SourceModel to "ManualAnnotationCrowd"
    si_marks = "Insert into TypeOfSocialInnotation (CriterionOutputs,CriterionObjectives,CriterionActors,CriterionInnovativeness,Projects_idProjects,SourceModel) Values ({0},{1},{2},{3},{4},'{5}')".format(
        Outputs,Objectives,Actors,Innovativeness,project_id,"ManualAnnotationCrowd")
    #execute the sql query
    cursor.execute(si_marks)
    #assign an Insert query to the variable - desc, (which inserts the description), which inserts the following into the
    #AdditionalProjectData table - FieldName-"Description_sum", Value -Description (entered through the portal) and
    #Projects_idProjects - project_id, DateObtained -NOW() and the SourceURL - "Manual"
    desc = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL) VALUES ('{0}','{1}','{2}',NOW(),'{3}')".format(
        "Description_sum",Description,project_id,"Manual"
    )
    #execute the cursor
    cursor.execute(desc)
    #iterate through actors_list
    for act in actors_list:
        #for each element, implement the sql query below, which inserts into the Actors table the following, and sets SourceOriginallyObtained to 'Manual Input'
        #and for DataSources_idDataSources - '57'
        act_sql = "Insert into Actors (ActorName,ActorWebsite,SourceOriginallyObtained,DataSources_idDataSources) Values ('{0}','{1}','{2}','{3}')".format(act['Name'],act['Website'],'ManualInput','57')
        #execute the sql query
        cursor.execute(act_sql)
        #set the value of actor_id to the lastrowid, an autogenerated number for that column
        actor_id = cursor.lastrowid
        #implement an insert sql query sql_user_log, which inserts into the following into the user_suggestions table. Assign
        #1 to add_suggestion and 0 to edit_suggestion. This means add suggestion is set to 1
        sql_user_log = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,entry_id,date_time,table_name) VALUES ('{0}','{1}','{2}','{3}',NOW(),'Actors')".format(
            user, 1, 0, actor_id)
        #execute the query
        cursor.execute(sql_user_log)
        #implement the sql insert query - act_location_sql below, which inserts the following into the ActorLocation table
        #it inserts the values from the actors_list
        act_location_sql = "Insert into ActorLocation (Type,City,Country,Actors_idActors) Values ('{0}','{1}','{2}','{3}')".format("Headquaters",act['City'],act['Country'],actor_id)
        #execute the query
        cursor.execute(act_location_sql)
    #Implement the sql insert query sql_user_log which inserts the following into the user_suggestions table.
    # The table_name is user; add suggestion is set to 1, and edit suggestion to 0. This shows that add_suggestion has
    #been set to true, or yes.
    sql_user_log = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id,entry_id,date_time,table_name,Comment) VALUES ('{0}','{1}','{2}','{3}','{4}',NOW(),'Projects','{5}')".format(
        user, 1, 0, project_id, project_id,Comment)
    #execute the query and commit the changes
    cursor.execute(sql_user_log)

    conn.commit()
    #Iterate through topics_to_add
    for topic in topics_to_add:
        #execute the sql insert query -sql- below. Insert into the user_suggestions table the variables below. Set add_suggestion to 1
        #meaning set it to true. Edit_suggestion is set to 0, table_name is assigned the string "Project_Topics", field_value should
        #be assigned 'TopicName' and also entry_id should be set to -1
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user, 1, 0, project_id,
                                                                                        'Project_Topics',
                                                                                        'TopicName', topic, -1,
                                                                                        Comment)
        #execute the query and commit the result
        cursor.execute(sql)
        conn.commit()
    #iterate through knowmak_ready;
    for kr in knowmak_ready:
        #if kr == 'knowmak_ready'
        if kr == 'knowmak_ready':
            #then execute the sql query - sql_p belopw, which updates the Projects table, setting the variable KNOWMAK_READY
            #to 1 for the project in question
            sql_p = "Update Projects set KNOWMAK_ready = 1 where idProjects={0}".format(project_id)
            cursor.execute(sql_p)
    #commit the changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()
    #show thank you template to signal end of submission of new project
    return render_template('thank_you_project.html')

@app.route('/submit_related_project', methods=['POST'])
#the submit related project function
def submit_related_project():
    conn = mysql.connect()
    cursor = conn.cursor()
    #request for and receive these values from the web portal and assign them to these variables
    Project_id_to_which_is_related = request.form['related_project']
    user = request.form['user']
    knowmak_ready = request.form.getlist('knowmak_checkbox')
    topics_to_add = request.form.getlist('topic_added_checkbox')
    Relationship = request.form['project_relationship']
    Project_name = request.form['project_name']
    Project_website = request.form['project_website']
    Project_facebook = request.form['project_facebook']
    Project_twitter = request.form['project_twitter']
    Address= request.form['project_address']
    City = request.form['project_city']
    Country = request.form['project_country']
    Objectives = request.form['objectives_satisfy']
    Actors = request.form['actors_satisfy']
    Outputs = request.form['outputs_satisfy']
    Innovativeness= request.form['innovativeness_satisfy']
    ProjectType = request.form['project_type']
    StartDate = request.form['project_date_start']
    EndDate = request.form['project_date_end']
    Description = request.form['project_description']
    Comment = request.form['project_description']
    #declare an empty list - actors_list
    actors_list = []
    #declare a variable actor_count and assign it the value from the counter, converted to an integer
    actor_count = int(request.form['counter'])
    #if the actor_count is higher than 0, meaning there is an actor
    if actor_count>0:
        #iterate through actor_count with range
        for i in range(0,actor_count):
            #declare an empty dictionary - Actor_e
            Actor_e = {}
            #fill the dictionary with the elements on the left and the values from the request form of the webportal
            Actor_e['Name'] = request.form['actor_name_'+str(i)]
            Actor_e['Website'] = request.form['actor_website_' + str(i)]
            Actor_e['City'] = request.form['actor_city_' + str(i)]
            Actor_e['Country'] = request.form['actor_country_' + str(i)]
            #append the dictionary Actor_e to the list - actors_list, so its a list containing a dictionary
            actors_list.append(Actor_e)
    #if the start and end date are empty, then assign them the string - 'Null'
    if StartDate == '':
        StartDate = 'Null'
    if EndDate =='':
        EndDate = 'Null'
    # project_sql = "Insert into Projects (ProjectName,Type,DateStart,DateEnd,ProjectWebpage,FacebookPage,ProjectTwitter,Suggestions,DataSources_idDataSources) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}',{8})"\
    #     .format(Project_name,ProjectType,StartDate,EndDate,Project_website,Project_facebook,Project_twitter,1,'57')

    #implement the sql query -project_sql, which inserts the following into the Projects table. It inserts 1 into Suggestions and '57' into
    #DataSources_idDataSources. It does appear that the DataSources_idDataSources = '57' represents the manually annotated files
    project_sql = "Insert into Projects (ProjectName,Type,DateStart,DateEnd,ProjectWebpage,FacebookPage,ProjectTwitter,Suggestions,DataSources_idDataSources) VALUES ('%s','%s',%s,%s,'%s','%s','%s','%s',%s)" \
        % (Project_name, ProjectType, StartDate, EndDate, Project_website, Project_facebook, Project_twitter, 1,
                '57')

    #execute the sql query
    cursor.execute(project_sql)
    #assign the lastrowid to the variable - project_id
    project_id = cursor.lastrowid
    #Implement the sql query - location_sql, which inserts into the ProjectLocation table the below. Projects_idProjects and Original_idProjects
    #are both project_id
    location_sql = "Insert into ProjectLocation (Type,Address,City,Country,Projects_idProjects,Original_idProjects) Values ('{0}','{1}','{2}','{3}','{4}','{5}')".format('Main',Address,City,Country,project_id,project_id)
    #execute the query
    cursor.execute(location_sql)
    #implement the sql query below, which inserts into the TypeOfSocialInnovation table, the following. SourceModel is set to "ManualAnnotationCrowd"
    si_marks = "Insert into TypeOfSocialInnotation (CriterionOutputs,CriterionObjectives,CriterionActors,CriterionInnovativeness,Projects_idProjects,SourceModel) Values ({0},{1},{2},{3},{4},'{5}')".format(
        Outputs,Objectives,Actors,Innovativeness,project_id,"ManualAnnotationCrowd"
    )
    #execute the query
    cursor.execute(si_marks)
    #implement the Insert query below, which inserts into the AdditionalProjectData table the follwoing details on Description
    #the FieldName is "Description_sum" and the SourceURL is assigned the string "Manual"
    desc = "Insert into AdditionalProjectData (FieldName,Value,Projects_idProjects,DateObtained,SourceURL) VALUES ('{0}','{1}','{2}',NOW(),'{3}')".format(
        "Description_sum",Description,project_id,"Manual"
    )
    #execute the query
    cursor.execute(desc)
    #iterate through the list - actors_list
    for act in actors_list:
        #implement the sql query below - act_sql, which inserts into the Actors table, the following. Assign the string 'Manaul'
        #to SourceOriginallyObtained and 1 to user_suggested
        act_sql = "Insert into Actors (ActorName,ActorWebsite,SourceOriginallyObtained,DataSources_idDataSources,user_suggested) Values ('{0}','{1}','{2}','{3}',1)".format(act['Name'],act['Website'],'ManualInput','57')
        cursor.execute(act_sql)
        #assign the lastrowid to the actor_id, which is an autogenerated column
        actor_id = cursor.lastrowid
        #implement the Insert query sql_user_log below, which inserts into the user_suggestions table the data below.add_suggestion
        #is again set to 1 and edit_suggestion to 0, and the Comment which was ofcourse entered from the web portal
        sql_user_log = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,entry_id,date_time,table_name,Comment) VALUES ('{0}','{1}','{2}','{3}',NOW(),'Actors','{4}')".format(
            user, 1, 0, actor_id,Comment)
        #execute the query
        cursor.execute(sql_user_log)

        #implement the act_location_sql query below, which inserts the values below into the ActorLocation table
        act_location_sql = "Insert into ActorLocation (Type,City,Country,Actors_idActors) Values ('{0}','{1}','{2}','{3}')".format("Headquaters",act['City'],act['Country'],actor_id)
        #execute the query
        cursor.execute(act_location_sql)
    #implement the sql insert query - sql_relation which inserts into Projects_relates_to_Projects table Projects_idProjects-
    # Project_id_to_which_is_related, Projects_idProjects1 - projects_id and the RelationshipType - Relationship entered from portal
    sql_relation = "Insert into Projects_relates_to_Projects (Projects_idProjects,Projects_idProjects1,RelationshipType) VALUES ({0},{1},'{2}')".format(Project_id_to_which_is_related,project_id,Relationship)
    #execute the sql query
    cursor.execute(sql_relation)
    #implement the sql query - sql_user_log which inserts the following into the user_suggestions table - add_suggestion - 1
    #project_id -project_id, entry_id - project_id and table_name - 'Projects'
    sql_user_log = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id,entry_id,date_time,table_name,Comment) VALUES ('{0}','{1}','{2}','{3}','{4}',NOW(),'Projects','{5}')".format(user,1,0,project_id,project_id,Comment)
    #execute the query and commit
    cursor.execute(sql_user_log)
    conn.commit()
    #iterate through topics_to_add
    for topic in topics_to_add:
        #implement the sql query -sql- to insert into the user_suggestions table the variables below. add_suggestion is
        #assigned 1,edit_suggestion - 0, table_name - 'Project_Topics, table_field - 'TopicName' and entry_id -> -1
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user, 1, 0, project_id,
                                                                                        'Project_Topics',
                                                                                        'TopicName', topic, -1,
                                                                                        Comment)
        #execute the sql query and commit the result
        cursor.execute(sql)
        conn.commit()
    #iterate through knowmak_ready
    for kr in knowmak_ready:
        #where the iterable is == 'knowmak_ready', then implement the sql query below to update the Projects table by setting
        #KNOWMAK_ready to 1 where the project_id is the same as that in focus
        if kr == 'knowmak_ready':
            sql_p = "Update Projects set KNOWMAK_ready = 1 where idProjects={0}".format(project_id)
            #execute the sql query
            cursor.execute(sql_p)
    #commit and close the connection and render the thank you template
    conn.commit()
    cursor.close()
    conn.close()
    return render_template('thank_you_project.html')

#implement program
if __name__ == "__main__":
    # MySQL configurations
    #conn = mysql.connect()
    #cursor = conn.cursor()
    #app.run(debug=True,port=8080,host="0.0.0.0") #to run this, I set this line to comment and added the next line.
    #with the right ESID web host ip address, and it ran - RA 26/01/2021
    app.run(debug=True, port=8080, host="130.159.136.15")
