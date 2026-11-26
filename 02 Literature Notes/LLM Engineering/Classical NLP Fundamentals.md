# Classical NLP Fundamentals

> Topic package — Domain 1 (Data Representation) · pre-LLM foundations.
> Depth goal: understand the classical NLP preprocessing pipeline (stemming, lemmatization, POS tagging, syntactic analysis) that predates subword tokenization and transformer-based language models — know what these techniques actually do, why most LLM pipelines no longer need them, and where they still genuinely matter.

## Source
- Track: LLM Engineering (self-directed, FDE roadmap)
- Reference reading: Jurafsky & Martin, Speech and Language Processing (NLP foundations); spaCy and NLTK documentation; Porter stemming algorithm (Porter 1980)
- Builds on: nothing upstream — this is pre-transformer foundational material
- Downstream: [[02 Literature Notes/LLM Engineering/Tokenization]] (modern subword tokenization supersedes most of this pipeline for LLM input, but the underlying linguistic concepts still matter for classical ML text pipelines and for understanding what LLMs implicitly learned to do without being told)
- Date: 2026-11-26

---

## 1. Mental Model

**Classical NLP normalizes and structurally annotates text *before* a model ever sees it — reducing words to canonical forms and labeling their grammatical role — because pre-transformer models (bag-of-words, TF-IDF, classical ML classifiers) have no way to learn these regularities themselves.** A bag-of-words model treats "running," "ran," and "runs" as three completely unrelated tokens unless you explicitly reduce them to a shared root first; it has no mechanism to discover on its own that these three strings refer to related forms of the same underlying concept.

This is fundamentally different from how modern subword tokenization + transformer models handle the same problem: a transformer learns distributional relationships between word forms directly from massive training data (it implicitly learns that "running"/"ran"/"runs" behave similarly in context, through its embeddings and attention, without anyone pre-processing the text to tell it so). Classical NLP preprocessing is the explicit, hand-engineered version of normalization that transformers now get to skip — understanding it is what lets you recognize *why* certain modern techniques exist (subword tokenization, covered in [[02 Literature Notes/LLM Engineering/Tokenization]], is in part a more general, learned solution to the same "related word forms" problem stemming and lemmatization were built to solve by hand).

