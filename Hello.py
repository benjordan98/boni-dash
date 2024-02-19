import streamlit as st
from PIL import Image
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)

def run():
    st.set_page_config(
        page_title="Welcome",
        page_icon="🍕",
        layout="wide"
    )

    # inter page variables 
    # currently selected member
    if 'index' not in st.session_state:
        st.session_state.index = 0

    # list of members
    if 'members' not in st.session_state:
        st.session_state.members = ('Ben', 'Hubert', 'Kasia', 'Tonda', 'Tomas', 
                                    'Oskar', 'Linn', 'Sofia')

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
        index = st.session_state.index)
    st.session_state.index = st.session_state.members.index(st.session_state.member)
    # blah blah blah
    st.write("👋 Welcome. This is a Mini Data App about the Piran Groups Boni Journey...")

if __name__ == "__main__":
    run()
