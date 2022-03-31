import requests
from flask import Blueprint, render_template
from flask import request
import json

from werkzeug.utils import redirect
from extensions import mysql

#conn = mysql.connect()
#cursor = conn.cursor()
webpage = Blueprint('webpage', __name__)

@webpage.route('/', methods=['GET'])
def index():
    return render_template('login.html')

@webpage.route('/register', methods=['GET'])
def register():
    return render_template('register.html')

@webpage.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@webpage.route('/user_created', methods=['GET'])
def user_created():
    return render_template('user_created.html')
    #return render_template('register.html')

@webpage.route('/home', methods=['GET'])
def home():
    return render_template('home.html')

@webpage.route('/suggest_new_project', methods=['GET'])
def suggest_new_project():
    return render_template('suggest.html')

@webpage.route('/perform_search', methods=['POST'])
#function to perform search through web interface
def perform_search():
    #connect to mysql and iterate through
    conn = mysql.connect()
    cursor = conn.cursor()
    #assign the entry from the search form to the variable search_query
    search_query = request.form['search']
    #select all the projects from the Projects Table where the ProjectName is like the search_query, and Exclude is false
    q = "Select * from Projects where ProjectName like '%{0}%' and Exclude=0".format(search_query)
    #execute the query -q with the cursor
    cursor.execute(q)
    #create variable project_list and fetch all entries from the query and assign them to this
    project_list = cursor.fetchall()
    #create an empty list - projects
    projects = []
    #iterate through project_list which holds all the entries returned from the query
    for pro in project_list:
        #assign an empty string to the variable Country
        Country = ""
        #select all from the ProjectLocation table where Project_idProjects is the same as the project ID from the Projects table
        q2 = "Select * from ProjectLocation where Projects_idProjects={0}".format(pro[0])
        #execute q2
        cursor.execute(q2)
        #assign all the fetched results from the database to the variable locs
        locs = cursor.fetchall()
        #iterate through the variable locs
        for loc in locs:
            #for each entry in locs list, assign the entry with index 5 (which is country from the dbase) to the variable Country
            Country = loc[5]
        #select all projects from the AdditionalProjectData table where the fieldname is like Description summary and the version like v1 and the project ID mataches the Project ID of searched project
        q2 = "Select * from AdditionalProjectData where FieldName like '%Description_sum%' and SourceURL like '%v1%' and  Projects_idProjects={0}".format(pro[0])
        cursor.execute(q2)
        #assign everything fetched to variable descs
        descs = cursor.fetchall()
        #initialize Description string
        Description = ""
        #for all the returned data in descs, concatenate the empty description string with the description summary extracted
        #at the end, you will have one long string, which you assign to variable Description
        for desc in descs:
            Description = Description+desc[2]+" "
        #if there is no description, meaning there is no description summary, as we loaded like Description_summary
        if Description == "":
            #select the field Description now from the AdditionalProjectData table where the project ID matches the Project ID in question
            q2 = "Select * from AdditionalProjectData where FieldName like '%Desc%' and  Projects_idProjects={0}".format(
                pro[0])
            #execute the cursor
            cursor.execute(q2)
            #put those in the descs variable as well
            descs = cursor.fetchall()
            #for each entry then, assign the description to the description string, appending it with concatenation to the empty string
            #this will add to and form one long string
            for desc in descs:
                Description = Description + desc[2] + " "
        #slice the description string to go from 0 index to 150 index. This summarizes the string
        #concatenate with ...
        Description = Description[0:150]+"..."
        #append the following variables to the projects list created above. It was initialised as an empty list above
        #This is a dictionary, with entries/values from the project_list created from extracts from the projects database table
        projects.append({"id":pro[0],"Name":pro[2],"Country":Country,"Description":Description})
    #close the connection to the database
    cursor.close()
    conn.close()
    #return the projects as the result to the search query that was entered on the webpage
    return render_template('perform_search.html',query = search_query,projects = projects)