> Key intuition: **stemming/lemmatization/POS tagging are manual feature engineering for text, the same way scaling and encoding are manual feature engineering for tabular data** (covered in [[02 Literature Notes/LLM Engineering/Embeddings]]'s predecessor concepts) — a transformer-based LLM learns equivalent structure implicitly from data instead of having it imposed by a hand-built rule or algorithm.

---

## 2. How It Actually Works

### 2.1 Stemming
**Stemming** crudely chops words down to a root form using rule-based suffix-stripping, without any real understanding of grammar or meaning — the classic **Porter stemmer** applies a sequence of mechanical suffix-removal rules ("running" → "run" by stripping "-ning"; "flies" → "fli" by stripping "-es," producing a root that isn't even a real word). Stemming is fast and purely algorithmic, but it's blunt: it can over-stem (reducing unrelated words to the same root by coincidence of suffix pattern) or under-stem (failing to unify genuinely related words whose surface forms don't share a common suffix pattern the rules anticipate), and the resulting "stem" is frequently not a valid dictionary word at all.

### 2.2 Lemmatization
**Lemmatization** instead reduces a word to its genuine dictionary base form (its **lemma**) using actual vocabulary and grammatical knowledge, not blind suffix-stripping — "ran" → "run," "better" → "good" (irregular forms lemmatization can resolve that stemming's suffix-stripping rules structurally cannot, since there's no shared suffix pattern linking "better" to "good," or "ran" to "run," at all). Lemmatization requires knowing the word's **part of speech** to resolve these correctly — "better" only lemmatizes to "good" when tagged as an adjective (the comparative form of "good"); tagged as a verb, "better" means something else entirely ("to better oneself"), with a different, unrelated lemma. This is why lemmatization is slower and more complex than stemming (it needs a dictionary and grammatical context) but produces more linguistically accurate, genuinely interpretable results — and also why real lemmatizers vary in coverage: even standard tools don't correctly resolve every irregular form (NLTK's WordNet lemmatizer, for instance, correctly reduces "ran"/"ate"/"went" to "run"/"eat"/"go," but fails to resolve "saw" to "see," leaving it unchanged — a genuine, checkable gap in that specific tool's irregular-verb coverage, not a universal property of lemmatization itself).

### 2.3 Part-of-speech (POS) tagging
**POS tagging** labels every word in a sentence with its grammatical role — noun, verb, adjective, determiner, and so on. This is a genuinely harder problem than it first appears because of pervasive ambiguity: the same word form can be different parts of speech depending entirely on context ("book" is a noun in "read a book" but a verb in "book a flight"). Classical POS taggers use statistical models (Hidden Markov Models, Conditional Random Fields) trained to predict the most likely tag sequence given both the word itself and the tags of surrounding words — resolving ambiguity using context, the same underlying intuition (meaning depends on surrounding context) that attention mechanisms in transformers later generalized far more powerfully.

### 2.4 Syntactic analysis (parsing)
**Syntactic analysis** goes one level beyond flat POS tags, building an actual structural tree of how words relate grammatically to each other in a sentence — which word is the subject, which is the main verb, which phrase modifies which other phrase. **Constituency parsing** breaks a sentence into nested phrase structures (noun phrases, verb phrases); **dependency parsing** instead draws direct grammatical links between words (a verb's subject, a noun's modifying adjective), without requiring the nested-phrase tree structure constituency parsing builds. Syntactic structure matters for tasks that depend on relationships between distant words in a sentence, not just the words in isolation — extracting "who did what to whom" from a sentence genuinely requires knowing the grammatical relationships, not just which words appeared.

### 2.5 Why LLMs mostly made this pipeline optional
Modern LLMs operate on subword tokens (BPE/WordPiece/Unigram, covered in [[02 Literature Notes/LLM Engineering/Tokenization]]) and learn contextual representations directly through massive-scale training — they implicitly learn that "running"/"ran"/"runs" share meaning-relevant structure, that "saw" means something different as a verb versus a noun depending on context, and effectively internalize syntactic relationships, all without anyone explicitly stemming, lemmatizing, POS-tagging, or parsing the input text first. The explicit preprocessing pipeline that classical NLP needed becomes largely redundant once a model is large enough and trained on enough data to learn these regularities on its own, directly from raw (tokenized, not lemmatized) text.

This doesn't make classical NLP preprocessing obsolete everywhere, though: classical ML text pipelines (TF-IDF + logistic regression for a lightweight spam filter, say) still benefit from stemming/lemmatization, since a bag-of-words-style representation has no mechanism to learn word-form relationships on its own the way a transformer does — if you're not using a transformer, you still need to hand-engineer the normalization a transformer would otherwise learn implicitly. Lemmatization also remains useful as an interpretability/search tool even in LLM-adjacent pipelines — normalizing query terms for exact-match keyword search (distinct from semantic vector search) still benefits from reducing "running"/"ran"/"runs" to one canonical form so a keyword search doesn't miss relevant documents purely due to surface-form mismatch.

---

## 3. Implementation

Assumed stack: `nltk` (classical NLP toolkit with Porter stemmer, WordNet lemmatizer, POS tagger).

### Stemming vs. Lemmatization Side-by-Side
```python
from nltk.stem import PorterStemmer, WordNetLemmatizer

stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

words = ["running", "ran", "runs", "better", "flies", "studies"]

for w in words:
    stem = stemmer.stem(w)
    lemma = lemmatizer.lemmatize(w, pos="v")  # pos hint matters -- try pos="a" for "better" below
    print(f"{w:>10}  stem={stem:<10}  lemma={lemma}")

# "better" stays "better" when lemmatized as a verb (pos="v") -- it's only the
# irregular comparative of "good" when used as an adjective:
print("better (adj) ->", lemmatizer.lemmatize("better", pos="a"))  # -> "good"
```

### POS Tagging and Disambiguating "saw"
```python
import nltk
from nltk import pos_tag, word_tokenize

sentences = ["The saw is on the table.", "I saw a movie yesterday."]
for s in sentences:
    tagged = pos_tag(word_tokenize(s))
    saw_tag = [tag for word, tag in tagged if word.lower() == "saw"]
    print(s, "->", tagged, "| 'saw' tagged as:", saw_tag)
# Same surface word "saw" resolves to a different POS tag (NN noun, cutting tool,
# vs VBD past-tense verb) depending purely on its sentence context. Not every
# ambiguous word reliably disambiguates this cleanly with a simple statistical
# tagger -- sentence-initial imperatives (e.g. "Please book a flight") can
# confuse a basic tagger; always verify against your actual sentences rather
# than assuming any textbook example generalizes.
```

---

## 4. Design Decisions & Tradeoffs

| Decision | Guidance |
|---|---|
| **Stemming vs. lemmatization** | Stemming when speed matters more than linguistic accuracy and false merges are tolerable (quick keyword search indexing); lemmatization when you need genuinely correct base forms (any pipeline where results are shown to a human). |
| **Classical preprocessing vs. transformer embeddings** | Use classical preprocessing only when the downstream model is itself classical (bag-of-words, TF-IDF, non-transformer); a transformer-based pipeline should feed it raw (tokenized) text, not pre-stemmed/lemmatized text, since stemming destroys information the transformer could otherwise use. |
| **POS tagging granularity** | Use flat POS tags when you only need word-level grammatical role; use full dependency/constituency parsing when the task needs relationships between words, not just their individual roles. |
| **Keyword search normalization** | Lemmatize query and document terms for exact-match keyword search even in an otherwise LLM-centric pipeline — semantic vector search doesn't need this, but keyword/BM25-style search still does. |

---

## 5. Failure Modes & Gotchas

- Feeding stemmed or lemmatized text into a transformer-based LLM or embedding model — this destroys information (surface form, inflection) the model could otherwise use, and transformers expect to see natural, unprocessed text.
- Treating stemming's output as if it were a real word, when a Porter-stemmed root is frequently not a valid dictionary word at all (a cosmetic/display bug if ever shown to a user).
- Lemmatizing without a POS hint, causing ambiguous words to resolve incorrectly (a lemmatizer that doesn't know "better" is an adjective in this sentence may fail to reduce it to "good").
- Assuming a specific lemmatizer's irregular-form coverage is complete without checking — even correctly POS-tagged input can still fail silently on a specific tool's exception-list gaps (e.g. NLTK's WordNet lemmatizer leaves "saw" unresolved as a verb).
- Assuming classical POS tagging or parsing is needed for a modern transformer-based pipeline, when the transformer has already implicitly learned equivalent structure — adding classical NLP preprocessing in front of an LLM call is usually solving a problem the LLM doesn't actually have.
- Using stemming for anything user-facing (search result highlighting, display text) where the crude, sometimes non-word stem would look obviously wrong to a human reader.

---

## 6. Self-Check

1. Why does stemming sometimes produce a string that isn't a real word, while lemmatization never does?
2. Why does lemmatizing "better" correctly require knowing its part of speech?
3. Why did subword tokenization + transformers make most of this preprocessing pipeline unnecessary for LLM input specifically?
4. Give one concrete pipeline where classical NLP preprocessing is still genuinely useful today.
5. What's the structural difference between POS tagging and full syntactic parsing?

---

## 7. Interview Q&A

**Q: Why does stemming sometimes produce output that isn't even a real word, while lemmatization never does?**
A: Stemming is a purely mechanical process — it applies a fixed sequence of suffix-stripping rules to a word's surface form, with no reference to an actual dictionary or any understanding of what the word genuinely means. The Porter stemmer, for instance, strips common suffix patterns ("-ing," "-es," "-ed") based purely on the characters present, regardless of whether what's left over after stripping is an actual, valid word — "flies" losing its "-es" suffix produces "fli," which isn't a real English word at all, but the rule doesn't know or care about that; it's just following a mechanical pattern-matching procedure.

Lemmatization, by contrast, is defined specifically as "reduce this word to its real dictionary base form" — it looks the word up (using a lexical resource like WordNet, combined with the word's part of speech to resolve ambiguity) and returns whatever that dictionary's actual canonical form for the word is. Since its entire definition is "return a genuine word," it structurally cannot produce a non-word as output the way stemming's blind suffix-stripping can — the tradeoff is that this requires a real dictionary lookup and grammatical context, making lemmatization slower and more complex to implement than stemming's simple rule-application.

*One-liner: stemming blindly strips suffixes by pattern-matching rules with no reference to whether the result is a real word, which is exactly why it can produce non-words like "fli" from "flies" — lemmatization looks words up against an actual dictionary using their part of speech, so by definition it always returns a genuine word, at the cost of needing real lexical and grammatical resources that stemming's pure rule-application doesn't.*

**Q: Why does correctly lemmatizing a word like "better" require knowing its part of speech first, and what happens when a real lemmatizer's irregular-form coverage is incomplete?**
A: "Better" is genuinely ambiguous in isolation — as an adjective, it's the irregular comparative form of "good" ("this one is better"), with a completely different surface form than its base lemma; as a verb, it means something unrelated ("to better oneself," whose lemma is just "better," unchanged, since that's already the verb's base form). These two uses need different lemmatization rules applied, and the bare string "better" with no grammatical context gives a lemmatizer no principled way to know which rule applies — it's not that the correct answer is hard to compute, it's that "what's the lemma of 'better'" is underspecified without knowing whether you mean the adjective or the verb use. This is exactly why real lemmatization pipelines run POS tagging *before* lemmatization and feed the resulting tag in as a required hint, rather than lemmatizing bare, untagged words.

A separate, important caveat worth internalizing: even once you supply the correct POS tag, a real lemmatizer's coverage of irregular forms can still be incomplete — NLTK's WordNet lemmatizer, for instance, correctly resolves "ran"/"ate"/"went" to their base verbs "run"/"eat"/"go" when tagged as verbs, but fails to resolve "saw" to "see" under the same conditions, instead leaving it unchanged. This isn't a flaw in the *concept* of lemmatization (a complete lexical resource genuinely could resolve "saw"→"see" given the right verb tag) — it's a gap in one specific tool's irregular-verb exception list, and it's exactly the kind of claim worth actually testing against the tool you're using rather than assuming every textbook example works, since "lemmatization resolves irregular forms" is true in principle but not uniformly true in every implementation.

*One-liner: "better" has genuinely different correct lemmas depending on whether it's an adjective ("good") or a verb (unchanged) — which is why lemmatization needs a POS tag as input, not just the bare word; but even with the correct tag supplied, don't assume a specific lemmatizer's irregular-form coverage is complete (NLTK's WordNet lemmatizer handles "ran"→"run" correctly but silently fails on "saw"→"see"), which is worth verifying against your actual tool rather than trusting the general claim uncritically.*

**Q: Why did subword tokenization plus transformer-based LLMs make most of the classical NLP preprocessing pipeline (stemming, lemmatization, POS tagging) unnecessary for LLM input specifically?**
A: Classical preprocessing exists to manually impose structure that a classical model (bag-of-words, TF-IDF, a simple feed-forward classifier) has no mechanism to learn on its own — these older models see each distinct word-form as a completely separate, unrelated feature, so without stemming/lemmatization to manually unify "running"/"ran"/"runs" into one shared representation, the model would never discover on its own that these forms are related, since it has no way to learn relationships between input features from their surface form alone.

A transformer-based LLM is a fundamentally different kind of model: it learns dense, contextual representations (embeddings, refined through attention across massive training corpora) where semantically and grammatically related words naturally end up with similar representations, purely as an emergent consequence of how it was trained — "running," "ran," and "runs" end up with related embeddings not because anyone told the model they're related, but because the model has seen enough real text to learn that these forms behave similarly in context. Similarly, a transformer implicitly learns to disambiguate "saw" as a verb versus a noun from surrounding context through attention, achieving (and typically exceeding) what explicit POS tagging was manually built to accomplish, without anyone running a separate POS-tagging step before feeding text to the model.

Because the model learns this structure directly and implicitly from data at training time, explicitly pre-processing the input text to manually impose the same structure not only becomes redundant, it's actively counterproductive — stemming/lemmatizing input before it reaches a transformer destroys surface-form information (tense, number, exact wording) the model was trained to use, and that the model can use far more effectively through its learned representations than any hand-built preprocessing rule could approximate.

*One-liner: classical preprocessing manually imposes structure (word-form unification, grammatical role) that a classical model has no way to learn itself — a transformer learns equivalent (and richer) structure directly and implicitly from massive training data through its embeddings and attention, which is exactly why feeding it pre-stemmed or pre-lemmatized text is not just unnecessary but actively destroys information the model is better equipped to use in its original, unprocessed form.*

**Q: Give a concrete, current pipeline where classical NLP preprocessing (stemming or lemmatization specifically) is still genuinely useful, even in an LLM-centric system.**
A: Exact-match keyword search (BM25-style or a simple inverted index), run alongside semantic vector search in a hybrid retrieval system, is a concrete, current case where lemmatization still earns its keep. Semantic vector search (embedding-based, covered in [[02 Literature Notes/LLM Engineering/Embeddings]]) doesn't need lemmatization at all — a good embedding model already captures that "running" and "ran" are semantically related, the same implicit-learning argument that makes classical preprocessing unnecessary for transformer input generally.

But a keyword-based index built on exact string matching has exactly the same blind spot classical bag-of-words models had: if a user searches for "running shoes" and a relevant document only contains the word "ran" (as in, "customers ran in these shoes for marathon training"), an exact-match keyword search with no normalization step would miss that document entirely, purely because "running" and "ran" are different literal strings — it's not doing any semantic reasoning at all, just literal string matching. Lemmatizing both the indexed documents and incoming queries to a shared canonical form before building the keyword index directly fixes this specific blind spot, letting the keyword-search side of a hybrid retrieval pipeline catch matches that differ only by inflection, which it would otherwise structurally miss.

*One-liner: lemmatization remains genuinely useful in a hybrid retrieval pipeline's keyword-search half specifically, since exact-match/BM25-style search has no semantic reasoning of its own and will miss a relevant document purely because of surface-form mismatch ("ran" vs. "running") — the semantic vector-search half of the same pipeline doesn't need this, since embedding models already implicitly capture those relationships, which is exactly why this gap is specific to the keyword-matching side, not retrieval in general.*

## 8. Links
- Domain MOC: [[06 Maps of Content/LLM Engineering Concepts]]
- Downstream: [[02 Literature Notes/LLM Engineering/Tokenization]] (modern subword tokenization as the generalized, learned successor to this manual pipeline), [[02 Literature Notes/LLM Engineering/Embeddings]] (semantic vector search sidesteps the keyword-matching gap classical NLP's lemmatization was built to solve)
