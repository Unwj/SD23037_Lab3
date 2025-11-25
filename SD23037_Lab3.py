import streamlit as st
import json
from streamlit_ace import st_ace

# Page config
st.set_page_config(page_title="Scholarship Decision Support System", layout="centered")
st.title("🏆 University Scholarship Advisory System")
st.markdown("A transparent rule-based decision support tool using forward chaining with priority.")

# Default rules (exactly as given in the lab)
DEFAULT_RULES = '''
[
  {
    "name": "Top merit candidate",
    "priority": 100,
    "conditions": [
      ["cgpa", ">=", 3.7],
      ["co_curricular_score", ">=", 80],
      ["family_income", "<=", 8000],
      ["disciplinary_actions", "==", 0]
    ],
    "action": {
      "decision": "AWARD_FULL",
      "reason": "Excellent academic & co-curricular performance, with acceptable need"
    }
  },
  {
    "name": "Good candidate - partial scholarship",
    "priority": 80,
    "conditions": [
      ["cgpa", ">=", 3.3],
      ["co_curricular_score", ">=", 60],
      ["family_income", "<=", 12000],
      ["disciplinary_actions", "<=", 1]
    ],
    "action": {
      "decision": "AWARD_PARTIAL",
      "reason": "Good academic & involvement record with moderate need"
    }
  },
  {
    "name": "Need-based review",
    "priority": 70,
    "conditions": [
      ["cgpa", ">=", 2.5],
      ["family_income", "<=", 4000]
    ],
    "action": {
      "decision": "REVIEW",
      "reason": "High need but borderline academic score"
    }
  },
  {
    "name": "Low CGPA - not eligible",
    "priority": 95,
    "conditions": [
      ["cgpa", "<", 2.5]
    ],
    "action": {
      "decision": "REJECT",
      "reason": "CGPA below minimum scholarship requirement"
    }
  },
  {
    "name": "Serious disciplinary record",
    "priority": 90,
    "conditions": [
      ["disciplinary_actions", ">=", 2]
    ],
    "action": {
      "decision": "REJECT",
      "reason": "Too many disciplinary records"
    }
  }
]
'''

# Simple rule engine
def evaluate_rules(facts, rules):
    triggered = []
    for rule in rules:
        name = rule["name"]
        priority = rule["priority"]
        conditions = rule["conditions"]
        action = rule["action"]
        
        all_true = True
        for cond in conditions:
            key, op, val = cond[0], cond[1], cond[2]
            value = facts.get(key)
            
            if op == "==" and value != val: all_true = False
            elif op == "!=" and value == val: all_true = False
            elif op == ">"  and not (value > val):  all_true = False
            elif op == ">=" and not (value >= val): all_true = False
            elif op == "<"  and not (value < val):  all_true = False
            elif op == "<=" and not (value <= val): all_true = False
        
        if all_true:
            triggered.append((priority, name, action))
    
    if not triggered:
        return {"decision": "NO_MATCH", "reason": "No rule matched the applicant's profile"}
    
    # Sort by priority descending, then take first
    triggered.sort(reverse=True, key=lambda x: x[0])
    winner = triggered[0]
    return {
        "decision": winner[2]["decision"],
        "reason": winner[2]["reason"],
        "triggered_rule": winner[1]
    }

# Sidebar - JSON editor
st.sidebar.header("Rule Configuration (Editable)")
rules_json = st.sidebar.text_area("Edit rules in JSON format (must be valid array):", 
                                  value=DEFAULT_RULES, height=500)

try:
    rules = json.loads(rules_json)
    st.sidebar.success("JSON loaded successfully")
except json.JSONDecodeError as e:
    st.sidebar.error(f"Invalid JSON: {e}")
    rules = []

# Main form
st.header("Applicant Information")
col1, col2 = st.columns(2)

with col1:
    cgpa = st.number_input("Cumulative GPA (CGPA)", min_value=0.0, max_value=4.0, step=0.01, value=3.5)
    co_curricular_score = st.number_input("Co-curricular involvement score (0-100)", min_value=0, max_value=100, value=75)
    family_income = st.number_input("Monthly family income (RM)", min_value=0, value=6000)

with col2:
    community_service = st.number_input("Community service hours", min_value=0, value=50)
    semester = st.number_input("Current semester of study", min_value=1, max_value=14, value=5)
    disciplinary_actions = st.number_input("Number of disciplinary actions", min_value=0, value=0)

facts = {
    "cgpa": cgpa,
    "co_curricular_score": co_curricular_score,
    "family_income": family_income,
    "disciplinary_actions": disciplinary_actions,
    # community_service and semester are collected but not used in current rules
}

if st.button("Evaluate Scholarship Eligibility", type="primary"):
    if not rules:
        st.error("Fix JSON errors first!")
    else:
        result = evaluate_rules(facts, rules)
        
        st.markdown("## Result")
        decision = result["decision"]
        
        if decision == "AWARD_FULL":
            st.success(f"**{decision}** - Full Scholarship")
        elif decision == "AWARD_PARTIAL":
            st.info(f"**{decision}** - Partial Scholarship")
        elif decision == "REVIEW":
            st.warning(f"**{decision}** - Manual Review Recommended")
        elif decision == "REJECT":
            st.error(f"**{decision}** - Not Eligible")
        else:
            st.info("No decision")
        
        st.write("**Reason:**", result["reason"])
        if "triggered_rule" in result:
            st.write("**Triggered Rule:**", result["triggered_rule"])

# Footer
st.markdown("---")
st.caption("BSD3513 Artificial Intelligence – Lab 3 | Rule-Based System with Streamlit")