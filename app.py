import pandas as pd, plotly.express as pl, dash
from dash import html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc


# WHAT LIBRARIES, WHAT USER IS DOING, OUTPUT THATS SHOWED/RELEVENCE

df = pd.read_csv("UW-Seattle_20110-20161-Course-Grade-Data_2016-04-06.csv")


# Takes a profs name in the format *First name* *Middle Initial* *Last Name*
# returns a dict with the following data format:
# {Term: Course + Average GPA}}
def prof_teaching_history(df, prof_name = 'Sean A Munson'):


    prof_name_clean = convert_prof_name(prof_name)
    # get dataframe of classes taught for prof
    df = df.loc[df['clean_names'] == prof_name_clean]
    df.head()
    course_dict = {}
    for index, row in df.iterrows():
        course_dict[row['clean_term']] =  str(row['clean_number']) + ", " + str(row['Course_Title']).title() + ", Average GPA: " + str(row['Average_GPA'])

    return course_dict



#takes input for a course number
#returns a bar chart of the number of students in a class each quarter
def students_per_quarter(df, course = 'MATH 124'):
    # group all sections of a course taught in the same quarter together
    df = df.groupby(['Term', 'clean_number']).agg({'Student_Count': 'sum'}).reset_index()
    # clean whitespaces
    df.columns = df.columns.str.strip()
    df = df.loc[df['clean_number'] == course.upper()]
    fig = pl.bar(df, x="Term", y="Student_Count")
    return fig

#takes input for a course number
#returns a scatterplot of the course and it's average GPA each quarter
def avg_gpa_scatterplot(df, course = 'MATH 124'):
    #filters out courses

    # Gets dataframe but merges all instructors for a course offering per quarter into one string
    # used to list profs teaching all the sections for each quarter when hovering
    df1 = df.loc[df['clean_number'] == course.upper()]
    df1 = df1.drop_duplicates(subset = ['Primary_Instructor'])
    df1 = df1.groupby(['Term', 'clean_number'])['Primary_Instructor'].apply(lambda x: ','.join(x)).reset_index()


    # group all sections of a course taught in the same quarter together
    # and finds average GPA across sections
    df = df.loc[df['clean_number'] == course.upper()]
    df.columns = df.columns.str.strip()
    df = df.groupby(['Term', 'clean_number']).agg({'Average_GPA': 'mean'}).reset_index()

    #Joins the two dataframes together
    df = df.merge(df1, left_on = "Term", right_on = "Term")

    # remove extranous characters from term
    df['Term'] = df["Term"].str[6:]

    fig = pl.scatter(df,
                     x="Term",
                     y="Average_GPA",
                     hover_data=["Primary_Instructor"])

    return fig


#takes input for a course number
#Returns dict of all profs (key) who have taught the course and average GPA (value) in their class
def course_gpa_and_prof(df, course = 'MATH 124'):
    #filters out courses
    df = df.loc[df['clean_number'] == course.upper()]
    df = df.groupby(['Primary_Instructor']).agg({'Average_GPA': 'mean'}).reset_index()
    prof_dict = {}
    for index, row in df.iterrows():
        prof_dict[row['Primary_Instructor']] = row['Average_GPA']
    return prof_dict

#Format for prof name for user input is first name middle initial(s) last name
#method converts from this format to format of name seen in dataframe.
def convert_prof_name(prof_name):
    # convert name user inputted to same format as seen in the CSV
    prof_name = prof_name.upper()
    prof_name_clean = ""
    s = prof_name.split()
    if len(s) == 2:
        prof_name_clean = s[1] + " " + s[0]
    else:
        prof_name_clean = s[len(s) - 1] + " " + s[0]
        # for multiple middle names
        for x in s[1:]:
            if x == s[len(s) - 1]:
                break
            prof_name_clean = prof_name_clean + " " + x
    return prof_name_clean

#Takes a prof name and course for parameters
#returns histogram of all letter grades they have given while teaching the class
def prof_course_grade_histogram(df, prof_name = 'Sean A Munson', course = 'HCDE 310'):

    #Filters data
    clean_prof_name = convert_prof_name(prof_name)
    df = df.loc[df['clean_number'] == course.upper()]
    df = df.loc[df['clean_names'] == clean_prof_name]

    # Groups all the quarters the prof has taught the course
    # sums all the grades they have given while teaching the course
    df = df.groupby(['clean_names', 'clean_number']).agg({
        'A':'sum',
        'A-':'sum',
        'B+':'sum',
        'B':'sum',
        'B-':'sum',
        'C+':'sum',
        'C':'sum',
        'C':'sum',
        'C-':'sum',
        'D+':'sum',
        'D':'sum',
        'D-':'sum',
        'F':'sum',
        'W':'sum'})
    grade_dict = {}
    for column in df:
        grade_dict[column] = df[column].values[0]
    fig = pl.bar(
                    x = grade_dict.keys(),
                    y = grade_dict.values(),
                    labels={
                        "x": "Letter Grade",
                        "y": course + " Grades Given",
                    }
    )

    return fig


