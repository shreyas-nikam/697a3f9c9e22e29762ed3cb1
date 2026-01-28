import pandas as pd
import json
import datetime
import os
import numpy as np


def normalize_lab1_to_lab2(payload: dict) -> dict:
    """
    Convert Lab 1 export artifact into Lab 2 expected schema.
    Maps Lab 1's simple values (Low/Medium/High) to Lab 2's detailed descriptions.
    """
    # If it's already in Lab 2 shape, return as-is
    if "key_attributes_for_tiering" in payload and "owner_preliminary_assessment" in payload:
        return payload

    # Mapping from Lab 1 simple values to Lab 2 detailed descriptions
    decision_criticality_map = {
        "Low": "Low - Informational, does not directly impact financial outcomes",
        "Medium": "Medium - Indirect impact on customer or significant operational impact",
        "High": "High - Direct impact on customer financial outcomes and regulatory compliance"
    }

    data_sensitivity_map = {
        "Public": "Non-Sensitive - Publicly available or anonymized data",
        "Internal": "Sensitive - Non-regulated PII or confidential business data",
        "Confidential": "Sensitive - Non-regulated PII or confidential business data",
        "Regulated-PII": "Regulated-PII - Personal Identifiable Information subject to stringent regulations"
    }

    automation_level_map = {
        "Manual": "Advisory - Provides recommendations to human decision-makers",
        "Human-in-the-loop": "Semi-Automated - Model output requires human review before decision",
        "Fully-Automated": "Automated Decision - Model output directly drives accept/reject decisions"
    }

    regulatory_materiality_map = {
        "None": "Low - No direct regulatory reporting impact",
        "Low": "Low - No direct regulatory reporting impact",
        "Medium": "Medium - Informative for regulatory processes, but not directly impactful on capital/reporting",
        "High": "High - Directly impacts credit risk capital and regulatory reporting (e.g., CECL)"
    }

    # Map risk factors from Lab 1 to Lab 2 format
    key_attrs = {}

    if "decision_criticality" in payload and payload["decision_criticality"]:
        key_attrs["decision_criticality"] = decision_criticality_map.get(
            payload["decision_criticality"],
            payload["decision_criticality"]
        )

    if "data_sensitivity" in payload and payload["data_sensitivity"]:
        key_attrs["data_sensitivity"] = data_sensitivity_map.get(
            payload["data_sensitivity"],
            payload["data_sensitivity"]
        )

    if "automation_level" in payload and payload["automation_level"]:
        key_attrs["automation_level"] = automation_level_map.get(
            payload["automation_level"],
            payload["automation_level"]
        )

    if "regulatory_materiality" in payload and payload["regulatory_materiality"]:
        key_attrs["regulatory_materiality"] = regulatory_materiality_map.get(
            payload["regulatory_materiality"],
            payload["regulatory_materiality"]
        )

    # Add model_complexity and interdependency if present (these are optional)
    if "model_complexity" in payload and payload["model_complexity"]:
        key_attrs["model_complexity"] = payload["model_complexity"]

    if "interdependency" in payload and payload["interdependency"]:
        key_attrs["interdependency"] = payload["interdependency"]

    # Map proposed_risk_tier from Lab 1 to preliminary_risk_tier in Lab 2
    prelim_tier = payload.get("proposed_risk_tier") or payload.get(
        "preliminary_risk_tier") or "Tier 3"

    normalized = {
        "model_id": payload.get("model_id"),
        "model_name": payload.get("model_name"),
        "model_domain": payload.get("domain") or payload.get("model_domain"),
        "model_owner": payload.get("created_by") or payload.get("model_owner") or "System/Unknown Owner",
        "submission_date": payload.get("created_at") or payload.get("submission_date") or payload.get("registration_timestamp"),
        "model_type": payload.get("model_type"),
        "model_purpose": payload.get("business_use") or payload.get("model_purpose"),
        "data_used": payload.get("data_used") or payload.get("data_sources") or [],
        "key_attributes_for_tiering": key_attrs,
        "owner_preliminary_assessment": {
            "preliminary_risk_tier": prelim_tier,
            "rationale": payload.get("owner_risk_narrative") or payload.get("owner_preliminary_rationale") or ""
        },
        "owner_narrative": payload.get("owner_risk_narrative") or "",
        "mitigations_proposed": payload.get("mitigations_proposed"),
        "open_questions": payload.get("open_questions"),
        "lab1_artifact_reference": payload.get("lab1_artifact_reference") or payload.get("export_filename"),
        "export_format_version": payload.get("export_format_version"),
        # Include Lab 1 scoring information for reference
        "lab1_inherent_risk_score": payload.get("inherent_risk_score"),
        "lab1_score_breakdown": payload.get("score_breakdown"),
        "lab1_scoring_version": payload.get("scoring_version")
    }
    return normalized


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
            "interdependency": "Medium - Input to other models, but not mission-critical"
        },
        "owner_preliminary_assessment": {
            "preliminary_risk_tier": "Tier 1",
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
            "data_sensitivity": "Non-Sensitive - Publicly available or anonymized data",
            "automation_level": "Advisory - Provides recommendations to human decision-makers",
            "regulatory_materiality": "Low - No direct regulatory reporting impact",
            "model_complexity": "Medium - Complex statistical model or simple ML model",
            "interdependency": "Low - Standalone model with no downstream dependencies"
        },
        "owner_preliminary_assessment": {
            "preliminary_risk_tier": "Tier 3",
            "rationale": "Primarily for internal marketing, no direct financial or regulatory impact."
        },
        "owner_narrative": "This model helps us optimize marketing spend by identifying key customer segments. It's an internal tool and has no direct impact on customer financials or regulatory compliance.",
        "lab1_artifact_reference": "lab1_model_registration_MRKT_SEG_002.json"
    }
]

