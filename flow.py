from streamlit_react_flow import react_flow
import streamlit as st
from pprint import pprint
import pandas as pd
import replicate
import os
from transformers import AutoTokenizer
import sys
from util import get_env_var_config
from snowflake.snowpark import Session

os.environ["SNOWSQL_USER"] = st.secrets["SNOWFLAKE_USER"]
os.environ["SNOWSQL_PWD"] = st.secrets["SNOWFLAKE_PASSWORD"]
os.environ["SNOWSQL_ACCOUNT"] = st.secrets["SNOWFLAKE_ACCOUNT"]
os.environ["SNOWSQL_ROLE"] = st.secrets["SNOWFLAKE_ROLE"]
os.environ["SNOWSQL_DATABASE"] = st.secrets["SNOWFLAKE_DATABASE"]
os.environ["SNOWSQL_SCHEMA"] = st.secrets["SNOWFLAKE_SCHEMA"]

session = Session.builder.configs(get_env_var_config()).create()

# FUNCTIONAL_ROLEの一覧を取得
# session.sql("SHOW ROLES").collect()
# result = session.sql(
#     # "SELECT * FROM table(result_scan(last_query_id())) where \"name\" in ('DATA_SCIENTIST', 'DATA_ENGINEER', 'MARKETING_ANALYST', 'SALES_ANALYST')")
#     "SELECT * FROM table(result_scan(last_query_id())) where \"name\" in ('MARKETING_ANALYST', 'DATA_SCIENTIST', 'SALES_ANALYST')")

# role_options = result.to_pandas()["name"].tolist()
# ハードコード
role_options = ["MARKETING_ANALYST", "SALES_ANALYST"]


def gen_element(row):
    return {
        "data": {"label": row["NAME"], "type": "ACCESS_ROLE"},
        "position": {"x": 300, "y": 100},
        "style": {"background": '#f8f8ff', "width": 350},
        "sourcePosition": "right",
        "targetPosition": "left",
    }


def mapping_access_role(row, element, last_element_id):

    grant_element = {
        "id": str(int(last_element_id) + 1),
        "data": {"label": row["GRANTED_ON"] + " | " + row["NAME"] + " | " + row["PRIVILEGE"], "type": "GRANT", "access_role": element["data"]["label"]},
        "type": "input",
        "position": {
            "x": 1000, "y": -300},
        "style": {"background": '#f8f8ff', "width": 300},
        "sourcePosition": "right"
    }
    mapping = {
        "id": f'e{element["id"]}-{row["NAME"]}',
        "source": element["id"],
        "target": grant_element["id"],
        "animated": True,
        'type': 'smoothstep',
    }

    return grant_element, mapping


