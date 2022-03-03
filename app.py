#Import packages and adjust parameters
import pandas as pd
#import psycopg2 #only import if database is loaded on PosgreSQL (See line 15)
import numpy as np
import streamlit as st
import calendar
import plotly.express as px
import plotly.graph_objects as go
st.set_option('deprecation.showPyplotGlobalUse', False)
st.set_page_config(page_title='Elmo Jose Jr. ESE Exam',layout='wide')

#This is the header of the page
st.title("2019 Employee Activity Report")

##This block is commented out since I did not have enough time to export the database when
# conducting the Streamlit --> GitHub --> GitLab --> Heroku migration
# 
#  
# #Connect Postgresql to Python
# con=psycopg2.connect(
#     user="postgres",
#     database="postgres",
#     host="localhost",
#     password="postgres"
# )
## Conduct SQL Query from checkins table in PosgreSQL
# df = pd.read_sql("SELECT * from \"checkins\"",con)

#Load data onto application
df = pd.read_csv('checkins.csv')

#Converting data to a DataFrame created separate columns for YY-MM-DD for easier data manipulation
df = df[["user_id","manager_id","project_id","date","hours"]]
df['date']=pd.to_datetime(df['date'],format='%Y-%m-%d')
df['year']=df['date'].dt.year
df['month']=df['date'].dt.month
df['day']=df['date'].dt.day

#Filter check-ins based on user_id. Store relevant data entries per user_id in a dictionary
i = 1
user_id={}
#Total of 57 employees, hence the decision to loop to the prescribed number
while i < 58:
    user_id[i]=df[df['user_id']==i]
    i=i+1

#This section corresponds to the General Report section
with st.expander('General report',expanded=True):
    a1,a2=st.columns((2,2)) #assign columns on the webpage
    with a1:
        st.header('Hours logged by employees on 2019')
        ##Annual monthly hours checked-in for all employees
        monthly_checkin = df.groupby('date' and 'month')['hours'].sum().reset_index() #group by month and sum total hours
        ##Plotting
        fig1 = px.line(monthly_checkin,x='month',y='hours', #Constructed line plot to visualize the trend
        labels=dict(hours='Hours logged by all employees',month='Month (Numerical)'))
        st.plotly_chart(fig1)
    
    with a2:
        tot_hours = int(np.sum(df['hours'])) #Get sum of all hours logged in the entire DataFrame
        tot_checkin = int(len(df)) #Get the total number of entries (rows) in the DataFrame
        ave_hrs_per_checkin = tot_hours/tot_checkin #Calculate check-in rate (hrs/check-in)
        ave_checkin_per_hrs = tot_checkin/tot_hours #Calculate check-ins that occur per hour
        #st.metric creates the "metric" like display of the values above
        st.metric(label='Hours logged by employees on 2019',value=tot_hours)
        st.metric(label='Total check-ins by employees on 2019', value=tot_checkin)
        st.metric(label='Employee check-in rate (check-ins per hour)',value="%.2f" % ave_checkin_per_hrs)
        st.metric(label='Hours logged per check-in', value="%.2f" % ave_hrs_per_checkin)

