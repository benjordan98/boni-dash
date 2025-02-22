import streamlit as st
from PIL import Image
from streamlit.logger import get_logger
import pandas as pd
from utils import create_header_triplet, initialise_session_states

LOGGER = get_logger(__name__)

def display_member_image():
    # images come with width 960 - seems too much rescale
    head = Image.open('Images/' + st.session_state.member + '.png')
    head = head.resize((int(head.size[0] * 0.75), int(head.size[1]*0.75)))
    st.image(head)

def on_member_change():
    st.session_state.member = st.session_state.selected_member

def setup_members_select_box(select_box):
    select_box.selectbox(
        label='Who are you?',
        options=st.session_state.members,
        key='selected_member',
        index=st.session_state.members.index(st.session_state.member), 
        on_change=on_member_change 
    )

def run():
    st.set_page_config(
        page_title="Welcome",
        page_icon="🍕",
        layout="wide"
    )

    initialise_session_states()

    _, _, select_box  = create_header_triplet()

    setup_members_select_box(select_box)
    
    st.write("👋 Welcome. This is a Mini Data App about the Piran Group's Boni Journey - data still pending on other mem. Enjoy 😋")

    display_member_image()

if __name__ == "__main__":
    run()
