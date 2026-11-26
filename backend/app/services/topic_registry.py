"""
Static mirror of `06 Maps of Content/Learning Progress Dashboard.md`'s
phase -> topic -> note_path structure.

Hand-maintained rather than parsed from the markdown at runtime — the
checkbox-to-note mapping is small and changes only when new vault content is
added, so a generic markdown-checkbox parser would be solving a problem this
file doesn't actually have. Update this alongside any future edit to the
Dashboard file itself.

note_path values match `Note.path` as stored by the indexer (relative to the
vault root, forward slashes, including the `.md` extension).
"""
from typing import List, TypedDict


class Topic(TypedDict):
    phase: str
    label: str
    note_path: str


TOPICS: List[Topic] = [
    # Phase 0 — Programming Foundations
    {"phase": "Phase 0 — Programming Foundations", "label": "Python Fundamentals and Setup",
     "note_path": "02 Literature Notes/Courses/Python Refresher - Lesson 01 Python Fundamentals and Setup.md"},
    {"phase": "Phase 0 — Programming Foundations", "label": "Data Structures, Conditionals and Loops",
     "note_path": "02 Literature Notes/Courses/Python Refresher - Lesson 02 Data Structures Conditionals and Loops.md"},
    {"phase": "Phase 0 — Programming Foundations", "label": "Functions, OOP, File and Error Handling",
     "note_path": "02 Literature Notes/Courses/Python Refresher - Lesson 03 Functions OOP File and Error Handling.md"},
    {"phase": "Phase 0 — Programming Foundations", "label": "Practical Use of AI Code-Gen Tools",
     "note_path": "02 Literature Notes/Courses/Python Refresher - Lesson 04 Practical Use of AI Code Generation Tools.md"},

    # Phase 1 — Software Engineering Foundation
    {"phase": "Phase 1 — Software Engineering Foundation", "label": "Software Engineering Refresh",
     "note_path": "02 Literature Notes/Software Engineering/Software Engineering Refresh.md"},
    {"phase": "Phase 1 — Software Engineering Foundation", "label": "System Design Fundamentals",
     "note_path": "02 Literature Notes/Software Engineering/System Design Fundamentals.md"},
    {"phase": "Phase 1 — Software Engineering Foundation", "label": "Data Structures, Algorithms & Complexity",
     "note_path": "02 Literature Notes/Software Engineering/Data Structures, Algorithms & Complexity.md"},
    {"phase": "Phase 1 — Software Engineering Foundation", "label": "APIs, Integration & Backend Engineering",
     "note_path": "02 Literature Notes/Software Engineering/APIs, Integration & Backend Engineering.md"},
    {"phase": "Phase 1 — Software Engineering Foundation", "label": "Production Delivery Engineering",
     "note_path": "02 Literature Notes/Software Engineering/Production Delivery Engineering.md"},
    {"phase": "Phase 1 — Software Engineering Foundation", "label": "Distributed Systems Reality",
     "note_path": "02 Literature Notes/Software Engineering/Distributed Systems Reality.md"},
    {"phase": "Phase 1 — Software Engineering Foundation", "label": "Applied Data Structures for Backend & AI",
     "note_path": "02 Literature Notes/Software Engineering/Applied Data Structures for Backend and AI.md"},
    {"phase": "Phase 1 — Software Engineering Foundation", "label": "Production API and Backend Patterns",
     "note_path": "02 Literature Notes/Software Engineering/Production API and Backend Patterns.md"},

    # Phase 2 — Applied Data Science Foundations
    {"phase": "Phase 2 — Applied Data Science Foundations", "label": "Introduction to Data Science",
     "note_path": "02 Literature Notes/Courses/Applied Data Science - Lesson 02 Introduction to Data Science.md"},
    {"phase": "Phase 2 — Applied Data Science Foundations", "label": "NumPy",
     "note_path": "02 Literature Notes/Courses/Applied Data Science - Lesson 03 NumPy.md"},
    {"phase": "Phase 2 — Applied Data Science Foundations", "label": "Pandas",
     "note_path": "02 Literature Notes/Courses/Applied Data Science - Lesson 04 Pandas.md"},
    {"phase": "Phase 2 — Applied Data Science Foundations", "label": "Data Visualization",
     "note_path": "02 Literature Notes/Courses/Applied Data Science - Lesson 05 Data Visualization.md"},
    {"phase": "Phase 2 — Applied Data Science Foundations", "label": "Linear Algebra and Statistics Fundamentals",
     "note_path": "02 Literature Notes/Courses/Applied Data Science - Lesson 06 Linear Algebra and Statistics Fundamentals.md"},
    {"phase": "Phase 2 — Applied Data Science Foundations", "label": "Probability Distributions",
     "note_path": "02 Literature Notes/Courses/Applied Data Science - Lesson 07 Probability Distributions.md"},
    {"phase": "Phase 2 — Applied Data Science Foundations", "label": "Advanced Statistics",
     "note_path": "02 Literature Notes/Courses/Applied Data Science - Lesson 08 Advanced Statistics.md"},
    {"phase": "Phase 2 — Applied Data Science Foundations", "label": "Data Wrangling",
     "note_path": "02 Literature Notes/Courses/Applied Data Science - Lesson 09 Data Wrangling.md"},
    {"phase": "Phase 2 — Applied Data Science Foundations", "label": "Feature Engineering",
     "note_path": "02 Literature Notes/Courses/Applied Data Science - Lesson 10 Feature Engineering.md"},

    # Phase 3 — Classical Machine Learning
    {"phase": "Phase 3 — Classical Machine Learning", "label": "Introduction to Machine Learning",
     "note_path": "02 Literature Notes/Courses/Machine Learning - Lesson 02 Introduction to Machine Learning.md"},
    {"phase": "Phase 3 — Classical Machine Learning", "label": "Supervised Learning and Regression",
     "note_path": "02 Literature Notes/Courses/Machine Learning - Lesson 03 Supervised Learning and Regression.md"},
    {"phase": "Phase 3 — Classical Machine Learning", "label": "Classification and Its Applications",
     "note_path": "02 Literature Notes/Courses/Machine Learning - Lesson 04 Classification and Its Applications.md"},
    {"phase": "Phase 3 — Classical Machine Learning", "label": "Ensemble Learning",
     "note_path": "02 Literature Notes/Courses/Machine Learning - Lesson 05 Ensemble Learning.md"},
    {"phase": "Phase 3 — Classical Machine Learning", "label": "Unsupervised Learning",
     "note_path": "02 Literature Notes/Courses/Machine Learning - Lesson 06 Unsupervised Learning.md"},
    {"phase": "Phase 3 — Classical Machine Learning", "label": "Recommendation Systems",
     "note_path": "02 Literature Notes/Courses/Machine Learning - Lesson 07 Recommendation Systems.md"},

    # Phase 4 — Deep Learning
    {"phase": "Phase 4 — Deep Learning", "label": "Introduction to Deep Learning",
     "note_path": "02 Literature Notes/Courses/Deep Learning - Lesson 02 Introduction to Deep Learning.md"},
    {"phase": "Phase 4 — Deep Learning", "label": "Artificial Neural Network",
     "note_path": "02 Literature Notes/Courses/Deep Learning - Lesson 03 Artificial Neural Network.md"},
    {"phase": "Phase 4 — Deep Learning", "label": "Deep Neural Network",
     "note_path": "02 Literature Notes/Courses/Deep Learning - Lesson 04 Deep Neural Network.md"},
    {"phase": "Phase 4 — Deep Learning", "label": "TensorFlow",
     "note_path": "02 Literature Notes/Courses/Deep Learning - Lesson 05 TensorFlow.md"},
    {"phase": "Phase 4 — Deep Learning", "label": "PyTorch",
     "note_path": "02 Literature Notes/Courses/Deep Learning - Lesson 06 PyTorch.md"},
    {"phase": "Phase 4 — Deep Learning", "label": "Model Optimization and Performance Improvement",
     "note_path": "02 Literature Notes/Courses/Deep Learning - Lesson 07 Model Optimization and Performance Improvement.md"},
    {"phase": "Phase 4 — Deep Learning", "label": "Convolutional Neural Networks",
     "note_path": "02 Literature Notes/Courses/Deep Learning - Lesson 08 Convolutional Neural Networks.md"},
    {"phase": "Phase 4 — Deep Learning", "label": "Transfer Learning",
     "note_path": "02 Literature Notes/Courses/Deep Learning - Lesson 09 Transfer Learning.md"},
    {"phase": "Phase 4 — Deep Learning", "label": "Object Detection",
     "note_path": "02 Literature Notes/Courses/Deep Learning - Lesson 10 Object Detection.md"},
    {"phase": "Phase 4 — Deep Learning", "label": "Recurrent Neural Network",
     "note_path": "02 Literature Notes/Courses/Deep Learning - Lesson 11 Recurrent Neural Network.md"},
    {"phase": "Phase 4 — Deep Learning", "label": "Transformer Models for NLP",
     "note_path": "02 Literature Notes/Courses/Deep Learning - Lesson 12 Transformer Models for NLP.md"},
    {"phase": "Phase 4 — Deep Learning", "label": "Getting Started with Autoencoders",
     "note_path": "02 Literature Notes/Courses/Deep Learning - Lesson 13 Getting Started with Autoencoders.md"},

    # Phase 5 — Generative AI
    {"phase": "Phase 5 — Generative AI", "label": "Overview of GenAI and AI Project Implementation",
     "note_path": "02 Literature Notes/Courses/Generative AI - Lesson 01 Overview of GenAI and AI Project Implementation.md"},
    {"phase": "Phase 5 — Generative AI", "label": "Working with GPTs",
     "note_path": "02 Literature Notes/Courses/Generative AI - Lesson 02 Working with GPTs.md"},

    # Phase 6 — LLM Engineering
    {"phase": "Phase 6 — LLM Engineering", "label": "Tokenization",
     "note_path": "02 Literature Notes/LLM Engineering/Tokenization.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Embeddings",
     "note_path": "02 Literature Notes/LLM Engineering/Embeddings.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Embedding Model Selection",
     "note_path": "02 Literature Notes/LLM Engineering/Embedding Model Selection.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Vector Search",
     "note_path": "02 Literature Notes/LLM Engineering/Vector Search.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "ANN Index Internals",
     "note_path": "02 Literature Notes/LLM Engineering/ANN Index Internals.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Chunking Strategies",
     "note_path": "02 Literature Notes/LLM Engineering/Chunking Strategies.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Attention Deep-Dive",
     "note_path": "02 Literature Notes/LLM Engineering/Attention Deep-Dive.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Transformer Architecture",
     "note_path": "02 Literature Notes/LLM Engineering/Transformer Architecture.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Decoding and Sampling",
     "note_path": "02 Literature Notes/LLM Engineering/Decoding and Sampling.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Structured Generation",
     "note_path": "02 Literature Notes/LLM Engineering/Structured Generation.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "LLM Efficiency",
     "note_path": "02 Literature Notes/LLM Engineering/LLM Efficiency.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Reasoning Models",
     "note_path": "02 Literature Notes/LLM Engineering/Reasoning Models.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Prompt Contracts",
     "note_path": "02 Literature Notes/LLM Engineering/Prompt Contracts.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Prompt Versioning",
     "note_path": "02 Literature Notes/LLM Engineering/Prompt Versioning.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Reasoning Prompt Patterns",
     "note_path": "02 Literature Notes/LLM Engineering/Reasoning Prompt Patterns.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Context Engineering",
     "note_path": "02 Literature Notes/LLM Engineering/Context Engineering.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "RAG Pipeline Fundamentals",
     "note_path": "02 Literature Notes/LLM Engineering/RAG Pipeline Fundamentals.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Advanced Retrieval",
     "note_path": "02 Literature Notes/LLM Engineering/Advanced Retrieval.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Query Transformation",
     "note_path": "02 Literature Notes/LLM Engineering/Query Transformation.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "GraphRAG",
     "note_path": "02 Literature Notes/LLM Engineering/GraphRAG.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Agentic RAG",
     "note_path": "02 Literature Notes/LLM Engineering/Agentic RAG.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Retrieval Evaluation",
     "note_path": "02 Literature Notes/LLM Engineering/Retrieval Evaluation.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Vector Database Landscape",
     "note_path": "02 Literature Notes/LLM Engineering/Vector Database Landscape.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Tool and Function Calling",
     "note_path": "02 Literature Notes/LLM Engineering/Tool and Function Calling.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Agent Loops and Planning",
     "note_path": "02 Literature Notes/LLM Engineering/Agent Loops and Planning.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Agent Memory",
     "note_path": "02 Literature Notes/LLM Engineering/Agent Memory.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Multi-Agent Orchestration",
     "note_path": "02 Literature Notes/LLM Engineering/Multi-Agent Orchestration.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Agentic Workflow Patterns",
     "note_path": "02 Literature Notes/LLM Engineering/Agentic Workflow Patterns.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Model Context Protocol",
     "note_path": "02 Literature Notes/LLM Engineering/Model Context Protocol.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Agent Framework Literacy",
     "note_path": "02 Literature Notes/LLM Engineering/Agent Framework Literacy.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Agent Reliability and Cost",
     "note_path": "02 Literature Notes/LLM Engineering/Agent Reliability and Cost.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Eval Fundamentals",
     "note_path": "02 Literature Notes/LLM Engineering/Eval Fundamentals.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Groundedness and Faithfulness",
     "note_path": "02 Literature Notes/LLM Engineering/Groundedness and Faithfulness.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "LLM as a Judge",
     "note_path": "02 Literature Notes/LLM Engineering/LLM as a Judge.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Online Evaluation",
     "note_path": "02 Literature Notes/LLM Engineering/Online Evaluation.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Red-Teaming and Adversarial Eval",
     "note_path": "02 Literature Notes/LLM Engineering/Red-Teaming and Adversarial Eval.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Statistical Rigor in Eval",
     "note_path": "02 Literature Notes/LLM Engineering/Statistical Rigor in Eval.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Eval Framework Literacy",
     "note_path": "02 Literature Notes/LLM Engineering/Eval Framework Literacy.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Benchmark Literacy",
     "note_path": "02 Literature Notes/LLM Engineering/Benchmark Literacy.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Supervised Fine-Tuning",
     "note_path": "02 Literature Notes/LLM Engineering/Supervised Fine-Tuning.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "LoRA QLoRA PEFT",
     "note_path": "02 Literature Notes/LLM Engineering/LoRA QLoRA PEFT.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Preference Optimization",
     "note_path": "02 Literature Notes/LLM Engineering/Preference Optimization.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Distillation and Small Models",
     "note_path": "02 Literature Notes/LLM Engineering/Distillation and Small Models.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Embedding Model Fine-Tuning",
     "note_path": "02 Literature Notes/LLM Engineering/Embedding Model Fine-Tuning.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Synthetic Data Generation",
     "note_path": "02 Literature Notes/LLM Engineering/Synthetic Data Generation.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Observability and Monitoring",
     "note_path": "02 Literature Notes/LLM Engineering/Observability and Monitoring.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Inference and Serving",
     "note_path": "02 Literature Notes/LLM Engineering/Inference and Serving.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Cost Architecture",
     "note_path": "02 Literature Notes/LLM Engineering/Cost Architecture.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Reliability Patterns",
     "note_path": "02 Literature Notes/LLM Engineering/Reliability Patterns.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "AI Security and Governance",
     "note_path": "02 Literature Notes/LLM Engineering/AI Security and Governance.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Guardrails and Prompt Injection",
     "note_path": "02 Literature Notes/LLM Engineering/Guardrails and Prompt Injection.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Document Ingestion and Parsing",
     "note_path": "02 Literature Notes/LLM Engineering/Document Ingestion and Parsing.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Multimodal AI",
     "note_path": "02 Literature Notes/LLM Engineering/Multimodal AI.md"},
    {"phase": "Phase 6 — LLM Engineering", "label": "Framework Ecosystem Literacy",
     "note_path": "02 Literature Notes/LLM Engineering/Framework Ecosystem Literacy.md"},

    # Phase 7 — AI Architecture
    {"phase": "Phase 7 — AI Architecture", "label": "AI Solution Architecture: Reference Patterns",
     "note_path": "02 Literature Notes/AI Architecture/AI Solution Architecture — Reference Patterns.md"},
    {"phase": "Phase 7 — AI Architecture", "label": "AI Solution Architecture: Applied",
     "note_path": "02 Literature Notes/AI Architecture/AI Solution Architecture — Applied.md"},
    {"phase": "Phase 7 — AI Architecture", "label": "Cloud Architecture & Deployment: Reference Patterns",
     "note_path": "02 Literature Notes/AI Architecture/Cloud Architecture & Deployment — Reference Patterns.md"},
    {"phase": "Phase 7 — AI Architecture", "label": "Cloud Architecture & Deployment: Applied",
     "note_path": "02 Literature Notes/AI Architecture/Cloud Architecture & Deployment — Applied.md"},
    {"phase": "Phase 7 — AI Architecture", "label": "Security, Governance & Responsible AI: Reference Patterns",
     "note_path": "02 Literature Notes/AI Architecture/Security, Governance & Responsible AI — Reference Patterns.md"},
    {"phase": "Phase 7 — AI Architecture", "label": "Security, Governance & Responsible AI: Applied",
     "note_path": "02 Literature Notes/AI Architecture/Security, Governance & Responsible AI — Applied.md"},
    {"phase": "Phase 7 — AI Architecture", "label": "LLMOps, Monitoring, Cost & Reliability: Reference Patterns",
     "note_path": "02 Literature Notes/AI Architecture/LLMOps, Monitoring, Cost & Reliability — Reference Patterns.md"},
    {"phase": "Phase 7 — AI Architecture", "label": "LLMOps, Monitoring, Cost & Reliability: Applied",
     "note_path": "02 Literature Notes/AI Architecture/LLMOps, Monitoring, Cost & Reliability — Applied.md"},

    # Phase 8 — FDE Delivery
    {"phase": "Phase 8 — FDE Delivery", "label": "Customer Discovery & Stakeholder Communication: Reference Patterns",
     "note_path": "02 Literature Notes/FDE Delivery/Customer Discovery & Stakeholder Communication — Reference Patterns.md"},
    {"phase": "Phase 8 — FDE Delivery", "label": "Customer Discovery & Stakeholder Communication: Applied",
     "note_path": "02 Literature Notes/FDE Delivery/Customer Discovery & Stakeholder Communication — Applied.md"},
    {"phase": "Phase 8 — FDE Delivery", "label": "Capstone FDE Portfolio Project: Reference Patterns",
     "note_path": "02 Literature Notes/FDE Delivery/Capstone FDE Portfolio Project — Reference Patterns.md"},
    {"phase": "Phase 8 — FDE Delivery", "label": "Capstone FDE Portfolio Project: Applied",
     "note_path": "02 Literature Notes/FDE Delivery/Capstone FDE Portfolio Project — Applied.md"},
]


def find_by_note_path(note_path: str) -> Topic | None:
    return next((t for t in TOPICS if t["note_path"] == note_path), None)


def find_by_label_fragment(text: str) -> Topic | None:
    """Fuzzy-match a topic by checking whether its label appears in free text
    (case-insensitive substring match) — used to resolve a topic name
    mentioned in a chat message to a note_path. Longest label wins on
    multiple matches, so more specific topic names aren't shadowed by a
    shorter topic name that happens to be a substring of a longer one."""
    lowered = text.lower()
    matches = [t for t in TOPICS if t["label"].lower() in lowered]
    if not matches:
        return None
    return max(matches, key=lambda t: len(t["label"]))
