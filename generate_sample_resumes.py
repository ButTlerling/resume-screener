"""
Generates 100 sample student/new-grad resume PDFs in 'sample_resumes/'.
Diverse majors: STEM, partial-fit, and non-STEM.
Run: python generate_sample_resumes.py
Requires: pip install fpdf2
"""

import os
import random
from fpdf import FPDF

OUTPUT_DIR = "sample_resumes"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Name pools
# ---------------------------------------------------------------------------

FIRST_NAMES = [
    "James", "Maria", "David", "Sarah", "Michael", "Emily", "Robert", "Jessica",
    "William", "Ashley", "Daniel", "Amanda", "Matthew", "Stephanie", "Andrew",
    "Jennifer", "Joshua", "Megan", "Ryan", "Lauren", "Kevin", "Rachel", "Brian",
    "Hannah", "Jason", "Nicole", "Tyler", "Samantha", "Nathan", "Emma",
    "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia", "Mason", "Isabella",
    "Logan", "Mia", "Lucas", "Charlotte", "Aiden", "Amelia", "Jackson", "Harper",
    "Priya", "Wei", "Yuna", "Arjun", "Fatima", "Carlos", "Mei", "Omar",
    "Zoe", "Eli", "Nadia", "Rafael", "Soren", "Layla", "Kai", "Elena",
    "Grace", "Owen", "Chloe", "Ethan", "Lily", "Sebastian", "Aria", "Jack",
    "Penelope", "Henry", "Scarlett", "Alexander", "Victoria", "Benjamin", "Aurora",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Wilson", "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris",
    "Martin", "Thompson", "Martinez", "Robinson", "Clark", "Rodriguez", "Lewis",
    "Lee", "Walker", "Hall", "Allen", "Young", "Hernandez", "King", "Wright",
    "Patel", "Chen", "Kim", "Nguyen", "Singh", "Okafor", "Fernandez", "Mueller",
    "Tanaka", "Kowalski", "Dubois", "Petrov", "Hassan", "Johansson", "Park",
    "O'Brien", "Ramirez", "Carter", "Mitchell", "Perez", "Roberts", "Turner",
    "Phillips", "Campbell", "Parker", "Evans", "Edwards", "Collins", "Stewart",
]

UNIVERSITIES = [
    ("MIT", "Cambridge, MA"),
    ("Stanford University", "Stanford, CA"),
    ("Carnegie Mellon University", "Pittsburgh, PA"),
    ("UC Berkeley", "Berkeley, CA"),
    ("University of Washington", "Seattle, WA"),
    ("Georgia Tech", "Atlanta, GA"),
    ("University of Michigan", "Ann Arbor, MI"),
    ("Cornell University", "Ithaca, NY"),
    ("Columbia University", "New York, NY"),
    ("UCLA", "Los Angeles, CA"),
    ("UT Austin", "Austin, TX"),
    ("Purdue University", "West Lafayette, IN"),
    ("University of Illinois Urbana-Champaign", "Urbana, IL"),
    ("NYU", "New York, NY"),
    ("Boston University", "Boston, MA"),
    ("University of Southern California", "Los Angeles, CA"),
    ("Duke University", "Durham, NC"),
    ("Johns Hopkins University", "Baltimore, MD"),
    ("University of Wisconsin-Madison", "Madison, WI"),
    ("Penn State University", "State College, PA"),
    ("Arizona State University", "Tempe, AZ"),
    ("Northeastern University", "Boston, MA"),
    ("Virginia Tech", "Blacksburg, VA"),
    ("UC San Diego", "La Jolla, CA"),
    ("Ohio State University", "Columbus, OH"),
    ("University of Minnesota", "Minneapolis, MN"),
    ("Indiana University", "Bloomington, IN"),
    ("University of Florida", "Gainesville, FL"),
    ("University of North Carolina", "Chapel Hill, NC"),
    ("Georgetown University", "Washington, DC"),
    ("American University", "Washington, DC"),
    ("University of Denver", "Denver, CO"),
    ("Fordham University", "New York, NY"),
    ("DePaul University", "Chicago, IL"),
    ("San Jose State University", "San Jose, CA"),
    ("Cal Poly San Luis Obispo", "San Luis Obispo, CA"),
    ("Rochester Institute of Technology", "Rochester, NY"),
    ("Drexel University", "Philadelphia, PA"),
    ("Tulane University", "New Orleans, LA"),
    ("University of Miami", "Coral Gables, FL"),
]

# ---------------------------------------------------------------------------
# Major category definitions
# Each entry: (major_name, category, fit_level)
#   fit_level: "strong" | "partial" | "weak"
# ---------------------------------------------------------------------------

MAJORS = {
    # -- strong fit --
    "Computer Science":         ("cs_ds",    "strong"),
    "Data Science":             ("cs_ds",    "strong"),
    "Computer Engineering":     ("cs_ds",    "strong"),
    "Applied Mathematics":      ("cs_ds",    "strong"),
    "Statistics":               ("cs_ds",    "strong"),
    # -- partial fit --
    "Electrical Engineering":   ("stem_adj", "partial"),
    "Physics":                  ("stem_adj", "partial"),
    "Industrial Engineering":   ("stem_adj", "partial"),
    "Mechanical Engineering":   ("stem_adj", "partial"),
    "Information Systems":      ("stem_adj", "partial"),
    "Economics":                ("stem_adj", "partial"),
    "Business Analytics":       ("stem_adj", "partial"),
    "Cognitive Science":        ("stem_adj", "partial"),
    "Neuroscience":             ("stem_adj", "partial"),
    "Biology (Bioinformatics)": ("stem_adj", "partial"),
    # -- weak / no fit --
    "Marketing":                ("non_stem", "weak"),
    "English":                  ("non_stem", "weak"),
    "Political Science":        ("non_stem", "weak"),
    "History":                  ("non_stem", "weak"),
    "Fine Arts":                ("non_stem", "weak"),
    "Psychology":               ("non_stem", "weak"),
    "Sociology":                ("non_stem", "weak"),
    "Communications":           ("non_stem", "weak"),
    "Finance":                  ("non_stem", "weak"),
    "Nursing":                  ("non_stem", "weak"),
    "Accounting":               ("non_stem", "weak"),
}

# ---------------------------------------------------------------------------
# Skill pools -- per category
# ---------------------------------------------------------------------------

# strong fit
CS_DS_LANGUAGES  = ["Python", "Java", "JavaScript", "TypeScript", "C++", "SQL", "R",
                    "Bash", "Go", "Scala"]
CS_DS_LIBRARIES  = ["Pandas", "NumPy", "Matplotlib", "Seaborn", "Scikit-learn",
                    "TensorFlow", "PyTorch", "Keras", "Flask", "FastAPI", "Django",
                    "Streamlit", "Plotly", "SciPy", "OpenCV", "NLTK", "Hugging Face",
                    "XGBoost", "LightGBM", "openpyxl", "requests"]
CS_DS_TOOLS      = ["Git", "GitHub", "Jupyter", "VS Code", "Linux", "AWS",
                    "GCP", "Azure", "Tableau", "Power BI", "Excel", "PostgreSQL",
                    "MySQL", "MongoDB", "Google Colab", "Anaconda", "Jira"]
CS_DS_DATA       = ["Data Cleaning", "Data Visualization", "Statistical Analysis",
                    "Feature Engineering",
                    "CSV/JSON Processing", "Excel Automation", "Web Scraping",
                    "API Integration", "Regression Analysis",
                    "Classification", "Clustering"]

# EE / Physics / MechE
EE_LANGUAGES     = ["MATLAB", "C", "C++", "Python", "Assembly", "VHDL", "LabVIEW"]
EE_LIBRARIES     = ["NumPy", "SciPy", "Matplotlib", "Pandas", "Control Systems Toolbox"]
EE_TOOLS         = ["MATLAB/Simulink", "Multisim", "LTspice", "Oscilloscope", "Git",
                    "Excel", "Jupyter", "AutoCAD", "SPICE"]
EE_DATA          = ["Signal Processing", "Circuit Simulation", "Data Acquisition",
                    "Statistical Analysis", "MATLAB Scripting", "Embedded Systems"]

# Industrial / Mechanical
IE_ME_LANGUAGES  = ["MATLAB", "Python", "C", "R"]
IE_ME_LIBRARIES  = ["Pandas", "NumPy", "Matplotlib", "SciPy"]
IE_ME_TOOLS      = ["MATLAB", "AutoCAD", "SolidWorks", "ANSYS", "Excel", "Minitab",
                    "Git", "Arena Simulation", "JMP"]
IE_ME_DATA       = ["Statistical Process Control", "Six Sigma", "Simulation Modeling",
                    "Data Analysis", "Root Cause Analysis", "Lean Methods",
                    "Regression Analysis"]

# Info Systems / Business Analytics
IS_BA_LANGUAGES  = ["SQL", "Python", "JavaScript", "VBA"]
IS_BA_LIBRARIES  = ["Pandas", "NumPy", "Matplotlib"]
IS_BA_TOOLS      = ["Tableau", "Power BI", "Excel", "MySQL", "Salesforce", "SAP",
                    "Google Analytics", "Git"]
IS_BA_DATA       = ["Data Visualization", "Dashboard Design", "SQL Querying",
                    "Business Intelligence", "KPI Reporting",
                    "Excel Automation"]

# Economics
ECON_LANGUAGES   = ["R", "Stata", "Python", "SQL"]
ECON_LIBRARIES   = ["ggplot2", "dplyr", "Pandas", "Statsmodels"]
ECON_TOOLS       = ["Excel", "Stata", "R Studio", "SPSS",
                    "Git", "Tableau", "Jupyter"]
ECON_DATA        = ["Econometric Modeling", "Regression Analysis", "Statistical Analysis",
                    "Data Visualization", "Policy Analysis",
                    "Financial Modeling"]

# Cognitive Science / Neuroscience
COGNEURO_LANGUAGES = ["Python", "R", "MATLAB"]
COGNEURO_LIBRARIES = ["NumPy", "SciPy", "Matplotlib", "MNE", "Pandas"]
COGNEURO_TOOLS     = ["SPSS", "E-Prime", "Psychtoolbox", "Excel", "R Studio",
                      "Jupyter", "MATLAB"]
COGNEURO_DATA      = ["EEG/fMRI Analysis", "Statistical Analysis", "Experimental Design",
                      "Survey Analysis", "Literature Review", "Data Collection"]

# Biology / Bioinformatics
BIO_LANGUAGES    = ["Python", "R", "Bash"]
BIO_LIBRARIES    = ["Biopython", "Pandas", "NumPy", "ggplot2", "DESeq2"]
BIO_TOOLS        = ["BLAST", "Galaxy", "Jupyter", "R Studio", "Excel", "Git",
                    "NCBI databases", "Conda"]
