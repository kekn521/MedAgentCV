from __future__ import annotations

from typing import Dict

from langchain_core.messages import AIMessage

from app.config import get_settings
from app.workflow.state import GraphState
from app.workflow.tools.cv_model import vinbigdata_cv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


def run_analytic_agent(state: GraphState) -> Dict[str, object]:
	settings = get_settings()
	llm = ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key)

	cv_output = vinbigdata_cv.invoke(state["image_path"])

	prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert radiological analysis assistant with deep knowledge of X-ray interpretation, pathology, and differential diagnosis.

			Your role is to synthesize computer vision (CV) findings with the clinician's description to produce a structured, evidence-grounded analysis and a reasoned differential diagnosis.

			Guidelines:
			- Ground every claim explicitly in either the CV findings or the clinician's description.
			- Treat the clinician's description as an expert radiologist's observation of the X-ray. If a finding is mentioned in either the clinician's description OR detected by CV, it is considered confirmed on imaging.
			- Clearly list all confirmed imaging findings, noting whether they were detected by the clinician, the CV tool, or both.
			- Flag ambiguous or low-confidence CV outputs explicitly.
			- Use precise anatomical and radiological terminology.
			- Never fabricate findings. If evidence is insufficient, say so.
			- For diagnosis: rank differentials by likelihood given the combined evidence. Justify each with specific findings.
			- Always append a standard medical disclaimer that this output is decision-support only and must be reviewed by a licensed clinician.

			Output format:
			1. **Imaging Findings**: All findings visible on the radiograph (supported by either clinician description, CV tool output, or both).
			2. **Uncertainties & Limitations**: Low-confidence areas, image quality issues, or ambiguous regions.
			3. **Diagnostic Assessment & Differentials**:
			- List definitively diagnosed diseases and differential diagnoses from most to least likely.
			- For each: state supporting evidence, contradicting evidence, and recommended next steps (e.g., additional imaging, labs, clinical correlation).
			4. **Summary**: A concise synthesis for clinical handoff.

			Disclaimer: This analysis is AI-generated decision support only. It must be reviewed and validated by a licensed radiologist or clinician before any clinical action is taken.""",
		),
		(
			"human",
			"""Please analyze the following:

			**User Description:** {description}

			**CV Findings:** {cv_output}

			Produce a structured radiological analysis and differential diagnosis following the output format.""",
		),
    ]
)

	response = llm.invoke(
		prompt.format_messages(
			description=state["disease_description"],
			cv_output=cv_output,
		)
	)

	message = AIMessage(content=response.content)

	return {
		"cv_tool_raw_output": cv_output,
		"draft_analysis": response.content,
		"messages": state.get("messages", []) + [message],
	}
