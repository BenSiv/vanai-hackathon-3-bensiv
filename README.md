# vanai-hackathon-3-bensiv

## Team: Ben Sivan

---

## Project Overview

This project focuses on analyzing a comprehensive AI survey dataset. I structured the raw survey data into a relational database, explored key questions, and extracted meaningful insights from both structured and open-ended responses.

---

## Progress So Far

- **Dataset Exploration:**  
  I explored the dataset to understand its structure, key variables, and response patterns.

- **Database Construction:**  
  I cleaned the raw CSV survey data and imported it into a SQLite database (`data/ai_survey.db`) for efficient querying and analysis.

- **Research Questions Formulation:**  
  I identified relevant questions that the dataset can help answer, such as trends in AI adoption, sentiment analysis, and demographic influences.

- **Insights Extraction:**  
  Using Python scripts and language models, I analyzed open-ended responses, summarized common themes, and generated word clouds (`plot/wordcloud_all_open_ended.png` and `plot/wordcloud_summary.png`).

- **Proof of Concept App Development:**  
  I developed an initial interactive AI Navigator app as a proof of concept using Python and Flask. The app helps users explore AI innovations, discover relevant AI tools, and addresses common misconceptions through a myth-busting FAQ.  
  The app is containerized with Podman, ensuring easy deployment and access via mapped ports.

---

## Product Idea: AI Navigator — Your Personal Guide to AI Innovation

I am building **AI Navigator**, an interactive app designed to help users confidently explore the complex AI landscape, understand innovations, and discover the right tools tailored to their unique needs.

The app aims to:

- Empower users by simplifying AI concepts and showcasing practical applications.  
- Alleviate fears and misconceptions by providing clear, trustworthy information and real-world use cases.  
- Personalize guidance to help users find AI tools and technologies relevant to their industry, role, or project goals.  
- Enable actionable insights so users can adopt AI solutions effectively and with confidence.

This product bridges the gap between complex AI technologies and user needs, making AI accessible, relatable, and actionable.

![AI Navigator Demo](docs/demo.gif)

---

## Next Steps

- Enhance the AI Navigator app with richer interactivity, personalized recommendations, and integration of survey insights.  
- Expand the app’s content with curated learning resources and community stories to further alleviate fears around AI adoption.  
- Develop a robust containerization and deployment strategy for easy scaling and sharing.  
- Prepare the final presentation and submit the project.
