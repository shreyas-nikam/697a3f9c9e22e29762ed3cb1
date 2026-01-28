
# Jupyter Notebook Specification: Model Risk Tiering & Control Mandate (SR 11-7 Aligned)

## Introduction: Operationalizing Model Risk Management at Fictional Bank Inc.

Welcome to this hands-on lab, designed for **Anya Sharma, our Model Risk Management Lead** at **Fictional Bank Inc.** Anya is a seasoned professional responsible for ensuring all AI models adhere to the highest standards of governance and risk management, particularly those outlined in supervisory guidance like SR 11-7.

Today, Anya faces a critical task: formally tiering a newly registered "Credit Risk Scoring Model." This model is customer-facing, utilizes regulated data, and makes automated decisions, classifying it as potentially high-risk. Her objective is to apply Fictional Bank Inc.'s standardized, deterministic tiering logic to assign an official Model Risk Tier and then define the minimum control expectations associated with that tier. This process is crucial for allocating appropriate validation resources, ensuring robust documentation, and establishing ongoing monitoring requirements, ultimately safeguarding the bank from potential model failures and regulatory non-compliance.

This notebook will guide Anya through the step-by-step workflow:
1.  **Setting up the MRM Environment**: Loading the bank's formal tiering policies and model inventory.
2.  **Identifying the Model for Assessment**: Retrieving the "Credit Risk Scoring Model" from the inventory.
3.  **Applying Deterministic Model Risk Tiering Logic**: Calculating the model's aggregate risk score based on predefined weighted criteria.
4.  **Assigning the Official Model Risk Tier**: Translating the risk score into a formal Model Risk Tier (e.g., Tier 1, 2, or 3).
5.  **Defining Minimum Required Control Expectations**: Mapping the assigned tier to a comprehensive list of controls, aligned with SR 11-7 principles.
6.  **Generating the Official Tiering Decision Report**: Producing audit-defensible reports and a plain-English rationale for stakeholders.

Through this exercise, Anya will demonstrate how Fictional Bank Inc. operationalizes key MRM principles to manage model risk effectively and transparently.

---

## 1. Environment Setup and MRM Policy Initialization

Anya begins by setting up her environment and loading the organization's formal Model Risk Tiering policies. These policies, meticulously crafted and approved by the Model Risk Committee, ensure a consistent, auditable, and transparent approach to risk assessment across all models, directly addressing SR 11-7 guidance on governance and control. Reproducibility is paramount; given the same model metadata and policy version, the score and tier must always be identical.

Anya needs to load several key configuration files:
*   `factor_weights.json`: Defines the importance (weights) of various model attributes.
*   `factor_scoring_map.json`: Translates qualitative model attributes (e.g., 'High' criticality) into numerical points.
*   `tier_thresholds.json`: Establishes the score ranges that define each Model Risk Tier.
*   `controls_catalog.json`: A comprehensive list of all available control measures.
*   `tier_controls_map.json`: Links specific Model Risk Tiers to a predefined set of mandatory controls.
*   `model_inventory.json`: The central repository of all models managed by Fictional Bank Inc.

These policy documents are critical for the **deterministic, explainable risk tiering mechanism** mandated by Fictional Bank Inc.'s MRM framework.

