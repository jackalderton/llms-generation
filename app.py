import streamlit as st
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="LLMS.txt Builder", page_icon="JAFavicon.png", layout="wide")

# -------------------------
# Force Dark Mode CSS
# -------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');

/* Global */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0e1117 !important;
    color: #E0E0E0 !important;
    font-family: 'Montserrat', sans-serif;
}

/* Titles and text */
h1, h2, h3, p, label, span {
    font-family: 'Montserrat', sans-serif !important;
    color: #E0E0E0 !important;
}

.st-emotion-cache-1j0k826 {
    text-align: center;
    color: #4A90E2 !important;
    font-size: 3em;
    padding-bottom: 0.5em;
    border-bottom: 2px solid #4A90E2;
    font-family: 'Montserrat', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #1a1e24 !important;
    border-right: 1px solid #4A90E2;
}
.streamlit-expanderHeader {
    background-color: #363945 !important;
    border-radius: 8px;
    padding: 10px 15px;
    margin-bottom: 10px;
    border: none;
    font-weight: bold;
    color: #E0E0E0 !important;
}

/* Buttons */
.stButton>button {
    width: 100%;
    background-color: #323640 !important;
    color: #E0E0E0 !important;
    border: 1px solid #4A90E2;
    border-radius: 8px;
    padding: 10px;
    transition: background-color 0.3s, color 0.3s;
}
.stButton>button:hover {
    background-color: #4A90E2 !important;
    color: white !important;
    border-color: white;
}

/* Tabs (class names may change between Streamlit versions) */
.st-emotion-cache-1cypcdb {
    background-color: #323640 !important;
}
.st-emotion-cache-1cypcdb .st-emotion-cache-1q8867a {
    color: #E0E0E0 !important;
}
.st-emotion-cache-1cypcdb .st-emotion-cache-1q8867a[data-selected="true"] {
    color: #4A90E2 !important;
    border-bottom: 3px solid #4A90E2;
}

/* Inputs and textareas */
.stTextInput>div>div>input,
.stTextArea>div>textarea {
    background-color: #1a1e24 !important;
    color: #E0E0E0 !important;
    border: 1px solid #4A90E2 !important;
}

