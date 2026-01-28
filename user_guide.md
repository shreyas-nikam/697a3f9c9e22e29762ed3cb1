id: 697a3f9c9e22e29762ed3cb1_user_guide
summary: Second Line - MRM Lead's Formal Model Tiering & Control Mandate User Guide
feedback link: https://docs.google.com/forms/d/e/1FAIpQLSfWkOK-in_bMMoHSZfcIvAeO58PAH9wrDqcxnJABHaxiDqhSA/viewform?usp=sf_link
environments: Web
status: Published
# QuLab: Formal Model Risk Tiering and Control Mandate

## 1. Navigating Model Risk with QuLab: An Introduction
Duration: 0:05
Welcome to the QuLab application, designed to streamline the critical process of Model Risk Management (MRM) within a financial institution. This codelab will guide you through the perspective of an MRM Lead, demonstrating how to formally tier models and mandate appropriate controls, adhering to regulatory best practices such as SR 11-7 (Supervisory Guidance on Model Risk Management).

In today's data-driven financial landscape, models are ubiquitous, influencing everything from credit decisions to trading strategies. While models offer immense benefits, they also introduce inherent risks—known as Model Risk. This risk arises from potential errors in model development, implementation, or use, which can lead to adverse consequences for the institution. Effectively managing model risk is not just a best practice; it's a regulatory imperative, particularly highlighted by supervisory guidance like SR 11-7 from the Federal Reserve. This guidance emphasizes that banks must have robust frameworks to identify, assess, and manage the risks associated with their models.

This application focuses on two crucial aspects of MRM:
1.  **Formal Model Tiering**: Objectively assessing a model's inherent risk and assigning it a specific "tier" (e.g., High, Medium, Low). This tier dictates the level of scrutiny and resources required for model validation and governance.
2.  **Control Mandate**: Establishing the minimum set of controls and expectations that must be in place, directly linked to the assigned risk tier, to mitigate identified risks.

By the end of this codelab, you will understand how this application facilitates a consistent, transparent, and auditable process for formal model risk tiering and control mandate, ensuring compliance and effective risk management.

<aside class="positive">
<b>Key takeaway:</b> Effective Model Risk Management (MRM) is crucial for financial institutions to prevent adverse outcomes and meet regulatory expectations like SR 11-7.
</aside>

## 2. Ingesting a Model Submission for Review
Duration: 0:08
As an MRM Lead, your journey begins with reviewing a Model Owner's preliminary submission. This initial document provides vital context about the model's purpose, design, and the owner's own assessment of its risk. It's the foundational step that informs your independent evaluation. According to SR 11-7 (Section IV: Model Development, Implementation, and Use), a "clear statement of purpose" and comprehensive documentation are essential. While the owner's preliminary tiering is valuable, it is the Second Line's independent assessment that determines the official tier and corresponding controls.

In this step, you will simulate the ingestion of such a submission.

