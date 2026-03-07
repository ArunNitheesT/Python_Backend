import os
import logging
import warnings
import requests

logging.getLogger("transformers").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

HF_API_KEY = os.environ.get("HF_API_KEY", "")
HF_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"


def classifier(text, labels):
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {
        "inputs": text,
        "parameters": {"candidate_labels": labels}
    }
    response = requests.post(HF_API_URL, headers=headers, json=payload)
    return response.json()


def get_domain_sensitivity_score(text):
    domains = [
        "healthcare and medical services",
        "financial services and banking",
        "legal and judicial system",
        "human resources and hiring",
        "education and academic systems",
        "low-risk business automation"
    ]
    result = classifier(text, domains)
    top = result['labels'][0].lower()
    if "healthcare" in top or "medical" in top: return 5
    if "legal" in top or "judicial" in top: return 5
    if "financial" in top or "banking" in top: return 4
    if "human resources" in top or "hiring" in top: return 4
    if "education" in top or "academic" in top: return 4
    return 1


def get_impact_severity_score(text):
    high = [
        "life","death","fatal","survival","emergency","critical condition","triage",
        "surgery","resuscitation","icu","treatment decision","diagnosis","treatment plan",
        "criminal","conviction","sentence","verdict","incarceration","arrest",
        "legal penalty","court decision","guilty","not guilty","freedom","human rights",
        "custody","deportation","bankruptcy","foreclosure","loan approval","loan rejection",
        "insurance claim decision","financial eligibility","tax penalty","fraud accusation",
        "account freeze","suicide risk","terminal illness","end of life",
        "psychological damage","severe distress","public safety","catastrophic",
        "irreversible harm","dangerous situation","termination","fired","dismissed",
        "job loss","employment decision"
    ]
    medium = [
        "evaluation","assessment","grading","scoring","ranking","prioritization",
        "performance review","credit scoring","risk assessment","recommendation",
        "suggestion","advice","decision support","prediction","forecast",
        "pricing","billing","payment reminder","content moderation","flagging",
        "shortlisting","interview selection","promotion consideration","admission recommendation",
        "promote","promotion","recommend termination","recommend promotion"
    ]
    t = text.lower()
    if any(w in t for w in high): return 5
    if any(w in t for w in medium): return 3
    return 1


def get_human_judgment_score(text):
    actions = ["decision making","recommendation","classification","monitoring","content generation"]
    result = classifier(text, actions)
    top = result['labels'][0]
    return {"decision making": 5, "recommendation": 4, "analysis": 3, "classification": 2}.get(top, 1)


def get_emotional_need_score(text):
    words = [
        "emotional","feelings","distress","grief","trauma","comfort","support",
        "empathy","compassion","counseling","therapy","psychological help",
        "bad news","terminal illness","mental health","conflict resolution",
        "relationship","trust","morale","motivation","personal guidance"
    ]
    return 1 if any(w in text.lower() for w in words) else 0


def get_data_sensitivity_score(text):
    sensitive = [
        "medical","health record","clinical data","patient data","biometric",
        "fingerprint","facial recognition","dna","genetic data","mental health record",
        "prescription data","diagnosis report","hospital record","ehr","emr"
    ]
    personal = [
        "salary","income","bank","credit score","loan","transaction history",
        "tax record","payment history","card number","resume","cv",
        "employment history","student record","academic record","grades",
        "transcript","national id","passport","ssn","appraisal","performance review"
    ]
    t = text.lower()
    if any(w in t for w in sensitive): return 5
    if any(w in t for w in personal): return 4
    return 2


def get_repetitiveness_score(text):
    words = [
        "routine","repetitive","standardized","structured","template","checklist",
        "fixed procedure","workflow","data processing","data entry","form processing",
        "record update","sorting","categorizing","tagging","labeling","verification",
        "validation","formatting","conversion","normalization","batch processing",
        "ticket routing","report generation","log processing","updating database"
    ]
    return 5 if any(w in text.lower() for w in words) else 2


def get_frequency_score(text):
    words = [
        "frequent","continuous","constant","repeated","high volume","large scale",
        "mass processing","bulk requests","daily operations","hourly tasks",
        "real time","every request","every transaction","ongoing monitoring",
        "thousands","millions","per second","per minute","high traffic","heavy load"
    ]
    return 5 if any(w in text.lower() for w in words) else 3