/* Code blocks */
[data-testid="stCodeBlock"] {
    background-color: #1a1e24 !important;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ------------- Helpers & State -------------
def init_state():
    if "client" not in st.session_state:
        st.session_state.client = {
            "name": "",
            "description": "",
            "email": "",
        }
    if "groups" not in st.session_state:
        st.session_state.groups = [
            {
                "name": "Group 1",
                "pages": [
                    {"page_name": "", "page_url": "", "page_desc": ""}
                ],
            }
        ]

def add_group():
    idx = len(st.session_state.groups) + 1
    st.session_state.groups.append(
        {"name": f"Group {idx}", "pages": [{"page_name": "", "page_url": "", "page_desc": ""}]}
    )

def remove_group(i):
    if len(st.session_state.groups) > 1:
        st.session_state.groups.pop(i)

def add_page(i):
    st.session_state.groups[i]["pages"].append({"page_name": "", "page_url": "", "page_desc": ""})

def remove_page(i, j):
    pages = st.session_state.groups[i]["pages"]
    if len(pages) > 1:
        pages.pop(j)

def sanitize(s: str) -> str:
    return (s or "").strip()

def build_llms_text(client, groups) -> str:
    name = sanitize(client["name"]) or "{Client name}"
    desc = sanitize(client["description"]) or "{Client description - multiple lines}"
    email = sanitize(client["email"]) or "{Client email}"

    lines = [f"# {name}", "", f"> {desc}", ""]
    for g in groups:
        gname = sanitize(g["name"]) or "{Group name}"
        lines.append(f"## {gname}")
        lines.append("")
        for p in g["pages"]:
            pn = sanitize(p["page_name"]) or "{Page name}"
            pu = sanitize(p["page_url"]) or "{Page URL}"
            pd = sanitize(p["page_desc"])
            if pd:
                lines.append(f"- [{pn}]({pu}): {pd}")
            else:
                lines.append(f"- [{pn}]({pu})")
        lines.append("")  # blank line after each group

    lines.append("## AI Usage")
    lines.append("")
    lines.append("We permit AI summarisation and linking to our public content.")
    lines.append("Use of our materials for AI model training requires prior consent.")
    lines.append(f"Contact us for licensing enquiries: {email}")
    return "\n".join(lines).rstrip() + "\n"

init_state()

# ------------- UI -------------
st.title("LLMS.txt generator")
st.caption("Create and download a structured LLMS.txt with groups and pages. Use +/– to add or remove items. Tool created by someone who doesn't entirely know what he's doing.")

with st.expander("Client details", expanded=True):
    c1, c2 = st.columns([1, 1])
    with c1:
        st.session_state.client["name"] = st.text_input(
            "Client name",
            value=st.session_state.client["name"],
            placeholder="e.g., Acme Corp"
        )
    with c2:
        st.session_state.client["email"] = st.text_input(
            "Client email",
            value=st.session_state.client["email"],
            placeholder="e.g., partnerships@acme.com"
        )
    st.session_state.client["description"] = st.text_area(
        "Client description (supports multiple lines)",
        value=st.session_state.client["description"],
        placeholder="Brief overview of the client, products/services, brand notes, etc.",
        height=120
    )

st.markdown("---")
st.subheader("Groups & Pages")

# Render each group and its pages
for i, group in enumerate(st.session_state.groups):
    with st.container(border=True):
        top = st.columns([6, 1, 1, 1])
        st.session_state.groups[i]["name"] = top[0].text_input(
            f"Group name #{i+1}",
            value=group["name"],
            key=f"group_name_{i}",
            placeholder="e.g., Product Pages"
        )
        if top[3].button("🗑️ Group", key=f"delete_group_{i}", help="Delete this group"):
            remove_group(i)
            st.rerun()

        st.markdown("**Pages in this group**")
        for j, page in enumerate(group["pages"]):
            with st.container():
                cols = st.columns([3, 3, 6, 1])
                st.session_state.groups[i]["pages"][j]["page_name"] = cols[0].text_input(
                    f"Page name (Group {i+1}, Page {j+1})",
                    value=page["page_name"],
                    key=f"page_name_{i}_{j}",
                    placeholder="e.g., Pricing"
                )
                st.session_state.groups[i]["pages"][j]["page_url"] = cols[1].text_input(
                    f"Page URL (Group {i+1}, Page {j+1})",
                    value=page["page_url"],
                    key=f"page_url_{i}_{j}",
                    placeholder="https://www.example.com/pricing"
                )
                st.session_state.groups[i]["pages"][j]["page_desc"] = cols[2].text_input(
                    f"Page description (Group {i+1}, Page {j+1})",
                    value=page["page_desc"],
                    key=f"page_desc_{i}_{j}",
                    placeholder="Short description of the page"
                )
                if cols[3].button("➖", key=f"remove_page_single_{i}_{j}", help="Remove this page"):
                    remove_page(i, j)
                    st.rerun()

        # Add Page button at bottom of group
        bottom_buttons = st.columns([1, 1])
        if bottom_buttons[0].button("➕ Page", key=f"add_page_bottom_{i}", help="Add a page to this group"):
            add_page(i)
            st.rerun()

st.markdown("")
add_cols = st.columns([1, 1])
if add_cols[0].button("➕ Add group"):
    add_group()
    st.rerun()

# ------------- Output / Download -------------
st.markdown("---")
st.subheader("Preview")

content = build_llms_text(st.session_state.client, st.session_state.groups)
st.code(content, language="markdown")

buf = BytesIO(content.encode("utf-8"))
default_filename = "LLMS.txt"

dl_col1, dl_col2 = st.columns([1, 2])
with dl_col1:
    st.download_button(
        label="⬇️ Download LLMS.txt",
        data=buf,
        file_name=default_filename,
        mime="text/plain"
    )
with dl_col2:
    st.caption(f"Generated {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
