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
				"You are a careful medical imaging assistant. "
				"Synthesize CV findings with the user's description, "
				"clearly stating what is supported by the image and what is uncertain.",
			),
			(
				"human",
				"User description: {description}\nCV findings: {cv_output}",
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
