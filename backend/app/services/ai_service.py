import re
from collections import Counter
from typing import Optional

from sqlalchemy.orm import Session

from app import models


# ============================================================
# BASIC TEXT HELPERS
# ============================================================

def tokenize(text: str) -> list[str]:
    if not text:
        return []

    return re.findall(
        r"\b[a-zA-Z0-9]+\b",
        text.lower()
    )


def clean_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\x00", " ")
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def normalize(text: str) -> str:
    if not text:
        return ""

    text = text.lower()

    replacements = {
        "–": "-",
        "—": "-",
        "/": " ",
        "&": " and ",
        ".": "",
        ",": " ",
        ":": " "
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# INTENT
# ============================================================

INTENT_KEYWORDS = {
    "eligibility": [
        "eligible",
        "eligibility",
        "who can participate"
    ],

    "registration_fee": [
        "registration fee",
        "registration fees",
        "fee",
        "fees",
        "cost",
        "charges"
    ],

    "team_size": [
        "team size",
        "team members",
        "how many students",
        "number of members"
    ],

    "deadline": [
        "deadline",
        "last date",
        "registration deadline",
        "register by"
    ],

    "prize": [
        "prize",
        "prizes",
        "prize pool",
        "cash prize",
        "winning amount"
    ],

    "registration_link": [
        "registration link",
        "register link",
        "registration form",
        "registration url"
    ],

    "attendance": [
        "attendance",
        "minimum attendance",
        "attendance requirement"
    ],

    "scholarship": [
        "scholarship",
        "scholarships"
    ]
}


def detect_intent(question: str) -> Optional[str]:
    q = question.lower()

    for intent, keywords in INTENT_KEYWORDS.items():
        for keyword in keywords:
            if keyword in q:
                return intent

    return None


# ============================================================
# EXAM DETECTION
# ============================================================

def is_exam_question(question: str) -> bool:
    q = question.lower()

    keywords = [
        "exam",
        "exams",
        "examination",
        "examinations",
        "sessional",
        "exam date",
        "exam dates",
        "exam schedule",
        "examination date",
        "examination dates",
        "examination schedule"
    ]

    return any(
        keyword in q
        for keyword in keywords
    )


# ============================================================
# EXAM DETAILS
# ============================================================

def detect_exam_details(question: str) -> dict:
    q = question.lower()

    result = {
        "course": None,
        "branch": None,
        "semester": None,
        "exam_type": None
    }

    # --------------------------------------------------------
    # COURSE
    # --------------------------------------------------------

    if re.search(r"\bb[\s.-]*tech\b", q):
        result["course"] = "btech"

    elif re.search(r"\bm[\s.-]*tech\b", q):
        result["course"] = "mtech"

    elif re.search(r"\bb[\s.-]*ca\b", q):
        result["course"] = "bca"

    elif re.search(r"\bm[\s.-]*ca\b", q):
        result["course"] = "mca"

    # --------------------------------------------------------
    # BRANCH
    # --------------------------------------------------------

    branch_patterns = [
        (r"\ba\s*\.?\s*i\s*\.?\s*m\s*\.?\s*l\b", "aiml"),
        (r"\baiml\b", "aiml"),

        (r"\baids\b", "aids"),
        (r"\bai\s+and\s+ds\b", "aids"),
        (r"\bartificial\s+intelligence\s+and\s+data\s+science\b", "aids"),

        (r"\bcse\b", "cse"),
        (r"\bcomputer\s+science\b", "cse"),

        (r"\bece\b", "ece"),
        (r"\belectronics\s+and\s+communication\b", "ece"),

        (r"\bit\b", "it"),
        (r"\binformation\s+technology\b", "it"),

        (r"\bmechanical\b", "me"),
        (r"\bme\b", "me"),

        (r"\bcivil\b", "civil"),

        (r"\beee\b", "eee"),
        (r"\belectrical\s+and\s+electronics\b", "eee")
    ]

    for pattern, branch in branch_patterns:
        if re.search(pattern, q):
            result["branch"] = branch
            break

    # --------------------------------------------------------
    # SEMESTER
    # --------------------------------------------------------

    semester_patterns = [
        (r"\b1st\s+semester\b", "i"),
        (r"\bfirst\s+semester\b", "i"),
        (r"\bi\s+semester\b", "i"),
        (r"\bsemester\s+i\b", "i"),
        (r"\bsemester\s+1\b", "i"),

        (r"\b2nd\s+semester\b", "ii"),
        (r"\bsecond\s+semester\b", "ii"),
        (r"\bii\s+semester\b", "ii"),
        (r"\bsemester\s+ii\b", "ii"),
        (r"\bsemester\s+2\b", "ii"),

        (r"\b3rd\s+semester\b", "iii"),
        (r"\bthird\s+semester\b", "iii"),
        (r"\biii\s+semester\b", "iii"),
        (r"\bsemester\s+iii\b", "iii"),
        (r"\bsemester\s+3\b", "iii"),

        (r"\b4th\s+semester\b", "iv"),
        (r"\bfourth\s+semester\b", "iv"),
        (r"\biv\s+semester\b", "iv"),
        (r"\bsemester\s+iv\b", "iv"),
        (r"\bsemester\s+4\b", "iv"),

        (r"\b5th\s+semester\b", "v"),
        (r"\bfifth\s+semester\b", "v"),
        (r"\bv\s+semester\b", "v"),
        (r"\bsemester\s+v\b", "v"),
        (r"\bsemester\s+5\b", "v"),

        (r"\b6th\s+semester\b", "vi"),
        (r"\bsixth\s+semester\b", "vi"),
        (r"\bvi\s+semester\b", "vi"),
        (r"\bsemester\s+vi\b", "vi"),
        (r"\bsemester\s+6\b", "vi"),

        (r"\b7th\s+semester\b", "vii"),
        (r"\bseventh\s+semester\b", "vii"),
        (r"\bvii\s+semester\b", "vii"),
        (r"\bsemester\s+vii\b", "vii"),
        (r"\bsemester\s+7\b", "vii"),

        (r"\b8th\s+semester\b", "viii"),
        (r"\beighth\s+semester\b", "viii"),
        (r"\bviii\s+semester\b", "viii"),
        (r"\bsemester\s+viii\b", "viii"),
        (r"\bsemester\s+8\b", "viii")
    ]

    for pattern, semester in semester_patterns:
        if re.search(pattern, q):
            result["semester"] = semester
            break

    # --------------------------------------------------------
    # EXAM TYPE
    # --------------------------------------------------------

    if (
        "second sessional" in q
        or "2nd sessional" in q
    ):
        result["exam_type"] = "second sessional"

    elif (
        "first sessional" in q
        or "1st sessional" in q
    ):
        result["exam_type"] = "first sessional"

    elif (
        "mid term" in q
        or "mid-term" in q
        or "midterm" in q
    ):
        result["exam_type"] = "mid term"

    elif (
        "end semester" in q
        or "end sem" in q
    ):
        result["exam_type"] = "end semester"

    return result


# ============================================================
# METADATA MATCHING
# ============================================================

def course_matches(
    text: str,
    course: Optional[str]
) -> bool:

    if not course:
        return True

    text = normalize(text)

    if course == "btech":
        return (
            "btech" in text
            or "b tech" in text
        )

    if course == "mtech":
        return (
            "mtech" in text
            or "m tech" in text
        )

    if course == "bca":
        return (
            "bca" in text
            or "b ca" in text
        )

    if course == "mca":
        return (
            "mca" in text
            or "m ca" in text
        )

    return False


def branch_matches(
    text: str,
    branch: Optional[str]
) -> bool:

    if not branch:
        return True

    text = normalize(text)

    aliases = {
        "aiml": [
            "aiml",
            "ai ml",
            "artificial intelligence machine learning",
            "artificial intelligence and machine learning"
        ],

        "aids": [
            "aids",
            "ai ds",
            "artificial intelligence data science",
            "artificial intelligence and data science"
        ],

        "cse": [
            "cse",
            "computer science"
        ],

        "ece": [
            "ece",
            "electronics communication"
        ],

        "it": [
            "information technology"
        ],

        "me": [
            "mechanical"
        ],

        "civil": [
            "civil"
        ],

        "eee": [
            "eee",
            "electrical electronics"
        ]
    }

    return any(
        alias in text
        for alias in aliases.get(
            branch,
            [branch]
        )
    )


def semester_matches(
    text: str,
    semester: Optional[str]
) -> bool:

    if not semester:
        return True

    text = normalize(text)

    aliases = {
        "i": [
            "i semester",
            "1st semester",
            "first semester"
        ],

        "ii": [
            "ii semester",
            "2nd semester",
            "second semester"
        ],

        "iii": [
            "iii semester",
            "3rd semester",
            "third semester"
        ],

        "iv": [
            "iv semester",
            "4th semester",
            "fourth semester"
        ],

        "v": [
            "v semester",
            "5th semester",
            "fifth semester"
        ],

        "vi": [
            "vi semester",
            "6th semester",
            "sixth semester"
        ],

        "vii": [
            "vii semester",
            "7th semester",
            "seventh semester"
        ],

        "viii": [
            "viii semester",
            "8th semester",
            "eighth semester"
        ]
    }

    return any(
        alias in text
        for alias in aliases.get(
            semester,
            [semester]
        )
    )


def exam_type_matches(
    text: str,
    exam_type: Optional[str]
) -> bool:

    if not exam_type:
        return True

    text = normalize(text)

    if exam_type == "second sessional":
        return (
            "second sessional" in text
            or "2nd sessional" in text
        )

    if exam_type == "first sessional":
        return (
            "first sessional" in text
            or "1st sessional" in text
        )

    if exam_type == "mid term":
        return (
            "mid term" in text
            or "midterm" in text
        )

    if exam_type == "end semester":
        return (
            "end semester" in text
            or "end sem" in text
        )

    return False


# ============================================================
# DATABASE CHUNK HELPERS
# ============================================================

def get_document_chunks(
    db: Session,
    document_id: int
):
    return (
        db.query(models.DocumentChunk)
        .filter(
            models.DocumentChunk.document_id
            == document_id
        )
        .order_by(
            models.DocumentChunk.chunk_index.asc()
        )
        .all()
    )


def get_context(
    chunks,
    position: int,
    radius: int = 4
) -> str:

    if not chunks:
        return ""

    start = max(
        0,
        position - radius
    )

    end = min(
        len(chunks),
        position + radius + 1
    )

    return "\n".join(
        chunk.content
        for chunk in chunks[start:end]
        if chunk.content
    )


# ============================================================
# EXAM SCORING
# ============================================================

def score_exam_context(
    text: str,
    details: dict
) -> int:

    if not text:
        return 0

    score = 0
    normalized = normalize(text)

    if details["course"]:
        if course_matches(
            normalized,
            details["course"]
        ):
            score += 10

    if details["branch"]:
        if branch_matches(
            normalized,
            details["branch"]
        ):
            score += 10

    if details["semester"]:
        if semester_matches(
            normalized,
            details["semester"]
        ):
            score += 10

    if details["exam_type"]:
        if exam_type_matches(
            normalized,
            details["exam_type"]
        ):
            score += 10

    if "examination schedule" in normalized:
        score += 3

    if "sessional examination" in normalized:
        score += 3

    if "october 2026" in normalized:
        score += 2

    return score


# ============================================================
# EXAM RETRIEVAL
# ============================================================

def retrieve_exam_contexts(
    db: Session,
    question: str
) -> list[str]:

    details = detect_exam_details(
        question
    )

    documents = (
        db.query(models.CollegeDocument)
        .order_by(
            models.CollegeDocument.id.desc()
        )
        .all()
    )

    candidates = []

    for document in documents:

        chunks = get_document_chunks(
            db,
            document.id
        )

        if not chunks:
            continue

        for position, chunk in enumerate(chunks):

            local_context = get_context(
                chunks,
                position,
                radius=4
            )

            score = score_exam_context(
                local_context,
                details
            )

            if score <= 0:
                continue

            candidates.append(
                {
                    "score": score,
                    "document_id": document.id,
                    "position": position,
                    "context": local_context
                }
            )

    candidates.sort(
        key=lambda item: (
            item["score"],
            item["document_id"],
            item["position"]
        ),
        reverse=True
    )

    results = []

    seen = set()

    for candidate in candidates:

        key = (
            candidate["document_id"],
            candidate["position"]
        )

        if key in seen:
            continue

        seen.add(key)

        results.append(
            candidate["context"]
        )

        if len(results) >= 5:
            break

    return results


# ============================================================
# DATE EXTRACTION
# ============================================================

def extract_dates(text: str) -> list[str]:

    if not text:
        return []

    patterns = [

        # 1 October 2026
        r"\b\d{1,2}\s+"
        r"(?:jan|january|feb|february|mar|march|apr|april|"
        r"may|jun|june|jul|july|aug|august|sep|september|"
        r"oct|october|nov|november|dec|december)"
        r"(?:\s*,?\s*2026)?\b",

        # October 1 2026
        r"\b"
        r"(?:jan|january|feb|february|mar|march|apr|april|"
        r"may|jun|june|jul|july|aug|august|sep|september|"
        r"oct|october|nov|november|dec|december)"
        r"\s+\d{1,2}"
        r"(?:st|nd|rd|th)?"
        r"(?:\s*,?\s*2026)?\b",

        # 01/10/2026
        r"\b\d{1,2}[/-]\d{1,2}[/-]2026\b",

        # 01-10-26
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2}\b"
    ]

    dates = []

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        for match in matches:

            value = re.sub(
                r"\s+",
                " ",
                match
            ).strip()

            if value not in dates:
                dates.append(value)

    return dates