@webpage.route('/edit/<id>', methods=['GET','POST'])
#the edit project via the webpage function takes as an input parameter the project ID
def edit_project(id):
    #establish connection with the database
    conn = mysql.connect()
    cursor = conn.cursor()
    #assign that ID received into the function to the project_id variable
    project_id = id
    #select the row in the Projects table with that project_id from the database; where Exclude is false
    q = "Select * from Projects where idProjects={0} and Exclude=0".format(project_id)
    #execute the query
    cursor.execute(q)
    #assign that list selection from the database to the variable 'project_list'
    project_list = cursor.fetchall()
    #declare an empty dictionary - project_data
    project_data = {}
    #iterate through the project_list and for each project, create an entry in the project_data dictionary with the key-value pairs below
    #the values are those at the indicated index positions from the Projects information obtained from the database
    for project in project_list:
        project_data['id'] = id
        project_data['project_name'] = project[2]
        project_data['type'] = project[4]
        project_data['DateStart'] = project[8]
        project_data['DateEnd'] = project[9]
        project_data['Website'] = project[11]
        project_data['Facebook'] = project[13]
        project_data['Twitter'] = project[14]
        project_data['FirstDataSource'] = project[16]
        project_data['Knowmak_ready'] = project[24]
    #The key locations in the project_data dictionary is set to the value of an empty list
    project_data['Locations'] = []
    #All the projects from the ProjectLocation table that have the Projects_idProjects equal to the project_id are selected
    q1 = "Select * From ProjectLocation where Projects_idProjects={0}".format(project_id)
    #execute the query
    cursor.execute(q1)
    #These selections are added to the variable - locations
    locations = cursor.fetchall()
    #The locations variable list is then iterated through to build a location dictionary
    for loc in locations:
        #declare an empty dictionary - location and enter in the key and value pairs below
        #the values are those at the indicated index positions below, derived from the location data from the database
        location = {}
        location['id_location'] = loc[0]
        location['loc_type'] = loc[1]
        location['address'] = loc[3]
        location['city'] = loc[4]
        location['country'] = loc[5]
        location['longitude'] = loc[9]
        location['latitude'] = loc[10]
        #This append is used to allow for the location dictionary to be added as a sub dictionary (in a list) in the Project_data dictionary, with Key - Locations
        project_data['Locations'].append(location)
    #Here, we select all the entries from the Actors_has_Projects table, on left join of idActors = Actors_idActors, where Projects_idProjects
    #is the same as the project_id in question/consideration
    q2 = "SELECT * FROM EDSI.Actors_has_Projects left join Actors on idActors=Actors_idActors where Projects_idProjects={0}".format(
        project_id)
    #wexecute the query
    cursor.execute(q2)
    #declare a variable called actors, and assign all entries fetched to it
    actors = cursor.fetchall()
    #add a new key/entry to the project_data dictionary, called Actors, and assign it an empty list
    project_data['Actors'] = []
    #iterate through the actors variable, which is mainly a list holding all the data fetched from the database on Actors above
    for actor in actors:
        #create a new dictionary called 'act'
        act = {}
        #add two elements to the 'act' dictionary, with their values being from the index locations shown, of data from the
        #database actors table
        act['Name'] = actor[5]
        act['Website'] = actor[12]
        #append the dictionary 'act' to the list assigned to project_data['Actors']. 'Actors' is a key in the project_data
        #dictionary, and it's value is a list which contains a dictionary - act
        project_data['Actors'].append(act)
    #create an sql variable q3, to hold results from a select statement which selects from AdditionalProjectData table where Projects_idProjects
    #is the same as the project_id, and FieldName is Description_summary and also the SourceModel is Manual
    #it appears in this case that the manual annotation entries are being taken to edit the record, where it was different
    #I'll confirm the above line later ***
    q3 = "SELECT * FROM EDSI.AdditionalProjectData where Projects_idProjects={0} and FieldName like '%Description_sum%' and SourceURL like '%Manual%'".format(
        project_id)
    #execute the sql select query
    cursor.execute(q3)
    #declare a variable descriptions and and assign the fetched results from the database to it
    descriptions = cursor.fetchall()
    #create an element in the project_data dictionary called 'Descriptions' and assign it a value of an empty list
    project_data['Descriptions'] = []
    #iterate through the descriptions which were extracted from the database
    for description in descriptions:
        #append the data in index position 2 of the extracted data, which is the description (the "value" column in the dbase)
        #to the project_data['Descriptions'] list. This is ofcourse the value of the project_data['Descriptions'] dictionary key
        project_data['Descriptions'].append(description[2])
    #if the length of project_data['Descriptions'] is equal to zero, that is, if it is empty
    if len(project_data['Descriptions']) == 0:
        #check that project_data['Knowmak_ready'] entry is equal to 1, meaning that project is ready for Knowmak
        #note, knowmakready was fetched up in the code, still in the edit function
        if project_data['Knowmak_ready'] == 1:
            #create an sql variable and select all from the AdditionalProjectData table where the fieldname is like Description_sum and the
            #SourceURL is like '%v1%', where the Projects_idProjects matches the project_id in question
            q3 = "SELECT * FROM EDSI.AdditionalProjectData where Projects_idProjects={0} and FieldName like '%Description_sum%' and SourceURL like '%v1%'".format(
                project_id)
        #if knowmak_ready is not equal to 1, then
        else:
            #declare an sql variable q3 and assign it the return from the select query, which selects all from AdditionalProjectData
            #where the fieldname is like Description_sum and SourceURL is like '%v2%' and the projects_idProjects matches the project_id in question
            q3 = "SELECT * FROM EDSI.AdditionalProjectData where Projects_idProjects={0} and FieldName like '%Description_sum%' and SourceURL like '%v2%'".format(
                project_id)
        #execute the query
        cursor.execute(q3)
        #fetch all the returns and place them in the variable descriptions
        descriptions = cursor.fetchall()
        #iterate through descriptions
        for description in descriptions:
            #append the value at index 2, which we recall is the value column from the database table.Append it to the list
            #which is the value of the project_data['Descriptions'] key in the project_data dictionary
            project_data['Descriptions'].append(description[2])
    #if the length of the project_data['Descriptions'] is equal to zero, meaning it is not empty;
    if len(project_data['Descriptions']) == 0:
        #declare an sql variable q3 and assign an sql select statement to it, selects all from AdditionalProjectData table where
        #Projects_idProjects is same as the project_id of the project in focus and the FieldName is like '%Desc%'
        q3 = "SELECT * FROM EDSI.AdditionalProjectData where Projects_idProjects={0} and FieldName like '%Desc%'".format(
            project_id)
        #execute the query
        cursor.execute(q3)
        #fetchall the data returned from the query and assign these to the variable - descriptions
        descriptions = cursor.fetchall()
        #declare a variable 'Descriptions' in the project_data dictionary as previously done and assign it an empty list
        project_data['Descriptions'] = []
        #iterate throught the descriptions returned from the query just above
        for description in descriptions:
            #append the entries at index 2 of the returned results from the database, to the list which is a value of 'Descriptions'
            #in the project_data dictionary
            project_data['Descriptions'].append(description[2])

    #declare a new query variable, q4 and assign it the select statement below, which selects all entries from the TypeOfSocailInnovation
    #table in the database, where the SourceModel is like '%Manual%' and Projects_idProjects is the same as the project_id in question
    q4 = "SELECT * FROM EDSI.TypeOfSocialInnotation where SourceModel like '%Manual%' and Projects_idProjects={0}".format(
        project_id);
    #execute the query
    cursor.execute(q4)
    #fetch all the results from the query and assign them the variable, marks
    marks = cursor.fetchall()
    #if the length of marks is equal to 0, that is, it is empty,which would mean that there are no projects like that in the dbase,
    if len(marks)==0:
        #declare a query variable q4 and assign it a select query, which selects all the entries from TypeOfSocialInnovation table
        # where the SourceModel is like '%v14%' and the Projects_idProjects is the same as the project_id
        q4 = "SELECT * FROM EDSI.TypeOfSocialInnotation where SourceModel like '%v14%' and Projects_idProjects={0}".format(
            project_id);
        #execute the query
        cursor.execute(q4)
        #assign the returned results to the variable - marks
        marks = cursor.fetchall()
    #iterate through marks
    for mark in marks:
        #assign the values retrieved from the execution of the query to the project_data dictionary with the keys - 'Outputs',
        #'Objectives', 'Actors_s' and 'Innovativeness'. Note that the value at index 1 is from the CriterionOutputs column in the
        #TypesofSocialInnovation table and same goes for the rest
        project_data['Outputs'] = mark[1]
        project_data['Objectives'] = mark[2]
        project_data['Actors_s'] = mark[3]
        project_data['Innovativeness'] = mark[4]
    #declare a variable q5 to hold the select query which selects the TopicName,TopicScore and Keywords from the Project_Topics
    #table where the Projects_idProject is equal to the project_id in question, and the version is like '%v4%' or Version like '%Manual%'
    #order by TopicScore descending limit 10
    q5 = "Select TopicName,TopicScore,KeyWords from Project_Topics where Projects_idProject={0} and (Version like '%v4%' or Version like '%Manual%') order by TopicScore desc limit 10".format(
        project_id);
    #execute the query
    cursor.execute(q5)
    #assign the retrieved results to the variable - topics
    topics = cursor.fetchall()
    #create a new element in the project_data dictionary- 'Topics' and assign an empty list to it
    project_data['Topics'] = []
    #iterate through topics returned from the query above
    for topic in topics:
        #from the query, TopicName is at index 0, TopicScore at index 1 and KeyWords at index 2
        #if topic score is greater than 0.7
        if topic[1]>0.7:
            #append the topic name to the list project_data['Topics']
            project_data['Topics'].append(topic[0])
    #close the cursor and the connection
    cursor.close()
    conn.close()
    #return the project_data dictionary
    return render_template('project_edit.html', project=project_data)