# Apex Financial's Official Tiering Logic Version
TIERING_LOGIC_VERSION = "Apex Financial_MRM_Tiering_v2.1"

# Define risk factor weights/points based on attribute values
# These map to the detailed descriptions used in Lab 2
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
tier_thresholds = {
    "Tier 1": {"min_score": 22, "max_score": float('inf')},
    "Tier 2": {"min_score": 15, "max_score": 21},
    "Tier 3": {"min_score": 0, "max_score": 14},
}

# Define the canonical controls library mapped to tiers
control_expectations_library = {
    "Tier 1": [
        {"control_id": "VAL_T1_001", "control_name": "Full Scope Independent Validation", "description": "Comprehensive independent validation covering conceptual soundness, data, outcomes analysis, and ongoing monitoring setup, prior to first use and annually thereafter.",
            "evidence_expected": "Detailed Validation Report, Model Performance Monitoring Plan, Back-testing results, Sensitivity Analysis report.", "frequency": "Pre-implementation & Annually", "owner_role": "MRM/Validation Team"},
        {"control_id": "MON_T1_002", "control_name": "Frequent Performance Monitoring",
            "description": "Daily/Weekly monitoring of model inputs, outputs, stability, and performance metrics (e.g., AUC, F1-score, KS, bias).", "evidence_expected": "Automated Monitoring Dashboards, Alerting Logs, Performance Metrics Reports.", "frequency": "Daily/Weekly", "owner_role": "Model Owner/Operations"},
        {"control_id": "DOC_T1_003", "control_name": "Rigorous Documentation & Change Management", "description": "Extensive documentation including model design, development, testing, limitations, and a formal change management process for any modifications.",
            "evidence_expected": "Model Documentation (MDR), Change Log, Version Control Records, Peer Review sign-offs.", "frequency": "Continuous", "owner_role": "Model Owner/Developers"},
        {"control_id": "GOV_T1_004", "control_name": "Senior Management Approval & Oversight",
            "description": "Formal approval by senior management or designated committee (e.g., Model Risk Committee) for model deployment and any material changes.", "evidence_expected": "Approval Memos, Committee Meeting Minutes.", "frequency": "Pre-implementation & Annually", "owner_role": "Model Governance Committee"},
        {"control_id": "DATA_T1_005", "control_name": "Data Quality & Governance", "description": "Strict data quality checks, lineage tracking, and governance processes for all input data, especially sensitive and regulated data.",
            "evidence_expected": "Data Quality Reports, Data Lineage Documentation, Data Governance Policies.", "frequency": "Continuous", "owner_role": "Data Governance/Model Owner"},
        {"control_id": "AUDIT_T1_006", "control_name": "Regular Internal Audit Review", "description": "Inclusion in the internal audit plan for periodic review of the model risk management process and control effectiveness.",
            "evidence_expected": "Internal Audit Report.", "frequency": "Biennially", "owner_role": "Internal Audit"}
    ],
    "Tier 2": [
        {"control_id": "VAL_T2_001", "control_name": "Targeted Independent Validation", "description": "Independent validation focusing on key risk areas, data, and outcomes analysis, prior to first use and biennially thereafter.",
            "evidence_expected": "Validation Report, Model Performance Monitoring Plan.", "frequency": "Pre-implementation & Biennially", "owner_role": "MRM/Validation Team"},
        {"control_id": "MON_T2_002", "control_name": "Monthly Performance Monitoring", "description": "Monthly monitoring of model inputs, outputs, and key performance indicators.",
            "evidence_expected": "Monitoring Reports, Alerting Logs.", "frequency": "Monthly", "owner_role": "Model Owner/Operations"},
        {"control_id": "DOC_T2_003", "control_name": "Standard Documentation & Version Control", "description": "Standard documentation of model design, development, testing, and version control for changes.",
            "evidence_expected": "Model Documentation, Change Log.", "frequency": "Continuous", "owner_role": "Model Owner/Developers"},
        {"control_id": "GOV_T2_004", "control_name": "Management Review & Approval", "description": "Formal review and approval by relevant business line management for model deployment and significant changes.",
            "evidence_expected": "Approval Records, Meeting Minutes.", "frequency": "Pre-implementation & Annually", "owner_role": "Business Line Management"},
        {"control_id": "DATA_T2_005", "control_name": "Data Quality Checks", "description": "Regular data quality checks for input data.",
            "evidence_expected": "Data Quality Logs.", "frequency": "Monthly", "owner_role": "Model Owner"}
    ],
    "Tier 3": [
        {"control_id": "VAL_T3_001", "control_name": "Self-Validation & MRM Review", "description": "Model owner performs self-validation, with periodic light-touch review by MRM to confirm adherence to basic standards.",
            "evidence_expected": "Self-Validation Report, MRM Review Summary.", "frequency": "Pre-implementation & Triennially", "owner_role": "Model Owner/MRM"},
        {"control_id": "MON_T3_002", "control_name": "Quarterly Performance Monitoring", "description": "Quarterly monitoring of model performance metrics.",
            "evidence_expected": "Quarterly Performance Reports.", "frequency": "Quarterly", "owner_role": "Model Owner/Operations"},
        {"control_id": "DOC_T3_003", "control_name": "Basic Documentation", "description": "Basic documentation of model purpose, inputs, outputs, and any known limitations.",
            "evidence_expected": "Model Summary Document.", "frequency": "Upon development", "owner_role": "Model Owner/Developers"},
        {"control_id": "GOV_T3_004", "control_name": "Business Unit Approval", "description": "Approval by relevant business unit lead before model use.",
            "evidence_expected": "Email approval or sign-off.", "frequency": "Pre-implementation", "owner_role": "Business Unit Lead"}
    ]
}


