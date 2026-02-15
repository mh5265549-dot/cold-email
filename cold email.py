import streamlit as st
import os
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import ScrapeWebsiteTool
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Cold Email Generator", page_icon="📧", layout="wide")

# Dark theme CSS with Comic Sans font
st.markdown("""
<style>
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
        font-family: 'Comic Sans MS', 'Comic Sans', 'Chalkboard SE', 'Comic Neue', cursive, sans-serif;
    }
    html, body, [class*="css"] {
        font-family: 'Comic Sans MS', 'Comic Sans', 'Chalkboard SE', 'Comic Neue', cursive, sans-serif;
    }
    h1 {
        font-family: 'Comic Sans MS', 'Comic Sans', cursive;
        font-weight: 700;
        font-size: 2.5rem;
    }
    h2, h3, h4, h5, h6 {
        font-family: 'Comic Sans MS', 'Comic Sans', cursive;
        font-weight: 600;
    }
    p, div, span, label {
        font-family: 'Comic Sans MS', 'Comic Sans', cursive;
        font-weight: 400;
    }
    .stTextInput > div > div > input {
        font-family: 'Comic Sans MS', 'Comic Sans', cursive;
        font-size: 1rem;
    }
    .stButton > button {
        font-family: 'Comic Sans MS', 'Comic Sans', cursive;
        font-weight: 700;
        font-size: 1rem;
    }
    .stTextInput > div > div > input {
        background-color: #21262d;
        color: #c9d1d9;
        border: 1px solid #30363d;
    }
    .stTextInput > label {
        color: #c9d1d9;
    }
    .stMarkdown {
        color: #c9d1d9;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #f0f6fc !important;
    }
    .stSidebar {
        background-color: #161b22;
    }
    .stSidebar .stMarkdown {
        color: #c9d1d9;
    }
    .stButton > button {
        background-color: #238636;
        color: white;
        border: none;
    }
    .stButton > button:hover {
        background-color: #2ea043;
    }
    .stInfo {
        background-color: #21262d;
        border: 1px solid #30363d;
        color: #c9d1d9;
    }
    .stSuccess {
        background-color: #238636;
        color: white;
    }
    .stError {
        background-color: #da3633;
        color: white;
    }
    .stTabs [data-baseweb="tab-list"] {
        background-color: #161b22;
    }
    .stTabs [data-baseweb="tab"] {
        color: #c9d1d9;
    }
    .stTabs [aria-selected="true"] {
        background-color: #21262d;
        color: #f0f6fc;
    }
    .stStatus {
        background-color: #21262d;
    }
    .stSpinner > div {
        border-top-color: #58a6ff;
    }
</style>
""", unsafe_allow_html=True)

st.title("📧 AI Cold Email Generator")
st.markdown("Enter a company URL and we'll analyze their business, identify pain points, and generate a personalized cold email pitch.")

api_key = os.getenv("GROQ_API_KEY")

llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    api_key=api_key,
    temperature=0.7,
    max_tokens=4096
)

agency_services = """
1. SEO Optimization Service: Best for companies with good products but low traffic. We increase organic reach.
2. Custom Web Development: Best for companies with outdated, ugly, or slow websites. We build modern React/Python sites.
3. AI Automation: Best for companies with manual, repetitive tasks. We build agents to save time.
"""

with st.sidebar:
    st.header("⚙️ Configuration")
    st.markdown("**Our Services:**")
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

if st.button("🚀 Generate Cold Email", type="primary", use_container_width=True):
    if not target_url.strip():
        st.error("Please enter a valid URL!")
    else:
        scrape_tool = ScrapeWebsiteTool()

        researcher = Agent(
            role='Business Intelligence Analyst',
            goal='Analyze the target company website and identify their core business and potential weaknesses.',
            backstory="You are an expert at analyzing businesses just by looking at their landing page. You look for what they do and where they might be struggling.",
            tools=[scrape_tool],
            llm=llm,
            verbose=False,
            allow_delegation=True,
            memory=True
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
            memory=True,
        )

        writer = Agent(
            role='Senior Sales Copywriter',
            goal='Write a personalized cold email that sounds human and professional.',
            backstory="""You write emails that get replies. You never sound robotic.
            You mention specific details found by the Researcher to prove we actually looked at their site.""",
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

        with st.status("🔍 Analyzing company website...", expanded=True) as status:
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
            task_write = Task(
                description=f"Draft a cold email to {recipient} of the target company. Pitch the selected service. Keep it under 150 words.",
                expected_output="A professional cold email body.",
                agent=writer,
                context=[task_analyze, task_strategize]
            )

            task_finalize = Task(
                description="""Take the drafted email and finalize it for sending:
                1. Create a compelling subject line (max 50 characters)
                2. Add a professional greeting
                3. Include the email body
                4. Add a clear call-to-action
                5. Add a professional signature with contact info placeholder
                Format the complete email ready to be sent.""",
                expected_output="A complete, formatted email with subject line, greeting, body, CTA, and signature ready to send.",
                agent=email_finalizer,
                context=[task_write]
            )

            sales_crew = Crew(
                agents=[researcher, strategist, writer, email_finalizer],
                tasks=[task_analyze, task_strategize, task_write, task_finalize],
                process=Process.sequential,
                verbose=False,
                memory=False
            )

            result = sales_crew.kickoff()
            status.update(label="✅ Analysis complete!", state="complete")

        st.success("🎉 Cold email generated successfully!")
        st.markdown("---")

        tab1, tab2, tab3 = st.tabs(["📧 Final Email", "📊 Full Analysis", "📤 Send Email"])

        with tab1:
            st.markdown("### Your Personalized Cold Email")
            st.info(result.raw)

            col_copy, col_space = st.columns([1, 3])
            with col_copy:
                st.download_button(
                    "📋 Download Email",
                    data=result.raw,
                    file_name="cold_email.txt",
                    mime="text/plain"
                )

        with tab2:
            st.markdown("### Complete Crew Output")
            st.write(result.raw)

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
