import streamlit as st
import pandas as pd
from snowflake.snowpark.functions import col
import requests

# App title
st.title("Customize Your Smoothie 🥤")

st.write(
    """
    Replace this example with your own code!
    **And if you're new to Streamlit,** check out the guides at https://docs.streamlit.io
    """
)

# Name input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit data
my_dataframe = session.table("smoothies.public.fruit_options") \
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))

# Convert to pandas
pd_df = my_dataframe.to_pandas()

# Optional: show table
st.dataframe(pd_df, use_container_width=True)

# ✅ Multiselect needs a LIST
ingredients_list = st.multiselect(
    "CHOOSE UP TO 5 INGREDIENTS:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        # Get SEARCH_ON value
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen, "SEARCH_ON"
        ].iloc[0]

        st.write(
            f"The search value for {fruit_chosen} is {search_on}."
        )

        # Call API using SEARCH_ON
        st.subheader(f"{fruit_chosen} Nutrition Information")
        response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + search_on
        )

        st.json(response.json())

    st.write("Ingredients:", ingredients_string)

    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    time_to_insert = st.button("Submit Order")
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered!", icon="✅")
