import streamlit as st
import requests
import time
import datetime
import json
import pandas as pd
import altair as alt

# --- CONFIGURATION ---
BACKEND_URL = "http://backend:8000"  # Docker service name
TRUST_SERVICE_URL = "http://trust-service:8000"
# For local testing if not in docker, might need localhost
# BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="BergerConnect X - Sovereign Data Exchange",
    page_icon="factory",
    layout="wide"
)

# --- STYLING ---
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6
    }
    .sidebar .sidebar-content {
        background: #262730;
        color: white;
    }
    .stButton>button {
        color: white;
        background-color: #0068c9;
        border-radius: 5px;
    }
    .stProgress > div > div > div > div {
        background-color: #00cc96;
    }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def get_all_tools():
    try:
        response = requests.get(f"{BACKEND_URL}/api/tools")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def get_organizations():
    try:
        response = requests.get(f"{BACKEND_URL}/api/registry/organizations")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def get_users():
    try:
        response = requests.get(f"{BACKEND_URL}/api/registry/users")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def create_new_tool(tool_id, name, description):
    try:
        payload = {"id": tool_id, "name": name, "description": description}
        response = requests.post(f"{BACKEND_URL}/api/tool", json=payload)
        return response.status_code == 200
    except:
        return False

def update_tool_details(tool_id, name, description, status):
    try:
        payload = {}
        if name: payload["name"] = name
        if description: payload["description"] = description
        if status: payload["status"] = status
        
        response = requests.put(f"{BACKEND_URL}/api/tool/{tool_id}", json=payload)
        return response.status_code == 200
    except:
        return False

def get_repository_files():
    try:
        response = requests.get(f"{BACKEND_URL}/api/repository/files")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def attach_file_to_tool(tool_id, filename, category):
    try:
        payload = {"filename": filename, "category": category}
        response = requests.post(f"{BACKEND_URL}/api/tool/{tool_id}/attach_file", json=payload)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def set_tool_policy(tool_id, policy_type, expiry_date=None, max_downloads=None, allowed_purpose=None):
    try:
        payload = {
            "type": policy_type,
            "created_at": datetime.datetime.now().isoformat()
        }
        if expiry_date:
            payload["expiry_date"] = expiry_date.isoformat()
        if max_downloads:
            payload["max_downloads"] = max_downloads
        if allowed_purpose:
            payload["allowed_purpose"] = allowed_purpose
            
        response = requests.post(f"{BACKEND_URL}/api/tool/{tool_id}/policy", json=payload)
        return response.status_code == 200
    except:
        return False

def get_tool_data(tool_id):
    try:
        # In a real scenario, this would go through the EDC connector
        # For prototype, we hit the backend directly but simulate the delay
        response = requests.get(f"{BACKEND_URL}/api/tool/{tool_id}")
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return None

def log_access_event(tool_id, action, consumer_name="Unknown"):
    try:
        requests.post(f"{BACKEND_URL}/api/tool/{tool_id}/log_access", json={"action": action, "consumer": consumer_name})
    except:
        pass

def simulate_edc_negotiation(action_name, tool_id, consumer_did="did:web:stripmeier.com"):
    with st.spinner(f"IDS Connector: Negotiating '{action_name}' Contract..."):
        # Verify Trust Anchor
        try:
            trust_res = requests.get(f"{TRUST_SERVICE_URL}/api/trust/verify/{consumer_did}")
            if trust_res.status_code == 200 and trust_res.json().get("verified"):
                st.toast(f"Gaia-X Trust Anchor: Identity Verified ({consumer_did}) ✅")
            else:
                st.error("Trust Verification Failed!")
                return
        except:
            pass # Fail silently if trust service is down for demo
            
        time.sleep(1.5) # Simulate network/negotiation latency
    log_access_event(tool_id, action_name, consumer_name=consumer_did)
    st.toast(f"Contract '{action_name}' Signed! Usage Policy Enforced.")