#This section corresponds to the Per-user filtered view section, the main block of the web application
with st.expander("Per-user filtered view",expanded=True):
    b1,b2=st.columns((2,2)) #Assign columns on this section
    #b1 column is the annual report (segmented by months) for a single employee
    with b1:
        #pick variable stores the chosen employee (user_id) from the number input box
        pick = st.number_input('Choose employee user_id',min_value=1,max_value=57,help='user_id from 1 to 57')
        p = int(pick) #convert pick variable to an integer to gain functionality across dataframe and indices
        st.header("2019 monthly check-ins by employee (user_id: {})".format(p),)
        #employee variable stores all rows which pertain to the specific user_id = p
        employee = user_id[p]
        #Constructing the table
        fig2 = go.Figure(data=[go.Table(
        header=dict(values=list(employee.iloc[:,0:5]), #disregards isolated year, month, and day columns to eliminate redundancy
                    fill_color='black',
                    font = dict(color = 'white', size = 15),
                    align='left'),
        cells=dict(values=[employee.user_id,employee.manager_id,employee.project_id,employee.date,employee.hours],
                    fill_color='#262730',
                    font = dict(color = 'white', size = 12),
                align='left'))
        ])
        st.plotly_chart(fig2)

        #Employee total hrs and check-ins (annual)
        tot_month_checkin = int(len(employee)) #this gets the overall check-in of an employee for the entire year
        tot_month_hours = np.sum(employee['hours']) #this gets the total hours logged by an employee for the entire year
        tot_checkin_rate = tot_month_checkin/tot_month_hours #this gets the check-in rate of an employee for the entire year
        tot_hours_per_checkin_ = tot_month_hours/tot_month_checkin #this gets the hours logged per check-in of an employee for the entire year
        #st.metric creates the "metric" like display of the values above
        st.metric(label='Overall check-ins by employee (user_id: {})'.format(pick),value=tot_month_checkin)
        st.metric(label='Hours logged by employee (user_id: {})'.format(pick),value=tot_month_hours)
        st.metric(label='Check-in rate of employee (user_id: {})'.format(pick),value="%.2f" %tot_checkin_rate)
        st.metric(label='Hours logged per check-in by employee (user_id: {})'.format(pick),value="%.2f" %tot_hours_per_checkin_)

        #We get the total number of hours logged per month and do it for all months
        monthly_performance = employee.groupby('date' and 'month')['hours'].sum().reset_index()
        #Plotting check-ins
        fig3 = px.line(monthly_performance,x='month',y='hours',
        labels=dict(hours='Hours Logged In',month='Month (Numerical)'))
        fig3.update_layout(
            xaxis=dict(tickmode='linear',tick0=1,dtick=1)
        )
        st.plotly_chart(fig3)

    #b2 column is the monthly report (segmented by days) for a single employee
    with b2:
        #month variable stores the chosen month from the number input box
        month = st.number_input('Choose month',min_value=1,max_value=12,help='use numerical (e.g. January = 1)')
        month = int(month) #convert month variable to an integer to gain functionality across dataframe and indices
        month_name = calendar.month_name[month] #Assign a variable for the corresponding name of numerical month (e.g. January = 1)
        #Adds up the total number of hours contributed per day in a given month for a specific employee
        daily_performance = employee[employee['month']==month]
        daily_performance = daily_performance.groupby('date' and 'day')['hours'].sum().reset_index()
        #Conditional statement to check if hours were logged by an employee on the chosen month
        if (employee['month']==month).any(): #if employee logged hours on a month...
            st.header('Daily check-ins by employee (user_id: {}) on {} 2019'.format(pick,month_name))
            #Constructing the table  
            fig4 = go.Figure(data=[go.Table(
            header=dict(values=list(daily_performance.iloc[:,0:2]),
                        fill_color='black',
                        font = dict(color = 'white', size = 15),
                        align='center'),
            cells=dict(values=[daily_performance.day,daily_performance.hours],
                        fill_color='#262730',
                        font = dict(color = 'white', size = 12),
                    align='center'))
            ])
            st.plotly_chart(fig4)
            #Employee total hrs and check-ins (monthly)
            tot_day_checkin = int(len(daily_performance))#this gets the daily check-in of an employee for the entire month
            tot_day_hours = np.sum(daily_performance['hours']) #this gets the total hours logged by an employee for the entire month
            tot_day_rate = tot_day_checkin/tot_day_hours #this gets the check-in rate of an employee for the entire month
            daily_hours_per_checkin_ = tot_day_hours/tot_day_checkin #this gets the hours logged per check-in of an employee for the entire month
            #st.metric creates the "metric" like display of the values above
            st.metric(label='{} check-ins by employee (user_id: {})'.format(month_name,pick),value=tot_day_checkin)
            st.metric(label='Hours logged by employee (user_id: {}) on {}'.format(pick,month_name),value="%.2f" %tot_day_hours)
            st.metric(label='{} check-in rate of employee (user_id: {})'.format(month_name,pick),value="%.2f" %tot_day_rate)
            st.metric(label='Hours logged per check-in by employee (user_id: {}) on {}'.format(pick,month_name),value="%.2f" % daily_hours_per_checkin_)
            #Plotting check-ins
            fig2 = px.line(daily_performance,x='day',y='hours',
            labels=dict(hours='Hours Logged In',day='Day ({}-XX)'.format(month_name)))
            fig2.update_layout(
                xaxis=dict(tickmode='linear',tick0=1,dtick=1)
            )
            st.plotly_chart(fig2)
        else: #if employee did not log hours on that month --> display no check-ins
            st.header("No check-ins on {}".format(month_name))

