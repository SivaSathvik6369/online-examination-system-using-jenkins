# Question bank management
questions_bank = [
    {
        "id": 1,
        "question": "What is the primary branch in modern Git repositories?",
        "options": ["master", "main", "trunk", "root"],
        "answer": "main"
    },
    {
        "id": 2,
        "question": "Which Jenkins file defines a declarative pipeline?",
        "options": ["build.xml", "Dockerfile", "Jenkinsfile", "pom.xml"],
        "answer": "Jenkinsfile"
    },
    {
        "id": 3,
        "question": "Which Git command performs binary search to find a bug?",
        "options": ["git search", "git bisect", "git blame", "git find"],
        "answer": "git bisect"
    },
    {
        "id": 4,
        "question": "What HTTP status indicates a successful response?",
        "options": ["200 OK", "404 Not Found", "500 Server Error", "301 Redirect"],
        "answer": "200 OK"
    }
]

def get_all_questions():
    return questions_bank

def get_question_by_id(qid):
    for q in questions_bank:
        if q["id"] == qid:
            return q
    return None