# ============================================================
# EXAM ANSWER
# ============================================================

def answer_exam_question(
    db: Session,
    question: str
) -> Optional[str]:

    details = detect_exam_details(
        question
    )

    contexts = retrieve_exam_contexts(
        db,
        question
    )

    if not contexts:
        return None

    # Combine contexts.
    combined = "\n".join(
        contexts
    )

    # --------------------------------------------------------
    # Get dates.
    # --------------------------------------------------------

    dates = extract_dates(
        combined
    )

    # --------------------------------------------------------
    # Build display title.
    # --------------------------------------------------------

    title_parts = []

    if details["course"] == "btech":
        title_parts.append("B.Tech")

    elif details["course"] == "mtech":
        title_parts.append("M.Tech")

    elif details["course"] == "bca":
        title_parts.append("BCA")

    elif details["course"] == "mca":
        title_parts.append("MCA")

    if details["branch"]:
        title_parts.append(
            details["branch"].upper()
        )

    if details["semester"]:
        title_parts.append(
            details["semester"].upper()
        )
        title_parts.append(
            "Semester"
        )

    if details["exam_type"]:
        title_parts.append(
            details["exam_type"].title()
        )
        title_parts.append(
            "Examination"
        )

    title = " ".join(
        title_parts
    )

    if not title:
        title = "Examination Schedule"

    # --------------------------------------------------------
    # IMPORTANT:
    # Do not dump the whole PDF.
    #
    # First try to identify compact lines containing dates.
    # --------------------------------------------------------

    lines = []

    for line in re.split(
        r"[\n]+",
        combined
    ):

        line = line.strip()

        if not line:
            continue

        if len(line) > 350:
            continue

        if extract_dates(line):
            lines.append(line)

    # Remove duplicates.
    unique_lines = []

    seen = set()

    for line in lines:

        key = normalize(line)

        if key in seen:
            continue

        seen.add(key)

        unique_lines.append(line)

    # --------------------------------------------------------
    # Return concise answer when dates were found.
    # --------------------------------------------------------

    if dates:

        answer = (
            "According to the college documents:\n\n"
            f"• Examination: {title}\n"
            "• Examination Date(s): "
            + ", ".join(dates[:10])
        )

        # Add at most two compact schedule rows.
        if unique_lines:

            answer += (
                "\n\n"
                "• Schedule details:"
            )

            for line in unique_lines[:2]:
                answer += (
                    "\n  - "
                    + line
                )

        return answer

    # --------------------------------------------------------
    # If date parser cannot identify dates, return a short
    # relevant excerpt instead of the entire document.
    # --------------------------------------------------------

    relevant_lines = []

    for line in re.split(
        r"[\n]+",
        combined
    ):

        line = line.strip()

        if not line:
            continue

        normalized = normalize(
            line
        )

        score = 0

        if details["course"]:
            if course_matches(
                normalized,
                details["course"]
            ):
                score += 2

        if details["branch"]:
            if branch_matches(
                normalized,
                details["branch"]
            ):
                score += 2

        if details["semester"]:
            if semester_matches(
                normalized,
                details["semester"]
            ):
                score += 2

        if details["exam_type"]:
            if exam_type_matches(
                normalized,
                details["exam_type"]
            ):
                score += 2

        if score > 0:
            relevant_lines.append(
                line
            )

    if relevant_lines:

        answer = (
            "According to the college documents:\n\n"
            f"• Examination: {title}\n"
            "• Relevant schedule information:"
        )

        for line in relevant_lines[:5]:
            answer += (
                "\n  - "
                + line
            )

        return answer

    return None


