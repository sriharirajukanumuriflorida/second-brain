# AI/ML Topics Covered — Chronological Learning Map

> A single chronological index of every AI/ML topic in this vault, ordered the way they should be learned: programming foundations → data science → classical ML → deep learning → generative AI → LLM engineering → production AI architecture. Each entry gives a plain explanation and, where useful, a concrete "why it matters" scenario.
>
> Source maps this consolidates: [[AIML Courses]] · [[Machine Learning Concepts]] · [[Deep Learning Concepts]] · [[Generative AI Concepts]] · [[LLM Engineering Concepts]] · [[AI Architecture Concepts]] · [[Applied Data Science Concepts]] · [[ML Snippets]]

---

## Stage 0 — Programming Foundations (Python Refresher)

### Python Fundamentals and Setup
Getting a working Python environment, syntax, variables, data types, and I/O in place before anything data-related is attempted. Nothing downstream — NumPy, Pandas, TensorFlow — works without this baseline.
Source: [[02 Literature Notes/Courses/Python Refresher - Lesson 01 Python Fundamentals and Setup]]

### Data Structures, Conditionals, and Loops
Lists, tuples, dicts, and sets are the containers almost every data pipeline is built from; `if/elif/else` and `for`/`while` loops (plus comprehensions) are the control-flow vocabulary used to filter, transform, and iterate over them. A dict is the right choice when you need fast lookup by key (e.g. mapping a user ID to their last order); a list is right when order matters (a sequence of transactions).
Source: [[02 Literature Notes/Courses/Python Refresher - Lesson 02 Data Structures Conditionals and Loops]]

### Functions, OOP, File and Error Handling
Functions and classes make code reusable instead of copy-pasted; file I/O and `try/except` make it survive real-world messiness (a missing file, a malformed row) instead of crashing. Any real data pipeline needs both — a one-off notebook cell does not.
Source: [[02 Literature Notes/Courses/Python Refresher - Lesson 03 Functions OOP File and Error Handling]]

### Practical Use of AI Code Generation Tools
Using AI coding assistants to draft, explain, and debug code faster — but always reviewing and testing the output rather than trusting it blindly. This is the bridge from "learning Python" into the AI-assisted and AI-building workflows the rest of the vault covers.
Source: [[02 Literature Notes/Courses/Python Refresher - Lesson 04 Practical Use of AI Code Generation Tools]]

---

## Stage 1 — Applied Data Science Foundations

### The Data Science Lifecycle
Every data science project moves through the same loop: collect → clean → explore → model → communicate. Framing a problem this way stops you from jumping straight to modeling before the data is even trustworthy.
Source: [[02 Literature Notes/Courses/Applied Data Science - Lesson 02 Introduction to Data Science]]

### NumPy (Arrays and Vectorized Computing)
NumPy's `ndarray` lets you apply one operation to an entire array at once (vectorization) instead of writing a Python loop over every element — this is dramatically faster and is the numerical foundation everything else (Pandas, scikit-learn, TensorFlow) is built on. Indexing and slicing let you pull out exactly the rows/columns/elements you need without copying the whole array.
Source: [[02 Literature Notes/Courses/Applied Data Science - Lesson 03 NumPy]]

### Pandas (DataFrames and Tabular Data)
Series and DataFrames give you labeled, spreadsheet-like tabular data with fast filtering, grouping, and aggregation — e.g. "average order value per customer, per month" is a one-line `groupby` instead of hand-rolled loops. Pandas also has dedicated support for dates/timedeltas and text columns, which show up in almost every real dataset.
Source: [[02 Literature Notes/Courses/Applied Data Science - Lesson 04 Pandas]]

### Data Visualization
A chart answers a question a table of numbers can't make obvious at a glance — e.g. a histogram instantly shows you a skewed distribution that a mean/median table would hide. Matplotlib covers the fundamentals, Seaborn adds statistical plotting (distributions, correlations), and Plotly adds interactivity for exploration and stakeholder-facing dashboards.
Source: [[02 Literature Notes/Courses/Applied Data Science - Lesson 05 Data Visualization]]

### Linear Algebra and Statistics Fundamentals
Vectors and matrices are the data structures every ML model actually computes with under the hood; descriptive statistics (mean, variance, correlation) are how you summarize a dataset before you model it. You can't reason about "why did this model do that" without this foundation.
Source: [[02 Literature Notes/Courses/Applied Data Science - Lesson 06 Linear Algebra and Statistics Fundamentals]]

### Probability Distributions
Distributions (normal, binomial, Poisson, etc.) are the mathematical shapes that model uncertainty in data — e.g. assuming customer arrivals follow a Poisson distribution lets you estimate the probability of an unusually busy hour. They underpin both statistical inference and many ML model assumptions.
Source: [[02 Literature Notes/Courses/Applied Data Science - Lesson 07 Probability Distributions]]

### Advanced Statistics (Hypothesis Testing, p-values)
Inferential statistics lets you draw conclusions about a whole population from a sample, with a measure of confidence. A p-value tells you how surprising your result would be if there were truly no effect — e.g. "is this A/B test winner real, or could it just be noise?" Misreading or cherry-picking p-values is one of the most common ways data analysis goes wrong.
Source: [[02 Literature Notes/Courses/Applied Data Science - Lesson 08 Advanced Statistics]]

### Data Wrangling
Real data is messy: missing values, duplicates, inconsistent formats, and data spread across multiple tables that need merging/joining/reshaping. This is usually the single most time-consuming part of a real project, and a model trained on unwrangled data inherits all of its problems.
Source: [[02 Literature Notes/Courses/Applied Data Science - Lesson 09 Data Wrangling]]

### Feature Engineering
Turning raw columns into the inputs a model can actually learn from well: encoding categorical variables (e.g. "city" → one-hot columns), scaling numeric features so one large-magnitude column doesn't dominate, and creating new derived features (e.g. "days since last purchase" from a timestamp). Feature quality is often a bigger lever on model performance than the choice of algorithm — this lesson is the direct bridge into the Machine Learning course.
Source: [[02 Literature Notes/Courses/Applied Data Science - Lesson 10 Feature Engineering]]

---

## Stage 2 — Classical Machine Learning

### Introduction to Machine Learning
The core ML vocabulary: features, labels, training/test split, generalization, overfitting — and the three paradigms (supervised, unsupervised, reinforcement). Supervised learning uses labeled examples to learn an input→output mapping; unsupervised learning finds structure in data that has no labels at all.
Source: [[02 Literature Notes/Courses/Machine Learning - Lesson 02 Introduction to Machine Learning]]

### Supervised Learning and Regression
Regression predicts a continuous number (price, temperature, demand) from input features, evaluated with error metrics like MSE, RMSE, and R-squared. It's the entry point into predictive modeling because the evaluation story is simple — "how far off was the prediction, on average?" — before classification adds the complication of discrete categories.
Source: [[02 Literature Notes/Courses/Machine Learning - Lesson 03 Supervised Learning and Regression]]

### Classification and Its Applications
Classification predicts a discrete label — binary (fraud / not fraud) or multiclass (which of 5 product categories) — using algorithms like logistic regression, decision trees, k-NN, SVM, and Naive Bayes. Evaluation uses accuracy, precision, recall, F1, and confusion matrices, and which metric to optimize depends heavily on class balance and the real-world cost of different error types (see SMOTE / Class Imbalance below).
Source: [[02 Literature Notes/Courses/Machine Learning - Lesson 04 Classification and Its Applications]]

### Class Imbalance and SMOTE
SMOTE helps a classification model learn from a class that doesn't have enough training examples by creating new synthetic examples of that minority class.

Why do we need SMOTE? Imagine you're building a fraud-detection model with:
- 100,000 transactions
- 99,000 → Normal
- 1,000 → Fraud

That's a 99:1 class imbalance. A naive model could predict "everything = Normal" and achieve 99% accuracy — but it detected 0% of fraud. That's why accuracy can be misleading with imbalanced datasets.

This is where techniques such as these become important:
- Random oversampling
- Random undersampling
- SMOTE
- Borderline-SMOTE
- ADASYN
- SMOTE-Tomek
- SMOTE-ENN
- Class weighting

SMOTE specifically works by picking a minority-class point, finding its nearest minority-class neighbors, and generating new synthetic points along the line segments between them — rather than just duplicating existing rows (which is what random oversampling does, and which risks overfitting to the exact same examples).
Source: drawn from [[02 Literature Notes/Courses/Machine Learning - Lesson 04 Classification and Its Applications]] and [[02 Literature Notes/Courses/Machine Learning - Lesson 05 Ensemble Learning]] (no dedicated vault note yet).

### Ensemble Learning (Bagging vs Boosting)
Combining many "weak" models into one stronger model almost always beats a single model on structured/tabular data. Bagging (e.g. Random Forest) trains many models in parallel on random subsets of data and averages them to reduce variance — it's why a forest of noisy, overfit trees can average out to a stable prediction. Boosting (AdaBoost, Gradient Boosting, XGBoost) instead trains models sequentially, where each new model specifically targets the previous model's mistakes, reducing bias. The trade-off in both cases is interpretability: a single decision tree is easy to explain, a forest of 500 trees is not.
Source: [[02 Literature Notes/Courses/Machine Learning - Lesson 05 Ensemble Learning]]

### Unsupervised Learning (Clustering and Dimensionality Reduction)
When you have no labels, clustering (K-Means, hierarchical, DBSCAN) groups similar data points together — e.g. segmenting customers into groups without being told in advance what the groups are. Dimensionality reduction (PCA) compresses many correlated features into fewer components while retaining most of the information, which helps with visualization and as a preprocessing step before supervised models. Because there are no labels, evaluation uses different tools (silhouette score, inertia) rather than accuracy/precision.
Source: [[02 Literature Notes/Courses/Machine Learning - Lesson 06 Unsupervised Learning]]

