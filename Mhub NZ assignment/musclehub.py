
# coding: utf-8

# # Capstone Project 1: MuscleHub AB Test

# ## Step 1: Get started with SQL

# Like most businesses, Janet keeps her data in a SQL database.  Normally, you'd download the data from her database to a csv file, and then load it into a Jupyter Notebook using Pandas.
# 
# For this project, you'll have to access SQL in a slightly different way.  You'll be using a special Codecademy library that lets you type SQL queries directly into this Jupyter notebook.  You'll have pass each SQL query as an argument to a function called `sql_query`.  Each query will return a Pandas DataFrame.  Here's an example:

# In[1]:


# This import only needs to happen once, at the beginning of the notebook
from codecademySQL import sql_query


# In[2]:


# Here's an example of a query that just displays some data
sql_query('''
SELECT *
FROM visits
LIMIT 5
''')


# In[3]:


# Here's an example where we save the data to a DataFrame
df = sql_query('''
SELECT *
FROM applications
LIMIT 5
''')


# ## Step 2: Get your dataset

# Let's get started!
# 
# Janet of MuscleHub has a SQLite database, which contains several tables that will be helpful to you in this investigation:
# - `visits` contains information about potential gym customers who have visited MuscleHub
# - `fitness_tests` contains information about potential customers in "Group A", who were given a fitness test
# - `applications` contains information about any potential customers (both "Group A" and "Group B") who filled out an application.  Not everyone in `visits` will have filled out an application.
# - `purchases` contains information about customers who purchased a membership to MuscleHub.
# 
# Use the space below to examine each table.

# In[4]:


# Examine visits here
visits = sql_query('''
SELECT * FROM visits;
''')
visits.info()


# In[5]:


# Examine fitness_tests here
fitness_tests = sql_query('''
SELECT * FROM fitness_tests;
''')
fitness_tests.info()


# In[6]:


# Examine applications here
applications = sql_query('''
SELECT * FROM applications
LIMIT 10;
''')
applications


# In[7]:


# Examine purchases here
purchases = sql_query('''
SELECT * FROM purchases
LIMIT 10;
''')
purchases


# We'd like to download a giant DataFrame containing all of this data.  You'll need to write a query that does the following things:
# 
# 1. Not all visits in  `visits` occurred during the A/B test.  You'll only want to pull data where `visit_date` is on or after `7-1-17`.
# 
# 2. You'll want to perform a series of `LEFT JOIN` commands to combine the four tables that we care about.  You'll need to perform the joins on `first_name`, `last_name`, and `email`.  Pull the following columns:
# 
# 
# - `visits.first_name`
# - `visits.last_name`
# - `visits.gender`
# - `visits.email`
# - `visits.visit_date`
# - `fitness_tests.fitness_test_date`
# - `applications.application_date`
# - `purchases.purchase_date`
# 
# Save the result of this query to a variable called `df`.
# 
# Hint: your result should have 5004 rows.  Does it?

# In[190]:


visits_intest = sql_query('''
SELECT DISTINCT first_name FROM visits
WHERE visit_date >= "7-1-17";
''')
visits_intest.info()


# In[194]:


df = sql_query('''
SELECT visits.first_name, visits.last_name, visits.email, visits.gender, visits.visit_date,
fitness_tests.fitness_test_date, applications.application_date, purchases.purchase_date
FROM visits
LEFT JOIN fitness_tests ON
visits.first_name = fitness_tests.first_name AND 
visits.last_name = fitness_tests.last_name AND 
visits.email = fitness_tests.email
LEFT JOIN applications ON
visits.first_name = applications.first_name AND 
visits.last_name = applications.last_name AND 
visits.email = applications.email
LEFT JOIN purchases ON
visits.first_name = purchases.first_name AND 
visits.last_name = purchases.last_name AND 
visits.email = purchases.email
WHERE visit_date >= "7-1-17"
ORDER BY visit_date DESC;
''')
df.head()


# Calculating the number of days needed to collect 5004 visitors. 

# In[195]:


from datetime import date
d0 = date(2017, 7, 1)
d1 = date(2017, 9, 9)
delta = d1 - d0
delta.days


# ## Step 3: Investigate the A and B groups

# We have some data to work with! Import the following modules so that we can start doing analysis:
# - `import pandas as pd`
# - `from matplotlib import pyplot as plt`

# In[10]:


import pandas as pd
get_ipython().run_line_magic('matplotlib', 'inline')
from matplotlib import pyplot as plt


# We're going to add some columns to `df` to help us with our analysis.
# 
# Start by adding a column called `ab_test_group`.  It should be `A` if `fitness_test_date` is not `None`, and `B` if `fitness_test_date` is `None`.

# In[11]:


df["ab_test_group"] = df.apply(lambda visit: 'B' if visit["fitness_test_date"] is None else 'A', axis=1)
df.head(10)


