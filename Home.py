'''
This code has been written and maintained by Viswanathan Ganesh.
Feel free to use the code but give due credits!
'''

import asyncio
import streamlit as st
import google.generativeai as genai
import base64
from httpx_oauth.clients.google import GoogleOAuth2
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

client_id = st.secrets['client_id']
client_secret = st.secrets['client_secret']
redirect_uri = st.secrets['redirect_uri']
client = GoogleOAuth2(client_id, client_secret)

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

st.set_page_config(page_title="mAIl-IT", page_icon=":speech_balloon:", layout="centered")

system_prompt = st.secrets['system_prompt']

if 'email' not in st.session_state:
    st.session_state['email'] = ""

if 'pw' not in st.session_state:
    st.session_state['pw'] = ""

if 'to_email' not in st.session_state:
    st.session_state['to_email'] = ""

if 'output' not in st.session_state:
    st.session_state['output'] = ""


def AI(user_prompt):
    genai.configure(api_key=st.secrets['genai_api_key'])
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(user_prompt)
    return response.text


def message_maker(content):
    p = content.split("\n")
    return p[0][9:], '\n'.join(p[2:])


async def get_authorization_url(client: GoogleOAuth2, redirect_uri: str):
    authorization_url = await client.get_authorization_url(redirect_uri, scope=SCOPES)
    return authorization_url


auth_url = asyncio.run(
    get_authorization_url(client, redirect_uri))


async def get_access_token(client: GoogleOAuth2, redirect_uri: str, code: str):
    token = await client.get_access_token(code, redirect_uri)
    return token


def sendMail(to_email, content):
    service = None
    if 'code' in st.query_params:
        code = st.query_params['code']
        token = asyncio.run(get_access_token(client, redirect_uri, code))
        creds = Credentials(
            token=token['access_token'],
            refresh_token=token.get('refresh_token'),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client.client_id,
            client_secret=client.client_secret,
            scopes=SCOPES
        )

        service = build('gmail', 'v1', credentials=creds)

    subj, body = message_maker(content)
    message = MIMEText(body)
    message['to'] = to_email
    message['subject'] = subj
    create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

    try:
        service.users().messages().send(userId="me", body=create_message).execute()
        st.write("Mail has been successfully sent!")
    except:
        st.write("There was trouble in sending mail")

@st.dialog("Custom Dialog Title", width="large")
def thankyou():
    st.write("Thank you for choosing mAIl-IT <3. Your mail has been sent succesfully")
    if st.button("Close"):
        st.rerun()

if 'submitted' not in st.session_state:
    st.session_state['submitted'] = False

if 'signedIn' not in st.session_state:
    st.session_state['signedIn'] = False

if 'mail_sent' not in st.session_state:
    st.session_state['mail_sent'] = False

if "logged_in" in st.query_params and st.query_params["logged_in"] == "logged_in":
    st.session_state['signedIn'] = True

if not st.session_state["submitted"] and not st.session_state["signedIn"]:
    st.markdown('''<header style="text-align: center; padding: 20px; background-color: #121829; color: white;">
    <h1>mAIl-IT</h1>
    <p>Your one-stop solution to generate and send emails effortlessly!</p>
</header>''', unsafe_allow_html=True)
    st.markdown('''<section style="
    margin-bottom: 30px;
    text-align: left; /* Left-align the text */
    max-width: 800px; /* Limit width for better readability */
    margin-left: auto; /* Keep horizontally centered (for the section, not text) */
    margin-right: auto;
    padding-left: 20px; /* Add some left padding */
    padding-right: 20px;
">
    <h2 style="color: #fff;">Welcome to mAIl-IT!</h2>
    <p style="
        line-height: 1.6; /* Improved readability */
        color: #555; /* Slightly softer text color */
        font-size: 20px; /* Consistent font size */
    ">
        Need to send an email quickly? We've got you covered. With mAIl-IT, you can craft personalized, <b>AI-generated</b> emails and send them directly to your recipient without the hassle of opening your email client.
    </p>
</section>''', unsafe_allow_html=True)
    st.link_button("Sign in with Google", auth_url)

    if 'code' in st.query_params:
        st.session_state['signedIn'] = True
elif not st.session_state["submitted"] and st.session_state['signedIn']:
    with st.form(key='my_form'):
        to = st.text_input("Receiver's Name")
        st.session_state['to_email'] = st.text_input("To Email")
        reason = st.text_area("Describe about what you want in your mail :)")
        name = st.text_input("Your Name")
        contact = st.text_input("Enter Phone number")
        submit = st.form_submit_button("Submit")
    if submit:
        user_prompt = system_prompt + " Write a very human email to " + to + " for the reason of: " + reason + ". My name is " + name + ". My Contact is " + contact
        st.session_state['output'] = AI(user_prompt=user_prompt)
        st.session_state['submitted'] = True
        st.rerun()
elif st.session_state["submitted"] and st.session_state['signedIn'] and not st.session_state['mail_sent']:
    st.write(st.session_state['output'])
    col1, col2 = st.columns(2)
    with col1:
        send = st.button("Send Mail")
    with col2:
        notsend = st.button("Redo")
    if send:
        try:
            sendMail(st.session_state['to_email'], st.session_state['output'])
            st.session_state['mail_sent'] = True
            st.query_params['logged_in'] = 'NAN'
            thankyou()
            st.rerun()
        except:
            st.write("There was an error in sending the mail! Please press the Redo button!")
    if notsend:
        st.session_state['submitted'] = False
        st.session_state['signedIn'] = False
        st.query_params['logged_in'] = 'NAN'
        st.rerun()

        
