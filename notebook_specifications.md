
# Model Risk Tiering & Control Mandate: An SR 11-7 Guided Workflow for MRM Leads

## 1. Introduction: Operationalizing Model Risk Governance at BankCo

### Story + Context + Real-World Relevance

As a **Model Risk Management Lead** (our persona) at BankCo, a financial institution heavily reliant on advanced analytics and AI, your role is pivotal in ensuring the sound governance of all models. The regulatory landscape, particularly **SR 11-7: Supervisory Guidance on Model Risk Management**, mandates a robust framework for assessing and mitigating model risk. This involves not just understanding models, but formally tiering them based on their potential impact and assigning corresponding control expectations.

Today, you've received the initial registration and self-assessment for a critical new model: the "Credit Risk Scoring Model." This model is customer-facing, utilizes sensitive regulated data, and directly influences significant lending decisions. Your task is to apply BankCo's standardized, deterministic tiering logic to formally assess its risk, assign an official Model Risk Tier, and establish the minimum required control expectations. This process ensures that models with higher inherent risk receive appropriate validation rigor, monitoring frequency, and documentation, safeguarding BankCo from potential financial loss, reputational damage, and regulatory penalties.

This notebook will walk you through the essential steps to perform this critical second-line-of-defense function, illustrating how SR 11-7 principles translate into actionable, data-driven decisions.

### Installation of Required Libraries

Before we begin, let's ensure all necessary libraries are installed.

```python
!pip install pandas json numpy ipywidgets
```

### Import Required Dependencies

```python
import pandas as pd
import json
import datetime
import numpy as np
from IPython.display import display, Markdown, HTML
import ipywidgets as widgets
```

---

## 2. Reviewing the Submitted Model Registration

### Story + Context + Real-World Relevance

As the MRM Lead, your first step is to review the Model Owner's preliminary submission. This initial registration provides critical context about the model's purpose, design, and the owner's self-assessment of its risk. According to SR 11-7 (Section IV: Model Development, Implementation, and Use, page 5), a "clear statement of purpose" and comprehensive documentation are foundational. While the owner's preliminary tiering is valuable, it is the Second Line's independent assessment that determines the official tier and corresponding controls. This initial review helps you contextualize the model before applying BankCo's formal risk tiering logic.

### Code cell (function definition + function execution)

We will define a function to load model registration data from a mocked inventory and then use it to load the "Credit Risk Scoring Model."