# --- SIDEBAR: ROLE SWITCHER ---
st.sidebar.title("Identity Provider")
base_role = st.sidebar.radio(
    "Select Context:",
    ("Internal (Werkzeugbau Berger)", "External Partner", "Registry Admin")
)

current_user = None

if base_role == "External Partner":
    st.sidebar.subheader("Select User Identity")
    users = get_users()
    # Filter for external users (simple check for now)
    external_users = [u for u in users if "werkzeugbau-berger" not in u.get('organization_id', '')]
    
    if not external_users:
        # Fallback for demo if backend empty
        external_users = [
            {"username": "klaus.stripmeier", "role": "Admin", "organization_id": "did:web:stripmeier.com"},
            {"username": "julia.schmidt", "role": "Viewer", "organization_id": "did:web:stripmeier.com"},
            {"username": "tom.steel", "role": "Sales", "organization_id": "did:web:steel-supply.com"}
        ]
    
    user_options = {f"{u['username']} ({u['role']} @ {u['organization_id'].split(':')[2]})": u for u in external_users}
    selected_label = st.sidebar.selectbox("User:", list(user_options.keys()))
    current_user = user_options[selected_label]
    
    st.sidebar.info(f"User: **{current_user['username']}**\nRole: **{current_user['role']}**")
    
    if "stripmeier" in current_user['organization_id']:
        st.sidebar.warning("IDS Connector: **Consumer-EDC** (Online)")
    else:
        st.sidebar.warning("IDS Connector: **Supplier-EDC** (Online)")

elif base_role == "Internal (Werkzeugbau Berger)":
    st.sidebar.success("IDS Connector: **Provider-EDC** (Online)")
    current_user = {"username": "hans.berger", "role": "Admin", "organization_id": "did:web:werkzeugbau-berger.com"}

else:
    st.sidebar.info("System: **Registry Admin**")

# --- MAIN APP LOGIC ---

st.title("BergerConnect X")
st.markdown("### Sovereign Data Exchange Platform")

# --- TOOL SELECTION ---
tools_list = get_all_tools()
tool_options = {t['name']: t['id'] for t in tools_list}
# Default to first tool if available, else "2201" as fallback
default_index = 0
selected_tool_name = st.sidebar.selectbox("Select Digital Twin Asset:", list(tool_options.keys()) if tool_options else ["No Tools Found"])
selected_tool_id = tool_options.get(selected_tool_name, "2201")