def get_automation_cost_score(text):
    words = [
        "complex system","advanced ai","deep learning","neural network",
        "computer vision","multimodal analysis","autonomous system","robotics",
        "adaptive learning","predictive modeling","behavior analysis",
        "long term planning","dynamic environment","unstructured environment","high uncertainty"
    ]
    return 5 if any(w in text.lower() for w in words) else 2


def get_skill_risk_score(text):
    words = [
        "surgeon","physician","doctor","clinician","psychiatrist","psychologist",
        "therapist","counselor","radiologist","clinical judgement","treatment planning",
        "judge","magistrate","prosecutor","lawyer","legal counsel","sentencing decision",
        "court decision","pilot","air traffic controller","incident commander",
        "financial advisor","investment advisor","portfolio manager","underwriter",
        "actuary","compliance officer","executive decision","policy decision",
        "strategic decision","crisis management","governance decision",
        "teacher","mentor","coach","career guidance","interviewer",
        "recruitment decision","performance evaluation","professional judgement",
        "evaluate","termination","promotion","school","faculty","staff",
        "recommend promotion","recommend termination","appraise"
    ]
    return 5 if any(w in text.lower() for w in words) else 2


def compute_scores(rep, freq, hj, ac, impact, domain, data, skill, emotion):
    suitability = (0.3 * rep + 0.25 * freq + 0.2 * (6 - hj) + 0.25 * (6 - ac))
    ethical_risk = (0.25 * impact + 0.2 * domain + 0.2 * data + 0.2 * skill + 0.15 * emotion)
    return suitability, ethical_risk


def classify_responsibility(text):
    labels = [
        "physical harm or life safety decision",
        "legal judgment affecting rights or punishment",
        "medical diagnosis or treatment decision",
        "emotional counseling or psychological care",
        "high-level strategic leadership decision",
        "professional evaluation requiring human review",
        "routine data processing or recommendation task"
    ]
    result = classifier(text, labels)
    return result["labels"][0]


def decide_from_role(role):
    if role in [
        "physical harm or life safety decision",
        "legal judgment affecting rights or punishment",
        "medical diagnosis or treatment decision",
        "emotional counseling or psychological care"
    ]:
        return "Do NOT Automate"
    elif role in [
        "high-level strategic leadership decision",
        "professional evaluation requiring human review"
    ]:
        return "Human-in-the-Loop"
    else:
        return "Fully Automate"


def generate_explanation(decision, role, evidence):
    context = f"""
    Decision: {decision}
    Responsibility Type: {role}
    Key Factors: {", ".join(evidence) if evidence else "general risk assessment"}
    """

    prompt = f"""
    You are an AI ethics reviewer writing a justification for a company manager.
    Write a natural human explanation.
    Rules:
    - Professional tone
    - No bullet points
    - No mentioning scores or numbers
    - 4 to 5 sentences
    - Explain responsibility and consequences
    - Do not change the decision and do not invent new reasons
    Context:{context}
    """

    response = requests.post(url="https://aura-backend-phi.vercel.app/api/llm", json={"prompt": prompt})
    response = response.json()
    return response.get("response", "No explanation generated.")


def evaluate_task(text):
    role = classify_responsibility(text)
    role_decision = decide_from_role(role)

    rep     = get_repetitiveness_score(text)
    freq    = get_frequency_score(text)
    hj      = get_human_judgment_score(text)
    ac      = get_automation_cost_score(text)
    impact  = get_impact_severity_score(text)
    domain  = get_domain_sensitivity_score(text)
    data    = get_data_sensitivity_score(text)
    skill   = get_skill_risk_score(text)
    emotion = get_emotional_need_score(text)

    _, ethical_risk = compute_scores(rep, freq, hj, ac, impact, domain, data, skill, emotion)

    if role_decision == "Fully Automate" and ethical_risk >= 4.0:
        final_decision = "Do NOT Automate"
    elif role_decision == "Fully Automate" and ethical_risk >= 2.8:
        final_decision = "Human-in-the-Loop"
    elif role_decision == "Human-in-the-Loop" and ethical_risk >= 4.0:
        final_decision = "Do NOT Automate"
    else:
        final_decision = role_decision

    evidence = []
    if impact >= 4:  evidence.append("high real-world consequences")
    if hj >= 4:      evidence.append("requires human judgement")
    if emotion == 1: evidence.append("involves emotional understanding")
    if domain >= 4:  evidence.append("sensitive professional domain")
    if skill >= 4:   evidence.append("replaces accountable human expertise")

    explanation = generate_explanation(final_decision, role, evidence)
    return final_decision, role, explanation