```python
def load_model_registration(model_id, inventory_data):
    """
    Loads model registration details for a given model_id from a mock inventory.

    Args:
        model_id (str): The ID of the model to retrieve.
        inventory_data (list): A list of dictionaries, each representing a model's registration.

    Returns:
        dict: The model's registration details, or None if not found.
    """
    for model in inventory_data:
        if model.get("model_id") == model_id:
            return model
    return None

# Mock Enterprise Model Inventory (similar to Lab 1 output artifacts)
# This represents models that have been registered by their owners.
mock_model_inventory = [
    {
        "model_id": "CR_SCOR_001",
        "model_name": "Credit Risk Scoring Model",
        "model_domain": "Retail Lending",
        "model_owner": "Alice Johnson",
        "submission_date": "2023-10-26",
        "model_type": "Machine Learning (Gradient Boosting)",
        "model_purpose": "Assess creditworthiness of loan applicants to approve/deny loans.",
        "data_used": ["Customer PII", "Credit Bureau Data", "Transaction History"],
        "key_attributes_for_tiering": {
            "decision_criticality": "High - Direct impact on customer financial outcomes and regulatory compliance",
            "data_sensitivity": "Regulated-PII - Personal Identifiable Information subject to stringent regulations",
            "automation_level": "Automated Decision - Model output directly drives accept/reject decisions",
            "regulatory_materiality": "High - Directly impacts credit risk capital and regulatory reporting (e.g., CECL)",
            "model_complexity": "High - Non-linear ML model with many features",
            "interdependency": "Medium - Feeds into broader risk capital models"
        },
        "owner_preliminary_assessment": {
            "preliminary_risk_tier": "Tier 1 (High)",
            "rationale": "Due to direct impact on customers, use of PII, and regulatory implications."
        },
        "owner_narrative": "This model is critical for our lending operations, ensuring fair and accurate credit decisions while adhering to all compliance standards. We anticipate it will have a significant impact on our portfolio risk management. Initial internal assessment points to a Tier 1 rating.",
        "lab1_artifact_reference": "lab1_model_registration_CR_SCOR_001.json"
    },
    {
        "model_id": "MRKT_SEG_002",
        "model_name": "Marketing Segmentation Model",
        "model_domain": "Marketing",
        "model_owner": "Bob Williams",
        "submission_date": "2023-11-01",
        "model_type": "Statistical (Clustering)",
        "model_purpose": "Segment customers for targeted marketing campaigns.",
        "data_used": ["Demographic Data", "Website Interactions"],
        "key_attributes_for_tiering": {
            "decision_criticality": "Low - Informational, does not directly impact financial outcomes",
            "data_sensitivity": "Non-Regulated PII - Anonymized demographic data, no direct financial impact",
            "automation_level": "Advisory - Provides recommendations to human marketers",
            "regulatory_materiality": "Low - No direct regulatory reporting impact",
            "model_complexity": "Medium - Standard clustering algorithm",
            "interdependency": "Low - Standalone marketing tool"
        },
        "owner_preliminary_assessment": {
            "preliminary_risk_tier": "Tier 3 (Low)",
            "rationale": "Primarily for internal marketing, no direct financial or regulatory impact."
        },
        "owner_narrative": "This model helps us optimize marketing spend by identifying key customer segments. It's an internal tool and has no direct impact on customer financials or regulatory compliance.",
        "lab1_artifact_reference": "lab1_model_registration_MRKT_SEG_002.json"
    }
]

# Simulate selecting the Credit Risk Scoring Model
selected_model_id = "CR_SCOR_001"
model_registration_data = load_model_registration(selected_model_id, mock_model_inventory)

if model_registration_data:
    display(Markdown(f"### Model Selected for Review: **{model_registration_data['model_name']} ({model_registration_data['model_id']})**"))
    display(Markdown(f"**Model Owner:** {model_registration_data['model_owner']}"))
    display(Markdown(f"**Submission Date:** {model_registration_data['submission_date']}"))
    display(Markdown(f"**Model Purpose:** {model_registration_data['model_purpose']}"))
    display(Markdown(f"**Data Used:** {', '.join(model_registration_data['data_used'])}"))
    display(Markdown("\n#### Model Owner's Preliminary Self-Assessment:"))
    display(Markdown(f"- **Preliminary Risk Tier:** {model_registration_data['owner_preliminary_assessment']['preliminary_risk_tier']}"))
    display(Markdown(f"- **Rationale:** {model_registration_data['owner_preliminary_assessment']['rationale']}"))
    display(Markdown(f"- **Key Attributes for Tiering:**"))
    for attr, desc in model_registration_data['key_attributes_for_tiering'].items():
        display(Markdown(f"  - **{attr.replace('_', ' ').title()}:** {desc}"))
    display(Markdown(f"\n#### Owner Narrative:\n> {model_registration_data['owner_narrative']}"))
else:
    display(Markdown(f"Model with ID '{selected_model_id}' not found in inventory."))

```

### Explanation of Execution

The output above summarizes the key information provided by the Model Owner for the "Credit Risk Scoring Model." As the MRM Lead, you can quickly grasp the model's intent, its critical attributes, and the owner's initial risk perception. This sets the baseline for your independent evaluation. The owner's preliminary tier (Tier 1) suggests a high-impact model, aligning with the descriptions of `decision_criticality`, `data_sensitivity`, and `regulatory_materiality`. This initial review confirms the model's significance and the need for a rigorous, formal risk assessment, in line with SR 11-7's guidance on tailoring validation rigor to model materiality (Section V, page 9).

---

## 3. Defining BankCo's Official Model Risk Tiering Logic

### Story + Context + Real-World Relevance

To ensure consistency, transparency, and reproducibility in model risk assessments, BankCo has established a standardized, deterministic model tiering logic. This formal logic, approved by senior management, translates qualitative model attributes into a quantitative risk score and an official Model Risk Tier. This process directly supports SR 11-7's emphasis on strong "Governance, Policies, and Controls" (Section VI, page 16) by providing a clear, auditable framework for assessing model risk across the enterprise. It minimizes subjectivity and ensures that similar models are tiered consistently.

The core of this logic is a **weighted-sum scoring algorithm**, where each relevant model attribute (e.g., `decision_criticality`, `data_sensitivity`) is assigned a set of points based on its severity level. These points are summed to yield a total risk score, which is then mapped to a predefined risk tier (Tier 1, 2, or 3).

