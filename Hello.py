import streamlit as st
from PIL import Image
from streamlit.logger import get_logger
import pandas as pd

LOGGER = get_logger(__name__)

def pre_process_df(df):
    """
    Any standard pre-processing of df
    for all charts
    """
    # datetime
    df['date'] = pd.to_datetime(df['date'])
    return df

def run():
    st.set_page_config(
        page_title="Welcome",
        page_icon="🍕",
        layout="wide"
    )

    # inter page variables
    if 'member' not in st.session_state:
        st.session_state.member = 'Ben'
    # list of members
    if 'members' not in st.session_state:
        # st.session_state.members = ('Ben', 'Hubert', 'Kasia', 'Tonda', 'Tomas', 
        #                             'Oskar', 'Linn', 'Sofia')
        st.session_state.members = ('Ben', 'Oskar', 'Tonda')
        
    if 'combined_df' not in st.session_state:
        combined_df = pre_process_df(pd.read_csv('data/combined_data2.csv'))
        st.session_state.combined_df = combined_df

    if 'last_recorded_date' not in st.session_state:
        st.session_state.last_recorded_date = st.session_state.combined_df['date'].max()

    # Displays title and image
    img, heading, member = st.columns([1,8, 2])
    # image
    image_path = "boni-removebg-preview.png"
    pillow_image = Image.open(image_path)
    scalar = 0.55
    new_image = pillow_image.resize((int(177*scalar), int(197*scalar)))
    img.image(new_image)
    # title
    heading.markdown(" # Študentska **prehrana**")
    # selectbox for who you are! Save in session_state for default values in 
    # comparison and journey page
    member.selectbox(
        label = 'Who are you?',
        options = st.session_state.members,
        key='member',
        index = st.session_state.members.index(st.session_state.member))
    # blah blah blah
    st.write("👋 Welcome. This is a little Mini Data App about the Piran Group's Boni Journey. Enjoy 😋")

if __name__ == "__main__":
    run()