BIO_DATA         = ["Genomic Data Analysis", "Sequence Alignment", "Statistical Analysis",
                    "Data Cleaning", "Literature Review", "Pipeline Scripting"]

# Marketing / Communications
MKT_SKILLS_TECH  = ["Excel", "PowerPoint", "Google Analytics",
                    "Canva", "Mailchimp",
                    "Hootsuite", "Word"]
MKT_SKILLS_SOFT  = ["Content Writing", "Campaign Management", "Social Media",
                    "Market Research",
                    "Copywriting", "Event Planning"]

# English / History / Poli Sci / Sociology / Communications
HUMANITIES_TECH  = ["Microsoft Word", "Excel", "PowerPoint", "Google Docs",
                    "Zotero", "WordPress", "Canva"]
HUMANITIES_SOFT  = ["Academic Writing", "Archival Research", "Policy Analysis",
                    "Qualitative Research", "Literature Review", "Public Speaking",
                    "Editing and Proofreading"]

# Psychology
PSYCH_TECH       = ["SPSS", "R", "Excel", "Qualtrics", "SurveyMonkey", "E-Prime",
                    "REDCap", "Google Forms"]
PSYCH_SOFT       = ["Survey Design", "Experimental Design", "Statistical Analysis",
                    "Qualitative Coding", "Literature Review",
                    "Clinical Documentation"]

# Finance / Accounting
FIN_TECH         = ["Excel", "PowerPoint", "QuickBooks", "SAP", "Word", "Salesforce"]
FIN_SOFT         = ["Financial Modeling", "Budgeting", "Forecasting",
                    "GAAP Accounting", "Auditing", "Tax Preparation",
                    "Financial Reporting"]

# Fine Arts
ARTS_TECH        = ["Adobe Photoshop", "Illustrator", "InDesign", "Premiere Pro",
                    "Figma", "Procreate", "Word"]
ARTS_SOFT        = ["Visual Communication", "Graphic Design",
                    "Typography", "Color Theory",
                    "Art Direction", "Portfolio Development"]

# Nursing
NURSING_TECH     = ["Epic EHR", "Meditech", "Excel", "Microsoft Office", "Cerner"]
NURSING_SOFT     = ["Patient Care", "Vital Signs Monitoring", "Medication Administration",
                    "Clinical Documentation", "HIPAA Compliance",
                    "Team Collaboration", "BLS/ACLS Certified"]

# ---------------------------------------------------------------------------
# Courses -- per category
# ---------------------------------------------------------------------------

CS_DS_COURSES = [
    "Data Structures and Algorithms", "Object-Oriented Programming", "Database Systems",
    "Operating Systems", "Machine Learning", "Probability and Statistics",
    "Linear Algebra", "Discrete Mathematics", "Software Engineering",
    "Introduction to AI", "Computer Vision", "Data Mining", "Web Development",
    "Python for Data Science", "Introduction to Data Analysis", "Deep Learning",
    "Natural Language Processing", "Cloud Computing",
]

EE_COURSES = [
    "Circuit Analysis I and II", "Signals and Systems", "Digital Logic Design",
    "Electromagnetic Fields", "Microelectronics", "Control Systems",
    "Embedded Systems Programming", "Power Systems", "Digital Signal Processing",
    "Wireless Communications", "Probability for Engineers", "VLSI Design",
]

IE_ME_COURSES = [
    "Engineering Statistics", "Operations Research", "Supply Chain Management",
    "Manufacturing Processes", "Thermodynamics", "Fluid Mechanics",
    "Engineering Economy", "Quality Control", "Simulation Modeling",
    "Project Management", "CAD/CAM", "Mechanics of Materials",
]

IS_BA_COURSES = [
    "Database Management Systems", "Business Intelligence", "Data Warehousing",
    "Systems Analysis and Design", "Enterprise Systems", "Project Management",
    "Business Statistics", "Web Technologies", "IT Strategy", "Data Visualization",
]

ECON_COURSES = [
    "Microeconomics", "Macroeconomics", "Econometrics", "Statistics for Economists",
    "Game Theory", "Public Finance", "Labor Economics", "Development Economics",
    "Financial Economics", "Research Methods in Economics",
]

COGNEURO_COURSES = [
    "Cognitive Psychology", "Neuroscience", "Research Methods",
    "Statistics for Behavioral Sciences", "Sensation and Perception",
    "Human-Computer Interaction", "Language and Cognition", "Brain Imaging",
]

BIO_COURSES = [
    "Bioinformatics", "Genomics", "Molecular Biology", "Computational Biology",
    "Statistics for Life Sciences", "Cell Biology", "Biochemistry",
    "Biostatistics", "Python for Biology",
]

MKT_COURSES = [
    "Principles of Marketing", "Consumer Behavior", "Digital Marketing",
    "Marketing Analytics", "Brand Management", "Advertising",
    "Market Research", "Social Media Strategy", "Public Relations",
    "Integrated Marketing Communications",
]

HUMANITIES_COURSES = [
    "Research Methods", "Academic Writing", "Modern History",
    "Political Theory", "Comparative Politics", "International Relations",
    "American Literature", "Rhetoric and Composition",
    "Sociology of Organizations", "Ethnography",
]

PSYCH_COURSES = [
    "Introduction to Psychology", "Research Methods in Psychology",
    "Statistics for Psychology", "Abnormal Psychology", "Social Psychology",
    "Developmental Psychology", "Cognitive Neuroscience",
    "Clinical Assessment", "Behavioral Neuroscience",
]

FIN_COURSES = [
    "Principles of Finance", "Financial Accounting", "Managerial Accounting",
    "Corporate Finance", "Investments", "Financial Statement Analysis",
    "Auditing", "Tax Accounting", "Fixed Income Securities", "Risk Management",
]

ARTS_COURSES = [
    "Foundations of Studio Art", "Art History", "Graphic Design",
    "Digital Media", "Typography", "Color Theory",
    "Visual Communication", "Portfolio Development", "Exhibition Design",
]

NURSING_COURSES = [
    "Anatomy and Physiology", "Pathophysiology", "Pharmacology",
    "Fundamentals of Nursing", "Medical-Surgical Nursing",
    "Pediatric Nursing", "Community Health Nursing", "Nursing Ethics",
]

MS_COURSES = [
    "Advanced Machine Learning", "Deep Learning", "Natural Language Processing",
    "Distributed Systems", "Big Data Analytics", "Reinforcement Learning",
    "Computer Vision", "Data Engineering", "Cloud Computing", "Optimization Methods",
    "Statistical Learning Theory", "Time Series Forecasting", "Applied Data Science",
]

MBA_MPA_COURSES = [
    "Strategic Management", "Organizational Behavior", "Financial Management",
    "Operations Management", "Marketing Strategy", "Business Analytics",
    "Public Policy Analysis", "Leadership and Ethics",
    "Nonprofit Management", "Data-Driven Decision Making",
]

PHD_COURSES = [
    "Advanced Topics in ML", "Research Seminar: AI/ML", "Convex Optimization",
    "Probabilistic Graphical Models", "Advanced NLP", "Computational Statistics",
    "Information Theory", "Causal Inference", "Deep Generative Models",
]

# ---------------------------------------------------------------------------
# Internship data -- per category
# ---------------------------------------------------------------------------

# CS/DS internship companies
CS_COMPANIES_BIG = [
    "Google", "Microsoft", "Amazon", "Apple", "Meta", "Nvidia", "Intel",
    "Salesforce", "Adobe", "Bloomberg", "Stripe", "Palantir", "Tesla",
    "SpaceX", "LinkedIn", "Airbnb", "Spotify",
]
CS_COMPANIES_MID = [
    "IBM", "Oracle", "Cisco", "VMware", "Qualcomm", "Deloitte (Tech)", "Accenture",
    "HubSpot", "Twilio", "Datadog", "Snowflake", "Databricks", "Booz Allen Hamilton",
    "MITRE Corporation", "Leidos", "SAIC", "Vena Solutions", "Sigma Computing",
    "ThoughtSpot", "Monte Carlo Data", "Scale AI", "Weights and Biases",
    "DataStax", "Airbyte", "Fivetran", "Roboflow", "Labelbox",
]
CS_COMPANIES_SMALL = [
    "local fintech startup", "university research lab", "campus IT department",
    "small SaaS startup", "edtech startup", "health tech startup",
]

CS_ROLES = [
    "Software Engineering Intern", "Data Science Intern", "Machine Learning Intern",
    "Data Engineering Intern", "Analytics Intern", "Backend Engineering Intern",
    "Python Developer Intern", "Business Intelligence Intern", "AI/ML Intern",
    "Research Intern", "Full Stack Intern",
]

# Mundane realistic intern bullets for CS/DS -- used for most students
CS_BULLETS_MUNDANE = [
    "Assisted in writing Python scripts to process CSV data files.",
    "Helped maintain Excel spreadsheets used by the operations team.",
    "Shadowed senior engineers and documented internal processes.",
    "Wrote basic SQL queries to pull weekly reports.",
    "Attended team meetings and took notes for project documentation.",
    "Updated and cleaned data in Excel files provided by the client.",
    "Tested Python scripts written by senior developers and reported bugs.",
    "Helped organize and label datasets for a machine learning project.",
    "Converted a small Excel tracker into a basic Python script under supervision.",
    "Supported the analytics team by running existing scripts and checking outputs.",
    "Looked up documentation and helped a senior developer debug a data pipeline.",
    "Formatted and cleaned a CSV export from the company's CRM system.",
    "Ran a pre-existing data validation script and summarized the results in a spreadsheet.",
    "Helped write a brief internal wiki page explaining how to use a reporting tool.",
    "Sat in on client calls and helped take notes for the project team.",
]

# A few slightly better bullets -- only used for strong-fit seniors
CS_BULLETS_DECENT = [
    "Built a Python script to automate Excel report generation, saving several hours per week.",
    "Developed a small data pipeline using Pandas to process sensor data from CSV files.",
    "Created a basic Tableau dashboard to track weekly KPIs for the team.",
    "Wrote SQL queries on the company database to pull data for a monthly report.",
    "Implemented a simple logistic regression model as a proof-of-concept for churn prediction.",
    "Wrote and ran basic unit tests in pytest for an existing internal Python library.",
    "Scraped public data using requests and BeautifulSoup for a research task.",
    "Built a Jupyter notebook summarizing exploratory analysis on a small customer dataset.",
    "Refactored some legacy Python code to remove hardcoded values and add comments.",
    "Assisted in deploying a small Python script to an internal server.",
]