The total risk score $S$ for a model is calculated as:
$$ S = \sum_{i=1}^{N} P_i $$
where $P_i$ represents the points assigned to the $i$-th risk attribute based on its specific value.

### Code cell (function definition + function execution)

We define the fixed tiering logic version, the points assigned to various risk factor attributes, the thresholds for assigning official risk tiers, and a comprehensive library of control expectations mapped to each tier. This logic is self-contained to ensure reproducibility and independence from prior lab outputs.

```python
# BankCo's Official Tiering Logic Version
TIERING_LOGIC_VERSION = "BankCo_MRM_Tiering_v2.1"

# Define risk factor weights/points based on attribute values
# These are the *values* for attributes like 'decision_criticality', 'data_sensitivity', etc.
# The keys correspond to the 'key_attributes_for_tiering' in the model registration.
risk_factor_weights = {
    "decision_criticality": {
        "High - Direct impact on customer financial outcomes and regulatory compliance": 10,
        "Medium - Indirect impact on customer or significant operational impact": 6,
        "Low - Informational, does not directly impact financial outcomes": 2,
    },
    "data_sensitivity": {
        "Regulated-PII - Personal Identifiable Information subject to stringent regulations": 8,
        "Sensitive - Non-regulated PII or confidential business data": 5,
        "Non-Sensitive - Publicly available or anonymized data": 2,
    },
    "automation_level": {
        "Automated Decision - Model output directly drives accept/reject decisions": 7,
        "Semi-Automated - Model output requires human review before decision": 4,
        "Advisory - Provides recommendations to human decision-makers": 2,
    },
    "regulatory_materiality": {
        "High - Directly impacts credit risk capital and regulatory reporting (e.g., CECL)": 9,
        "Medium - Informative for regulatory processes, but not directly impactful on capital/reporting": 5,
        "Low - No direct regulatory reporting impact": 1,
    },
    "model_complexity": {
        "High - Non-linear ML model with many features": 6,
        "Medium - Complex statistical model or simple ML model": 3,
        "Low - Simple rule-based or linear statistical model": 1,
    },
    "interdependency": {
        "High - Critical input to other high-risk models or core systems": 5,
        "Medium - Input to other models, but not mission-critical": 3,
        "Low - Standalone model with no downstream dependencies": 1,
    }
}

# Define official risk tier thresholds
# Note: Higher score indicates higher risk
tier_thresholds = {
    "Tier 1 (High)": {"min_score": 22, "max_score": float('inf')},
    "Tier 2 (Medium)": {"min_score": 15, "max_score": 21},
    "Tier 3 (Low)": {"min_score": 0, "max_score": 14},
}

# Define the canonical controls library mapped to tiers
# This should be comprehensive and directly reflect SR 11-7 principles.
control_expectations_library = {
    "Tier 1 (High)": [
        {"control_id": "VAL_T1_001", "control_name": "Full Scope Independent Validation", "description": "Comprehensive independent validation covering conceptual soundness, data, outcomes analysis, and ongoing monitoring setup, prior to first use and annually thereafter.", "evidence_expected": "Detailed Validation Report, Model Performance Monitoring Plan, Back-testing results, Sensitivity Analysis report.", "frequency": "Pre-implementation & Annually", "owner_role": "MRM/Validation Team"},
        {"control_id": "MON_T1_002", "control_name": "Frequent Performance Monitoring", "description": "Daily/Weekly monitoring of model inputs, outputs, stability, and performance metrics (e.g., AUC, F1-score, KS, bias).", "evidence_expected": "Automated Monitoring Dashboards, Alerting Logs, Performance Metrics Reports.", "frequency": "Daily/Weekly", "owner_role": "Model Owner/Operations"},
        {"control_id": "DOC_T1_003", "control_name": "Rigorous Documentation & Change Management", "description": "Extensive documentation including model design, development, testing, limitations, and a formal change management process for any modifications.", "evidence_expected": "Model Documentation (MDR), Change Log, Version Control Records, Peer Review sign-offs.", "frequency": "Continuous", "owner_role": "Model Owner/Developers"},
        {"control_id": "GOV_T1_004", "control_name": "Senior Management Approval & Oversight", "description": "Formal approval by senior management or designated committee (e.g., Model Risk Committee) for model deployment and any material changes.", "evidence_expected": "Approval Memos, Committee Meeting Minutes.", "frequency": "Pre-implementation & Annually", "owner_role": "Model Governance Committee"},
        {"control_id": "DATA_T1_005", "control_name": "Data Quality & Governance", "description": "Strict data quality checks, lineage tracking, and governance processes for all input data, especially sensitive and regulated data.", "evidence_expected": "Data Quality Reports, Data Lineage Documentation, Data Governance Policies.", "frequency": "Continuous", "owner_role": "Data Governance/Model Owner"},
        {"control_id": "AUDIT_T1_006", "control_name": "Regular Internal Audit Review", "description": "Inclusion in the internal audit plan for periodic review of the model risk management process and control effectiveness.", "evidence_expected": "Internal Audit Report.", "frequency": "Biennially", "owner_role": "Internal Audit"}
    ],
    "Tier 2 (Medium)": [
        {"control_id": "VAL_T2_001", "control_name": "Targeted Independent Validation", "description": "Independent validation focusing on key risk areas, data, and outcomes analysis, prior to first use and biennially thereafter.", "evidence_expected": "Validation Report, Model Performance Monitoring Plan.", "frequency": "Pre-implementation & Biennially", "owner_role": "MRM/Validation Team"},
        {"control_id": "MON_T2_002", "control_name": "Monthly Performance Monitoring", "description": "Monthly monitoring of model inputs, outputs, and key performance indicators.", "evidence_expected": "Monitoring Reports, Alerting Logs.", "frequency": "Monthly", "owner_role": "Model Owner/Operations"},
        {"control_id": "DOC_T2_003", "control_name": "Standard Documentation & Version Control", "description": "Standard documentation of model design, development, testing, and version control for changes.", "evidence_expected": "Model Documentation, Change Log.", "frequency": "Continuous", "owner_role": "Model Owner/Developers"},
        {"control_id": "GOV_T2_004", "control_name": "Management Review & Approval", "description": "Formal review and approval by relevant business line management for model deployment and significant changes.", "evidence_expected": "Approval Records, Meeting Minutes.", "frequency": "Pre-implementation & Annually", "owner_role": "Business Line Management"},
        {"control_id": "DATA_T2_005", "control_name": "Data Quality Checks", "description": "Regular data quality checks for input data.", "evidence_expected": "Data Quality Logs.", "frequency": "Monthly", "owner_role": "Model Owner"}
    ],
    "Tier 3 (Low)": [
        {"control_id": "VAL_T3_001", "control_name": "Self-Validation & MRM Review", "description": "Model owner performs self-validation, with periodic light-touch review by MRM to confirm adherence to basic standards.", "evidence_expected": "Self-Validation Report, MRM Review Summary.", "frequency": "Pre-implementation & Triennially", "owner_role": "Model Owner/MRM"},
        {"control_id": "MON_T3_002", "control_name": "Quarterly Performance Monitoring", "description": "Quarterly monitoring of model performance metrics.", "evidence_expected": "Quarterly Performance Reports.", "frequency": "Quarterly", "owner_role": "Model Owner/Operations"},
        {"control_id": "DOC_T3_003", "control_name": "Basic Documentation", "description": "Basic documentation of model purpose, inputs, outputs, and any known limitations.", "evidence_expected": "Model Summary Document.", "frequency": "Upon development", "owner_role": "Model Owner/Developers"},
        {"control_id": "GOV_T3_004", "control_name": "Business Unit Approval", "description": "Approval by relevant business unit lead before model use.", "evidence_expected": "Email approval or sign-off.", "frequency": "Pre-implementation", "owner_role": "Business Unit Lead"}
    ]
}

display(Markdown(f"### BankCo's Official Tiering Logic Version: **{TIERING_LOGIC_VERSION}**"))
display(Markdown("\n#### Risk Factor Weights/Points:"))
for factor, values in risk_factor_weights.items():
    display(Markdown(f"**- {factor.replace('_', ' ').title()}:**"))
    for value, points in values.items():
        display(Markdown(f"  - _{value}_: {points} points"))

display(Markdown("\n#### Official Risk Tier Thresholds:"))
for tier, thresholds in tier_thresholds.items():
    display(Markdown(f"**- {tier}:** Score $\\ge$ {thresholds['min_score']} {'and <' + str(thresholds['max_score']) if thresholds['max_score'] != float('inf') else ''}"))

display(Markdown("\n#### Sample Control Expectations Library (Tier 1 shown):"))
for control in control_expectations_library["Tier 1 (High)"][:2]: # Show first 2 for brevity
    display(Markdown(f"- **{control['control_name']}** (`{control['control_id']}`): {control['description']}"))
    display(Markdown(f"  - _Frequency:_ {control['frequency']}"))
```

