# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import inspect
import textwrap

import streamlit as st
from PIL import Image
import pandas as pd

def show_code(demo):
    """Showing the code of the demo."""
    show_code = st.sidebar.checkbox("Show code", True)
    if show_code:
        # Showing the code of the demo.
        st.markdown("## Code")
        sourcelines, _ = inspect.getsourcelines(demo)
        st.code(textwrap.dedent("".join(sourcelines[1:])))


def create_header_triplet(image_path="boni-removebg-preview.png", title="Študentska **prehrana**", scalar=0.55):
    img, heading, member = st.columns([1, 8, 2])
    try:
        pillow_image = Image.open(image_path)
        new_image = pillow_image.resize((int(177 * scalar), int(197 * scalar)))
        img.image(new_image)
    except Exception as e:
        st.error(f"Error loading image: {e}")
    heading.markdown(f"# {title}")

    return img, heading, member

def pre_process_df(df):
    """
    Any standard pre-processing of df
    for all charts
    """
    df['date'] = pd.to_datetime(df['date'])
    return df

def initialise_session_states():
    if 'member' not in st.session_state:
        st.session_state.member = 'Ben'

    if 'members' not in st.session_state:
        # st.session_state.members = ('Ben', 'Hubert', 'Kasia', 'Tonda', 'Tomas', 
        #                             'Oskar', 'Linn', 'Sofia')
        st.session_state.members = ('Ben', 'Oskar', 'Tonda')
        
    if 'combined_df' not in st.session_state:
        combined_df = pre_process_df(pd.read_csv('data/combined_data2.csv'))
        st.session_state.combined_df = combined_df

    if 'last_recorded_date' not in st.session_state:
        st.session_state.last_recorded_date = st.session_state.combined_df['date'].max()