#submitting the edit
@webpage.route('/submit_edit', methods=['POST'])
def edit_submit():
    #connect to the database
    conn = mysql.connect()
    cursor = conn.cursor()
    #receive the project_id from the request form and assign it to variable project_id
    project_id = request.form['project_id']
    #get the topics to exclude from the topic checkbox and assign the list to variable- topics_to_exclude
    topics_to_exclude = request.form.getlist('topic_checkbox')
    #get the knowmak_ready list from the knowmak_checkbox form and assign to variable - knowmak_ready
    knowmak_ready = request.form.getlist('knowmak_checkbox')
    #get the topics to add from the topic_added_checkbox and assign to variable - topics_to_add
    topics_to_add = request.form.getlist('topic_added_checkbox')
    #declare variable q and assign the select query below to it; which selects all projects that match the project_id from the
    #Projects table
    q = "Select * from Projects where idProjects={0} and Exclude=0".format(project_id)
    #execute the query q
    cursor.execute(q)
    #fetch the extracted results from the database query and add them to variable project_list
    project_list = cursor.fetchall()
    #declare a variable project_data and assign an empty dictionary to this
    project_data = {}
    #iterate though the project_list which contains the fetched results from the database
    for project in project_list:
        #assign the entires at the following index positions from the database to the project_data dictionary elements
        project_data['id'] = id
        project_data['project_name'] = project[2]
        project_data['type'] = project[4]
        project_data['DateStart'] = project[8]
        project_data['DateEnd'] = project[9]
        project_data['Website'] = project[11]
        project_data['Facebook'] = project[13]
        project_data['Twitter'] = project[14]
        project_data['FirstDataSource'] = project[16]
        project_data['Knowmak_ready'] = project[24]
    #create dictionary element - Locations and assign it an empty list
    project_data['Locations'] = []
    #create query element q1 and assign it the select query which selects all the entries from table - ProjectLocation where
    #Projects_idProjects is equal to the project_id in question
    q1 = "Select * From ProjectLocation where Projects_idProjects={0}".format(project_id)
    #execute that query
    cursor.execute(q1)
    #create variable location and put in all the fetched entries from the ProjectLocation table
    locations = cursor.fetchall()
    #iterate the locations
    for loc in locations:
        #create an empty dictionary - location
        location = {}
        #assign the fetched entries at these index positions from the database to the dictionary elements here
        location['id_location'] = loc[0]
        location['loc_type'] = loc[1]
        location['address'] = loc[3]
        location['city'] = loc[4]
        location['country'] = loc[5]
        location['longitude'] = loc[9]
        location['latitude'] = loc[10]
        #append the location dictionary as a value to the project_data['Locations'], making it a sub dictionary in the project_data
        #dictionary, which now contains a dictionary as the value of its element - 'Locations'
        project_data['Locations'].append(location)
    #declare an sql varaible and assign the select query which selects all the entries from the Actors_has_Projects table; on left join
    #with the Actors table on the ids, where the Projects_idProjects is the same as the project_id in question
    q2 = "SELECT * FROM EDSI.Actors_has_Projects left join Actors on idActors=Actors_idActors where Projects_idProjects={0}".format(
        project_id)
    #execute the query
    cursor.execute(q2)
    #declare a variable - actors and assign the returned results to it
    actors = cursor.fetchall()
    #create a new element in the project_data dictionary - 'Actors' and assign it an empty list as a value
    project_data['Actors'] = []
    #iterate through 'actors', the results fetched from the database
    for actor in actors:
        #create a new dictionary - 'act'
        act = {}
        #create these two elements to include in the dictionary - 'act' and assign them the values in these index positions
        #when the above join is performed, these are the indices. I confirmed these from the database
        act['Name'] = actor[5]
        act['Website'] = actor[12]
        #append the 'act' dictionary to the project_data['Actors'], hence making it a subdictionary of project_data. This makes
        #it a dictionary in a list
        project_data['Actors'].append(act)
    #decalre a varaible q3 and assign it all the select query, which selects all from AdditionalProjectData table where Projects_
    #idProjects is the same as the project_id in question, and FieldName is like '%Description_sum%' and the SourceURL is like '%Manual%'
    q3 = "SELECT * FROM EDSI.AdditionalProjectData where Projects_idProjects={0} and FieldName like '%Description_sum%' and SourceURL like '%Manual%'".format(
        project_id)
    #execute the query
    cursor.execute(q3)
    #assign a variable -descriptions to hold all the fetched returns from the query
    descriptions = cursor.fetchall()
    #create an element in the project_data dictionary named 'Descriptions' and assign it an empty list
    project_data['Descriptions'] = []
    #iterate through descriptions, which is the variable that holds the results from the select query q3 above
    for description in descriptions:
        #append the data in index 2 of the description fetched from the database to the project_data['Descriptions'] list, which
        #that data in index 2 is the value column from the databse, which contains the description text
        project_data['Descriptions'].append(description[2])
    #if the length of project_data['Descriptions'] is zero, meaning the list is empty, then
    if len(project_data['Descriptions']) == 0:
        #check if project_data['Knowmak_ready'] is equal to 1 and if it is;
        if project_data['Knowmak_ready'] == 1:
            #declare a new variable q3 and assign to it the select statement below, which selects all from AdditionalProjectData where
            #Projects_idProjects is the same as the project_id in question, and the FieldName like Description_sum and the SourceURL like v1 (this v1 turns out to be
            #SI SVM Summarizer v1 in database btw)
            q3 = "SELECT * FROM EDSI.AdditionalProjectData where Projects_idProjects={0} and FieldName like '%Description_sum%' and SourceURL like '%v1%'".format(
                project_id)
        else:
            #else, assign to q3 the select query  which selects same as above, but with SourceURL like v2 (this v2 turns out to be NB Summarizer v2)
            #else here being, if Knowmak_ready is not equal to 1
            q3 = "SELECT * FROM EDSI.AdditionalProjectData where Projects_idProjects={0} and FieldName like '%Description_sum%' and SourceURL like '%v2%'".format(
                project_id)
        #execute the query q3
        cursor.execute(q3)
        #assign all the fetched data from q3 to variable - descriptions
        descriptions = cursor.fetchall()
        #iterate through descriptions
        for description in descriptions:
            #append the data at index 2 to project_data['Descriptions']. This is the value column, which is the description text
            project_data['Descriptions'].append(description[2])
    #if the length of project_data['Descriptions'] is still equal to zero, meaning the list is empty still, then do the following;
    if len(project_data['Descriptions']) == 0:
        #declare a variable q3 and assign a select statement to it; to select all from AdditionalProjectData table, where the Projects_idProjects
        #is the same as the project_id in question, but the fieldname this time is like - Desc.
        q3 = "SELECT * FROM EDSI.AdditionalProjectData where Projects_idProjects={0} and FieldName like '%Desc%'".format(
            project_id)
        #execute q3
        cursor.execute(q3)
        #fetch all the returned data and assign them to the variable 'descriptions'
        descriptions = cursor.fetchall()
        #create an element in the project_data dictionary called 'Descriptions' and assign it a value of an empty list
        project_data['Descriptions'] = []
        #iterate through descriptions, returned from the database
        for description in descriptions:
            #append the data at index 2 to the list project_data['Descriptions'], which makes this a list as a value of one of the
            #elements of a dictionary
            project_data['Descriptions'].append(description[2])
    #create a new sql variable q4 to hold the select statement which selects all from the table 'TypeOfSocialInnovation' where the
    #SourceModel is like v14 and the Projects_idProjects is the same as that of the project_id in question
    q4 = "SELECT * FROM EDSI.TypeOfSocialInnotation where SourceModel like '%v14%' and Projects_idProjects={0}".format(
        project_id);
    #execute the query q4
    cursor.execute(q4)
    #declare a variable marks and assign it all the data returned from the implementation of q4
    marks = cursor.fetchall()
    #iterate through marks
    for mark in marks:
        #iterate through marks and assign the data at the index positions below to the project_data dictionary elements as done
        #below
        project_data['SI_Marks_id'] = mark[0]
        project_data['Outputs'] = mark[1]
        project_data['Objectives'] = mark[2]
        project_data['Actors_s'] = mark[3]
        project_data['Innovativeness'] = mark[4]
    #assign the values from the request forms as shown below, to the variables on the left hand side
    #it appears these are the responses to the requests that are entered through the forms on the webpage. The elements (in gree)
    #are the prompts that appear and their values, which are responses are assigned to these variables
    Project_name = request.form['project_name']
    user = request.form['user']
    Project_website_f = request.form['project_website']
    Project_facebook = request.form['project_facebook']
    Project_twitter = request.form['project_twitter']
    Address= request.form['project_address']
    City = request.form['project_city']
    Country_f = request.form['project_country']
    Objectives = request.form['objectives_satisfy']
    Actors = request.form['actors_satisfy']
    Outputs = request.form['outputs_satisfy']
    Innovativeness= request.form['innovativeness_satisfy']
    ProjectType = request.form['project_type']
    StartDate_f = request.form['project_date_start']
    EndDate_f = request.form['project_date_end']
    Description = request.form['project_description']
    Comment = request.form['project_comment']
    #check if the enteres description is longer than 7000 words and if so, print the error in the return below
    if len(Description)>7000:
        return render_template('error.html',error="Description length is too large (it should be up to 7000 characters")
    #check of the length of the comment is longer than 1000, and if so, print the error in the return below
    if len(Comment)>1000:
        return render_template('error.html',error="Comment length is too large (it should be up to 1000 characters")
    #create a list called actors_list
    actors_list = []
    #create a variable actor_count which takes the value from a variable - 'counter' on the request form. This number is entered
    #via the web interface
    actor_count = int(request.form['counter'])
    #if the actor_count is greater than 0,
    if actor_count>0:
        #iterate through this range, which goes through the actor_count
        for i in range(0,actor_count):
            #create a dictionary - Actor_e
            Actor_e = {}
            #input the following elements or keys in the dictionary and assign the values from the request form
            Actor_e['Name'] = request.form['actor_name_'+str(i)]
            Actor_e['Website'] = request.form['actor_website_' + str(i)]
            Actor_e['City'] = request.form['actor_city_' + str(i)]
            Actor_e['Country'] = request.form['actor_country_' + str(i)]
            #append this to dictionary to actors_list, which will now be a list that contains a dictionary
            actors_list.append(Actor_e)
    #if StartDate_f is an empty string
    if StartDate_f == '':
        #assign the string 'Null' to StartDate_f
        StartDate_f = 'Null'
    #if EndDate_f is an empty string
    if EndDate_f =='':
        #assign the string 'Null' to EndDate_f
        EndDate_f = 'Null' #there was an error here, where EndDate_f was written as EndDate only. Corrected by RA 13/1/21
    #if the Project_name entered in the interface is not equal to the porject_name in project_data
    if Project_name!=project_data['project_name']:
        #create an sql query which inserts into the user_suggestions table the following - username -user, add_suggestion-0, edit_suggestion-1,
        #project_id -project_id, 'date_time -NOW(),table_name - the string 'Projects',table_field - the string 'Project_name', field_value - Project_name,
        #entry_id - project_id and Comment - Comment
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user,0,1,project_id,'Projects','ProjectName',Project_name,project_id,Comment)
        #execute the sql query to input this into the table
        cursor.execute(sql)
        #commit
        conn.commit()
    #if the Project_website_f is equal to the string 'None', from the web request form
    #then assign the variable Project_website_f to None
    if Project_website_f=='None':
        Project_website_f = None
    #if the Project_website_f entered from the webform is not equal to the value in project_data['Website'], recall the project_data dictionary
    if Project_website_f!=project_data['Website']:
        #implement the sql insert query below, which inserts into user_suggestions the following - username -user,add_suggestion- 0
        #edit_suggestion-1,project_id-project_id,date_time -NOW(),table_name - the string 'Projects', table_field - the string 'ProjectWebsite',
        #field_value - Project_website_f (which is the website entered from the webpage prompt),entry_id-project_id and Comment -Comment
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user,0,1,project_id,'Projects','ProjectWebsite',Project_website_f,project_id,Comment)
        #execute the sql query
        cursor.execute(sql)
        #commit
        conn.commit()
    #if the Project_facebook variable is equal to the string 'None'
    #equate the Project_facebook to None
    if Project_facebook=='None':
        Project_facebook = None
    #if the Project_twitter variable is equal to the string 'None'
    #set the Project_twitter to None
    #what these mean is if the project has no Facebooj or Twitter page, then set to None
    if Project_twitter=='None':
        Project_twitter = None
    #if the Project_facebook entered from the web portal is not the same as the one in the project_data dictionary
    if Project_facebook!=project_data['Facebook']:
        #implement an sql Insert query as those above, except now set the table_field - the string'FacebookPage', field_value - Project_facebook (which is basically
        #what was put in through the web portal
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user,0,1,project_id,'Projects','FacebookPage',Project_facebook,project_id,Comment)
        #execute the sql query
        cursor.execute(sql)
        #commit
        conn.commit()
    #if the Project_twitter put in through the webportal is not the same as that in the project_data dictionary value for Twitter
    if Project_twitter!=project_data['Twitter']:
        # implement an sql Insert query as those above, except now set the table_field - the string'ProjectTwitter', field_value - Project_twitter (which is basically
        # what was put in through the web portal
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user,0,1,project_id,'Projects','ProjectTwitter',Project_twitter,project_id,Comment)
        #execute the sql query and commit it
        cursor.execute(sql)
        conn.commit()
    #if ProjectType put in through the web portal does not match the type in the project_data
    if ProjectType!=project_data['type']:
        #implement an sql query to insert into the user_suggestions table the details below, as was previously done, except for this, insert into the table_field
        #the string - 'Type' and the field_value - ProjectType (that entered from the portal)
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user,0,1,project_id,'Projects','Type',ProjectType,project_id,Comment)
        #execute the sql query and commit it
        cursor.execute(sql)
        conn.commit()
    #if StartDate_f is equal to 'None' or StartDate_f is equal to an empty string or StartDate_f is equal to the string 'Null'
    #this is the start date from the portal. Not sure why this was not checked above already
    if StartDate_f=='None' or StartDate_f=='' or StartDate_f=='Null':
        #then set the StartDate_f to be equal to None
        StartDate_f = None
    if EndDate_f=='None' or EndDate_f=='' or EndDate_f=='Null': #corrected the last or here to EndDate, as Start_Date was repeated. RA 13/01/21
        #then set the EndDate_f to be equal to None
        EndDate_f = None
    #if StartDate_f is not equal to the variable for the start date in the project_data dictionary; meaning there is a disparity with
    #what is on the database and what has been entered at the web portal
    if StartDate_f!=project_data['DateStart']:
        #implement an sql query to insert into the user_suggestions table the details below, as was previously done, except for this,
        # insert into the table_field the string - 'DateStart' and the field_value - StartDate_f (the value entered from the portal)
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user,0,1,project_id,'Projects','DateStart',StartDate_f,project_id,Comment)
        #execute the sql query and commit
        cursor.execute(sql)
        conn.commit()
    # if EndDate_f is not equal to the variable for the end date in the project_data dictionary; meaning there is a disparity
    # between what is on the database and what has been entered at the web portal
    if EndDate_f!=project_data['DateEnd']:
        # implement an sql query to insert into the user_suggestions table the details below, as was previously done, except for this,
        # insert into the table_field the string - 'DateEnd' and the field_value - EndDate_f (the value entered from the portal)
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user,0,1,project_id,'Projects','DateEnd',EndDate_f,project_id,Comment)
        #execute the sql query and commit
        cursor.execute(sql)
        conn.commit()

    #implement some exception handling
    try:
        #if Objectives entered from the web portal does not match that in the project_data dictionary
        if Objectives!=str(project_data['Objectives']):
            #declare sql insert query as those above, and set the table_name to string 'TypeOfSocialInnotation',table_field to string
            #'CriterionObjectives', and field_value - Objectives(the value entered from the web portal)
            sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
                  "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user,0,1,project_id,'TypeOfSocialInnotation','CriterionObjectives',Objectives,project_id,Comment)
            #execute and commit sql query
            cursor.execute(sql)
            conn.commit()
    #this except appears to be catching an exception that could occur maybe if there is a problem with the conversion to string
    #in the if statement above
    except:
        #this is the same sql query as the prvious one. It does the same thing
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user, 0, 1, project_id,
                                                                                        'TypeOfSocialInnotation',
                                                                                        'CriterionObjectives',
                                                                                        Objectives, project_id, Comment)
        #execute the query and commit
        cursor.execute(sql)
        conn.commit()
    try:
        # if Outputs entered from the web portal does not match that in the project_data dictionary
        if Outputs!=str(project_data['Outputs']):
            # declare sql insert query as those above, and set the table_name to string 'TypeOfSocialInnotation',table_field to string
            # 'CriterionOutputs', and field_value - Outputs(the value entered from the web portal)
            sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
                  "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user,0,1,project_id,'TypeOfSocialInnotation','CriterionOutputs',Outputs,project_id,Comment)
            # execute the query and commit
            cursor.execute(sql)
            conn.commit()
    # this except appears to be catching an exception that could occur maybe if there is a problem with the conversion to string
    # in the if statement above
    except:
        # this is the same sql query as the prvious one. It does the same thing
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user, 0, 1, project_id,
                                                                                        'TypeOfSocialInnotation',
                                                                                        'CriterionOutputs', Outputs,
                                                                                        project_id, Comment)
        #execute and commit
        cursor.execute(sql)
        conn.commit()
    try:
        #another esception is handled from here
        #if the Actors entered from the web portal is different from what is in the project_data
        if Actors!=str(project_data['Actors_s']):
            # declare sql insert query as those above, and set the table_name to string 'TypeOfSocialInnotation',table_field to string
            # 'CriterionActors', and field_value - Actors(the value entered from the web portal)
            sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
                  "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user,0,1,project_id,'TypeOfSocialInnotation','CriterionActors',Actors,project_id,Comment)
            #execute the query and commit
            cursor.execute(sql)
            conn.commit()
    except:
        #this exception probably handles a potential problem with the string conversion above
        #the sql query is the same as just above, in this except clause
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user, 0, 1, project_id,
                                                                                        'TypeOfSocialInnotation',
                                                                                        'CriterionActors', Actors,
                                                                                        project_id, Comment)
        #execute the query and commit
        cursor.execute(sql)
        conn.commit()
    try:
        #exception handling above as well
        #if Innovativeness is not equal to the value of Innovativeness in the project_data dictionary
        if Innovativeness!=str(project_data['Innovativeness']):
            # declare sql insert query as those above, and set the table_name to string 'TypeOfSocialInnotation',table_field to string
            # 'CriterionInnovativeness', and field_value - Innovativeness(the value entered from the web portal)
            sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
                  "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user,0,1,project_id,'TypeOfSocialInnotation','CriterionInnovativeness',Innovativeness,project_id,Comment)
            #execute the sql query and commit
            cursor.execute(sql)
            conn.commit()
    except:
        # this exception probably handles a potential problem with the string conversion above
        # the sql query is the same as just above, in this except clause
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user, 0, 1, project_id,
                                                                                        'TypeOfSocialInnotation',
                                                                                        'CriterionInnovativeness',
                                                                                        Innovativeness, project_id,
                                                                                        Comment)
        #execute the query in the except clause and commit
        cursor.execute(sql)
        conn.commit()


    #if the length of project_data['Locations'] value, (which is a list containing a dictionary) is greater than 0
    #meaning it is not empty. and Address.strip() -(which is the address entered from the web portal, but stripped of leading
    #and trailing whitespaces) is not equal to the address in project_data['Locations']
    #this means if there is a location for the project in project_data, but it does not match what is entered in the web portal
    if len(project_data['Locations'])>0 and Address.strip()!=str(project_data['Locations'][0]['address']):
        #execute an sql Insert query and insert the values below, just as before; with table_name - the string 'ProjectLocation',
        # table field -the string 'Address' and field_value - Address, entry_id - project_data['Locations'][0]['id_location']
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user,0,1,project_id,'ProjectLocation','Address',Address,project_data['Locations'][0]['id_location'],Comment)
        #execute and commit query results
        cursor.execute(sql)
        conn.commit()
    #else; if the length of project_data['Locations'] is equal to 0 and the Address entered from the portal is
    #not an empty string or not equal to 'None', meaning an address is actually entered from the portal
    elif len(project_data['Locations']) == 0 and (Address != '' and Address != 'None'):
        #implement a similar sql insert statement as above, with table_field- the string 'Address', field_value - Address
        #and entry_id -> -1
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user, 0, 1, project_id,
                                                                                  'ProjectLocation', 'Address', Address,
                                                                                  -1,Comment)
        #execute the query and commit the result
        cursor.execute(sql)
        conn.commit()
    #if the length of project_data['Locations'] is greater than 0, meaning it is not empty and City entered from
    #the webportal, stripped of trailing and leading whitespaces is different from the value in project_data['Locations'][0]['city']
    #which is the project_data dictionary
    if len(project_data['Locations'])>0 and City.strip()!=project_data['Locations'][0]['city']:
        #implement the insert sql query below, as with those above, with table_field- the string 'City', field_value - City
        #entry_id - project_data['Locations'][0]['id_location']
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user,0,1,project_id,'ProjectLocation','City',City,project_data['Locations'][0]['id_location'],Comment)
        #execute and commit the sql query
        cursor.execute(sql)
        conn.commit()
    #else if the length of project_data['Locations'] is equal to zero and ther City entered at the portal is not
    #an empty string or equal to 'None', meaning a value is entered, then
    elif len(project_data['Locations']) == 0 and (City != '' and City != 'None'):
        # implement a similar sql insert statement as above, with table_field- the string 'City', field_value - City
        # and entry_id -> -1
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user, 0, 1, project_id,
                                                                                  'ProjectLocation', 'City', City,
                                                                                  -1,Comment)
        #execute and commit the query
        cursor.execute(sql)
        conn.commit()
    #if the length of project_data['Locations'] is greater than 0 and Country_f, the value of Country entered at the web portal
    #is not equal to project_data['Locations'][0]['country'], basically the value of country in the project_data dictionary
    if len(project_data['Locations'])>0 and Country_f!=project_data['Locations'][0]['country']:
        # implement the insert sql query below, as with those above, with table_field- the string 'Country', field_value - Country_f, the value
        # inputted from the web portal and entry_id - project_data['Locations'][0]['id_location']
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user,0,1,project_id,'ProjectLocation','Country',Country_f,project_data['Locations'][0]['id_location'],Comment)
        #execute and commit the query
        cursor.execute(sql)
        conn.commit()
    #but if the length of project_data['Locations'] is not equal to 0 and Country_f entered from the web portal is not an
    #empty string and also not equal to 'None'
    elif len(project_data['Locations'])==0 and (Country_f!='' and Country_f!='None'):
        #implement this sql query instead, which is the same as the above, except, table_field is the string 'Country' and
        #field_value - Country_f (the value entered from the web portal) and entry_id - -1
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user, 0, 1, project_id,
                                                                                  'ProjectLocation', 'Country', Country_f,
                                                                                  -1,Comment)
        #execute and commit the sql query
        cursor.execute(sql)
        conn.commit()


    #iterate through topics_to_add, which was also received from the webpage. This was in form of checckboxes, maybe it
    #translates to a list
    #do the following for each entry in topics_to_add
    for topic in topics_to_add:
        #implement the sql insert query below, just like the others above and set table_name - to string 'Project_Topics',
        #table_field - 'TopicName', field_value - topic and entry_id - -1
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user, 1, 0, project_id,
                                                                                        'Project_Topics',
                                                                                        'TopicName', topic, -1,
                                                                                        Comment)
        #execute the sql query and commit
        cursor.execute(sql)
        conn.commit()

    #for topics to exclude, iterate through topics_to_exclude, which was again recieved from the web portal
    for topic in topics_to_exclude:
        #implement sql query sql_sel which selects all from Project_Topics in the dbase where the Projects_idProject is the same as
        #that of the project_id in question, and Version like v4 or Version like Manual, and the TopicName is the same
        #as the topic being iterated
        sql_sel = "Select * from Project_Topics where Projects_idProject={0} and (Version like '%v4%' or Version like '%Manual%') and TopicName='{1}'".format(project_id,topic)
        #excute the sql query
        cursor.execute(sql_sel)
        #input all the entries from that sql query implementation into variable - entries
        entries = cursor.fetchall()
        #set variable id_entry to '-1'
        id_entry = -1
        #iterate through the data received from the sql query above
        for ent in entries:
            #set the id_entry to the value at index 0, which is idTopics
            id_entry = ent[0]

        #implement the sql query below, which is an insert statement. Insert into the table user_suggestions similar to
        #the previous inserts, set table_name - string 'Project_Topics', table_field - set to string 'Exclude'
        #field_value - 0 and entry_id - id_entry, which was determined just previously in the for-statment
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user, 0, 1, project_id,
                                                                                        'Project_Topics',
                                                                                        'Exclude', 0, id_entry,
                                                                                        Comment)
        #execute and commit the sql query
        cursor.execute(sql)
        conn.commit()

    #declare an empty string variable - desc
    desc = ""
    #iterate through the 'Descriptions' value in the project_data dictionary
    for description in project_data['Descriptions']:
        #append each entry to the variable to create one long string, and assign this to the variable - desc
        desc = desc + description
    #replace the carriage returns -\r and new line -\n, as well as double space in the desc string with single space
    desc = desc.replace('\r','').replace('\n','').replace(' ','')
    #assign the Description entry from the web portal to the variable - orig_desc
    orig_desc = Description
    #replace the carriage returns and the new line and double space in the string entered from the web portal with
    #a space
    Description = Description.replace('\r','').replace('\n','').replace(' ','')
    #if the description entered from the web portal does not match the description in the project_data dictionary:
    if Description!=desc:
        #then create an sql variable and assign it an Insert query, which inserts into the user_suggestions table as has been
        #done previously, with table_name - set to string 'AdditionalProjectData', table_field - set to string 'Description_sum',
        #field_value - set to orig_desc, which is the description entered from the portal, and entry_id set to -1
        sql = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,project_id, date_time,table_name,table_field,field_value,entry_id,Comment)" \
              "VALUES ('{0}',{1},{2},'{3}',NOW(),'{4}','{5}','{6}','{7}','{8}')".format(user,0,1,project_id,'AdditionalProjectData','Description_sum',orig_desc,-1,Comment)
        #execute the sql insert query and commit
        cursor.execute(sql)
        conn.commit()
    #iterate through actors_list, a list which was created above and used to hold a dictionary where actor details from the web portal
    #were entered, like name, website, etc
    for act in actors_list:
        #implement an sql insert query - act_sql to insert into the Actors table act['Name'] as the actor name,
        #act['Website'] as the actor website, the string 'ManualInput' as the SourceOriginallyObtained, and 57 as the DataSources_idDataSources
        act_sql = "Insert into Actors (ActorName,ActorWebsite,SourceOriginallyObtained,DataSources_idDataSources) Values ('{0}','{1}','{2}','{3}')".format(act['Name'],act['Website'],'ManualInput','57')
        #execute the sql query
        cursor.execute(act_sql)
        #we use the lastrowid property of the cursor object to retrieve the newly inserted value for the actor_id
        #column, which is auto incremented
        actor_id = cursor.lastrowid
        #implement another sql insert query sql_user_log, which inserts into the user_suggestions table username as - user,
        #add_suggestion set to 1, edit_suggestion - set to 0, entry_id as actor_id and the table_name as - the string 'Actors'
        sql_user_log = "Insert into user_suggestions (username,add_suggestion,edit_suggestion,entry_id,date_time,table_name,Comment) VALUES ('{0}','{1}','{2}','{3}',NOW(),'Actors','{4}')".format(
            user, 1, 0, actor_id,Comment)
        #execute the sql query
        cursor.execute(sql_user_log)
        #implement another sql insert query - act_location_sql, which inserts into the ActorLocation table, the Type as the string-
        #"Headquarters", the City as the act['City'] value, the Country as act['Country'] and Actors_idActors set to actor_id
        #recall we are still iterating through the list - actors_list from above
        act_location_sql = "Insert into ActorLocation (Type,City,Country,Actors_idActors) Values ('{0}','{1}','{2}','{3}')".format("Headquaters",act['City'],act['Country'],actor_id)
        #execute the sql query
        cursor.execute(act_location_sql)
    #iterate through knowmak_ready, the list obtained from the checkbox in the webportal
    for kr in knowmak_ready:
        #if an entry is equal to the string 'knowmak_ready'
        if kr == 'knowmak_ready':
            #the implement the sql update query sql_p below, which updates the Projects table by setting the value in
            # the KNOWMAK_ready column to 1.; where the Project_id is the same as that being considered
            sql_p = "Update Projects set KNOWMAK_ready = 1 where idProjects={0}".format(project_id)
            #execute the update query
            cursor.execute(sql_p)
    #commit the query execution result and close the connection and the cursor
    conn.commit()
    cursor.close()
    conn.close()
    #return the thank you page to show completion of edit submit
    return render_template('thank_you_project.html')


