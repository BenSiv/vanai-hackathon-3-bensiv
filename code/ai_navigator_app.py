import streamlit as st

def main():
    st.title("AI Navigator — Your Guide to AI Innovation")
    st.write("Explore AI innovations and find the right tools for your needs.")

    # Step 1: Select Industry/Role
    industries = {
        "Healthcare": [
            "AI-powered diagnostics",
            "Patient data analytics",
            "Virtual health assistants"
        ],
        "Education": [
            "Personalized learning platforms",
            "Automated grading",
            "AI tutors and chatbots"
        ],
        "Marketing": [
            "Customer segmentation using AI",
            "Content generation tools",
            "Sentiment analysis on social media"
        ],
        "General": [
            "AI adoption and automation tools",
            "Natural Language Processing",
            "Computer Vision applications"
        ]
    }

    industry = st.selectbox("Select your industry or role:", list(industries.keys()))

    st.subheader("AI Innovations Relevant to You")
    for item in industries[industry]:
        st.write(f"- {item}")

    # Step 2: Select User Need
    needs = {
        "Automation": ["UiPath", "Automation Anywhere", "Microsoft Power Automate"],
        "Analysis": ["Tableau with AI integrations", "Google Cloud AI Platform", "IBM Watson Analytics"],
        "Customer Engagement": ["ChatGPT", "Zendesk AI", "HubSpot AI"],
        "General": ["Azure AI", "AWS AI", "Google AI Platform"]
    }

    need = st.selectbox("What is your main AI need?", list(needs.keys()))

    st.subheader("Recommended AI Tools for Your Need")
    for tool in needs[need]:
        st.write(f"- {tool}")

    # Step 3: Myth Busting FAQ
    if st.checkbox("Show AI Myth Busting FAQ"):
        st.markdown("""
        **AI Myth Busting:**
        - AI will replace all human jobs: *AI is designed to augment human work, not replace it completely.*  
        - AI is only for big companies: *Many accessible AI tools exist for small businesses and individuals.*  
        - AI decisions are always unbiased: *AI can reflect biases in data; transparency is key.*  
        """)

    st.write("---")
    st.write("Thank you for exploring AI Navigator! Stay curious and empowered.")

if __name__ == "__main__":
    main()