### Recommendation Systems
Predicting what a user will like next by combining supervised and unsupervised ideas into an applied system. Collaborative filtering uses patterns across users or items ("people who liked X also liked Y") without needing to understand *why*; content-based filtering uses the actual features of the items (genre, price, ingredients) to recommend similar ones. Hybrid systems combine both, since collaborative filtering struggles with brand-new users or items that have no interaction history yet (the "cold start" problem).
Source: [[02 Literature Notes/Courses/Machine Learning - Lesson 07 Recommendation Systems]]

---

## Stage 3 — Deep Learning

### Introduction to Deep Learning
Deep learning is machine learning built on layered neural networks that learn hierarchical representations directly from data — the conceptual bridge from "ML algorithms" (regression, trees, SVMs) into "network architectures" (ANN, CNN, RNN, Transformer, autoencoder) that make up the rest of this stage.
Source: [[02 Literature Notes/Courses/Deep Learning - Lesson 02 Introduction to Deep Learning]]

### Artificial Neural Networks (Perceptrons, Activation Functions)
A perceptron is the basic neural unit: it takes weighted inputs, sums them, and passes the result through an activation function to decide its output. Activation functions (sigmoid, ReLU, etc.) are what let a network learn non-linear patterns — without them, stacking layers would collapse mathematically into a single linear model.
Source: [[02 Literature Notes/Courses/Deep Learning - Lesson 03 Artificial Neural Network]]

### Deep Neural Networks and Forward Propagation
Stacking multiple hidden layers (instead of just one) lets a network learn more complex, hierarchical representations — but also makes training harder. Forward propagation is the mechanism of computing a prediction: data flows layer by layer, each layer transforming the previous layer's output, until it reaches the final prediction.
Source: [[02 Literature Notes/Courses/Deep Learning - Lesson 04 Deep Neural Network]]

### TensorFlow
A major framework for building and training neural networks, built around **tensors** (the N-dimensional array data structure used throughout). It offers a Sequential API (stack layers in order — simple, covers most cases) and a Functional API (define arbitrary graphs of layers — needed for models with multiple inputs/outputs or shared layers).
Source: [[02 Literature Notes/Courses/Deep Learning - Lesson 05 TensorFlow]] · Snippet: [[04 Code Snippets/ML/TensorFlow Sequential Classifier]]

### PyTorch
A second major deep learning framework, more code-first and flexible, widely used in research and iterative experimentation. The underlying concepts — tensors, layers, training loops, optimization — transfer directly between PyTorch and TensorFlow; framework choice matters less than understanding those underlying concepts.
Source: [[02 Literature Notes/Courses/Deep Learning - Lesson 06 PyTorch]]

### Optimization and Regularization (SGD, Adam, Dropout)
Optimization algorithms determine *how* a network updates its weights in response to error, which strongly affects whether training converges quickly, slowly, or not at all. Plain gradient descent (SGD) moves weights in the direction that reduces loss; Momentum, AdaGrad, RMSProp, and Adam build on this by adapting the step size over time, generally training faster and more reliably than plain SGD. Dropout is a separate lever — randomly disabling neurons during training — that fights overfitting by preventing the network from relying too heavily on any single neuron.
Source: [[02 Literature Notes/Courses/Deep Learning - Lesson 07 Model Optimization and Performance Improvement]] · Permanent: [[03 Permanent Notes/Optimization Shapes How Neural Networks Learn]]

### Convolutional Neural Networks (CNNs)
CNNs learn spatial features in image data by sliding small filters across the image to detect patterns like edges and textures, then pooling and stacking layers to build up to higher-level shapes and objects. This local-pattern-then-compose structure is what makes CNNs dramatically more effective on images than a plain fully-connected network, which would have to learn every pixel position independently.
Source: [[02 Literature Notes/Courses/Deep Learning - Lesson 08 Convolutional Neural Networks]] · Permanent: [[03 Permanent Notes/Convolutional Neural Networks Learn Spatial Features]] · Snippet: [[04 Code Snippets/ML/CNN Image Classifier with Data Augmentation]]

### Transfer Learning
Instead of training a model from scratch, reuse a model already trained on a large dataset (e.g. ImageNet) and adapt it to your smaller, specific task — either by using it as a fixed feature extractor or by fine-tuning some/all of its layers on your data. This is one of the most practical techniques in all of deep learning because it slashes the amount of labeled data and compute you need; a team with 2,000 labeled images can still get strong results by starting from a model trained on millions.
Source: [[02 Literature Notes/Courses/Deep Learning - Lesson 09 Transfer Learning]] · Permanent: [[03 Permanent Notes/Transfer Learning Reuses Pretrained Models]] · Snippet: [[04 Code Snippets/ML/Transfer Learning with VGG16 Base Model]]

### Object Detection (YOLO)
Image classification answers "what is in this image?"; object detection answers "what is in this image, and where?" by predicting bounding boxes alongside class labels. YOLO ("You Only Look Once") is a prominent real-time approach, fast enough for live video. This lesson also introduces deployment concerns — converting a trained model to a lightweight format (TensorFlow Lite) for running on constrained devices.
Source: [[02 Literature Notes/Courses/Deep Learning - Lesson 10 Object Detection]]

### Recurrent Neural Networks (RNNs) and LSTMs
An RNN processes a sequence one step at a time while carrying a hidden state forward, so it can use earlier context (earlier words in a sentence, earlier timesteps in a series) when interpreting what comes next. Basic RNNs struggle with long-range dependencies (forgetting something mentioned many steps earlier); LSTMs add gating mechanisms that let them selectively remember or forget, handling longer sequences much better.
Source: [[02 Literature Notes/Courses/Deep Learning - Lesson 11 Recurrent Neural Network]] · Permanent: [[03 Permanent Notes/Recurrent Neural Networks Model Sequence Dependencies]] · Snippet: [[04 Code Snippets/ML/Bidirectional LSTM Text Classifier]]

### Transformers and Attention (BERT)
Transformers model sequences using attention — directly relating any token to any other token — instead of processing step-by-step like an RNN. This makes long-range dependencies much easier to capture and, critically, parallelizes across a sequence instead of forcing sequential processing, which is why transformers scale so well to huge pretrained models. BERT is a landmark pretrained transformer that can be fine-tuned for classification, search, and question answering with comparatively little task-specific data.
Source: [[02 Literature Notes/Courses/Deep Learning - Lesson 12 Transformer Models for NLP]] · Permanent: [[03 Permanent Notes/Transformers Use Attention for Sequence Modeling]] · Snippet: [[04 Code Snippets/ML/BERT Text Classifier in PyTorch]]

### Autoencoders
An autoencoder is two networks back to back: an encoder that compresses input into a small latent representation, and a decoder that reconstructs the original input from that compressed form. Training it to minimize reconstruction error forces it to keep only the most important information — useful for dimensionality reduction, representation learning, and spotting anomalies (inputs that reconstruct unusually poorly are "unlike" the training data).
Source: [[02 Literature Notes/Courses/Deep Learning - Lesson 13 Getting Started with Autoencoders]] · Permanent: [[03 Permanent Notes/Autoencoders Learn Compact Representations]]

---

## Stage 4 — Generative AI

### GenAI Overview and AI Project Implementation
Generative AI differs from traditional (discriminative) ML: instead of predicting a label or number, it generates new content — text, images, audio, or a mix (multimodal). This lesson also covers how to scope and implement an AI project end to end, which matters because GenAI projects fail as often from poor scoping as from poor models.
Source: [[02 Literature Notes/Courses/Generative AI - Lesson 01 Overview of GenAI and AI Project Implementation]]

### Working with GPTs (Prompting and Custom GPTs)
Prompt design and iteration — how you phrase and structure a request to a GPT model materially changes output quality and reliability. Includes customizing GPTs for specific tasks and evaluating/refining outputs rather than accepting the first result.
Source: [[02 Literature Notes/Courses/Generative AI - Lesson 02 Working with GPTs]]

### GPT Demos Catalog (Applied GenAI Patterns)
A set of 16 hands-on demos applying GPT/GenAI tools across real workflows, grouped into themes: content creation & marketing, analysis & productivity, custom GPTs & tool integrations (e.g. Zapier automation), and multimodal exploration. This is the "apply what you learned" counterpart to the prompting lesson above.
Source: [[02 Literature Notes/Courses/Generative AI - GPT Demos Catalog]]

---

## Stage 5 — LLM Engineering

> The applied LLM-engineering layer that sits on top of the classical ML/DL foundation above — the implementation-ready knowledge for building production LLM systems (RAG, agents, evals, fine-tuning, LLMOps, security).

### Domain 1 — Data Representation

#### Tokenization (Subword Tokenization)
LLMs don't read text — they read integer token IDs produced by a tokenizer. Subword tokenization (BPE, WordPiece, Unigram) is the practical compromise between word-level and character-level tokenizing: common words become a single token, rare words split into meaningful pieces, and byte-level fallback guarantees *any* string — emojis, typos, code, unseen languages — can be represented with zero out-of-vocabulary tokens. The trade-off: because characters are often hidden inside merged tokens, models are unreliable at character-level tasks like reversing a string or counting letters.
Source: [[02 Literature Notes/LLM Engineering/Tokenization]] · Permanent: [[03 Permanent Notes/Subword Tokenization Balances Vocabulary and Sequence Length]]

#### Tokens as the Unit of Cost and Context
Because LLMs process tokens (not characters or words), the token is the atomic unit of API pricing, context-window limits, and latency. Cost is linear: `input tokens × input price + output tokens × output price`. A rule of thumb is ~4 characters ≈ 1 token for English, but non-English or code-heavy text fragments into more tokens per character — the same idea can cost noticeably more in Japanese than in English, and a naive sum of message lengths underestimates true token count because chat APIs add hidden per-message template overhead.
Source: [[02 Literature Notes/LLM Engineering/Tokenization]] · Permanent: [[03 Permanent Notes/Tokens Are the Unit of Cost and Context]]

