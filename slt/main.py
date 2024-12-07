import json
import os
import streamlit as st
import requests
import pandas as pd
from io import StringIO
from matplotlib import pyplot as plt
import seaborn as sns

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")


def fetch_info():
    try:
        response = requests.get(BASE_URL + '/data_info')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from the API: {e}")
        return None


def fetch_head(table_name: str, page: int = 0, page_size: int = 10):
    try:
        response = requests.get(BASE_URL + '/head',
                                params={'table_name': table_name, 'page': page, 'page_size': page_size})
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from the API: {e}")
        return None


@st.cache_data
def fetch_theory():
    try:
        response = requests.get(BASE_URL + '/theory')
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from the API: {e}")
        return None


@st.cache_data
def fetch_analysis():
    try:
        response = requests.get(BASE_URL + '/preview_message')
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from the API: {e}")
        return None


@st.cache_data
def download_parties_data():
    st.text('downloading...')
    data_folder = "./data"
    os.makedirs(data_folder, exist_ok=True)

    file_url = BASE_URL + '/data.csv'
    try:
        response = requests.get(file_url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        chunk_size = 8192

        progress_bar = st.progress(0)
        status_text = st.empty()

        with open(data_folder + "/data.csv", "wb") as file:
            bytes_downloaded = 0
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    file.write(chunk)
                    bytes_downloaded += len(chunk)

                    progress = bytes_downloaded / total_size
                    progress_bar.progress(min(progress, 1.0))

                    status_text.text(f"progress: {bytes_downloaded / (1024 * 1024):.2f} MB of "
                                     f"{total_size / (1024 * 1024):.2f} MB")

        progress_bar.empty()
        df = pd.read_csv(data_folder + "/data.csv")
        return df
    except requests.exceptions.RequestException as e:
        st.error(f"Error downloading the file: {e}")


@st.cache_data
def download_traumas_data():
    st.text('downloading...')
    data_folder = "./data"
    os.makedirs(data_folder, exist_ok=True)

    file_url = BASE_URL + '/traumas.csv'
    try:
        response = requests.get(file_url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        chunk_size = 8192

        progress_bar = st.progress(0)
        status_text = st.empty()

        with open(data_folder + "/traumas.csv", "wb") as file:
            bytes_downloaded = 0
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    file.write(chunk)
                    bytes_downloaded += len(chunk)

                    progress = bytes_downloaded / total_size
                    progress_bar.progress(min(progress, 1.0))

                    status_text.text(f"progress: {bytes_downloaded / (1024 * 1024):.2f} MB of "
                                     f"{total_size / (1024 * 1024):.2f} MB")

        progress_bar.empty()
        df = pd.read_csv(data_folder + "/traumas.csv")
        return df
    except requests.exceptions.RequestException as e:
        st.error(f"Error downloading the file: {e}")


if 'pagination' not in st.session_state:
    st.session_state.pagination = {}


def display_table_info(data):
    if data:
        for table in data:
            table_name = table['table_name']
            st.subheader(table_name)
            st.write(table['description'])

            if table_name not in st.session_state.pagination:
                st.session_state.pagination[table_name] = {'page': 0, 'page_size': 10}

            page = st.session_state.pagination[table_name]['page']
            page_size = st.session_state.pagination[table_name]['page_size']

            head = fetch_head(table_name, page, page_size)
            if head:
                df = pd.read_csv(StringIO(head))
                st.dataframe(df)

                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"Previous ({table_name})", key=f"prev_{table_name}"):
                        if page > 0:
                            st.session_state.pagination[table_name]['page'] -= 1

                with col2:
                    st.text(f"Page: {page + 1}")

                with col3:
                    if st.button(f"Next ({table_name})", key=f"next_{table_name}"):
                        st.session_state.pagination[table_name]['page'] += 1

                new_page_size = st.number_input(
                    f"Rows per page ({table_name})",
                    min_value=1,
                    max_value=100,
                    value=page_size,
                    key=f"page_size_{table_name}"
                )
                if new_page_size != page_size:
                    st.session_state.pagination[table_name]['page_size'] = new_page_size
                    st.session_state.pagination[table_name]['page'] = 0
            st.write("---")
    else:
        st.write("No data available.")


st.title("Table Information")

table_info = fetch_info()
display_table_info(table_info)

st.title('My Theory')
st.write(fetch_theory())

st.title('The Analysis')
st.markdown(
    '''Lets analyze `parties` table.  
This table has a lot of numeric fields. The most essential fields are `vehicle_year`,`party_type`, `at_fault`, `party_sex`, `party_age`, `party_sobriety` (can be a numeric field), `party_number_killed` (injured), `party_race`.  
`vehicle_year` says what year the vehicle is.  
`party_age` says the age of a victim.  
`party_sex` and `party_race` says about the person in general.  '''
)

st.title('Download Vehicle Data')
data = download_parties_data()

cars_df = data

st.dataframe(cars_df[['case_id', 'vehicle_year']].head())


@st.cache_resource
def create_box_plot_year():
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(data=cars_df['vehicle_year'])
    ax.set_title("Vehicle Year Distribution")
    ax.set_ylim(1900, 2025)
    ax.set_xlabel("Vehicle Year")
    ax.set_ylabel("Frequency")

    st.pyplot(fig)


create_box_plot_year()

st.text(
    "as we can see, there are a lot of outliers and most of them are below 1980 year. => we can take all vehicles from 1980 to 2022 (since database is from 2022)")

cars_df = cars_df[
    (cars_df['vehicle_year'].notna()) &
    (cars_df['vehicle_year'] >= 1980) &
    (cars_df['vehicle_year'] <= 2022)
    ]

car_counts = cars_df['vehicle_year'].value_counts().sort_index()


@st.cache_resource
def create_bar_plot_cars():
    fig, ax = plt.subplots(figsize=(14, 6))
    sns.barplot(x=car_counts.index, y=car_counts.values, color='skyblue', ax=ax)
    ax.set_title('Number of Cars by Manufacture Year Involved in Accidents')
    ax.set_xlabel('Car Manufacture Year')
    ax.set_ylabel('Number of Incidents')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)  # Rotate x-axis labels
    st.pyplot(fig)


