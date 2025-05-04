PROMPT_TEMPLATE = """
You are vetting a Wikipedia page to decide if it really records a FIRST-TIME
*scientific discovery or invention* that changed what scientists could DO or
UNDERSTAND.

Return EXACTLY three tokens, separated by dashes:
  is_discovery - year - is_person

------------ What COUNTS ------------
• Isolation / synthesis of a brand-new substance
• Landmark experiment revealing a new physical or biological phenomenon
• First clear proof of a theory (experimentally or observationally)
• Invention of a tool or device only if it directly enabled new
  scientific results (e.g. x-ray tube, electron microscope)

------------ What does NOT count ------------
• Named theorems, or purely mathematical results
• Broad subjects, instruments, or techniques (e.g. “Physics”, “Microscope”)
• Generic devices that are mainly engineering or consumer tech
• Lists, timelines, glossaries, taxonomies
• Stretch of geologic time or group of organisms
• Biographies (if the page is mainly about a person)

------------ Output rules ------------
• is_discovery  : “true” or “false”
• year          : first 4-digit year mentioned, or “unknown”
• is_person     : “true” if the page is a biography, else “false”
• Everything must be lowercase; no spaces.

------------ Page excerpt ------------
{intro}
--------------------------------------
Examples
  Oxygen was first isolated in 1774 …      → true-1774-false
  DNA double helix model (1953) …          → true-1953-false
  The electron microscope (1931) …         → true-1931-false
  Photosynthesis is the process …          → false-unknown-false
  Dogs are a domestic species …            → false-unknown-false
  Marie Curie (born 1867) …                → false-unknown-true
"""



PROMPT_TEMPLATE = """
You are a strict science history curator.

Return exactly three tokens separated by dashes:
  is_discovery - year - is_person

If the page is about a biological creature, time-period,
or a broad discipline/tool, output: false-unknown-false.

Else decide whether it describes a *specific* discovery/invention:
  • new substance isolated / phenomenon first observed
  • landmark experiment / pivotal technique or database

If yes -> is_discovery=true and year = first year mentioned.
If the year is missing, write "unknown".

If the text is a biography, set is_person=true.
"""







