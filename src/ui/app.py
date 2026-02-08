import streamlit as st
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.generation.llm_generator import COREPGenerator
from src.validation.validator import CR1Validator
from src.validation.template_exporter import CR1Exporter
from src.schemas import CR1Template

# Page config
st.set_page_config(
    page_title="COREP CR1 Assistant",
    page_icon="",
    layout="wide"
)

# Initialize session state
if 'generator' not in st.session_state:
    st.session_state.generator = COREPGenerator()
    st.session_state.validator = CR1Validator()
    st.session_state.exporter = CR1Exporter()
    st.session_state.rows = []

# Title
st.title(" COREP CR1 Reporting Assistant")
st.markdown("**LLM-assisted PRA COREP reporting tool** - Prototype focused on Credit Risk (Standardised Approach)")

# Sidebar
with st.sidebar:
    st.header(" About")
    st.markdown("""
    This prototype demonstrates:
    - 📚 RAG retrieval of PRA Rulebook
    - 🤖 LLM-powered data extraction
    - ✅ Validation & audit trails
    - 📊 COREP template generation
    """)
    
    st.divider()
    
    if st.button(" Clear All Entries"):
        st.session_state.rows = []
        st.rerun()

# Main interface
st.header("Enter Exposure Information")

# Input form
with st.form("exposure_form"):
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_input(
            "Describe your exposure",
            placeholder="e.g., £50 million in unrated corporate exposures",
            help="Enter exposure details in natural language"
        )
    
    with col2:
        submit = st.form_submit_button("➕ Add Exposure", use_container_width=True)

if submit and query:
    with st.spinner("🔍 Processing..."):
        try:
            # Generate CR1 row
            result = st.session_state.generator.generate_cr1_row(query)
            st.session_state.rows.append(result)
            
            st.success("✅ Exposure added successfully!")
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Display current entries
if st.session_state.rows:
    st.divider()
    st.header(" Current Entries")
    
    for i, result in enumerate(st.session_state.rows):
        row = result['cr1_row']
        
        with st.expander(f"**{i+1}. {row.exposure_class.value}** - £{row.original_exposure_value:,.0f}", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Original Exposure", f"£{row.original_exposure_value:,.0f}")
            with col2:
                st.metric("Risk Weight", f"{row.risk_weight_percent}%")
            with col3:
                st.metric("RWA", f"£{row.risk_weighted_assets:,.0f}")
            
            st.markdown("**💡 Reasoning:**")
            st.info(result['reasoning'])
            
            if row.regulatory_references:
                st.markdown("** Regulatory Basis:**")
                for ref in row.regulatory_references:
                    st.markdown(f"- {ref.source}")

    # Summary
    st.divider()
    st.header(" Summary")
    
    total_exposure = sum(r['cr1_row'].original_exposure_value for r in st.session_state.rows)
    total_rwa = sum(r['cr1_row'].risk_weighted_assets for r in st.session_state.rows)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Exposure", f"£{total_exposure:,.0f}")
    with col2:
        st.metric("Total RWA", f"£{total_rwa:,.0f}")
    with col3:
        avg_rw = (total_rwa / total_exposure * 100) if total_exposure > 0 else 0
        st.metric("Average Risk Weight", f"{avg_rw:.1f}%")
    
    # Validation
    st.divider()
    st.header("✅ Validation")
    
    template = CR1Template(
        rows=[r['cr1_row'] for r in st.session_state.rows],
        total_exposure=total_exposure,
        total_rwa=total_rwa
    )
    
    validation = st.session_state.validator.validate_template(template)
    
    if validation['is_valid']:
        st.success("✅ All validations passed!")
    else:
        st.error("❌ Validation errors found:")
        for error in validation['errors']:
            st.write(f"- {error}")
    
    if validation['warnings']:
        st.warning("⚠️ Warnings:")
        for warning in validation['warnings']:
            st.write(f"- {warning}")
    
    # Export buttons
    st.divider()
    st.header("📥 Export")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Export to Excel", use_container_width=True):
            with st.spinner("Generating Excel..."):
                excel_path = st.session_state.exporter.export_to_excel(template)
                st.success(f"✅ Exported to: `{excel_path}`")
                
                # Provide download button
                with open(excel_path, 'rb') as f:
                    st.download_button(
                        label="⬇️ Download Excel",
                        data=f,
                        file_name=Path(excel_path).name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
    
    with col2:
        if st.button("📄 Export Audit Trail", use_container_width=True):
            with st.spinner("Generating audit trail..."):
                audit_path = st.session_state.exporter.export_audit_trail(template)
                st.success(f"✅ Exported to: `{audit_path}`")
                
                # Provide download button
                with open(audit_path, 'r', encoding='utf-8') as f:
                    st.download_button(
                        label="⬇️ Download Audit Trail",
                        data=f,
                        file_name=Path(audit_path).name,
                        mime="text/plain"
                    )

else:
    st.info("👆 Enter your first exposure above to get started")

# Footer
st.divider()
st.caption("🔬 Prototype - For demonstration purposes only. Not for production use.")