def generate_list(dict):
    for key, value in dict.items():
        dict[key] = str(key) + " " + str(dict[key])

    return html.Ul(children = [html.Li(value) for key, value in dict.items()])




# DATA CLEANING
# removes section (A, B, C) from course numbers
df['clean_number'] = df["Course_Number"].str[:-2]
# many existing prof names may contain these characters,
# cleaning for easier filtering
df['clean_names'] = df['Primary_Instructor'].str.replace(".", "")
df['clean_names'] = df['clean_names'].str.replace(",", "")
# remove extranous characters from term
df['clean_term'] = df["Term"].str[7:]
df['clean_term'] = df["clean_term"].str[:-1]


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Tabs(id="tabs-styled", value='tab-1', children=[
        dcc.Tab(label='Tab one', value='tab-1', children=[
        ]),
        dcc.Tab(label='Tab two', value='tab-2', children=[
        ]),
        dcc.Tab(label='Tab three', value='tab-3', children=[
        ]),
        dcc.Tab(label='Tab four', value='tab-4', children=[
        ]),
        dcc.Tab(label='Tab five', value='tab-5', children=[
        ])
        ,
    ]),
    html.Div([
        html.P('Input Course Number (EX, Math 126)'),
        dcc.Input(id='my-input', value='initial value', type='text'),
        html.Br(),
        html.Br(),
        html.P('Input Professor Name In The Format *First Name* *Middle Initial(s)* *Last Name* (No *)'),
        dcc.Input(id='my-input2', value='initial value', type='text'),
        html.Br()
    ]),
    html.Div(id='tabs-content')
])


@app.callback(Output('tabs-content', 'children'),
              [Input('tabs-styled', 'value'),
              Input('my-input', 'value'),
              Input('my-input2', 'value')])
def render_content(tab, input, input2):
    if tab == 'tab-1':
        try:
            fig = students_per_quarter(df, input)
            return html.Div([
                html.H3('Students Enrolled Per Quarter'),
                html.Br(),
                html.P("Takes a course name as an input and returns a barchart showing the "
                       "amount of students enrolled for each quarter"),
                dcc.Graph(figure=fig)
            ])
        except:
            return html.Div([
                html.H3('Students Enrolled Per Quarter'),
                html.Br(),
                html.P("Takes a course name as an input and returns a barchart showing the "
                       "amount of students enrolled for each quarter"),
                html.Br(),
                html.P("Error, please re-enter query")
            ])
    elif tab == 'tab-2':
        try:
            fig = avg_gpa_scatterplot(df, input)
            return html.Div([
                html.H3('Average GPA Scatterplot'),
                html.Br(),
                html.P("Takes a course name as an input and returns a scatterplot showing the "
                       "average GPA for all sections taught each quarter"),
                dcc.Graph(figure=fig)
            ])
        except:
            return html.Div([
                html.H3('Average GPA Scatterplot'),
                html.Br(),
                html.P("Takes a course name as an input and returns a scatterplot showing the "
                       "average GPA for all sections taught each quarter"),
                html.Br(),
                html.P("Error, please re-enter query")
            ])
    elif tab == 'tab-3':
        try:
            fig = prof_course_grade_histogram(df, input2, input)
            return html.Div([
                html.H3('Professor Course Histogram of Grades'),
                html.Br(),
                html.P("Takes a course name and professor name as an input and returns a histogram showing "
                       "the amount of letter grades they have given for all their quarters teaching " 
                       "the course"),
                dcc.Graph(figure=fig)
            ])
        except:
            return html.Div([
                html.H3('Professor Course Histogram of Grades'),
                html.Br(),
                html.P("Takes a course name and professor name as an input and returns a histogram showing "
                       "the amount of letter grades they have given for all their quarters teaching "
                       "the course"),
                html.Br(),
                html.P("Error, please re-enter query")
            ])
    elif tab == 'tab-4':
        try:
            return html.Div([
                html.H3('Professor Teaching History'),
                html.Br(),
                html.P("Takes a professor name as an input and returns a list of "
                       "all the courses they have taught and their average GPA in that course"),
                generate_list(prof_teaching_history(df, input2))
            ])
        except:
            return html.Div([
                html.H3('Professor Teaching History'),
                html.Br(),
                html.P("Takes a professor name as an input and returns a list of "
                       "all the courses they have taught and their average GPA in that course"),
                html.Br(),
                html.P("Error, please re-enter query")
            ])
    elif tab == 'tab-5':
        try:
            return html.Div([
                html.H3('Average Course GPA For Professor'),
                html.Br(),
                html.P("Takes a course number as an input and returns a list of all professors"
                       "who have taught the course and the average GPA in the course"
                       "across all quarters taught"),
                generate_list(course_gpa_and_prof(df, input))
            ])
        except:
            html.H3('Average Course GPA For Professor'),
            html.Br(),
            html.P("Takes a course number as an input and returns a list of all professors"
                   "who have taught the course and the average GPA in the course"
                   "across all quarters taught"),
            html.Br(),
            html.P("Error, please re-enter query")

if __name__ == '__main__':
    app.run_server(debug=True)