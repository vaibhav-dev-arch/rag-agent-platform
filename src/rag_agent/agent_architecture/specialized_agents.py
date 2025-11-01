"""
Specialized Agent Examples for Different Use Cases
This shows how to customize agents for specific industries and applications
"""

import os
from dotenv import load_dotenv
from llama_index.core import Settings, VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

load_dotenv()

class LegalAgent:
    """Specialized agent for legal research and analysis"""
    
    def __init__(self):
        self.setup_llamaindex()
        self.memory = ChatMemoryBuffer.from_defaults(token_limit=3000)
        self.tools = self.create_legal_tools()
        self.agent = self.create_agent()
    
    def setup_llamaindex(self):
        """Setup LlamaIndex with OpenAI models"""
        Settings.llm = OpenAI(model="gpt-3.5-turbo", temperature=0.1)
        Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
        Settings.chunk_size = 1024
        Settings.chunk_overlap = 20
    
    def create_legal_tools(self) -> List[FunctionTool]:
        """Create legal-specific tools"""
        tools = [
            FunctionTool.from_defaults(fn=self.search_case_law, name="search_case_law"),
            FunctionTool.from_defaults(fn=self.analyze_contract, name="analyze_contract"),
            FunctionTool.from_defaults(fn=self.check_compliance, name="check_compliance"),
            FunctionTool.from_defaults(fn=self.generate_legal_brief, name="generate_legal_brief"),
            FunctionTool.from_defaults(fn=self.find_precedents, name="find_precedents"),
            FunctionTool.from_defaults(fn=self.calculate_damages, name="calculate_damages"),
        ]
        return tools
    
    def create_agent(self) -> ReActAgent:
        """Create the legal agent"""
        agent = ReActAgent.from_tools(
            tools=self.tools,
            llm=Settings.llm,
            memory=self.memory,
            verbose=True,
            system_prompt="""You are a specialized legal research assistant with access to legal tools and databases.

            Your capabilities include:
            - Searching case law and legal precedents
            - Analyzing contracts and legal documents
            - Checking compliance with regulations
            - Generating legal briefs and documents
            - Finding relevant precedents
            - Calculating damages and settlements

            Always provide accurate legal information and cite relevant sources.
            When dealing with legal matters, always recommend consulting with a qualified attorney.
            Be thorough in your research and provide comprehensive analysis."""
        )
        return agent
    
    # Legal-specific tool implementations
    def search_case_law(self, query: str) -> str:
        """Search case law database"""
        try:
            print(f"⚖️ Searching case law for: {query}")
            
            # Mock case law database
            case_law_db = {
                "contract breach": "Smith v. Jones (2023): Established that material breach requires substantial non-performance.",
                "intellectual property": "TechCorp v. InnovateInc (2022): Clarified fair use in software development.",
                "employment law": "Workers v. CorpCo (2023): Defined reasonable accommodation requirements.",
                "privacy rights": "Citizen v. DataCorp (2022): Established data protection standards."
            }
            
            return case_law_db.get(query.lower(), f"Case law search for '{query}': No relevant cases found.")
        except Exception as e:
            return f"Error searching case law: {str(e)}"
    
    def analyze_contract(self, contract_text: str) -> str:
        """Analyze contract for potential issues"""
        try:
            print(f"📋 Analyzing contract...")
            
            # Simple contract analysis
            issues = []
            if "liability" not in contract_text.lower():
                issues.append("Missing liability clause")
            if "termination" not in contract_text.lower():
                issues.append("Missing termination clause")
            if "payment" not in contract_text.lower():
                issues.append("Missing payment terms")
            
            analysis = f"Contract Analysis:\n"
            if issues:
                analysis += f"Issues found: {', '.join(issues)}\n"
            else:
                analysis += "No major issues detected.\n"
            
            analysis += f"Contract length: {len(contract_text)} characters\n"
            analysis += "Recommendation: Have contract reviewed by legal counsel"
            
            return analysis
        except Exception as e:
            return f"Error analyzing contract: {str(e)}"
    
    def check_compliance(self, regulation: str, practice: str) -> str:
        """Check compliance with regulations"""
        try:
            print(f"✅ Checking compliance with {regulation}...")
            
            # Mock compliance checker
            compliance_db = {
                "gdpr": "GDPR compliance requires data protection, consent mechanisms, and privacy by design.",
                "hipaa": "HIPAA compliance requires administrative, physical, and technical safeguards.",
                "sox": "SOX compliance requires internal controls and financial reporting accuracy.",
                "ccpa": "CCPA compliance requires consumer rights and data transparency."
            }
            
            regulation_info = compliance_db.get(regulation.lower(), f"Regulation '{regulation}' not found in database.")
            
            return f"Compliance Check for {regulation}:\n{regulation_info}\n\nPractice: {practice}\nRecommendation: Review with compliance officer"
        except Exception as e:
            return f"Error checking compliance: {str(e)}"
    
    def generate_legal_brief(self, case_summary: str) -> str:
        """Generate a legal brief"""
        try:
            print(f"📝 Generating legal brief...")
            
            brief = f"""LEGAL BRIEF
            
Case Summary: {case_summary}

I. STATEMENT OF FACTS
[Facts would be extracted from case summary]

II. LEGAL ISSUES
[Issues would be identified from case summary]

III. ARGUMENT
[Legal arguments would be developed]

IV. CONCLUSION
[Conclusion would be drawn based on analysis]

Note: This is a template brief. Actual briefs require detailed legal research and analysis."""
            
            return brief
        except Exception as e:
            return f"Error generating brief: {str(e)}"
    
    def find_precedents(self, legal_issue: str) -> str:
        """Find legal precedents for an issue"""
        try:
            print(f"🔍 Finding precedents for: {legal_issue}")
            
            precedents_db = {
                "contract dispute": "Johnson v. Smith (2021): Established good faith requirement in contracts",
                "employment discrimination": "Equal v. Corp (2020): Defined hostile work environment standards",
                "intellectual property": "Innovate v. Copy (2022): Clarified fair use boundaries",
                "product liability": "Consumer v. Manufacturer (2023): Established defect standards"
            }
            
            precedent = precedents_db.get(legal_issue.lower(), f"No precedents found for '{legal_issue}'")
            return f"Precedent found: {precedent}"
        except Exception as e:
            return f"Error finding precedents: {str(e)}"
    
    def calculate_damages(self, damage_type: str, amount: str) -> str:
        """Calculate potential damages"""
        try:
            print(f"💰 Calculating damages...")
            
            # Simple damage calculation
            base_amount = float(amount) if amount.replace('.', '').isdigit() else 1000
            
            damage_calculations = {
                "compensatory": base_amount,
                "punitive": base_amount * 2,
                "liquidated": base_amount * 1.5,
                "consequential": base_amount * 1.2
            }
            
            result = f"Damage Calculations for {damage_type}:\n"
            for damage_type_calc, amount_calc in damage_calculations.items():
                result += f"{damage_type_calc.title()}: ${amount_calc:,.2f}\n"
            
            result += "\nNote: Actual damages require detailed legal analysis and expert testimony."
            return result
        except Exception as e:
            return f"Error calculating damages: {str(e)}"
    
    def chat(self, message: str) -> str:
        """Main chat interface"""
        try:
            response = self.agent.chat(message)
            return str(response)
        except Exception as e:
            return f"Error in legal chat: {str(e)}"

