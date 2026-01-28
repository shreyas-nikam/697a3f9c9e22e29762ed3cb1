Here's a comprehensive `README.md` file for your Streamlit application lab project, designed for developers and users.

---

# QuLab: Second Line - MRM Lead's Formal Model Tiering & Control Mandate

![Streamlit App Screenshot Placeholder](https://via.placeholder.com/800x400?text=Streamlit+App+Screenshot)
*Replace this with an actual screenshot of your running application.*

## Project Description

This Streamlit application, "QuLab: Second Line - MRM Lead's Formal Model Tiering & Control Mandate," simulates the critical workflow of a Model Risk Management (MRM) Lead within a financial institution (BankCo). It serves as a practical lab project demonstrating how the "Second Line of Defense" independently assesses the risk of quantitative models and mandates appropriate controls, strictly adhering to regulatory guidelines such as SR 11-7 (Guidance on Model Risk Management).

The application guides the MRM Lead through a structured process: ingesting model submissions from Model Owners, applying a standardized, deterministic tiering logic to assign an official Model Risk Tier, mapping corresponding control expectations, and finally generating formal documentation. This ensures transparency, consistency, and reproducibility in model risk assessments, minimizing subjectivity and establishing a clear audit trail for compliance.

## Features

The application provides the following key functionalities, organized as a step-by-step workflow for the MRM Lead:

1.  **Ingest Model Submission**:
    *   Uploads a Model Owner's preliminary registration details via a JSON file.
    *   Performs basic schema validation to ensure required fields are present.
    *   Displays a summary of the model's purpose, key attributes, and the owner's preliminary risk assessment.
    *   Provides context aligned with SR 11-7 on the importance of initial review.

2.  **Official Tiering**:
    *   Presents BankCo's predefined, deterministic model risk tiering logic, including risk factor weights and tier thresholds.
    *   Applies this formal logic to the ingested model data to calculate an official risk score and assign a definitive Model Risk Tier.
    *   Displays a detailed breakdown of the score by each risk factor.
    *   Compares the official tier with the Model Owner's preliminary assessment.
    *   Generates an initial plain-English rationale for the tiering decision.

3.  **Required Controls**:
    *   Based on the officially assigned Model Risk Tier, it automatically maps and displays the minimum required control expectations from BankCo's control library.
    *   Presents a detailed, categorized checklist of controls (e.g., Validation, Monitoring, Documentation, Governance).
    *   Provides a summary of the control expectations for the model.

4.  **Export Reports**:
    *   Allows the MRM Lead to review and finalize the rationale for the tiering decision.
    *   Generates and enables download of three crucial artifacts:
        *   `risk_tiering.json`: Structured JSON containing the official tiering results and rationale.
        *   `required_controls_checklist.json`: Structured JSON detailing the mandated controls for the model.
        *   `executive_summary.md`: A human-readable Markdown report summarizing the model overview, official tiering decision, and control expectations.

## Getting Started

Follow these instructions to set up and run the Streamlit application on your local machine.

### Prerequisites

*   Python 3.8+
*   `pip` (Python package installer)

### Installation

1.  **Clone the repository** (if applicable):
    ```bash
    git clone <your-repository-url>
    cd <your-repository-name>
    ```
    *(If not a repository, simply ensure `app.py` and `source.py` are in the same directory.)*

2.  **Create a virtual environment** (recommended):
    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment**:
    *   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

4.  **Install dependencies**:
    ```bash
    pip install streamlit pandas
    ```
    *(`json`, `datetime`, `io` are part of Python's standard library and do not need separate installation.)*

5.  **Ensure `source.py` is present**:
    This application relies on a `source.py` file containing the core business logic, constants, and functions (e.g., `TIERING_LOGIC_VERSION`, `risk_factor_weights`, `tier_thresholds`, `control_expectations_library`, `apply_model_tiering_logic`, `map_controls_to_tier`). This file must be in the same directory as `app.py`.

## Usage

1.  **Run the Streamlit application**:
    Ensure your virtual environment is active and navigate to the directory containing `app.py` and `source.py`. Then run:
    ```bash
    streamlit run app.py
    ```
    This will open the application in your default web browser.

2.  **Follow the Workflow**:
    *   **1) Ingest Model Submission**: Click on "Upload Lab 1 Model Registration JSON" and select a valid JSON file. An example JSON structure is provided below. The application will validate the file and display its contents. Upon successful ingestion, it will automatically advance to the next step.
    *   **2) Official Tiering**: The application will automatically compute and display the official risk tiering results based on BankCo's predefined logic. It will then automatically advance.
    *   **3) Required Controls**: The application will display the minimum required controls mapped to the official risk tier. It will then automatically advance.
    *   **4) Export Reports**: Review the generated rationale (you can edit it) and then download the `risk_tiering.json`, `required_controls_checklist.json`, and `executive_summary.md` files.

### Example Model Submission JSON

To get started, you will need a JSON file structured similar to this example:

```json
{
  "model_id": "MOD-2023-001",
  "model_name": "Credit Risk Scoring Model v2",
  "model_purpose": "Assess creditworthiness of loan applicants for retail banking.",
  "model_owner": "Alice Smith",
  "submission_date": "2023-10-26",
  "data_used": ["Customer Demographics", "Credit Bureau Scores", "Transaction History"],
  "key_attributes_for_tiering": {
    "decision_criticality": "High",
    "regulatory_materiality": "High",
    "data_sensitivity": "High",
    "model_complexity": "Medium",
    "model_transparency": "High"
  },
  "owner_preliminary_assessment": {
    "preliminary_risk_tier": "Tier 1",
    "rationale": "Model directly impacts lending decisions and uses sensitive customer data. Subject to significant regulatory scrutiny."
  },
  "owner_narrative": "This model is a critical component of our retail lending strategy, replacing an older version. It has been thoroughly tested internally and shows improved predictive accuracy. We believe it warrants a 'Tier 1' designation due to its broad impact and data usage, aligning with our internal guidelines for highly material models. Validation efforts are currently underway."
}
```
*Note: The actual `key_attributes_for_tiering` and `owner_preliminary_assessment` keys and values should match the definitions in your `source.py` file for accurate tiering.*

## Project Structure

```
.
├── app.py              # Main Streamlit application script
├── source.py           # Core business logic, constants, and functions for tiering and controls
└── README.md           # This README file
└── example_submission.json # (Optional) Example JSON model submission file
```

## Technology Stack

*   **Python 3.x**: The core programming language.
*   **Streamlit**: For rapidly building and deploying interactive web applications.
*   **Pandas**: Used for data manipulation and displaying tabular data (e.g., score breakdown, control checklists).
*   **JSON**: For handling structured data ingestion and export.
*   **Datetime**: For timestamping generated reports.

## Contributing

Contributions to this lab project are welcome! If you have suggestions for improvements, bug fixes, or new features, please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature-name`).
3.  Make your changes and commit them (`git commit -m 'Add new feature'`).
4.  Push to the branch (`git push origin feature/your-feature-name`).
5.  Open a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
*(Replace `LICENSE` with a link to your actual license file if it exists, otherwise remove this section or state "No License Specified" for a lab project.)*

## Contact

For any questions or further information, please feel free to reach out:

*   **QuantUniversity**: [www.quantuniversity.com](https://www.quantuniversity.com)
*   **Project Maintainer**: [Your Name/GitHub Profile](https://github.com/your-github-profile) (Optional)

---