# ============================================================
# GENERIC RETRIEVAL
# ============================================================

def keyword_score(
    question_tokens: list[str],
    text: str
) -> float:

    if not question_tokens or not text:
        return 0.0

    text_tokens = tokenize(
        text
    )

    if not text_tokens:
        return 0.0

    counts = Counter(
        text_tokens
    )

    score = 0.0

    for token in set(question_tokens):

        if token in counts:
            score += 1.0

            if counts[token] >= 2:
                score += 0.25

    return score


def retrieve_relevant_chunks(
    db: Session,
    question: str,
    max_chunks: int = 8
) -> list[str]:

    question_tokens = tokenize(question)

    if not question_tokens:
        return []

    # Ignore very common words so unrelated documents
    # cannot become relevant because of weak keyword overlap.
    stop_words = {
        "the", "a", "an", "is", "are", "am", "was", "were",
        "my", "me", "i", "we", "you", "what", "when", "where",
        "how", "why", "can", "could", "would", "please",
        "tell", "about", "do", "does", "did", "in", "on",
        "at", "to", "for", "of", "and", "or", "with",
        "college"
    }

    meaningful_tokens = [
        token
        for token in question_tokens
        if token not in stop_words
        and len(token) > 2
    ]

    if not meaningful_tokens:
        return []

    chunks = (
        db.query(models.DocumentChunk)
        .order_by(
            models.DocumentChunk.created_at.desc()
        )
        .all()
    )

    scored = []

    for chunk in chunks:

        if not chunk.content:
            continue

        text_tokens = tokenize(chunk.content)

        if not text_tokens:
            continue

        counts = Counter(text_tokens)

        score = 0.0

        for token in set(meaningful_tokens):

            if token in counts:
                score += 1.0

                if counts[token] >= 2:
                    score += 0.25

        # Require at least two meaningful matching signals.
        if score < 2.0:
            continue

        scored.append(
            (
                score,
                chunk.content
            )
        )

    scored.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return [
        content
        for _, content in scored[:max_chunks]
    ]


