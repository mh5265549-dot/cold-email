import streamlit as st
import os
import smtplib
import re
import json
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import ScrapeWebsiteTool
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Cold Email Generator", page_icon="📧", layout="wide")

if 'email_history' not in st.session_state:
    st.session_state.email_history = []
if 'templates' not in st.session_state:
    st.session_state.templates = {
        "Professional": "Formal business tone",
        "Friendly": "Casual and approachable",
        "Aggressive": "Direct and compelling",
        "Short & Sweet": "Brief and to the point"
    }
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True

# Dynamic theme CSS
theme_css = """
<style>
    .stApp {
        font-family: 'Comic Sans MS', 'Comic Sans', 'Chalkboard SE', 'Comic Neue', cursive, sans-serif;
        transition: all 0.3s ease;
    }
    html, body, [class*="css"] {
        font-family: 'Comic Sans MS', 'Comic Sans', 'Chalkboard SE', 'Comic Neue', cursive, sans-serif;
    }
    h1 {
        font-family: 'Comic Sans MS', 'Comic Sans', cursive;
        font-weight: 700;
        font-size: 2.5rem;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    h2, h3, h4, h5, h6 {
        font-family: 'Comic Sans MS', 'Comic Sans', cursive;
        font-weight: 600;
    }
    .stTextInput > div > div > input {
        font-family: 'Comic Sans MS', 'Comic Sans', cursive;
        font-size: 1rem;
        border-radius: 10px;
    }
    .stButton > button {
        font-family: 'Comic Sans MS', 'Comic Sans', cursive;
        font-weight: 700;
        font-size: 1rem;
        border-radius: 20px;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    .agent-card {
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid;
    }
    .progress-container {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
    }
    .feature-icon {
        font-size: 2rem;
        margin-right: 10px;
    }
    .email-preview {
        background: #f6f8fa;
        border: 1px solid #e1e4e8;
        border-radius: 10px;
        padding: 20px;
        font-family: 'Courier New', monospace;
    }
</style>
"""
st.markdown(theme_css, unsafe_allow_html=True)

st.title("📧 AI Cold Email Generator")
st.markdown("Enter a company URL and we'll analyze their business, identify pain points, and generate a personalized cold email pitch.")

with st.sidebar:
    st.header("🎨 Appearance")
    dark_mode = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
    if dark_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode
        st.rerun()
    
    st.markdown("---")
    st.header("🔑 API Configuration")
    api_key = st.text_input(
        "Enter your Groq API Key:",
        type="password",
        placeholder="gsk_...",
        help="Get your API key from https://console.groq.com/keys"
    )
    
    st.markdown("---")
    st.header("⚙️ AI Settings")
    
    model_option = st.selectbox(
        "🤖 Select Model:",
        ["groq/llama-3.3-70b-versatile", "groq/llama-3.1-8b-instant", "groq/mixtral-8x7b-32768"],
        index=0
    )
    
    temperature = st.slider(
        "🌡️ Temperature (Creativity):",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Higher = more creative, Lower = more focused"
    )
    
    email_tone = st.selectbox(
        "🎭 Email Tone:",
        ["Professional", "Friendly", "Aggressive", "Short & Sweet"],
        index=0
    )
    
    email_length = st.select_slider(
        "📏 Email Length:",
        options=["Short", "Medium", "Long"],
        value="Medium"
    )
    
    language = st.selectbox(
        "🌍 Language:",
        ["English", "Spanish", "French", "German", "Portuguese"],
        index=0
    )
    
    st.markdown("---")
    st.header("📋 Templates")
    selected_template = st.selectbox(
        "Choose a template:",
        list(st.session_state.templates.keys())
    )
    st.caption(st.session_state.templates[selected_template])
    
    st.markdown("---")
    st.markdown("**Don't have an API key?**")
    st.markdown("[Get one free from Groq](https://console.groq.com/keys)")

if not api_key:
    st.info("👈 Please enter your Groq API key in the sidebar to get started.")
    st.stop()

if not api_key.startswith("gsk_"):
    st.sidebar.error("❌ Invalid API key format!")
    st.error("⚠️ The API key is wrong! Please type the correct API key. It should start with 'gsk_'")
    st.stop()

try:
    llm = LLM(
        model=model_option,
        api_key=api_key,
        temperature=temperature,
        max_tokens=4096
    )
    st.sidebar.success("✅ API key validated!")
except Exception as e:
    st.sidebar.error("❌ Invalid API key!")
    st.error("⚠️ The API key is wrong! Please type the correct API key.")
    st.stop()

agency_services = """
1. SEO Optimization Service: Best for companies with good products but low traffic. We increase organic reach.
2. Custom Web Development: Best for companies with outdated, ugly, or slow websites. We build modern React/Python sites.
3. AI Automation: Best for companies with manual, repetitive tasks. We build agents to save time.
"""

with st.sidebar:
    st.header("⚙️ Our Services")
    st.markdown(agency_services)
    st.markdown("---")
    st.caption("Powered by CrewAI + Groq")

