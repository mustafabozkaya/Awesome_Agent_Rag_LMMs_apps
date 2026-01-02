import abc
import os
import re
import time
from typing import List, Dict, Any, Optional

from google import genai
from google.genai import types
from openai import OpenAI
from duckduckgo_search import DDGS

import streamlit as st

class LLMClient(abc.ABC):
    """Abstract base class for LLM interactions."""
    
    @abc.abstractmethod
    def create_plan(self, goal: str) -> Dict[str, Any]:
        """Creates a research plan."""
        pass

    @abc.abstractmethod
    def execute_research(self, tasks: List[str], previous_context: Any = None) -> List[Dict[str, Any]]:
        """Executes research based on tasks."""
        pass
        
    @abc.abstractmethod
    def synthesize_report(self, research_data: Any, previous_context: Any = None) -> str:
        """Synthesizes research findings into a report."""
        pass

    @abc.abstractmethod
    def generate_infographic(self, text: str) -> Optional[bytes]:
        """Generates an infographic (if supported)."""
        pass

class GeminiClient(LLMClient):
    """Client for Google Gemini Interactions API."""
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def create_plan(self, goal: str) -> Dict[str, Any]:
        try:
            interaction = self.client.interactions.create(
                model="gemini-3-flash-preview",
                input=f"Create a numbered research plan for: {goal}\n\nFormat: 1. [Task] - [Details]\n\nInclude 5-8 specific tasks.",
                tools=[{"type": "google_search"}],
                store=True
            )
            return {
                "id": interaction.id,
                "text": get_text(interaction.outputs),
                "raw": interaction
            }
        except Exception as e:
            st.error(f"Gemini Plan Error: {e}")
            return None

    def execute_research(self, tasks: List[str], previous_context: Any = None) -> Dict[str, Any]:
        plan_id = previous_context if previous_context else None
        task_text = "\n\n".join(tasks)
        try:
            interaction = self.client.interactions.create(
                agent="deep-research-pro-preview-12-2025",
                input=f"Research these tasks thoroughly with sources:\n\n{task_text}",
                previous_interaction_id=plan_id,
                background=True,
                store=True
            )
            # Wait for completion
            interaction = self._wait_for_completion(interaction.id)
            return {
                "id": interaction.id,
                "text": get_text(interaction.outputs) or f"Status: {interaction.status}",
                "raw": interaction
            }
        except Exception as e:
             st.error(f"Gemini Research Error: {e}")
             return None

    def synthesize_report(self, research_data: str, previous_context: Any = None) -> str:
        research_id = previous_context
        try:
            interaction = self.client.interactions.create(
                model="gemini-3-pro-preview",
                input=f"Create executive report with Summary, Findings, Recommendations, Risks:\n\n{research_data}",
                previous_interaction_id=research_id,
                store=True
            )
            return get_text(interaction.outputs)
        except Exception as e:
            st.error(f"Gemini Synthesis Error: {e}")
            return ""

    def generate_infographic(self, text: str) -> Optional[bytes]:
        try:
            response = self.client.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents=f"Create a whiteboard summary infographic for the following: {text}"
            )
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    return part.inline_data.data
        except Exception as e:
            st.warning(f"Infographic Error: {e}")
            return None

    def _wait_for_completion(self, iid: str, timeout: int = 300):
        progress, status, elapsed = st.progress(0), st.empty(), 0
        while elapsed < timeout:
            interaction = self.client.interactions.get(iid)
            if interaction.status != "in_progress": 
                progress.progress(100)
                status.empty()
                return interaction
            elapsed += 3
            progress.progress(min(90, int(elapsed/timeout*100)))
            status.text(f"⏳ {elapsed}s...")
            time.sleep(3)
        return self.client.interactions.get(iid)


class OpenAICompatibleClient(LLMClient):
    """Client for OpenRouter, Ollama, vLLM."""
    def __init__(self, api_key: str, base_url: str, model: str):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.ddgs = DDGS()

    def create_plan(self, goal: str) -> Dict[str, Any]:
        prompt = f"Create a numbered research plan for: {goal}\n\nFormat: 1. [Task] - [Details]\n\nInclude 5-8 specific tasks."
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            text = response.choices[0].message.content
            return {
                "id": None, # No server-side ID
                "text": text,
                "raw": response
            }
        except Exception as e:
            st.error(f"Plan Error: {e}")
            return None

    def execute_research(self, tasks: List[str], previous_context: Any = None) -> Dict[str, Any]:
        # Manual "Deep Research" implementation
        research_results = []
        progress = st.progress(0)
        status = st.empty()
        
        total_tasks = len(tasks)
        for idx, task in enumerate(tasks):
            status.text(f"Searching: {task[:50]}...")
            # 1. Search
            results = self.ddgs.text(task, max_results=3)
            search_context = "\n".join([f"- {r['title']}: {r['body']} ({r['href']})" for r in results])
            
            # 2. Analyze/Summarize with LLM
            prompt = f"Analyze these search results for the task: '{task}'. Extract key facts and details.\n\nResults:\n{search_context}"
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}]
                )
                summary = response.choices[0].message.content
                research_results.append(f"### Research for: {task}\n{summary}\n\nSources:\n{search_context}")
            except Exception as e:
                research_results.append(f"### Research for: {task}\nError: {e}")
            
            progress.progress(int((idx + 1) / total_tasks * 100))
        
        status.empty()
        return {
            "id": None,
            "text": "\n\n".join(research_results),
            "raw": research_results
        }

    def synthesize_report(self, research_data: str, previous_context: Any = None) -> str:
        prompt = f"Create executive report with Sumeexmary, Findings, Recommendations, Risks based on this research:\n\n{research_data}"
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            st.error(f"Synthesis Error: {e}")
            return ""

    def generate_infographic(self, text: str) -> Optional[bytes]:
        # Not supported natively by text-only models
        return None

# Helper from original code
def get_text(outputs): 
    return "\n".join(o.text for o in (outputs or []) if hasattr(o, 'text') and o.text) or ""
