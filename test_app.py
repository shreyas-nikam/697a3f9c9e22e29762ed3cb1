
import pytest
from streamlit.testing.v1 import AppTest
import json
from io import StringIO
import datetime

# --- Mock Data for Testing ---
MOCK_VALID_MODEL_REGISTRATION_DATA = {
    "model_id": "MDL-001",
    "model_name": "Credit Risk Scoring Model",
    "model_purpose": "Assess creditworthiness of loan applicants.",
    "model_owner": "John Doe",
    "submission_date": "2025-01-15",
    "data_used": ["Customer Demographics", "Financial History"],
    "key_attributes_for_tiering": {
        "decision_criticality": "High",
        "data_sensitivity": "Confidential",
        "regulatory_materiality": "High Impact"
    },
    "owner_preliminary_assessment": {
        "preliminary_risk_tier": "Tier 1",
        "rationale": "High impact due to financial decisions."
    },
    "owner_narrative": "This model is crucial for our lending operations and directly impacts customer financial well-being. We believe it warrants a Tier 1 classification due to its critical nature and the sensitive data it processes."
}

MOCK_VALID_MODEL_REGISTRATION_JSON_STR = json.dumps(MOCK_VALID_MODEL_REGISTRATION_DATA, indent=4)

MOCK_INVALID_JSON_FORMAT_STR = "{ 'model_id': 'MDL-002', }" # Malformed JSON

MOCK_INCOMPLETE_MODEL_REGISTRATION_DATA = {
    "model_id": "MDL-003",
    "model_name": "Fraud Detection Model",
    # Missing model_purpose, model_owner, submission_date, data_used
    "key_attributes_for_tiering": {
        "decision_criticality": "Medium",
        "data_sensitivity": "Confidential",
        "regulatory_materiality": "Medium Impact"
    },
    "owner_preliminary_assessment": {
        "preliminary_risk_tier": "Tier 2",
        "rationale": "Detects fraud, moderate impact."
    },
}
MOCK_INCOMPLETE_MODEL_REGISTRATION_JSON_STR = json.dumps(MOCK_INCOMPLETE_MODEL_REGISTRATION_DATA, indent=4)

# Mock return values for source.py functions.
# These will be the expected values that the app's session state should hold after calling these functions.
MOCK_TIERING_RESULTS_TIER1 = {
    "model_id": "MDL-001",
    "model_name": "Credit Risk Scoring Model",
    "official_risk_score": 25, # Example score that would result in Tier 1
    "official_risk_tier": "Tier 1",
    "tiering_logic_version": "1.0", # Assuming from source.py
    "date_tiered": datetime.date.today().isoformat(),
    "tiered_by": "MRM Lead (Automated)",
    "score_breakdown": {
        "decision_criticality": {"value_matched": "High", "points": 10},
        "data_sensitivity": {"value_matched": "Confidential", "points": 8},
        "regulatory_materiality": {"value_matched": "High Impact", "points": 7},
    },
    "mrm_lead_rationale_plain_english": "Model MDL-001 assigned Tier 1 based on a score of 25. Attributes like decision criticality (High), data sensitivity (Confidential), and regulatory materiality (High Impact) were key factors."
}

MOCK_CONTROLS_CHECKLIST_TIER1 = {
    "model_id": "MDL-001",
    "assigned_tier": "Tier 1",
    "required_controls": [
        {"control_id": "C001", "control_name": "Full Scope Independent Validation", "description": "Comprehensive validation required.", "frequency": "Annually", "owner_role": "MRM"},
        {"control_id": "C002", "control_name": "Frequent Performance Monitoring", "description": "Daily monitoring of model performance.", "frequency": "Daily", "owner_role": "Model Owner"},
        {"control_id": "C003", "control_name": "Detailed Documentation Standards", "description": "Full documentation including design, data, and validation.", "frequency": "Continuous", "owner_role": "Model Owner"},
        {"control_id": "C007", "control_name": "Governance Oversight", "description": "Senior management review.", "frequency": "Quarterly", "owner_role": "Governance Committee"},
    ],
    "control_expectations_summary": "Most stringent controls for Tier 1 models."
}