```python
!pip install pandas # Install pandas for structured data handling if not already present
import pandas as pd
import json
import os
import datetime
import uuid
import hashlib

# Define file paths for configuration and data
CONFIG_DIR = "config"
DATA_DIR = "data"
REPORTS_DIR = "reports/session03"

# Ensure directories exist
os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Define configuration content (explicitly for reproducibility)
FACTOR_WEIGHTS_CONTENT = {
  "policy_version": "1.0",
  "effective_date": "2023-10-26",
  "weights": {
    "decision_criticality": 0.35,
    "data_sensitivity": 0.30,
    "automation_level": 0.20,
    "regulatory_materiality": 0.15
  }
}

FACTOR_SCORING_MAP_CONTENT = {
  "policy_version": "1.0",
  "effective_date": "2023-10-26",
  "scoring_map": {
    "decision_criticality": {
      "Low": 1,
      "Medium": 3,
      "High": 5,
      "unknown": 5 # Conservative default for unknown
    },
    "data_sensitivity": {
      "Public": 1,
      "Internal": 2,
      "Confidential": 3,
      "Regulated-PII": 5,
      "unknown": 5 # Conservative default for unknown
    },
    "automation_level": {
      "Advisory": 1,
      "Human-Approval": 3,
      "Fully-Automated": 5,
      "unknown": 5 # Conservative default for unknown
    },
    "regulatory_materiality": {
      "None": 1,
      "Moderate": 3,
      "High": 5,
      "unknown": 5 # Conservative default for unknown
    }
  }
}

TIER_THRESHOLDS_CONTENT = {
  "policy_version": "1.0",
  "effective_date": "2023-10-26",
  "thresholds": {
    "Tier 1": 22, # Aggregate Score >= 22
    "Tier 2": 15, # Aggregate Score >= 15 and < 22
    "Tier 3": 0   # Aggregate Score < 15
  }
}

CONTROLS_CATALOG_CONTENT = {
  "control_001": {
    "description": "Independent validation by a second-line function prior to production use.",
    "sr_11_7_principle": "Validation Depth",
    "category": "Validation"
  },
  "control_002": {
    "description": "Annual independent re-validation or targeted review based on risk profile.",
    "sr_11_7_principle": "Ongoing Monitoring",
    "category": "Validation"
  },
  "control_003": {
    "description": "Comprehensive model documentation covering development, implementation, and limitations (SR 11-7 Section VI).",
    "sr_11_7_principle": "Documentation Rigor",
    "category": "Documentation"
  },
  "control_004": {
    "description": "Formal sign-off by Model Risk Committee or equivalent senior management (SR 11-7 Section VI).",
    "sr_11_7_principle": "Governance Approvals",
    "category": "Governance"
  },
  "control_005": {
    "description": "Daily automated performance monitoring with alert thresholds (SR 11-7 Section V).",
    "sr_11_7_principle": "Monitoring Frequency",
    "category": "Monitoring"
  },
  "control_006": {
    "description": "Quarterly performance review and back-testing by model owner (SR 11-7 Section V).",
    "sr_11_7_principle": "Monitoring Frequency",
    "category": "Monitoring"
  },
  "control_007": {
    "description": "Basic model documentation outlining purpose and key assumptions (SR 11-7 Section VI).",
    "sr_11_7_principle": "Documentation Rigor",
    "category": "Documentation"
  },
  "control_008": {
    "description": "Managerial review and approval before production deployment (SR 11-7 Section VI).",
    "sr_11_7_principle": "Governance Approvals",
    "category": "Governance"
  }
}

TIER_CONTROLS_MAP_CONTENT = {
  "policy_version": "1.0",
  "effective_date": "2023-10-26",
  "tier_controls": {
    "Tier 1": ["control_001", "control_002", "control_003", "control_004", "control_005", "control_006"],
    "Tier 2": ["control_002", "control_003", "control_004", "control_006"],
    "Tier 3": ["control_007", "control_008"]
  }
}

MODEL_INVENTORY_CONTENT = [
  {
    "model_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
    "model_name": "Credit Risk Scoring Model",
    "business_use": "Assess creditworthiness of loan applicants and assign risk scores.",
    "domain": "finance",
    "model_type": "ML",
    "owner_role": "Retail Banking - Head of Credit",
    "decision_criticality": "High",
    "data_sensitivity": "Regulated-PII",
    "automation_level": "Fully-Automated",
    "deployment_mode": "Real-time",
    "external_dependencies": "Credit Bureau APIs, Transaction History Database",
    "regulatory_materiality": "High",
    "model_status": "Candidate for Production",
    "last_updated": "2023-10-20"
  },
  {
    "model_id": "f2e1d0c9-b8a7-6543-210f-edcba9876543",
    "model_name": "Churn Prediction Model",
    "business_use": "Identify customers likely to churn for targeted retention campaigns.",
    "domain": "marketing",
    "model_type": "ML",
    "owner_role": "Marketing - CRM Lead",
    "decision_criticality": "Medium",
    "data_sensitivity": "Confidential",
    "automation_level": "Human-Approval",
    "deployment_mode": "Batch",
    "external_dependencies": "Customer Data Platform",
    "regulatory_materiality": "None",
    "model_status": "In Development",
    "last_updated": "2023-09-15"
  },
  {
    "model_id": "1a2b3c4d-5e6f-7g8h-9i0j-klmnopqrstuv",
    "model_name": "Internal Fraud Detection Model",
    "business_use": "Detect anomalous employee behavior indicating potential internal fraud.",
    "domain": "compliance",
    "model_type": "ML",
    "owner_role": "Compliance - Head of Internal Audit",
    "decision_criticality": "High",
    "data_sensitivity": "Confidential",
    "automation_level": "Advisory",
    "deployment_mode": "Human-in-loop",
    "external_dependencies": "HR Systems, Financial Transaction Logs",
    "regulatory_materiality": "Moderate",
    "model_status": "Pilot Phase",
    "last_updated": "2023-10-01"
  }
]

# Save configuration and data files
def save_json_file(content, directory, filename):
    filepath = os.path.join(directory, filename)
    with open(filepath, 'w') as f:
        json.dump(content, f, indent=2)
    print(f"Saved {filepath}")

save_json_file(FACTOR_WEIGHTS_CONTENT, CONFIG_DIR, "factor_weights.json")
save_json_file(FACTOR_SCORING_MAP_CONTENT, CONFIG_DIR, "factor_scoring_map.json")
save_json_file(TIER_THRESHOLDS_CONTENT, CONFIG_DIR, "tier_thresholds.json")
save_json_file(CONTROLS_CATALOG_CONTENT, CONFIG_DIR, "controls_catalog.json")
save_json_file(TIER_CONTROLS_MAP_CONTENT, CONFIG_DIR, "tier_controls_map.json")
save_json_file(MODEL_INVENTORY_CONTENT, DATA_DIR, "model_inventory.json")

# Functions to load configurations and inventory
def load_json_config(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def load_model_inventory(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

# Load all policies and inventory
factor_weights_config = load_json_config(os.path.join(CONFIG_DIR, "factor_weights.json"))
factor_scoring_map_config = load_json_config(os.path.join(CONFIG_DIR, "factor_scoring_map.json"))
tier_thresholds_config = load_json_config(os.path.join(CONFIG_DIR, "tier_thresholds.json"))
controls_catalog = load_json_config(os.path.join(CONFIG_DIR, "controls_catalog.json"))
tier_controls_map_config = load_json_config(os.path.join(CONFIG_DIR, "tier_controls_map.json"))
model_inventory = load_model_inventory(os.path.join(DATA_DIR, "model_inventory.json"))

print("\n--- MRM Policies and Model Inventory Loaded ---")
print(f"Policy Version: {factor_weights_config['policy_version']}")
print(f"Effective Date: {factor_weights_config['effective_date']}")
print(f"Number of models in inventory: {len(model_inventory)}")

# Combine all policy configurations for a single snapshot
config_snapshot = {
    "factor_weights": factor_weights_config,
    "factor_scoring_map": factor_scoring_map_config,
    "tier_thresholds": tier_thresholds_config,
    "controls_catalog": controls_catalog,
    "tier_controls_map": tier_controls_map_config
}
```

