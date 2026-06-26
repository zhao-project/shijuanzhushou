from src.llm_client import create_llm_client
from src.generator import QuestionGenerator

client = create_llm_client()
gen = QuestionGenerator(client)

# 只生成1道单选题（控制用量）
kps = ['Python基础语法']
questions = gen.generate_questions(kps, ['single_choice'])
print('生成题目数:', len(questions))
for i, q in enumerate(questions, 1):
    print(str(i) + '. ' + q['question'])
    for opt in q.get('options', []):
        print('   ' + opt)
    print('   答案: ' + q['answer'])
    print()

usage = client.get_total_usage()
print('Token消耗:', usage['total_tokens'])