def test_initial_app_state_and_navigation():
    at = AppTest.from_file("app.py").run()

    # Check initial page
    assert at.session_state["current_page"] == "1) Ingest Model Submission"
    assert "Ingest Model Submission" in at.header[0].value

    # Check sidebar navigation button states
    assert at.button[0].label == "1) Ingest Model Submission"
    assert at.button[0].disabled is False
    assert at.button[1].label == "2) Official Tiering"
    assert at.button[1].disabled is True
    assert at.button[2].label == "3) Required Controls"
    assert at.button[2].disabled is True
    assert at.button[3].label == "4) Export Reports"
    assert at.button[3].disabled is True

    # Check initial session state values
    assert at.session_state["uploaded_file_content"] is None
    assert at.session_state["model_registration_data"] is None
    assert at.session_state["validation_status"] is None
    assert at.session_state["tiering_results"] is None
    assert at.session_state["controls_checklist"] is None


def test_upload_invalid_json_format():
    at = AppTest.from_file("app.py").run() # Initial run for page 1

    at.file_uploader[0].upload(StringIO(MOCK_INVALID_JSON_FORMAT_STR), name="invalid.json", type="application/json").run()

    # Verify validation error and session state
    assert at.session_state["validation_status"] is False
    assert "Error: Invalid JSON format." in at.session_state["validation_error"]
    assert at.error[0].value == "Error: Invalid JSON format. Please upload a valid JSON file."
    assert at.session_state["model_registration_data"] is None
    assert at.session_state["current_page"] == "1) Ingest Model Submission" # Should not auto-advance


def test_upload_incomplete_json_schema():
    at = AppTest.from_file("app.py").run() # Initial run for page 1

    at.file_uploader[0].upload(StringIO(MOCK_INCOMPLETE_MODEL_REGISTRATION_JSON_STR), name="incomplete.json", type="application/json").run()

    # Verify validation error and session state
    assert at.session_state["validation_status"] is False
    assert "Error: Missing or invalid required fields in JSON:" in at.session_state["validation_error"]
    assert "model_purpose" in at.session_state["validation_error"]
    assert "model_owner" in at.session_state["validation_error"]
    assert "submission_date" in at.session_state["validation_error"]
    assert "data_used" in at.session_state["validation_error"]

    assert at.error[0].value.startswith("Error: Missing or invalid required fields in JSON:")
    assert at.session_state["model_registration_data"] is None
    assert at.session_state["current_page"] == "1) Ingest Model Submission" # Should not auto-advance


def test_full_workflow_from_upload_to_export():
    at = AppTest.from_file("app.py").run() # 1) Ingest Model Submission (initial state)

    # --- Page 1: Ingest Model Submission ---
    at.file_uploader[0].upload(StringIO(MOCK_VALID_MODEL_REGISTRATION_JSON_STR), name="valid.json", type="application/json").run()
    # At this point, the app has processed the upload, set session_state.model_registration_data,
    # set session_state.current_page to "2) Official Tiering", and called st.rerun().
    # We need to run the app again to render the "2) Official Tiering" page.
    at.run() # Rerun to render "2) Official Tiering" page

    assert at.session_state["validation_status"] is True
    assert at.session_state["model_registration_data"] == MOCK_VALID_MODEL_REGISTRATION_DATA
    assert at.session_state["current_page"] == "2) Official Tiering"
    assert "Official Tiering" in at.header[0].value # Verify header of the new page

    # Verify that 'tiering_results' and 'controls_checklist' were populated by the app's auto-advance logic
    # and the assumed execution of source.py functions.
    # We are asserting against the expected structure that those functions *should* produce given the inputs.
    assert at.session_state["tiering_results"] is not None
    assert at.session_state["tiering_results"]["model_id"] == MOCK_VALID_MODEL_REGISTRATION_DATA["model_id"]
    assert at.session_state["tiering_results"]["official_risk_tier"] == MOCK_TIERING_RESULTS_TIER1["official_risk_tier"]
    assert at.session_state["controls_checklist"] is not None
    assert at.session_state["controls_checklist"]["model_id"] == MOCK_VALID_MODEL_REGISTRATION_DATA["model_id"]
    assert at.session_state["controls_checklist"]["assigned_tier"] == MOCK_TIERING_RESULTS_TIER1["official_risk_tier"]


    # After the `at.run()` that rendered "2) Official Tiering", the app will have
    # computed the tiering results and then auto-advanced to "3) Required Controls" with another st.rerun().
    at.run() # Rerun to render "3) Required Controls" page

    # --- Page 3: Required Controls ---
    assert at.session_state["current_page"] == "3) Required Controls"
    assert "Required Controls" in at.header[0].value
    assert f"**Model ID:** {MOCK_CONTROLS_CHECKLIST_TIER1['model_id']}" in at.markdown[4].value
    assert at.expander[0].label == "**Validation Controls**" # Check for control categories

    # After the `at.run()` that rendered "3) Required Controls", the app will have
    # generated the control checklist and then auto-advanced to "4) Export Reports" with another st.rerun().
    at.run() # Rerun to render "4) Export Reports" page

    # --- Page 4: Export Reports ---
    assert at.session_state["current_page"] == "4) Export Reports"
    assert "Export Reports" in at.header[0].value

    # Simulate editing the rationale
    new_rationale = "Updated rationale by MRM Lead during final review. Emphasizing high financial impact and increased monitoring requirements."
    at.text_area[0].set_value(new_rationale).run()
    assert at.session_state["mrm_lead_rationale_text"] == new_rationale

    # Verify download JSON content for tiering
    downloaded_tiering_json = json.loads(at.session_state["download_json_tiering_content"])
    assert downloaded_tiering_json["model_id"] == MOCK_TIERING_RESULTS_TIER1["model_id"]
    assert downloaded_tiering_json["mrm_lead_rationale_plain_english"] == new_rationale

    # Verify download JSON content for controls
    downloaded_controls_json = json.loads(at.session_state["download_json_controls_content"])
    assert downloaded_controls_json["model_id"] == MOCK_CONTROLS_CHECKLIST_TIER1["model_id"]
    assert len(downloaded_controls_json["required_controls"]) == len(MOCK_CONTROLS_CHECKLIST_TIER1["required_controls"])

    # Verify download Markdown summary content
    downloaded_md_summary = at.session_state["download_md_summary_content"]
    assert f"Official Risk Tier of {MOCK_TIERING_RESULTS_TIER1['official_risk_tier']}" in downloaded_md_summary
    assert new_rationale in downloaded_md_summary
    assert MOCK_CONTROLS_CHECKLIST_TIER1["control_expectations_summary"] in downloaded_md_summary
    assert MOCK_VALID_MODEL_REGISTRATION_DATA["model_owner"] in downloaded_md_summary


