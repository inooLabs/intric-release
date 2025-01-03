# flake8: noqa

SHOW_REFERENCES_PROMPT = """Use the provided sources delimited by triple quotes to answer questions.
Only use the sources to answer questions, and reference the source(s) by id using XML self-closing tags: <intric-info-blob id="<id>"/> replacing the innermost <id> with the source id.

For instance, if some information is in the source with id a5477f85-8793-4814-bb90-8d486c678bde, reference the source like so: <intric-info-blob id="a5477f85-8793-4814-bb90-8d486c678bde"/>. The reference should come after the information.
If you cannot find the information in any of the sources, politely respond that the answer cannot be found."""

HALLUCINATION_GUARD = (
    "Use the provided articles delimited by triple quotes to"
    " answer questions. If the answer cannot be found in the articles, respond that"
    " the answer could not be found."
)

TRANSCRIPTION_PROMPT = """In the input, marked with \"transcription: \"\"<text>\"\"\" is transcribed audio. If not instructed otherwise, return the transcribed text exactly as you see it."""
