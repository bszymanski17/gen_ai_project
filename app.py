from src.orchestrators.edit_data import edit_data
from src.orchestrators.generate_data import generate_data
import streamlit as st
from src.database.database_handler import init_tables, preprocess_ddl
from src.core.utilts import create_logger, load_config
import json
from src.core.utilts import get_cached, init_instrumentation
from src.orchestrators.talk_to_data import talk_to_data, init_data_chat
from src.core.jailbreak_detection import security_check

st.set_page_config(page_title="Synthetic AI Data Gen", layout="wide")
logger = create_logger("UI APP")

#langfuse
init_instrumentation()

prompts, config = get_cached()


if "generated_data" not in st.session_state:
    st.session_state.generated_data = {} # dict table_name: table

if "current_page" not in st.session_state:
    st.session_state.current_page = "data_generation"


# SIDEBAR
with st.sidebar:
    st.title("Data Assistant")
    if st.button("Data Generation",width="stretch"):
        st.session_state.current_page = "data_generation"
    if st.button("Talk to your data", width="stretch"):
        st.session_state.current_page = "talk_to_data"

########################
# Data generation page:
########################

if st.session_state.current_page == "data_generation":
    
    # UPPER SECTION
    upper_section = st.container(border=True)

    with upper_section:
        st.text_input(placeholder="Enter your prompt here...", label="Prompt", key="user_prompt")
        uploaded_file = st.file_uploader(label="Upload DDL Schema", type=['ddl', 'sql', 'json'])
        if uploaded_file is not None:
            ddl_schema_raw = uploaded_file.getvalue().decode("utf-8")
            st.session_state.ddl_schema = preprocess_ddl(ddl_schema_raw)
            st.success(f"Successfully loaded schema from file: {uploaded_file.name}")
        elif "ddl_schema" in st.session_state and st.session_state.ddl_schema is not None:
            st.info("Using DDL schema previously loaded in this session.")

        st.divider()
        st.text("Advanced Parameters")
        col_temp, col_tokens = st.columns([3,1], gap="large")
        with col_temp:
            temp_val = st.slider(label="Temperature", min_value=0.0, max_value=2.0, value=0.7)
        with col_tokens:
            max_tokens_val = st.number_input(label="Max tokens", min_value=1, value=65000, max_value=65536)
        
        
        if st.button(label="Generate"):
            if "ddl_schema" in st.session_state and st.session_state.ddl_schema is not None:
                security_check(st.session_state.user_prompt, "generation")
                
                if init_tables(st.session_state.ddl_schema):
                    with st.spinner("Generating data..."):
                        generated_tables = None
                        generated_tables, warning_msg = generate_data(prompts=prompts, ddl_schema=st.session_state.ddl_schema, user_instructions=st.session_state.user_prompt, approach=config['validation_approaches']['generating_approach'], temperature=temp_val, max_tokens=max_tokens_val)
                        
                        if warning_msg:
                            st.warning(warning_msg)
                        elif generated_tables:
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

        edit_alerts = st.empty()


        col_instr, col_submit = st.columns([10,1])
        with col_instr:
            st.text_input(label="Edit instruction", label_visibility="collapsed", placeholder="Enter quick edit instructions...", key="edit_prompt")
        with col_submit:
            if st.button(label="Submit"):
                if st.session_state.edit_prompt and st.session_state.generated_data and st.session_state.ddl_schema:
                    security_check(st.session_state.edit_prompt, "generation")
                    with st.spinner("Editing data..."):
                        ddl_schema = st.session_state.ddl_schema
                        current_data_dict = {t_name: df.to_dict(orient='records') for t_name,df in st.session_state.generated_data.items()}
                        current_data_json = json.dumps(current_data_dict, default=str)
                        edited_tables = None
                        edited_tables, warn_msg = edit_data(prompts=prompts, ddl_schema=st.session_state.ddl_schema, user_instructions=st.session_state.edit_prompt, approach=config['validation_approaches']['editing_approach'], data=current_data_json, temperature=temp_val, max_tokens=max_tokens_val)

                        if warn_msg:
                            edit_alerts.warning(warn_msg)
                        elif edited_tables:
                            st.session_state.generated_data = edited_tables
                            st.rerun()
                            edit_alerts.succ("Data edited successfully.")
                        else:
                            edit_alerts.error("Faild to edit data.")
                elif not st.session_state.generated_data:
                    edit_alerts.warning("You need to generate data first before editing.")
                elif not st.session_state.edit_prompt:
                    edit_alerts.warning("Please provide instructions how to edit the data.")



##########################
# Talk to your data page:
##########################                    

elif st.session_state.current_page == "talk_to_data":

    if "data_chat" not in st.session_state:
        st.session_state.data_chat = init_data_chat(temperature=0.7, max_tokens=65000)

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "user":
                st.write(msg["text"])
            else:
                if "text" in msg and msg["text"]:
                    st.write(msg["text"])

                if "plot" in msg and msg["plot"] is not None:
                    st.plotly_chart(msg["plot"], width="stretch")
                else:
                    if "sql" in msg:
                        st.code(msg["sql"], language="sql")
                    if "table" in msg:
                        st.dataframe(msg["table"], width="stretch")
    
    user_ask_prompt = st.chat_input(placeholder="Ask a question abour your data...")

    if user_ask_prompt:
        if st.session_state.generated_data != {}:
            security_check(user_ask_prompt, "chat")
            st.session_state.chat_messages.append({'role': 'user', 'text': user_ask_prompt})
            with st.chat_message("user"):
                st.write(user_ask_prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Analyzing data..."):
                    talk_artifacts = talk_to_data(st.session_state.data_chat, prompts['user_prompts']['talk_to_data_main_promot'].format(ddl_schema=st.session_state.ddl_schema, user_instructions=user_ask_prompt))
                    if talk_artifacts['warning']:
                        st.warning(talk_artifacts['warning'])
                    else:
                        if talk_artifacts['plot'] is not None:
                            st.plotly_chart(talk_artifacts["plot"], width="stretch")
                        else:
                            if talk_artifacts['sql_query'] is not None:
                                st.code(talk_artifacts['sql_query'], language="sql")
                            if talk_artifacts['df'] is not None:
                                st.dataframe(talk_artifacts['df'], width="stretch")

                        st.session_state.chat_messages.append({"role": "assistant", "sql": talk_artifacts['sql_query'], "table": talk_artifacts['df'], "plot": talk_artifacts['plot']})
        else: 
            st.warning("Najpierw wygeneruj dane!")