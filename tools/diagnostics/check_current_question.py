with open("backend_benchmark.log", "r", encoding="utf-8") as f:
    text = f.read()
q_count = text.count("POST /chat HTTP/1.1")
print(f"Total /chat requests processed so far: {q_count}")
