import fitz
import re

def count_clean_questions():
    doc = fitz.open('brenchmark/Correction 150 question.pdf')
    text = "\n".join([page.get_text() for page in doc])
    lines = text.split('\n')
    questions = []
    current_act = ""
    current_q_id = ""
    current_q_text = ""
    current_ans_text = ""
    state = "NONE"

    sec_heading_re = re.compile(r'^Section\s+\d+:\s*(.+)', re.IGNORECASE)
    q_start_re = re.compile(r'^Q(\d+):\s*(.*)', re.IGNORECASE)

    for line in lines:
        l_strip = line.strip()
        if not l_strip:
            continue
        m_sec = sec_heading_re.match(l_strip)
        if m_sec:
            current_act = m_sec.group(1).strip()
            continue
        m_q = q_start_re.match(l_strip)
        if m_q:
            if current_q_id and current_q_text:
                questions.append({
                    'act': current_act,
                    'q_id': current_q_id,
                    'question': current_q_text.strip(),
                    'answer': current_ans_text.strip()
                })
            current_q_id = m_q.group(1)
            current_q_text = m_q.group(2)
            current_ans_text = ""
            state = "Q"
            continue
        if l_strip.startswith("●") or l_strip.startswith("Answer Details:"):
            state = "ANS"
            current_ans_text += " " + re.sub(r'^[●\s]+', '', l_strip)
            continue
        if state == "Q":
            current_q_text += " " + l_strip
        elif state == "ANS":
            current_ans_text += " " + l_strip

    if current_q_id and current_q_text:
        questions.append({
            'act': current_act,
            'q_id': current_q_id,
            'question': current_q_text.strip(),
            'answer': current_ans_text.strip()
        })

    # Also check if any question swallowed another question inside answer (like Q37 inside Q36 answer)
    # But first let's deduplicate by clean question text
    seen_q = set()
    clean_qs = []
    for q in questions:
        # clean question text: normalize spaces, strip trailing dot/bullet
        cq = re.sub(r'\s+', ' ', q['question']).strip().rstrip('●').strip()
        if cq not in seen_q:
            seen_q.add(cq)
            # also clean answer text
            ca = re.sub(r'\s+', ' ', q['answer']).strip()
            # If this is the Q36 where Q37 is swallowed inside answer, fix or pick the clean one
            if "Q37:" in ca:
                continue
            clean_qs.append({
                'act': q['act'],
                'orig_qid': q['q_id'],
                'question': cq,
                'answer': ca
            })

    print(f"Total unique clean questions (ignoring swallowed/duplicates): {len(clean_qs)}")
    return clean_qs

if __name__ == '__main__':
    count_clean_questions()
