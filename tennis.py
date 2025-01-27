
import streamlit as st
import pandas as pd
import mysql.connector
import numpy as np
def get_connection():
    return  mysql.connector.connect(
  host = "gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
  port = 4000,
  user = "4MBhHyMvpwwkCgp.root",
  password = "wW5SWx4oG97MwJXC",
  database="tennis"
    )
def fetch_data(query, params=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params or ())
    data = cursor.fetchall()
    conn.close()
    return data
def main():
    st.title('Tennis Details')
    st.image('https://plus.unsplash.com/premium_photo-1666913667082-c1fecc45275d?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D')
    st.write("Explore competitors and their rankings with search and filter options.")

    # Search and Filters Section
    st.sidebar.header("Search & Filters")
    search_name = st.sidebar.text_input("Search by Competitor Name")
    country_filter = st.sidebar.text_input("Filter by Country Code")
    points_filter = st.sidebar.slider("Filter by Points (Min)", 0, 5000, 0)
    rank_range = st.sidebar.slider("Filter by Rank Range", 1, 100, (1, 100))

    # Base Query for Competitors
    base_query = """
        SELECT 
            c.competitor_id, 
            c.name, 
            c.country, 
            c.country_code, 
            cr.rank, 
            cr.points 
        FROM competitor c
        LEFT JOIN competitor_rankings cr ON c.competitor_id = cr.Competitor_id
        WHERE 1=1
    """

    # Dynamic Filtering
    filters = []
    params = []
    if search_name:
        filters.append("AND c.name LIKE %s")
        params.append(f"%{search_name}%")
    if country_filter:
        filters.append("AND c.country_code = %s")
        params.append(country_filter)
    if points_filter > 0:
        filters.append("AND cr.points >= %s")
        params.append(points_filter)
    if rank_range:
        filters.append("AND cr.rank BETWEEN %s AND %s")
        params.extend(rank_range)

    # Combine query and filters
    full_query = base_query + " ".join(filters)
    competitors = fetch_data(full_query, params)

    # Display Competitors
    st.subheader("Competitor List")
    if competitors:
        competitors_df = pd.DataFrame(competitors)
        st.dataframe(competitors_df)
    else:
        st.warning("No competitors found with the given criteria.")

    # Competitor Details Viewer
    st.subheader("Competitor Details Viewer")
    competitor_ids = [comp["competitor_id"] for comp in competitors]
    selected_competitor = st.selectbox("Select a Competitor ID", competitor_ids)

    if selected_competitor:
        detail_query = """
            SELECT 
                c.competitor_id, 
                c.name, 
                c.country, 
                c.country_code, 
                c.abbreviation, 
                cr.rank, 
                cr.movement, 
                cr.points, 
                cr.competitions_played 
            FROM competitor c
            LEFT JOIN competitor_rankings cr ON c.competitor_id = cr.Competitor_id
            WHERE c.competitor_id = %s
        """
        details = fetch_data(detail_query, (selected_competitor,))
        if details:
            details_df = pd.DataFrame(details)
            st.write("Competitor Details:")
            st.dataframe(details_df)
        else:
            st.warning("No details found for the selected competitor.")

if __name__ == "__main__":
    main()


def fetch_data(search_term, min_rank, max_rank, country, points_threshold):
    query = """
    SELECT c.competitor_id, c.name, c.country, r.rank, r.points, r.competitions_played
    FROM competitor c
    JOIN competitor_rankings r ON c.competitor_id = r.Competitor_id
    WHERE 1=1
    """
    
    # Dynamically add conditions
    if search_term:
        query += f" AND c.name LIKE '%{search_term}%'"
    if min_rank and max_rank:
        query += f" AND r.rank BETWEEN {min_rank} AND {max_rank}"
    if country:
        query += f" AND c.country = '{country}'"
    if points_threshold:
        query += f" AND r.points >= {points_threshold}"
    
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query)
    results = cursor.fetchall()
    connection.close()
    
    return pd.DataFrame(results)

# Streamlit Page
st.title("Search and Filter Competitors")

# Input fields for filters
search_term = st.text_input("Search by Competitor Name:")
min_rank, max_rank = st.slider("Rank Range:", 1, 100, (1, 100))
country = st.text_input("Country:")
points_threshold = st.number_input("Minimum Points Threshold:", min_value=845, value=845)

# Fetch and display data
if st.button("Search"):
    data = fetch_data(search_term, min_rank, max_rank, country, points_threshold)
    if not data.empty:
        st.dataframe(data)
    else:
        st.warning("No competitors found with the given filters.")