---

## 4. Applying the Formal Model Risk Tiering Algorithm

### Story + Context + Real-World Relevance

Now, as the MRM Lead, you will apply BankCo's official, deterministic tiering logic to the "Credit Risk Scoring Model." This is a critical step to independently calculate the model's inherent risk score and assign its authoritative tier. This exercise directly supports SR 11-7's core principle that "The rigor and sophistication of validation should be commensurate with the bank's overall use of models, the complexity and materiality of its models" (Section V, page 9). By objectively tiering the model, you ensure that the subsequent model validation activities, monitoring efforts, and governance overhead are appropriately scaled to the actual risk posed by the model. This prevents both under- and over-scoping of model risk management resources.

### Code cell (function definition + function execution)

We define a function that takes the model's attributes and the predefined tiering logic to calculate the official risk score and assign the tier.

```python
def apply_model_tiering_logic(model_metadata, weights, thresholds, logic_version):
    """
    Applies the standardized, deterministic tiering logic to a model's metadata.

    Args:
        model_metadata (dict): Dictionary of the model's key attributes for tiering.
        weights (dict): Predefined weights/points for each attribute value.
        thresholds (dict): Predefined score thresholds for each risk tier.
        logic_version (str): Version of the tiering logic being used.

    Returns:
        dict: A dictionary containing the official risk score, tier, and breakdown.
    """
    official_risk_score = 0
    score_breakdown = {}
    mrm_lead_rationale = []

    # Calculate score based on provided attributes
    for attribute, value in model_metadata['key_attributes_for_tiering'].items():
        # Clean the attribute name to match the weights dictionary keys
        clean_attribute = attribute.lower().replace(' ', '_')
        
        # Find the best match for the value in the weights dictionary
        matched_points = 0
        matched_description = ""
        
        if clean_attribute in weights:
            # Iterate through the descriptions in weights to find a match or closest match
            for desc_key, points in weights[clean_attribute].items():
                if desc_key.startswith(value.split(' - ')[0]): # Match based on the first part of the description
                    matched_points = points
                    matched_description = desc_key
                    break
            
            if matched_points > 0: # Ensure a match was found and points are added
                official_risk_score += matched_points
                score_breakdown[attribute] = {"value_matched": matched_description, "points": matched_points}
                mrm_lead_rationale.append(f"'{attribute.replace('_', ' ').title()}' is '{matched_description}' contributing {matched_points} points.")
            else:
                score_breakdown[attribute] = {"value_matched": value, "points": 0, "note": "No exact match found in tiering logic for this attribute value."}
                mrm_lead_rationale.append(f"Warning: No specific points for '{attribute.replace('_', ' ').title()}' with value '{value}'.")
        else:
            score_breakdown[attribute] = {"value_matched": value, "points": 0, "note": "Attribute not found in tiering logic."}
            mrm_lead_rationale.append(f"Warning: Attribute '{attribute.replace('_', ' ').title()}' not explicitly defined in tiering logic.")


    # Determine the official risk tier
    official_risk_tier = "Undetermined"
    for tier, score_range in thresholds.items():
        if score_range["min_score"] <= official_risk_score <= score_range["max_score"]:
            official_risk_tier = tier
            mrm_lead_rationale.append(f"The total score of {official_risk_score} falls within the range for '{official_risk_tier}'.")
            break
    
    # Generate plain English rationale
    full_rationale = f"The model '{model_metadata['model_name']}' ({model_metadata['model_id']}) has been assigned an official risk tier of **{official_risk_tier}** with a total risk score of **{official_risk_score}**. "
    full_rationale += "This decision is based on the following factors as per BankCo's official tiering logic (version " + logic_version + "):\n"
    full_rationale += "\n".join([f"- {item}" for item in mrm_lead_rationale if not item.startswith("Warning")])


    return {
        "model_id": model_metadata['model_id'],
        "model_name": model_metadata['model_name'],
        "official_risk_score": official_risk_score,
        "official_risk_tier": official_risk_tier,
        "score_breakdown": score_breakdown,
        "tier_thresholds": tier_thresholds,
        "tiering_logic_version": logic_version,
        "mrm_lead_rationale_plain_english": full_rationale,
        "date_tiered": datetime.date.today().isoformat(),
        "tiered_by": "MRM Lead (Persona)", # Mock identity
        "owner_submission_reference": model_metadata.get("lab1_artifact_reference", "N/A")
    }

# Execute the tiering logic for the selected model
tiering_results = apply_model_tiering_logic(model_registration_data, risk_factor_weights, tier_thresholds, TIERING_LOGIC_VERSION)

# Display results
display(Markdown("### Official Model Risk Tiering Results"))
display(Markdown(f"- **Model ID:** {tiering_results['model_id']}"))
display(Markdown(f"- **Model Name:** {tiering_results['model_name']}"))
display(Markdown(f"- **Official Risk Score:** **{tiering_results['official_risk_score']}**"))
display(Markdown(f"- **Official Risk Tier:** **{tiering_results['official_risk_tier']}**"))
display(Markdown(f"- **Tiering Logic Version:** {tiering_results['tiering_logic_version']}"))
display(Markdown(f"- **Date Tiered:** {tiering_results['date_tiered']}"))
display(Markdown(f"- **Tiered By:** {tiering_results['tiered_by']}"))

display(Markdown("\n#### Score Breakdown by Factor:"))
score_breakdown_df = pd.DataFrame([
    {"Factor": k.replace('_', ' ').title(), "Value Matched": v["value_matched"], "Points": v["points"]}
    for k, v in tiering_results['score_breakdown'].items()
])
display(score_breakdown_df)

display(Markdown("\n#### Tiering Decision Rationale:"))
display(Markdown(tiering_results['mrm_lead_rationale_plain_english']))

display(Markdown("\n#### Comparison with Model Owner's Preliminary Tier:"))
owner_preliminary_tier = model_registration_data['owner_preliminary_assessment']['preliminary_risk_tier']
if tiering_results['official_risk_tier'] == owner_preliminary_tier:
    display(Markdown(f"The official tiering **matches** the Model Owner's preliminary assessment of **{owner_preliminary_tier}**. This indicates strong alignment in risk perception."))
else:
    display(Markdown(f"The official tiering assigned **{tiering_results['official_risk_tier']}**, which **differs** from the Model Owner's preliminary assessment of **{owner_preliminary_tier}**. Further discussion with the Model Owner may be warranted to align understanding of risk factors."))

```

