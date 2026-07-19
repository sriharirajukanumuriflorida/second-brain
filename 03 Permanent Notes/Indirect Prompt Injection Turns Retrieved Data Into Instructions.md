# Indirect Prompt Injection Turns Retrieved Data Into Instructions

Indirect prompt injection hides malicious instructions in content an LLM app retrieves: webpages, PDFs, emails, tickets, calendar invites, or tool outputs. The attack works because the model receives both developer instructions and untrusted content as tokens, so hostile data attempts to become authority.

The fix is layered: retrieve only authorized data, delimit and spotlight untrusted context, state precedence in the prompt contract, scan for injection patterns, permission tools outside the model, and filter outputs for leakage.

> One-liner: **untrusted content can inform the answer but must never control the system**.


Related: [[02 Literature Notes/LLM Engineering/Guardrails and Prompt Injection]] · [[02 Literature Notes/LLM Engineering/Prompt Contracts]]