def load_model_registration(model_id: str, inventory_data: list) -> dict | None:
    """
    Loads model registration details for a given model_id from a model inventory.

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


def apply_model_tiering_logic(model_metadata: dict, weights: dict, thresholds: dict, logic_version: str) -> dict:
    """
    Applies the standardized, deterministic tiering logic to a model's metadata.

    Args:
        model_metadata (dict): Dictionary of the model's key attributes for tiering, including
                                'model_id', 'model_name', and 'key_attributes_for_tiering'.
        weights (dict): Predefined weights/points for each attribute value.
        thresholds (dict): Predefined score thresholds for each risk tier.
        logic_version (str): Version of the tiering logic being used.

    Returns:
        dict: A dictionary containing the official risk score, tier, and breakdown.
    """
    official_risk_score = 0
    score_breakdown = {}
    mrm_lead_rationale_points = []
    mrm_lead_rationale_warnings = []

    attrs = model_metadata.get("key_attributes_for_tiering")
    if not isinstance(attrs, dict):
        attrs = {k: model_metadata.get(
            k) for k in weights.keys() if model_metadata.get(k) is not None}

    for attribute, value in attrs.items():
        clean_attribute = attribute.lower().replace(' ', '_')

        matched_points = 0
        matched_description = ""

        if clean_attribute in weights:
            # Match based on the first part of the description in weights
            # This handles cases where model_metadata values are more verbose
            score_map = weights[clean_attribute]
            if value in score_map:
                matched_points = score_map[value]
                matched_description = value
            else:
                value_prefix = str(value).split(" - ")[0]
                for desc_key, points in score_map.items():
                    if desc_key.startswith(value_prefix):
                        matched_points = points
                        matched_description = desc_key
                        break

            if matched_points > 0:
                official_risk_score += matched_points
                score_breakdown[attribute] = {
                    "value_matched": matched_description, "points": matched_points}
                mrm_lead_rationale_points.append(
                    f"'{attribute.replace('_', ' ').title()}' is '{matched_description}' contributing {matched_points} points.")
            else:
                score_breakdown[attribute] = {"value_matched": value, "points": 0,
                                              "note": "No specific match found in tiering logic for this attribute value."}
                mrm_lead_rationale_warnings.append(
                    f"Warning: No specific points for '{attribute.replace('_', ' ').title()}' with value '{value}'.")
        else:
            score_breakdown[attribute] = {
                "value_matched": value, "points": 0, "note": "Attribute not found in tiering logic."}
            mrm_lead_rationale_warnings.append(
                f"Warning: Attribute '{attribute.replace('_', ' ').title()}' not explicitly defined in tiering logic.")

    # Determine the official risk tier
    official_risk_tier = "Undetermined"
    for tier, score_range in thresholds.items():
        if score_range["min_score"] <= official_risk_score <= score_range["max_score"]:
            official_risk_tier = tier
            break

    # Generate plain English rationale
    full_rationale = (
        f"The model '{model_metadata['model_name']}' ({model_metadata['model_id']}) "
        f"has been assigned an official risk tier of **{official_risk_tier}** "
        f"with a total risk score of **{official_risk_score}**. "
        f"This decision is based on the following factors as per Apex Financial's official tiering logic "
        f"(version {logic_version}):\n  "
    )
    full_rationale += "\n".join(
        [f"- {item}" for item in mrm_lead_rationale_points])
    full_rationale += f"\nThe total score of {official_risk_score} falls within the range for '{official_risk_tier}'."

    if mrm_lead_rationale_warnings:
        full_rationale += "\n\n**Notes/Warnings during scoring:**\n"
        full_rationale += "\n".join(
            [f"- {item}" for item in mrm_lead_rationale_warnings])

    return {
        "model_id": model_metadata['model_id'],
        "model_name": model_metadata['model_name'],
        "official_risk_score": official_risk_score,
        "official_risk_tier": official_risk_tier,
        "score_breakdown": score_breakdown,
        "tier_thresholds_used": thresholds,  # Include thresholds for context
        "tiering_logic_version": logic_version,
        "mrm_lead_rationale_plain_english": full_rationale,
        "date_tiered": datetime.date.today().isoformat(),
        "tiered_by": "MRM Lead (via Lab 2 Tiering Logic)"
    }


def map_controls_to_tier(tier: str, controls_library: dict, model_id: str = None) -> dict:
    """
    Maps the assigned risk tier to the corresponding control expectations.

    Args:
        tier (str): The official risk tier assigned to the model.
        controls_library (dict): The library of control expectations for each tier.
        model_id (str, optional): The model ID for reference in the output.

    Returns:
        dict: A dictionary containing the assigned tier, required controls,
              model_id, and control expectations summary.
    """
    required_controls = controls_library.get(tier, [])

    control_expectations_summary = ""
    if tier == "Tier 1":
        control_expectations_summary = (
            "This model is classified as **Tier 1 (High Risk)**. It requires the most rigorous oversight, "
            "including full-scope independent validation, frequent performance monitoring, extensive documentation, "
            "senior management approval, and regular internal audit review."
        )
    elif tier == "Tier 2":
        control_expectations_summary = (
            "This model is classified as **Tier 2 (Medium Risk)**. It requires targeted independent validation, "
            "monthly performance monitoring, standard documentation, and management review and approval."
        )
    elif tier == "Tier 3":
        control_expectations_summary = (
            "This model is classified as **Tier 3 (Low Risk)**. It requires self-validation with MRM review, "
            "quarterly performance monitoring, basic documentation, and business unit approval."
        )
    else:
        control_expectations_summary = (
            "This model's risk tier could not be determined. Please review the tiering logic and model attributes."
        )

    return {
        "model_id": model_id,
        "assigned_tier": tier,
        "required_controls": required_controls,
        "control_expectations_summary": control_expectations_summary
    }


def export_tiering_result(tiering_result: dict, output_dir: str, filename_prefix: str = "tiering_result") -> str:
    """
    Exports the tiering result to a JSON file.

    Args:
        tiering_result (dict): The tiering result dictionary to export.
        output_dir (str): The directory where the file should be saved.
        filename_prefix (str): Prefix for the filename.

    Returns:
        str: The full path to the exported file.
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w') as f:
        json.dump(tiering_result, f, indent=4)

    return filepath


def export_controls_checklist(controls_checklist: dict, output_dir: str, filename_prefix: str = "controls_checklist") -> str:
    """
    Exports the controls checklist to a JSON file.

    Args:
        controls_checklist (dict): The controls checklist dictionary to export.
        output_dir (str): The directory where the file should be saved.
        filename_prefix (str): Prefix for the filename.

    Returns:
        str: The full path to the exported file.
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'w') as f:
        json.dump(controls_checklist, f, indent=4)

    return filepath