col1, col2 = st.columns([2, 1])

with col1:
    target_url = st.text_input(
        "🌐 Target Company URL",
        placeholder="https://example.com",
        help="Enter the website URL of the company you want to pitch"
    )

with col2:
    recipient_name = st.text_input(
        "👤 Recipient Name (Optional)",
        placeholder="CEO or specific person",
        help="Who should the email be addressed to?"
    )

st.markdown("---")
st.markdown("### 🤖 Our AI Team")
col_agent1, col_agent2, col_agent3, col_agent4 = st.columns(4)
with col_agent1:
    st.metric("🔍 Researcher", "Analyzing", delta="Ready")
with col_agent2:
    st.metric("🎯 Strategist", "Planning", delta="Ready")
with col_agent3:
    st.metric("✍️ Writer", "Creating", delta="Ready")
with col_agent4:
    st.metric("📤 Sender", "Finalizing", delta="Ready")

if st.button("🚀 Generate Cold Email", type="primary", use_container_width=True):
    if not target_url.strip():
        st.error("Please enter a valid URL!")
    else:
        scrape_tool = ScrapeWebsiteTool()
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        length_words = {"Short": "100", "Medium": "200", "Long": "350"}
        
        researcher = Agent(
            role='Business Intelligence Analyst',
            goal='Analyze the target company website and identify their core business and potential weaknesses.',
            backstory="You are an expert at analyzing businesses just by looking at their landing page. You look for what they do and where they might be struggling.",
            tools=[scrape_tool],
            llm=llm,
            verbose=False,
            allow_delegation=True,
            memory=False
        )

        strategist = Agent(
            role='Agency Strategist',
            goal='Match the target company needs with ONE of our agency services.',
            backstory=f"""You work for a top-tier digital agency.
Your goal is to read the analysis of a prospect and decide which of OUR services to pitch.

OUR SERVICES KNOWLEDGE BASE:
{agency_services}

You must pick the SINGLE best service for this specific client and explain why.""",
            llm=llm,
            verbose=False,
            memory=False,
        )

        writer = Agent(
            role='Senior Sales Copywriter',
            goal=f'Write a {email_tone.lower()} cold email that sounds human and professional in {language}.',
            backstory=f"""You write emails that get replies. You never sound robotic.
            You mention specific details found by the Researcher to prove we actually looked at their site.
            Use a {email_tone} tone and write in {language}.""",
            llm=llm,
            verbose=False
        )

        email_finalizer = Agent(
            role='Email Campaign Manager',
            goal='Finalize and prepare the email for delivery with proper formatting and send-off.',
            backstory="""You are an expert email campaign manager. Your job is to take drafted emails and:
            1. Add a professional subject line
            2. Format the email properly with greeting and signature
            3. Add a compelling call-to-action
            4. Prepare the final version ready to be sent
            You ensure every email is polished and ready for delivery.""",
            llm=llm,
            verbose=False
        )

        with st.status("🎯 Processing your request...", expanded=True) as status:
            task_analyze = Task(
                description=f"Scrape the website {target_url}. Summarize what the company does and identify 1 key area where they could improve (e.g., design, traffic, automation).",
                expected_output="A brief summary of the company and their potential pain points.",
                agent=researcher
            )

            task_strategize = Task(
                description="Based on the analysis, pick ONE service from our Agency Knowledge Base that solves their problem. Explain the match.",
                expected_output="The selected service and the reasoning for the match.",
                agent=strategist,
                context=[task_analyze]
            )

            recipient = recipient_name if recipient_name.strip() else "the CEO"
            progress_bar.progress(25)
            status_text.text("🔍 Researcher: Analyzing website...")
            
            task_write = Task(
                description=f"Draft a {email_tone.lower()} cold email to {recipient} of the target company in {language}. Use the {selected_template} template style. Pitch the selected service. Keep it around {length_words[email_length]} words.",
                expected_output=f"A {email_tone.lower()} cold email body in {language}.",
                agent=writer,
                context=[task_analyze, task_strategize]
            )

            progress_bar.progress(50)
            status_text.text("✍️ Writer: Creating email content...")

            task_finalize = Task(
                description=f"""Take the drafted email and finalize it for sending in {language}:
                1. Create a compelling subject line (max 50 characters)
                2. Add a professional greeting
                3. Include the email body ({email_tone} tone)
                4. Add a clear call-to-action
                5. Add a professional signature with contact info placeholder
                Format the complete email ready to be sent.""",
                expected_output="A complete, formatted email with subject line, greeting, body, CTA, and signature ready to send.",
                agent=email_finalizer,
                context=[task_write]
            )

            progress_bar.progress(75)
            status_text.text("📤 Finalizer: Polishing email...")

            sales_crew = Crew(
                agents=[researcher, strategist, writer, email_finalizer],
                tasks=[task_analyze, task_strategize, task_write, task_finalize],
                process=Process.sequential,
                verbose=False,
                memory=False
            )

            result = sales_crew.kickoff()
            progress_bar.progress(100)
            status_text.text("✅ Complete!")
            status.update(label="✅ Email generated successfully!", state="complete")
            
            st.session_state.email_history.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "url": target_url,
                "tone": email_tone,
                "language": language,
                "email": result.raw
            })

        st.success("🎉 Cold email generated successfully!")
        st.markdown("---")

        tab1, tab2, tab3, tab4 = st.tabs(["📧 Final Email", "📊 Full Analysis", "📤 Send Email", "📜 History"])

        with tab1:
            st.markdown("### Your Personalized Cold Email")
            
            col_copy1, col_copy2, col_space = st.columns([1, 1, 2])
            with col_copy1:
                st.download_button(
                    "📋 Download",
                    data=result.raw,
                    file_name="cold_email.txt",
                    mime="text/plain"
                )
            with col_copy2:
                if st.button("📄 Copy to Clipboard"):
                    st.write("<script>navigator.clipboard.writeText(`" + result.raw.replace('`', '\\`') + "`)</script>", unsafe_allow_html=True)
                    st.toast("✅ Copied to clipboard!")
            
            with st.container():
                st.markdown("#### Gmail Preview:")
                st.markdown(f"""
                <div style="background: #f6f8fa; border: 1px solid #e1e4e8; border-radius: 10px; padding: 20px; font-family: Arial, sans-serif;">
                    <pre style="white-space: pre-wrap; word-wrap: break-word; margin: 0;">{result.raw}</pre>
                </div>
                """, unsafe_allow_html=True)

        with tab2:
            st.markdown("### Complete Crew Output")
            st.write(result.raw)
            
            st.markdown("### 📊 Generation Details")
            detail_col1, detail_col2, detail_col3, detail_col4 = st.columns(4)
            with detail_col1:
                st.metric("Tone", email_tone)
            with detail_col2:
                st.metric("Language", language)
            with detail_col3:
                st.metric("Length", email_length)
            with detail_col4:
                st.metric("Template", selected_template)

        with tab3:
            st.markdown("### 📤 Send Email")
            st.info("Enter your email credentials to send the email directly.")
            
            with st.form("email_send_form"):
                sender_email = st.text_input("Your Email (Gmail)", placeholder="your.email@gmail.com")
                sender_password = st.text_input("Your App Password", type="password", 
                    help="Use Gmail App Password, not your regular password. Get it from Google Account > Security > 2-Step Verification > App passwords")
                recipient_email = st.text_input("Recipient Email", placeholder="ceo@company.com")
                
                send_button = st.form_submit_button("🚀 Send Email Now", type="primary")
                
                if send_button:
                    if not sender_email or not sender_password or not recipient_email:
                        st.error("Please fill in all email fields!")
                    elif not re.match(r'^[^@]+@[^@]+\.[^@]+$', recipient_email):
                        st.error("Please enter a valid recipient email address!")
                    else:
                        with st.spinner("Sending email..."):
                            try:
                                msg = MIMEMultipart()
                                msg['From'] = sender_email
                                msg['To'] = recipient_email
                                
                                email_content = result.raw
                                lines = email_content.split('\n')
                                subject = "Cold Email Pitch"
                                body = email_content
                                
                                for line in lines:
                                    if line.lower().startswith('subject:'):
                                        subject = line.replace('Subject:', '').replace('subject:', '').strip()
                                        body = '\n'.join(lines[lines.index(line)+1:]).strip()
                                        break
                                
                                msg['Subject'] = subject
                                msg.attach(MIMEText(body, 'plain'))
                                
                                server = smtplib.SMTP('smtp.gmail.com', 587)
                                server.starttls()
                                server.login(sender_email, sender_password)
                                server.send_message(msg)
                                server.quit()
                                
                                st.success(f"✅ Email sent successfully to {recipient_email}!")
                                st.balloons()
                            except Exception as e:
                                st.error(f"❌ Failed to send email: {str(e)}")
                                st.info("💡 Tip: Make sure you're using a Gmail App Password, not your regular Gmail password.")

        with tab4:
            st.markdown("### 📜 Email History")
            if st.session_state.email_history:
                for idx, item in enumerate(reversed(st.session_state.email_history)):
                    with st.expander(f"📧 {item['timestamp']} - {item['url'][:40]}..."):
                        st.markdown(f"**Tone:** {item['tone']} | **Language:** {item['language']}")
                        st.text_area("Email Content", item['email'], height=200, key=f"history_{idx}")
                        if st.button(f"Load This Email", key=f"load_{idx}"):
                            st.info("Feature: Click to reload this email into the editor")
                
                if st.button("🗑️ Clear History"):
                    st.session_state.email_history = []
                    st.rerun()
            else:
                st.info("No emails generated yet. Create your first cold email!")

st.markdown("---")
st.caption("🚀 Powered by CrewAI + Groq | Made with ❤️ using Streamlit")
