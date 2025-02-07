import streamlit as st
from google import genai
import smtplib

st.set_page_config(page_title="mAIl-IT", page_icon=":speech_balloon:", layout="centered")

system_prompt = "You are a professional formal email writer. Just write a mail with the given information. Don't suggest anything in the mail. Make subject professional."

if 'email' not in st.session_state:
    st.session_state['email'] = ""

if 'pw' not in st.session_state:
    st.session_state['pw'] = ""

if 'to_email' not in st.session_state:
    st.session_state['to_email'] = ""


if 'output' not in st.session_state:
    st.session_state['output'] = ""

def AI(user_prompt):
    client = genai.Client(api_key="AIzaSyBOvwQexlkM5UFLEDv6si9xj2wfikGvmt0")
    response = client.models.generate_content(
    model="gemini-2.0-flash", contents=user_prompt
    )
    return response.text

def sendMail(email, password, to_email, content):
    reciever = to_email
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()

    server.login(email, password=password)
    try:
        server.sendmail(email, reciever, content)
        
    except:
        print("Error 404")

if 'submitted' not in st.session_state:
    st.session_state['submitted'] = False


if not st.session_state["submitted"]:
    with st.form(key='my_form'):
        to = st.text_input("Name")
        st.session_state['to_email'] = st.text_input("To Email")
        reason = st.text_area("Describe about your mail requirements")
        name = st.text_input("Your Name")
        st.session_state['email'] = st.text_input("Your Email")
        st.session_state['pw'] = st.text_input("Email's Password", type="password")
        contact  = st.text_input("Enter Phone number")
        submit = st.form_submit_button("Submit")

    if submit:
        user_prompt = system_prompt + " Write a very human email to " + to + " for the reason of: " + reason + ". My name is " + name + ". My Contact is " + contact
        st.session_state['output'] = AI(user_prompt=user_prompt)
        st.session_state['submitted'] = True
else:
    st.write(st.session_state['output'])
    col1, col2 = st.columns(2)

    with col1:
        send = st.button("Send Mail")
    
    with col2:
        notsend = st.button("Redo")
    
    if send:
        sendMail(st.session_state['email'], st.session_state['pw'], st.session_state['to_email'], st.session_state['output'])

    if notsend:
        st.session_state['submitted'] = False
