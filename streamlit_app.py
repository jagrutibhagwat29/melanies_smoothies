# Import python packages
import streamlit as st
import pandas as pd
import hashlib

def hash_ingredients(text):
    return hashlib.sha256(text.encode()).hexdigest()

from snowflake.snowpark.functions import col
import requests
# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write( """Choose the fruit you want in your custom smoothie!.""")

name_on_order = st.text_input("Name on smoothie:")
st.write('The name on your smoothie will be :', name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('fruit_name'),col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

#convert the snowpark Dataframe to a panda Dataframe so we can use the LOC function
pd_df=my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()

ingredients_list = st.multiselect('Choose upto 5 ingredents:'
                                  ,my_dataframe
                                  ,max_selections=5)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen +','

        ingredients_hash = hash_ingredients(ingredients_string)

       
    st.write("Ingredients:", ingredients_string)
    st.write("Ingredients Hash:", ingredients_hash)

    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[
            pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'
        ].iloc[0]

        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )
        st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders
        (ingredients, ingredients_hash, name_on_order)
        VALUES
        ('{ingredients_string}', '{ingredients_hash}', '{name_on_order}')
    """

    if st.button('Submit Order'):
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")