create_bar_plot_cars()

st.text(f"Median Year: {cars_df['vehicle_year'].median()}")
st.text(f"Mean Year: {int(cars_df['vehicle_year'].mean())}")
st.text(f"Standard Deviation: {cars_df['vehicle_year'].std():.2f}")

st.markdown("#### as we can see, vehicles made in 2000 collide the most")
st.markdown("#### that's probably because there are more cars of that year, then any other")

peoples_age_df = data


@st.cache_resource
def create_people_age_distribution():
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(data=peoples_age_df['party_age'])
    ax.set_title("People Age Distribution")
    ax.set_ylabel("Age")
    st.pyplot(fig)


create_people_age_distribution()

st.text(
    "obviously, we should not take into account people younger than 12 and older than 90, since they do not really drive.")
st.text("we can also see that in data there are a lot of outliers that we need to get rid of. ")


def clean_peoples_age():
    global peoples_age_df
    peoples_age_df = peoples_age_df[
        (peoples_age_df['party_age'].notna()) &
        (peoples_age_df['party_age'] >= 12) &
        (peoples_age_df['party_age'] <= 90)
        ]


peoples_age_counts = peoples_age_df['party_age'].value_counts().sort_index()


@st.cache_resource
def create_bar_plot_people():
    fig, ax = plt.subplots(figsize=(24, 6))
    sns.barplot(x=peoples_age_counts.index, y=peoples_age_counts.values, color='skyblue')
    ax.set_title('Peoples Age Distribution')
    ax.set_xlabel('Age')
    ax.set_ylabel('Number of Incidents')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    st.pyplot(fig)


st.text(f"Median Year: {peoples_age_df['party_age'].median()}")
st.text(f"Mean Year: {int(peoples_age_df['party_age'].mean())}")
st.text(f"Standard Deviation: {peoples_age_df['party_age'].std():.2f}")

st.text("as we can see, the most dangerous drivers are young: 18 to 30 yo.")
st.text("as the person gets older, the less likely they are to get into accident.")

st.title("People's description")

people_info_df = data[
    ((data['party_sex'] == 'female') | (data['party_sex'] == 'male')) &
    (data['party_age'].notna()) &
    (data['cellphone_in_use'].notna()) &
    (data['party_race'].notna())
    ]

people_info_df.head()

