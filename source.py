import pandas as pd
import json
import datetime
import os
import numpy as np


def normalize_lab1_to_lab2(payload: dict) -> dict:
    """
    Convert Lab 1 export artifact into Lab 2 expected schema.
    """
    # If it's already in Lab 2 shape, return as-is
    if "key_attributes_for_tiering" in payload and "owner_preliminary_assessment" in payload:
        return payload

    # Map risk factors (Lab 1 stores them flat)
    key_attrs = {}
    for k in ["decision_criticality", "data_sensitivity", "automation_level", "regulatory_materiality",
              "model_complexity", "interdependency"]:
        if k in payload and payload[k] is not None:
            key_attrs[k] = payload[k]

    # Map owner preliminary tier (Lab 1 uses proposed tier)
    prelim_tier = payload.get("proposed_risk_tier") or payload.get(
        "preliminary_risk_tier") or "Tier 3"

    normalized = {
        "model_id": payload.get("model_id"),
        "model_name": payload.get("model_name"),
        "model_domain": payload.get("domain") or payload.get("model_domain"),
        "model_owner": payload.get("model_owner"),
        "submission_date": payload.get("submission_date") or payload.get("registration_timestamp"),
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
        "export_format_version": payload.get("export_format_version")
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
            "interdependency": "Medium - Feeds into broader risk capital models"
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
            "data_sensitivity": "Non-Regulated PII - Anonymized demographic data, no direct financial impact",
            "automation_level": "Advisory - Provides recommendations to human marketers",
            "regulatory_materiality": "Low - No direct regulatory reporting impact",
            "model_complexity": "Medium - Standard clustering algorithm",
            "interdependency": "Low - Standalone marketing tool"
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
        "tiered_by": "MRM Lead (Persona)",  # Mock identity
        "owner_submission_reference": model_metadata.get("lab1_artifact_reference", "N/A")
    }


def map_controls_to_tier(assigned_tier: str, controls_library: dict, model_id: str) -> dict:
    """
    Maps minimum required control expectations to an assigned model risk tier.

    Args:
        assigned_tier (str): The official risk tier assigned to the model.
        controls_library (dict): The canonical library of control expectations.
        model_id (str): The ID of the model.

    Returns:
        dict: A dictionary containing the model ID, assigned tier, the list of required controls,
              and a summary string of expectations.
    """
    required_controls = controls_library.get(assigned_tier, [])

    control_expectations_summary = (
        f"Based on the assigned **{assigned_tier}**, the following minimum control expectations "
        f"are required for model '{model_id}':\n"
    )
    for control in required_controls:
        control_expectations_summary += (
            f"- **{control['control_name']}** ({control['control_id']}): {control['description']} "
            f"(Frequency: {control['frequency']}, Owner: {control['owner_role']})\n"
        )

    return {
        "model_id": model_id,
        "assigned_tier": assigned_tier,
        "required_controls": required_controls,
        "control_expectations_summary": control_expectations_summary
    }


