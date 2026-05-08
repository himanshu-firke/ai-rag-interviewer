"""
Answer evaluation service.
- Standard questions: correctness, depth, clarity
- Coding questions: correctness, optimization, complexity, plagiarism
- Session report generation
"""

import json
from pydantic import BaseModel
from backend.services.llm_client import get_json_response
from backend.src import rag_logger


class AnswerEvaluation(BaseModel):
    correctness_score: float = 0.0
    depth_score: float = 0.0
    clarity_score: float = 0.0
    overall_score: float = 0.0
    feedback: str = ""
    key_points_covered: list[str] = []
    key_points_missed: list[str] = []
    # Coding-specific scores
    optimization_score: float = 0.0
    complexity_score: float = 0.0
    plagiarism_score: float = 0.0  # 0 = original, 10 = likely copied


def evaluate_answer(
    question: str, answer: str, context: str, role: str,
    difficulty: str = "medium", question_type: str = "conceptual",
) -> AnswerEvaluation:
    """Evaluate a candidate's answer. Uses different criteria for coding vs standard."""
    if not answer or not answer.strip():
        return AnswerEvaluation(feedback="No answer was provided.")

    rag_logger.log_answer_received(answer)

    if question_type == "coding":
        return _evaluate_code(question, answer, context, role, difficulty)
    else:
        return _evaluate_standard(question, answer, context, role, difficulty)


def _evaluate_standard(question, answer, context, role, difficulty):
    """Evaluate conceptual/applied/scenario/debugging answers."""
    prompt = f"""You are an expert technical interviewer evaluating a candidate's answer for {role}.

QUESTION: {question}
DIFFICULTY: {difficulty}

REFERENCE CONTEXT (from knowledge base):
{context[:3000]}

CANDIDATE'S ANSWER:
{answer}

Evaluate on (score 1-10 each):
1. Correctness: Is the answer factually correct?
2. Depth: Does it show deep understanding?
3. Clarity: Is it well-structured and clear?

Return JSON: {{"correctness_score": N, "depth_score": N, "clarity_score": N, "feedback": "2-4 sentences", "key_points_covered": [...], "key_points_missed": [...]}}
ONLY JSON."""

    try:
        data = get_json_response(prompt)
        correctness = float(data.get("correctness_score", 5.0))
        depth = float(data.get("depth_score", 5.0))
        clarity = float(data.get("clarity_score", 5.0))
        result = AnswerEvaluation(
            correctness_score=correctness, depth_score=depth, clarity_score=clarity,
            overall_score=round((correctness + depth + clarity) / 3, 1),
            feedback=data.get("feedback", "Answer evaluated."),
            key_points_covered=data.get("key_points_covered", []),
            key_points_missed=data.get("key_points_missed", []),
        )
        rag_logger.log_evaluation(
            result.correctness_score, result.depth_score,
            result.clarity_score, result.overall_score, result.feedback,
        )
        return result
    except Exception as e:
        print(f"[WARN] Standard evaluation failed: {e}")
        return _fallback_eval(answer)


