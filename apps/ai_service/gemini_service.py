"""
Gemini AI Integration Service
"""
import os
from django.conf import settings
import json
import time
from typing import Dict, List, Any, Optional


# Force pure-Python protobuf implementation for Python 3.14 compatibility
os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")


def lazy_import_genai():
    """Import and configure google.generativeai lazily to avoid import-time side effects."""
    import google.generativeai as _genai  # Local import to defer protobuf bindings
    _genai.configure(api_key=settings.GEMINI_API_KEY)
    return _genai


class GeminiService:
    """Service class for interacting with Gemini AI."""
    
    def __init__(self):
        # Defer model creation to call time to avoid import-time failures
        self.default_model_name = 'gemini-2.0-flash-exp'
    
    def _call_gemini(
        self,
        prompt: str,
        model_name: str = 'gemini-2.0-flash-exp',
        response_schema: Optional[Dict] = None,
        use_search: bool = False
    ) -> Any:
        """
        Call Gemini AI API.
        
        Args:
            prompt: The prompt to send
            model_name: Model to use
            response_schema: JSON schema for structured output
            use_search: Whether to use Google Search
        
        Returns:
            Response text or parsed JSON
        """
        try:
            config = {}

            if response_schema:
                config['response_mime_type'] = "application/json"
                config['response_schema'] = response_schema

            if use_search:
                config['tools'] = [{'google_search': {}}]

            genai = lazy_import_genai()
            model = genai.GenerativeModel(model_name or self.default_model_name)

            generation_config = genai.types.GenerationConfig(**config) if config else None

            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )

            text = response.text
            
            if response_schema:
                # Clean and parse JSON
                cleaned_text = text.strip()
                if cleaned_text.startswith('```json'):
                    cleaned_text = cleaned_text[7:]
                if cleaned_text.endswith('```'):
                    cleaned_text = cleaned_text[:-3]
                cleaned_text = cleaned_text.strip()
                
                try:
                    return json.loads(cleaned_text)
                except json.JSONDecodeError as e:
                    print(f"Failed to parse JSON: {e}")
                    print(f"Response: {cleaned_text}")
                    raise ValueError("Received invalid JSON from API")
            
            return text
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            error_msg = str(e)
            
            # Log detailed error for debugging (but don't expose to user)
            logger.error(f"Gemini API call failed: {error_msg}", exc_info=True)
            
            # Provide user-friendly error message
            if "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
                raise Exception("AI service rate limit exceeded. Please try again later.")
            elif "invalid" in error_msg.lower() or "malformed" in error_msg.lower():
                raise ValueError("Invalid request format. Please check your input.")
            else:
                raise Exception("AI service temporarily unavailable. Please try again later.")
    
    def generate_clarifying_questions(
        self,
        patient_data: Dict,
        language: str = 'en'
    ) -> List[str]:
        """Generate clarifying questions based on patient data."""
        
        lang_map = {
            'uz-L': 'Uzbek (Latin script)',
            'uz-C': 'Uzbek (Cyrillic script)',
            'ru': 'Russian',
            'en': 'English'
        }
        
        target_lang = lang_map.get(language, 'English')
        
        prompt = f"""
        Based on the following patient information, generate 3-5 clarifying questions
        that would help in making a more accurate diagnosis.
        
        Patient Information:
        - Complaints: {patient_data.get('complaints', 'Not provided')}
        - History: {patient_data.get('history', 'Not provided')}
        - Objective Data: {patient_data.get('objectiveData', 'Not provided')}
        - Lab Results: {patient_data.get('labResults', 'Not provided')}
        
        Return the questions in {target_lang} language as a JSON array of strings.
        Format: {{"questions": ["Question 1?", "Question 2?", ...]}}
        """
        
        schema = {
            "type": "object",
            "properties": {
                "questions": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["questions"]
        }
        
        result = self._call_gemini(prompt, response_schema=schema)
        return result.get('questions', [])
    
    def recommend_specialists(
        self,
        patient_data: Dict,
        language: str = 'en'
    ) -> Dict:
        """Recommend specialists based on patient data and disease condition."""
        
        lang_map = {
            'uz-L': 'Uzbek (Latin script)',
            'uz-C': 'Uzbek (Cyrillic script)',
            'ru': 'Russian',
            'en': 'English'
        }
        
        target_lang = lang_map.get(language, 'English')
        
        # Extract comprehensive patient information
        complaints = patient_data.get('complaints', 'Not provided')
        history = patient_data.get('history', 'Not provided')
        objective_data = patient_data.get('objectiveData', 'Not provided')
        lab_results = patient_data.get('labResults', 'Not provided')
        additional_info = patient_data.get('additionalInfo', 'Not provided')
        age = patient_data.get('age', 'Not provided')
        gender = patient_data.get('gender', 'Not provided')
        current_medications = patient_data.get('currentMedications', 'Not provided')
        
        # Analyze the disease/symptom pattern to recommend appropriate medical specialties
        prompt = f"""
        You are a medical consultation coordinator. Based on the patient's condition, symptoms, and clinical data, 
        recommend 5-6 MEDICAL SPECIALTIES (not AI models) that are MOST RELEVANT and NECESSARY for this specific case.
        
        IMPORTANT: The specialty selection MUST be based on the DISEASE/SYMPTOM TYPE. Different diseases require 
        different specialist teams. DO NOT recommend a generic team - tailor it to the specific medical condition.
        
        CRITICAL: Recommend MEDICAL SPECIALTIES (e.g., "Cardiology", "Neurology", "Radiology", etc.), NOT AI model names.
        The AI models will be assigned to these specialties automatically by the system.
        
        Patient Information:
        - Age: {age}
        - Gender: {gender}
        - Chief Complaints (Symptoms): {complaints}
        - Medical History: {history}
        - Objective Physical Examination Data: {objective_data}
        - Laboratory Results: {lab_results}
        - Current Medications: {current_medications}
        - Additional Information: {additional_info}
        
        Available Medical Specialties (use EXACT names):
        - "Cardiology" (Heart and cardiovascular diseases, chest pain, hypertension, arrhythmias)
        - "Neurology" (Brain, nerves, headaches, seizures, neurological conditions)
        - "Radiology" (Medical imaging interpretation, X-rays, CT scans, MRIs, ultrasound)
        - "Oncology" (Cancer, tumors, malignancies, cancer diagnosis and treatment)
        - "Endocrinology" (Hormones, diabetes, thyroid disorders, metabolic conditions)
        - "Gastroenterology" (Digestive system, liver, stomach, intestines)
        - "Pulmonology" (Lungs, respiratory system, breathing disorders)
        - "Nephrology" (Kidneys, renal diseases, dialysis)
        - "Rheumatology" (Joints, autoimmune diseases, arthritis)
        - "Infectious Disease" (Infections, bacterial/viral diseases, antibiotics)
        - "Hematology" (Blood disorders, anemia, clotting problems)
        - "Geriatrics" (Elderly care, age-related conditions)
        - "Emergency Medicine" (Acute care, trauma, critical conditions)
        - "Internal Medicine" (General medicine, complex multi-system diseases)
        - "Pediatrics" (Children's health, pediatric conditions)
        - "Dermatology" (Skin conditions, dermatological diseases)
        - "Orthopedics" (Bones, joints, fractures, musculoskeletal)
        - "Urology" (Urinary system, kidneys, bladder)
        - "Gynecology" (Women's reproductive health)
        - "Psychiatry" (Mental health, psychological conditions)
        
        Analysis Instructions:
        1. Identify the PRIMARY disease/symptom category (e.g., cardiovascular, neurological, gastrointestinal, respiratory, oncological, endocrine, etc.)
        2. Select 5-6 MEDICAL SPECIALTIES (not AI models) that directly relate to the identified condition and its complications
        3. Consider related organ systems and potential comorbidities
        4. Prioritize specialties based on disease relevance - the most important specialties first
        5. For each specialty, provide a clear reason explaining why this medical specialty is needed for THIS SPECIFIC CASE and how it relates to the disease/symptoms
        
        Examples:
        - For chest pain + cardiac symptoms → Recommend: Cardiology (primary), Radiology (for imaging), Emergency Medicine (if acute), etc.
        - For headache + neurological symptoms → Recommend: Neurology (primary), Radiology (for brain imaging), Emergency Medicine (if severe), etc.
        - For suspected cancer/tumor → Recommend: Oncology (primary), Radiology (for imaging), relevant organ specialty (e.g., Gastroenterology for GI cancer), etc.
        - For diabetes/metabolic issues → Recommend: Endocrinology (primary), Cardiology (complications), Nephrology (kidney complications), etc.
        
        Return recommendations in {target_lang} with this JSON format:
        {{
            "recommendations": [
                {{
                    "specialty": "Cardiology",
                    "reason": "Detailed explanation why this specialty is needed for this specific case"
                }}
            ]
        }}
        
        Make sure to return exactly 5-6 specialty recommendations based on disease-specific needs.
        DO NOT include AI model names in your response - only medical specialties.
        """
        
        schema = {
            "type": "object",
            "properties": {
                "recommendations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "specialty": {"type": "string"},
                            "reason": {"type": "string"}
                        },
                        "required": ["specialty", "reason"]
                    },
                    "minItems": 5,
                    "maxItems": 6
                }
            },
            "required": ["recommendations"]
        }
        
        result = self._call_gemini(prompt, response_schema=schema, model_name='gemini-2.0-flash-exp')
        
        # Map specialties to AI models
        specialty_to_model = {
            'Cardiology': 'Gemini',
            'Neurology': 'Claude',
            'Radiology': 'GPT',
            'Oncology': 'Llama',
            'Endocrinology': 'Grok',
            # Default mappings for other specialties
            'Gastroenterology': 'Gemini',
            'Pulmonology': 'GPT',
            'Nephrology': 'Gemini',
            'Rheumatology': 'Claude',
            'Infectious Disease': 'Llama',
            'Hematology': 'Llama',
            'Geriatrics': 'Gemini',
            'Emergency Medicine': 'GPT',
            'Internal Medicine': 'Gemini',
            'Pediatrics': 'Claude',
            'Dermatology': 'GPT',
            'Orthopedics': 'GPT',
            'Urology': 'Gemini',
            'Gynecology': 'Gemini',
            'Psychiatry': 'Claude',
        }
        
        # Add AI model to each recommendation
        if result.get('recommendations'):
            for rec in result['recommendations']:
                specialty_name = rec.get('specialty', '')
                rec['model'] = specialty_to_model.get(specialty_name, 'Gemini')  # Default fallback
        
        return result
    
    def generate_initial_diagnoses(
        self,
        patient_data: Dict,
        language: str = 'en'
    ) -> List[Dict]:
        """Generate initial differential diagnoses."""
        
        lang_map = {
            'uz-L': 'Uzbek (Latin script)',
            'uz-C': 'Uzbek (Cyrillic script)',
            'ru': 'Russian',
            'en': 'English'
        }
        
        target_lang = lang_map.get(language, 'English')
        
        prompt = f"""
        Based on the patient information, generate 3-5 differential diagnoses
        with probability estimates and justification.
        
        Patient Information:
        - Name: {patient_data.get('firstName', '')} {patient_data.get('lastName', '')}
        - Age: {patient_data.get('age', 'Not provided')}
        - Gender: {patient_data.get('gender', 'Not provided')}
        - Complaints: {patient_data.get('complaints', 'Not provided')}
        - History: {patient_data.get('history', 'Not provided')}
        - Objective Data: {patient_data.get('objectiveData', 'Not provided')}
        - Lab Results: {patient_data.get('labResults', 'Not provided')}
        
        Return in {target_lang} with this JSON format:
        {{
            "diagnoses": [
                {{
                    "name": "Diagnosis name",
                    "probability": 0.75,
                    "justification": "Why this diagnosis is likely",
                    "evidenceLevel": "High/Moderate/Low"
                }}
            ]
        }}
        """
        
        schema = {
            "type": "object",
            "properties": {
                "diagnoses": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "probability": {"type": "number"},
                            "justification": {"type": "string"},
                            "evidenceLevel": {"type": "string"}
                        },
                        "required": ["name", "probability", "justification", "evidenceLevel"]
                    }
                }
            },
            "required": ["diagnoses"]
        }
        
        result = self._call_gemini(prompt, response_schema=schema)
        return result.get('diagnoses', [])
    
    def generate_final_report(
        self,
        patient_data: Dict,
        debate_history: List[Dict],
        diagnoses: List[Dict],
        language: str = 'en'
    ) -> Dict:
        """Generate final medical report."""
        
        lang_map = {
            'uz-L': 'Uzbek (Latin script)',
            'uz-C': 'Uzbek (Cyrillic script)',
            'ru': 'Russian',
            'en': 'English'
        }
        
        target_lang = lang_map.get(language, 'English')
        
        # Prepare debate summary
        debate_summary = "\n".join([
            f"{msg.get('author', 'Unknown')}: {msg.get('content', '')[:200]}..."
            for msg in debate_history[-10:]  # Last 10 messages
        ])
        
        prompt = f"""
        Generate a comprehensive medical report based on the AI council discussion.
        
        Patient: {patient_data.get('firstName', '')} {patient_data.get('lastName', '')}
        Age: {patient_data.get('age', '')}, Gender: {patient_data.get('gender', '')}
        
        Chief Complaints: {patient_data.get('complaints', '')}
        
        Differential Diagnoses Considered:
        {json.dumps(diagnoses, indent=2)}
        
        Debate Summary:
        {debate_summary}
        
        Generate a complete report in {target_lang} with:
        - Consensus diagnosis (most likely diagnoses with probability)
        - Rejected hypotheses and why
        - Recommended tests
        - Treatment plan
        - Medication recommendations
        - Follow-up plan
        - Prognosis
        - Any unexpected findings
        
        Return as structured JSON.
        """
        
        schema = {
            "type": "object",
            "properties": {
                "consensusDiagnosis": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "probability": {"type": "number"},
                            "justification": {"type": "string"},
                            "evidenceLevel": {"type": "string"}
                        }
                    }
                },
                "rejectedHypotheses": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "reason": {"type": "string"}
                        }
                    }
                },
                "recommendedTests": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "treatmentPlan": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "medicationRecommendations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "dosage": {"type": "string"},
                            "notes": {"type": "string"}
                        }
                    }
                },
                "unexpectedFindings": {"type": "string"}
            }
        }
        
        result = self._call_gemini(prompt, response_schema=schema)
        return result
    
    def check_drug_interactions(
        self,
        medications: List[str],
        language: str = 'en'
    ) -> List[Dict]:
        """Check for drug interactions."""
        
        lang_map = {
            'uz-L': 'Uzbek (Latin script)',
            'uz-C': 'Uzbek (Cyrillic script)',
            'ru': 'Russian',
            'en': 'English'
        }
        
        target_lang = lang_map.get(language, 'English')
        
        medications_str = ", ".join(medications)
        
        prompt = f"""
        Check for potential drug interactions between these medications:
        {medications_str}
        
        Return interactions in {target_lang} with JSON format:
        {{
            "interactions": [
                {{
                    "interaction": "Drug A + Drug B",
                    "severity": "High/Medium/Low",
                    "mechanism": "How they interact",
                    "management": "What to do"
                }}
            ]
        }}
        """
        
        schema = {
            "type": "object",
            "properties": {
                "interactions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "interaction": {"type": "string"},
                            "severity": {"type": "string"},
                            "mechanism": {"type": "string"},
                            "management": {"type": "string"}
                        }
                    }
                }
            }
        }
        
        result = self._call_gemini(prompt, response_schema=schema)
        return result.get('interactions', [])
    
    def suggest_cme_topics(
        self,
        analyses: List[Dict],
        language: str = 'en'
    ) -> List[Dict]:
        """Suggest CME topics based on user's case history."""
        
        lang_map = {
            'uz-L': 'Uzbek (Latin script)',
            'uz-C': 'Uzbek (Cyrillic script)',
            'ru': 'Russian',
            'en': 'English'
        }
        
        target_lang = lang_map.get(language, 'English')
        
        # Extract diagnoses from analyses
        diagnoses = []
        for analysis in analyses[:10]:  # Last 10 analyses
            if isinstance(analysis, dict) and 'final_report' in analysis:
                report = analysis['final_report']
                if isinstance(report, dict) and 'consensusDiagnosis' in report:
                    for dx in report['consensusDiagnosis']:
                        if isinstance(dx, dict):
                            diagnoses.append(dx.get('name', ''))
        
        diagnoses_str = ", ".join(set(diagnoses[:20]))
        
        prompt = f"""
        Based on these recent cases: {diagnoses_str}
        
        Suggest 3-5 CME (Continuing Medical Education) topics that would be
        most relevant for this physician in {target_lang}.
        
        Return as JSON:
        {{
            "topics": [
                {{
                    "topic": "Topic name",
                    "relevance": "Why this is relevant"
                }}
            ]
        }}
        """
        
        schema = {
            "type": "object",
            "properties": {
                "topics": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "topic": {"type": "string"},
                            "relevance": {"type": "string"}
                        }
                    }
                }
            }
        }
        
        result = self._call_gemini(prompt, response_schema=schema)
        return result.get('topics', [])


# Singleton instance (safe: no heavy imports in __init__)
gemini_service = GeminiService()