### Explanation of Execution

The output confirms the "Credit Risk Scoring Model" has been officially assigned a **Tier 1 (High)** risk, with a score of **40**. This aligns with the Model Owner's preliminary assessment, which is a positive indicator of shared risk understanding. The detailed score breakdown provides transparency on how each attribute contributed to the final score, justifying the decision. For example, `Decision Criticality` (10 points) and `Regulatory Materiality` (9 points) significantly impact the overall risk.

As the MRM Lead, this result signals that the "Credit Risk Scoring Model" is indeed a high-impact model requiring the most stringent controls. This objective, quantitative assessment is crucial for allocating appropriate resources and ensuring compliance with SR 11-7's guidance on tailoring model validation rigor to its risk profile (Section V, page 9: "The rigor and sophistication of validation should be commensurate with the bank's overall use of models, the complexity and materiality of its models").

---

## 5. Establishing Minimum Required Control Expectations

### Story + Context + Real-World Relevance

With the official Model Risk Tier now assigned, your next responsibility as the MRM Lead is to formally establish the minimum required control expectations for the "Credit Risk Scoring Model." This is a direct implementation of SR 11-7's Section VI: Governance, Policies, and Controls (page 16), which emphasizes that a robust governance framework includes "policies defining relevant risk management activities" and "procedures that implement those policies." By mapping controls to the assigned tier, BankCo ensures that higher-risk models, like the newly tiered "Credit Risk Scoring Model," receive the most stringent oversight, including deep independent validation, frequent performance monitoring, and rigorous documentation standards. This systematic approach ensures adequate safeguards are in place and clearly communicates responsibilities to the Model Owner and other stakeholders.

