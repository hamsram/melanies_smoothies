import streamlit as st

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


name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)
# Define the selectbox label and options (you had undefined names)
label = "Choose a base for your smoothie"
options = ["Banana", "Strawberry", "Mango", "Spinach", "Blueberry"]


cnx=st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
#st.dataframe(data=my_dataframe, use_container_width=True)
ingredients_list=st.multiselect('cHOOSE UP TO 5 INGREDIENTS:',my_dataframe,max_selections=5)
if ingredients_list:
    
    ingredients_string=''
    for fruit_chosen in ingredients_list:
        ingredients_string+=fruit_chosen+' '
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
        #st.text(smoothiefroot_response.json())
        sf_df=st.dataframe(data=smoothiefroot_response.json(),use_container_width=True)
    st.write(ingredients_string)
    my_insert_stmt = """insert into smoothies.public.orders (ingredients, name_on_order)
values ('""" + ingredients_string + """', '""" + name_on_order + """')"""

    st.write(my_insert_stmt)
    #st.stop()

    st.write(my_insert_stmt)
    time_to_insert=st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")