def generate_reports(tiering_results: dict, controls_checklist: dict, model_metadata_snapshot: dict, output_dir: str = ".") -> dict:
    """
    Generates and saves the Model Risk Tiering Report and Required Controls Checklist to files.

    Args:
        tiering_results (dict): The dictionary containing official tiering outcomes.
        controls_checklist (dict): The dictionary containing the mapped controls.
        model_metadata_snapshot (dict): A snapshot of the initial model registration data.
        output_dir (str): Directory to save the output files.

    Returns:
        dict: A dictionary containing the paths to the generated files.
    """
    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    model_id = tiering_results['model_id']
    report_paths = {}

    # 1. Generate risk_tiering.json
    risk_tiering_filename = os.path.join(
        output_dir, f"{model_id}_risk_tiering.json")
    with open(risk_tiering_filename, 'w') as f:
        json.dump(tiering_results, f, indent=4)
    report_paths['risk_tiering_json'] = risk_tiering_filename

    # 2. Generate required_controls_checklist.json
    controls_checklist_filename = os.path.join(
        output_dir, f"{model_id}_required_controls_checklist.json")
    with open(controls_checklist_filename, 'w') as f:
        json.dump(controls_checklist, f, indent=4)
    report_paths['required_controls_checklist_json'] = controls_checklist_filename

    # 3. Generate executive_summary.md
    executive_summary_filename = os.path.join(
        output_dir, f"{model_id}_executive_summary.md")
    with open(executive_summary_filename, 'w') as f:
        f.write(
            f"# Model Risk Tiering Decision Report: {model_id} - {tiering_results['model_name']}\n\n")
        f.write(f"**Date:** {tiering_results['date_tiered']}\n")
        f.write(f"**Tiered By:** {tiering_results['tiered_by']}\n\n")
        f.write("---\n\n")
        f.write("## 1. Executive Summary\n\n")
        f.write(
            f"The **{tiering_results['model_name']}** (`{model_id}`) has undergone formal "
            f"risk tiering by the Model Risk Management (MRM) team at Apex Financial. Based on the "
            f"enterprise's official tiering logic (version: {tiering_results['tiering_logic_version']}), "
            f"the model has been assigned an **Official Risk Tier of {tiering_results['official_risk_tier']}** "
            f"with a total risk score of **{tiering_results['official_risk_score']}**.\n\n"
        )
        owner_prelim_tier = model_metadata_snapshot.get(
            'owner_preliminary_assessment', {}).get('preliminary_risk_tier', 'N/A')
        alignment_note = ""
        if tiering_results['official_risk_tier'] == owner_prelim_tier:
            alignment_note = "This tiering aligns with the Model Owner's preliminary assessment, indicating strong alignment in risk perception."
        else:
            alignment_note = (
                f"This tiering differs from the Model Owner's preliminary assessment of {owner_prelim_tier}. "
                "Further discussion with the Model Owner may be warranted to align understanding of risk factors."
            )

        f.write(
            f"This tiering signifies that the model carries a {tiering_results['official_risk_tier'].lower()} "
            f"level of inherent risk, necessitating the most stringent oversight and control measures as "
            f"per SR 11-7 guidance. {alignment_note}\n\n"
        )
        f.write("---\n\n")
        f.write("## 2. Model Overview (from Owner Submission)\n\n")
        f.write(
            f"- **Model Purpose:** {model_metadata_snapshot.get('model_purpose', 'N/A')}\n")
        f.write(
            f"- **Model Owner:** {model_metadata_snapshot.get('model_owner', 'N/A')}\n")
        f.write(
            f"- **Submission Date:** {model_metadata_snapshot.get('submission_date', 'N/A')}\n")
        f.write(
            f"- **Model Owner's Preliminary Tier:** {owner_prelim_tier}\n\n")
        f.write("---\n\n")
        f.write("## 3. Official Tiering Decision\n\n")
        f.write(
            f"**Official Risk Score:** {tiering_results['official_risk_score']}\n")
        f.write(
            f"**Official Risk Tier:** {tiering_results['official_risk_tier']}\n")
        f.write(
            f"**Tiering Logic Version:** {tiering_results['tiering_logic_version']}\n\n")
        f.write("### Score Breakdown:\n\n")
        for factor, details in tiering_results['score_breakdown'].items():
            f.write(
                f"- **{factor.replace('_', ' ').title()}**: '{details['value_matched']}' contributing {details['points']} points.")
            if 'note' in details:
                f.write(f" (Note: {details['note']})")
            f.write("\n")
        f.write("\n### MRM Lead Rationale:\n")
        f.write(tiering_results['mrm_lead_rationale_plain_english'] + "\n\n")
        f.write("---\n\n")
        f.write(
            "## 4. Minimum Required Control Expectations (Based on Official Tier)\n\n")
        f.write(
            f"Based on the **{tiering_results['official_risk_tier']}** assignment, "
            f"the following controls are mandated for the **{tiering_results['model_name']}**:\n\n"
        )

        controls_summary_df = pd.DataFrame(
            controls_checklist['required_controls'])
        if not controls_summary_df.empty:
            f.write(controls_summary_df[[
                    'control_id', 'control_name', 'description', 'frequency', 'owner_role']].to_markdown(index=False))
            f.write("\n\n")
        else:
            f.write("No specific controls defined for this tier.\n\n")

        f.write("### Control Expectations Summary:\n")
        f.write(controls_checklist['control_expectations_summary'] + "\n")
        f.write("---\n\n")
        f.write(
            "This report serves as the formal documentation of the model's risk tier and "
            "the corresponding control requirements, enabling consistent model risk management "
            "and compliance with regulatory expectations.\n"
        )
    report_paths['executive_summary_md'] = executive_summary_filename

    return report_paths


