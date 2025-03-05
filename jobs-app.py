from plot_helpers import *
import requests
import streamlit as st
import pandas as pd
st.set_page_config(layout="wide")
from stoc import stoc
from datetime import datetime

toc = stoc()
API_BASE_URL = "https://api.careerinsights.me"

@st.cache_data
def get_summary_stats_data():
    r = requests.get(f"{API_BASE_URL}/summary_stats")
    r.raise_for_status()
    data = r.json()  # should be a list of records
    return pd.DataFrame(data)

@st.cache_data
def get_salary_stats_data(by="median", smoothing_window=3, keep_predicted_jobs = True):
    """
    calls the fastapi endpoint /salary_stats
    returns a dataframe
    """
    params = {
        "by": by,
        "smoothing_window": smoothing_window,
        "keep_predicted_jobs": keep_predicted_jobs
    }
    r = requests.get(f"{API_BASE_URL}/salary_stats", params=params)
    r.raise_for_status()
    data = r.json()  # should be a list of records
    return pd.DataFrame(data)

@st.cache_data
def get_seniority_stats_data(smoothing_window=3, keep_predicted_jobs = True):
    """
    calls the fastapi endpoint /seniority_stats
    returns a dataframe
    """
    params = {"smoothing_window": smoothing_window,
               "keep_predicted_jobs": keep_predicted_jobs
               }
    r = requests.get(f"{API_BASE_URL}/seniority_stats", params=params)
    r.raise_for_status()
    data = r.json()
    return pd.DataFrame(data)

@st.cache_data
def get_skill_proportions_data(job_category=None, threshold=10, seniority=None):
    params = {"threshold": threshold,        
             "seniority": seniority
             }
    if job_category:
        job_category = job_category.lower().replace(' ', '_')
    r = requests.get(f"{API_BASE_URL}/skill_proportions/{job_category}", params=params)
    r.raise_for_status()
    data = r.json()
    if isinstance(data, dict) and "results" in data:
        data = data["results"]
    return pd.DataFrame(data)

@st.cache_data
def get_skill_frequencies_data(job_category=None, proportion_threshold=0.01, min_edge_frequency=20, seniority=None):
    params = {
        "proportion_threshold": proportion_threshold,
        "seniority": seniority
        # "min_edge_frequency": min_edge_frequency
    }
    if job_category:
        job_category = job_category.lower().replace(' ', '_')
    r = requests.get(f"{API_BASE_URL}/skill_frequencies/{job_category}", params=params)
    r.raise_for_status()
    data = r.json()
    if isinstance(data, dict) and "results" in data:
        data = data["results"]
    return data

def display_top_metrics(summary_df):
    stats_to_show = st.selectbox(
        "Select a Region:", 
        ["Overall", "Canada", "United States"],
        index=0
    )

    col1, col2, col3 = st.columns([3, 3, 3])

    with col1:
        if stats_to_show == "Overall":
            df_filtered = summary_df[summary_df['country'] == 'overall']
        elif stats_to_show == "Canada":
            df_filtered = summary_df[summary_df['country'] == 'canada']
        elif stats_to_show == "United States":
            df_filtered = summary_df[summary_df['country'] == 'us']

        df_filtered['job_category'] = df_filtered['job_category'].apply(lambda x: x.replace("_", " ").title())
        df_filtered['job_category'] = df_filtered['job_category'].str.replace('Machine Learning', 'ML')

        total_jobs = df_filtered['counts'].sum()

        df_filtered = df_filtered.sort_values("counts", ascending=False)

        top_categories = df_filtered.head(10)

        if len(top_categories) == 0:
            st.warning("No data for this region.")
            return

        top_category = top_categories.iloc[0]
        st.metric(label="Total Jobs", value=f"{total_jobs:,}")

    with col2:
        st.metric(label=f"Largest Category (n = {top_category['counts']:,})", value=f"{top_category['job_category']}")

    with col3:
        median_salary = top_category['median_mid_salary']
        mid_level_count = top_category.get('mid_level_count', 0)
        salary_text = f"${median_salary:,.0f}"
        st.metric(label=f"Median Salary (USD; last 3 months, n = {mid_level_count:,})", value=salary_text)

    # display additional categories
    for i in range(1, len(top_categories)):
        cat = top_categories.iloc[i]
        col1, col2, col3 = st.columns([3, 3, 3])

        with col2:
            suffix = "th"
            if i == 1:
                suffix = "nd"
            if i == 2: 
                suffix = "rd"
            st.metric(label=f"{i+1}{suffix} Largest Category (n = {cat['counts']:,})", value=f"{cat['job_category']}")

        with col3:
            median_salary = cat['median_mid_salary']
            mid_level_count = cat.get('mid_level_count', 0)
            salary_text = f"${median_salary:,.0f}"
            st.metric(label=f"Median Mid-Level Salary (USD; last 3 months, n = {mid_level_count:,})", value=salary_text)