# EE internship data
EE_COMPANIES = [
    "Boeing", "Lockheed Martin", "Raytheon", "GE", "Siemens", "Honeywell",
    "Garmin", "Trimble", "National Instruments", "Eaton", "Emerson Electric",
    "ABB", "Schneider Electric", "NextEra Energy", "Carrier Global",
    "L3 Technologies", "Texas Instruments", "Analog Devices",
    "Qualcomm", "Intel", "Broadcom",
]

EE_ROLES = [
    "Electrical Engineering Intern", "Hardware Engineering Intern",
    "Embedded Systems Intern", "Power Systems Intern",
    "Signal Processing Intern", "Firmware Engineering Intern",
    "Test Engineering Intern", "Controls Engineering Intern",
]

EE_BULLETS = [
    "Assisted in simulating a low-pass filter in LTspice and compared results to bench measurements.",
    "Helped write basic firmware in C for a microcontroller under senior engineer supervision.",
    "Ran MATLAB scripts to visualize oscilloscope data and flagged anomalies for review.",
    "Assisted in PCB layout review and documented notes from the engineering walkthrough.",
    "Ran automated test scripts written by senior engineers and logged results in Excel.",
    "Updated a MATLAB/Simulink model based on specifications provided by the lead engineer.",
    "Pulled power quality data from a database and organized it in Excel for weekly reports.",
    "Helped set up a data acquisition system and verified sensor readings against expected values.",
    "Maintained and cleaned lab equipment and updated calibration logs in a spreadsheet.",
    "Wrote up test procedure notes and assisted with failure documentation for two prototype units.",
]

# IE/ME internship data
IE_ME_COMPANIES = [
    "GE", "Honeywell", "3M", "Caterpillar", "John Deere", "Parker Hannifin",
    "Cummins", "Ford", "General Motors", "Boeing", "Lockheed Martin",
    "Procter and Gamble", "Johnson and Johnson", "Danaher",
    "Eaton", "IDEX Corporation", "Flowserve", "local manufacturing firm",
]

IE_ME_ROLES = [
    "Manufacturing Engineering Intern", "Industrial Engineering Intern",
    "Process Improvement Intern", "Quality Assurance Intern",
    "Supply Chain Intern", "Operations Research Intern",
    "Mechanical Engineering Intern", "Product Design Intern",
]

IE_ME_BULLETS = [
    "Observed assembly line operations and helped document process steps for the engineering team.",
    "Updated an Excel-based production tracking spreadsheet with daily output data.",
    "Assisted in running an Arena simulation model built by a senior engineer.",
    "Helped create SolidWorks models for a small fixture redesign under supervision.",
    "Compiled supplier quality data into a monthly Excel summary for the QA team.",
    "Assisted in a root cause analysis meeting and took notes for the engineering report.",
    "Measured and recorded dimensions of parts during incoming inspection.",
    "Updated calibration records and SOPs for lab instruments as directed.",
    "Attended daily production stand-ups and tracked action items in a spreadsheet.",
    "Helped a senior engineer prepare slides for a project status presentation.",
]

# IS/Business Analytics internship data
IS_BA_COMPANIES = [
    "Deloitte", "PwC", "EY", "KPMG", "Accenture", "IBM", "SAP",
    "Oracle", "Salesforce", "HubSpot", "Domo", "MicroStrategy",
    "local healthcare system", "retail analytics startup", "logistics company",
]

IS_BA_ROLES = [
    "Business Analyst Intern", "Data Analytics Intern", "BI Analyst Intern",
    "IT Analyst Intern", "Operations Analyst Intern", "Reporting Analyst Intern",
]

IS_BA_BULLETS = [
    "Helped update a Tableau dashboard by adding a new data field as directed.",
    "Wrote basic SQL queries to pull weekly data summaries for the reporting team.",
    "Assisted in reformatting a monthly Excel report to match a new template.",
    "Helped gather requirements for a system update by attending stakeholder meetings.",
    "Updated SharePoint documentation for an internal project.",
    "Helped map out a business process in a flowchart using Visio.",
    "Distributed a Qualtrics survey and compiled responses into an Excel summary.",
    "Maintained and organized a shared project tracking spreadsheet.",
    "Helped train two staff members on a new CRM reporting screen.",
    "Prepared a PowerPoint slide summarizing weekly operational metrics for the team.",
]

# Economics internship data
ECON_COMPANIES = [
    "World Bank", "IMF", "Congressional Budget Office", "Federal Reserve",
    "economic consulting firm", "policy think tank", "state government office",
    "Bloomberg", "Morgan Stanley", "JPMorgan Chase", "Bank of America",
    "Keystone Economic Group", "Analysis Group", "NERA Economic Consulting",
]

ECON_ROLES = [
    "Economic Research Intern", "Policy Research Intern", "Research Analyst Intern",
    "Data Analyst Intern", "Investment Research Intern",
]

ECON_BULLETS = [
    "Downloaded and organized macroeconomic datasets from FRED and World Bank into Excel.",
    "Assisted a senior economist in compiling references for a labor market literature review.",
    "Updated an Excel model with new quarterly GDP figures provided by the research team.",
    "Helped summarize Federal Register filings for the policy team.",
    "Ran basic OLS regressions in Stata following instructions from a senior researcher.",
    "Created simple bar charts in R showing income distribution data for a slide deck.",
    "Fact-checked and formatted sections of a report on housing affordability.",
    "Organized survey data from respondents into a spreadsheet for the research team.",
    "Helped draft a short memo summarizing findings from an assigned policy document.",
]

# Cognitive Science / Neuroscience internship data
COGNEURO_COMPANIES = [
    "university research lab", "NIH research program", "psychology research institute",
    "brain imaging center", "UX research startup", "behavioral science consultancy",
    "local hospital research department",
]

COGNEURO_ROLES = [
    "Research Assistant", "Cognitive Research Intern", "UX Research Intern",
    "Lab Assistant", "Behavioral Research Intern",
]

COGNEURO_BULLETS = [
    "Helped recruit and schedule participants for an EEG study.",
    "Ran quality checks on fMRI data files following a checklist provided by the PI.",
    "Administered standardized cognitive assessments to study participants.",
    "Entered survey responses from paper forms into an Excel spreadsheet.",
    "Assisted with literature search for a project on mindfulness interventions.",
    "Coded video clips using a pre-built coding scheme and logged results in Excel.",
    "Maintained a participant tracking spreadsheet for session scheduling.",
    "Took notes during a usability testing session and helped compile the summary.",
]

# Biology/Bioinformatics internship data
BIO_COMPANIES = [
    "Genentech", "Pfizer", "Merck", "Illumina", "10x Genomics",
    "university genomics core", "NIH research lab", "biotech startup",
    "Broad Institute", "Pacific Biosciences",
]

BIO_ROLES = [
    "Bioinformatics Research Intern", "Computational Biology Intern",
    "Genomics Lab Intern", "Research Intern (Wet Lab)",
]

BIO_BULLETS = [
    "Ran a pre-existing RNA-seq pipeline on new samples following step-by-step instructions.",
    "Wrote a short Python script to rename BLAST output files in a consistent format.",
    "Ran FastQC on sequencing datasets and summarized the quality metrics in a table.",
    "Helped maintain a database of gene variant records in Excel.",
    "Updated an R Markdown report template with new results from the PI's analysis.",
    "Ran alignment jobs on the university HPC cluster using provided SLURM scripts.",
    "Compiled a reading list of papers on CRISPR off-target methods as assigned by the PI.",
    "Helped with routine cell culture maintenance and PCR setup under supervision.",
]

# Marketing / Communications internship data
MKT_COMPANIES = [
    "Ogilvy", "Leo Burnett", "BBDO", "Omnicom Group", "WPP agency",
    "local marketing agency", "consumer goods brand", "e-commerce startup",
    "nonprofit communications team", "media company", "retail chain",
    "real estate marketing firm", "hospital marketing department",
]

MKT_ROLES = [
    "Marketing Intern", "Social Media Intern", "Communications Intern",
    "Content Marketing Intern", "Brand Marketing Intern",
    "PR Intern", "Digital Marketing Intern", "Event Marketing Intern",
]

MKT_BULLETS = [
    "Helped schedule social media posts using a content calendar in Excel.",
    "Drafted a few email newsletter sections in Mailchimp as assigned.",
    "Pulled basic campaign stats from Google Analytics into a weekly Excel summary.",
    "Helped coordinate logistics for a small team event, including booking a room.",
    "Created simple graphics in Canva for social media posts.",
    "Helped compile a competitor benchmarking document in PowerPoint.",
    "Wrote short blog post drafts and submitted them for editor review.",
    "Updated the company website with new content using WordPress.",
    "Entered new contacts into HubSpot CRM and cleaned up duplicate entries.",
    "Helped run a basic SEO audit by pulling keyword data from SEMrush into Excel.",
    "Reached out to a few influencer contacts and tracked responses in a spreadsheet.",
    "Updated a media contacts list in Excel and helped send out a press kit.",
]

# Humanities internship data
HUMANITIES_COMPANIES = [
    "public library", "local historical society", "museum", "newspaper",
    "nonprofit advocacy organization", "state archives", "think tank",
    "congressional office", "law firm (paralegal)", "publishing house",
    "university library", "documentary film production company",
    "community outreach organization",
]

HUMANITIES_ROLES = [
    "Research Assistant", "Editorial Intern", "Policy Research Intern",
    "Archival Assistant", "Communications Intern", "Writing Intern",
    "Program Intern",
]

HUMANITIES_BULLETS = [
    "Reviewed and summarized a batch of primary sources for the research team.",
    "Helped draft a short policy memo on a housing issue for review by senior staff.",
    "Transcribed handwritten archival documents and entered them into a spreadsheet.",
    "Proofread and lightly edited articles for a nonprofit newsletter.",
    "Helped organize logistics for a small public panel event.",
    "Wrote a short blog post draft for the organization's website.",
    "Assisted with transcription for a community oral history project.",
    "Updated a grants tracking spreadsheet with new deadline information.",
    "Looked up legislative history for a pending bill and summarized findings for staff.",
    "Proofread a section of an academic manuscript before submission.",
]

# Psychology internship data
PSYCH_COMPANIES = [
    "community mental health center", "university counseling center",
    "behavioral health clinic", "research hospital", "school district",
    "HR consulting firm", "UX research lab", "social services agency",
    "therapy practice", "online mental health startup",
]

PSYCH_ROLES = [
    "Research Assistant", "Clinical Intern", "HR Research Intern",
    "Behavioral Health Intern", "School Psychology Intern",
    "UX Research Intern",
]

