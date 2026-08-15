import fitz
import re
import pandas as pd

def check_duplicates():
    pdf_path = 'brenchmark/Correction 150 question.pdf'
    doc = fitz.open(pdf_path)
    full_text = [page.get_text() for page in doc]
    text = "\n".join(full_text)

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

    # Group by q_id
    by_id = {}
    for q in questions:
        qid = q['q_id']
        by_id.setdefault(qid, []).append(q)

    diff_dups = 0
    with open('dups_check.txt', 'w', encoding='utf-8') as f:
        f.write(f"Total extracted: {len(questions)}\n")
        f.write(f"Unique q_ids: {len(by_id)}\n")
        for qid in sorted(by_id.keys(), key=lambda x: int(x) if x.isdigit() else 999):
            instances = by_id[qid]
            if len(instances) > 1:
                # Check if all instances have exact same question and answer
                first_q = instances[0]['question']
                first_ans = instances[0]['answer']
                is_same = all(x['question'] == first_q and x['answer'] == first_ans for x in instances)
                if not is_same:
                    diff_dups += 1
                    f.write(f"\n--- Q_ID {qid} has {len(instances)} DIFFERENT instances ---\n")
                    for idx, inst in enumerate(instances):
                        f.write(f"  Instance {idx+1} Act: {inst['act']}\n")
                        f.write(f"  Question: {inst['question']}\n")
                        f.write(f"  Answer:   {inst['answer'][:100]}...\n")
                else:
                    # Same question, maybe different act or exact same?
                    is_same_act = all(x['act'] == instances[0]['act'] for x in instances)
                    if not is_same_act:
                        f.write(f"Q_ID {qid} has {len(instances)} instances with SAME q/ans but different act: {[x['act'] for x in instances]}\n")
        f.write(f"\nSummary: {diff_dups} Q_IDs have different question/answer text across duplicates.\n")

if __name__ == '__main__':
    check_duplicates()