def test_navigation_buttons_direct_click():
    at = AppTest.from_file("app.py")

    # Set session state to simulate a fully processed workflow to enable all buttons
    at.session_state["current_page"] = "4) Export Reports" # Start at the end to ensure all are enabled
    at.session_state["model_registration_data"] = MOCK_VALID_MODEL_REGISTRATION_DATA
    at.session_state["tiering_results"] = MOCK_TIERING_RESULTS_TIER1
    at.session_state["controls_checklist"] = MOCK_CONTROLS_CHECKLIST_TIER1
    at.run() # Render the "4) Export Reports" page initially

    # All buttons should be enabled
    for i in range(4):
        assert at.button[i].disabled is False

    # Click "1) Ingest Model Submission"
    at.button[0].click().run()
    assert at.session_state["current_page"] == "1) Ingest Model Submission"
    assert "Ingest Model Submission" in at.header[0].value

    # Click "2) Official Tiering"
    at.button[1].click().run()
    assert at.session_state["current_page"] == "2) Official Tiering"
    assert "Official Tiering" in at.header[0].value

    # Click "3) Required Controls"
    at.button[2].click().run()
    assert at.session_state["current_page"] == "3) Required Controls"
    assert "Required Controls" in at.header[0].value

    # Click "4) Export Reports"
    at.button[3].click().run()
    assert at.session_state["current_page"] == "4) Export Reports"
    assert "Export Reports" in at.header[0].value


def test_recompute_tier_button_on_page_2():
    at = AppTest.from_file("app.py")

    # Set session state to be on page 2 with model data but no tiering results yet
    at.session_state["current_page"] = "2) Official Tiering"
    at.session_state["model_registration_data"] = MOCK_VALID_MODEL_REGISTRATION_DATA
    at.session_state["tiering_results"] = None # Simulate no initial computation
    at.session_state["controls_checklist"] = None # Also no controls yet
    at.run() # Render "2) Official Tiering"

    # The button should be present and enabled
    assert at.button[4].label == "Recompute Official Tier"
    assert at.button[4].disabled is False

    # Click the "Recompute Official Tier" button
    at.button[4].click().run()
    # After click and re-run, it should auto-advance to "3) Required Controls"
    assert at.session_state["current_page"] == "3) Required Controls"
    assert at.session_state["tiering_results"] is not None
    assert at.session_state["tiering_results"]["official_risk_tier"] == MOCK_TIERING_RESULTS_TIER1["official_risk_tier"]
    assert at.session_state["controls_checklist"] is not None
    assert at.session_state["controls_checklist"]["assigned_tier"] == MOCK_TIERING_RESULTS_TIER1["official_risk_tier"]
