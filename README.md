🏛️ Academic Writing Studio

Academic Writing Studio is a powerful, locally-hosted research and writing environment designed specifically for academics, urban planners, and researchers. It bridges the gap between drafting manuscripts and conducting complex literature reviews by integrating advanced Natural Language Processing (NLP), multi-source literature crawlers, and a distraction-free word processor into a single, cohesive interface.

Built with Python (Flask) and a vanilla HTML/JS frontend, the application prioritizes a human-like, active academic writing style and keeps your unpublished manuscripts entirely private on your local machine.

✨ Key Features

📝 Professional Writing Environment

MS Word-style Canvas: A highly legible, A4-proportioned editor featuring precise margin controls, deep line-spacing tools, and professional typography (Century Gothic, Times New Roman, Georgia).

Focus Mode & Pomodoro: Toggle "Zen Mode" to hide research panels for distraction-free writing, and utilize the built-in Pomodoro sprint timer to maintain creative flow.

Live Manuscript Metrics: Real-time tracking of word count, character count, and estimated reading time.

Human-like Tone & Grammar Checker: Goes beyond basic spell-check by flagging robotic, clunky academic jargon (e.g., suggesting "using" instead of "the utilization of") to encourage a natural, active voice.

Tense-Compliant Synonyms: Highlight any word to get extensive, context-aware synonyms. The NLTK-powered lemmatizer automatically reapplies the correct morphological suffixes (-ing, -ed, -ly, -s) to the generated suggestions.

🔍 Multi-Tier Literature Crawler

Search across the world's leading academic databases directly from your workspace without opening a browser tab.

Supported Engines: Google Scholar, Semantic Scholar, OpenAlex, Crossref, and arXiv.

Advanced Bypassing: Utilizes custom browser-mimicking headers and specific 2-tier fallback algorithms to ensure successful data retrieval.

1-Click APA Citations: Instantly generate and copy APA-formatted citations from your search results straight to your clipboard.

🧠 Semantic PDF Mindmap (NLP Graph)

Stop manually highlighting PDFs. Upload multiple papers and let the custom NLP engine build a visual, interactive network graph of the literature.

Noun-Phrase Extraction: Uses NLTK Part-of-Speech (POS) tagging to isolate complex academic concepts (Adjective + Noun chains) rather than generic keywords.

Similarity Mapping (Green Nodes): Uses TF-IDF vector math to connect papers that share highly specific methodological or thematic focuses.

Differentiating Insights (Orange Nodes): Employs absolute-absence logic to highlight what one paper deeply explores that another entirely lacks.

Contextual Gap Analysis (Red Nodes): Dynamically extracts the exact syntactic clauses where authors state their limitations or directions for future research.

🛠️ Tech Stack

Backend: Python 3.x, Flask

NLP & Data Science: NLTK (WordNet, POS Taggers), Scikit-Learn (TF-IDF, Cosine Similarity), NumPy

Scraping & Parsing: Requests, BeautifulSoup4, PyPDF2

Frontend: HTML5, CSS3 (CSS Variables for Light/Dark Mode), Vanilla JavaScript, FontAwesome 6

Data Visualization: Vis.js (Network Graphs)

🚀 Installation & Setup

Because Academic Writing Studio runs locally, your data remains completely private.

1. Prerequisites

Ensure you have Python 3.8+ installed on your system.

2. Install Required Packages

Run the following command in your terminal to install the necessary Python libraries:

pip install flask requests beautifulsoup4 nltk PyPDF2 scikit-learn numpy


3. Run the Application

Navigate to the directory containing GWriter.py and run:

python GWriter.py


Note: On the very first run, the app will automatically download the necessary NLTK corpora (WordNet, Punkt, Averaged Perceptron Tagger) in the background.

4. Open in Browser

Once the server is running, open your preferred web browser and navigate to:

[http://127.0.0.1:5000](http://127.0.0.1:5000)


💡 How to Use

Drafting: Start typing in the central canvas. Use the + Insert Academic Phrase dropdown to overcome writer's block with discipline-specific transitional phrases.

Finding Sources: Open the "Literature Crawler" tab on the right, enter your research topic, select a database (e.g., Google Scholar), and click Search. Click Cite (APA) to instantly grab the reference.

Mapping PDFs: Download relevant PDFs from the crawler. Switch to the "Mindmap Graph" tab, click Upload & Analyze Multiple PDFs, select your downloaded papers, and wait for the NLP engine to draw the conceptual relationships and research gaps.

Saving: Click the Save (.aws) button in the header. This generates a .aws JSON file containing your entire editor content, PDF notes, and Mindmap state to your local downloads folder. You can resume later using the Load (.aws) button.

🤝 Contributing

Contributions, issues, and feature requests are welcome!
If you are an academic, developer, or NLP enthusiast looking to improve the extraction algorithms or add new citation formats, feel free to fork the repository and submit a pull request.

📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
