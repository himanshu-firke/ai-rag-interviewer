"""
Question generation service.
Supports question formats:
- conceptual: theory/definition questions
- applied: real-world application
- scenario: system design scenarios
- debugging: bug finding/fixing
- coding: write/analyze code (role-based, RAG-driven)
"""

from pydantic import BaseModel
from backend.services.llm_client import get_json_response
from backend.src import rag_logger


class GeneratedQuestion(BaseModel):
    question_text: str
    topic: str = ""
    question_type: str = "conceptual"
    difficulty: str = "medium"
    context_used: str = ""
    code_template: str = ""
    expected_language: str = ""
    options: list[str] = []
    correct_option: int = -1


def determine_difficulty(question_index: int, total_questions: int, previous_avg_score: float = None) -> str:
    if previous_avg_score is not None:
        if previous_avg_score >= 8.0: return "hard"
        elif previous_avg_score >= 5.0: return "medium"
        else: return "easy"
    progress = question_index / max(total_questions, 1)
    if progress < 0.3: return "easy"
    elif progress < 0.7: return "medium"
    else: return "hard"


def determine_question_type(question_index: int, total_questions: int) -> str:
    """Rotate through question types — coding appears twice."""
    types = [
        "conceptual",   # Q1: warm-up theory
        "coding",       # Q2: write code
        "applied",      # Q3: real-world application
        "scenario",     # Q4: system design
        "coding",       # Q5: algorithm/optimization
        "debugging",    # Q6: find & fix bugs
        "coding",       # Q7: advanced coding challenge
    ]
    return types[question_index % len(types)]


# Role-specific coding focus areas
ROLE_CODING_FOCUS = {
    "AI/ML Engineer": {
        "languages": ["python"],
        "topics": [
            "implement a machine learning algorithm from scratch",
            "data preprocessing and feature engineering pipeline",
            "neural network forward pass implementation",
            "loss function and gradient computation",
            "model evaluation metrics implementation",
            "data augmentation or sampling technique",
        ],
    },
    "Backend Engineer": {
        "languages": ["python", "javascript"],
        "topics": [
            "design a REST API endpoint handler",
            "implement a caching mechanism",
            "database query optimization",
            "rate limiter implementation",
            "async task queue processor",
            "authentication middleware",
        ],
    },
    "Data Scientist": {
        "languages": ["python"],
        "topics": [
            "statistical hypothesis test implementation",
            "data cleaning and transformation pipeline",
            "feature selection algorithm",
            "cross-validation implementation",
            "data visualization function",
            "outlier detection algorithm",
        ],
    },
    "Full Stack Engineer": {
        "languages": ["javascript", "python"],
        "topics": [
            "implement a REST API with CRUD operations",
            "build a React component with state management",
            "design a database schema and write queries",
            "implement user authentication middleware",
            "create a responsive UI component",
            "build a full-stack feature with frontend and backend",
        ],
    },
}


def generate_question(
    context: str, role: str, skills: list[str], technologies: list[str],
    experience_level: str, question_index: int, total_questions: int,
    previous_qa: list[dict] = None, previous_avg_score: float = None,
) -> GeneratedQuestion:
    difficulty = determine_difficulty(question_index, total_questions, previous_avg_score)
    q_type = determine_question_type(question_index, total_questions)

    prev_context = ""
    covered_topics = []
    if previous_qa:
        parts = []
        for qa in previous_qa[-3:]:
            parts.append(f"Q: {qa.get('question', '')}\nA: {qa.get('answer', 'Not answered')}")
            if qa.get("topic"): covered_topics.append(qa["topic"])
        prev_context = "\n\n".join(parts)

    if q_type == "coding":
        return _generate_coding_question(
            context, role, skills, technologies, experience_level,
            difficulty, question_index, total_questions, covered_topics, prev_context,
        )

    # Non-coding question
    format_instructions = _get_format_instructions(q_type, skills, technologies, role)

    prompt = f"""You are an expert technical interviewer for the role of {role}.
Generate ONE interview question based on the following context.

CANDIDATE PROFILE:
- Skills: {', '.join(skills[:10])}
- Technologies: {', '.join(technologies[:8])}
- Experience Level: {experience_level}

KNOWLEDGE BASE CONTEXT:
{context[:4000]}

QUESTION REQUIREMENTS:
- Type: {q_type}
- Difficulty: {difficulty}
- Question number: {question_index + 1} of {total_questions}
- Must NOT repeat topics: {', '.join(covered_topics) if covered_topics else 'None'}

{format_instructions}

{"PREVIOUS CONTEXT:" + chr(10) + prev_context if prev_context else "First question."}

DIFFICULTY: easy=basic definitions, medium=application/reasoning, hard=edge cases/system design

Return JSON: {{"question_text": "...", "topic": "2-5 words", "question_type": "{q_type}", "difficulty": "{difficulty}"}}
ONLY JSON, no markdown."""

    try:
        data = get_json_response(prompt)
        q = GeneratedQuestion(
            question_text=data.get("question_text", "Could not generate question"),
            topic=data.get("topic", "General"),
            question_type=q_type, difficulty=difficulty,
            context_used=context[:2000],
        )
        rag_logger.log_question_generated(
            question_index + 1, total_questions, q.question_text,
            q.topic, q.question_type, q.difficulty,
        )
        return q
    except Exception as e:
        print(f"[WARN] Question generation failed: {e}")
        return _fallback_question(q_type, difficulty, skills, technologies, role)


