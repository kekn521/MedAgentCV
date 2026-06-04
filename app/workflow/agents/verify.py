from __future__ import annotations

from typing import Dict

from langchain_core.messages import AIMessage

from app.config import get_settings
from app.workflow.state import GraphState
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


def run_verify_agent(state: GraphState) -> Dict[str, object]:
	settings = get_settings()
	llm = ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key)

	prompt = ChatPromptTemplate.from_messages(
		[
			(
				"system",
				"""You are a rigorous medical QA reviewer specializing in radiological report validation.

				Your role is to detect inconsistencies, unsupported claims, or hallucinations in a draft analysis by cross-checking it against the original user description.

				Review criteria — flag if any of the following occur:
				- **Contradiction**: The draft states something that directly conflicts with the user description.
				- **Hallucination**: The draft asserts a finding not present in the user description or CV findings (fabricated detail).
				- **Unsupported inference**: The draft draws a clinical conclusion beyond what is supported by either the user description or the CV findings. (Note: Any finding mentioned in the user description is considered fully supported and should not be flagged).
				- **Omission**: A clinically significant detail from the user description is missing from the draft.
				- **Terminology mismatch**: Anatomical or radiological terms used inconsistently or incorrectly.

				Response rules:
				- If the draft is fully consistent and grounded: reply with exactly `CONSISTENT`.
				- If issues are found: reply with a structured list of flagged issues, each labeled with its type (e.g., `[HALLUCINATION]`, `[CONTRADICTION]`, `[OMISSION]`), the specific text in question, and a brief explanation.
				- Be precise and concise — do not rewrite the analysis, only report issues.""",
			),
			(
				"human",
				"""Please verify the following:

				**User Description:** {description}

				**Draft Analysis:**
				{draft}

				Report any inconsistencies, hallucinations, or unsupported claims using the specified format.""",
			),
		]
	)

	response = llm.invoke(
		prompt.format_messages(
			description=state["disease_description"],
			draft=state["draft_analysis"],
		)
	)

	content = response.content.strip()
	is_consistent = content.upper().startswith("CONSISTENT")
	message = AIMessage(content=content)

	return {
		"verification_feedback": content,
		"is_consistent": is_consistent,
		"iterations": state.get("iterations", 0) + 1,
		"messages": state.get("messages", []) + [message],
	}