# ============================================================
# FACT HELPERS
# ============================================================

def find_fact(
    chunks: list[str],
    keywords: list[str]
) -> Optional[str]:

    for chunk in chunks:

        if not chunk:
            continue

        lines = re.split(
            r"[\n.!?]+",
            chunk
        )

        for line in lines:

            line = line.strip()

            if not line:
                continue

            lower = line.lower()

            if any(
                keyword.lower() in lower
                for keyword in keywords
            ):
                return line

    return None


def find_registration_link(
    chunks: list[str]
) -> Optional[str]:

    pattern = r"https?://[^\s<>\"]+"

    for chunk in chunks:

        urls = re.findall(
            pattern,
            chunk
        )

        for url in urls:

            url = url.rstrip(
                ".,);"
            )

            if (
                "forms.gle" in url.lower()
                or "register" in url.lower()
                or "registration" in url.lower()
            ):
                return url

    return None


# ============================================================
# SPECIAL ANSWERS
# ============================================================

def special_answer(
    question: str,
    chunks: list[str]
) -> Optional[str]:

    intent = detect_intent(
        question
    )

    if intent == "registration_link":

        link = find_registration_link(
            chunks
        )

        if link:
            return (
                "You can register using the college "
                "registration form:\n\n"
                + link
            )

        return (
            "You can register using the college "
            "registration form:\n\n"
            "https://forms.gle/XcjeXTkeqoVRe2qG7"
        )

    if intent == "eligibility":

        fact = find_fact(
            chunks,
            [
                "eligible",
                "eligibility",
                "participate"
            ]
        )

        if fact:
            return (
                "According to the college documents:\n\n"
                + fact
            )

    if intent == "registration_fee":

        fact = find_fact(
            chunks,
            [
                "registration fee",
                "registration fees",
                "fee",
                "fees"
            ]
        )

        if fact:
            return (
                "According to the college documents:\n\n"
                + fact
            )

    if intent == "team_size":

        fact = find_fact(
            chunks,
            [
                "team size",
                "team members",
                "members"
            ]
        )

        if fact:
            return (
                "According to the college documents:\n\n"
                + fact
            )

    if intent == "deadline":

        fact = find_fact(
            chunks,
            [
                "deadline",
                "last date",
                "registration deadline"
            ]
        )

        if fact:
            return (
                "According to the college documents:\n\n"
                + fact
            )

    if intent == "prize":

        fact = find_fact(
            chunks,
            [
                "prize",
                "prize pool",
                "cash prize"
            ]
        )

        if fact:
            return (
                "According to the college documents:\n\n"
                + fact
            )

    if intent == "attendance":

        fact = find_fact(
            chunks,
            [
                "attendance",
                "minimum attendance",
                "attendance requirement"
            ]
        )

        if fact:
            return (
                "According to the college documents:\n\n"
                + fact
            )

    if intent == "scholarship":

        fact = find_fact(
            chunks,
            [
                "scholarship",
                "scholarships"
            ]
        )

        if fact:
            return (
                "According to the college documents:\n\n"
                + fact
            )

    return None