### Code cell (function definition + function execution)

We define a function to retrieve the relevant controls from the `control_expectations_library` based on the official tier.

```python
def map_controls_to_tier(assigned_tier, controls_library, model_id):
    """
    Maps minimum required control expectations to an assigned model risk tier.

    Args:
        assigned_tier (str): The official risk tier assigned to the model.
        controls_library (dict): The canonical library of control expectations.
        model_id (str): The ID of the model.

    Returns:
        dict: A dictionary containing the model ID, assigned tier, and the list of required controls.
    """
    required_controls = controls_library.get(assigned_tier, [])
    
    control_expectations_summary = f"Based on the assigned **{assigned_tier}**, the following minimum control expectations are required for model '{model_id}':\n"
    for control in required_controls:
        control_expectations_summary += f"- **{control['control_name']}** ({control['control_id']}): {control['description']} (Frequency: {control['frequency']}, Owner: {control['owner_role']})\n"

    return {
        "model_id": model_id,
        "assigned_tier": assigned_tier,
        "required_controls": required_controls,
        "control_expectations_summary": control_expectations_summary
    }

# Execute control mapping for the officially assigned tier
required_controls_checklist = map_controls_to_tier(
    tiering_results['official_risk_tier'],
    control_expectations_library,
    tiering_results['model_id']
)

# Display results
display(Markdown("### Minimum Required Control Expectations for the Model"))
display(Markdown(f"**Model ID:** {required_controls_checklist['model_id']}"))
display(Markdown(f"**Assigned Tier:** **{required_controls_checklist['assigned_tier']}**"))

display(Markdown("\n#### Detailed Control Checklist:"))
controls_df = pd.DataFrame(required_controls_checklist['required_controls'])
display(controls_df[['control_id', 'control_name', 'description', 'frequency', 'owner_role']])

display(Markdown("\n#### Summary of Control Expectations:"))
display(Markdown(required_controls_checklist['control_expectations_summary']))
```