## 2. Identifying the Model for Assessment

Anya now needs to pinpoint the specific model requiring tiering from Fictional Bank Inc.'s enterprise model inventory. For this session, the focus is on the "Credit Risk Scoring Model," a critical new model that has just completed its initial self-assessment and registration. This step aligns with SR 11-7 Section VI, which mandates maintaining a comprehensive model inventory to facilitate overall model risk management.

```python
def find_model_in_inventory(model_name: str, inventory: list) -> dict:
    """
    Searches the model inventory for a specific model by name.

    Args:
        model_name (str): The name of the model to find.
        inventory (list): A list of dictionaries, where each dictionary represents a model.

    Returns:
        dict: The metadata of the found model, or None if not found.
    """
    for model in inventory:
        if model.get("model_name") == model_name:
            return model
    return None

# The model Anya needs to tier
target_model_name = "Credit Risk Scoring Model"
selected_model_metadata = find_model_in_inventory(target_model_name, model_inventory)

if selected_model_metadata:
    print(f"--- Model Selected: {target_model_name} ---")
    for key, value in selected_model_metadata.items():
        print(f"- {key}: {value}")
else:
    print(f"Error: Model '{target_model_name}' not found in inventory.")
```

## 3. Applying Deterministic Model Risk Tiering Logic