# Let's do a quick sanity check that Janet split her visitors such that about half are in A and half are in B.
# 
# Start by using `groupby` to count how many users are in each `ab_test_group`.  Save the results to `ab_counts`.

# In[12]:


ab_counts = df.groupby(["ab_test_group"])["first_name"].count()
ab_counts


# We'll want to include this information in our presentation.  Let's create a pie cart using `plt.pie`.  Make sure to include:
# - Use `plt.axis('equal')` so that your pie chart looks nice
# - Add a legend labeling `A` and `B`
# - Use `autopct` to label the percentage of each group
# - Save your figure as `ab_test_pie_chart.png`

# In[188]:


labels = 'Fitness test', 'No fitness test'
sizes = [2504, 2500]

fig = plt.figure(figsize=(20,20))
fig1, ax1 = plt.subplots()

ax1.pie(ab_counts, labels=labels, autopct='%1f%%')
ax1.axis('equal')
plt.savefig('Musclehub_test_samples.png')
plt.show()


# ## Step 4: Who picks up an application?

# Recall that the sign-up process for MuscleHub has several steps:
# 1. Take a fitness test with a personal trainer (only Group A)
# 2. Fill out an application for the gym
# 3. Send in their payment for their first month's membership
# 
# Let's examine how many people make it to Step 2, filling out an application.
# 
# Start by creating a new column in `df` called `is_application` which is `Application` if `application_date` is not `None` and `No Application`, otherwise.

# In[15]:


df["is_application"] = df.apply(lambda visit: "No Application" if visit["application_date"] is None else "Application", axis=1)
df.head(20)


# Now, using `groupby`, count how many people from Group A and Group B either do or don't pick up an application.  You'll want to group by `ab_test_group` and `is_application`.  Save this new DataFrame as `app_counts`

# In[91]:


app_counts = df.groupby(['ab_test_group','is_application'])['first_name'].count().reset_index()
app_counts


# We're going to want to calculate the percent of people in each group who complete an application.  It's going to be much easier to do this if we pivot `app_counts` such that:
# - The `index` is `ab_test_group`
# - The `columns` are `is_application`
# Perform this pivot and save it to the variable `app_pivot`.  Remember to call `reset_index()` at the end of the pivot!

# In[92]:


app_pivot = app_counts.pivot(index='ab_test_group', columns='is_application', values='first_name')
app_pivot


# Define a new column called `Total`, which is the sum of `Application` and `No Application`.

# In[93]:


app_pivot["Total"] = app_pivot.apply(lambda row: row['Application'] + row['No Application'], axis=1)
app_pivot


# Calculate another column called `Percent with Application`, which is equal to `Application` divided by `Total`.

# In[96]:


app_pivot['Percent with Application'] = app_pivot.apply(lambda app: 100. * app['Application'] / app['Total'], axis=1)
app_pivot


# It looks like more people from Group B turned in an application.  Why might that be?
# 
# We need to know if this difference is statistically significant.
# 
# Choose a hypothesis tests, import it from `scipy` and perform it.  Be sure to note the p-value.
# Is this result significant?

# Our hypothesis is that the fitness test negatively affects the likelyhood of a visitor 
# applying at Musclehub. We want to test this hypothesis with a binomial test, since the variable is dichotomus (application / no application). 

# In[98]:


from scipy.stats import binom_test


# In[120]:


pval = binom_test(325, n=2500, p=0.09984026)
pval


# The p-value is well below 0.05. The null hypothesis can be safely rejected and we can assert that the difference between the two samples is significant. 

# ## Step 4: Who purchases a membership?

# Of those who picked up an application, how many purchased a membership?
# 
# Let's begin by adding a column to `df` called `is_member` which is `Member` if `purchase_date` is not `None`, and `Not Member` otherwise.

# In[100]:


df['is_member'] = df.apply(lambda visit: 'Not Member' if visit['purchase_date'] is None else 'Member', axis=1)
df.head()


# Now, let's create a DataFrame called `just_apps` the contains only people who picked up an application.

# In[106]:


just_apps = df[df.is_application.isin(['Application'])]
just_apps.head()


# Great! Now, let's do a `groupby` to find out how many people in `just_apps` are and aren't members from each group.  Follow the same process that we did in Step 4, including pivoting the data.  You should end up with a DataFrame that looks like this:
# 
# |is_member|ab_test_group|Member|Not Member|Total|Percent Purchase|
# |-|-|-|-|-|-|
# |0|A|?|?|?|?|
# |1|B|?|?|?|?|
# 
# Save your final DataFrame as `member_pivot`.

# In[110]:


member = just_apps.groupby(['is_member', 'ab_test_group'])['first_name'].count().reset_index()
member


# In[113]:


member_pivot = member.pivot(index='ab_test_group', columns='is_member', values='first_name').reset_index()
member_pivot


# In[140]:


member_pivot['Total'] = member_pivot.apply(lambda app: app['Member'] + app['Not Member'], axis=1)
member_pivot['Percent Purchase'] = member_pivot.apply(lambda percent: 100.0 * (percent['Member'] / percent['Total']), axis=1)
member_pivot


# It looks like people who took the fitness test were more likely to purchase a membership **if** they picked up an application.  Why might that be?
# 
# Just like before, we need to know if this difference is statistically significant.  Choose a hypothesis tests, import it from `scipy` and perform it.  Be sure to note the p-value.
# Is this result significant?

# In[121]:


pval2 = binom_test(250, n=325, p=0.8)
pval2


# The p-value is over 0.05, we cannot reject the null hypothesis. The difference between group A and B in purchasing a membership following their application is not significant enough to draw any conclusion, at least not with this sample.

# Previously, we looked at what percent of people **who picked up applications** purchased memberships.  What we really care about is what percentage of **all visitors** purchased memberships.  Return to `df` and do a `groupby` to find out how many people in `df` are and aren't members from each group.  Follow the same process that we did in Step 4, including pivoting the data.  You should end up with a DataFrame that looks like this:
# 
# |is_member|ab_test_group|Member|Not Member|Total|Percent Purchase|
# |-|-|-|-|-|-|
# |0|A|?|?|?|?|
# |1|B|?|?|?|?|
# 
# Save your final DataFrame as `final_member_pivot`.

# In[122]:


all_visits = df.groupby(['ab_test_group', 'is_member'])['first_name'].count().reset_index()
all_visits


# In[123]:


final_member_pivot = all_visits.pivot(index='ab_test_group', columns='is_member', values='first_name').reset_index()
final_member_pivot


# In[125]:


final_member_pivot['Total'] = final_member_pivot.apply(lambda visit: visit['Member'] + visit['Not Member'], axis=1)
final_member_pivot['Percent Purchase'] = final_member_pivot.apply(lambda visit: 100.0 * (visit['Member'] / visit['Total']), axis=1)
final_member_pivot


# Previously, when we only considered people who had **already picked up an application**, we saw that there was no significant difference in membership between Group A and Group B.
# 
# Now, when we consider all people who **visit MuscleHub**, we see that there might be a significant different in memberships between Group A and Group B.  Perform a significance test and check.

# In[196]:


lift_members = 100 * (10 - 7.98722) / 7.98722
lift_members


# In[128]:


pval3 = binom_test(250, n=2500, p=0.0798722)
pval3


# The p-value of this test is below 0.05, we can reject the null hypothesis and conclude that Musclhub will consistantly increase the likelihood of visitors becoming members if they avoid the fitness test. 

# ## Step 5: Summarize the acquisition funel with a chart

# We'd like to make a bar chart for Janet that shows the difference between Group A (people who were given the fitness test) and Group B (people who were not given the fitness test) at each state of the process:
# - Percent of visitors who apply
# - Percent of applicants who purchase a membership
# - Percent of visitors who purchase a membership
# 
# Create one plot for **each** of the three sets of percentages that you calculated in `app_pivot`, `member_pivot` and `final_member_pivot`.  Each plot should:
# - Label the two bars as `Fitness Test` and `No Fitness Test`
# - Make sure that the y-axis ticks are expressed as percents (i.e., `5%`)
# - Have a title

# I found a better way to illustrate our findings: a superimposed bar chart with Visitors, Applicants and Members all represented on a bar chart relative to the number of visits in each group, represented in percentage. 
# 
# I estimated that representing the rate of membership from applicants didn't deserve its own plot since the difference between group A and B were found to be insignificant. However this chart still represents all important dimensions (visits, applications, memberships). 

# In[186]:


from matplotlib.ticker import FuncFormatter

fig = plt.figure(figsize=(5,7))

groups = ['Fitness Test', 'No Fitness Test']
pct_app = app_pivot['Percent with Application']
pct_app_member = member_pivot['Percent Purchase']
pct_all_member = final_member_pivot['Percent Purchase']

def tickpct(x, pos=0):
    return '%1d%%' %(x)
    
plt.bar(range(len(groups)), [100, 100], label='Visitors')
plt.bar(range(len(groups)), pct_app, label='Applications in %')
plt.bar(range(len(groups)), pct_all_member, label='Memberships in %')

plt.title('Membership Rate of Visitors with and without Fitness Test')

ax1 = plt.subplot()

ax1.set_xticks(range(len(group)))
ax1.set_xticklabels(group)
ax1.yaxis.set_major_formatter(FuncFormatter(tickpct))

plt.ylim(0,30)
plt.legend()
plt.savefig('Musclehub_bar_chart.png')
plt.show()