# ============================================================
# MAIN ANSWER
# ============================================================

def generate_answer(
    db: Session,
    question: str
) -> str:

    question = question.strip()

    if not question:
        return "Please enter a question."

    # --------------------------------------------------------
    # EXAM QUESTIONS
    # --------------------------------------------------------

    if is_exam_question(question):

        answer = answer_exam_question(
            db,
            question
        )

        if answer:
            return answer

        return (
            "I couldn't find a matching examination "
            "schedule in the college documents. "
            "Please check the course, branch, semester, "
            "and examination type."
        )

    # --------------------------------------------------------
    # NORMAL DOCUMENT SEARCH
    # --------------------------------------------------------

    chunks = retrieve_relevant_chunks(
        db,
        question
    )

    if not chunks:
        return (
            "I couldn't find a precise answer in the "
            "college documents. Please raise a support "
            "request if you need further help."
        )

    # --------------------------------------------------------
    # SPECIAL KNOWLEDGE ANSWERS
    # --------------------------------------------------------

    answer = special_answer(
        question,
        chunks
    )

    if answer:
        return answer

    # --------------------------------------------------------
    # GENERIC ANSWER
    # --------------------------------------------------------

    useful_lines = []

    for chunk in chunks[:3]:

        for line in re.split(
            r"[\n.!?]+",
            chunk
        ):

            line = line.strip()

            if len(line) < 15:
                continue

            if line not in useful_lines:
                useful_lines.append(
                    line
                )

            if len(useful_lines) >= 5:
                break

        if len(useful_lines) >= 5:
            break

    if useful_lines:

        return (
            "According to the college documents:\n\n"
            + "\n".join(
                f"• {line}"
                for line in useful_lines
            )
        )

    return (
        "I couldn't find a precise answer in the "
        "college documents. Please raise a support "
        "request if you need further help."
    )


# ============================================================
# PUBLIC CHATBOT FUNCTION
# ============================================================

def answer_question(
    db: Session,
    question: str
) -> str:

    try:

        return generate_answer(
            db,
            question
        )

    except Exception as error:

        # IMPORTANT:
        # During development we expose the real error so
        # debugging is possible. Remove the error details
        # before the final production demo if desired.

        import traceback

        print(
            "========== AI SERVICE ERROR =========="
        )

        print(
            str(error)
        )

        traceback.print_exc()

        print(
            "======================================"
        )

        return (
            "AI service error: "
            + str(error)
        )