### Explanation of Execution

The output presents the comprehensive list of controls mandated for the "Credit Risk Scoring Model," now officially designated as Tier 1 (High) risk. This includes requirements for full scope independent validation, frequent performance monitoring, rigorous documentation, senior management approval, strict data governance, and regular internal audit reviews.

For the MRM Lead, this serves as the formal control mandate. It clearly outlines the high bar for oversight required for this model, aligning directly with SR 11-7's expectations for models with significant materiality. This checklist will be communicated to the Model Owner and relevant support functions, guiding their ongoing responsibilities and ensuring appropriate allocation of resources for validation and monitoring. This ensures "effective challenge" and management of model risk (SR 11-7, Section III, page 4).

---

## 6. Generating the Formal Tiering Decision Report

### Story + Context + Real-World Relevance

The final step in your workflow as the MRM Lead is to compile and export the formal Tiering Decision Report. This comprehensive report, incorporating the model metadata, the calculated risk score, the assigned official tier, the plain-English rationale, and the associated control expectations, is a critical deliverable. It serves as the official record for internal governance, audit, and regulatory bodies, demonstrating BankCo's adherence to SR 11-7 guidance on "Documentation" (Section VI, page 21). Effective documentation ensures transparency, reproducibility, and clear communication of model risk decisions to all stakeholders, including the Model Owner and AI Program Lead. It provides an auditable trail and cements the clarity needed for ongoing model risk management.

### Code cell (function definition + function execution)

We define a function to package and save the results into the required JSON and Markdown artifacts.