def main():
    st.set_page_config(layout="wide")

    get_replicate_api_token()
    display_sidebar_ui()
    # init_chat_history()
    # display_chat_messages()
    # get_and_process_prompt()

    # セッション状態の初期化
    if 'selected_role' not in st.session_state or st.session_state['selected_role'] not in role_options:
        st.session_state['selected_role'] = role_options[0] if role_options else None

    # FUNCTIONAL_ROLEの一覧から一つを選択
    selected_role = st.selectbox(
        "**Select Role**", role_options)

    # 選択された値をセッション状態に保存
    st.session_state['selected_role'] = selected_role

    if not st.session_state['selected_role']:
        pass
    else:
        result = session.sql(
            f"select name from role_info where grantee_name = '{st.session_state['selected_role']}'")
        roles = result.to_pandas()

        result = session.sql(f"""
            select DISTINCT * from role_info where grantee_name in 
            (select name from role_info where grantee_name = '{st.session_state['selected_role']}')
            """)
        access_role_grants = result.to_pandas()
        session.close()

        elements = roles.apply(gen_element, axis=1).tolist()

        # add id to elements and add x, y position
        element_mapping = []
        for i, element in enumerate(elements):
            element["id"] = str(i+2)
            element_mapping.append(
                {
                    "id": f'e1-{i+2}',
                    "source": '1',
                    "target": element["id"],
                    "animated": True,
                    'type': 'smoothstep',
                })
        last_element_id = len(elements) + 1

        grant_elements_list = []
        for i, element in enumerate(elements):
            # access_rolesの紐付け
            print(element["data"]["label"])
            elements_grants = access_role_grants[access_role_grants["GRANTEE_NAME"] ==
                                                 element["data"]["label"]]
            result = elements_grants.apply(mapping_access_role,
                                           element=element, last_element_id=last_element_id, axis=1)
            grant_elements = [r[0] for r in result]
            mapping = [r[1] for r in result]

            # grant_elements, mappingのid更新
            for j, grant_element in enumerate(grant_elements):
                grant_element["id"] = str(int(last_element_id) + j + 1)
                mapping[j]["id"] = f'e{element["id"]}-{grant_element["id"]}'
                mapping[j]["target"] = grant_element["id"]
            grant_elements_list.extend(grant_elements)
            grant_elements_list.extend(mapping)
            last_element_id += len(grant_elements) + len(mapping)

        # 'id': 1の要素を追加
        root_element = {
            "id": '1',
            "data": {"label": st.session_state['selected_role']},
            "type": "input",
            # ここで位置を動的に計算する
            "position": {"x": 0, "y": 200},
            "style": {"background": '#ffcc50', "width": 150},
            "sourcePosition": "right",
        }
        elements.append(root_element)

        elements.extend(element_mapping)
        elements.extend(grant_elements_list)

        # ポジションの更新
        # 権限系のelementをy軸等間隔で配置
        i = 0
        for elem in elements:
            if elem.get("data", {}).get("type", "") == "GRANT":
                elem["position"]["y"] = 100 * i
                i += 1
        # ACCESS_ROLEを権限系のelementの真ん中に配置
        for i, elem in enumerate(elements):
            if elem.get("data", {}).get("type", "") == "ACCESS_ROLE":
                grant_elems = [e for e in elements if e.get("data", {}).get("type", "") == "GRANT" and e.get(
                    "data", {}).get("access_role") == elem.get("data", {}).get("label")]
                if grant_elems:
                    y_positions = [e2["position"]["y"]
                                   for e2 in grant_elems]
                    average_y = sum(y_positions) / len(y_positions)
                    elem["position"]["y"] = average_y

        # 'id': 1の要素を真ん中に配置
        if elements:
            y_positions = [elem["position"]["y"]
                           for elem in elements if "ACCESS" in elem.get("data", {}).get("label", "")]
            if y_positions:
                average_y = sum(y_positions) / len(y_positions)
                root_element["position"]["y"] = average_y

        flowStyles = {"height": 1000, "width": 2000}
        access_role_grants_mrkdwn = access_role_grants.to_markdown()

        prompt = f"""日本語で回答をお願いします。
Snowflake環境のロール設計について評価とアドバイスをお願いします。以下の情報を基に、ファンクショナルロールとアクセスロールの関係、および命名規則について問題がないか確認してください。
選択されたファンクショナルロール: {st.session_state['selected_role']}
以下の表は、ファンクショナルロールとアクセスロールの関係を示しています。
NAME: オブジェクト名、PRIVILEGE: 権限名、GRANTEE_NAME: アクセスロール名、GRANTED_ON: オブジェクトの種類
{access_role_grants_mrkdwn}
- 命名規則: ロール名はすべて大文字で、アンダースコアで区切ります。
- ファンクショナルロールには「_ROLE」、アクセスロールには「_ACCESS」を末尾に付けます。
- 評価ポイント
    - 権限の過剰付与
    - 権限の不足
    - アクセスロールの適用範囲
    - セキュリティ
    - 一貫性
    - 命名規則
- 期待する出力
    - ロール設計の評価
    - 命名規則の評価
    - 問題点と改善策
"""
        # 英語ver.
#         prompt = f"""
# The relationship between the functional role: {st.session_state['selected_role']} and the access roles is as shown in the following markdown.
# NAME is the object name, PRIVILEGE is the privilege name, GRANTEE_NAME is the access role name, and GRANTED_ON indicates the type of object.
# Please advise if there are any issues with this content.
# {access_role_grants_mrkdwn}
# """
        print(prompt)

        get_and_process_prompt(prompt)
        st.subheader(f"Relationship of {selected_role} and Access Roles")
        react_flow("friends", elements=elements, flow_styles=flowStyles)