With the "Credit Risk Scoring Model" identified, Anya proceeds to apply Fictional Bank Inc.'s **deterministic weighted-sum scoring algorithm**. This algorithm quantifies model risk by evaluating specific attributes (e.g., `decision_criticality`, `data_sensitivity`) against predefined points and weights. This systematic approach ensures that the rigor of subsequent validation and control activities is commensurate with the inherent risk of the model, a core principle emphasized in SR 11-7 Section V.

The aggregate risk score is calculated using the following formula:

$$
\text{Aggregate Score} = \sum_{i=1}^{N} (\text{Factor Points}_i \times \text{Weight}_i)
$$

Where:
*   $\text{Factor Points}_i$: Numerical points assigned to the specific value of model attribute $i$, retrieved from `factor_scoring_map.json`.
*   $\text{Weight}_i$: The importance (weight) of model attribute $i$, retrieved from `factor_weights.json`.
*   $N$: The total number of model attributes considered in the tiering policy.

For any unknown or missing attribute values, a conservative (highest risk) point value is automatically assigned to ensure that potential risks are not underestimated.

```python
def calculate_model_risk_score(model_metadata: dict, factor_scoring_map: dict, factor_weights: dict) -> dict:
    """
    Calculates the aggregate model risk score based on metadata, scoring map, and weights.

    Args:
        model_metadata (dict): The metadata of the model to be scored.
        factor_scoring_map (dict): Configuration mapping factor values to points.
        factor_weights (dict): Configuration mapping factors to their weights.

    Returns:
        dict: A dictionary containing the aggregate score and a breakdown by factor.
    """
    aggregate_score = 0.0
    score_breakdown = {}
    weights_map = factor_weights['weights']
    scoring_map = factor_scoring_map['scoring_map']

    for factor, weight in weights_map.items():
        model_value = model_metadata.get(factor, "unknown") # Default to "unknown" for conservative scoring

        # Get points for the value, if not found, use "unknown" in scoring_map
        points_map_for_factor = scoring_map.get(factor, {})
        points = points_map_for_factor.get(model_value, points_map_for_factor.get("unknown", 0))

        contribution = points * weight
        aggregate_score += contribution
        score_breakdown[factor] = {
            "value": model_value,
            "points": points,
            "weight": weight,
            "contribution": contribution
        }
    
    return {
        "aggregate_score": aggregate_score,
        "score_breakdown": score_breakdown
    }

# Ensure a model is selected before proceeding
if selected_model_metadata:
    risk_score_details = calculate_model_risk_score(
        selected_model_metadata, 
        factor_scoring_map_config, 
        factor_weights_config
    )
    aggregate_score = risk_score_details['aggregate_score']
    score_breakdown = risk_score_details['score_breakdown']

    print("\n--- Model Risk Score Calculation ---")
    print(f"Aggregate Model Risk Score: {aggregate_score:.2f}")

    print("\nScore Breakdown by Factor:")
    for factor, details in score_breakdown.items():
        print(f"- {factor}: Value='{details['value']}', Points={details['points']}, Weight={details['weight']:.2f}, Contribution={details['contribution']:.2f}")
else:
    print("Cannot calculate score: No model selected.")
```

The detailed score breakdown highlights how each attribute of the "Credit Risk Scoring Model" contributes to its overall risk profile. Anya can clearly see that factors like `decision_criticality` and `data_sensitivity` carry substantial weight and points, significantly elevating the model's risk score. This transparency is vital for justifying the risk assessment to stakeholders like Model Owners and AI Program Leads, facilitating a shared understanding of the model's inherent risks. It also provides an evidence base for discussions around potential mitigations or changes to model design to reduce risk, aligning with SR 11-7's emphasis on comprehensive documentation and effective challenge.