def _generate_coding_question(
    context, role, skills, technologies, experience_level,
    difficulty, question_index, total_questions, covered_topics, prev_context,
):
    """Generate a coding question with starter code, role-based and RAG-driven."""
    role_config = ROLE_CODING_FOCUS.get(role, ROLE_CODING_FOCUS["AI/ML Engineer"])
    lang = role_config["languages"][0]

    prompt = f"""You are an expert coding interviewer for {role}.
Generate a CODING question that the candidate must solve by writing code.

CANDIDATE: Skills={', '.join(skills[:8])}, Technologies={', '.join(technologies[:6])}, Level={experience_level}

KNOWLEDGE BASE (use this to create relevant problems):
{context[:3000]}

REQUIREMENTS:
- Language: {lang}
- Difficulty: {difficulty}
- Must be relevant to {role} role
- Must NOT repeat topics: {', '.join(covered_topics) if covered_topics else 'None'}
- The problem should test real coding ability, not just theory

DIFFICULTY GUIDELINES:
- easy: Simple function (e.g., data transformation, basic algorithm)
- medium: Multi-step problem (e.g., implement a pipeline, optimize a solution)
- hard: Complex algorithm with edge cases, optimization requirements

{"PREVIOUS CONTEXT:" + chr(10) + prev_context if prev_context else ""}

Return JSON with:
- "question_text": Clear problem statement. Include input/output examples.
- "topic": Main topic (2-5 words)
- "question_type": "coding"
- "difficulty": "{difficulty}"
- "code_template": Starter code with function signature and comments. Use \\n for newlines.
- "expected_language": "{lang}"

IMPORTANT: The code_template must have a clear function signature with # Your code here comments.
Return ONLY JSON, no markdown."""

    try:
        data = get_json_response(prompt)
        template = data.get("code_template", "").replace("\\n", "\n")
        if not template.strip():
            template = f"def solution():\n    # Your code here\n    pass"

        q = GeneratedQuestion(
            question_text=data.get("question_text", "Write a solution"),
            topic=data.get("topic", "Coding"),
            question_type="coding", difficulty=difficulty,
            context_used=context[:2000],
            code_template=template,
            expected_language=data.get("expected_language", lang),
        )
        rag_logger.log_question_generated(
            question_index + 1, total_questions, q.question_text,
            q.topic, q.question_type, q.difficulty,
        )
        return q
    except Exception as e:
        print(f"[WARN] Coding question generation failed: {e}")
        return GeneratedQuestion(
            question_text=f"Write a {lang} function that processes a dataset: filter rows where a numeric column exceeds a threshold, then compute the mean of the remaining values. Handle edge cases (empty input, missing values).",
            topic="Data Processing",
            question_type="coding", difficulty=difficulty,
            code_template=f"def process_data(data, column, threshold):\n    \"\"\"\n    Filter rows where column > threshold, return mean.\n    Handle edge cases.\n    \"\"\"\n    # Your code here\n    pass",
            expected_language=lang,
            context_used="Fallback",
        )


def _get_format_instructions(q_type, skills, techs, role):
    tech = techs[0] if techs else "Python"
    skill = skills[0] if skills else "programming"
    return {
        "conceptual": f"Ask a clear theoretical question about {skill} relevant to {role}.",
        "applied": f"Ask about a real-world application scenario using {tech}.",
        "scenario": f"Present a system design scenario relevant to {role}. Include trade-offs.",
        "debugging": f"Present buggy code or a system with a defect. Ask the candidate to identify and fix it. Include the code in question_text.",
    }.get(q_type, f"Ask a technical question about {skill}.")


def _fallback_question(q_type, difficulty, skills, technologies, role):
    tech = technologies[0] if technologies else "Python"
    skill = skills[0] if skills else "machine learning"
    fallbacks = {
        "conceptual": GeneratedQuestion(
            question_text=f"Explain the key concepts behind {skill} and how they apply to {role}.",
            topic=skill, question_type="conceptual", difficulty=difficulty,
        ),
        "applied": GeneratedQuestion(
            question_text=f"Describe a project where you used {tech} to solve a real-world problem.",
            topic=tech, question_type="applied", difficulty=difficulty,
        ),
        "scenario": GeneratedQuestion(
            question_text=f"Design a scalable {role.lower()} system. Walk through your architecture and trade-offs.",
            topic="System Design", question_type="scenario", difficulty=difficulty,
        ),
        "debugging": GeneratedQuestion(
            question_text=f"A {tech} application is producing incorrect results intermittently. How would you diagnose it?",
            topic="Debugging", question_type="debugging", difficulty=difficulty,
        ),
    }
    return fallbacks.get(q_type, fallbacks["conceptual"])