def get_replicate_api_token():
    os.environ['REPLICATE_API_TOKEN'] = st.secrets['REPLICATE_API_TOKEN']


def display_sidebar_ui():
    with st.sidebar:
        st.title('Snowflake Role Adviser')
        st.caption("ファンクショナルロールとアクセスロールの関係を可視化します。")
        st.caption("またその関係に問題がないかアドバイスを行います。")
        # st.slider('temperature', min_value=0.01, max_value=5.0, value=0.3,
        #           step=0.01, key="temperature")
        # st.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01,
        #           key="top_p")

        # st.button('Clear chat history', on_click=clear_chat_history)

        st.write("---")

        st.subheader("About")
        st.caption("""
Hi! I'm a Data Engineer at Telecom Company. I've developed a tool to visualize the relationship between functional roles and access roles in Snowflake.
and Advice on whether the relationship is appropriate or not using Snowflake Arctic!
        """)

        # # # Uncomment to show debug info
        # st.subheader("Debug")
        # st.write(st.session_state)


def clear_chat_history():
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi. I'm Arctic, a new, efficient, intelligent, and truly open language model created by Snowflake AI Research. Ask me anything."}]
    st.session_state.chat_aborted = False


def init_chat_history():
    """Create a st.session_state.messages list to store chat messages"""
    if "messages" not in st.session_state:
        clear_chat_history()
        # check_safety()


def display_chat_messages():
    # Set assistant icon to Snowflake logo
    icons = {"assistant": "./Snowflake_Logomark_blue.svg", "user": "⛷️"}

    # Display the messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=icons[message["role"]]):
            st.write(message["content"])


@st.cache_resource(show_spinner=False)
def get_tokenizer():
    """Get a tokenizer to make sure we're not sending too much text
    text to the Model. Eventually we will replace this with ArcticTokenizer
    """
    return AutoTokenizer.from_pretrained("huggyllama/llama-7b")


@st.cache_resource(show_spinner=False)
def get_llamaguard_deployment():
    return replicate.deployments.get("meta/meta-llama-guard-2-8b")


def get_num_tokens(prompt):
    """Get the number of tokens in a given prompt"""
    tokenizer = get_tokenizer()
    tokens = tokenizer.tokenize(prompt)
    return len(tokens)


def abort_chat(error_message: str):
    """Display an error message requiring the chat to be cleared. 
    Forces a rerun of the app."""
    assert error_message, "Error message must be provided."
    error_message = f":red[{error_message}]"
    if st.session_state.messages[-1]["role"] != "assistant":
        st.session_state.messages.append(
            {"role": "assistant", "content": error_message})
    else:
        st.session_state.messages[-1]["content"] = error_message
    st.session_state.chat_aborted = True
    st.rerun()


def get_and_process_prompt(content):
    """Get the user prompt and process it"""

    response = generate_arctic_response(content)
    st.write_stream(response)


def generate_arctic_response(content):
    messages = [{
        "role": "user",
        "content": content
    }]
    prompt = []
    for dict_message in messages:
        if dict_message["role"] == "user":
            prompt.append("<|im_start|>user\n" +
                          dict_message["content"] + "<|im_end|>")
        else:
            prompt.append("<|im_start|>assistant\n" +
                          dict_message["content"] + "<|im_end|>")

    prompt.append("<|im_start|>assistant")
    prompt.append("")
    prompt_str = "\n".join(prompt)

    messages.append({"role": "assistant", "content": ""})
    # meta/meta-llama-3-70b-instruct
    # model_name = "meta/meta-llama-3-70b-instruct"
    # snowflake/snowflake-arctic-instruct
    model_name = "snowflake/snowflake-arctic-instruct"
    for event_index, event in enumerate(replicate.stream(model_name,
                                                         input={"prompt": prompt_str,
                                                                "prompt_template": r"{prompt}",
                                                                "temperature": 0.2,
                                                                "top_p": 0.9,
                                                                "max_new_tokens": 4096,
                                                                })):
        if (event_index + 0) % 50 == 0:
            pass
        messages[-1]["content"] += str(event)
        sys.stdout.write(str(event))
        sys.stdout.flush()
        yield str(event)


if __name__ == '__main__':
    main()