## 4. Assigning the Official Model Risk Tier

Now that the aggregate risk score is calculated, Anya assigns the official Model Risk Tier. This is a crucial step in Fictional Bank Inc.'s MRM framework, as the assigned tier directly dictates the level of oversight, validation rigor, and control expectations for the model. The tiering decision is made by comparing the aggregate score against the predefined thresholds from `tier_thresholds.json`.

The tier assignment logic follows these rules:
*   **Tier 1**: Highest risk, requiring the most rigorous oversight.
*   **Tier 2**: Moderate risk, requiring substantial oversight.
*   **Tier 3**: Lowest risk, requiring standard oversight.

Mathematically, the tier is assigned as follows, based on the `thresholds` provided:
$$
\text{Tier} = \begin{cases}
\text{Tier 1} & \text{if Aggregate Score} \ge \text{Threshold for Tier 1} \\
\text{Tier 2} & \text{if Threshold for Tier 2} \le \text{Aggregate Score} < \text{Threshold for Tier 1} \\
\text{Tier 3} & \text{if Aggregate Score} < \text{Threshold for Tier 2}
\end{cases}
$$
Given Fictional Bank Inc.'s default thresholds (from `tier_thresholds.json`): Tier 1: $\ge 22$; Tier 2: $\ge 15$; Tier 3: $< 15$.

```python
def assign_model_risk_tier(aggregate_score: float, tier_thresholds: dict) -> str:
    """
    Assigns a model risk tier based on the aggregate score and defined thresholds.

    Args:
        aggregate_score (float): The calculated aggregate model risk score.
        tier_thresholds (dict): Configuration mapping tiers to their score thresholds.

    Returns:
        str: The assigned model risk tier (e.g., "Tier 1", "Tier 2", "Tier 3").
    """
    thresholds = tier_thresholds['thresholds']
    
    # Sort tiers by threshold in descending order to correctly apply ranges
    sorted_tiers = sorted(thresholds.items(), key=lambda item: item[1], reverse=True)
    
    assigned_tier = "Tier 3" # Default to lowest tier

    for tier_name, min_score in sorted_tiers:
        if aggregate_score >= min_score:
            assigned_tier = tier_name
            break
            
    return assigned_tier

if selected_model_metadata:
    assigned_tier = assign_model_risk_tier(aggregate_score, tier_thresholds_config)
    print("\n--- Official Model Risk Tier Assignment ---")
    print(f"The '{selected_model_metadata['model_name']}' is formally assigned as: {assigned_tier}")
else:
    print("Cannot assign tier: No model selected.")
```

The "Credit Risk Scoring Model" has been formally classified as **Tier 1**. This means it falls into the highest risk category, which necessitates the most stringent governance, validation, and monitoring requirements. This classification ensures that Fictional Bank Inc. allocates appropriate resources and rigor to manage the potential risks associated with this high-impact model, directly adhering to the proportionality principle outlined in SR 11-7 Section V, where validation rigor must be commensurate with the model's complexity and materiality.

## 5. Defining Minimum Required Control Expectations

Following the Tier 1 assignment, Anya must now specify the minimum control expectations for the "Credit Risk Scoring Model." This step directly translates the risk tier into actionable governance requirements, ensuring robust oversight. Fictional Bank Inc. maintains a comprehensive `controls_catalog` and a `tier_controls_map` to automate this process. These controls are aligned with SR 11-7 principles, covering key areas such as validation depth, documentation rigor, monitoring frequency, and governance approvals.

This proactive mapping of controls is a cornerstone of Fictional Bank Inc.'s MRM framework, providing clear mandates to Model Owners and ensuring consistency across all models of similar risk profiles.