PSYCH_BULLETS = [
    "Helped administer psychological assessments to clients under clinician supervision.",
    "Entered survey data from paper forms into SPSS and ran basic frequency tables.",
    "Observed group therapy sessions and helped prepare session notes.",
    "Reviewed case files and summarized relevant background information as requested.",
    "Helped recruit and schedule participants for an IRB-approved study.",
    "Coded open-ended survey responses using a provided codebook.",
    "Compiled references for a literature review on anxiety interventions.",
    "Helped format and submit a short IRB amendment form under supervision.",
    "Showed two new volunteers how to log data in the lab's tracking spreadsheet.",
    "Entered pre/post survey scores into a spreadsheet for the research team.",
]

# Finance / Accounting internship data
FIN_COMPANIES = [
    "JPMorgan Chase", "Goldman Sachs", "Morgan Stanley", "Bank of America",
    "Wells Fargo", "Citigroup", "PwC", "EY", "Deloitte", "KPMG",
    "regional CPA firm", "Merrill Lynch", "Raymond James",
    "private equity firm", "hedge fund (small)", "corporate treasury department",
]

FIN_ROLES = [
    "Investment Banking Analyst Intern", "Corporate Finance Intern",
    "Accounting Intern", "Financial Analyst Intern",
    "Audit Intern", "Tax Intern", "Wealth Management Intern",
]

FIN_BULLETS = [
    "Helped update an Excel financial model with new figures provided by the team.",
    "Assisted in organizing audit workpapers for a client engagement.",
    "Pulled comparable company data from FactSet into a spreadsheet as directed.",
    "Reconciled monthly bank statements and flagged a few discrepancies for review.",
    "Helped prepare supporting schedules for individual tax returns.",
    "Updated and maintained an Excel tracker for active deal-flow entries.",
    "Took notes during due diligence calls and drafted a brief summary memo.",
    "Helped format pitchbook slides in PowerPoint using a provided template.",
    "Ran a DCF model template in Excel using figures provided by a senior analyst.",
    "Helped format sections of a quarterly earnings report.",
]

# Fine Arts internship data
ARTS_COMPANIES = [
    "local design studio", "advertising agency creative department",
    "museum curatorial team", "nonprofit arts organization",
    "publishing house (design)", "UX/UI design agency",
    "apparel brand creative team", "film production company",
    "community arts center",
]

ARTS_ROLES = [
    "Graphic Design Intern", "Creative Intern", "Visual Arts Intern",
    "UX/UI Design Intern", "Production Design Intern",
    "Curatorial Assistant",
]

ARTS_BULLETS = [
    "Created a few social media graphics in Canva as assigned by the design lead.",
    "Helped hang and label artwork for a small gallery exhibition.",
    "Assisted in compiling visual identity assets for a nonprofit rebrand project.",
    "Helped color-correct footage in Adobe Premiere Pro following a senior editor's notes.",
    "Formatted files for print according to vendor specifications.",
    "Helped build wireframe mockups in Figma based on a design brief.",
    "Researched and summarized artist bios for an upcoming exhibition catalog.",
    "Photographed products and did basic retouching in Photoshop.",
]

# Nursing internship data
NURSING_COMPANIES = [
    "regional hospital (clinical rotation)", "community health clinic",
    "long-term care facility", "pediatric specialty clinic",
    "urgent care center", "university health center",
    "hospice care organization",
]

NURSING_ROLES = [
    "Nursing Student (Clinical Rotation)", "Clinical Intern",
    "Patient Care Technician Intern", "Community Health Intern",
]

NURSING_BULLETS = [
    "Completed clinical rotation in medical-surgical unit assisting RN with patient care.",
    "Helped with medication administration and vital sign checks under RN supervision.",
    "Participated in care team rounds and observed patient assessments.",
    "Helped conduct basic health screenings at a community health fair.",
    "Assisted with wound care and dressing changes under supervising RN.",
    "Provided discharge instructions to patients as directed by the care team.",
    "Maintained sterile technique during dressing changes.",
    "Documented shift notes for assigned patients in the EMR system.",
]

# ---------------------------------------------------------------------------
# Career changer profiles
# ---------------------------------------------------------------------------

BOOTCAMP_LANGUAGES  = ["Python", "JavaScript", "SQL", "HTML/CSS"]
BOOTCAMP_LIBRARIES  = ["Pandas", "NumPy", "Matplotlib", "Flask", "React"]
BOOTCAMP_TOOLS      = ["Git", "GitHub", "Jupyter", "VS Code", "Excel", "Tableau"]
BOOTCAMP_DATA       = ["Data Cleaning", "Data Visualization", "CSV Processing",
                       "Basic SQL Querying", "Web Scraping", "Excel Automation"]
BOOTCAMP_COURSES    = ["Python for Data Science (Coursera)", "SQL for Data Analysis (Udemy)",
                       "Data Visualization with Tableau (LinkedIn Learning)",
                       "Machine Learning Fundamentals (fast.ai)",
                       "Applied Data Science Bootcamp (DataCamp)"]
BOOTCAMP_CERTS      = ["Google Data Analytics Certificate", "IBM Data Science Professional Certificate",
                       "AWS Certified Cloud Practitioner", "Tableau Desktop Specialist",
                       "Python Institute PCEP Certification"]

BOOTCAMP_PREV_MAJORS = [
    "Marketing", "Communications", "Business Administration", "English",
    "Political Science", "Accounting", "Graphic Design", "Sociology", "History",
]

BOOTCAMP_BULLETS = [
    "Completed a Python/SQL data science course online; built a small portfolio project.",
    "Automated a personal budget tracker in Python/openpyxl as a self-learning exercise.",
    "Built a basic web scraper in Python to collect job listing data as a practice project.",
    "Created a Tableau dashboard analyzing local real estate CSV data from a public dataset.",
    "Completed Google Data Analytics Certificate; capstone project done in Python and Tableau.",
    "Self-taught Python through Coursera and Kaggle; worked through 2 guided projects.",
    "Built a simple Flask app to display personal finance data from exported bank CSVs.",
    "Worked through a K-means clustering tutorial on a retail dataset in a Jupyter notebook.",
]

# ---------------------------------------------------------------------------
# Projects -- per category
# ---------------------------------------------------------------------------

CS_PROJECTS = [
    {
        "title": "Excel-to-Python Automation Tool",
        "desc": "Class project: wrote a Python script (openpyxl) that reads an Excel workbook and prints out a summary of the data. Built for a software engineering course assignment.",
    },
    {
        "title": "Energy Consumption Dashboard",
        "desc": "Personal project: Streamlit dashboard reading hourly CSV data from a public dataset and displaying usage trends. Built to practice data visualization.",
    },
    {
        "title": "Simple ETL Pipeline",
        "desc": "Group project for Database Systems course. Python script that reads JSON files, validates required fields, and loads records into a SQLite database.",
    },
    {
        "title": "Python Lab Report Automation",
        "desc": "Personal project: replaced a manual Excel workflow in a research lab with a Python script using Pandas and openpyxl. Built under guidance from a grad student.",
    },
    {
        "title": "Stock Price Visualization",
        "desc": "Class project: pulled stock price data from Yahoo Finance API and plotted trends using Matplotlib. Applied a simple moving average as a course exercise.",
    },
    {
        "title": "Resume Keyword Classifier",
        "desc": "Personal project: trained a basic text classifier using Scikit-learn to categorize resumes by job type. Used TF-IDF features and a small labeled dataset.",
    },
    {
        "title": "Automated Report Generator",
        "desc": "Personal project: Python script using openpyxl to read raw CSV data and write a formatted summary Excel file. Replaced a manual copy-paste process.",
    },
    {
        "title": "COVID-19 Data Explorer",
        "desc": "Group project for data analysis course. Loaded JHU CSV datasets into Pandas, cleaned the data, and built basic Matplotlib charts showing case trends by state.",
    },
    {
        "title": "Weather Forecasting Exploration",
        "desc": "Personal project: applied a basic ARIMA model to publicly available weather CSV data as practice with time series concepts from a statistics course.",
    },
    {
        "title": "Personal Finance Tracker",
        "desc": "Personal project: Python script that parses exported bank CSV files and categorizes transactions. Built to practice file I/O and pandas. Not deployed.",
    },
    {
        "title": "Data Migration Helper",
        "desc": "Course project: Python scripts to read Excel files and insert records into a PostgreSQL database with basic validation checks.",
    },
    {
        "title": "Sensor Data Logger",
        "desc": "Group project for an IoT course. Python script that reads simulated sensor readings from a CSV, detects outliers using a simple threshold, and writes a summary report.",
    },
    {
        "title": "Grid Load Visualization",
        "desc": "Class project: loaded publicly available electricity load CSV data into Pandas and created charts showing demand trends. Presented to classmates at end of semester.",
    },
]

EE_PROJECTS = [
    {
        "title": "Audio Filter Lab Project",
        "desc": "Class project: designed a simple low-pass filter in LTspice for a circuits lab. Compared simulation output to bench measurements and wrote a lab report.",
    },
    {
        "title": "Line-Following Robot",
        "desc": "Senior capstone group project: built a line-following robot using a microcontroller and IR sensors. Wrote basic embedded C firmware for motor control.",
    },
    {
        "title": "Power Factor Correction Lab",
        "desc": "Lab assignment: simulated a basic PFC circuit in LTspice, measured results on the bench, and documented findings in a lab report.",
    },
    {
        "title": "MATLAB Signal Processing Exercise",
        "desc": "Course assignment: wrote MATLAB scripts to filter and plot ECG signals from a public dataset. Applied FFT and a bandpass filter as instructed.",
    },
    {
        "title": "Solar Charge Controller Design",
        "desc": "Class project: designed a basic solar charge controller schematic in a CAD tool and simulated the charging circuit in MATLAB as part of a power electronics course.",
    },
]

IE_ME_PROJECTS = [
    {
        "title": "Warehouse Simulation (Class Project)",
        "desc": "Group project for Operations Research course. Modeled a simple warehouse using Arena simulation software and identified a bottleneck at the picking station.",
    },
    {
        "title": "Quality Control Dashboard",
        "desc": "Course project: built an Excel dashboard with basic charts for SPC and defect tracking for a fictional production line scenario.",
    },
    {
        "title": "Ergonomic Workstation Analysis",
        "desc": "Class project: applied NIOSH lifting guidelines and RULA analysis to a sample workstation design and wrote a recommendation report.",
    },
    {
        "title": "Inventory Reorder Model",
        "desc": "Course assignment: built a basic inventory simulation in Python using NumPy to explore reorder point policies on a small set of example SKUs.",
    },
]

IS_BA_PROJECTS = [
    {
        "title": "Sales Dashboard (Class Project)",
        "desc": "Built a Tableau dashboard connected to a sample MySQL database to visualize weekly sales figures. Created for a business intelligence course assignment.",
    },
    {
        "title": "CRM Data Cleanup Exercise",
        "desc": "Course project: wrote SQL queries to find and remove duplicate records in a sample CRM dataset. Summarized results in a short report.",
    },
    {
        "title": "E-Commerce Funnel Analysis",
        "desc": "Personal project: pulled Google Analytics sample data into Excel and built a pivot table showing conversion rates at each checkout step.",
    },
]

