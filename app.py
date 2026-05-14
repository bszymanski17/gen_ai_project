# aporach 1
from src.orchestrators.direct.generator_direct import generate_data
from src.orchestrators.direct.editor_direct import edit_data

# aproach 2 (function calling)
from src.orchestrators.function_calling.generator_fc import generate_data_fc
from src.orchestrators.function_calling.editor_fc import edit_data_fc

# aporach 3 (query database)
from src.orchestrators.query.query_engine import query_engine, update_tables

# config
import streamlit as st
from src.database.database_handler import init_tables, preprocess_ddl, get_engine
from src.core.utilts import create_logger
import json
from src.core.utilts import load_config
import pandas as pd

st.set_page_config(page_title="Synthetic AI Data Gen", layout="wide")
logger = create_logger("UI APP")

@st.cache_data
def get_cached_prompts():
    return load_config("prompts/prompts.yaml")

prompts = get_cached_prompts()

if "generated_data" not in st.session_state:
    st.session_state.generated_data = {} # dict table_name: table


# SIDEBAR
with st.sidebar:
    st.title("Data Assistant")
    st.button("Data Generation",width="stretch")
    st.button("Talk to your data", width="stretch")

# UPPER SECTION
upper_section = st.container(border=True)

with upper_section:
    st.text_input(placeholder="Enter your prompt here...", label="Prompt", key="user_prompt")
    uploaded_file = st.file_uploader(label="Upload DDL Schema", type=['ddl', 'sql', 'json'])
    st.divider()
    st.text("Advanced Parameters")
    col_temp, col_tokens = st.columns([3,1], gap="large",)
    with col_temp:
        st.slider(label="Temperature", min_value=0.0, max_value=2.0, value=0.7)
    with col_tokens:
        st.number_input(label="Max tokens", min_value=1, value=65000)
    
    
    if st.button(label="Generate"):
        if uploaded_file is not None:
            ddl_schema = uploaded_file.getvalue().decode("utf-8")
            ddl_schema = preprocess_ddl(ddl_schema)
            logger.info(f"File uploaded: {uploaded_file.name}.")
            
            if init_tables(ddl_schema):
                with st.spinner("Generating data..."):
                    generated_tables = generate_data(prompts=prompts, ddl_schema=ddl_schema, user_instructions=st.session_state.user_prompt,max_tokens=8000) # aporach 1
                    # generated_tables = generate_data_fc(prompts=prompts, ddl_schema=ddl_schema, user_instructions=st.session_state.user_prompt) # aproach 2 (function calling)
                    if generated_tables:
                        st.session_state.generated_data = generated_tables
                        st.success("Data generated successfully!")
                    else:
                        st.error("Failed to generate data.")
            else:
                st.error("Creating tables failed!")
        else:
            st.warning("Uplod DDL schema first!")



#LOWER SECTION
lower_section = st.container(border=True)

with lower_section:
    col_title, col_tables = st.columns([5,1])
    with col_title:
        st.subheader("Data preview")

    if st.session_state.generated_data:
        with col_tables:
            selected_table = st.selectbox(label="Table", options=st.session_state.generated_data.keys(), label_visibility="collapsed")

        st.dataframe(st.session_state.generated_data[selected_table], width='stretch')
    else:
        with col_tables:
            st.selectbox(label="Tables", options=["No data yet"], label_visibility="collapsed")
        st.info("Upload DDL schema and generate data to see preview here.")


    col_instr, col_submit = st.columns([14,1])
    with col_instr:
        st.text_input(label="Edit instruction", label_visibility="collapsed", placeholder="Enter quick edit instructions...", key="edit_prompt")
    with col_submit:
        if st.button(label="Submit"):
            if st.session_state.edit_prompt and st.session_state.generated_data and uploaded_file is not None:
                with st.spinner("Editing data..."):
                    ddl_schema = uploaded_file.getvalue().decode('utf-8')
                    current_data_dict = {t_name: df.to_dict(orient='records') for t_name,df in st.session_state.generated_data.items()}
                    current_data_json = json.dumps(current_data_dict, default=str)
                    # edited_tables = edit_data(current_data_json, prompts, ddl_schema, st.session_state.edit_prompt) # aporach 1
                    # edited_tables = edit_data_fc(current_data_json, prompts, ddl_schema, st.session_state.edit_prompt) # aproach 2 with function calling
                    
                    
                    # query aproach #
                    response = query_engine(ddl_schema,system_instructions=prompts['system_prompts']['edit_query_main_promt'], user_instructions=st.session_state.edit_prompt) # aporach 3 with database queries
                    edited_tables = update_tables(st.session_state.generated_data)                                                                                               # aporach 3 with database queries
                    # end of query aporach #

                    if edited_tables:
                        st.session_state.generated_data = edited_tables
                        st.success("Data edited successfully.")
                        st.rerun()
                    else:
                        st.error("Faild to edit data.")
            elif not st.session_state.generated_data:
                st.warning("You need to generate data first before editing.")
            elif not st.session_state.edit_prompt:
                st.warning("Please provide instructions how to edit the data.")