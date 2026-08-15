import fitz
import re
import pandas as pd

def parse_and_combine_pdf():
    # 1. Load the old verified 45 questions
    df_45_path = 'brenchmark/justor benchmark verified 45.csv'
    df_45 = pd.read_csv(df_45_path)
    print(f"Loaded {len(df_45)} verified questions from {df_45_path}")

    # 2. Extract and clean questions from Correction 150 question.pdf
    pdf_path = 'brenchmark/Correction 150 question.pdf'
    doc = fitz.open(pdf_path)
    full_text = []
    for page in doc:
        full_text.append(page.get_text())
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

    # Clean and deduplicate questions from Correction 150 question.pdf
    seen_q = set()
    clean_qs = []
    for q in questions:
        cq = re.sub(r'\s+', ' ', q['question']).strip().rstrip('●').strip()
        if cq not in seen_q:
            seen_q.add(cq)
            ca = re.sub(r'\s+', ' ', q['answer']).strip()
            if "Q37:" in ca:
                continue
            clean_qs.append({
                'act': q['act'],
                'orig_qid': q['q_id'],
                'question': cq,
                'answer': ca
            })

    print(f"Extracted and deduplicated exactly {len(clean_qs)} questions from Correction 150 question.pdf.")

    # 3. Format the new questions into rows matching df_45 columns
    new_rows = []
    start_id = len(df_45) + 1
    for idx, q in enumerate(clean_qs, start=start_id):
        qid_str = f"Q{idx:03d}"
        ans = q['answer']
        sec_m = re.search(r'\bSection[s]?\s+([0-9]+[A-Za-z]?(?:\([0-9A-Za-z]+\))?)', ans, re.IGNORECASE)
        sec_num = sec_m.group(1) if sec_m else ""
        if not sec_num:
            art_m = re.search(r'\bArticle\s+([0-9]+[A-Za-z]?)', ans, re.IGNORECASE)
            if art_m:
                sec_num = "Article " + art_m.group(1)

        new_rows.append({
            'id': qid_str,
            'category': q['act'] or "General Law",
            'source_file': "Correction 150 question.pdf",
            'question': q['question'],
            'gold_answer': ans,
            'expected_act': q['act'],
            'expected_section': sec_num
        })

    df_new = pd.DataFrame(new_rows)

    # Ensure df_45 has the same columns and order
    df_combined = pd.concat([df_45, df_new], ignore_index=True)

    out_path = 'brenchmark/justor_benchmark_195.csv'
    df_combined.to_csv(out_path, index=False)
    print(f"Successfully combined {len(df_45)} old questions and {len(df_new)} new questions.")
    print(f"Saved total {len(df_combined)} rows to {out_path}")

if __name__ == '__main__':
    parse_and_combine_pdf()