#the project view page
@webpage.route('/project_view/<id>', methods=['GET','POST'])
#the project_view funtion
def project_view(id):
    #connect to mysql
    conn = mysql.connect()
    cursor = conn.cursor()
    #assign the variable 'id' passed into the function to project_id
    project_id = id

    #implement an sql select statement in variable sq, which selcects distinct Topic names from the Project_Topics table
    #and sums the TopicScores and divide this sum by the Count of the TopicName in the Table,
    # where the version is like v4 and version like 'Manual' grouped by the Topic Names. The output is two columns
    #tn and Sum(TopicScore)/Count(TopicName) this basically calculates an average of the TopicScore for each distinct topicname
    sq = "SELECT Distinct(TopicName) as tn,Sum(TopicScore)/Count(TopicName) FROM EDSI.Project_Topics where (Version like '%v4%' or Version like '%Manual%') group by tn;"
    #execute the query
    cursor.execute(sq)
    #assign all the fetched data from the query to the variable - means
    means = cursor.fetchall()
    #create an empty dictionary - topic_means
    topic_means = {}
    #iterate through the list in the variable - means, which is basically the fetched data from the database
    for m in means:
        #assign the data at m[1], which is the calculated mean as the value for m[0] in the dictionary topic_means
        #hence in the dictionary topic_means, enter the first entry/key as m[0] and assign it's value as m[1]
        #it's been written in an abriged manner below
        topic_means[m[0]]=m[1]

    #implement an sql select query q, which selects all Projects from the Projects table where the project_id is the same
    #as that of the project in question, and Exclude is equal to 0
    q = "Select * from Projects where idProjects={0} and Exclude=0".format(project_id)
    #execute the query
    cursor.execute(q)
    #assign all the retrieved data to a variable - project_list
    project_list = cursor.fetchall()
    #create an empty dictionary - project_data
    project_data = {}
    #iterate through the fetched data from the database
    for project in project_list:
        #assign the following data from the indicies of each iterable as values to the dictionary elements as shown
        project_data['id'] = id
        project_data['project_name'] = project[2]
        project_data['type'] = project[4]
        project_data['DateStart'] = project[8]
        project_data['DateEnd'] = project[9]
        project_data['Website'] = project[11]
        project_data['Facebook'] = project[13]
        project_data['Twitter'] = project[14]
        project_data['FirstDataSource'] = project[16]
        project_data['Knowmak_ready'] = project[24]
    #assign an empty list to the 'Locations' element in the project_data dictionary
    project_data['Locations'] = []
    #implement an sql select query q1, which selects all from the ProjectLocation table where the project_id is the
    #same as that being considered
    q1 = "Select * From ProjectLocation where Projects_idProjects={0}".format(project_id)
    #execute the query
    cursor.execute(q1)
    #assign all the retrieved data to a variable - locations
    locations = cursor.fetchall()
    #iterate through the retrieved data in locations
    for loc in locations:
        #first create a dictionary called - location
        location = {}
        #as you iterate through the retrieved data, add the data in the indices as shown below to the elements in the
        #location dictionary below
        location['id_location'] = loc[0]
        location['loc_type'] = loc[1]
        location['address']=loc[3]
        location['city']=loc[4]
        location['country'] = loc[5]
        location['longitude'] = loc[9]
        location['latitude']=loc[10]
        #append the location dictionary to project_data['Locations'], hence, append it to the list which was the value
        #of Locations in the project_data dictionary. This gives you a dictionary within a list
        project_data['Locations'].append(location)

    #implement a select query q2, which selects all from the Actors_has_Projects table, left_joined to the Actors table on
    #id_Actors=Actors_idActors, where the Projects_idProjects is the same as the project_id being considered
    q2 = "SELECT * FROM EDSI.Actors_has_Projects left join Actors on idActors=Actors_idActors where Projects_idProjects={0}".format(project_id)
    #execute the query q2
    cursor.execute(q2)
    #create a variable - actors which holds all the data fetched from the database on q2 execution
    actors = cursor.fetchall()
    #create an element/key in the project_data dictionary, called 'Actors' and assign it an empty list
    project_data['Actors'] = []
    #iterate through the retrieved data
    for actor in actors:
        #create an empty dictionary- act to hold the data retrieved from the database
        act = {}
        # as you iterate through the retrieved data, add the data in the indices as shown below to the elements in the
        # act dictionary as below
        act['Name'] = actor[5]
        act['Website'] = actor[12]
        #append the dictionary - act to the list value of project_data['Actors'], hence, this becomes a list containing
        #a dictionary
        project_data['Actors'].append(act)

    #implement the select query q3 which selects all the data from the table AdditionalProjectData where the Projects_idProjects
    #is equal to the project_id in question, and the FieldName is like 'Description_sum' and the SourceURL is like 'Manual'
    q3 = "SELECT * FROM EDSI.AdditionalProjectData where Projects_idProjects={0} and FieldName like '%Description_sum%' and SourceURL like '%Manual%'".format(
        id)
    #execute the query
    cursor.execute(q3)
    #add all the data retrieved from the query in a variable - descriptions
    descriptions = cursor.fetchall()
    #create an empty list- Descriptions
    Descriptions = []
    #iterate through the retrieved data from the database
    for description in descriptions:
        ##append the data at index 2 position of the retrieved data from the database to the list - Descriptions
        #this data btw if the value column - which is the text description
        Descriptions.append(description[2])
    #if the length of the list Descriptions is 0, meaning there is no description
    if len(Descriptions) == 0:
        #implement another select query q3, this time, select all from the AdditionalProjectData table where the Projects_idProjects
        #matches the project_id in question and the FieldName is like Description_sum, but the SourceURL is like v2
        q3 = "SELECT * FROM EDSI.AdditionalProjectData where Projects_idProjects={0} and FieldName like '%Description_sum%' and SourceURL like '%v2%'".format(
            id)

        #execute the query
        cursor.execute(q3)
        #fetch all the data from the query and assign them to the variable - descriptions
        descriptions = cursor.fetchall()

        #iterate through the fetched data in descriptions again
        for description in descriptions:
            #append the data at the index position 2 in the retrieved descriptions to the list Descriptions. This is
            #the value column, and contains the text
            Descriptions.append(description[2])
    #if the length of the Descriptions is equal to 0, meaning there is no description,
    if len(Descriptions) == 0:
        #implement another sql select query - q3 which selects same as the above, except now, SourceURL is like v1
        q3 = "SELECT * FROM EDSI.AdditionalProjectData where Projects_idProjects={0} and FieldName like '%Description_sum%' and SourceURL like '%v1%'".format(
            id)

        #execute the query q3
        cursor.execute(q3)
        #assign all the retrieved data to the variable - descriptions
        descriptions = cursor.fetchall()

        #iterate through descriptions
        for description in descriptions:
            # append the data at the index position 2 in the retrieved descriptions to the list Descriptions. This is
            # the value column, and contains the text
            Descriptions.append(description[2])

    #if the length of Descriptions is equal to 0, meaning there is no description
    if len(Descriptions) == 0:
        #implement sql select query q3 which selects from the AdditionalProjectData as above, but this time where the
        #FieldName is like Desc
        q3 = "SELECT * FROM EDSI.AdditionalProjectData where Projects_idProjects={0} and FieldName like '%Desc%'".format(
            id)
        #execute the cursor
        cursor.execute(q3)
        #assign all retrieved data to the variable - descriptions
        descriptions = cursor.fetchall()
        #iterate through the data retrieved from the database
        for descriptionA in descriptions:
            #if the iterable is an empty string, then continue; that is, go back to the beginning of the loop
            if descriptionA[2] == "":
                continue
            #append the description to the list - Descriptions
            Descriptions.append(descriptionA[2])

    #length of the list - Descriptions is greater than 0,meaning the list is not empty; assign the value at the index
    #position 0 of the list Descriptions, to the variable - description
    if len(Descriptions) > 0:
        description = Descriptions[0]
    #if len (Descriptions) is not greater than 0, then set the variable - description to an empty string
    else:
        description = ""
    #create an element - Descriptions in the project_data dictionary and assign it an empty list
    project_data['Descriptions'] = []
    #append the variable -description-to this empty list, creating a value of a list of description for the project_data
    #dictionary element - 'Descriptions'
    project_data['Descriptions'].append(description)
    # q3 = "SELECT * FROM EDSI.AdditionalProjectData where Projects_idProjects={0} and FieldName like '%Description_sum%' and SourceURL like '%Manual%'".format(
    #     project_id)
    # cursor.execute(q3)
    # descriptions = cursor.fetchall()
    # project_data['Descriptions'] = []
    # for description in descriptions:
    #     project_data['Descriptions'].append(description[2])
    # if len(project_data['Descriptions'])==0:
    #     if project_data['Knowmak_ready']==1:
    #         q3 = "SELECT * FROM EDSI.AdditionalProjectData where Projects_idProjects={0} and FieldName like '%Description_sum%' and SourceURL like '%v1%'".format(
    #         project_id)
    #     else:
    #         q3 = "SELECT * FROM EDSI.AdditionalProjectData where Projects_idProjects={0} and FieldName like '%Description_sum%' and SourceURL like '%v2%'".format(
    #             project_id)
    #     cursor.execute(q3)
    #     descriptions = cursor.fetchall()
    #
    #     for description in descriptions:
    #         project_data['Descriptions'].append(description[2])
    # if len(project_data['Descriptions']) == 0:
    #     q3 = "SELECT * FROM EDSI.AdditionalProjectData where Projects_idProjects={0} and FieldName like '%Desc%'".format(
    #         project_id)
    #     cursor.execute(q3)
    #     descriptions = cursor.fetchall()
    #     project_data['Descriptions'] = []
    #     for description in descriptions:
    #         project_data['Descriptions'].append(description[2])




    #create an sql variable q4 which holds a select query that selects all the entries from the table - TypeOfSocialInnovation
    #where the SourceModel is like 'Manual', and the Projects_idProjects is the same as that of the project_id in question
    q4 = "SELECT * FROM EDSI.TypeOfSocialInnotation where SourceModel like '%Manual%' and Projects_idProjects={0}".format(
        project_id);
    #execute the query - q4
    cursor.execute(q4)
    #assign all the retrieved data to the variable - marks
    marks = cursor.fetchall()
    #if the length of the variable 'marks' is equal to 0, meaning there was nothing retrieved from the query,
    if len(marks)==0:
        #implement another select query 'q4', similar to that above, but with SourceModel like v14
        q4 = "SELECT * FROM EDSI.TypeOfSocialInnotation where SourceModel like '%v14%' and Projects_idProjects={0}".format(project_id);
        #execute the query
        cursor.execute(q4)
        #assign  all the retrieved data to the variable - marks
        marks = cursor.fetchall()
    #iterate through the variable - marks
    for mark in marks:
        #add the following values at these indices, as values of the elements in the project_data dictionary as shown below
        project_data['Outputs']=mark[1]
        project_data['Objectives']=mark[2]
        project_data['Actors_s']=mark[3]
        project_data['Innovativeness']=mark[4]
    #implement an sql query which selects all from the Project_Topics table where the Projects_idProjects is same as the
    #project_id being considered, and the Version is like v5 or like Manual
    q5 = "Select * from Project_Topics where Projects_idProject={0} and (Version like '%v5%' or Version like '%Manual%')".format(project_id)
    #execute the query
    cursor.execute(q5)
    #fetch all data from the query execution and assign them to the variable - topics
    topics = cursor.fetchall()
    #create an empty list - r_topics
    r_topics = []
    #iterate through topics, the data retrieved from the query q5
    for topic in topics:
        #assign the value at index 9 to length, the value at index 2 to score, and the value at index 1 to topic_name
        lenght = topic[9]
        score = topic[2]
        topic_name = topic[1]
        #if the value score, which is the TopicScore in the database is greater than 0.7
        if score>0.7:
            #then append the following to the r_topics list, taking these values from these index postions of our retrieved data
            r_topics.append({"TopicName":topic[1],"TopicScore1":topic[2],"TopicScore2":topic[3],"Keywords":topic[4]})
    #     keywords = topic[4].split(',')
    #     if len(keywords)<=1:
    #         continue
    #
    #     if lenght>100000:
    #         score = score*10
    #     elif lenght>50000:
    #         score = score*7
    #     elif lenght>30000:
    #         score = score*2
    #     elif lenght>10000:
    #         score = score*1.7
    #
    #     if score>0.7*topic_means[topic_name]:
    #         r_topics.append({"TopicName":topic[1],"TopicScore1":topic[2],"TopicScore2":topic[3],"Keywords":topic[4]})
    #######
    #declare another variable r_topics2 which takes as a value the result of the sorted r_topics below
    #the sorted function sorts the r_topics according to the TopicScore1, and does this in ascending order, but
    #this order is reversed with the 'reverse = True" keyword. The lambda stands in as an anonymous fucntion (more
    #online). TopicScore1 is the TopicScore column in the database
    r_topics2 = sorted(r_topics, key=lambda k: k['TopicScore1'],reverse=True)
    #if the length of r_topics2 is equal to 0
    if len(r_topics2)==0:
        #close the connection
        cursor.close()
        conn.close()
        #assign r_topics2 as the value to project_data['Topic']. This is not clear at all. Why are we assigning
        #r_topics2 as the value of project_data['Topic'] if its empty? ---Have to confirm this on run
        project_data['Topic'] = r_topics2

        #return the project_data out to the project_view request
        return render_template('project_view.html', project=project_data)
    top_topic = r_topics2[0]
    # r_topics3 = []
    # for r_top in r_topics2:
    #     if r_top["TopicScore1"]>0.4*top_topic["TopicScore1"]:
    #         r_topics3.append(r_top)

    #assign the first ten items in r_topics2 to r_topics2 variable, basically the top ten topics, based on the sorting
    r_topics2 = r_topics2[:10]
    #assign the value - r_topics2 to the 'Topic' element in the project_data dictionary
    project_data['Topic'] = r_topics2
    #close the cursor and the connection
    cursor.close()
    conn.close()
    #return the project_data in response to the request for viewing
    return render_template('project_view.html',project = project_data)