st.sidebar.title("Menu")
st.sidebar.caption("""
                   These options are only for the **skills heatmap** and **network analysis**. 
                   """)

st.title("North American Tech Career Insights")

st.markdown("""
                                    
This dashboard is served by an end-to-end ETL data pipeline orchestrated by Dagster that is updated nightly. It is designed to scrape, load, and transform job postings for analysis. About ~6000 jobs are collected each week, although only roughly half are relevant to software. 
For more information on the architecture of the pipeline, please scroll to the bottom or use the table of contents on the left.
            
""")

# placeholder
job_titles = ['Machine Learning Engineer', 'Software Engineer', 'Data Engineer', 'Data Scientist', 'Data Analyst']
seniorities = ['Intern', "Entry Level", "Mid-Level", "Senior-Level"]

selected_job_category = st.sidebar.selectbox(
    "Select a pre-defined job title",
    job_titles,
    index=2
)

selected_seniority = st.sidebar.selectbox(
    "Select a seniority level",
    seniorities,
    index=2
)

# available_countries = ['us', 'canada']
# selected_countries = st.sidebar.multiselect("Countries", available_countries,  default=['us', 'canada'])

# if filter_job_categories:
#     jobs = jobs[jobs['source'] == 'regex']
# filter_job_salaries = st.sidebar.toggle("Exclude Jobs without Salaries")

toc.h2("Statistics")

st.markdown("Counts for each job title is across all seniorities whereas the median salary is for ONLY mid-entry jobs.")

summary_df = get_summary_stats_data()

display_top_metrics(summary_df)

toc.h2("Market Overview")
st.markdown("""
   This section is intended to give a broad overview of the market in terms of the distribution of aggregated job categories by seniority, as well as any trends in salary over time.      
   **None of the settings on the left affect this section other than excluding jobs with predicted titles.** 
""")

# filter_job_categories = st.toggle("Exclude Predicted Job Titles (applies to both seniority and salary analyses)")
filter_job_categories = False

toc.h3("Seniority Over Time")
st.markdown("""
            The figure below depicts the the breakdown of seniority, for each job category between the US and Canada. The idea is to see the demand of particular seniority levels between jobs, and between countries.
            """)

proportion_df = get_seniority_stats_data( smoothing_window=3, keep_predicted_jobs=filter_job_categories)
proportion_plot = create_seniority_plot(proportion_df)
st.plotly_chart(proportion_plot, use_container_width=False)

toc.h3("Salary (USD) Over Time")

st.markdown("""
            These fields, specifically salary and seniority are parsed by a mix of OpenAI's API and regular expression. 
            Job category is done primarily using regex with some machine learning as indicated in the methods above. Data presented is a rolling median (k = 3), of medians.
            """)

filtered_jobs = get_salary_stats_data(by="median", smoothing_window=3, keep_predicted_jobs=filter_job_categories)
fig = create_salary_plot(filtered_jobs)
st.plotly_chart(fig, use_container_width=False)


# available_seniority = list(jobs['binned_seniority'].cat.categories) # be careful this is a pd.Categorical object
# select_all_seniority = st.sidebar.checkbox("Select All Seniority Levels")

# if select_all_seniority:
#     selected_seniority = st.sidebar.multiselect("Seniority", available_seniority, default=available_seniority)
# else:
#     selected_seniority = st.sidebar.multiselect("Seniority", available_seniority,  default=['Intern', 'Entry Level', 'Senior-Level', 'Mid-Level'])


toc.h2("Trends in Technologies")

st.markdown(
"""
    This analysis identifies trends in skill demand across various job categories, countries, and seniority levels (the latter two TBD). 
    By normalizing skill occurrences as a percentage of total job postings per month, the heatmap highlights the most sought-after skills and their fluctuations over time
""")
with st.container():
    col1, col2 = st.columns([0.2, 1])

    df_skill_props = get_skill_proportions_data(
            job_category=selected_job_category, 
            seniority = selected_seniority,
            threshold=10
    )

    # with col1:
        # threshold = st.slider("Skill Threshold (WIP)", 1, 50, 10)
    # with col2: 

    # don't need if using the csv
    df_pivot = df_skill_props.pivot_table(
        index=['year_month', 'job_category'],  # row identifiers
        columns='skill',                       # each unique skill becomes a column
        values='proportion',                   # values for cells 
        fill_value=0                          
    ).reset_index()

    df_pivot = df_pivot.merge(
        df_skill_props[['year_month', 'job_category', 'total_jobs']].drop_duplicates(),
        on=['year_month', 'job_category'],
        how='left'
    )

    fig_heatmap = create_skill_heatmap(df_pivot, height=700, width=800)
    st.plotly_chart(fig_heatmap, use_container_width=True)

toc.h2("Network Analysis of Co-occuring skills")