def process_model_risk_tiering(
    model_id: str,
    inventory_data: list = mock_model_inventory,
    tiering_logic_version: str = TIERING_LOGIC_VERSION,
    risk_factor_weights: dict = risk_factor_weights,
    tier_thresholds: dict = tier_thresholds,
    control_expectations_library: dict = control_expectations_library,
    output_dir: str | None = None
) -> dict:
    """
    Orchestrates the model risk tiering process from model selection to report generation.

    Args:
        model_id (str): The ID of the model to process.
        inventory_data (list): The list of registered models. Defaults to `mock_model_inventory`.
        tiering_logic_version (str): Version identifier for the tiering logic. Defaults to `TIERING_LOGIC_VERSION`.
        risk_factor_weights (dict): The predefined weights for risk factors. Defaults to `risk_factor_weights`.
        tier_thresholds (dict): The predefined score thresholds for risk tiers. Defaults to `tier_thresholds`.
        control_expectations_library (dict): The library mapping tiers to required controls.
                                             Defaults to `control_expectations_library`.
        output_dir (str | None): Directory to save generated reports. If None, reports are not saved to disk.

    Returns:
        dict: A dictionary containing all results:
              - "model_registration_data": The loaded model metadata.
              - "tiering_results": The outcome of the tiering logic.
              - "required_controls_checklist": The mapped control expectations.
              - "generated_report_paths": A dict of paths to generated reports, or None if `output_dir` was None.
    Raises:
        ValueError: If the specified model_id is not found in the inventory.
    """
    model_registration_data = load_model_registration(model_id, inventory_data)
    if not model_registration_data:
        raise ValueError(f"Model with ID '{model_id}' not found in inventory.")

    tiering_results = apply_model_tiering_logic(
        model_registration_data,
        risk_factor_weights,
        tier_thresholds,
        tiering_logic_version
    )

    required_controls_checklist = map_controls_to_tier(
        tiering_results['official_risk_tier'],
        control_expectations_library,
        tiering_results['model_id']
    )

    generated_report_paths = None
    if output_dir:
        generated_report_paths = generate_reports(
            tiering_results,
            required_controls_checklist,
            model_registration_data,
            output_dir
        )

    return {
        "model_registration_data": model_registration_data,
        "tiering_results": tiering_results,
        "required_controls_checklist": required_controls_checklist,
        "generated_report_paths": generated_report_paths
    }


