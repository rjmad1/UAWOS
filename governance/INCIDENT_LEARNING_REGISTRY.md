# Incident Learning Registry

## Post-Mortems and Learnings

### INC-01 - 2026-06-11: Virtualenv dashboard daemon crash loop due to syntax error in dspy-ai dependency.
- **Root Cause:** Syntax IndentationError in third-party library signature.py file.
- **Immediate Action Taken:** Removed accidental classmethod decorator from ensure_signature module-level function.
- **Preventative Actions:** Execute dependency verification checks and check import syntaxes before starting backend daemons.


*Last updated: 2026-06-12T14:34:09+0530*