st.markdown("""
            This analysis explores how different skills commonly appear together in job postings. By examining these combinations, we can uncover patterns of which skills are frequently required together for specific roles. 
            This insight can help job seekers understand which skills are valuable to learn together and provide a clearer picture of industry demands.

            Edges between two nodes are only kept if two skills co-occur in at least 1% of jobs.
            """)

with st.container():
    col3, col4 = st.columns([1, 0.4])

    with col4:
        edge_scaling_factor = st.slider('Edge Scaling Factor', min_value=1.0, max_value=10.0, value=5.0, step=0.5)
        st.markdown('Data used is since 2024-06-01.')
        # st.markdown('Defaults to year to date.')
        current_date = datetime.today()
        formatted_date_str = current_date.strftime('%Y-%m')
        formatted_date = datetime.strptime(formatted_date_str, '%Y-%m').date()

        default_start_date = datetime.strptime('2024-01-01', '%Y-%m-%d').date()
        default_end_date = formatted_date
        start_date = default_start_date
        end_date = default_end_date
        # start_date = st.date_input('Start date', value=default_start_date, min_value=datetime(2020, 1, 1).date())
        # end_date = st.date_input('End date', value=default_end_date, max_value=formatted_date)
    with col3:

        with st.container():
            # prop_thresh = st.slider("proportion threshold", 0.0, 0.1, 0.01, step=0.01)
            
            skill_freq_data = get_skill_frequencies_data(
                job_category=selected_job_category, 
                seniority = selected_seniority,
                proportion_threshold=0.01, 
                # min_edge_frequency=min_edge
            )

            fig = create_network_graph(
                selected_job_category, skill_freq_data, layout_algo="Kamada-Kawai Layout", k=0,
                edge_scaling_factor=edge_scaling_factor, dates_for_title=f"{start_date} to {end_date}"
            )

            st.plotly_chart(fig, use_container_width=True)

st.markdown(
""" 
Interpreting the Network Graph

1.	Connections (node degree, represented by the node size):
    * The degree of a node represents the number of edges (connections) that the node has. As a node represents a skill, its degree represents how many skills it frequently co-occurs with across the job postings.
    * A higher degree indicates that a skill is commonly found with a larger variety of other skills and is more likely to be a fundamental or widely applicable skill that employers look for across different roles.

2.	Edge Weight:
    * The edge weight represents the frequency of co-occurrence between two skills. An edge between two nodes (skills) represents how often those two skills appear together in the job postings.
    * A higher edge weight indicates that two skills are strongly associated with each other. For instance, if Python and SQL frequently appear together, the edge between them will have a higher weight, suggesting that roles requiring Python often also require SQL.
""")


st.markdown("""
TODO:
- add country filters to skill frequencies and proportions
- add date filter to skill frequencies
- facilitate analyses by user input title
            """)


toc.h2("About the Pipeline")
st.image("./featured.png")

st.markdown("""
            
The pipeline, which is containerized and hosted on an Oracle Cloud Infrastructure (OCI) vm,  works as follows:
<p>    
<details>
<summary>Click this to collapse/fold.</summary>

1. Multiple job boards are scraped using different job queries and locations as search parameters.
2. Job postings are categorized into one of 7 categories using regex patterns. 
3. Deduplication is done by comparing:
    - Exact id 
    - Exact job description using a hash
    - Near-deduplication, which accounts for the same job posting posted on different sites or re-posted with slight format changes using the SimHash algorithm and a fingerprint index which compares job descriptions textual similarity by fragmenting and hashing them. This step relies on an index that's saved to disk and tightly coupled to insertion into the database. 
4. Jobs are inserted into a table into the database.
    - 'Unknown' job categories are passed through a fine-tuned DistilBERT model to classify them into one of 6 categories using their job descriptions. The model was fine tuned on 55 336 job postings with an average F1 score of 0.87.  Inference is able to assign a relevant job title to 34% of previously unknown job postings, equating to 9 670 out of 24136 entries as of October 15th, 2024. Of the final dataset, about 10% are from inference.
    - All job postings except for those that were categorized as 'Irrelevant', are then sent to the OpenAI Batch API (vs. the synchronous API, saving on 50% of the costs) for parsing attributes such as salary, job type, seniority level, etc using Function Calls. Results are then awaited by batch, cleaned, and inserted in the database. 
5. After inference is complete, a dbt model is run to extract skills from relevant job titles from a) the raw postings table and b) the inference table. 
6. Lastly, a final dbt model is run to combine the scraped job attributes, the extracted skills, and the OpenAI parsed attributes into a single table, and
            - The table is retrieved and uploaded to AWS S3 for further analytics.
            - Multiple views are made and accessible through FastAPI-based API, which serves the Streamlit dashboard. 
</details>
</p>

            
""", unsafe_allow_html=True)

toc.toc()