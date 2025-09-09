import streamlit as st
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(page_title="Automation Toolkit GS/ORS3-IN", layout="wide")
st.markdown("<h1 style='text-align: center;'>Welcome to the Automation Toolkit 🧰</h1>", unsafe_allow_html=True)


# Inject custom CSS for equal-height cards

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.markdown("### 🧾 BRC Tool")
        st.markdown("""
        Generate **Business Role Catalog** reports to audit access rights and role compliance.  
        Designed to help keep access permissions clean and aligned.

        """)
        st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)
        if st.button("Let's Get Started", key="brc"):
            st.switch_page("pages/2_BRC.py")

with col2:
    with st.container(border=True):
        st.markdown("### 🔄 Movers Check")
        st.markdown("""
        This tool helps automate checking who’s responsible for specific movers in the system.
        Automatically generate movers check reports with just a few clicks.  

        """)
        st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)
        if st.button("Let's Get Started", key="movers"):
            st.switch_page("pages/1_Movers_Check.py")

with col3:
    with st.container(border=True):
        st.markdown("### 📊 UAD Merger")
        st.markdown("""
        Merge multiple **User Access Data (UAD)** Excel files into a single structured report.  
        Simplifies data for starting the manual workflows in RAC process.

        """)
        st.markdown("<div style='height:40px;'></div>", unsafe_allow_html=True)
        if st.button("Let's Get Started", key="uad"):
            st.switch_page("pages/3_UAD_Consolidation.py")

# Sticky footer with custom styling
st.markdown("""
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        color: #6c757d;
        text-align: center;
        padding: 5px;
        font-size: 14px;
        box-shadow: 0 -1px 3px rgba(0,0,0,0.1);
        z-index: 100;
    }
    </style>

    <div class="footer">
        © 2025 Automation Toolkit | Bosch Internal Tool | Feedback or ideas? Reach out to Shashank Joshi (GS/ORS3-IN)
    </div>
""", unsafe_allow_html=True)

# Add floating chatbot icon (redirect link)
chatbot_url = "https://gsaccessmanagement.azurewebsites.net "  # Replace with actual URL

chatbot_icon_html = f"""
    <div style="position: fixed; bottom: 80px; right: 30px; z-index: 9999;">
        <a href="{chatbot_url}" target="_blank">
            <img src="https://cdn-icons-png.flaticon.com/512/4712/4712027.png"
                 alt="Chatbot" title="Ask our Chatbot"
                 style="width: 60px; height: 60px; border-radius: 50%; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
        </a>
    </div>
"""
st.markdown(chatbot_icon_html, unsafe_allow_html=True)