1.  On the left sidebar, ensure **"1) Ingest Model Submission"** is selected. This is the default starting page.
2.  Locate the file uploader labeled **"Upload Lab 1 Model Registration JSON"**.
3.  Click on the browse button and upload a valid JSON file that represents a model registration.

    For this codelab, we assume you have a sample JSON file, for example, named `model_registration.json`, that adheres to the expected schema. A typical structure for such a file might look like this (you don't need to create this file, just understand its content):
    ```json
    {
        "model_id": "M001",
        "model_name": "Credit Scoring Model v2.0",
        "model_purpose": "To assess creditworthiness of loan applicants and predict default probability.",
        "model_owner": "Jane Doe, Head of Retail Lending",
        "submission_date": "2023-10-26",
        "data_used": ["Customer Demographics", "Credit Bureau Scores", "Transaction History"],
        "owner_narrative": "This model is a critical component of our retail lending decisions, directly impacting customer acquisition and portfolio risk. It has a significant financial impact and is subject to regulatory scrutiny.",
        "key_attributes_for_tiering": {
            "decision_criticality": "High - Direct impact on core business decisions and profitability.",
            "financial_impact": "Material - Potential for significant financial loss in case of error.",
            "data_sensitivity": "Confidential - Uses sensitive customer PII and financial data.",
            "regulatory_materiality": "High - Directly subject to Consumer Protection and Fair Lending laws."
        },
        "owner_preliminary_assessment": {
            "preliminary_risk_tier": "High",
            "rationale": "Given its direct impact on customer lending decisions, use of sensitive data, and regulatory oversight, a 'High' risk tier is appropriate."
        }
    }
    ```
4.  Once uploaded, the application will perform a quick schema validation. If successful, you will see a summary of the model owner's submission displayed, including the model ID, name, purpose, owner, and their preliminary risk assessment.

    Notice the summary section provides a concise overview of the model's intent, critical attributes, and the owner's initial risk perception. This sets the baseline for your independent evaluation. For instance, if the preliminary tier is "High," it suggests a high-impact model, aligning with descriptions of `decision_criticality`, `data_sensitivity`, and `regulatory_materiality`. This initial review confirms the model's significance and the need for a rigorous, formal risk assessment, in line with SR 11-7's guidance on tailoring validation rigor to model materiality (Section V, page 9).

<aside class="negative">
If you encounter an error (e.g., "Invalid JSON format" or "Missing required fields"), please ensure your uploaded file is a valid JSON and contains all the necessary keys as outlined in the example.
</aside>

## 3. Understanding BankCo's Official Tiering Logic
Duration: 0:07
With the model submission ingested, your next step is to understand and apply BankCo's formal, standardized model tiering logic. This logic is crucial because it ensures consistency, transparency, and reproducibility in model risk assessments across the entire organization. It's a direct reflection of SR 11-7's emphasis on strong "Governance, Policies, and Controls" (Section VI, page 16), providing a clear, auditable framework for assessing model risk. This minimizes subjectivity and ensures similar models are tiered consistently.

1.  The application will automatically navigate you to the **"2) Official Tiering"** page once a valid JSON is uploaded.
2.  On this page, you will first see **"BankCo's Official Tiering Logic Version"** displayed. This highlights that the tiering process is based on a formally approved and version-controlled methodology.
3.  Review the **"Risk Factor Weights/Points"** section. This table outlines how different attributes of a model contribute to its overall risk score. For each risk factor (e.g., `decision_criticality`, `financial_impact`), specific values (e.g., "High", "Medium", "Low") are assigned a certain number of points. These points quantify the impact of each attribute.
4.  Examine the **"Official Risk Tier Thresholds"** section. This defines the score ranges that correspond to each official risk tier (e.g., "High", "Medium", "Low"). For example:
    *   **High**: Score $\ge 20$
    *   **Medium**: Score $\ge 10$ and $< 20$
    *   **Low**: Score $< 10$

    The total risk score $S$ for a model is calculated as the sum of points assigned to its various risk attributes.
    $$ S = \sum_{i=1}^{N} P_i $$
    where $P_i$ represents the points assigned to the $i$-th risk attribute based on its specific value.

    This clear, quantitative approach ensures that the tiering process is objective and easily explainable, which is fundamental for regulatory compliance and internal audit. For instance, a model with "High" `decision_criticality` and "Material" `financial_impact` will inherently accrue more points, pushing it towards a higher risk tier.

<aside class="positive">
<b>Important:</b> The defined risk factor weights and tier thresholds are the bedrock of BankCo's formal MRM framework, ensuring objectivity and consistency.
</aside>

## 4. Applying the Formal Tiering Algorithm
Duration: 0:06
Now that you understand BankCo's formal tiering logic, it's time to apply it to the model you just ingested. This is a crucial step where you, as the MRM Lead, independently calculate the model's inherent risk score and assign its authoritative tier. This exercise directly supports SR 11-7's core principle that "The rigor and sophistication of validation should be commensurate with the bank's overall use of models, the complexity and materiality of its models" (Section V, page 9). By objectively tiering the model, you ensure that subsequent model validation activities, monitoring efforts, and governance overhead are appropriately scaled to the actual risk posed by the model.

1.  On the **"2) Official Tiering"** page, click the **"Recompute Official Tier"** button. If this is your first time on this page with an uploaded model, the tiering logic may have already run automatically.
2.  The application will then display the **"Official Model Risk Tiering Results"**.
    *   You'll see the **Official Risk Score** and the corresponding **Official Risk Tier**. These are the definitive outputs of BankCo's formal assessment.
    *   The **Score Breakdown by Factor** table provides transparency, showing how each `key_attribute_for_tiering` from the model owner's submission contributed points to the total score. This breakdown is vital for justifying the final tier.
    *   A **Tiering Decision Rationale** is automatically generated, providing a plain-English explanation for the assigned tier, referencing the factors that contributed to the score.
    *   Finally, the application provides a **Comparison with Model Owner's Preliminary Tier**. This highlights whether the independent assessment aligns with the model owner's initial self-assessment. Alignment is positive, while differences may indicate areas for further discussion to ensure a shared understanding of model risk.

    For example, if the model has been assigned a **High** risk tier with a score of **25**, and the model owner's preliminary assessment was also "High", this signals a strong alignment in risk perception. The score breakdown will show how factors like `decision_criticality` and `regulatory_materiality` contributed significantly to this high score.

This objective, quantitative assessment is paramount for allocating appropriate resources and ensuring compliance with SR 11-7's guidance on tailoring model validation rigor to its risk profile (Section V, page 9). It confirms the model's impact and the need for stringent controls.

## 5. Establishing Minimum Required Control Expectations
Duration: 0:07
With the official Model Risk Tier now assigned, your next responsibility as the MRM Lead is to formally establish the minimum required control expectations for the model. This is a direct implementation of SR 11-7's Section VI: Governance, Policies, and Controls (page 16), which emphasizes that a robust governance framework includes "policies defining relevant risk management activities" and "procedures that implement those policies."

By mapping controls to the assigned tier, BankCo ensures that higher-risk models, like the one we're evaluating, receive the most stringent oversight, including deep independent validation, frequent performance monitoring, and rigorous documentation standards. This systematic approach ensures adequate safeguards are in place and clearly communicates responsibilities to the Model Owner and other stakeholders.

1.  The application will automatically navigate you to the **"3) Required Controls"** page once the official tiering is complete.
2.  On this page, you will see the **"Minimum Required Control Expectations for the Model"** section. This details the controls mandated for the model based on its assigned risk tier.
3.  The **"Detailed Control Checklist"** is presented, often categorized (e.g., Validation, Monitoring, Documentation, Governance). You can expand each category to view the specific `control_id`, `control_name`, `description`, `frequency`, and `owner_role` for each required control.
    *   For a **High** risk model, you would expect to see controls like "Full scope independent validation required annually," "Continuous performance monitoring with quarterly reporting," and "Comprehensive documentation covering all lifecycle stages." These are stringent requirements reflecting the model's significant risk profile.
4.  A **"Summary of Control Expectations"** provides an overarching narrative of the control mandate.

This serves as the formal control mandate. It clearly outlines the high bar for oversight required for this model, aligning directly with SR 11-7's expectations for models with significant materiality. This checklist will be communicated to the Model Owner and relevant support functions, guiding their ongoing responsibilities and ensuring appropriate allocation of resources for validation and monitoring. This ensures "effective challenge" and management of model risk (SR 11-7, Section III, page 4).

## 6. Generating and Exporting Formal Decision Reports
Duration: 0:07
The final step in your workflow as the MRM Lead is to compile and export the formal Tiering Decision Report. This comprehensive report, incorporating the model metadata, the calculated risk score, the assigned official tier, the plain-English rationale, and the associated control expectations, is a critical deliverable. It serves as the official record for internal governance, audit, and regulatory bodies, demonstrating BankCo's adherence to SR 11-7 guidance on "Documentation" (Section VI, page 21). Effective documentation ensures transparency, reproducibility, and clear communication of model risk decisions to all stakeholders, including the Model Owner and AI Program Lead. It provides an auditable trail and cements the clarity needed for ongoing model risk management.

1.  The application will automatically navigate you to the **"4) Export Reports"** page once the controls checklist is generated.
2.  First, you will see a text area labeled **"MRM Lead's Official Rationale (editable)"**. Review the pre-populated rationale, which was generated during the tiering step. You can refine this rationale here to add any additional context or specific considerations. This ensures the final rationale is comprehensive and accurate.
3.  Next, review the **"Preview and Download Reports"** section. The application prepares three distinct reports:
    *   **`risk_tiering.json`**: This is a machine-readable JSON file containing all the details of the official risk tiering, including the score breakdown and the final rationale. This structured data is ideal for integration into BankCo's enterprise model inventory systems or for automated downstream processes.
    *   **`required_controls_checklist.json`**: Another machine-readable JSON, this file contains the full list of mandated controls and their details. It's useful for systems that track control implementation and compliance.
    *   **`executive_summary.md`**: This is a human-readable Markdown file providing a comprehensive summary of the entire process—from model overview to official tiering decision and control expectations. This report is perfect for communication to Model Owners, AI Program Leads, senior management, and for audit purposes.

    Each report is displayed in a preview section.
4.  Click the respective **"Download"** buttons for each report to save them to your local machine. The files will be named using the model ID (e.g., `M001_risk_tiering.json`).

These exportable files are your concrete deliverables. The JSON files provide structured data for automation and integration, while the Markdown summary offers a clear, auditable trail for communication and compliance. This ensures transparency, consistency, and alignment with the comprehensive documentation and governance requirements outlined in SR 11-7 (Section VI, page 16, and Section VII, page 21). This completes your formal assessment and provides the necessary foundation for the ongoing management of the model's risk.
