import streamlit as st
import json
import pandas as pd
import datetime
from io import StringIO
from source import normalize_lab1_to_lab2

# Import all necessary functions and constants from source.py
from source import TIERING_LOGIC_VERSION, risk_factor_weights, tier_thresholds, control_expectations_library, apply_model_tiering_logic, map_controls_to_tier

# --- Page Configuration ---
st.set_page_config(
    page_title="QuLab: Second Line - MRM Lead's Formal Model Tiering & Control Mandate", layout="wide")
st.sidebar.image("https://www.quantuniversity.com/assets/img/logo5.jpg")
st.sidebar.divider()
st.title("QuLab: Second Line - MRM Lead's Formal Model Tiering & Control Mandate")
st.divider()


def render_official_tiering_result(data):
    """
    Renders the Official MRM Tiering Result using native Streamlit components.
    """

    # --- Header & Audit Trail ---
    st.title(f"Official Tiering Result: {data.get('model_name', 'Unknown')}")

    # Audit metadata displayed prominently at the top
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        st.caption(f"**Model ID:** {data.get('model_id')}")
    with c2:
        st.caption(f"**Tiered By:** {data.get('tiered_by')}")
    with c3:
        st.caption(f"**Date:** {data.get('date_tiered')}")

    st.markdown("---")

    # --- Key Results (Hero Section) ---
    st.subheader("Final Determination")

    m1, m2, m3 = st.columns(3)

    with m1:
        st.metric(
            label="Official Risk Tier",
            value=data.get("official_risk_tier")
        )
    with m2:
        st.metric(
            label="Total Risk Score",
            value=data.get("official_risk_score")
        )
    with m3:
        st.metric(
            label="Logic Version Applied",
            value=data.get("tiering_logic_version")
        )

    # --- Rationale (Plain English) ---
    # Using a colored container (success/info) to make the decision rationale stand out
    st.subheader("MRM Lead Rationale")
    st.info(data.get("mrm_lead_rationale_plain_english"), icon=None)

    # --- Detailed Score Breakdown ---
    st.subheader("Scoring Breakdown")

    breakdown_data = data.get("score_breakdown", {})
    if breakdown_data:
        breakdown_items = []
        for category, details in breakdown_data.items():
            # Check if there is a note/warning for this line item
            note = details.get("note", "")

            breakdown_items.append({
                "Category": category.replace("_", " ").title(),
                "Value Matched": details.get("value_matched"),
                "Points": details.get("points"),
                "Notes / Warnings": note
            })

        df_breakdown = pd.DataFrame(breakdown_items)

        # We highlight the 'Notes' column if it contains data
        st.dataframe(
            df_breakdown,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Points": st.column_config.NumberColumn(format="%d"),
                "Notes / Warnings": st.column_config.TextColumn(width="large")
            }
        )

    # --- Logic Reference (Collapsible) ---
    with st.expander("View Tiering Thresholds Used"):
        st.markdown(f"**Logic Version:** {data.get('tiering_logic_version')}")

        thresholds = data.get("tier_thresholds_used", {})
        if thresholds:
            t_data = []
            for tier, limits in thresholds.items():
                # Handle 'Infinity' string or float
                max_score = limits.get("max_score")
                if max_score == "Infinity" or max_score == float('inf'):
                    range_str = f">= {limits.get('min_score')}"
                else:
                    range_str = f"{limits.get('min_score')} - {max_score}"

                t_data.append({
                    "Tier": tier,
                    "Score Range": range_str
                })

            st.dataframe(pd.DataFrame(t_data), hide_index=True,
                         use_container_width=True)