def display_tiering_results_notebook(results: dict):
    """
    Displays the model risk tiering results in a notebook-friendly format using IPython.display.
    This function is intended for interactive notebook environments and requires
    `IPython.display` to be installed.

    Args:
        results (dict): The dictionary returned by `process_model_risk_tiering`.
    """
    try:
        from IPython.display import display, Markdown, HTML
    except ImportError:
        print("IPython.display not found. Cannot display results in notebook format.")
        print("Raw results:")
        print(json.dumps(results, indent=2))
        return

    model_registration_data = results['model_registration_data']
    tiering_results = results['tiering_results']
    required_controls_checklist = results['required_controls_checklist']
    generated_report_paths = results['generated_report_paths']

    # --- Initial Model Selection and Display ---
    if model_registration_data:
        display(Markdown(
            f"### Model Selected for Review: **{model_registration_data['model_name']} ({model_registration_data['model_id']})**"))
        display(
            Markdown(f"**Model Owner:** {model_registration_data['model_owner']}"))
        display(
            Markdown(f"**Submission Date:** {model_registration_data['submission_date']}"))
        display(
            Markdown(f"**Model Purpose:** {model_registration_data['model_purpose']}"))
        display(
            Markdown(f"**Data Used:** {', '.join(model_registration_data['data_used'])}"))
        display(Markdown("\n#### Model Owner's Preliminary Self-Assessment:"))
        display(Markdown(
            f"- **Preliminary Risk Tier:** {model_registration_data['owner_preliminary_assessment']['preliminary_risk_tier']}"))
        display(Markdown(
            f"- **Rationale:** {model_registration_data['owner_preliminary_assessment']['rationale']}"))
        display(Markdown(f"- **Key Attributes for Tiering:**"))
        for attr, desc in model_registration_data['key_attributes_for_tiering'].items():
            display(
                Markdown(f"  - **{attr.replace('_', ' ').title()}**: {desc}"))
        display(Markdown(
            f"\n#### Owner Narrative:\n  > {model_registration_data['owner_narrative']}"))
    else:
        display(Markdown(
            f"Model with ID '{tiering_results.get('model_id', 'N/A')}' not found in inventory."))

    # --- Tiering Logic Constants Display ---
    display(Markdown(
        f"### Apex Financial's Official Tiering Logic Version: **{TIERING_LOGIC_VERSION}**"))
    display(Markdown("\n#### Risk Factor Weights/Points:"))
    for factor, values in risk_factor_weights.items():
        display(Markdown(f"**- {factor.replace('_', ' ').title()}**:"))
        for value, points in values.items():
            display(Markdown(f"  - _{value}_: {points} points"))

    display(Markdown("\n#### Official Risk Tier Thresholds:"))
    for tier, thresholds in tier_thresholds.items():
        display(Markdown(
            f"**- {tier}**: Score $\ge$ {thresholds['min_score']} {'and <' + str(thresholds['max_score']) if thresholds['max_score'] != float('inf') else ''}"))

    display(Markdown("\n#### Sample Control Expectations Library (Tier 1 shown):"))
    # Show first 2 for brevity
    for control in control_expectations_library["Tier 1"][:2]:
        display(Markdown(
            f"- **{control['control_name']}** (`{control['control_id']}`): {control['description']}"))
        display(Markdown(f"  - _Frequency:_ {control['frequency']}"))

    # --- Official Model Risk Tiering Results Display ---
    display(Markdown("### Official Model Risk Tiering Results"))
    display(Markdown(f"- **Model ID:** {tiering_results['model_id']}"))
    display(Markdown(f"- **Model Name:** {tiering_results['model_name']}"))
    display(Markdown(
        f"- **Official Risk Score:** **{tiering_results['official_risk_score']}**"))
    display(Markdown(
        f"- **Official Risk Tier:** **{tiering_results['official_risk_tier']}**"))
    display(Markdown(
        f"- **Tiering Logic Version:** {tiering_results['tiering_logic_version']}"))
    display(Markdown(f"- **Date Tiered:** {tiering_results['date_tiered']}"))
    display(Markdown(f"- **Tiered By:** {tiering_results['tiered_by']}"))

    display(Markdown("\n#### Score Breakdown by Factor:"))
    score_breakdown_df = pd.DataFrame([
        {"Factor": k.replace('_', ' ').title(
        ), "Value Matched": v["value_matched"], "Points": v["points"]}
        for k, v in tiering_results['score_breakdown'].items()
    ])
    display(score_breakdown_df)

    display(Markdown("\n#### Tiering Decision Rationale:"))
    display(Markdown(tiering_results['mrm_lead_rationale_plain_english']))

    display(Markdown("\n#### Comparison with Model Owner's Preliminary Tier:"))
    owner_preliminary_tier = model_registration_data[
        'owner_preliminary_assessment']['preliminary_risk_tier']
    if tiering_results['official_risk_tier'] == owner_preliminary_tier:
        display(Markdown(
            f"The official tiering **matches** the Model Owner's preliminary assessment of **{owner_preliminary_tier}**. This indicates strong alignment in risk perception."))
    else:
        display(Markdown(
            f"The official tiering assigned **{tiering_results['official_risk_tier']}**, which **differs** from the Model Owner's preliminary assessment of **{owner_preliminary_tier}**. Further discussion with the Model Owner may be warranted to align understanding of risk factors."))

    # --- Minimum Required Control Expectations Display ---
    display(Markdown("### Minimum Required Control Expectations for the Model"))
    display(
        Markdown(f"**Model ID:** {required_controls_checklist['model_id']}"))
    display(Markdown(
        f"**Assigned Tier:** **{required_controls_checklist['assigned_tier']}**"))

    display(Markdown("\n#### Detailed Control Checklist:"))
    controls_df = pd.DataFrame(
        required_controls_checklist['required_controls'])
    display(controls_df[['control_id', 'control_name',
            'description', 'frequency', 'owner_role']])

    display(Markdown("\n#### Summary of Control Expectations:"))
    display(
        Markdown(required_controls_checklist['control_expectations_summary']))

    # --- Report Generation Summary Display ---
    if generated_report_paths:
        output_directory = os.path.dirname(list(generated_report_paths.values())[
                                           0])  # Get directory from any path
        display(Markdown(
            f"\nAll required artifacts for Model '{tiering_results['model_id']}' have been generated in the '{output_directory}' directory."))
        display(Markdown(f"You can now download the following files:\n"))
        for key, path in generated_report_paths.items():
            display(Markdown(f"- `{os.path.basename(path)}`"))
    else:
        display(
            Markdown("\nReport generation skipped as `output_dir` was not specified."))


def generate_report_payloads(tiering_results: dict, controls_checklist: dict, model_metadata_snapshot: dict) -> dict:
    tiering_json = json.dumps(tiering_results, indent=4)
    controls_json = json.dumps(controls_checklist, indent=4)

    # Build markdown (reuse your existing executive summary content, but as a string)
    md = []
    md.append(
        f"# Model Risk Tiering Decision Report: {tiering_results['model_id']} - {tiering_results['model_name']}")
    md.append(f"**Date:** {tiering_results['date_tiered']}")
    md.append(f"**Tiered By:** {tiering_results['tiered_by']}")
    md.append("\n---\n")
    md.append("## Executive Summary")
    md.append(tiering_results["mrm_lead_rationale_plain_english"])
    md.append("\n---\n")
    md.append("## Minimum Required Controls")
    for c in controls_checklist.get("required_controls", []):
        md.append(
            f"- **{c['control_name']}** ({c['control_id']}): {c['frequency']} | {c['owner_role']}")

    md_content = "\n".join(md)

    return {
        "risk_tiering_json": tiering_json,
        "required_controls_json": controls_json,
        "executive_summary_md": md_content,
    }