class HealthcareAgent:
    """Specialized agent for healthcare and medical applications"""
    
    def __init__(self):
        self.setup_llamaindex()
        self.memory = ChatMemoryBuffer.from_defaults(token_limit=3000)
        self.tools = self.create_healthcare_tools()
        self.agent = self.create_agent()
    
    def setup_llamaindex(self):
        """Setup LlamaIndex with OpenAI models"""
        Settings.llm = OpenAI(model="gpt-3.5-turbo", temperature=0.1)
        Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
        Settings.chunk_size = 1024
        Settings.chunk_overlap = 20
    
    def create_healthcare_tools(self) -> List[FunctionTool]:
        """Create healthcare-specific tools"""
        tools = [
            FunctionTool.from_defaults(fn=self.search_medical_literature, name="search_medical_literature"),
            FunctionTool.from_defaults(fn=self.check_drug_interactions, name="check_drug_interactions"),
            FunctionTool.from_defaults(fn=self.analyze_symptoms, name="analyze_symptoms"),
            FunctionTool.from_defaults(fn=self.get_treatment_guidelines, name="get_treatment_guidelines"),
            FunctionTool.from_defaults(fn=self.check_hipaa_compliance, name="check_hipaa_compliance"),
            FunctionTool.from_defaults(fn=self.generate_patient_summary, name="generate_patient_summary"),
        ]
        return tools
    
    def create_agent(self) -> ReActAgent:
        """Create the healthcare agent"""
        agent = ReActAgent.from_tools(
            tools=self.tools,
            llm=Settings.llm,
            memory=self.memory,
            verbose=True,
            system_prompt="""You are a specialized healthcare assistant with access to medical tools and databases.

            Your capabilities include:
            - Searching medical literature and research
            - Checking drug interactions and contraindications
            - Analyzing symptoms and conditions
            - Providing treatment guidelines
            - Checking HIPAA compliance
            - Generating patient summaries

            IMPORTANT: Always remind users that this is for informational purposes only and not a substitute for professional medical advice.
            Always recommend consulting with qualified healthcare professionals for medical decisions.
            Be accurate, thorough, and prioritize patient safety."""
        )
        return agent
    
    # Healthcare-specific tool implementations
    def search_medical_literature(self, query: str) -> str:
        """Search medical literature database"""
        try:
            print(f"🏥 Searching medical literature for: {query}")
            
            # Mock medical literature database
            literature_db = {
                "diabetes": "Recent studies show that continuous glucose monitoring improves glycemic control in Type 1 diabetes.",
                "hypertension": "ACE inhibitors are first-line treatment for hypertension in patients with diabetes.",
                "covid-19": "Current guidelines recommend vaccination and booster shots for COVID-19 prevention.",
                "mental health": "Cognitive behavioral therapy is effective for treating anxiety and depression."
            }
            
            return literature_db.get(query.lower(), f"Medical literature search for '{query}': No relevant studies found.")
        except Exception as e:
            return f"Error searching medical literature: {str(e)}"
    
    def check_drug_interactions(self, drugs: str) -> str:
        """Check for drug interactions"""
        try:
            print(f"💊 Checking drug interactions for: {drugs}")
            
            # Mock drug interaction checker
            interaction_db = {
                "aspirin warfarin": "Major interaction: Increased bleeding risk",
                "metformin insulin": "Moderate interaction: Enhanced hypoglycemic effect",
                "digoxin furosemide": "Moderate interaction: Increased digoxin toxicity risk",
                "statins grapefruit": "Major interaction: Increased statin levels"
            }
            
            drug_key = " ".join(sorted(drugs.lower().split()))
            interaction = interaction_db.get(drug_key, f"No known interactions between {drugs}")
            
            return f"Drug Interaction Check:\n{drugs}\nResult: {interaction}\n\nNote: Always consult with a pharmacist or physician."
        except Exception as e:
            return f"Error checking drug interactions: {str(e)}"
    
    def analyze_symptoms(self, symptoms: str) -> str:
        """Analyze symptoms and suggest possible conditions"""
        try:
            print(f"🔍 Analyzing symptoms: {symptoms}")
            
            # Mock symptom analyzer
            symptom_db = {
                "fever cough": "Possible conditions: Common cold, flu, COVID-19, pneumonia",
                "chest pain shortness": "Possible conditions: Heart attack, angina, pulmonary embolism",
                "headache nausea": "Possible conditions: Migraine, tension headache, concussion",
                "fatigue weight loss": "Possible conditions: Diabetes, thyroid disorder, depression"
            }
            
            symptom_key = " ".join(sorted(symptoms.lower().split()))
            conditions = symptom_db.get(symptom_key, f"No specific conditions identified for symptoms: {symptoms}")
            
            return f"Symptom Analysis:\nSymptoms: {symptoms}\nPossible conditions: {conditions}\n\nIMPORTANT: This is not a diagnosis. Please consult with a healthcare professional."
        except Exception as e:
            return f"Error analyzing symptoms: {str(e)}"
    
    def get_treatment_guidelines(self, condition: str) -> str:
        """Get treatment guidelines for a condition"""
        try:
            print(f"📋 Getting treatment guidelines for: {condition}")
            
            # Mock treatment guidelines
            guidelines_db = {
                "hypertension": "Treatment: ACE inhibitors, ARBs, thiazide diuretics. Lifestyle: DASH diet, exercise, weight loss.",
                "diabetes": "Treatment: Metformin first-line, insulin if needed. Lifestyle: Carbohydrate counting, regular exercise.",
                "depression": "Treatment: SSRIs, psychotherapy, combination therapy. Lifestyle: Regular sleep, exercise, social support.",
                "asthma": "Treatment: Inhaled corticosteroids, bronchodilators. Lifestyle: Avoid triggers, regular monitoring."
            }
            
            guidelines = guidelines_db.get(condition.lower(), f"No specific guidelines found for {condition}")
            
            return f"Treatment Guidelines for {condition}:\n{guidelines}\n\nNote: Guidelines may vary by patient. Consult with healthcare provider."
        except Exception as e:
            return f"Error getting treatment guidelines: {str(e)}"
    
    def check_hipaa_compliance(self, practice_description: str) -> str:
        """Check HIPAA compliance for healthcare practices"""
        try:
            print(f"🔒 Checking HIPAA compliance...")
            
            compliance_check = f"""HIPAA Compliance Check:

Practice: {practice_description}

Required Safeguards:
✓ Administrative: Policies, training, access controls
✓ Physical: Facility access, workstation security
✓ Technical: Encryption, audit logs, access controls

Recommendations:
- Implement encryption for all PHI
- Conduct regular staff training
- Maintain audit logs
- Use secure communication methods
- Implement access controls

Note: This is a general checklist. Consult with HIPAA compliance experts."""
            
            return compliance_check
        except Exception as e:
            return f"Error checking HIPAA compliance: {str(e)}"
    
    def generate_patient_summary(self, patient_info: str) -> str:
        """Generate a patient summary"""
        try:
            print(f"📄 Generating patient summary...")
            
            summary = f"""PATIENT SUMMARY

Patient Information: {patient_info}

Assessment:
[Assessment would be based on patient information]

Plan:
[Treatment plan would be developed]

Follow-up:
[Follow-up recommendations would be provided]

Note: This is a template summary. Actual summaries require detailed medical evaluation."""
            
            return summary
        except Exception as e:
            return f"Error generating patient summary: {str(e)}"
    
    def chat(self, message: str) -> str:
        """Main chat interface"""
        try:
            response = self.agent.chat(message)
            return str(response)
        except Exception as e:
            return f"Error in healthcare chat: {str(e)}"