def render_controls_checklist(data):
    """
    Renders the Model Risk Controls Checklist using native Streamlit components.
    """

    # --- Header & Tier Status ---
    st.title("Controls Checklist & Requirements")

    # We display the Tier prominently as it dictates the controls
    c1, c2 = st.columns([3, 1])
    with c1:
        st.caption(f"**Model ID:** {data.get('model_id')}")
    with c2:
        st.metric(label="Assigned Tier", value=data.get("assigned_tier"))

    st.markdown("---")

    # --- Executive Summary ---
    # Good for a quick reading of the expectations
    if data.get("control_expectations_summary"):
        st.subheader("Expectations Summary")
        st.info(data.get("control_expectations_summary"), icon=None)

    # --- Detailed Controls Table ---
    st.subheader("Required Controls")

    controls = data.get("required_controls", [])

    if controls:
        # Create a DataFrame for a clean, filterable checklist view
        df = pd.DataFrame(controls)

        # Reordering and renaming columns for display purposes
        # We handle missing keys gracefully using .get inside the list logic if needed,
        # but pandas handles missing dict keys by creating NaN.

        # Map JSON keys to Friendly Names
        column_mapping = {
            "control_id": "ID",
            "control_name": "Control Name",
            "frequency": "Frequency",
            "owner_role": "Owner / Accountability",
            "evidence_expected": "Evidence Required",
            "description": "Description"
        }

        # Rename columns that exist in the dataframe
        df = df.rename(columns=column_mapping)

        # Select only the columns we want to display (in order)
        display_cols = [
            "ID",
            "Control Name",
            "Frequency",
            "Owner / Accountability",
            "Evidence Required",
            "Description"
        ]

        # Ensure only columns that actually exist in the data are selected
        final_cols = [c for c in display_cols if c in df.columns]
        df_final = df[final_cols]

        st.dataframe(
            df_final,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID": st.column_config.TextColumn(width="small"),
                "Control Name": st.column_config.TextColumn(width="medium"),
                "Description": st.column_config.TextColumn(width="large"),
                "Evidence Required": st.column_config.TextColumn(width="medium"),
            }
        )
    else:
        st.warning("No specific controls found for this model tier.", icon=None)


# --- Session State Initialization ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = "1) Ingest Model Submission"
if 'uploaded_file_content' not in st.session_state:
    st.session_state.uploaded_file_content = None
if 'model_registration_data' not in st.session_state:
    st.session_state.model_registration_data = None
if 'validation_status' not in st.session_state:
    st.session_state.validation_status = None
if 'validation_error' not in st.session_state:
    st.session_state.validation_error = None
if 'tiering_results' not in st.session_state:
    st.session_state.tiering_results = None
if 'controls_checklist' not in st.session_state:
    st.session_state.controls_checklist = None
if 'mrm_lead_rationale_text' not in st.session_state:
    st.session_state.mrm_lead_rationale_text = ""
if 'download_json_tiering_content' not in st.session_state:
    st.session_state.download_json_tiering_content = ""
if 'download_json_controls_content' not in st.session_state:
    st.session_state.download_json_controls_content = ""
if 'download_md_summary_content' not in st.session_state:
    st.session_state.download_md_summary_content = ""


# --- Sidebar Navigation ---
with st.sidebar:
    st.title("MRM Lead Workflow")
    # Disable subsequent pages until prior steps are complete
    page_options = [
        "1) Ingest Model Submission",
        "2) Official Tiering",
        "3) Required Controls",
        "4) Export Reports"
    ]
    disabled_pages = []
    if not st.session_state.model_registration_data:
        disabled_pages.extend(["2) Official Tiering",
                              "3) Required Controls", "4) Export Reports"])
    elif not st.session_state.tiering_results:
        disabled_pages.extend(["3) Required Controls", "4) Export Reports"])
    elif not st.session_state.controls_checklist:
        disabled_pages.extend(["4) Export Reports"])

    st.markdown("### Navigation")

    st.sidebar.selectbox("Go to Page:", page_options, key="current_page",)


