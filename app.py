import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
import google.auth.transport.requests
import os

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

CLIENT_ID     = st.secrets["google_oauth"]["client_id"]
CLIENT_SECRET = st.secrets["google_oauth"]["client_secret"]
REDIRECT_URI  = st.secrets["google_oauth"]["redirect_uri"]
SCOPES = ["openid", "email", "profile"]

def get_flow():
    return Flow.from_client_config(
        {"web": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }},
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

st.set_page_config(page_title="Sign in with Google", page_icon="🔐")

if "user" not in st.session_state:
    st.session_state.user = None

params = st.query_params
if "code" in params and not st.session_state.user:
    flow = get_flow()
    flow.fetch_token(code=params["code"])
    creds = flow.credentials
    info = id_token.verify_oauth2_token(
        creds.id_token,
        google.auth.transport.requests.Request(),
        CLIENT_ID
    )
    st.session_state.user = info
    st.query_params.clear()

if st.session_state.user:
    user = st.session_state.user
    st.image(user["picture"], width=80)
    st.title(f"Welcome, {user['name']}!")
    st.write(f"Email: {user['email']}")
    if st.button("Sign out"):
        st.session_state.user = None
        st.rerun()
else:
    st.title("Sign in with Google")
    st.write("Click below to sign in using your Google account.")
    flow = get_flow()
    auth_url, _ = flow.authorization_url(prompt="consent")
    st.link_button("Sign in with Google", auth_url)