def demo_legal_agent():
    """Demonstrate legal agent capabilities"""
    print("⚖️ Legal Agent Demo")
    print("=" * 50)
    
    agent = LegalAgent()
    
    queries = [
        "Search for case law on contract breach",
        "Analyze this contract: 'The party agrees to deliver goods within 30 days'",
        "Check compliance with GDPR for our data processing practices",
        "Find precedents for employment discrimination cases",
        "Calculate damages for a $50,000 contract breach"
    ]
    
    for query in queries:
        print(f"\n❓ Query: {query}")
        response = agent.chat(query)
        print(f"🤖 Legal Agent: {response}")
        print("-" * 50)

def demo_healthcare_agent():
    """Demonstrate healthcare agent capabilities"""
    print("\n🏥 Healthcare Agent Demo")
    print("=" * 50)
    
    agent = HealthcareAgent()
    
    queries = [
        "Search medical literature on diabetes treatment",
        "Check drug interactions between aspirin and warfarin",
        "Analyze symptoms: fever and cough",
        "Get treatment guidelines for hypertension",
        "Check HIPAA compliance for our telemedicine practice"
    ]
    
    for query in queries:
        print(f"\n❓ Query: {query}")
        response = agent.chat(query)
        print(f"🤖 Healthcare Agent: {response}")
        print("-" * 50)

def main():
    """Main function"""
    print("🎯 Specialized Agent Examples")
    print("=" * 50)
    
    print("Choose agent type:")
    print("1. Legal Agent")
    print("2. Healthcare Agent")
    print("3. Both agents")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        demo_legal_agent()
    elif choice == "2":
        demo_healthcare_agent()
    elif choice == "3":
        demo_legal_agent()
        demo_healthcare_agent()
    else:
        print("Invalid choice. Running both demos...")
        demo_legal_agent()
        demo_healthcare_agent()

if __name__ == "__main__":
    main()