# --- Page Content ---
if st.session_state.get("current_page") == "1) Ingest Model Submission":
    st.header("1. Ingest Model Submission from Model Owner")

    st.markdown("""
    As the MRM Lead, your first step is to review the Model Owner's preliminary submission. 
    This initial registration provides critical context about the model's purpose, design, 
    and the owner's self-assessment of its risk.
    """)

    uploaded_file = st.file_uploader(
        "Upload Lab 1 Model Registration JSON", type=["json"])

    # LOGIC CHANGE: Only process if a file is uploaded AND we haven't successfully processed this specific file yet
    # We use file.id or just check if data is missing/mismatched to avoid re-parsing on every rerun.
    if uploaded_file is not None:
        file_content = uploaded_file.getvalue().decode("utf-8")

        # Only parse if the content is new or data hasn't been loaded yet
        if st.session_state.get("uploaded_file_content") != file_content:
            st.session_state.uploaded_file_content = file_content

            try:
                parsed_data = json.loads(file_content)
                parsed_data = normalize_lab1_to_lab2(parsed_data)

                # Removed st.write(parsed_data) to clean UI

                required_keys = [
                    "model_id", "model_name", "model_owner", "submission_date",
                    "model_purpose", "data_used", "key_attributes_for_tiering",
                    "owner_preliminary_assessment", "owner_narrative"
                ]
                missing_keys = [
                    key for key in required_keys if key not in parsed_data]

                # Validation Logic
                if parsed_data.get("key_attributes_for_tiering") is None or not isinstance(parsed_data["key_attributes_for_tiering"], dict):
                    missing_keys.append(
                        "key_attributes_for_tiering is missing or invalid")

                if parsed_data.get("owner_preliminary_assessment") is None or not isinstance(parsed_data["owner_preliminary_assessment"], dict):
                    missing_keys.append(
                        "owner_preliminary_assessment is missing or invalid")
                elif "preliminary_risk_tier" not in parsed_data["owner_preliminary_assessment"]:
                    missing_keys.append(
                        "owner_preliminary_assessment.preliminary_risk_tier is missing")

                if missing_keys:
                    st.session_state.validation_status = False
                    st.session_state.validation_error = f"Error: Missing/Invalid fields: {', '.join(missing_keys)}"
                    st.session_state.model_registration_data = None
                else:
                    st.session_state.validation_status = True
                    st.session_state.validation_error = None
                    st.session_state.model_registration_data = parsed_data
                    # CRITICAL FIX: Removed st.rerun() here to prevent infinite loop

            except json.JSONDecodeError:
                st.session_state.validation_status = False
                st.session_state.validation_error = "Error: Invalid JSON format."
                st.session_state.model_registration_data = None
    else:
        # Reset state if file is removed
        st.session_state.model_registration_data = None
        st.session_state.validation_status = None
        st.session_state.uploaded_file_content = None

    # UI RENDERING SECTION
    if st.session_state.get("validation_status"):
        data = st.session_state.model_registration_data

        st.success("JSON schema validation successful!")

        # Display Data
        st.markdown(
            f"### Model Submitted: **{data['model_name']} ({data['model_id']})**")
        st.markdown(f"**Model Owner:** {data['model_owner']}")
        st.markdown(f"**Purpose:** {data['model_purpose']}")

        st.markdown("#### Owner Assessment")
        risk_tier = data['owner_preliminary_assessment']['preliminary_risk_tier']
        st.markdown(f"- **Preliminary Risk Tier:** {risk_tier}")
        st.markdown(
            f"- **Rationale:** {data['owner_preliminary_assessment']['rationale']}")

        st.markdown(f"**Key Attributes:**")
        for attr, desc in data['key_attributes_for_tiering'].items():
            st.markdown(f"- **{attr.replace('_', ' ').title()}**: {desc}")

        st.markdown("---")

        # LOGIC FIX: Dynamic interpretation text
        tier_context = "a high-impact model" if "High" in str(risk_tier) or "1" in str(
            risk_tier) else "a model requiring specific review"

        st.markdown(
            f"The output above summarizes the key information provided by the Model Owner. "
            f"The owner's preliminary tier ({risk_tier}) suggests {tier_context}, "
            f"aligning with the provided rationale. This initial review confirms the need for "
            f"validation rigor proportional to this tier."
        )

    elif st.session_state.get("validation_status") is False:
        st.error(st.session_state.validation_error)
        st.warning("Please upload a valid JSON file to proceed.")