@webpage.route('/suggest_related_project', methods=['POST'])
#the suggested_related_project function
def suggest_related_project():
    related_id = request.form['project_id']
    return render_template('suggest_related.html',related_project= related_id)

@webpage.route('/check_projects', methods=['POST','GET'])
#this is the check projects method
def check_projects():
    #connection to mysql is established
    conn = mysql.connect()
    cursor = conn.cursor()
    #implement sql query to select all from Projects table where ReadyForCheck = 1 and KNOWMAK_ready=0 and Exclude = 0
    q = "Select * from Projects where ReadyForCheck=1 and KNOWMAK_ready=0 and Exclude=0"
    #execute the query
    cursor.execute(q)
    #declare a variable -> project_list to hold all the selection from the query
    project_list = cursor.fetchall()
    #create an empty list - projects
    projects = []
    #iterate through project_list, which contains all the data fetched from the database
    for pro in project_list:
        #implement an sql query q2 which selects all from the ProjectLocation table where the Projects_idProjects
        #matches the idProjects of the project in question, each fetched from the database above (query q)
        q2 = "Select * from ProjectLocation where Projects_idProjects={0}".format(pro[0])
        #execute the query
        cursor.execute(q2)
        #declare a variable locs which holds all the data fetched from the location table above
        locs = cursor.fetchall()
        #iterate through the data fetched from q2
        for loc in locs:
            #assign the data at index 5 to variable Country
            Country = loc[5]
        #implement an sql query q2 to hold the select statement which selects all from the AdditionalProjectData table where the
        #FieldName is like Description_sum and the SourceURL is like v1 and the Project_id matches that of the fetched ones above
        #note, this is still under the for pro in project_list function
        q2 = "Select * from AdditionalProjectData where FieldName like '%Description_sum%' and SourceURL like '%v1%' and  Projects_idProjects={0}".format(
            pro[0])
        #execute the query
        cursor.execute(q2)
        #assign all the fetched data to a variable - descs
        descs = cursor.fetchall()
        #declare an Empty string - Description
        Description = ""
        #iterate through descs, containing all the fetched description data
        for desc in descs:
            #concatenate the data at index 2 to the Description string with a space; assign this to back to the Description variable
            #the data at index 2 is the value of the Description, basically the description text
            Description = Description + desc[2] + " "
        #if Description is equal to an empty string, meaning there was no Description, then
        if Description == "":
            #implement an sql query q2, which selects all from the AdditionalProjectData table, as above, but this time
            #with FieldName like 'Desc'; for the project_id in question
            q2 = "Select * from AdditionalProjectData where FieldName like '%Desc%' and  Projects_idProjects={0}".format(
                pro[0])
            #execute the cursor
            cursor.execute(q2)
            #assign all the retrieved data from the query into a variable - descs
            descs = cursor.fetchall()
            #create a Description variable containing an empty string
            Description = ""
            #iterate through the retrieved data in descs
            for desc in descs:
                #concatenate the data at index 2, basically the description text in the database to the empty string, Description
                #seperated by spaces
                Description = Description + desc[2] + " "
        #slice the Description string to go from 0 to 150 only
        Description = Description[0:150] + "..."
        #append the following to the list - projects which was created above, so that each projects would have these. You
        #are appending a dictionary here. Note, project name is from pro[2], extracted from the Projects query
        projects.append({"id": pro[0], "Name": pro[2], "Country": Country, "Description": Description})
    #close cursor and connection
    cursor.close()
    conn.close()
    #render the projects list as a response to the check_projects response
    return render_template('check_projects.html',projects=projects)