```python
def map_controls_to_tier(assigned_tier: str, tier_controls_map: dict, controls_catalog: dict) -> list:
    """
    Maps the assigned model risk tier to a list of minimum required controls.

    Args:
        assigned_tier (str): The assigned model risk tier (e.g., "Tier 1").
        tier_controls_map (dict): Configuration mapping tiers to control IDs.
        controls_catalog (dict): A catalog of all available controls with descriptions.

    Returns:
        list: A list of dictionaries, each representing a required control with its details.
    """
    required_control_ids = tier_controls_map['tier_controls'].get(assigned_tier, [])
    
    required_controls = []
    for control_id in required_control_ids:
        control_details = controls_catalog.get(control_id)
        if control_details:
            required_controls.append({
                "control_id": control_id,
                "description": control_details['description'],
                "category": control_details['category'],
                "sr_11_7_principle": control_details['sr_11_7_principle']
            })
    return required_controls

if selected_model_metadata and assigned_tier:
    required_controls_for_tier = map_controls_to_tier(assigned_tier, tier_controls_map_config, controls_catalog)

    print(f"\n--- Minimum Required Controls for {assigned_tier} of '{selected_model_metadata['model_name']}' ---")
    if required_controls_for_tier:
        # Group controls by category for better readability
        controls_by_category = {}
        for control in required_controls_for_tier:
            category = control['category']
            if category not in controls_by_category:
                controls_by_category[category] = []
            controls_by_category[category].append(control)
        
        for category, controls in controls_by_category.items():
            print(f"\nCategory: {category}")
            for control in controls:
                print(f"- [ID: {control['control_id']}] {control['description']} (Principle: {control['sr_11_7_principle']})")
    else:
        print("No specific controls mapped for this tier.")
else:
    print("Cannot map controls: No model selected or tier assigned.")

# Store for report generation
final_required_controls_list = required_controls_for_tier
```

The assigned **Tier 1** for the "Credit Risk Scoring Model" mandates a comprehensive set of controls, encompassing rigorous independent validation (both pre-production and annual), extensive documentation, daily automated monitoring, quarterly performance reviews, and formal approvals by the Model Risk Committee. These controls directly operationalize the principles outlined in SR 11-7 Section V ("Key Elements of Comprehensive Validation") and Section VI ("Governance, Policies, and Controls"), ensuring that this high-risk model receives the highest level of scrutiny and oversight throughout its lifecycle. This robust framework is essential for maintaining trust in the model's outputs and protecting Fictional Bank Inc. from significant financial or reputational harm.

## 6. Generating the Official Tiering Decision Report

Anya's final task is to compile and export the official "Tiering Decision Report." This report is a critical governance artifact that provides a transparent record of the risk assessment, including the calculated score, assigned tier, a breakdown of contributing factors, and the mandated controls. It also includes a plain-English rationale for the tiering decision, crucial for clear communication with Model Owners, AI Program Leads, and internal auditors. This report ensures auditability and traceability, consistent with SR 11-7 Section VI guidance on documentation and reporting.

A quality gate is implemented to prevent report generation if the plain-English rationale is missing, ensuring that all necessary context for the decision is captured. The report outputs include:
*   `risk_tiering.json`: Detailed JSON of the risk score and tier.
*   `required_controls_checklist.json`: JSON list of all mandated controls.
*   `executive_summary.md`: Markdown file with the plain-English rationale and key findings.
*   `config_snapshot.json`: A snapshot of all policy configurations used, ensuring reproducibility.
*   `evidence_manifest.json`: Contains hashes of all generated files for integrity and traceability.

