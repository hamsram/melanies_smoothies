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

pd_df = my_dataframe.to_pandas()

# Multiselect (must be a list)
ingredients_list = st.multiselect(
    "CHOOSE UP TO 5 INGREDIENTS:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

if ingredients_list:

    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        # Lookup SEARCH_ON
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen, "SEARCH_ON"
        ].iloc[0]

        st.subheader(f"{fruit_chosen} Nutrition Information")
        smoothiefroot_response=requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        sf_df=st.dataframe(data=smoothiefroot_response.json(),usecontainer_width=True)

        # Call API using SEARCH_ON
        response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + search_on
        )

        fruit_json = response.json()

        # ✅ Convert nutrition JSON to table
        if "nutrition" in fruit_json:
            nutrition_df = pd.DataFrame(
                fruit_json["nutrition"].items(),
                columns=["Nutrient", "Amount"]
            )
            st.dataframe(nutrition_df, use_container_width=True)
        else:
            st.warning("No nutrition data available.")

    st.write("Ingredients:", ingredients_string)

    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    time_to_insert = st.button("Submit Order")
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered!", icon="✅")