male_count = people_info_df[people_info_df['party_sex'] == 'male'].shape[0]
female_count = people_info_df[people_info_df['party_sex'] == 'female'].shape[0]

race_counts = people_info_df['party_race'].value_counts()
phone_usage = people_info_df['cellphone_in_use'].value_counts()


@st.cache_resource
def create_pie_charts():
    fig, axes = plt.subplots(1, 3, figsize=(12, 6))

    axes[0].pie(
        [male_count, female_count],
        labels=['Male', 'Female'],
        autopct='%1.1f%%',
        colors=['blue', 'pink']
    )
    axes[0].set_title('Gender Distribution')

    axes[1].pie(
        race_counts,
        labels=race_counts.index,
        autopct='%1.1f%%',
        startangle=140
    )
    axes[1].set_title('Race Distribution')

    axes[2].pie(
        phone_usage,
        labels=['Not Used', 'Used'],
        autopct='%1.1f%%',
        startangle=140
    )
    axes[2].set_title('Phone Usage Distribution')

    plt.tight_layout()
    st.pyplot(fig)


create_pie_charts()

st.markdown("""1. men get into accidents twice as much are women.  
2. white and hispanic races are much more likely to get into accidents then asian and black.
3. only a small percent of people got into accidents because of their phone.""")

st.title("Now lets see whether young (18-30) people kill people more often then old (30+)")

traumas_df = download_traumas_data()
traumas_df.head()
traumas_df['fatality_prob'] = traumas_df['total_killed'] / traumas_df['total_people']
traumas_df['trauma_prob'] = traumas_df['total_injured'] / traumas_df['total_people']
traumas_df['fatality_prob'] = traumas_df['fatality_prob'].round(5)
traumas_df['trauma_prob'] = traumas_df['trauma_prob'].round(5)
traumas_df.head()


@st.cache_resource
def create_data_comparison():
    fig, axes = plt.subplots(1, 3, figsize=(15, 6))

    sns.barplot(x='age_group', y='total_killed', data=traumas_df, ax=axes[0], palette=['#66C2A5', '#FC8D62', '#8DA0CB'],
                hue='total_killed')
    axes[0].set_xlabel('Age Group')
    axes[0].set_ylabel('Total Killed')
    axes[0].set_title('Total People Killed by Age Group')

    sns.barplot(x='age_group', y='fatality_prob', data=traumas_df, ax=axes[1], palette='coolwarm', hue='fatality_prob')
    axes[1].set_xlabel('Age Group')
    axes[1].set_ylabel('Fatality Probability')
    axes[1].set_title('Fatality Probability')

    sns.barplot(x='age_group', y='trauma_prob', data=traumas_df, ax=axes[2], palette='viridis', hue='trauma_prob')
    axes[2].set_xlabel('Age Group')
    axes[2].set_ylabel('Trauma Probability')
    axes[2].set_title('Trauma Probability by Age Group')

    plt.tight_layout()
    st.pyplot(fig)


create_data_comparison()

st.markdown('''as we can see, adults kill more people in general. that's simply because this group is the largest.  
however, adults are much more likely to unalive people.  
on the other hand, young drivers can injure people with slightly more chances.''')

st.markdown('''## Theory Conclusion
- Young people cause more collisions.
- Young drivers are less likely to kill others.
- Young drivers more likely to injure others.
- The risk of collisions decreases with age.
- Young drivers are primarily a threat to property (cars), not health.

Therefore, the theory is only proven true partially.''')

with st.form("predict_form"):
    st.title("Will the person get into accident? Hm...")

    party_age = st.number_input("Enter Age", min_value=0.0, max_value=100.0, value=25.0)
    party_sex = st.selectbox("Select Gender", ["male", "female"])
    party_race = st.selectbox("Enter Race", ["white", "black", "asian", "hispanic", "other"])

    submit_button = st.form_submit_button()


    def send_request(age, sex, race):
        url = f"{BASE_URL}/predict"
        payload = {
            "age": age,
            "sex": sex,
            "race": race
        }
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Server responded with status code {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}


    if submit_button:
        result = send_request(party_age, party_sex, party_race)
        if "error" in result:
            st.error(result["error"])
        else:
            if result["at_fault"]:
                st.write("Yeah, this person is very likely to get into accident")
            else:
                st.write("No, this person is not likely to get into accident")