@webpage.route('/knowmak_ready', methods=['POST','GET'])
#declare function knowmak_ready
def knowmak_ready():
    #connect to mysql
    conn = mysql.connect()
    cursor = conn.cursor()
    #implement an sql select query q, which selects all from Projects table, where KNOWMAK_ready = 1 and Exclude = 0
    q = "Select * from Projects where KNOWMAK_ready=1 and Exclude=0"
    #execute the query
    cursor.execute(q)
    #assign all the data extracted from the query implementation to variable - project_list
    project_list = cursor.fetchall()
    #declare an empty list called projects
    projects = []
    #iterate through the retrieved data in project_list
    for pro in project_list:
        #implement a query q2 which selects all from the ProjectLocation table where Project_iProjects is the same as that
        #project_id being considered
        q2 = "Select * from ProjectLocation where Projects_idProjects={0}".format(pro[0])
        #execute the query
        cursor.execute(q2)
        #assign all the extracted data from the implementation of q2 to variable locs
        locs = cursor.fetchall()
        #iterate through locs
        for loc in locs:
            #assign the data at index 5 to variable Country
            Country = loc[5]
        #implement another select query which selects all from the AdditionalProjectData table where the FieldName is like
        #Desc and the Projects_idProjects is the same as that being considered
        q2 = "Select * from AdditionalProjectData where FieldName like '%Desc%' and  Projects_idProjects={0}".format(
            pro[0])
        cursor.execute(q2)
        #assign all the fetched data to variable descs
        descs = cursor.fetchall()
        #declare an empty string Description
        Description = ""
        #iterate through the data in descs
        for desc in descs:
            #concatenate the data at index 2 in each desc for that project to the string Description, seperated by space
            Description = Description + desc[2] + " "
        #slice the Description, taking from 0-150 and assign this to the string Description
        Description = Description[0:150] + "..."
        #append the dictionary below to the list projects declared above
        projects.append({"id": pro[0], "Name": pro[2], "Country": Country, "Description": Description})
    #close the connection
    cursor.close()
    conn.close()
    #return projects, the list to the knowmak_ready request; hence you will return the project_id, project name, country
    #and description which have been marked as knowmak_ready, and marked not to exclude, to the request for knowmak_ready
    #projects
    return render_template('knowmak_ready.html',projects=projects)


@webpage.route('/error', methods=['POST','GET'])
#error fucntion
def error():
    return render_template('error.html')