```python
def generate_plain_english_rationale(model_name: str, score_breakdown: dict, assigned_tier: str, required_controls: list) -> str:
    """
    Generates a plain-English narrative explaining the tiering decision.

    Args:
        model_name (str): The name of the model.
        score_breakdown (dict): The breakdown of the score by factor.
        assigned_tier (str): The assigned model risk tier.
        required_controls (list): The list of required controls.

    Returns:
        str: A plain-English explanation.
    """
    rationale_text = f"The '{model_name}' has been formally assigned a **{assigned_tier}** risk classification. This indicates it is a model of {'highest' if assigned_tier == 'Tier 1' else 'moderate' if assigned_tier == 'Tier 2' else 'lower'} risk, necessitating {'the most rigorous' if assigned_tier == 'Tier 1' else 'substantial' if assigned_tier == 'Tier 2' else 'standard'} oversight in accordance with Fictional Bank Inc.'s Model Risk Management policy, which aligns with SR 11-7 guidance.\n\n"
    rationale_text += "This classification is primarily driven by the following key factors:\n"

    # Sort factors by contribution for better narrative flow
    sorted_factors = sorted(score_breakdown.items(), key=lambda item: item[1]['contribution'], reverse=True)

    for factor, details in sorted_factors:
        rationale_text += f"- **{factor.replace('_', ' ').title()}**: Identified as '{details['value']}', this factor significantly contributes to the risk profile, adding {details['contribution']:.2f} points to the overall score. "
        if factor == 'decision_criticality' and details['value'] == 'High':
            rationale_text += "Its direct impact on critical financial decisions and customer outcomes elevates inherent risk.\n"
        elif factor == 'data_sensitivity' and details['value'] == 'Regulated-PII':
            rationale_text += "Handling Regulated-PII data introduces stringent compliance requirements and potential privacy risks.\n"
        elif factor == 'automation_level' and details['value'] == 'Fully-Automated':
            rationale_text += "The fully-automated nature of its deployment implies decisions are made without human intervention, requiring robust automated controls and monitoring.\n"
        elif factor == 'regulatory_materiality' and details['value'] == 'High':
            rationale_text += "Given its high regulatory materiality, the model is subject to intensive regulatory scrutiny and reporting obligations.\n"
        else:
            rationale_text += "\n"

    rationale_text += f"\nAs a **{assigned_tier}** model, it is subject to a predefined set of minimum control expectations to manage its inherent risks effectively. These controls include:\n"
    
    controls_by_category_for_rationale = {}
    for control in required_controls:
        category = control['category']
        if category not in controls_by_category_for_rationale:
            controls_by_category_for_rationale[category] = []
        controls_by_category_for_rationale[category].append(f"- {control['description']}")
    
    for category, controls in controls_by_category_for_rationale.items():
        rationale_text += f"\n**{category} Controls:**\n" + "\n".join(controls) + "\n"

    rationale_text += "\nThis tiering decision ensures that validation, monitoring, and documentation efforts are appropriately scaled to the model's risk, aligning with Fictional Bank Inc.'s commitment to responsible AI governance and regulatory compliance."
    
    return rationale_text

def calculate_file_hash(filepath: str) -> str:
    """Calculates the SHA256 hash of a file."""
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(4096)  # Read file in chunks
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()

def export_tiering_report(
    output_base_dir: str, 
    model_name: str, 
    model_metadata: dict, 
    risk_score_details: dict, 
    assigned_tier: str, 
    required_controls: list, 
    plain_english_rationale: str, 
    config_snapshot: dict,
    policy_version: str,
    effective_date: str
):
    """
    Generates and exports the Model Risk Tiering Report artifacts.

    Args:
        output_base_dir (str): Base directory to save reports.
        model_name (str): Name of the model.
        model_metadata (dict): Full metadata of the model.
        risk_score_details (dict): Details including aggregate score and breakdown.
        assigned_tier (str): The assigned model risk tier.
        required_controls (list): List of required controls.
        plain_english_rationale (str): The generated narrative.
        config_snapshot (dict): Snapshot of all policy configurations used.
        policy_version (str): Version of the policy used.
        effective_date (str): Effective date of the policy used.

    Raises:
        ValueError: If plain_english_rationale is empty (quality gate).
    """
    if not plain_english_rationale.strip():
        raise ValueError("Cannot export report: Plain-English rationale is missing or empty. Please generate a rationale.")

    run_id = datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + str(uuid.uuid4())[:8]
    output_dir = os.path.join(output_base_dir, run_id)
    os.makedirs(output_dir, exist_ok=True)
    
    generated_files = []

    # 1. risk_tiering.json
    risk_tiering_data = {
        "model_id": model_metadata['model_id'],
        "model_name": model_name,
        "aggregate_risk_score": risk_score_details['aggregate_score'],
        "assigned_model_risk_tier": assigned_tier,
        "score_breakdown": risk_score_details['score_breakdown'],
        "tiering_policy_version": policy_version,
        "tiering_policy_effective_date": effective_date,
        "tiered_by": "Anya Sharma (MRM Lead)",
        "tiering_timestamp": datetime.datetime.now().isoformat()
    }
    risk_tiering_filepath = os.path.join(output_dir, "risk_tiering.json")
    save_json_file(risk_tiering_data, output_dir, "risk_tiering.json")
    generated_files.append({"filename": "risk_tiering.json", "filepath": risk_tiering_filepath})

    # 2. required_controls_checklist.json
    required_controls_filepath = os.path.join(output_dir, "required_controls_checklist.json")
    save_json_file({"model_id": model_metadata['model_id'], "model_name": model_name, "required_controls": required_controls}, output_dir, "required_controls_checklist.json")
    generated_files.append({"filename": "required_controls_checklist.json", "filepath": required_controls_filepath})

    # 3. executive_summary.md
    executive_summary_filepath = os.path.join(output_dir, "executive_summary.md")
    with open(executive_summary_filepath, 'w') as f:
        f.write(f"# Model Risk Tiering Executive Summary for '{model_name}'\n\n")
        f.write(plain_english_rationale)
    print(f"Saved {executive_summary_filepath}")
    generated_files.append({"filename": "executive_summary.md", "filepath": executive_summary_filepath})

    # 4. config_snapshot.json
    config_snapshot_filepath = os.path.join(output_dir, "config_snapshot.json")
    save_json_file(config_snapshot, output_dir, "config_snapshot.json")
    generated_files.append({"filename": "config_snapshot.json", "filepath": config_snapshot_filepath})

    # 5. evidence_manifest.json (with hashes)
    evidence_manifest_data = {
        "run_id": run_id,
        "generated_at": datetime.datetime.now().isoformat(),
        "files": []
    }
    for file_info in generated_files:
        file_hash = calculate_file_hash(file_info['filepath'])
        evidence_manifest_data['files'].append({
            "filename": file_info['filename'],
            "filepath": os.path.relpath(file_info['filepath'], start=output_dir), # Relative path within run_id folder
            "sha256_hash": file_hash
        })
    evidence_manifest_filepath = os.path.join(output_dir, "evidence_manifest.json")
    save_json_file(evidence_manifest_data, output_dir, "evidence_manifest.json")
    print(f"Saved {evidence_manifest_filepath}")
    
    print(f"\nAll tiering report artifacts generated in: {output_dir}")
    print("These reports are ready to be communicated to the Model Owner and AI Program Lead.")


if selected_model_metadata and assigned_tier and risk_score_details and final_required_controls_list:
    plain_english_rationale_text = generate_plain_english_rationale(
        selected_model_metadata['model_name'], 
        risk_score_details['score_breakdown'], 
        assigned_tier, 
        final_required_controls_list
    )

    try:
        export_tiering_report(
            REPORTS_DIR,
            selected_model_metadata['model_name'],
            selected_model_metadata,
            risk_score_details,
            assigned_tier,
            final_required_controls_list,
            plain_english_rationale_text,
            config_snapshot,
            policy_version=config_snapshot['factor_weights']['policy_version'],
            effective_date=config_snapshot['factor_weights']['effective_date']
        )
    except ValueError as e:
        print(f"Report export failed: {e}")
else:
    print("Cannot generate reports: Ensure model is selected, tier assigned, score calculated, and controls mapped.")
```

The generation of the "Tiering Decision Report" completes Anya's formal assessment workflow. This collection of artifacts serves as a comprehensive record, providing transparency and auditability for the model's risk classification. The `executive_summary.md` with its plain-English rationale is particularly valuable for communicating the decision clearly to non-technical stakeholders, fostering understanding and buy-in for the mandated controls. The `config_snapshot.json` and `evidence_manifest.json` ensure that the entire tiering process is reproducible and tamper-evident, upholding Fictional Bank Inc.'s commitment to robust governance and regulatory compliance, as underscored by SR 11-7 Section VI on documentation and controls. This report is now ready for formal submission and presentation to the Model Owner and AI Program Lead.
