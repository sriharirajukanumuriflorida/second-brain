# Synthetic Evaluation Data Must Stay Out of Training

If generated eval cases or their answers leak into training, the eval stops measuring generalization. Synthetic pipelines need split hygiene, similarity checks, and provenance metadata so training data cannot contaminate held-out tests.


Related: [[02 Literature Notes/LLM Engineering/Synthetic Data Generation]]