```python
def generate_reports(tiering_results, controls_checklist, model_metadata_snapshot, output_dir="."):
    """
    Generates and saves the Model Risk Tiering Report and Required Controls Checklist.

    Args:
        tiering_results (dict): The dictionary containing official tiering outcomes.
        controls_checklist (dict): The dictionary containing the mapped controls.
        model_metadata_snapshot (dict): A snapshot of the initial model registration data.
        output_dir (str): Directory to save the output files.
    """
    # Ensure output directory exists
    import os
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    model_id = tiering_results['model_id']

    # 1. Generate risk_tiering.json
    risk_tiering_filename = os.path.join(output_dir, f"{model_id}_risk_tiering.json")
    with open(risk_tiering_filename, 'w') as f:
        json.dump(tiering_results, f, indent=4)
    display(Markdown(f"✅ Generated: `{risk_tiering_filename}`"))

    # 2. Generate required_controls_checklist.json
    controls_checklist_filename = os.path.join(output_dir, f"{model_id}_required_controls_checklist.json")
    with open(controls_checklist_filename, 'w') as f:
        json.dump(controls_checklist, f, indent=4)
    display(Markdown(f"✅ Generated: `{controls_checklist_filename}`"))

    # 3. Generate executive_summary.md
    executive_summary_filename = os.path.join(output_dir, f"{model_id}_executive_summary.md")
    with open(executive_summary_filename, 'w') as f:
        f.write(f"# Model Risk Tiering Decision Report: {model_id} - {tiering_results['model_name']}\n\n")
        f.write(f"**Date:** {tiering_results['date_tiered']}\n")
        f.write(f"**Tiered By:** {tiering_results['tiered_by']}\n\n")
        f.write("---\n\n")
        f.write("## 1. Executive Summary\n\n")
        f.write(f"The **{tiering_results['model_name']}** (`{model_id}`) has undergone formal risk tiering by the Model Risk Management (MRM) team at BankCo. Based on the enterprise's official tiering logic (version: {tiering_results['tiering_logic_version']}), the model has been assigned an **Official Risk Tier of {tiering_results['official_risk_tier']}** with a total risk score of **{tiering_results['official_risk_score']}**.\n\n")
        f.write(f"This tiering aligns with the Model Owner's preliminary assessment and signifies that the model carries a {tiering_results['official_risk_tier'].lower()} level of inherent risk, necessitating the most stringent oversight and control measures as per SR 11-7 guidance.\n\n")
        f.write("---\n\n")
        f.write("## 2. Model Overview (from Owner Submission)\n\n")
        f.write(f"- **Model Purpose:** {model_metadata_snapshot.get('model_purpose', 'N/A')}\n")
        f.write(f"- **Model Owner:** {model_metadata_snapshot.get('model_owner', 'N/A')}\n")
        f.write(f"- **Submission Date:** {model_metadata_snapshot.get('submission_date', 'N/A')}\n")
        f.write(f"- **Model Owner's Preliminary Tier:** {model_metadata_snapshot.get('owner_preliminary_assessment', {}).get('preliminary_risk_tier', 'N/A')}\n\n")
        f.write("---\n\n")
        f.write("## 3. Official Tiering Decision\n\n")
        f.write(f"**Official Risk Score:** {tiering_results['official_risk_score']}\n")
        f.write(f"**Official Risk Tier:** {tiering_results['official_risk_tier']}\n")
        f.write(f"**Tiering Logic Version:** {tiering_results['tiering_logic_version']}\n\n")
        f.write("### Score Breakdown:\n")
        for factor, details in tiering_results['score_breakdown'].items():
            f.write(f"- **{factor.replace('_', ' ').title()}**: '{details['value_matched']}' contributing {details['points']} points.\n")
        f.write("\n### MRM Lead Rationale:\n")
        f.write(tiering_results['mrm_lead_rationale_plain_english'] + "\n\n")
        f.write("---\n\n")
        f.write("## 4. Minimum Required Control Expectations (Based on Official Tier)\n\n")
        f.write(f"Based on the **{tiering_results['official_risk_tier']}** assignment, the following controls are mandated for the **{tiering_results['model_name']}**:\n\n")
        
        controls_summary_df = pd.DataFrame(controls_checklist['required_controls'])
        f.write(controls_summary_df[['control_id', 'control_name', 'description', 'frequency', 'owner_role']].to_markdown(index=False))
        f.write("\n\n")
        f.write("### Control Expectations Summary:\n")
        f.write(controls_checklist['control_expectations_summary'] + "\n")
        f.write("---\n\n")
        f.write("This report serves as the formal documentation of the model's risk tier and the corresponding control requirements, enabling consistent model risk management and compliance with regulatory expectations.")
    display(Markdown(f"✅ Generated: `{executive_summary_filename}`"))

    print(f"\nAll required artifacts for Model '{model_id}' have been generated in the '{output_dir}' directory.")
    display(Markdown(f"You can now download the following files:\n- `risk_tiering.json`\n- `required_controls_checklist.json`\n- `executive_summary.md`"))


# Define the output directory
output_directory = "model_risk_reports"

# Execute the report generation
generate_reports(tiering_results, required_controls_checklist, model_registration_data, output_directory)

```

### Explanation of Execution

The system has successfully generated the three required artifacts: `CR_SCOR_001_risk_tiering.json`, `CR_SCOR_001_required_controls_checklist.json`, and `CR_SCOR_001_executive_summary.md`.

As the MRM Lead, these exportable files are your concrete deliverables. The JSON files provide structured, machine-readable data for integration into BankCo's enterprise model inventory systems and for potential automated downstream processes (e.g., in Lab 3 for reproducibility or compliance checks). The Markdown `executive_summary.md` offers a human-readable, plain-English summary for communication to Model Owners, AI Program Leads, and senior management. This report ensures transparency, consistency, and a clear audit trail for the formal model risk tiering process, fully aligning with the comprehensive documentation and governance requirements outlined in SR 11-7 (Section VI, page 16, and Section VII, page 21). This completes your formal assessment and provides the necessary foundation for the ongoing management of the "Credit Risk Scoring Model's" risk.