ECON_PROJECTS = [
    {
        "title": "Housing Price Regression (Class Project)",
        "desc": "Course assignment: ran an OLS regression in Stata on a sample of home sale data to estimate the effect of lot size on price. Wrote a short results summary.",
    },
    {
        "title": "Minimum Wage Policy Brief",
        "desc": "Senior seminar paper: analyzed BLS employment data in R and wrote a 15-page policy brief on minimum wage effects on teen employment.",
    },
    {
        "title": "Trade Data Visualization",
        "desc": "Course project: downloaded US Census trade data and built simple ggplot2 charts showing import/export trends with a few major trade partners.",
    },
]

COGNEURO_PROJECTS = [
    {
        "title": "EEG Data Analysis (Research Course)",
        "desc": "Semester research project: preprocessed EEG data from a small participant sample using MNE-Python and generated event-related potential plots for a lab poster.",
    },
    {
        "title": "Cognitive Load Survey (Course Project)",
        "desc": "Designed a 20-item Qualtrics survey on cognitive load during study sessions. Collected responses from classmates and ran basic ANOVA in SPSS for a class report.",
    },
]

BIO_PROJECTS = [
    {
        "title": "RNA-seq Pipeline (Class Assignment)",
        "desc": "Course assignment: ran a provided Bash/R pipeline for RNA-seq analysis on a sample dataset, generated a volcano plot, and wrote a brief interpretation report.",
    },
    {
        "title": "Protein Sequence Classification",
        "desc": "Personal project following a bioinformatics tutorial: used Biopython to parse FASTA files and trained a basic Random Forest classifier on k-mer features.",
    },
]

MKT_PROJECTS = [
    {
        "title": "Social Media Campaign Analysis (Class Project)",
        "desc": "Course assignment: tracked Instagram ad campaign data in Excel over one month, built pivot tables showing engagement metrics, and presented recommendations.",
    },
    {
        "title": "Brand Audit Report",
        "desc": "Group project for Brand Management course. Conducted a SWOT analysis and competitor review for a local restaurant and presented findings in a 20-slide deck.",
    },
    {
        "title": "Email Marketing Analysis",
        "desc": "Personal project: exported Mailchimp data from a club newsletter and used Excel to compare open rates across different subject line types.",
    },
]

HUMANITIES_PROJECTS = [
    {
        "title": "Oral History Project (Class Assignment)",
        "desc": "Conducted and transcribed interviews with local community members for a history course project. Compiled summaries in a shared Google Doc.",
    },
    {
        "title": "Policy Memo: Affordable Housing",
        "desc": "Senior seminar paper: researched housing voucher programs in several cities and wrote a 12-page policy memo with recommendations for a state-level audience.",
    },
    {
        "title": "Literary Analysis Blog",
        "desc": "Maintained a small personal blog applying critical theory to contemporary fiction. Written as a supplementary exercise for an English literature course.",
    },
]

PSYCH_PROJECTS = [
    {
        "title": "Mindfulness Survey Study (Class Project)",
        "desc": "Semester research project: helped administer pre/post surveys for a mindfulness study (n=20). Entered data in SPSS and ran paired t-tests for a course paper.",
    },
    {
        "title": "Social Media and Self-Esteem Survey",
        "desc": "Ran an online survey (Qualtrics, n=60) on social media use and self-esteem for a research methods course. Ran multiple regression in SPSS and wrote a report.",
    },
]

FIN_PROJECTS = [
    {
        "title": "DCF Valuation (Class Project)",
        "desc": "Course assignment: built a basic DCF model in Excel for a publicly traded company using a provided template. Calculated WACC and created a sensitivity table.",
    },
    {
        "title": "Momentum Strategy Backtest",
        "desc": "Personal project following a finance textbook exercise: used Yahoo Finance data in Excel to test a simple moving average strategy on a few stock tickers.",
    },
    {
        "title": "Credit Analysis Report",
        "desc": "Group project for corporate finance course. Analyzed financial statements of two high-yield companies and summarized key risk ratios in a 6-page report.",
    },
]

ARTS_PROJECTS = [
    {
        "title": "Student Org Visual Identity (Class Project)",
        "desc": "Designed a basic logo and color palette for a student organization as part of a graphic design course. Delivered files in Adobe Illustrator.",
    },
    {
        "title": "Short Documentary Film",
        "desc": "Directed and edited a 5-minute documentary on a campus topic for a film production course. Edited in Adobe Premiere Pro.",
    },
]

NURSING_PROJECTS = [
    {
        "title": "Community Health Needs Assessment",
        "desc": "Group course project: conducted door-to-door surveys in a local neighborhood and compiled findings in a Word report for a community health class.",
    },
    {
        "title": "Patient Education Brochure",
        "desc": "Class assignment: designed a plain-language brochure on post-operative wound care in Microsoft Publisher, reviewed by a supervising RN for accuracy.",
    },
]

BOOTCAMP_PROJECTS = [
    {
        "title": "Job Listing Scraper",
        "desc": "Personal project following a tutorial: built a Python web scraper using requests and BeautifulSoup to collect job listings and store them in a CSV file.",
    },
    {
        "title": "Personal Budget Tracker",
        "desc": "Personal project: Python script that reads exported CSV bank statements and writes a categorized summary to Excel using openpyxl.",
    },
    {
        "title": "Housing Price Prediction (Kaggle Tutorial)",
        "desc": "Followed a Kaggle tutorial to train a gradient boosting model on the Ames Housing dataset. Completed as a self-study exercise.",
    },
    {
        "title": "COVID Data Dashboard",
        "desc": "Personal project: loaded JHU CSV data into Pandas, cleaned it, and built a basic Tableau Public dashboard showing case trends.",
    },
]

# ---------------------------------------------------------------------------
# Awards
# ---------------------------------------------------------------------------

AWARDS_STRONG = [
    "Dean's List - one semester",
    "1st Place - {event} Hackathon",
    "Best Capstone Project Award - {dept} Department",
    "Tau Beta Pi Engineering Honor Society inductee",
    "IEEE Student Branch member, {year}",
    "Top performer in {dept} senior cohort",
]

AWARDS_PARTIAL = [
    "Dean's List - one semester",
    "Department Honors in {dept}",
    "Undergraduate Research Grant recipient",
    "Outstanding TA Award - {dept} Department",
    "1st Place - Regional Engineering Competition",
    "Honors Program member",
]

AWARDS_WEAK = [
    "Dean's List - one semester",
    "Honors Program graduate",
    "Undergraduate Research Symposium Presenter",
]

# PhD pubs
PHD_PUBS = [
    "'{title}' - submitted to {venue}, {year} (under review)",
    "'{title}' - {venue} Workshop, {year} (accepted)",
    "'{title}' - {venue}, {year} (accepted)",
]
PHD_TITLES = [
    "Efficient Python Automation Frameworks for Scientific Data Pipelines",
    "Graph-Based Anomaly Detection in Infrastructure Sensor Networks",
    "Federated Learning for Privacy-Preserving Energy Consumption Forecasting",
    "Automated Spreadsheet-to-Code Translation via Program Synthesis",
    "Time-Series Foundation Models for Electrical Grid Load Forecasting",
    "Self-Supervised Representation Learning for Supply Chain Optimization",
    "Scalable ETL Pipelines for High-Volume Telemetry Data",
    "Interpretable ML for Predictive Maintenance in Power Systems",
]
PHD_VENUES = ["NeurIPS", "ICML", "ICLR", "KDD", "AAAI", "IEEE TPDS", "ACM e-Energy",
              "SIGMOD", "VLDB", "CVPR"]

# ---------------------------------------------------------------------------
# Profile assignment: 100 profiles with specified distribution
# ---------------------------------------------------------------------------
# Strong fit (~35 total): CS/DS undergrads, recent grads, MS, PhD
# Partial fit (~30 total): STEM-adjacent
# Weak fit (~25 total): non-STEM
# Career changers (~10): separate bucket

# We build a fixed list of 100 profile specs:
# Each spec: (profile_type, major)
# profile_type: "bs_current" | "bs_recent" | "ms_current" | "phd" | "bs_career" | "career_change"

_STRONG_MAJORS  = ["Computer Science", "Data Science", "Computer Engineering",
                   "Applied Mathematics", "Statistics"]
_PARTIAL_MAJORS = ["Electrical Engineering", "Physics", "Industrial Engineering",
                   "Mechanical Engineering", "Information Systems", "Economics",
                   "Business Analytics", "Cognitive Science", "Neuroscience",
                   "Biology (Bioinformatics)"]
_WEAK_MAJORS    = ["Marketing", "English", "Political Science", "History",
                   "Fine Arts", "Psychology", "Sociology", "Communications",
                   "Finance", "Nursing", "Accounting"]

def _build_profile_list():
    profiles = []

    # 30 current undergrads - mix all majors
    for _ in range(12):
        profiles.append(("bs_current", random.choice(_STRONG_MAJORS)))
    for _ in range(10):
        profiles.append(("bs_current", random.choice(_PARTIAL_MAJORS)))
    for _ in range(8):
        profiles.append(("bs_current", random.choice(_WEAK_MAJORS)))

    # 25 recent BS grads 2024-2025 - mix all majors
    for _ in range(10):
        profiles.append(("bs_recent", random.choice(_STRONG_MAJORS)))
    for _ in range(8):
        profiles.append(("bs_recent", random.choice(_PARTIAL_MAJORS)))
    for _ in range(7):
        profiles.append(("bs_recent", random.choice(_WEAK_MAJORS)))

    # 20 MS students - mostly STEM, some MBA/MPA
    for _ in range(14):
        profiles.append(("ms_current", random.choice(_STRONG_MAJORS + _PARTIAL_MAJORS[:5])))
    for _ in range(6):
        profiles.append(("ms_current", "MBA/MPA"))

    # 10 BS with 1-2 internships (strong/partial fit)
    for _ in range(5):
        profiles.append(("bs_career", random.choice(_STRONG_MAJORS)))
    for _ in range(5):
        profiles.append(("bs_career", random.choice(_PARTIAL_MAJORS)))

    # 5 PhD students
    for _ in range(5):
        profiles.append(("phd", random.choice(["Computer Science", "Electrical Engineering",
                                                "Physics", "Applied Mathematics"])))

    # 10 career changers
    for _ in range(10):
        prev = random.choice(BOOTCAMP_PREV_MAJORS)
        profiles.append(("career_change", prev))

    random.shuffle(profiles)
    return profiles[:100]

