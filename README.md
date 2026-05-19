# Synthetic AI Data Gen & Analytics Assistant

An AI application which allows users to generate synthetic relational data based on DDL schemas, perform AI-driven data modifications, and interact with the database using natural language to obtain direct answers, SQL queries, or dynamic visualizations.

---

##  Features & Approaches

The application operates through three core orchestrators, each designed for a specific data challenge:

1. **Data Generation**
   * Translates raw DDL schemas into structurally valid synthetic data.
   * Uses configurable LLM temperature and token boundaries to control data diversity and volume.
   * Validates and initializes database tables automatically before populating them.
   * Supports two distinct validation approaches:
   
       * **Direct**: Executes a robust retry cycle: `LLM call -> validation -> feedback loop` (if a validation error occurs, the error message is dynamically appended back into the prompt for the next loop iteration).

       * **Function calling**

3. **Data Editing**
   * Allows quick, natural language instructions to modify, correct, or expand existing synthetic data.
   *  * Supports three distinct validation approaches:
          * **Direct**: Executes a robust retry cycle: `LLM call -> validation -> feedback loop` (if a validation error occurs, the error message is dynamically appended back into the prompt for the next loop iteration).
          * **Function Calling**
          * **Query**: Generates precise SQL modification statements (e.g., `UPDATE`, `INSERT`, `DELETE`) to execute the requested data edits directly within the database.

4. **Talk to Your Data (`talk_to_data.py`)**
   * Analytical interface that strictly translates user queries into database operations or create data visualizations.
   * **Zero-Token Local Execution:** True data is processed locally as a pandas DataFrame. The cloud LLM only acts as the architect (writing code based on schemas), preventing data leaks and heavy cloud token billing.

---

## 📂 Project Structure

```text
├── config/
│   └── config.yaml          # Global application and LLM configuration
├── experiments/
│   └── llm_experiments_log.md  # Prompt engineering and research logs
├── prompts/
│   └── prompts.yaml         # System and User prompt templates 
└── src/
    ├── core/
    │   └── utilts.py        # Core utilities (environment and config loaders, logger)
    ├── database/            # Connection pooling and database initialization handlers
    │   └── database_handler.py
    ├── llm_tools/           # Atomic tools mapped to Google GenAI Function Calling
    │   ├── query_database.py
    │   ├── talk_to_data_tools.py # Tools for query execution and plot structure definition
    │   └── upload_data.py
    └── orchestrators/       # Higher-level managers routing LLM responses to local processes
        ├── approaches/      # Internal logic structures for validation pipelines
        │   ├── engine_direct.py
        │   ├── engine_fc.py
        │   └── engine_query.py
        ├── edit_data.py
        ├── generate_data.py
        └── talk_to_data.py
├── tests/                  # Application testing and validation suite
│   └── edit_mode_tests.md  # Test cases for the data editing
├── app.py                  # Main Streamlit user interface and session state manager
├── .env                    # Local environment secrets (Git ignored)
├── .gitignore              # Specifies intentionally untracked files to ignore from Git version control
├── README.md               # Project documentation and setup guide
└── requirements.txt        # Project dependencies

```

---

## Setup & Installation

### 1. Install Dependencies

Install the required dependencies using:

```bash
pip install -r requirements.txt

```

### 2. Configure Environment Variables

Create a `.env` file in the root directory of the project. See the configuration example below.

### 3. Launch the Application

```bash
streamlit run app.py

```

---

## Configuration Setup

### Application Config (`config/config.yaml`)

Defines validation approaches, token maximums, and specifies the targeted Gemini model from Vertex AI.

```yaml
llm:
  model: 'gemini-3.1-pro-preview'

validation_approaches:
  generating_approach: function_calling   # options: direct / function_calling
  editing_approach: query    # options: direct / function_calling / query

```

### Environment Secrets (`.env` Example)

The application expects database credentials and GCP environment definitions to bind the Google GenAI Client correctly.

```env
# Google Cloud Platform Setup
GCP_PROJECT_ID=your-gcp-project-id

# PostgreSQL Database Connection
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT="5432"
DB_NAME=synthetic_bi_db

```

---

## Usage Lifecycle

1. **Upload Schema:** Start in the **Data Generation** tab by uploading a standard `.sql` or `.ddl` file.
2. **Populate Database:** Provide context-specific instructions, set your generation temperature, and click *Generate*.
3. **Refine & Edit Data:** Use the "Edit instruction" field to modify, expand, or correct the generated synthetic datasets on the fly using natural language commands.
4. **Analyze:** Switch to **Talk to your data**. Ask plain-text analytical questions (e.g., *"Show me the distribution of ratings as a bar chart"*). The frontend automatically displays clean charts, hides underlying relational code when visualizers trigger, and commits chat states to memory safely.