# 2) Official Tiering Page
if st.session_state.current_page == "2) Official Tiering":
    if not st.session_state.model_registration_data:
        st.warning(
            "Please first ingest a model submission on the 'Ingest Model Submission' page.")
    else:
        st.markdown(f"")
        st.markdown(
            f"## 3. Defining Apex Financial's Official Model Risk Tiering Logic")
        st.markdown(f"")
        st.markdown(f"To ensure consistency, transparency, and reproducibility in model risk assessments, Apex Financial has established a standardized, deterministic model tiering logic. This formal logic, approved by senior management, translates qualitative model attributes into a quantitative risk score and an official Model Risk Tier. This process directly supports SR 11-7's emphasis on strong 'Governance, Policies, and Controls' (Section VI, page 16) by providing a clear, auditable framework for assessing model risk across the enterprise. It minimizes subjectivity and ensures that similar models are tiered consistently.")
        st.markdown(f"")
        st.markdown(r"The total risk score $S$ for a model is calculated as:")
        st.markdown(r"""$$ 
S = \sum_{{i=1}}^{{N}} P_i 
$$""")
        st.markdown(
            r"where $P_i$ represents the points assigned to the $i$-th risk attribute based on its specific value.")
        st.markdown(f"")

        st.markdown(
            f"### Apex Financial's Official Tiering Logic Version: **{TIERING_LOGIC_VERSION}**")
        st.markdown(f"\n#### Risk Factor Weights/Points:")
        markdown_builder = ""
        for factor, values in risk_factor_weights.items():
            markdown_builder += f"\n\n- **{factor.replace('_', ' ').title()}**:\n"

            for value, points in values.items():
                markdown_builder += f"  - _{value}_: {points} points\n"

        st.markdown(markdown_builder)

        st.markdown(f"\n#### Official Risk Tier Thresholds:")

        for tier, thresholds in tier_thresholds.items():
            st.markdown(r"**- " + tier + "**: Score $\\ge$ " + str(thresholds['min_score']) + (
                " and < " + str(thresholds['max_score']) if thresholds['max_score'] != float('inf') else ""))
        st.markdown(f"---")

        st.markdown(f"")
        st.markdown(f"## 4. Applying the Formal Model Risk Tiering Algorithm")
        st.markdown(f"")
        st.markdown(f"Now, as the MRM Lead, you will apply Apex Financial's official, deterministic tiering logic to the \"{st.session_state.model_registration_data['model_name']}\" model. This is a critical step to independently calculate the model's inherent risk score and assign its authoritative tier. This exercise directly supports SR 11-7's core principle that \"The rigor and sophistication of validation should be commensurate with the bank's overall use of models, the complexity and materiality of its models\" (Section V, page 9). By objectively tiering the model, you ensure that the subsequent model validation activities, monitoring efforts, and governance overhead are appropriately scaled to the actual risk posed by the model. This prevents both under- and over-scoping of model risk management resources.")
        st.markdown(f"")

        if st.button("Recompute Official Tier", key="recompute_tier_button") or st.session_state.tiering_results is None:
            # Function invocation from source.py
            st.session_state.tiering_results = apply_model_tiering_logic(
                st.session_state.model_registration_data,
                risk_factor_weights,
                tier_thresholds,
                TIERING_LOGIC_VERSION
            )
            st.session_state.mrm_lead_rationale_text = st.session_state.tiering_results[
                'mrm_lead_rationale_plain_english']

            st.rerun()

        if st.session_state.tiering_results:
            tr = st.session_state.tiering_results
            st.markdown("### Official Model Risk Tiering Results")
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="Official Risk Score",
                          value=f"**{tr['official_risk_score']}**")
            with col2:
                st.metric(label="Official Risk Tier",
                          value=f"**{tr['official_risk_tier']}**")

            st.markdown(f"- **Model ID:** {tr['model_id']}")
            st.markdown(f"- **Model Name:** {tr['model_name']}")
            st.markdown(
                f"- **Tiering Logic Version:** {tr['tiering_logic_version']}")
            st.markdown(f"- **Date Tiered:** {tr['date_tiered']}")
            st.markdown(f"- **Tiered By:** {tr['tiered_by']}")

            st.markdown("\n#### Score Breakdown by Factor:")
            score_breakdown_df = pd.DataFrame([
                {"Factor": k.replace('_', ' ').title(
                ), "Value Matched": v["value_matched"], "Points": v["points"]}
                for k, v in tr['score_breakdown'].items()
            ])
            st.dataframe(score_breakdown_df, hide_index=True,
                         width='stretch')

            st.markdown("\n#### Tiering Decision Rationale:")
            st.markdown(tr['mrm_lead_rationale_plain_english'])

            st.markdown(
                "\n#### Comparison with Model Owner's Preliminary Tier:")
            owner_preliminary_tier = st.session_state.model_registration_data[
                'owner_preliminary_assessment']['preliminary_risk_tier']
            if tr['official_risk_tier'] == owner_preliminary_tier:
                st.success(
                    f"The official tiering **matches** the Model Owner's preliminary assessment of **{owner_preliminary_tier}**. This indicates strong alignment in risk perception.")
            else:
                st.warning(
                    f"The official tiering assigned **{tr['official_risk_tier']}**, which **differs** from the Model Owner's preliminary assessment of **{owner_preliminary_tier}**. Further discussion with the Model Owner may be warranted to align understanding of risk factors.")

            st.markdown("---")
            st.markdown(f"The output confirms the \"{st.session_state.model_registration_data['model_name']}\" model has been officially assigned a **{tr['official_risk_tier']}** risk, with a score of **{tr['official_risk_score']}**. This {('aligns with' if tr['official_risk_tier'] == owner_preliminary_tier else 'differs from')} the Model Owner's preliminary assessment, which is a {('positive' if tr['official_risk_tier'] == owner_preliminary_tier else 'point for discussion')} indicator of shared risk understanding. The detailed score breakdown provides transparency on how each attribute contributed to the final score, justifying the decision. For example, `Decision Criticality` ({tr['score_breakdown'].get('decision_criticality', {}).get('points', 0)} points) and `Regulatory Materiality` ({tr['score_breakdown'].get('regulatory_materiality', {}).get('points', 0)} points) significantly impact the overall risk.")
            st.markdown(f"")
            st.markdown(f"As the MRM Lead, this result signals that the \"{st.session_state.model_registration_data['model_name']}\" is indeed a high-impact model requiring the most stringent controls. This objective, quantitative assessment is crucial for allocating appropriate resources and ensuring compliance with SR 11-7's guidance on tailoring model validation rigor to its risk profile (Section V, page 9: \"The rigor and sophistication of validation should be commensurate with the bank's overall use of models, the complexity and materiality of its models\").")