random.seed(42)
PROFILES = _build_profile_list()

# ---------------------------------------------------------------------------
# PDF helpers
# ---------------------------------------------------------------------------

NL = {"new_x": "LMARGIN", "new_y": "NEXT"}


def section_header(pdf, W, text):
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_fill_color(225, 225, 225)
    pdf.cell(W, 7, text, fill=True, **NL)
    pdf.ln(1)


def bold_label(pdf, label, value, W, label_w=42):
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(label_w, 5.5, label, new_x="END", new_y="TOP")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(W - label_w, 5.5, value, **NL)


def body_line(pdf, W, text, indent=4):
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(W - indent, 5.5, "  - " + text, **NL)


def _award_str(tmpl, deg_field, rng):
    return tmpl.format(
        semesters=rng.randint(2, 4),
        year=rng.randint(2022, 2025),
        year2=rng.randint(2023, 2025),
        event=rng.choice(["HackMIT", "TreeHacks", "HackNY", "LA Hacks", "MHacks"]),
        teams=rng.randint(80, 400),
        dept=deg_field,
    )

# ---------------------------------------------------------------------------
# Main builder
# ---------------------------------------------------------------------------

def make_resume(index: int, profile_type: str, major: str):
    rng = random.Random(index * 97 + hash(profile_type + major) % 9973)

    first = rng.choice(FIRST_NAMES)
    last  = rng.choice(LAST_NAMES)
    name  = f"{first} {last}"
    email = f"{first.lower()}.{last.lower()}{rng.randint(1,99)}@gmail.com"
    phone = f"+1-{rng.randint(200,999)}-{rng.randint(100,999)}-{rng.randint(1000,9999)}"
    location = rng.choice(["San Francisco, CA", "New York, NY", "Seattle, WA",
                            "Austin, TX", "Boston, MA", "Chicago, IL",
                            "Los Angeles, CA", "Atlanta, GA", "Remote"])
    university, uni_city = rng.choice(UNIVERSITIES)
    linkedin = f"linkedin.com/in/{first.lower()}{last.lower()}{rng.randint(10,99)}"
    github   = f"github.com/{first.lower()}{last.lower()}"

    cat, fit = MAJORS.get(major, ("non_stem", "weak"))

    # ---- helper: pick skills based on major ----
    def _skills_for_major():
        if cat == "cs_ds":
            # 3-5 total skills for most; slightly more for strong-fit seniors/MS
            langs = rng.sample(CS_DS_LANGUAGES, rng.randint(2, 4))
            if "Python" not in langs: langs[0] = "Python"
            libs  = rng.sample(CS_DS_LIBRARIES, rng.randint(2, 4))
            tools = rng.sample(CS_DS_TOOLS, rng.randint(2, 3))
            data  = rng.sample(CS_DS_DATA, rng.randint(1, 3))
            return langs, libs, tools, data
        elif major == "Electrical Engineering":
            langs = rng.sample(EE_LANGUAGES, rng.randint(2, 3))
            libs  = rng.sample(EE_LIBRARIES, rng.randint(1, 2))
            tools = rng.sample(EE_TOOLS, rng.randint(2, 4))
            data  = rng.sample(EE_DATA, rng.randint(1, 3))
            return langs, libs, tools, data
        elif major in ("Industrial Engineering", "Mechanical Engineering", "Physics"):
            langs = rng.sample(IE_ME_LANGUAGES, rng.randint(1, 3))
            libs  = rng.sample(IE_ME_LIBRARIES, rng.randint(1, 2))
            tools = rng.sample(IE_ME_TOOLS, rng.randint(2, 4))
            data  = rng.sample(IE_ME_DATA, rng.randint(1, 3))
            return langs, libs, tools, data
        elif major in ("Information Systems", "Business Analytics"):
            langs = rng.sample(IS_BA_LANGUAGES, rng.randint(1, 3))
            libs  = rng.sample(IS_BA_LIBRARIES, rng.randint(1, 2))
            tools = rng.sample(IS_BA_TOOLS, rng.randint(2, 4))
            data  = rng.sample(IS_BA_DATA, rng.randint(1, 3))
            return langs, libs, tools, data
        elif major == "Economics":
            langs = rng.sample(ECON_LANGUAGES, rng.randint(1, 3))
            libs  = rng.sample(ECON_LIBRARIES, rng.randint(1, 2))
            tools = rng.sample(ECON_TOOLS, rng.randint(2, 3))
            data  = rng.sample(ECON_DATA, rng.randint(1, 2))
            return langs, libs, tools, data
        elif major in ("Cognitive Science", "Neuroscience"):
            langs = rng.sample(COGNEURO_LANGUAGES, rng.randint(1, 2))
            libs  = rng.sample(COGNEURO_LIBRARIES, rng.randint(1, 2))
            tools = rng.sample(COGNEURO_TOOLS, rng.randint(2, 3))
            data  = rng.sample(COGNEURO_DATA, rng.randint(1, 2))
            return langs, libs, tools, data
        elif major == "Biology (Bioinformatics)":
            langs = rng.sample(BIO_LANGUAGES, rng.randint(1, 2))
            libs  = rng.sample(BIO_LIBRARIES, rng.randint(1, 2))
            tools = rng.sample(BIO_TOOLS, rng.randint(2, 3))
            data  = rng.sample(BIO_DATA, rng.randint(1, 2))
            return langs, libs, tools, data
        elif major in ("Marketing", "Communications", "Sociology"):
            tools = rng.sample(MKT_SKILLS_TECH, rng.randint(2, 4))
            soft  = rng.sample(MKT_SKILLS_SOFT, rng.randint(1, 3))
            return [], [], tools, soft
        elif major in ("English", "Political Science", "History"):
            tools = rng.sample(HUMANITIES_TECH, rng.randint(2, 3))
            soft  = rng.sample(HUMANITIES_SOFT, rng.randint(1, 3))
            return [], [], tools, soft
        elif major == "Psychology":
            tools = rng.sample(PSYCH_TECH, rng.randint(2, 3))
            soft  = rng.sample(PSYCH_SOFT, rng.randint(1, 3))
            return [], [], tools, soft
        elif major in ("Finance", "Accounting"):
            tools = rng.sample(FIN_TECH, rng.randint(2, 4))
            soft  = rng.sample(FIN_SOFT, rng.randint(1, 3))
            return [], [], tools, soft
        elif major == "Fine Arts":
            tools = rng.sample(ARTS_TECH, rng.randint(2, 4))
            soft  = rng.sample(ARTS_SOFT, rng.randint(1, 3))
            return [], [], tools, soft
        elif major == "Nursing":
            tools = rng.sample(NURSING_TECH, rng.randint(2, 3))
            soft  = rng.sample(NURSING_SOFT, rng.randint(1, 3))
            return [], [], tools, soft
        elif major == "MBA/MPA":
            tools = rng.sample(IS_BA_TOOLS + FIN_TECH, rng.randint(3, 5))
            soft  = rng.sample(FIN_SOFT + MKT_SKILLS_SOFT, rng.randint(2, 4))
            return [], [], tools, soft
        else:  # career changer
            langs = rng.sample(BOOTCAMP_LANGUAGES, rng.randint(2, 3))
            libs  = rng.sample(BOOTCAMP_LIBRARIES, rng.randint(1, 3))
            tools = rng.sample(BOOTCAMP_TOOLS, rng.randint(2, 3))
            data  = rng.sample(BOOTCAMP_DATA, rng.randint(1, 3))
            return langs, libs, tools, data

    def _courses_for_major():
        if cat == "cs_ds":
            return rng.sample(CS_DS_COURSES, rng.randint(5, 8))
        elif major == "Electrical Engineering":
            return rng.sample(EE_COURSES, rng.randint(4, 7))
        elif major in ("Industrial Engineering", "Mechanical Engineering", "Physics"):
            return rng.sample(IE_ME_COURSES, rng.randint(4, 6))
        elif major in ("Information Systems", "Business Analytics"):
            return rng.sample(IS_BA_COURSES, rng.randint(4, 6))
        elif major == "Economics":
            return rng.sample(ECON_COURSES, rng.randint(4, 6))
        elif major in ("Cognitive Science", "Neuroscience"):
            return rng.sample(COGNEURO_COURSES, rng.randint(4, 6))
        elif major == "Biology (Bioinformatics)":
            return rng.sample(BIO_COURSES, rng.randint(4, 6))
        elif major in ("Marketing", "Communications", "Sociology"):
            return rng.sample(MKT_COURSES, rng.randint(4, 6))
        elif major in ("English", "Political Science", "History"):
            return rng.sample(HUMANITIES_COURSES, rng.randint(4, 6))
        elif major == "Psychology":
            return rng.sample(PSYCH_COURSES, rng.randint(4, 6))
        elif major in ("Finance", "Accounting"):
            return rng.sample(FIN_COURSES, rng.randint(4, 6))
        elif major == "Fine Arts":
            return rng.sample(ARTS_COURSES, rng.randint(3, 5))
        elif major == "Nursing":
            return rng.sample(NURSING_COURSES, rng.randint(4, 6))
        elif major == "MBA/MPA":
            return rng.sample(MBA_MPA_COURSES, rng.randint(4, 6))
        else:
            return rng.sample(BOOTCAMP_COURSES, rng.randint(2, 4))

    def _intern_data_for_major():
        if cat == "cs_ds":
            pool = CS_COMPANIES_MID + CS_COMPANIES_SMALL
            if rng.random() > 0.7: pool += CS_COMPANIES_BIG
            return pool, CS_ROLES, CS_BULLETS_MUNDANE, CS_BULLETS_DECENT
        elif major == "Electrical Engineering":
            return EE_COMPANIES, EE_ROLES, EE_BULLETS, None
        elif major in ("Industrial Engineering", "Mechanical Engineering", "Physics"):
            return IE_ME_COMPANIES, IE_ME_ROLES, IE_ME_BULLETS, None
        elif major in ("Information Systems", "Business Analytics"):
            return IS_BA_COMPANIES, IS_BA_ROLES, IS_BA_BULLETS, None
        elif major == "Economics":
            return ECON_COMPANIES, ECON_ROLES, ECON_BULLETS, None
        elif major in ("Cognitive Science", "Neuroscience"):
            return COGNEURO_COMPANIES, COGNEURO_ROLES, COGNEURO_BULLETS, None
        elif major == "Biology (Bioinformatics)":
            return BIO_COMPANIES, BIO_ROLES, BIO_BULLETS, None
        elif major in ("Marketing", "Communications", "Sociology"):
            return MKT_COMPANIES, MKT_ROLES, MKT_BULLETS, None
        elif major in ("English", "Political Science", "History"):
            return HUMANITIES_COMPANIES, HUMANITIES_ROLES, HUMANITIES_BULLETS, None
        elif major == "Psychology":
            return PSYCH_COMPANIES, PSYCH_ROLES, PSYCH_BULLETS, None
        elif major in ("Finance", "Accounting"):
            return FIN_COMPANIES, FIN_ROLES, FIN_BULLETS, None
        elif major == "Fine Arts":
            return ARTS_COMPANIES, ARTS_ROLES, ARTS_BULLETS, None
        elif major == "Nursing":
            return NURSING_COMPANIES, NURSING_ROLES, NURSING_BULLETS, None
        elif major == "MBA/MPA":
            return IS_BA_COMPANIES + FIN_COMPANIES, IS_BA_ROLES + FIN_ROLES, IS_BA_BULLETS + FIN_BULLETS, None
        else:  # career changer: prior-field + some tech
            return CS_COMPANIES_SMALL + MKT_COMPANIES, MKT_ROLES + ["Data Analyst Intern"], MKT_BULLETS + BOOTCAMP_BULLETS, None

    def _projects_for_major():
        # Weak-fit: 50% chance of no projects, otherwise 0-1
        if fit == "weak":
            if rng.random() < 0.5:
                return []
            return rng.sample(globals().get(f"{cat.upper()}_PROJECTS", []) or [], 0) or _pick_weak_projects()
        # Strong-fit CS/DS: 1-2 projects
        if cat == "cs_ds":
            return rng.sample(CS_PROJECTS, rng.randint(1, 2))
        elif major == "Electrical Engineering":
            return rng.sample(EE_PROJECTS, rng.randint(1, 2))
        elif major in ("Industrial Engineering", "Mechanical Engineering", "Physics"):
            combined = IE_ME_PROJECTS + CS_PROJECTS[:3]
            return rng.sample(combined, min(rng.randint(1, 2), len(combined)))
        elif major in ("Information Systems", "Business Analytics"):
            combined = IS_BA_PROJECTS + CS_PROJECTS[:3]
            return rng.sample(combined, min(rng.randint(1, 2), len(combined)))
        elif major == "Economics":
            return rng.sample(ECON_PROJECTS, rng.randint(1, 2))
        elif major in ("Cognitive Science", "Neuroscience"):
            return rng.sample(COGNEURO_PROJECTS, rng.randint(0, 1))
        elif major == "Biology (Bioinformatics)":
            return rng.sample(BIO_PROJECTS, rng.randint(0, 1))
        elif major in ("Marketing", "Communications", "Sociology"):
            return rng.sample(MKT_PROJECTS, rng.randint(0, 1))
        elif major in ("English", "Political Science", "History"):
            return rng.sample(HUMANITIES_PROJECTS, rng.randint(0, 1))
        elif major == "Psychology":
            return rng.sample(PSYCH_PROJECTS, rng.randint(0, 1))
        elif major in ("Finance", "Accounting"):
            return rng.sample(FIN_PROJECTS, rng.randint(0, 1))
        elif major == "Fine Arts":
            return rng.sample(ARTS_PROJECTS, rng.randint(0, 1))
        elif major == "Nursing":
            return rng.sample(NURSING_PROJECTS, rng.randint(0, 1))
        elif major == "MBA/MPA":
            return rng.sample(IS_BA_PROJECTS + FIN_PROJECTS, rng.randint(0, 1))
        else:  # career changer
            return rng.sample(BOOTCAMP_PROJECTS, rng.randint(1, 2))

    def _pick_weak_projects():
        pools = [MKT_PROJECTS, HUMANITIES_PROJECTS, PSYCH_PROJECTS,
                 FIN_PROJECTS, ARTS_PROJECTS, NURSING_PROJECTS]
        pool = rng.choice(pools)
        return rng.sample(pool, 1)

    def _awards_for_fit():
        # Only 20% of resumes should have any awards
        if rng.random() > 0.20:
            return []
        pool = {"strong": AWARDS_STRONG, "partial": AWARDS_PARTIAL, "weak": AWARDS_WEAK}.get(fit, AWARDS_WEAK)
        return [_award_str(rng.choice(pool), major, rng)]

    # ---- degree / timeline ----
    if profile_type == "bs_current":
        deg_level = "B.S."
        deg_field = major
        standing_choices = ["Sophomore", "Junior", "Senior"]
        standing = rng.choice(standing_choices)
        grad_year = {"Sophomore": 2027, "Junior": 2026, "Senior": 2025}[standing]
        status_line = f"{standing}, Expected Graduation: {grad_year}"

        # Lower GPA ranges; 30% omit GPA entirely
        if fit == "strong":
            gpa_raw = round(rng.uniform(2.7, 3.7), 2)
        elif fit == "partial":
            gpa_raw = round(rng.uniform(2.5, 3.5), 2)
        else:
            gpa_raw = round(rng.uniform(2.3, 3.3), 2)
        show_gpa = rng.random() > 0.30

        # 40% of current undergrads have ZERO internships
        if rng.random() < 0.40:
            num_internships = 0
        else:
            max_intern = {"Sophomore": 0, "Junior": 1, "Senior": 1}[standing]
            num_internships = rng.randint(0, max_intern)

        # Only 20% have TA/RA
        has_ta_ra = rng.random() < 0.20
        pub_info = None
        bs_info = None

    elif profile_type == "bs_recent":
        deg_level = "B.S."
        deg_field = major
        grad_year = rng.choice([2024, 2025])
        standing = None
        status_line = f"Graduated: {grad_year}"

        if fit == "strong":
            gpa_raw = round(rng.uniform(2.7, 3.7), 2)
        elif fit == "partial":
            gpa_raw = round(rng.uniform(2.5, 3.5), 2)
        else:
            gpa_raw = round(rng.uniform(2.3, 3.3), 2)
        show_gpa = rng.random() > 0.30

        # Recent grads: 0-1 internships (not 1-2)
        num_internships = rng.randint(0, 1)
        # Only 20% have TA/RA
        has_ta_ra = rng.random() < 0.20
        pub_info = None
        bs_info = None

    elif profile_type == "bs_career":
        deg_level = "B.S."
        deg_field = major
        grad_year = rng.choice([2023, 2024])
        standing = None
        status_line = f"Graduated: {grad_year}"

        if fit == "strong":
            gpa_raw = round(rng.uniform(2.7, 3.7), 2)
        else:
            gpa_raw = round(rng.uniform(2.5, 3.5), 2)
        show_gpa = rng.random() > 0.30

        num_internships = rng.randint(0, 1)
        has_ta_ra = rng.random() < 0.20
        pub_info = None
        bs_info = None

    elif profile_type == "ms_current":
        if major == "MBA/MPA":
            deg_level = "M.B.A." if rng.random() > 0.4 else "M.P.A."
        else:
            deg_level = "M.S."
        deg_field = major
        bs_major = rng.choice(_STRONG_MAJORS + _PARTIAL_MAJORS[:4]) if cat in ("cs_ds", "stem_adj") else rng.choice(_PARTIAL_MAJORS + _WEAK_MAJORS)
        bs_uni, _ = rng.choice(UNIVERSITIES)
        bs_year = rng.randint(2020, 2023)
        grad_year_ms = rng.choice([2025, 2026])
        standing = None
        status_line = f"Expected Graduation: {grad_year_ms}"
        grad_year = grad_year_ms
        gpa_raw = round(rng.uniform(3.2, 4.0), 2)
        show_gpa = rng.random() > 0.20
        num_internships = rng.randint(0, 1)
        has_ta_ra = rng.random() < 0.20
        pub_info = None
        bs_info = (bs_major, bs_uni, bs_year)

    elif profile_type == "phd":
        deg_level = "Ph.D."
        deg_field = major
        bs_field2 = rng.choice(["Computer Science", "Electrical Engineering", "Mathematics", "Physics"])
        bs_uni2, _ = rng.choice(UNIVERSITIES)
        bs_year2 = rng.randint(2016, 2020)
        ms_year2 = bs_year2 + 2
        start_phd = ms_year2 + 1
        grad_year = rng.choice([2025, 2026])
        standing = None
        status_line = f"Ph.D. Candidate, Started {start_phd}"
        gpa_raw = round(rng.uniform(3.7, 4.0), 2)
        show_gpa = True
        num_internships = rng.randint(0, 1)
        has_ta_ra = True
        num_pubs = rng.randint(1, 3)
        pub_info = []
        for _ in range(num_pubs):
            tmpl = rng.choice(PHD_PUBS)
            pub_info.append(tmpl.format(
                title=rng.choice(PHD_TITLES),
                venue=rng.choice(PHD_VENUES),
                year=rng.randint(2023, 2025),
            ))
        bs_info = (bs_field2, bs_uni2, bs_year2)

    else:  # career_change
        deg_level = "B.S."
        deg_field = major  # prior unrelated major
        grad_year = rng.choice([2019, 2020, 2021, 2022])
        standing = None
        status_line = f"Graduated: {grad_year}"
        gpa_raw = round(rng.uniform(2.5, 3.3), 2)
        show_gpa = rng.random() > 0.40
        num_internships = 0
        has_ta_ra = False
        pub_info = None
        bs_info = None

    # ---- skills ----
    langs, libs, tools, data_skills = _skills_for_major()
    courses = _courses_for_major()

    # ---- internships ----
    intern_result = _intern_data_for_major()
    intern_company_pool, intern_roles = intern_result[0], intern_result[1]
    intern_bullets_main = intern_result[2]
    intern_bullets_good = intern_result[3]  # None for non-CS majors

    internships = []
    base_year = 2025
    for i in range(num_internships):
        yr = base_year - i
        season = rng.choice(["Summer", "Fall", "Spring"])
        company = rng.choice(intern_company_pool)
        role = rng.choice(intern_roles)
        # CS strong-fit seniors get a mix; others get mundane bullets only
        if intern_bullets_good and fit == "strong" and profile_type in ("bs_career", "bs_recent"):
            # 2 mundane + 1-2 decent
            bullet_pool = rng.sample(intern_bullets_main, min(2, len(intern_bullets_main))) + \
                          rng.sample(intern_bullets_good, min(rng.randint(1, 2), len(intern_bullets_good)))
        else:
            bullet_pool = rng.sample(intern_bullets_main, min(rng.randint(2, 3), len(intern_bullets_main)))
        bullets = bullet_pool
        internships.append({"season": season, "year": yr, "company": company,
                             "role": role, "bullets": bullets})

    # ---- TA/RA ----
    ta_ra_entries = []
    if has_ta_ra:
        ta_options = [
            f"Teaching Assistant for {rng.choice(courses)} - helped grade assignments and held office hours.",
            f"Research Assistant in {deg_field} department - helped collect and organize data for a faculty project.",
            f"Lab Assistant - helped set up equipment and supported students during lab sessions.",
        ]
        ta_ra_entries.append(rng.choice(ta_options))

    # ---- career changer extra section ----
    bootcamp_entries = []
    if profile_type == "career_change":
        num_certs = rng.randint(1, 3)
        certs = rng.sample(BOOTCAMP_CERTS, min(num_certs, len(BOOTCAMP_CERTS)))
        for c in certs:
            bootcamp_entries.append(c)

    # ---- projects ----
    projects = _projects_for_major()

    # ---- awards ----
    awards = _awards_for_fit()

    # ---- MS courses override ----
    if profile_type == "ms_current":
        if cat == "cs_ds" or major in _PARTIAL_MAJORS[:5]:
            courses = rng.sample(MS_COURSES, rng.randint(4, 7))
        else:
            courses = rng.sample(MBA_MPA_COURSES, rng.randint(4, 6))
    elif profile_type == "phd":
        courses = rng.sample(PHD_COURSES, rng.randint(3, 5)) + rng.sample(MS_COURSES, 2)

    # ---- Objective text -- more realistic student language ----
    if profile_type in ("bs_current", "bs_recent", "bs_career"):
        if fit == "strong":
            objective = (
                f"{'%s ' % standing if standing else ''}"
                f"{deg_level} {deg_field} student at {university} "
                f"looking for an internship where I can apply my programming and data skills. "
                f"I have taken courses in Python, data analysis, and databases and am eager to "
                f"get hands-on experience in industry."
            )
        elif fit == "partial":
            objective = (
                f"{'%s ' % standing if standing else ''}"
                f"{deg_level} {deg_field} student at {university} "
                f"interested in data analysis or technical roles. "
                f"Looking for an opportunity where I can apply my quantitative background "
                f"and continue to grow my skills."
            )
        else:
            objective = (
                f"{'%s ' % standing if standing else ''}"
                f"{deg_level} {deg_field} student at {university} "
                f"seeking an entry-level position where I can contribute and gain experience. "
                f"Hard-working team player with strong communication and organizational skills."
            )
    elif profile_type == "ms_current":
        if major == "MBA/MPA":
            objective = (
                f"{deg_level} candidate in {deg_field} at {university} (expected {grad_year}). "
                f"Looking for a summer internship in business analytics or operations. "
                f"Background in strategy and data-driven decision making."
            )
        elif fit == "strong":
            objective = (
                f"M.S. student in {deg_field} at {university} (expected {grad_year}), "
                f"with B.S. in {bs_info[0]} from {bs_info[1]} ({bs_info[2]}). "
                f"Interested in data engineering and machine learning applications. "
                f"Looking for an internship to apply Python and data skills to real problems."
            )
        else:
            objective = (
                f"M.S. student in {deg_field} at {university} (expected {grad_year}), "
                f"with B.S. in {bs_info[0]} from {bs_info[1]} ({bs_info[2]}). "
                f"Background in quantitative methods. "
                f"Seeking a role in analytics or research where I can grow."
            )
    elif profile_type == "phd":
        objective = (
            f"Ph.D. candidate in {deg_field} at {university}. "
            f"Research focus on machine learning and data systems. "
            f"Looking for an applied research or engineering internship."
        )
    else:  # career_change
        objective = (
            f"Career changer with B.S. in {deg_field} ({grad_year}) looking to move into data. "
            f"Have completed online Python and SQL courses and built a few small personal projects. "
            f"Looking for an entry-level data role where I can learn on the job."
        )

    # ---- Build PDF ----
    MARGIN = 15
    pdf = FPDF()
    pdf.set_margins(MARGIN, MARGIN, MARGIN)
    pdf.set_auto_page_break(auto=True, margin=MARGIN)
    pdf.add_page()
    W = pdf.w - 2 * MARGIN

    # Header
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(W, 11, name, **NL)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(W, 5, f"{email}   |   {phone}   |   {location}", **NL)
    contact_line = f"{linkedin}   |   {github}" if cat == "cs_ds" or profile_type == "career_change" else linkedin
    pdf.cell(W, 5, contact_line, **NL)
    pdf.ln(4)

    # Objective
    section_header(pdf, W, "OBJECTIVE")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(W, 5.5, objective, **NL)
    pdf.ln(3)

    # Education
    section_header(pdf, W, "EDUCATION")
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(W, 6, f"{deg_level} {deg_field}  -  {university}", **NL)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(W, 5.5, status_line, **NL)
    if show_gpa:
        pdf.cell(W, 5.5, f"GPA: {gpa_raw} / 4.0   |   Location: {uni_city}", **NL)
    else:
        pdf.cell(W, 5.5, f"Location: {uni_city}", **NL)
    pdf.set_font("Helvetica", "I", 9)
    pdf.multi_cell(W, 5, f"Relevant Coursework: {', '.join(courses)}", **NL)

    if profile_type == "ms_current" and bs_info:
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(W, 6, f"B.S. {bs_info[0]}  -  {bs_info[1]}", **NL)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(W, 5.5, f"Graduated: {bs_info[2]}", **NL)

    if profile_type == "phd" and bs_info:
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(W, 6, f"M.S. {deg_field}  -  {university}", **NL)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(W, 5.5, f"Graduated: {ms_year2}", **NL)
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(W, 6, f"B.S. {bs_info[0]}  -  {bs_info[1]}", **NL)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(W, 5.5, f"Graduated: {bs_info[2]}", **NL)

    pdf.ln(3)

    # Certifications (career changer)
    if bootcamp_entries:
        section_header(pdf, W, "CERTIFICATIONS AND TRAINING")
        pdf.set_font("Helvetica", "", 10)
        for cert in bootcamp_entries:
            body_line(pdf, W, cert)
        pdf.ln(3)

    # Skills
    section_header(pdf, W, "SKILLS")
    if langs:
        bold_label(pdf, "Languages:", ", ".join(langs), W)
    if libs:
        bold_label(pdf, "Libraries / Frameworks:", ", ".join(libs), W)
    if tools:
        bold_label(pdf, "Tools / Software:", ", ".join(tools), W)
    if data_skills:
        label = "Data Skills:" if fit in ("strong", "partial") else "Core Skills:"
        bold_label(pdf, label, ", ".join(data_skills), W)
    pdf.ln(3)

    # Experience
    if internships or ta_ra_entries:
        section_header(pdf, W, "EXPERIENCE")
        for intern in internships:
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(W, 6, f"{intern['role']}  -  {intern['company']}", **NL)
            pdf.set_font("Helvetica", "I", 9)
            pdf.cell(W, 5, f"{intern['season']} {intern['year']}   |   Internship", **NL)
            pdf.ln(1)
            for b in intern["bullets"]:
                body_line(pdf, W, b)
            pdf.ln(2)
        if ta_ra_entries:
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(W, 6, f"Campus Experience  -  {university}", **NL)
            pdf.ln(1)
            for entry in ta_ra_entries:
                body_line(pdf, W, entry)
            pdf.ln(2)

    # Career changer: prior work experience block
    if profile_type == "career_change":
        section_header(pdf, W, "PRIOR PROFESSIONAL EXPERIENCE")
        prior_roles = [
            f"Staff {major} Specialist  -  {rng.choice(MKT_COMPANIES + FIN_COMPANIES)}",
            f"Associate  -  {rng.choice(HUMANITIES_COMPANIES + PSYCH_COMPANIES)}",
        ]
        for pr in prior_roles[:1]:
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(W, 6, pr, **NL)
            pdf.set_font("Helvetica", "I", 9)
            pdf.cell(W, 5, f"{grad_year + 1} - {grad_year + rng.randint(2, 4)}   |   Full-time", **NL)
            pdf.ln(1)
            pdf.set_font("Helvetica", "", 10)
            prior_bullets = [
                f"Managed {rng.randint(3,8)} concurrent projects and coordinated with the team.",
                f"Produced weekly reports using Excel and presented updates to the team.",
                f"Started teaching myself Python after noticing repetitive manual tasks at work.",
            ]
            for b in prior_bullets:
                body_line(pdf, W, b)
            pdf.ln(2)

    # Projects
    if projects:
        section_header(pdf, W, "PROJECTS")
        for proj in projects:
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(W, 6, proj["title"], **NL)
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(W - 4, 5.5, "  " + proj["desc"], **NL)
            pdf.ln(2)

    # Publications (PhD)
    if pub_info:
        section_header(pdf, W, "PUBLICATIONS")
        pdf.set_font("Helvetica", "", 10)
        for pub in pub_info:
            body_line(pdf, W, pub)
        pdf.ln(2)

    # Awards
    if awards:
        section_header(pdf, W, "AWARDS AND HONORS")
        pdf.set_font("Helvetica", "", 10)
        for award in awards:
            pdf.cell(W, 5.5, f"- {award}", **NL)
        pdf.ln(2)

    filename = f"{OUTPUT_DIR}/{index:03d}_{first}_{last}.pdf"
    pdf.output(filename)
    return filename, profile_type, major, fit


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Generating 100 diverse student/new-grad resumes...")
    counts_type  = {}
    counts_major = {}
    counts_fit   = {"strong": 0, "partial": 0, "weak": 0}
    failed = 0

    for i, (ptype, major) in enumerate(PROFILES, start=1):
        try:
            path, pt, maj, fit = make_resume(i, ptype, major)
            counts_type[pt]  = counts_type.get(pt, 0) + 1
            counts_major[maj] = counts_major.get(maj, 0) + 1
            counts_fit[fit]   = counts_fit.get(fit, 0) + 1
            print(f"  [{i:3d}/100] [{pt:<14}] [{fit:<8}] {maj:<30} -> {path}")
        except Exception as e:
            import traceback
            print(f"  [{i:3d}/100] ERROR ({ptype}, {major}): {e}")
            traceback.print_exc()
            failed += 1

    print(f"\nDone. {100 - failed}/100 PDFs saved to '{OUTPUT_DIR}/'")

    print("\n--- Profile type breakdown ---")
    for k, v in sorted(counts_type.items()):
        print(f"  {k:<16}: {v}")

    print("\n--- Major breakdown ---")
    for k, v in sorted(counts_major.items()):
        print(f"  {k:<35}: {v}")

    print("\n--- Fit level distribution ---")
    for k, v in counts_fit.items():
        print(f"  {k:<10}: {v}")
    print()
    print("Expected score spread against Python/data science JD:")
    print("  Score 8-10 (strong fit - CS/DS with Python): ~", counts_fit.get("strong", 0))
    print("  Score 3-7  (partial fit - STEM-adjacent):    ~", counts_fit.get("partial", 0))
    print("  Score 1-3  (weak fit   - non-STEM/other):    ~", counts_fit.get("weak", 0))