#### Embeddings
An embedding is a fixed-length vector encoding meaning, such that semantically similar text lands near each other in vector space and unrelated text lands far apart — "car" and "automobile" end up close despite sharing no characters. This turns "find similar meaning" into "find nearby vectors," a fast geometric operation, which is what powers semantic search, RAG, clustering, deduplication, and recommendation. The crucial caveat: embeddings encode similarity of *meaning*, not factual truth — two confidently wrong sentences can embed very close together.
Source: [[02 Literature Notes/LLM Engineering/Embeddings]] · Permanent: [[03 Permanent Notes/Embeddings Turn Meaning into Geometry]]

#### Normalizing Embeddings (Dot Product as Cosine)
If every embedding vector is normalized to unit length (L2-normalized), cosine similarity becomes mathematically equal to the dot product — and the dot product is cheaper to compute, since it skips a magnitude division per comparison. Production systems normalize once at ingestion time, then use the faster dot product everywhere downstream. Skipping this step while using dot product lets a vector's raw magnitude leak into the similarity score, unfairly favoring longer texts.
Source: [[02 Literature Notes/LLM Engineering/Embeddings]] · Permanent: [[03 Permanent Notes/Normalize Embeddings to Use Dot Product as Cosine]]

#### Embedding Model Selection
There is no universal "best" embedding model — only the best model for a specific workload. The right process: use the MTEB benchmark to build a shortlist (looking at the Retrieval sub-score specifically, not the overall average), then build a 30-100 query golden test set from your *own* corpus and measure recall@k and MRR directly — because a model that tops the general leaderboard can still under-retrieve on your specific domain. Model choice is semi-permanent: switching later means re-embedding your entire corpus.
Source: [[02 Literature Notes/LLM Engineering/Embedding Model Selection]] · Permanent: [[03 Permanent Notes/Pick Embedding Models by Retrieval Eval Not Leaderboard]]

#### Vector Search (Approximate Nearest Neighbors)
Vector search finds the top-k stored vectors most similar to a query vector. Exact nearest-neighbor search (brute force, comparing against every vector) is simple and exact but scales linearly with corpus size; beyond roughly 100k vectors, production systems switch to Approximate Nearest Neighbor (ANN) indexes that trade a small amount of recall for large speed gains. The central operational knob in any vector search system is this recall-vs-latency trade-off.
Source: [[02 Literature Notes/LLM Engineering/Vector Search]] · Permanent: [[03 Permanent Notes/Vector Search Is Approximate Nearest Neighbors at Scale]]

#### ANN Index Internals — HNSW
HNSW (Hierarchical Navigable Small World) organizes vectors into a multi-layer graph you *navigate* rather than scan — like a skip-list's "express lanes," search starts at a sparse top layer and greedily hops toward the query, dropping down a layer whenever it can't get closer, for roughly O(log N) hops instead of O(N). It gives the best recall-at-latency of the major ANN approaches, at the cost of the most memory (it stores the full vectors plus the graph), and is the default choice in most vector databases for corpora under ~10M vectors.
Source: [[02 Literature Notes/LLM Engineering/ANN Index Internals]] · Permanent: [[03 Permanent Notes/HNSW Trades Memory for Fast High-Recall Search]]

#### ANN Index Internals — IVF and Product Quantization (PQ)
IVF (Inverted File) *prunes* the search space: cluster the corpus with k-means, then at query time only scan the handful of clusters nearest the query instead of the whole corpus. PQ (Product Quantization) *compresses* each vector by splitting it into sub-vectors and replacing each with a 1-byte cluster ID — shrinking a 768-dimension float32 vector from 3072 bytes down to as little as 64 bytes (~48x), though lossily, which is why it's paired with an exact re-ranking step on the surviving candidates. `IVFPQ` combines both and is how billion-scale vector search fits on a single machine.
Source: [[02 Literature Notes/LLM Engineering/ANN Index Internals]] · Permanent: [[03 Permanent Notes/IVF and PQ Prune and Compress the Search Space]]

#### Chunking Strategies
In a RAG system, a "chunk" is simultaneously the unit that gets *retrieved* and the unit the model *grounds* its answer on — so chunk size and boundaries set a hard ceiling on how accurate the whole system can be. Too small, and the answer gets scattered across more chunks than top-k returns; too large, and one vector tries to represent too many ideas at once and matches nothing sharply. Example: a one-sentence chunk like "This reduced latency by 40%" is nearly unretrievable in isolation, because "this" lost the referent that made it meaningful.
Source: [[02 Literature Notes/LLM Engineering/Chunking Strategies]] · Permanent: [[03 Permanent Notes/Chunking Is the Unit of Retrieval and Grounding]]

#### Contextual Retrieval
Chunking strips away the surrounding document context that made a passage meaningful. Contextual retrieval repairs this by having an LLM read the whole document plus a chunk, and prepend a short context sentence to the chunk *before* embedding it — e.g. turning "This cut costs by 40%" into "[From the 2023 annual report, discussing the new supplier contract:] This cut costs by 40%," which is now retrievable for cost-related queries. The cost (one LLM call per chunk) is paid once at ingestion and amortized across every future query.
Source: [[02 Literature Notes/LLM Engineering/Chunking Strategies]] · Permanent: [[03 Permanent Notes/Contextual Retrieval Restores Lost Chunk Context]]

### Domain 2 — Model Internals

#### Attention (Query, Key, Value)
Attention computes, for each token, a weighted average of every other token's **Value**, where the weights come from comparing that token's **Query** (what it's looking for) against every other token's **Key** (what it offers) via `softmax(QKᵀ/√d_k)`. It's a differentiable, content-based lookup: rather than a fixed rule for which words relate to which, the model learns to compute relevance on the fly. Multi-head attention runs several of these lookups in parallel so different heads can specialize — one tracking syntax, another tracking coreference ("it" refers to what?), etc.
Source: [[02 Literature Notes/LLM Engineering/Attention Deep-Dive]] · Permanent: [[03 Permanent Notes/Attention Is Content-Based Soft Lookup]]

#### Transformer Architecture (Attention + MLP, Residual Stream)
A transformer block has two distinct jobs: attention mixes information *between* token positions (the only place tokens actually talk to each other), while the MLP sublayer transforms each token's representation independently (believed to store much of the model's factual knowledge as key-value memories). Both write into a shared "residual stream" that carries information forward through the network with a clean gradient path — stack many of these blocks and you have a GPT-style decoder-only LLM.
Source: [[02 Literature Notes/LLM Engineering/Transformer Architecture]] · Permanent: [[03 Permanent Notes/Attention Communicates Between Tokens the MLP Computes Within Them]]

#### Why Attention Is Quadratic in Sequence Length
The attention score matrix is `[sequence length, sequence length]` in size, so computing it costs O(seq²) in both time and memory — double your context length and you quadruple the compute. This single fact is the root cause of long-context pricing, the need for techniques like FlashAttention (which avoids ever materializing the full score matrix), and the KV cache (which lets each new generated token attend to *cached* past keys/values in O(seq) instead of recomputing from scratch).
Source: [[02 Literature Notes/LLM Engineering/Attention Deep-Dive]] · Permanent: [[03 Permanent Notes/Attention Is Quadratic in Sequence Length]]

#### Decoding and Sampling (Temperature, Top-k, Top-p)
A model outputs a *probability distribution* over the next token; decoding is the policy you use to actually pick one — and it's a product decision independent of the model's weights. Temperature rescales the distribution before sampling (low = peaked/deterministic, high = flat/random); top-k keeps only the k most likely tokens; top-p ("nucleus") keeps the smallest set of tokens whose combined probability covers p, adapting automatically to how confident the model is. The same model can be a precise fact-answerer at temperature=0 or a creative writer at temperature=1.1.
Source: [[02 Literature Notes/LLM Engineering/Decoding and Sampling]] · Permanent: [[03 Permanent Notes/Decoding Is a Policy Over the Models Distribution]]

#### Temperature Zero for Structured/Evaluated Output
For anything that must be correct and reproducible — JSON tool calls, structured extraction, evaluation runs — use greedy decoding (temperature=0). Randomness only adds a risk of schema breaks and non-reproducible evals with zero upside in these cases; reserve higher temperatures for open-ended creative generation where diversity is actually the goal. Caveat: temperature=0 is *near*-deterministic, not bit-exact, because hardware/batching/floating-point effects can still perturb results slightly.
Source: [[02 Literature Notes/LLM Engineering/Decoding and Sampling]] · Permanent: [[03 Permanent Notes/Set Temperature Zero for Structured and Evaluated Output]]