# 3) Required Controls Page
if st.session_state.current_page == "3) Required Controls":
    if not st.session_state.tiering_results:
        st.warning("Please first complete the 'Official Tiering' process.")
    else:
        st.markdown(f"")
        st.markdown(f"## 5. Establishing Minimum Required Control Expectations")
        st.markdown(f"")
        st.markdown(f"With the official Model Risk Tier now assigned, your next responsibility as the MRM Lead is to formally establish the minimum required control expectations for the \"{st.session_state.model_registration_data['model_name']}\" model. This is a direct implementation of SR 11-7's Section VI: Governance, Policies, and Controls (page 16), which emphasizes that a robust governance framework includes \"policies defining relevant risk management activities\" and \"procedures that implement those policies.\" By mapping controls to the assigned tier, Apex Financial ensures that higher-risk models, like the newly tiered \"{st.session_state.model_registration_data['model_name']}\" model, receive the most stringent oversight, including deep independent validation, frequent performance monitoring, and rigorous documentation standards. This systematic approach ensures adequate safeguards are in place and clearly communicates responsibilities to the Model Owner and other stakeholders.")
        st.markdown(f"")

        # Function invocation from source.py
        if st.session_state.controls_checklist is None or \
           st.session_state.controls_checklist.get('assigned_tier') != st.session_state.tiering_results['official_risk_tier']:
            st.session_state.controls_checklist = map_controls_to_tier(
                st.session_state.tiering_results['official_risk_tier'],
                control_expectations_library,
                st.session_state.tiering_results['model_id']
            )

        if st.session_state.controls_checklist:
            cc = st.session_state.controls_checklist
            st.markdown(
                "### Minimum Required Control Expectations for the Model")
            st.markdown(f"**Model ID:** {cc['model_id']}")
            st.markdown(f"**Assigned Tier:** **{cc['assigned_tier']}**")

            st.markdown("\n#### Detailed Control Checklist:")
            controls_df = pd.DataFrame(cc['required_controls'])

            # Group controls by category (Validation, Monitoring, Documentation, Governance, Data, Audit)
            def categorize_control(control_name):
                if "Validation" in control_name or "validation" in control_name:
                    return "Validation Controls"
                if "Monitoring" in control_name or "monitoring" in control_name:
                    return "Monitoring Controls"
                if "Documentation" in control_name or "documentation" in control_name:
                    return "Documentation Controls"
                if "Management" in control_name or "Approval" in control_name or "Oversight" in control_name:
                    return "Governance Controls"
                if "Data Quality" in control_name:
                    return "Data Quality & Governance"
                if "Audit" in control_name:
                    return "Audit & Compliance"
                return "General Controls"

            if not controls_df.empty:
                controls_df['Category'] = controls_df['control_name'].apply(
                    categorize_control)
                categories = ["Validation Controls", "Monitoring Controls", "Documentation Controls",
                              "Governance Controls", "Data Quality & Governance", "Audit & Compliance", "General Controls"]

                for category in categories:
                    category_df = controls_df[controls_df['Category'] == category]
                    if not category_df.empty:
                        with st.expander(f"**{category}**"):
                            st.dataframe(category_df[['control_id', 'control_name', 'description',
                                         'frequency', 'owner_role']], hide_index=True, width='stretch')
            else:
                st.info("No specific controls found for this tier in the library.")

            st.markdown("\n#### Summary of Control Expectations:")
            st.markdown(cc['control_expectations_summary'])

            st.markdown("---")
            st.markdown(
                f"The output presents the comprehensive list of controls mandated for the \"{st.session_state.model_registration_data['model_name']}\" model, now officially designated as {st.session_state.tiering_results['official_risk_tier']} risk. This includes requirements for full scope independent validation, frequent performance monitoring, rigorous documentation, senior management approval, strict data governance, and regular internal audit reviews.")
            st.markdown(f"")
            st.markdown(f"For the MRM Lead, this serves as the formal control mandate. It clearly outlines the high bar for oversight required for this model, aligning directly with SR 11-7's expectations for models with significant materiality. This checklist will be communicated to the Model Owner and relevant support functions, guiding their ongoing responsibilities and ensuring appropriate allocation of resources for validation and monitoring. This ensures \"effective challenge\" and management of model risk (SR 11-7, Section III, page 4).")