if base_role == "Internal (Werkzeugbau Berger)":
    st.header("Internal Dashboard: Asset Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"Digital Twin: {selected_tool_name}")
        tool_data = get_tool_data(selected_tool_id)
        
        if tool_data:
            st.json(tool_data)
        else:
            st.warning("Could not fetch Digital Twin data.")

    with col2:
        st.subheader("Publish Assets via IDS")
        st.write("Define Usage Control Policies for External Partners.")
        
        policy_type = st.selectbox(
            "Select Policy Template",
            ["N-Times Usage", "Time-Restricted", "Purpose-Restricted", "Custom Duration (Years)"]
        )
        
        expiry_date = None
        max_downloads = None
        allowed_purpose = None
        
        if policy_type == "Time-Restricted":
            expiry_date = st.date_input("Set Contract Expiry Date", datetime.date.today() + datetime.timedelta(days=7))
        elif policy_type == "N-Times Usage":
            max_downloads = st.number_input("Max Downloads", min_value=1, value=5)
        elif policy_type == "Purpose-Restricted":
            allowed_purpose = st.text_input("Allowed Purpose", value="Quality Control")
        elif policy_type == "Custom Duration (Years)":
            years = st.number_input("Contract Duration (Years)", min_value=1, value=5)
            expiry_date = datetime.date.today() + datetime.timedelta(days=365*years)
            st.info(f"Contract will expire on: **{expiry_date}**")
        
        if st.button("Publish & Enforce Policy"):
            simulate_edc_negotiation("Publish Asset", selected_tool_id)
            if set_tool_policy(selected_tool_id, policy_type, expiry_date, max_downloads, allowed_purpose):
                st.success(f"Asset '{selected_tool_name}' published to Gaia-X Ecosystem.\n\n**Policy**: {policy_type}")
            else:
                st.error("Failed to publish policy to backend.")

    st.markdown("---")
    
    # --- MANAGEMENT SECTION ---
    st.subheader("Asset Management")
    
    with st.expander("Create New Digital Twin"):
        with st.form("create_tool_form"):
            new_id = st.text_input("Tool ID (Unique)")
            new_name = st.text_input("Tool Name")
            new_desc = st.text_area("Description")
            submitted = st.form_submit_button("Create Tool")
            if submitted:
                if new_id and new_name:
                    if create_new_tool(new_id, new_name, new_desc):
                        st.success("Tool created successfully! Please refresh the page.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Failed to create tool. ID might already exist.")
                else:
                    st.error("ID and Name are required.")

    with st.expander("Document Repository (Local)"):
        st.write("Attach files from the local `example_data` folder to this Digital Twin.")
        repo_files = get_repository_files()
        if repo_files:
            with st.form("attach_file_form"):
                selected_file = st.selectbox("Select File", repo_files)
                file_category = st.selectbox("Category", ["Steel Certificate", "Technical Drawing", "Quality Protocol", "Timeline", "Change Request", "Other"])
                attach_submitted = st.form_submit_button("Attach to Tool")
                
                if attach_submitted:
                    result = attach_file_to_tool(selected_tool_id, selected_file, file_category)
                    if result:
                        st.success(f"Attached '{selected_file}' to {selected_tool_name}!")
                        if result.get("timeline_updated"):
                            st.info("**Timeline updated automatically from PDF!**")
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("Failed to attach file.")
        else:
            st.info("No files found in `example_data`.")

    if tool_data:
        with st.expander("Edit Current Tool Details"):
            with st.form("edit_tool_form"):
                edit_name = st.text_input("Name", value=tool_data.get("name", ""))
                edit_desc = st.text_area("Description", value=tool_data.get("description", ""))
                
                current_status = tool_data.get("status", "Active")
                status_options = ["Active", "Maintenance", "Retired"]
                try:
                    status_index = status_options.index(current_status)
                except ValueError:
                    status_index = 0
                    
                edit_status = st.selectbox("Status", status_options, index=status_index)
                
                update_submitted = st.form_submit_button("Update Tool")
                if update_submitted:
                    if update_tool_details(selected_tool_id, edit_name, edit_desc, edit_status):
                        st.success("Tool updated!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Failed to update tool.")

    st.markdown("---")
    
    # --- NEW: APPROVALS & AUDIT LOG ---
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Received Approvals")
        if tool_data and "approvals" in tool_data and tool_data["approvals"]:
            st.dataframe(tool_data["approvals"])
        else:
            st.info("No approvals received yet.")
            
    with col4:
        st.subheader("Contract Audit Log")
        st.caption("Real-time usage logs from EDC Connector")
        if tool_data and "audit_log" in tool_data and tool_data["audit_log"]:
            st.dataframe(tool_data["audit_log"])
        else:
            st.info("No usage events logged.")

elif base_role == "External Partner":
    
    # --- PERMISSION CHECK ---
    user_role = current_user.get("role", "Viewer")
    user_org = current_user.get("organization_id", "")
    
    if "steel-supply" in user_org:
        st.header(f"Supplier Portal: {current_user['username']}")
        st.info("Raw Material Supplier View")
        
        st.subheader("Open Material Requests")
        st.write(f"Requests for Digital Twin: **{selected_tool_name}**")
        
        # Mock Supplier Workflow
        st.warning("⚠️ Pending Request: Steel Grade 1.2343 Certification")
        
        uploaded_cert = st.file_uploader("Upload Material Certificate", type=['pdf'])
        if uploaded_cert:
            if st.button("Submit Certificate"):
                simulate_edc_negotiation("Upload Material Cert", selected_tool_id, consumer_did=user_org)
                st.success("Certificate uploaded and linked to Digital Twin.")
        
        st.stop() # Stop here for Supplier view

    # --- CUSTOMER VIEW (Stripmeier) ---
    st.header(f"Customer Portal: {current_user['username']}")
    
    st.info(f"You are viewing a shared Digital Twin: **{selected_tool_name}**")
    
    # Fetch Data Button
    if st.button("Request Live Status Update"):
        simulate_edc_negotiation("Read Status", selected_tool_id, consumer_did=user_org)
        tool_data = get_tool_data(selected_tool_id)
        
        if tool_data:
            st.session_state['tool_data'] = tool_data
            st.success("Data retrieved successfully via EDC Connector.")
    
    if 'tool_data' in st.session_state:
        # Check if the session data matches the selected tool to avoid showing wrong data
        if st.session_state['tool_data'].get('id') != selected_tool_id:
             st.warning("Please request live status update for the selected tool.")
        else:
            data = st.session_state['tool_data']
            
            # --- CONTRACT VISUALIZATION ---
            active_policy = data.get("active_policy")
            if active_policy:
                st.markdown("### Smart Contract Status")
                
                # Check Expiry
                is_expired = False
                expiry_str = active_policy.get("expiry_date")
                if expiry_str:
                    expiry_date = datetime.date.fromisoformat(expiry_str)
                    days_left = (expiry_date - datetime.date.today()).days
                    if days_left < 0:
                        is_expired = True
                
                if is_expired:
                    st.error(f"**CONTRACT EXPIRED**\n\nThis data usage contract expired on {expiry_str}. Access is revoked.")
                    st.stop() # Stop rendering the rest of the page
                
                # Visual Card
                c1, c2, c3 = st.columns(3)
                c1.metric("Policy Type", active_policy.get("type"))
                
                if expiry_str:
                    c2.metric("Valid Until", expiry_str, f"{days_left} days remaining")
                elif active_policy.get("max_downloads"):
                    c2.metric("Max Downloads", active_policy.get("max_downloads"))
                
                c3.success("Active & Verified")
                
                st.markdown("---")
            else:
                st.warning("No active usage policy found. Data access might be restricted in production.")

            # Display Timeline as Progress
            st.subheader("Production Status")
            
            timeline = data.get("assets", {}).get("timeline", {})
            if timeline:
                milestones = timeline.get("milestones", [])
                
                # Determine Status
                status_color = "green"
                
                # Check for specific status keywords in milestones
                if any(m.get("status") == "Delayed" for m in milestones):
                    status_color = "gold"
                elif any(m.get("status") == "Stopped" for m in milestones):
                    status_color = "red"
                
                # Traffic Light UI
                c1, c2, c3 = st.columns(3)
                
                def render_light(col, color_code, label, active_status):
                    opacity = 1.0 if active_status == color_code else 0.1
                    with col:
                        st.markdown(f"""
                            <div style='text-align: center; opacity: {opacity};'>
                                <div style='
                                    width: 60px; height: 60px; 
                                    background-color: {color_code}; 
                                    border-radius: 50%; 
                                    margin: 0 auto;
                                    box-shadow: 0 0 15px {color_code};
                                    border: 2px solid #333;
                                '></div>
                                <h4 style='margin-top: 10px;'>{label}</h4>
                            </div>
                        """, unsafe_allow_html=True)

                render_light(c1, "green", "On Track", status_color)
                render_light(c2, "gold", "Delay", status_color)
                render_light(c3, "red", "Stopped", status_color)

                st.write("") # Spacer

                # Show current active phase
                active_phase = next((m for m in milestones if m["status"] == "In Progress"), None)
                if active_phase:
                    st.info(f"**Current Phase**: {active_phase['phase']}")
                    
                with st.expander("View Detailed Schedule"):
                    st.dataframe(milestones)
            else:
                st.info("No timeline data available for this tool.")
            
            st.markdown("---")

            # --- VERSION HISTORY ---
            st.subheader("Asset Version History")
            
            # Hardcoded Version Data
            version_data = [
                {"version": "v1.0", "date": "2023-10-01", "description": "Initial Digital Twin"},
                {"version": "v1.1", "date": "2023-10-15", "description": "Added CAD Geometry"},
                {"version": "v1.2", "date": "2023-11-01", "description": "Integrated Material Properties"},
                {"version": "v2.0", "date": "2023-12-01", "description": "Real-time Sensor Calibration"},
                {"version": "v2.1", "date": "2024-01-10", "description": "Fine-tuning with Production Data"}
            ]
            
            # Create DataFrame for Chart
            df_versions = pd.DataFrame(version_data)
            df_versions['date'] = pd.to_datetime(df_versions['date'])
            df_versions['y'] = 0  # Constant Y for 1D timeline
            
            # Altair Timeline
            st.write("Version Release Timeline:")
            
            base = alt.Chart(df_versions).encode(
                x=alt.X('date', title='Release Date', axis=alt.Axis(format='%Y-%m-%d'))
            )

            points = base.mark_circle(size=200, color='#00cc96').encode(
                y=alt.Y('y', axis=None),
                tooltip=['version', 'date', 'description']
            )

            labels = base.mark_text(dy=-25, color='white').encode(
                y=alt.Y('y', axis=None),
                text='version'
            )

            # White line connecting the versions to show flow
            lines = base.mark_line(color='white', strokeWidth=2).encode(
                y=alt.Y('y', axis=None)
            )
            
            st.altair_chart((lines + points + labels).properties(height=150), use_container_width=True)
            
            with st.expander("View Version Details"):
                st.dataframe(
                    df_versions[['version', 'date', 'description']]
                )
            
            st.markdown("---")
            
            # --- PERMISSION CHECK: DOWNLOADS ---
            if user_role == "Viewer":
                st.warning("🔒 **Restricted Access**: You have 'Viewer' permissions. Downloads are disabled.")
            else:
                # Download Section
                st.subheader("Secure Downloads")
                st.write("Access controlled by Usage Policy.")
                
                # Dynamic Documents List
                documents = data.get("assets", {}).get("documents", [])
                
                # Legacy support for hardcoded steel cert if not in documents list
                legacy_cert = data.get("assets", {}).get("steel_cert")
                if legacy_cert and not any(d.get("category") == "Steel Certificate" for d in documents):
                     # Just display it as a static item if needed, or we can ignore it if we want to move fully to the new system.
                     # For now, let's keep the hardcoded one as a fallback or just show the new dynamic list.
                     pass

                if documents:
                    st.write("### Attached Documents")
                    
                    # Filter for Change Requests first
                    change_requests = [d for d in documents if d.get('category') == 'Change Request']
                    other_docs = [d for d in documents if d.get('category') != 'Change Request']
                    
                    if change_requests:
                        st.warning("### ⚠️ Pending Change Requests")
                        for doc in change_requests:
                            col_cr1, col_cr2 = st.columns([3, 1])
                            with col_cr1:
                                st.write(f"**{doc['name']}**")
                                st.caption(f"Published: {doc.get('attached_at', 'N/A')}")
                            with col_cr2:
                                if st.button(f"Review Request", key=f"review_{doc['filename']}"):
                                    simulate_edc_negotiation(f"Review {doc['name']}", selected_tool_id, consumer_did=user_org)
                                    try:
                                        file_res = requests.get(f"{BACKEND_URL}/api/files/{doc['filename']}")
                                        if file_res.status_code == 200:
                                            st.download_button(
                                                label="Download & Sign",
                                                data=file_res.content,
                                                file_name=doc['name'],
                                                mime="application/pdf",
                                                key=f"sign_{doc['filename']}"
                                            )
                                    except:
                                        st.error("Download failed.")
                        st.markdown("---")

                    for doc in other_docs:
                        col_doc1, col_doc2 = st.columns([3, 1])
                        with col_doc1:
                            st.write(f"**{doc['category']}**: {doc['name']}")
                            st.caption(f"Attached: {doc.get('attached_at', 'N/A')}")
                        with col_doc2:
                            if st.button(f"Download", key=doc['filename']):
                                simulate_edc_negotiation(f"Download {doc['name']}", selected_tool_id, consumer_did=user_org)
                                # Fetch file content
                                try:
                                    file_res = requests.get(f"{BACKEND_URL}/api/files/{doc['filename']}")
                                    if file_res.status_code == 200:
                                        st.download_button(
                                            label="Save File",
                                            data=file_res.content,
                                            file_name=doc['name'],
                                            mime="application/pdf",
                                            key=f"save_{doc['filename']}"
                                        )
                                    else:
                                        st.error("File not found on server.")
                                except:
                                    st.error("Download failed.")
                    st.markdown("---")

                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.write("**Legacy Steel Certificate (PDF)**")
                    if st.button("Download Certificate"):
                        simulate_edc_negotiation("Download File", selected_tool_id, consumer_did=user_org)
                        st.success("Download started... (Mock)")
                
                with col_d2:
                    st.write("**Bill of Materials (JSON)**")
                    
                    # Show BOM Preview
                    bom_data = data.get("assets", {}).get("bom", {})
                    if bom_data and "components" in bom_data:
                        st.dataframe(bom_data["components"])
                    
                    if st.button("Download BOM"):
                        simulate_edc_negotiation("Download BOM", selected_tool_id, consumer_did=user_org)
                        if bom_data:
                            st.download_button(
                                label="Save BOM",
                                data=json.dumps(bom_data, indent=2),
                                file_name=f"tool_{selected_tool_id}_bom.json",
                                mime="application/json"
                            )
                        else:
                            st.warning("No BOM data available.")

                st.markdown("---")
                st.subheader("Secure Approval Uplink (Sovereign Change Loop)")
                st.write("Upload signed Change Requests or Milestone Approvals here. The EDC Connector will verify your token before transmission.")
                uploaded_file = st.file_uploader("Upload Signed Document", type=['pdf', 'png', 'jpg'])
                if uploaded_file is not None:
                    if st.button("Secure Upload"):
                        simulate_edc_negotiation("Upload Approval", selected_tool_id, consumer_did=user_org)
                        # Send to backend
                        files = {'file': (uploaded_file.name, uploaded_file, uploaded_file.type)}
                        try:
                            res = requests.post(f"{BACKEND_URL}/api/tool/{selected_tool_id}/approve", files=files)
                            if res.status_code == 200:
                                st.success("Approval transmitted securely to Provider's 'Approvals' folder.")
                            else:
                                st.error("Failed to send approval.")
                        except Exception as e:
                            st.error(f"Error sending file: {e}")

elif base_role == "Registry Admin":
    st.header("Global User & Organization Registry")
    st.write("Centralized registry of all participants in the Data Space.")
    
    tab1, tab2 = st.tabs(["Organizations", "Users"])
    
    with tab1:
        st.subheader("Registered Organizations")
        orgs = get_organizations()
        if orgs:
            df_orgs = pd.DataFrame(orgs)
            st.dataframe(df_orgs)
        else:
            st.info("No organizations found.")
            
    with tab2:
        st.subheader("Registered Users")
        users = get_users()
        if users:
            df_users = pd.DataFrame(users)
            st.dataframe(df_users)
        else:
            st.info("No users found.")