def fetch_competitors():
    query = "SELECT competitor_id, name FROM competitor;"
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query)
    results = cursor.fetchall()
    connection.close()
    return pd.DataFrame(results)

# Fetch detailed information for a specific competitor
def fetch_competitor_details(competitor_id):
    query = """
    SELECT c.name, c.country, r.rank, r.movement, r.competitions_played, r.points
    FROM competitor c
    JOIN competitor_rankings r ON c.competitor_id = r.Competitor_id
    WHERE c.competitor_id = %s;
    """
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query, (competitor_id,))
    result = cursor.fetchone()
    connection.close()
    return result

# Streamlit App
st.title("Competitor Details Viewer")

# Step 1: Dropdown for competitor selection
st.subheader("Select a Competitor")
competitors_df = fetch_competitors()
competitor_name_to_id = dict(zip(competitors_df["name"], competitors_df["competitor_id"]))
selected_competitor_name = st.selectbox("Choose a competitor:", competitors_df["name"])

if selected_competitor_name:
    competitor_id = competitor_name_to_id[selected_competitor_name]
    
    # Step 2: Fetch and display details
    competitor_details = fetch_competitor_details(competitor_id)
    
    if competitor_details:
        st.subheader("Competitor Details")
        st.write(f"**Name:** {competitor_details['name']}")
        st.write(f"**Country:** {competitor_details['country']}")
        st.write(f"**Rank:** {competitor_details['rank']}")
        st.write(f"**Movement:** {competitor_details['movement']}")
        st.write(f"**Competitions Played:** {competitor_details['competitions_played']}")
        st.write(f"**Points:** {competitor_details['points']}")
    else:
        st.error("No details found for the selected competitor.")

def fetch_country_analysis():
    query = """
    SELECT 
        c.country,
        COUNT(c.competitor_id) AS total_competitors,
        AVG(r.points) AS average_points
    FROM competitor c
    JOIN competitor_rankings r ON c.competitor_id = r.Competitor_id
    GROUP BY c.country
    ORDER BY total_competitors DESC;
    """
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query)
    results = cursor.fetchall()
    connection.close()
    return pd.DataFrame(results)

# Streamlit App
st.title("Country-Wise Competitor Analysis")

# Fetch and display country-wise analysis
st.subheader("Country Statistics")
data = fetch_country_analysis()

if not data.empty:
    # Display the data in a table
    st.dataframe(data)

    # Visualize using a bar chart
    st.subheader("Total Competitors by Country")
    st.bar_chart(data.set_index("country")["total_competitors"])
    
    st.subheader("Average Points by Country")
    st.bar_chart(data.set_index("country")["average_points"])
else:
    st.error("No data available for analysis.")


def fetch_top_ranked(limit=10):
    query = """
    SELECT c.name, c.country, r.rank, r.points, r.competitions_played
    FROM competitor c
    JOIN competitor_rankings r ON c.competitor_id = r.Competitor_id
    ORDER BY r.rank ASC
    LIMIT %s;
    """
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query, (limit,))
    results = cursor.fetchall()
    connection.close()
    return pd.DataFrame(results)

# Fetch competitors with the highest points
def fetch_highest_points(limit=10):
    query = """
    SELECT c.name, c.country, r.rank, r.points, r.competitions_played
    FROM competitor c
    JOIN competitor_rankings r ON c.competitor_id = r.Competitor_id
    ORDER BY r.points DESC
    LIMIT %s;
    """
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query, (limit,))
    results = cursor.fetchall()
    connection.close()
    return pd.DataFrame(results)

# Streamlit App
st.title("Tennis Leaderboards")

# Sidebar for leaderboard selection
st.sidebar.title("Leaderboard Options")
leaderboard_type = st.sidebar.radio(
    "Choose a leaderboard to view:",
    ("Top-Ranked Competitors", "Competitors with Highest Points")
)

# Sidebar for number of entries to show
limit = st.sidebar.slider("Number of competitors to display:", min_value=5, max_value=20, value=10)

# Display leaderboard based on user selection
if leaderboard_type == "Top-Ranked Competitors":
    st.subheader("🏆 Top-Ranked Competitors")
    data = fetch_top_ranked(limit)
else:
    st.subheader("🌟 Competitors with the Highest Points")
    data = fetch_highest_points(limit)

# Display data in a table
if not data.empty:
    st.dataframe(data)
else:
    st.error("No data available to display.")