#This section corresponds to the Employee and manager rankings section
with st.expander("Employee and manager rankings"):
    c1,c2 = st.columns(2) #assign columns on the page
    #c1 column shows the top 10 performing employees based on hours logged
    with c1:
        st.header('Top 10 employees with most hours logged (2019)')
        ##Annual Employee Hours Ranking (across all employees)
        hour_group = df.groupby('user_id')['hours'].sum().reset_index() #group employee and get total hours for each employee
        hour_rankings= hour_group.sort_values(by='hours',ascending=False) #sort values in descending order to display top candidates
        hour_rankings.insert(0,'Ranking',range(1,1+len(hour_rankings))) #insert the Rank column on leftmost column
        hour_rankings.reset_index(drop=True,inplace=True)
        top_10 = hour_rankings[0:10] #Select first 10 row entries and assign them to the top_10 variable
        #Plot ranking
        fig5 = go.Figure(data=[go.Table(
        header=dict(values=list(top_10),
                    fill_color='black',
                    font = dict(color = 'white', size = 20),
                    align='center'),
        cells=dict(values=[top_10.Ranking,top_10.user_id,top_10.hours],
                    fill_color='#262730',
                    font = dict(color = 'white', size = 15),
                align='center'))
        ])
        st.plotly_chart(fig5)
    
    #c2 column corresponds to the manager's productivity based on hours logged by employees whom they manage
    with c2:
        st.header('Manager productivity')
        mgr_group = df.groupby('manager_id')['hours'].sum().reset_index()#group managers and get hours logged by their staff
        mgr_rankings= mgr_group.sort_values(by='hours',ascending=False)#sort values in descending order to display top managers
        mgr_rankings.insert(0,'Ranking',range(1,1+len(mgr_rankings))) #insert Rank column on leftmost column
        mgr_rankings.reset_index(drop=True,inplace=True) 
        #Create bar plot of managers
        fig6 = px.bar(mgr_rankings,x='manager_id',y='hours',
        labels=dict(hours='Hours logged by staff of a manager',manager_id='Manager ID'))
        fig6.update_layout(
            xaxis=dict(tickmode='linear',tick0=1,dtick=1)
        )
        st.plotly_chart(fig6)

    #Average,max, and min Annual Check-in for all employees
    d1,d2,d3 = st.columns(3)
    ave_annual_hours = int(np.mean(hour_group['hours'])) #Gets the average hours logged by employees for an entire year
    max_annual_hours = int(np.max(hour_group['hours'])) #Gets the least hours logged by an employee
    min_annual_hours = int(np.min(hour_group['hours'])) #Gets the most hours logged by an employee
    #create 3 columns with corresponding metric (d1:min hours, d2:average hours, d3: max hours)
    with d1:
        st.metric(label='Employee with least hours contribtued',value='user_id: 1',delta=-(min_annual_hours))
    with d2:
        st.metric(label='Average employee hours contributed',value=(ave_annual_hours))
    with d3:
        st.metric(label='Employee with most hours contributed',value='user_id: 50',delta=(max_annual_hours))

#This section corresponds to the Project insights, an in-depth examination of data with a focus on projects
with st.expander("Project insights"):
    st.header('Project insights and relationships')
    d1,d2 = st.columns((2,2))
    #We display histograms of project_id vs. check-ins (count) and project_id vs. total hours logged by employees
    with d1:
        proj = df.groupby(['project_id']).agg(count=('project_id','count'),hours=('hours','sum')) #we aggregate the dataframes...see Raw Dataset
        proj.insert(0,'project_id',range(1,1+len(proj))) #insert the Rank column on leftmost column

        fig7 = px.histogram(df,x='project_id',labels={'project_id':"Project ID",'y':"Check-in count"})
        st.plotly_chart(fig7)
        fig8 = px.histogram(proj,x='project_id',y='hours',nbins=len(proj),
        labels={'project_id':'Project ID','hours':'hours dedicated to project'})
        st.plotly_chart(fig8)

    with d2:
        st.metric(label='Total project count',value=len(proj)) #Total Number of projects
       
        st.metric(label="Project ID with least hours dedicated to: ", value=proj['hours'].idxmin(),delta=proj['hours'].min(),delta_color='inverse')#project ID least worked on
        st.metric(label="Average hours dedicated per project: ", value="%.2f" %proj['hours'].mean()) #Average hours allotted per project
        st.metric(label="Project ID with most hours dedicated to: ", value=proj['hours'].idxmax(),delta=proj['hours'].max()) #max hours logged for a project ID
       
        st.metric(label="Project ID with least check-ins: ", value=proj['count'].idxmin(),delta=proj['count'].min(),delta_color='inverse') #project id w/ least check-ins
        st.metric(label="Average check-ins per project: ", value=int(proj['count'].mean())) #average check-ins per project id
        st.metric(label="Project ID with most check-ins: ", value=proj['count'].idxmax(),delta=proj['count'].max()) #project id w/ most check-ins

#This section corresponds to the raw dataset
with st.expander("Raw dataset (for DevOps and researchers)"):
    e1,e2 = st.columns((3,2))
    #We display the raw data so that other teams (e.g. DevOps, Data Scientists and ML researchers) can work with it
    with e1:
        st.header("Raw DataFrame")
        st.dataframe(df.iloc[:,0:5])
    with e2:
        st.header("Aggregated projects DataFrame")
        st.dataframe(proj)