#### Structured Generation (Constrained Decoding)
To make LLM output usable by downstream code, enforce a schema rather than hoping the free-text output parses correctly. Three levels of strength: prompt-and-hope (weakest), provider structured-output/function-calling modes (strong, easy), and constrained decoding (masks out any token that would violate a grammar, so illegal output is *structurally impossible* — even from a small model). Always pair this with a semantic validation and repair step, since valid JSON is not the same thing as *correct* JSON (a well-formed invoice could still have a `total` that doesn't match the sum of its line items).
Source: [[02 Literature Notes/LLM Engineering/Structured Generation]] · Permanent: [[03 Permanent Notes/Constrain Generation Dont Parse Hope]] · [[03 Permanent Notes/Structural Validity Is Not Semantic Correctness]]

#### LLM Efficiency (Memory-Bandwidth-Bound Inference)
The bottleneck in serving an LLM is usually *moving data* (weights and the KV cache) through GPU memory, not raw arithmetic throughput. This reframes where the real optimization wins are: quantization (fewer bits per weight), KV cache reuse, GQA/MQA (sharing K/V across attention heads to shrink the cache), and FlashAttention (avoid materializing the full attention matrix) — all memory-side levers, not compute-side ones.
Source: [[02 Literature Notes/LLM Engineering/LLM Efficiency]] · Permanent: [[03 Permanent Notes/LLM Inference Is Usually Memory-Bandwidth Bound]]

#### Reasoning Models and Test-Time Compute
Beyond making a model bigger during training, accuracy on hard problems can also be bought at *inference* time — by generating longer chains of thought, sampling multiple solution paths and voting (self-consistency), or searching over reasoning states with a verifier. Reasoning models (o1/o3, DeepSeek-R1) bake this in via reinforcement learning, effectively learning to "think longer" before answering. The catch: it's a dial, not free — latency and cost scale with how long the model thinks, and easy tasks see little or no benefit from it.
Source: [[02 Literature Notes/LLM Engineering/Reasoning Models]] · Permanent: [[03 Permanent Notes/Test-Time Compute Is a New Scaling Axis]]

### Domain 3 — Prompting & Interaction

#### Prompt Contracts
Production prompts should be designed like API contracts, not prose tweaked by feel: use message roles deliberately (system = identity and hard rules, developer = task and schema, user = runtime data), pin an output schema you can validate against, provide few-shot examples for format and edge cases, and explicitly define a refusal path for the unhappy case. When the contract is explicit, the model behaves like a dependable software component instead of "a slot machine."
Source: [[02 Literature Notes/LLM Engineering/Prompt Contracts]] · Permanent: [[03 Permanent Notes/A Prompt Is an API Contract Not a Sentence]]

#### Always Give the Model a Refusal Path
If a prompt demands an answer in a fixed format but gives no legitimate way to say "I can't," the model will fabricate an answer just to satisfy the format. The fix is a first-class escape hatch built into the schema itself — e.g. `{"answer": null, "reason": "insufficient context"}` — plus an explicit instruction to use it when context is missing or low-confidence. This single change is one of the largest levers on groundedness in a RAG system: it converts "confident hallucination" into an honest, handle-able abstention.
Source: [[02 Literature Notes/LLM Engineering/Prompt Contracts]] · Permanent: [[03 Permanent Notes/Always Give the Model a Refusal Path]]

#### Prompt Versioning
Production prompts are release artifacts, not throwaway text — they need semantic versions (patch = wording-only fix, minor = compatible improvement, major = schema/task/refusal/tool-contract change), traveling alongside the model ID, decoding parameters, output schema, examples, and a changelog. When a regression appears in production, you need to know precisely which prompt+model combination produced it, and how to roll back.
Source: [[02 Literature Notes/LLM Engineering/Prompt Versioning]] · Permanent: [[03 Permanent Notes/Prompts Need Semantic Versions]]

#### Reasoning Prompt Patterns (CoT, ReAct, Self-Consistency)
Each reasoning pattern spends extra tokens/calls to improve hard tasks, and is a control-flow choice rather than a magic phrase: chain-of-thought adds intermediate reasoning steps, ReAct adds tool observations into the loop, self-consistency samples several solution paths and votes, decomposition splits a big problem into subproblems, and reflection revises an answer using feedback. The practical rule is to use the cheapest pattern that actually clears your evaluation bar — direct prompting for simple tasks, escalating only when the task justifies the extra cost.
Source: [[02 Literature Notes/LLM Engineering/Reasoning Prompt Patterns]] · Permanent: [[03 Permanent Notes/Reasoning Patterns Are Compute Allocation Strategies]]

#### Context Engineering (Context Assembly)
An LLM call is never just "a prompt" — it's an assembled context window containing instructions, task input, conversation history, retrieved documents, tool definitions, few-shot examples, and selected memory. Treating that assembly as production logic (ranking candidates, filtering irrelevant chunks, compressing carefully, enforcing token budgets, deliberately ordering evidence, tracing exactly what was included) is what context engineering means — the model only ever reasons over the context you actually hand it.
Source: [[02 Literature Notes/LLM Engineering/Context Engineering]] · Permanent: [[03 Permanent Notes/Context Assembly Is Part of the Program]]

#### Long Context Is Not the Same as Useful Context
A large context window is *capacity*, not quality — irrelevant tokens can distract the model, raise cost, and bury the evidence it actually needs. The well-known "lost in the middle" finding is the practical warning here: facts placed in the middle of a long context are used less reliably than facts near the beginning or end. The fix is selective assembly: retrieve fewer, better chunks, order them deliberately, and summarize or deduplicate aggressively rather than just stuffing the window full.
Source: [[02 Literature Notes/LLM Engineering/Context Engineering]] · Permanent: [[03 Permanent Notes/Long Context Does Not Mean Useful Context]]

### Domain 4 — Retrieval-Augmented Generation (RAG)

#### RAG Pipeline Fundamentals (Retrieve Then Read)
RAG is best understood as "retrieve then read": first find a small evidence set from an external corpus, then ask the model to answer under a contract that requires citing that evidence and allows refusing when evidence is missing. Because the knowledge lives in documents and indexes rather than only in the model's weights, it can be updated, filtered, deleted, and audited — e.g. a company can update its RAG answers by editing a document, with no retraining required.
Source: [[02 Literature Notes/LLM Engineering/RAG Pipeline Fundamentals]] · Permanent: [[03 Permanent Notes/RAG Is Retrieve Then Read With a Citation Contract]]

#### RAG Quality Is Capped by Ingestion Quality
A retriever can only search what ingestion actually preserved. If a document parser shuffles reading order, drops headings, flattens tables into scrambled prose, or treats OCR errors as ground truth, the embedding index contains distorted knowledge — and the model then appears to "hallucinate" when really it was just fed bad context. Production ingestion needs to preserve structure: reading order, section hierarchy, tables, captions, page provenance, and OCR confidence.
Source: [[02 Literature Notes/LLM Engineering/Document Ingestion and Parsing]] · Permanent: [[03 Permanent Notes/RAG Quality Is Capped by Ingestion Quality]]

#### Document Ingestion and Parsing (Tables, OCR)
PDFs encode positioned glyphs, HTML encodes hierarchy, tables encode two-dimensional row/column relationships, and scanned documents need OCR with inherent uncertainty — "parsing" is not simply "extract the text," it's preserving enough structure for the downstream chunker and retriever to work with. Tables in particular should be serialized as structure (Markdown table, or JSON/CSV for computation), not flattened into paragraphs, because flattening destroys the row/column relationships a question might depend on.
Source: [[02 Literature Notes/LLM Engineering/Document Ingestion and Parsing]] · Permanent: [[03 Permanent Notes/Tables Are Two Dimensional Evidence Not Paragraphs]]

#### Advanced Retrieval (Recall → Rerank → Diversity Funnel)
A mature retriever is a funnel, not a single search call: start broad and cheap to maximize *recall* (dense vector search plus lexical/BM25 search as candidates), fuse the two result lists robustly (often with Reciprocal Rank Fusion), spend an expensive cross-encoder model on *reranking* the merged candidates for *precision*, then select a diverse final set (MMR) so the model sees complementary rather than redundant evidence. Dense vector search alone is a reasonable baseline — but not a production-grade architecture by itself.
Source: [[02 Literature Notes/LLM Engineering/Advanced Retrieval]] · Permanent: [[03 Permanent Notes/Production Retrieval Is a Recall Precision Diversity Funnel]]

#### Reciprocal Rank Fusion
Dense (vector) and lexical (BM25) search scores live on incompatible numeric scales, so simply averaging them is brittle. Reciprocal Rank Fusion instead combines ranked lists by *rank position* — a document gets credit for appearing near the top of either list — which makes hybrid retrieval robust and easy to reason about without needing to calibrate scores against each other.
Source: [[02 Literature Notes/LLM Engineering/Advanced Retrieval]] · Permanent: [[03 Permanent Notes/Reciprocal Rank Fusion Avoids Score Calibration Problems]]

#### Query Transformation (HyDE, Decomposition)
Users ask conversational questions, but retrievers need search-optimized text, so query transformation rewrites the raw question into forms that match the corpus better: HyDE generates a hypothetical ideal answer and embeds *that* for search, decomposition breaks a compound question into subquestions, and step-back prompting abstracts a specific question into a more general one first. Crucially, the transformed text is only a retrieval aid — the final answer must still cite the real documents that were actually retrieved, not the hypothetical query text.
Source: [[02 Literature Notes/LLM Engineering/Query Transformation]] · Permanent: [[03 Permanent Notes/Query Transformation Turns One Bad Search Into Several Better Searches]]

#### GraphRAG
GraphRAG builds a second index over the corpus — entities, relationships, communities, and summaries, each with provenance back to source chunks — so retrieval can follow *relationships between facts* instead of only finding text that looks semantically similar. It's most valuable when answers depend on connections across many documents, like "who owns what" or "what risks cluster together" — questions a single-chunk vector search can't answer no matter how good the embedding model is. Without provenance on every node and edge, a graph becomes just another source of uncited, ungrounded claims.
Source: [[02 Literature Notes/LLM Engineering/GraphRAG]] · Permanent: [[03 Permanent Notes/GraphRAG Adds a Relationship Index to RAG]] · [[03 Permanent Notes/GraphRAG Needs Provenance or It Becomes Uncited Claims]]

#### Agentic RAG
Agentic RAG lets the system call retrieval repeatedly and adaptively instead of once: plan a subquestion, retrieve, grade whether the evidence found is actually sufficient, rewrite or broaden the query if it's weak, and only answer once the evidence clears a bar. This helps with multi-hop or ambiguous questions that one-shot RAG underserves — but needs strict iteration budgets and logging, or adaptivity turns into runaway, unbounded search.
Source: [[02 Literature Notes/LLM Engineering/Agentic RAG]] · Permanent: [[03 Permanent Notes/Agentic RAG Makes Retrieval an Adaptive Tool Call]]

#### Corrective RAG
A specific agentic-RAG pattern: grade the retrieved evidence's quality *before* generation. Strong evidence proceeds straight to answering; partial evidence triggers a query rewrite; weak evidence broadens the search to more sources; no evidence (or an exhausted retry budget) produces an explicit refusal. The point is to never blindly hand the model low-quality context and hope the prompt alone fixes it — because a capable model will often "launder" weak evidence into a confident-sounding but wrong answer.
Source: [[02 Literature Notes/LLM Engineering/Agentic RAG]] · Permanent: [[03 Permanent Notes/Corrective RAG Is an Evidence Quality Gate]]

#### Retrieval Evaluation (Recall@k, MRR, Precision@k)
RAG evals that only look at the final answer hide *where* a failure actually came from — search or generation. Retrieval needs its own labeled evaluation set with known-relevant chunk IDs per query, scored with recall@k (was the evidence found at all?), MRR (did the first relevant result appear early?), and precision@k (how much noise is in the final context?). These metrics diagnose different problems: low recall points to chunking/candidate generation, low MRR points to reranking, low precision points to filtering.
Source: [[02 Literature Notes/LLM Engineering/Retrieval Evaluation]] · Permanent: [[03 Permanent Notes/Retrieval Needs Its Own Evaluation Set]] · [[03 Permanent Notes/Recall MRR and Precision Diagnose Different Retrieval Failures]]

#### Vector Database Landscape
Vector database choice should follow retrieval requirements — scale, latency, metadata filtering, hybrid search, multi-tenancy, update/delete support, managed operations — not brand recognition or raw ANN benchmark recall. RAG systems fail just as often from missing hybrid search or poor delete handling as from a slightly worse recall number. FAISS is a useful comparison point here: it's a high-performance *library* for vector indexing, not a production *service* — persistence, APIs, filters, and access control are all still your responsibility if you build on it directly.
Source: [[02 Literature Notes/LLM Engineering/Vector Database Landscape]] · Permanent: [[03 Permanent Notes/Choose a Vector Database by Retrieval Operations Not Brand]] · [[03 Permanent Notes/FAISS Is a Library While Vector Databases Are Retrieval Services]]

#### Multimodal AI and Multimodal RAG
CLIP-style models align images and text in a shared embedding space, enabling text-to-image and image-to-text retrieval by cosine similarity — but that similarity reflects likely *relevance*, not verified *visual truth*; CLIP can match concepts without actually reading small text or counting objects precisely. Multimodal RAG extends retrieval to wherever the evidence actually lives: text chunks, OCR'd pages, image embeddings, audio transcripts — retrieving in the evidence's native modality, then reasoning/answering in a shared layer (often by calling a vision-language model when genuine visual reasoning, not just matching, is required).
Source: [[02 Literature Notes/LLM Engineering/Multimodal AI]] · Permanent: [[03 Permanent Notes/CLIP Similarity Is Retrieval Not Visual Truth]] · [[03 Permanent Notes/Multimodal RAG Retrieves Evidence Where It Lives]]

#### RAG Authorization (Access Control Before Retrieval)
A RAG system must never retrieve documents a user isn't allowed to see — once unauthorized text enters the model's prompt, the access breach has already happened; asking the model to "please ignore this" is not a real access control. Tenant, role, document ACL, and time-bound entitlement filters must be applied *before* vector ranking (or at the very latest, before context assembly) — and both allowed and denied retrieval decisions should be audited so security teams can reconstruct what happened after an incident.
Source: [[02 Literature Notes/LLM Engineering/AI Security and Governance]] · Permanent: [[03 Permanent Notes/RAG Authorization Happens Before Retrieval]]

#### RAG vs Fine-Tuning vs Long Context
These three are not interchangeable tools for the same problem. RAG is for external, frequently-changing, private, or citation-required knowledge. Fine-tuning is for internalizing *behavior* — style, tool-use habits, output schemas, domain skill. Long-context is useful when the relevant working set is genuinely small enough to pass in whole, and retrieval would risk lossily filtering out something needed. Mature systems often combine all three: fine-tuned behavior, retrieved evidence, and long-context assembly where the token budget allows.
Source: [[02 Literature Notes/LLM Engineering/RAG Pipeline Fundamentals]] · Permanent: [[03 Permanent Notes/RAG Fine Tuning and Long Context Solve Different Problems]] · [[03 Permanent Notes/Fine Tune Behavior Retrieve Knowledge]]

### Domain 5 — Agents

#### Tool and Function Calling
Tool calling turns an LLM into a planner that can request typed, structured actions — but the model only *proposes* the call; your runtime remains the executor, validating arguments, enforcing permissions, and actually running the action. This is a typed runtime boundary, not a model privilege: treating a model's tool-call output as something to execute directly (rather than as a request to authorize) is exactly how prompt injection escalates into real-world side effects.
Source: [[02 Literature Notes/LLM Engineering/Tool and Function Calling]] · Permanent: [[03 Permanent Notes/Tool Calling Is a Typed Runtime Boundary]] · [[03 Permanent Notes/The Model Proposes Tool Calls Policy Disposes]]

#### Agent Loops and Planning (ReAct)
An agent is fundamentally a bounded observe-think-act loop — a "while loop with brakes" — where a model decides the next step inside a software runtime that enforces termination conditions. ReAct is the dominant pattern underlying most agent implementations: alternating Thought (reason about what's needed), Action (call a tool), and Observation (inspect the result) in a cycle, where the observations ground each next step in real external state rather than the model's unchecked assumptions. The agentic failure modes are just as real as the capability: hallucinated tools, malformed arguments, infinite loops — all of which require a strict tool list, schemas, and a max-iteration cap.
Source: [[02 Literature Notes/LLM Engineering/Agent Loops and Planning]] · Permanent: [[03 Permanent Notes/An Agent Is a While Loop With Brakes]] · [[03 Permanent Notes/ReAct Turns Reasoning Into Tool Grounded Control Flow]]

#### Agent Memory (Scratchpad vs Durable Memory)
Agent memory is really a *write policy plus a retrieval policy*, not just "a vector database bolted on." A scratchpad holds state for the current run only; durable long-term memory persists facts, preferences, and episodes across runs, and needs its own rules about what's safe and useful enough to write (never secrets, never every single turn) and how it gets consolidated over time (summarizing old episodes, marking stale facts) so it doesn't just accumulate noise.
Source: [[02 Literature Notes/LLM Engineering/Agent Memory]] · Permanent: [[03 Permanent Notes/Memory Is Policy Not Storage]]

#### Multi-Agent Orchestration
Splitting a task across multiple specialized agents (a supervisor, debate between agents, a shared "blackboard" of state) only pays off when the specialization itself outweighs the coordination overhead it introduces. The default should be a single well-scoped agent; multi-agent architectures add real cost and debugging ambiguity, so they're justified specifically when distinct roles (e.g. "researcher" vs "critic" vs "executor") genuinely produce better results than one agent doing everything.
Source: [[02 Literature Notes/LLM Engineering/Multi-Agent Orchestration]] · Permanent: [[03 Permanent Notes/Use Multi-Agent Only When Specialization Wins]]

#### Model Context Protocol (MCP)
MCP is a standard protocol for plugging a model host into external resources, tools, and prompts through a consistent server interface — it standardizes the *plumbing* for giving a model access to capabilities, not the model's behavior itself. MCP servers package capabilities explicitly (a defined tool, with a defined schema and defined scope) rather than leaving "what the model can touch" implicit or ad hoc.
Source: [[02 Literature Notes/LLM Engineering/Model Context Protocol]] · Permanent: [[03 Permanent Notes/MCP Standardizes Context Plumbing]]

#### Agent Framework Literacy (LangChain, LlamaIndex, LangGraph, DSPy)
The right framework choice depends on what's actually hard in your system, not on which one is most hyped: raw SDK calls if the hard part is simple provider calls, LlamaIndex/Haystack if it's ingestion and retrieval, LangGraph if it's stateful multi-step agent workflows, DSPy if it's optimizing prompt behavior against labeled examples. Frameworks buy real velocity through packaged integrations and orchestration — but the moment they hide visibility into prompts, retrieved context, tool arguments, and costs, debugging through the abstraction becomes harder than just building the missing piece directly.
Source: [[02 Literature Notes/LLM Engineering/Framework Ecosystem Literacy]] · [[02 Literature Notes/LLM Engineering/Agent Framework Literacy]] · Permanent: [[03 Permanent Notes/Choose LLM Frameworks by the Hard Part of the System]] · [[03 Permanent Notes/Frameworks Are Leverage Until They Hide the Control Surface]]

#### Agent Reliability and Cost
Agent reliability lives in the *runtime*, not in clever prompting: caps on iteration count, hard cost budgets per run, retries with limits, guardrails, checkpoints for recovery, and full execution traces are what make an inherently stochastic planner safe to run unattended. Every agent run needs an explicit cost budget — otherwise a single malformed loop (the agent repeatedly retrying a failing tool call, for instance) can silently burn an unbounded amount of API spend before anyone notices.
Source: [[02 Literature Notes/LLM Engineering/Agent Reliability and Cost]] · Permanent: [[03 Permanent Notes/Agent Reliability Lives in the Runtime]] · [[03 Permanent Notes/Every Agent Run Needs a Cost Budget]]

### Domain 6 — Evaluation

#### Eval Fundamentals
An eval is an *executable claim* about quality: a dataset of representative cases, a runner that executes the system under test, a scorer (metric, judge, or human label), and a decision rule (a threshold that gates shipping). A polished demo shows a system can work *once*; an eval harness shows how often it works, for whom, and where specifically it fails — which is the actual difference between "looks good" and "proven good enough to ship." Offline evals run on fixed data before shipping (cheap, repeatable, good for regression testing); online evals observe real users via A/B tests and guardrail metrics (needed to confirm real-world impact).
Source: [[02 Literature Notes/LLM Engineering/Eval Fundamentals]] · Permanent: [[03 Permanent Notes/A Demo Is Not Proof]] · [[03 Permanent Notes/An Eval Harness Is a Product Instrument]]

#### Prompt Evals as Regression Tests
A golden prompt evaluation set functions exactly like a regression test suite for model behavior: it encodes "must not break" cases — common inputs, edge cases, known adversarial injections, prior production incidents — and CI compares a candidate prompt/model change against those cases before real traffic ever sees it. For structured tasks, test exact field values and types; for generative tasks, test *properties* (groundedness, citation coverage, length, cost) rather than exact text, since exact text will legitimately vary run to run.
Source: [[02 Literature Notes/LLM Engineering/Prompt Versioning]] · Permanent: [[03 Permanent Notes/Prompt Evals Are Regression Tests]]

#### Groundedness and Faithfulness
Groundedness measures whether a model's claims are actually *supported by* the retrieved evidence — not whether the answer merely reads fluently and confidently. Faithfulness and answer relevance are genuinely different metrics: an answer can be perfectly faithful to the retrieved context while being irrelevant to what the user actually asked, or relevant to the question while fabricating details the context never supported.
Source: [[02 Literature Notes/LLM Engineering/Groundedness and Faithfulness]]

#### LLM as a Judge
Using one LLM to score another LLM's output scales evaluation far beyond what human review alone can cover — but an LLM judge is an *instrument*, not an oracle: it needs calibration against human-labeled examples before you trust it as a gate, and pairwise judging (comparing two outputs head-to-head) specifically needs bias audits, since judges have been shown to systematically favor longer answers or whichever response happens to appear first in the prompt.
Source: [[02 Literature Notes/LLM Engineering/LLM as a Judge]] · Permanent: [[03 Permanent Notes/LLM Judges Are Instruments Not Oracles]]

#### Online Evaluation
Watching a metrics dashboard trend up or down after a change is not the same thing as establishing that the change *caused* the difference — other traffic shifts, seasonality, or unrelated releases can produce the same pattern. Online evaluation needs actual causal design (A/B tests, canary comparisons with a real control group) rather than just "dashboard watching," because LLM quality signals are often too noisy at the single-request level to trust a trend without a proper comparison group.
Source: [[02 Literature Notes/LLM Engineering/Online Evaluation]]

#### Red-Teaming and Adversarial Evaluation
Red-teaming measures how robust a system is against deliberately hostile input — jailbreak attempts, prompt injection, attempts to extract system prompts or training data. The goal is *adversarial coverage* (systematically testing known attack categories) rather than chasing one clever one-off jailbreak that happened to work once; a single successful bypass tells you almost nothing about the system's overall hostile-robustness.
Source: [[02 Literature Notes/LLM Engineering/Red-Teaming and Adversarial Eval]]

#### Statistical Rigor in Evaluation
A single eval score with no uncertainty interval invites false confidence — a 2-point difference between two prompt versions might just be noise from a small test set, not a real improvement. Paired tests (comparing the *same* test cases across two versions) are statistically stronger than comparing independent averages, because they control for case-to-case difficulty variance that would otherwise drown out the actual signal you're trying to detect.
Source: [[02 Literature Notes/LLM Engineering/Statistical Rigor in Eval]]

#### Eval Framework Literacy
Eval frameworks (RAGAS, DeepEval, promptfoo, etc.) handle the plumbing — running cases, computing standard metrics, formatting reports — but they do not replace *product judgment* about what should actually be measured and what threshold means "ship it." Choosing an eval tool should follow the system boundary you're actually testing (retrieval-only vs end-to-end vs safety-specific), not just pick whichever tool is most popular.
Source: [[02 Literature Notes/LLM Engineering/Eval Framework Literacy]]

#### Benchmark Literacy
Public benchmarks and leaderboards are capability *signals*, not shipping gates — a model's benchmark rank says little about your specific domain, and leaderboards can mislead when they ignore test-set contamination (the model may have seen the benchmark during training), the exact evaluation harness used, or raw cost per query. Use benchmarks to narrow a shortlist of candidate models; make the final call with your own eval set.
Source: [[02 Literature Notes/LLM Engineering/Benchmark Literacy]]

### Domain 7 — Model Adaptation

#### Supervised Fine-Tuning (SFT)
SFT is best understood as behavioral cloning: the model is trained to imitate a set of (prompt, preferred-response) demonstration pairs, which define its response *policy* — structure, tone, refusal behavior, task procedure. Because SFT literally copies the behavior shown in the examples, bad labels directly become bad habits in the deployed model — the training data quality bar is "would I want the model to behave exactly like this example, every time?"
Source: [[02 Literature Notes/LLM Engineering/Supervised Fine-Tuning]] · Permanent: [[03 Permanent Notes/SFT Is Behavioral Cloning for Language Models]]

#### LoRA, QLoRA, and PEFT
Rather than retraining all of a model's billions of parameters, LoRA freezes the original weight matrix and learns a small low-rank "delta" matrix (`ΔW = (α/r)·B·A`) added on top — learning the *patch*, not a new model from scratch. This slashes the number of trainable parameters and the optimizer memory needed, and — just as importantly for production — turns the fine-tuned result into a small, swappable adapter artifact that can be trained, evaluated, rolled back, or hot-swapped while the (much larger) base model stays fixed and shared across many such adapters.
Source: [[02 Literature Notes/LLM Engineering/LoRA QLoRA PEFT]] · Permanent: [[03 Permanent Notes/LoRA Learns a Low Rank Delta Not a New Model]] · [[03 Permanent Notes/Adapters Make Fine Tuning Operationally Modular]]

#### Preference Optimization (RLHF, DPO)
Rather than training on single "correct" examples, preference optimization trains on *comparisons*: for a given prompt, response A should be ranked above response B. RLHF does this via a separate reward model plus reinforcement learning (PPO); DPO simplifies this by optimizing the pairwise preference margin directly without a separate RL loop. The risk in either approach: the reward model (or an AI judge standing in for one) is a *proxy* for what you actually want, and optimizing against it too hard can produce responses that are verbose, flattering, or evasive in ways that please the proxy while actually hurting the user.
Source: [[02 Literature Notes/LLM Engineering/Preference Optimization]] · Permanent: [[03 Permanent Notes/Preference Optimization Teaches Relative Judgment]] · [[03 Permanent Notes/Reward Models Are Proxies That Can Be Hacked]]

#### Distillation and Small Models
A large "teacher" model can label data, provide soft output distributions, or generate reasoning traces that train a smaller "student" model to imitate its behavior — the goal being *enough* quality at dramatically lower latency and cost, not matching the teacher's benchmark score exactly. A small model specifically wins over a large one when the task boundary is narrow, traffic volume is high, latency is critical, or the deployment needs to run offline/on-device — with uncertain edge cases routed up to a larger model rather than forcing the small model to handle everything.
Source: [[02 Literature Notes/LLM Engineering/Distillation and Small Models]] · Permanent: [[03 Permanent Notes/Distillation Converts Expensive Capability Into Cheap Inference]] · [[03 Permanent Notes/Small Models Win When the Task Boundary Is Narrow]]

#### Embedding Model Fine-Tuning
Fine-tuning an embedding model is a *ranking* problem, not a generation problem: training reshapes the vector space so that genuinely relevant query-document pairs end up close together and irrelevant pairs end up far apart, typically using contrastive learning with both easy and "hard" negatives (documents that look deceptively similar but are actually wrong) to force the model to learn the fine distinctions that actually matter for your domain.
Source: [[02 Literature Notes/LLM Engineering/Embedding Model Fine-Tuning]] · Permanent: [[03 Permanent Notes/Embedding Fine Tuning Teaches Retrieval Geometry]] · [[03 Permanent Notes/Hard Negatives Make Retrievers Smarter]]

#### Synthetic Data Generation
Using one LLM to generate training or eval data can expand coverage fast — but generation is only the first step; the real quality comes from the seeds you start with, your choice of teacher model, filtering, deduplication, and checking for contamination. Critically, synthetic *evaluation* data must never leak into training data: if a generated eval case (or its answer) ends up in the training set, the eval silently stops measuring real generalization and starts measuring memorization instead.
Source: [[02 Literature Notes/LLM Engineering/Synthetic Data Generation]] · Permanent: [[03 Permanent Notes/Synthetic Data Is a Factory Not Free Truth]] · [[03 Permanent Notes/Synthetic Evaluation Data Must Stay Out of Training]]

#### Scaling Laws (Chinchilla)
Transformer loss falls in a predictable power-law relationship with parameters, data, and compute. The key correction from the Chinchilla paper (2022) over earlier scaling-law work: for a *fixed* compute budget, most large models of that era were actually under-trained — you get a better result training a smaller model on substantially more tokens (roughly ~20 tokens per parameter) than training a huge model on comparatively few tokens. Concretely: a well-trained 7B-parameter model on 2 trillion tokens can beat a 13B model trained on only 300 billion tokens — bigger is not automatically better if the data budget doesn't scale with it.
Source: [[02 Literature Notes/LLM Engineering/Transformer Architecture]] · Permanent: [[03 Permanent Notes/Scaling Laws Reward Data Not Just Parameters]]

### Domain 8 — LLMOps / Production

#### LLM Observability (Traces, Not Just Logs)
A production LLM system is a causal graph — retrieval feeds prompt assembly, prompts feed the model call, the model calls tools, tools change later prompts — and a single log line cannot explain that chain. The basic unit of observability therefore has to be a *trace* with spans for retrieval, prompt rendering, the model call itself, tool calls, and any output validators, each carrying structured metadata like prompt version, token counts, latency, and cost.
Source: [[02 Literature Notes/LLM Engineering/Observability and Monitoring]] · Permanent: [[03 Permanent Notes/LLM Observability Starts With Traces Not Logs]]

#### PII-Safe Telemetry
LLM telemetry often contains the most sensitive data anywhere in the system — raw user messages, retrieved private documents, full completions, tool arguments — so observability has to be designed with redaction, sampling, and access control from day one, not bolted on afterward. The practical rule: store structured metadata (token counts, latency, cost, prompt version) always, but only store raw payloads when sampled, redacted, and specifically justified.
Source: [[02 Literature Notes/LLM Engineering/Observability and Monitoring]] · Permanent: [[03 Permanent Notes/PII Safe Telemetry Is a Product Requirement]]

#### Inference and Serving (KV Cache, Continuous Batching)
Once a model is loaded, serving performance depends mostly on scheduling and memory pressure rather than on the model's name. "Prefill" builds the KV cache from the input prompt; "decode" then generates output token-by-token while carrying that cache forward. Continuous batching keeps the GPU busy by adding and removing requests at token boundaries rather than waiting for a whole batch to finish together, and vLLM-style paged KV cache management reduces memory fragmentation across requests with wildly varying lengths.
Source: [[02 Literature Notes/LLM Engineering/Inference and Serving]] · Permanent: [[03 Permanent Notes/LLM Serving Is Queueing Plus KV Cache Management]]

#### Quantization and GQA
Two levers that cut serving cost with comparatively little effort and small quality loss: post-training quantization (compressing weights to INT4/INT8 with no retraining needed) roughly halves-to-quarters memory use and boosts throughput; GQA/MQA shrink the KV cache by sharing keys/values across multiple attention heads instead of storing a full separate copy per head — this matters most at long context lengths and large batch sizes, where the KV cache itself can actually exceed the memory footprint of the model's weights.
Source: [[02 Literature Notes/LLM Engineering/LLM Efficiency]] · Permanent: [[03 Permanent Notes/Quantization and GQA Are the Cheapest Serving Wins]]

#### Streaming Output
Token-by-token streaming (via server-sent events or websockets) usually doesn't reduce the *total* time to generate a full response, but it dramatically improves how fast the response *feels* — users care about time-to-first-token as proof the system is actually working, and streaming also enables mid-generation cancellation. A system can have perfectly fine average latency and still feel broken if its time-to-first-token is bad under load, which is why the two need to be measured separately.
Source: [[02 Literature Notes/LLM Engineering/Inference and Serving]] · Permanent: [[03 Permanent Notes/Streaming Improves Trust Before It Improves Throughput]]

#### Cost Architecture (The LLM Gateway)
An LLM gateway centralizes everything that otherwise sprawls uncontrolled across every application calling an LLM: provider API keys, model aliases, per-tenant budgets, retry policy, fallback behavior, caching, and logging — turning cost management from "a surprising invoice at the end of the month" into an enforceable, real-time control. The underlying cost principle is *selective escalation*: cache identical or near-identical requests, route routine traffic to cheap/small models, and reserve frontier-model spend specifically for cases where it measurably changes the outcome.
Source: [[02 Literature Notes/LLM Engineering/Cost Architecture]] · Permanent: [[03 Permanent Notes/The LLM Gateway Is the Cost Control Plane]] · [[03 Permanent Notes/Spend Strong Model Dollars Only Where They Change Outcomes]]

#### Reliability Patterns (Retries, Fallbacks, Escape Plans)
LLM calls fail in more varied ways than an ordinary API call: provider rate limits, long-tail latency spikes, malformed JSON output, safety refusals, flaky tool calls. Every LLM call needs an explicit "escape plan": time out, retry only if the failure is transient, fall back to a degraded path if a specific dependency is down, and when correctness genuinely can't be preserved, surface honest uncertainty rather than a confident guess. Retries specifically need exponential backoff with jitter (so clients don't all retry in a synchronized wave that amplifies an outage) and an idempotency key if the retried action has side effects.
Source: [[02 Literature Notes/LLM Engineering/Reliability Patterns]] · Permanent: [[03 Permanent Notes/Every LLM Call Needs an Escape Plan]] · [[03 Permanent Notes/Retries Need Jitter and Idempotency]]

### Domain 9 — Security, Safety, Governance

#### AI Security and Governance (Defense in Depth)
LLM security has to be a layered control system wrapped around the *entire* workflow — user input, data classification, retrieval, the model call, tool execution, output, and audit logs — because a rule enforced only at the prompt level cannot compensate for private data entering context in the first place, or an unauthorized document being retrieved before the model ever sees the prompt. The practical pattern: minimize PII before it reaches a prompt, enforce access-control filters before retrieval (not after), constrain what tools are allowed to do, and log every security-relevant decision as evidence.
Source: [[02 Literature Notes/LLM Engineering/AI Security and Governance]] · Permanent: [[03 Permanent Notes/Secure the AI Workflow Not Just the Prompt]]

#### Guardrails and Prompt Injection (Direct and Indirect)
Indirect prompt injection hides malicious instructions inside content the system retrieves on the model's behalf — a webpage, a PDF, an email, a support ticket — and works precisely because the model receives both the developer's legitimate instructions and this untrusted retrieved content as the same stream of tokens, so hostile data can attempt to impersonate authority. The layered fix: retrieve only from authorized sources, clearly delimit untrusted content as data (never as instructions) in the prompt, state explicit precedence rules, and scan both inputs and outputs for injection and leakage patterns.
Source: [[02 Literature Notes/LLM Engineering/Guardrails and Prompt Injection]] · Permanent: [[03 Permanent Notes/Indirect Prompt Injection Turns Retrieved Data Into Instructions]]

---

## Stage 6 — AI Solution Architecture & Production

> Weeks 19-22 of the FDE roadmap: taking an LLM-engineering system from notebook to a defensible, deployable, operable, and secure enterprise system.

### Reference AI Architectures Catalog
Eight reference shapes an AI architect should recognize on sight and pick the *smallest* one that actually satisfies the requirements: (1) a simple LLM call for bounded generation, (2) RAG when answers need grounding and freshness, (3) a single agent when the system must choose its own actions, (4) multi-agent/orchestrated workflows when roles are genuinely separable, (5) fine-tuned serving for stable, learnable behavior, (6) a hybrid of RAG + fine-tune + agent only once evals *prove* each piece helps, (7) evaluation-in-the-loop for continuous improvement, and (8) human-in-the-loop approval for high-risk or regulated actions. Reaching for (4) or (6) when (1) or (2) would do is one of the most common over-engineering mistakes in AI system design.
Source: [[02 Literature Notes/AI Architecture/AI Solution Architecture — Reference Patterns]] · Permanent: [[03 Permanent Notes/AI Week 19a Reference AI Architectures Catalog]]

### ADRs for AI Systems
An Architecture Decision Record captures one real decision (title, status, context, decision, consequences, alternatives considered and rejected) so a future incident reviewer can understand *why* the system was built a certain way, not just *that* it was. Good AI ADRs name specific real choices — Azure OpenAI vs Bedrock vs Vertex, RAG vs fine-tune, pgvector vs a managed vector database — and explicitly document the safety/operational consequences: the PII boundary, the evaluation gate, the fallback behavior, the audit trail, the cost budget, and who owns it.
Source: [[02 Literature Notes/AI Architecture/AI Solution Architecture — Reference Patterns]] · Permanent: [[03 Permanent Notes/AI Week 19a ADR Template for AI Systems]]

### Enterprise AI One-Pager Architecture
A reusable one-page structure for presenting an AI architecture to stakeholders: the clarified business problem, a current-state workflow summary, a future-state C4 Container diagram (showing trust boundaries, identity, data stores, model provider, guardrails, and observability), the key ADRs behind it, capacity/cost math at realistic scale, named failure modes, and a concrete hand-off package (ADRs, capacity sheet, risk register, eval plan, runbook). The point is that a useful architecture page is a *decision record with arithmetic and named risks*, not just a pretty diagram.
Source: [[02 Literature Notes/AI Architecture/AI Solution Architecture — Applied]] · Permanent: [[03 Permanent Notes/AI Week 19b Enterprise AI One-Pager Architecture Template]]

### Discovery-to-Architecture Playbook
The practical workflow for going from a vague customer ask to a defensible architecture: restate the ask in the customer's own language, discover users/workflow/pain/compliance constraints before touching a diagram, draw the *current* state before the future state, only choose specific architecture components once real constraints are visible, write ADRs for each major decision, do capacity math early enough to kill unrealistic designs before they're built, and name every failure mode with an owner and a runbook. The job is explicitly framed as making the customer's *next engineering decision* safer — not just producing an impressive-looking diagram.
Source: [[02 Literature Notes/AI Architecture/AI Solution Architecture — Applied]] · Permanent: [[03 Permanent Notes/AI Week 19b FDE Discovery to Architecture Playbook]]

### Cloud AI Platform Selection (Azure vs Bedrock vs Vertex)
The platform decision should start from residency, procurement, and existing governance (if a customer already has Azure landing zones and Entra ID governance, Azure AI Foundry is the default, independent of any specific model-quality benchmark) rather than starting from which model performs best on a leaderboard. Capacity itself is a product decision too: pay-as-you-go suits pilots and bursty traffic, while provisioned/reserved capacity (Azure PTU, Bedrock Provisioned Throughput) suits predictable SLOs — but idle reserved capacity is real wasted money, so this has to be sized against actual expected utilization.
Source: [[02 Literature Notes/AI Architecture/Cloud Architecture & Deployment — Reference Patterns]] · Permanent: [[03 Permanent Notes/AI Week 20a Cloud AI Platform Decision Guide]]

### Containers and Kubernetes for AI Services
A checklist of what actually matters when containerizing an AI service: a multi-stage Dockerfile with a pinned base image and no secrets baked in; a private, scanned container registry; Kubernetes readiness probes that specifically check the *dependencies* needed to serve traffic (for a RAG service, that means confirming the vector store and model route are actually reachable, not just that the process started); and dedicated GPU node pools sized and tainted correctly. The one-liner captures the key insight: a healthy AI pod isn't one that merely started — it's one that can actually retrieve, call the model, and honor its secrets.
Source: [[02 Literature Notes/AI Architecture/Cloud Architecture & Deployment — Reference Patterns]] · Permanent: [[03 Permanent Notes/AI Week 20a Container and Kubernetes Cheat Sheet for AI Services]]

### Azure Enterprise AI Deployment Reference
A worked reference topology for a production RAG assistant on Azure: Front Door + WAF into Container Apps running the API, Azure OpenAI for the model and embeddings, Postgres with `pgvector` for the index, Blob Storage for immutable audit logs, Entra ID for user identity and managed identity for the workload itself, Key Vault for secrets, private endpoints everywhere feasible, and Bicep-based infrastructure-as-code with staged CI/CD gates (tests, evals, image scanning, canary, rollback). This demonstrates that "deploying an AI system" is really "deploying a private, observable, parameterized distributed system" — the model endpoint is a small part of the whole picture.
Source: [[02 Literature Notes/AI Architecture/Cloud Architecture & Deployment — Applied]] · Permanent: [[03 Permanent Notes/AI Week 20b Azure Enterprise AI Deployment Reference]]

### Prompt/Model/Index Release Discipline
Every production AI behavior should be released as a three-part tuple — `(prompt_version, model_deployment, index_version)` — with each lane gated and rolled back *independently*. The prompt lane is gated by golden-answer evals; the model lane by latency/cost/refusal metrics; the index lane by retrieval recall and freshness checks. Without this separation, a single bad incident (say, a bad index rebuild) forces a full-system rollback of prompt, model, *and* index together — even though only one axis actually broke.
Source: [[02 Literature Notes/AI Architecture/Cloud Architecture & Deployment — Applied]] · Permanent: [[03 Permanent Notes/AI Week 20b Prompt Model Index Release Discipline]]

### AI SLO Design
AI Service Level Objectives need to be layered beyond ordinary service SLOs (availability, p95 latency): they also need AI-quality SLOs (e.g. groundedness ≥ 0.88, hallucination rate < 2%, unsafe-completion rate < 0.1%) and cost SLOs (cost per request, PTU utilization target). The error budget has to be sized across *both* axes — a 3-point drop in groundedness on a core workflow can burn more of the error budget than a brief latency spike — and the "golden set" used to measure quality needs ongoing refresh with real production questions and SME review, or its labels quietly rot out of date.
Source: [[02 Literature Notes/AI Architecture/LLMOps, Monitoring, Cost & Reliability — Reference Patterns]] · Permanent: [[03 Permanent Notes/AI Week 22a AI SLO Design Guide]]

### LLM Observability Attributes (OpenTelemetry)
A canonical, reusable set of OpenTelemetry span attributes for an LLM/RAG request — tenant ID, prompt version, model deployment, embedding model, index version, retrieved document IDs, token counts, cost, groundedness score, safety flags — each tagged with a sensitivity level, because several of these (retrieved doc IDs, safety flags) need careful handling to avoid becoming a PII leak in the observability pipeline itself. The sampling rule: capture 100% of errors, eval failures, and safety flags, but only a *sampled and PII-redacted* subset of otherwise-healthy traces.
Source: [[02 Literature Notes/AI Architecture/LLMOps, Monitoring, Cost & Reliability — Reference Patterns]] · Permanent: [[03 Permanent Notes/AI Week 22a LLM Observability Attribute Reference]]

### Customer SLO Contracts for Enterprise AI
A negotiated, customer-facing SLO contract covering service availability, AI quality (groundedness, hallucination rate, citation coverage measured against the *customer's own* golden set), and unit cost (cost per answered question) — with an error budget that spans all three dimensions and a monthly report showing the SLO table, incidents, and corrective actions. An example worked target: availability ≥ 99.5%, p95 latency ≤ 6s, groundedness ≥ 92%, cost ≤ $0.08 per answered question.
Source: [[02 Literature Notes/AI Architecture/LLMOps, Monitoring, Cost & Reliability — Applied]] · Permanent: [[03 Permanent Notes/AI Week 22b Customer SLO Contract for Enterprise AI]]

### Enterprise AI On-Call Runbooks
A compact runbook per AI-specific incident type — a groundedness drop, a cost spike, a latency regression, a safety-flag spike, a provider outage, a suspected prompt injection — each structured the same way: how to *detect* it, how to *mitigate* it immediately (which release-tuple lane to roll back), how to *communicate* impact to the customer, and how to *correct* the underlying gap (e.g. adding the failed case to the golden eval set so it's caught automatically next time). The discipline is that a runbook isn't actually done until it covers all four of those steps, not just the mitigation.
Source: [[02 Literature Notes/AI Architecture/LLMOps, Monitoring, Cost & Reliability — Applied]] · Permanent: [[03 Permanent Notes/AI Week 22b Enterprise AI On-Call Runbook Bundle]]

### Responsible AI and Governance Framework
Turning Responsible AI principles (fairness, reliability & safety, privacy & security, transparency, accountability) into actual engineering controls rather than leaving them as abstract values: fairness becomes stratified evals by demographic/use-case segment, transparency becomes citations and model cards, accountability becomes named owners and an immutable audit log. Minimum required artifacts for an enterprise review include a model card, a data card, a prompt registry with approval history, a tool registry, and (for high-risk workflows) a formal risk assessment.
Source: [[02 Literature Notes/AI Architecture/Security, Governance & Responsible AI — Reference Patterns]] · Permanent: [[03 Permanent Notes/AI Week 21a Enterprise AI Governance and Responsible AI Framework]]

### OWASP LLM Top 10
A standard checklist mapping the ten named LLM-specific threat categories (prompt injection, insecure output handling, training data poisoning, model denial of service, supply chain risk, sensitive information disclosure, insecure plugin/tool design, excessive agency, overreliance, model theft) to concrete engineering controls — e.g. prompt injection is countered by instruction hierarchy and retrieved-content sanitization, excessive agency is countered by narrow tool scopes and human-in-the-loop approval for risky actions. Each threat should map to a named control with a named owner and evidence in logs — "we thought about it" is not a control.
Source: [[02 Literature Notes/AI Architecture/Security, Governance & Responsible AI — Reference Patterns]] · Permanent: [[03 Permanent Notes/AI Week 21a OWASP LLM Top 10 Engineering Controls Map]]

### Enterprise AI Security Review Submission
The structure of a full Security Review Board packet for an enterprise AI system: system context and intended use, data classification (public/internal/confidential/PII) with a control for each class, a threat model combining STRIDE with the OWASP LLM Top 10 applied to the *actual* architecture, a trust-boundary diagram, and a control matrix mapping each threat to a control, an owner, and linked evidence — with the rule that "no owner or evidence means no go-live claim."
Source: [[02 Literature Notes/AI Architecture/Security, Governance & Responsible AI — Applied]] · Permanent: [[03 Permanent Notes/AI Week 21b Enterprise AI Security Review Submission Template]]

### Enterprise AI Go-Live Checklist
A concrete, evidence-based launch checklist spanning data (PII redact-before-embed, right-to-erasure tested), identity (least-privilege managed identity, no secrets in images), network (private endpoints, no public egress), audit (immutable storage, redacted telemetry), versioning (the prompt/model/index release tuple and a tested rollback drill), evals (golden eval green, drift/safety/cost alerts live), governance (model card, data card, risk assessment signed off), and red-teaming (injection and PII-exfiltration attempts specifically tested, not just a generic pen test). Traffic only moves to 100% once every blocking item on this list is green — the whole point is to make go-live an evidenced risk decision rather than an optimistic deployment.
Source: [[02 Literature Notes/AI Architecture/Security, Governance & Responsible AI — Applied]] · Permanent: [[03 Permanent Notes/AI Week 21b Enterprise AI Go-Live Checklist]]

---

## Capstone Projects

### Autonomous Driving
Applies computer vision and deep learning (CNNs, object detection) to an autonomous-driving perception problem — framing driving-related predictions as an ML/CV task and carrying it through the full workflow from data to evaluated results. Consolidates the CNN, transfer learning, and object detection material from Stage 3.
Source: [[02 Literature Notes/Courses/Capstone - Project Autonomous Driving]]

### Preserving Heritage and Enhancing Tourism with AI
Applies classification and recommendation techniques to a cultural-heritage and tourism domain, balancing raw model performance against real-world usefulness for the actual audience the system serves. Consolidates classical ML and applied data science material from Stages 1-2.
Source: [[02 Literature Notes/Courses/Capstone - Project Heritage Tourism with AI]]

### Sales Forecasting
Frames sales forecasting as a supervised/time-series regression problem, with feature engineering specifically for temporal data (trend, seasonality) and forecast accuracy evaluated with appropriate error metrics. Consolidates statistics, regression, and data-wrangling material from Stages 1-2.
Source: [[02 Literature Notes/Courses/Capstone - Project Sales Forecasting]]

---

## How to Use This Map

This is a flattened, chronological read-through index — for the underlying hierarchical structure (course → lesson → permanent note → code snippet → project), see the individual concept maps linked at the top of this note. Work through the stages in order; each stage assumes the vocabulary and tools introduced in the ones before it.