def _evaluate_code(question, answer, context, role, difficulty):
    """Evaluate coding answers on correctness, optimization, complexity, plagiarism."""
    prompt = f"""You are a senior code reviewer evaluating a candidate's code for {role}.

PROBLEM: {question}
DIFFICULTY: {difficulty}

REFERENCE CONTEXT:
{context[:2000]}

CANDIDATE'S CODE:
```
{answer}
```

Evaluate the code on these criteria (score 1-10 each):

1. **correctness_score**: Does the code correctly solve the problem? Does it handle edge cases?
   - 1-3: Doesn't work / major bugs
   - 4-6: Partially works, missing edge cases
   - 7-9: Works correctly with good edge case handling
   - 10: Perfect solution

2. **optimization_score**: Is the solution efficient? Time and space complexity?
   - 1-3: Brute force, very inefficient
   - 4-6: Acceptable but could be better
   - 7-9: Efficient, good algorithm choice
   - 10: Optimal solution

3. **complexity_score**: Code quality — readability, structure, naming, comments?
   - 1-3: Messy, hard to read
   - 4-6: Acceptable structure
   - 7-9: Clean, well-organized
   - 10: Production-quality code

4. **plagiarism_score**: Does this look like original thinking or copied from a template?
   - 1-3: Clearly original work with personal style
   - 4-6: Some common patterns but shows understanding
   - 7-10: Looks heavily copied/memorized, no original thinking

Return JSON:
{{
  "correctness_score": N,
  "optimization_score": N,
  "complexity_score": N,
  "plagiarism_score": N,
  "feedback": "3-5 sentences about the code quality, what works, what could be improved",
  "key_points_covered": ["list of things done well"],
  "key_points_missed": ["list of improvements needed"]
}}
ONLY JSON, no markdown."""

    try:
        data = get_json_response(prompt)
        correctness = float(data.get("correctness_score", 5.0))
        optimization = float(data.get("optimization_score", 5.0))
        complexity = float(data.get("complexity_score", 5.0))
        plagiarism = float(data.get("plagiarism_score", 3.0))

        # Overall: weighted average (plagiarism is inverse — lower is better)
        originality = max(0, 10 - plagiarism)  # Convert to positive scale
        overall = round(
            (correctness * 0.35 + optimization * 0.25 + complexity * 0.20 + originality * 0.20),
            1,
        )

        result = AnswerEvaluation(
            correctness_score=correctness,
            depth_score=complexity,  # Map complexity to depth for consistency
            clarity_score=optimization,  # Map optimization to clarity slot
            overall_score=overall,
            optimization_score=optimization,
            complexity_score=complexity,
            plagiarism_score=plagiarism,
            feedback=data.get("feedback", "Code evaluated."),
            key_points_covered=data.get("key_points_covered", []),
            key_points_missed=data.get("key_points_missed", []),
        )

        # Log code evaluation with all 4 metrics
        rag_logger.log_evaluation(
            correctness, complexity, optimization, overall,
            f"[CODE] Plagiarism Risk: {plagiarism}/10 | {result.feedback}",
        )
        return result
    except Exception as e:
        print(f"[WARN] Code evaluation failed: {e}")
        return _fallback_eval(answer)


def _fallback_eval(answer):
    """Fallback evaluation when AI is unavailable."""
    word_count = len(answer.split())
    base = min(7.0, max(3.0, word_count / 20))
    return AnswerEvaluation(
        correctness_score=base, depth_score=base - 1, clarity_score=base,
        overall_score=round(base - 0.3, 1),
        feedback="Automated evaluation was temporarily unavailable.",
    )


def generate_session_report(role: str, candidate_name: str, qa_pairs: list[dict]) -> dict:
    """Generate a comprehensive session report."""
    qa_summary = ""
    total_score = 0
    for i, qa in enumerate(qa_pairs):
        score = qa.get("score", 0)
        total_score += score
        qa_summary += f"\nQ{i+1} [{qa.get('topic', 'General')}] (Score: {score}/10):\n  Q: {qa.get('question', '')}\n  A: {qa.get('answer', 'Not answered')[:200]}\n"

    avg_score = round(total_score / max(len(qa_pairs), 1), 1)

    prompt = f"""You are a senior hiring manager reviewing an interview for {role}.
Candidate: {candidate_name}

INTERVIEW TRANSCRIPT:
{qa_summary}

AVERAGE SCORE: {avg_score}/10

Generate a hiring report. Return JSON:
{{
  "overall_score": {avg_score},
  "strengths": ["3-5 strengths"],
  "weaknesses": ["3-5 areas for improvement"],
  "summary": "3-5 sentence assessment",
  "recommendation": "strong_hire|hire|maybe|no_hire",
  "detailed_analysis": "paragraph analysis"
}}
Thresholds: strong_hire>=8, hire>=6.5, maybe>=4.5, no_hire<4.5
ONLY JSON."""

    try:
        data = get_json_response(prompt)
        data["overall_score"] = avg_score
        return data
    except Exception as e:
        print(f"[WARN] Report generation failed: {e}")
        rec = "strong_hire" if avg_score >= 8 else "hire" if avg_score >= 6.5 else "maybe" if avg_score >= 4.5 else "no_hire"
        return {
            "overall_score": avg_score,
            "strengths": ["Completed the interview"],
            "weaknesses": ["Detailed analysis unavailable"],
            "summary": f"Candidate scored {avg_score}/10 across {len(qa_pairs)} questions.",
            "recommendation": rec,
            "detailed_analysis": "Automated analysis was temporarily unavailable.",
        }