# 4) Export Reports Page
if st.session_state.current_page == "4) Export Reports":
    if not st.session_state.controls_checklist:
        st.warning("Please first complete the 'Required Controls' process.")
    else:
        st.markdown(f"")
        st.markdown(f"## 6. Generating the Formal Tiering Decision Report")
        st.markdown(f"")
        st.markdown(f"The final step in your workflow as the MRM Lead is to compile and export the formal Tiering Decision Report. This comprehensive report, incorporating the model metadata, the calculated risk score, the assigned official tier, the plain-English rationale, and the associated control expectations, is a critical deliverable. It serves as the official record for internal governance, audit, and regulatory bodies, demonstrating Apex Financial's adherence to SR 11-7 guidance on \"Documentation\" (Section VI, page 21). Effective documentation ensures transparency, reproducibility, and clear communication of model risk decisions to all stakeholders, including the Model Owner and AI Program Lead. It provides an auditable trail and cements the clarity needed for ongoing model risk management.")
        st.markdown(f"")

        st.markdown("### Review and Finalize Rationale")
        # Ensure the text area is always populated with the current rationale from session state
        st.session_state.mrm_lead_rationale_text = st.text_area(
            "MRM Lead's Official Rationale (editable):",
            value=st.session_state.mrm_lead_rationale_text,
            height=200
        )

        st.markdown("### Preview and Download Reports")

        model_id_for_reports = st.session_state.model_registration_data['model_id']
        model_name_for_reports = st.session_state.model_registration_data['model_name']
        official_risk_tier_for_reports = st.session_state.tiering_results['official_risk_tier']
        official_risk_score_for_reports = st.session_state.tiering_results['official_risk_score']
        tiering_logic_version_for_reports = st.session_state.tiering_results[
            'tiering_logic_version']
        date_tiered_for_reports = st.session_state.tiering_results['date_tiered']
        tiered_by_for_reports = st.session_state.tiering_results['tiered_by']
        owner_preliminary_tier_for_reports = st.session_state.model_registration_data[
            'owner_preliminary_assessment']['preliminary_risk_tier']
        model_purpose_for_reports = st.session_state.model_registration_data['model_purpose']
        model_owner_for_reports = st.session_state.model_registration_data['model_owner']
        submission_date_for_reports = st.session_state.model_registration_data[
            'submission_date']

        # Prepare risk_tiering.json content
        tiering_results_for_download = st.session_state.tiering_results.copy()
        tiering_results_for_download['mrm_lead_rationale_plain_english'] = st.session_state.mrm_lead_rationale_text
        st.session_state.download_json_tiering_content = json.dumps(
            tiering_results_for_download, indent=4)

        st.subheader(f"1. Risk Tiering Result")
        # Display nicely
        render_official_tiering_result(json.loads(
            st.session_state.download_json_tiering_content))
        st.download_button(
            label="Download Risk Tiering JSON",
            data=st.session_state.download_json_tiering_content,
            file_name=f"{model_id_for_reports}_risk_tiering.json",
            mime="application/json",
            key="download_tiering_json"
        )

        # Prepare required_controls_checklist.json content
        controls_checklist_for_download = st.session_state.controls_checklist.copy()
        st.session_state.download_json_controls_content = json.dumps(
            controls_checklist_for_download, indent=4)

        st.subheader(f"2. Required Controls Checklist")
        # Display nicely
        render_controls_checklist(json.loads(
            st.session_state.download_json_controls_content))
        st.download_button(
            label="Download Required Controls JSON",
            data=st.session_state.download_json_controls_content,
            file_name=f"{model_id_for_reports}_required_controls_checklist.json",
            mime="application/json",
            key="download_controls_json"
        )

        # Prepare executive_summary.md content
        md_summary_content = f"""# Model Risk Tiering Decision Report: {model_id_for_reports} - {model_name_for_reports}

**Date:** {date_tiered_for_reports}
**Tiered By:** {tiered_by_for_reports}

---

## 1. Executive Summary

The **{model_name_for_reports}** (`{model_id_for_reports}`) has undergone formal risk tiering by the Model Risk Management (MRM) team at Apex Financial. Based on the enterprise's official tiering logic (version: {tiering_logic_version_for_reports}), the model has been assigned an **Official Risk Tier of {official_risk_tier_for_reports}** with a total risk score of **{official_risk_score_for_reports}**.

This tiering {'aligns with' if official_risk_tier_for_reports == owner_preliminary_tier_for_reports else 'differs from'} the Model Owner's preliminary assessment and signifies that the model carries a {official_risk_tier_for_reports.lower()} level of inherent risk, necessitating the most stringent oversight and control measures as per SR 11-7 guidance.

---

## 2. Model Overview (from Owner Submission)

- **Model Purpose:** {model_purpose_for_reports}
- **Model Owner:** {model_owner_for_reports}
- **Submission Date:** {submission_date_for_reports}
- **Model Owner's Preliminary Tier:** {owner_preliminary_tier_for_reports}

---

## 3. Official Tiering Decision

**Official Risk Score:** {official_risk_score_for_reports}
**Official Risk Tier:** {official_risk_tier_for_reports}
**Tiering Logic Version:** {tiering_logic_version_for_reports}

### Score Breakdown:
"""
        for factor, details in tiering_results_for_download['score_breakdown'].items():
            md_summary_content += f"- **{factor.replace('_', ' ').title()}**: '{details['value_matched']}' contributing {details['points']} points.\n"

        md_summary_content += f"""
### MRM Lead Rationale:
{st.session_state.mrm_lead_rationale_text}

---

## 4. Minimum Required Control Expectations (Based on Official Tier)

Based on the **{official_risk_tier_for_reports}** assignment, the following controls are mandated for the **{model_name_for_reports}**:

"""
        controls_summary_df = pd.DataFrame(
            controls_checklist_for_download['required_controls'])
        if not controls_summary_df.empty:
            md_summary_content += controls_summary_df[['control_id', 'control_name',
                                                       'description', 'frequency', 'owner_role']].to_markdown(index=False)
        else:
            md_summary_content += "No specific controls found for this tier in the library.\n"

        md_summary_content += f"""
### Control Expectations Summary:
{controls_checklist_for_download['control_expectations_summary']}
---

This report serves as the formal documentation of the model's risk tier and the corresponding control requirements, enabling consistent model risk management and compliance with regulatory expectations.
"""
        st.session_state.download_md_summary_content = md_summary_content

        st.subheader(f"3. Executive Summary Report")
        with st.container(border=True):
            st.markdown(st.session_state.download_md_summary_content)
        st.download_button(
            label="Download Executive Summary MD",
            data=st.session_state.download_md_summary_content,
            file_name=f"{model_id_for_reports}_executive_summary.md",
            mime="text/markdown",
            key="download_summary_md"
        )

        st.markdown("---")
        st.markdown(f"")
        st.markdown(
            f"As the MRM Lead, these exportable files are your concrete deliverables. The JSON files provide structured, machine-readable data for integration into Apex Financial's enterprise model inventory systems and for potential automated downstream processes (e.g., in Lab 3 for reproducibility or compliance checks). The Markdown `executive_summary.md` offers a human-readable, plain-English summary for communication to Model Owners, AI Program Leads, and senior management. This report ensures transparency, consistency, and a clear audit trail for the formal model risk tiering process, fully aligning with the comprehensive documentation and governance requirements outlined in SR 11-7 (Section VI, page 16, and Section VII, page 21). This completes your formal assessment and provides the necessary foundation for the ongoing management of the \"{model_name_for_reports}\" model's risk.")


# License
st.caption('''
---
## QuantUniversity License

© QuantUniversity 2025  
This notebook was created for **educational purposes only** and is **not intended for commercial use**.  

- You **may not copy, share, or redistribute** this notebook **without explicit permission** from QuantUniversity.  
- You **may not delete or modify this license cell** without authorization.  
- This notebook was generated using **QuCreate**, an AI-powered assistant.  
- Content generated by AI may contain **hallucinated or incorrect information**. Please **verify before using**.  

All rights reserved. For permissions or commercial licensing, contact: [info@qusandbox.com](mailto:info@qusandbox.com)
''')
