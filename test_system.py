# Automated Jenkins CI test suite
from questions import get_all_questions
from scoring import calculate_score

def test_scoring_system():
    questions = get_all_questions()
    perfect_submission = {1: "main", 2: "Jenkinsfile", 3: "git bisect", 4: "200 OK"}
    score, passed = calculate_score(perfect_submission, questions)
    assert score == 100.0, f"Expected 100.0, got {score}"
    assert passed is True, "Expected passed to be True"

    half_submission = {1: "main", 2: "Jenkinsfile", 3: "wrong", 4: "wrong"}
    score, passed = calculate_score(half_submission, questions)
    assert score == 50.0, f"Expected 50.0, got {score}"
    assert passed is True, "Expected passed to be True"

    failing_submission = {1: "wrong", 2: "wrong", 3: "wrong", 4: "wrong"}
    score, passed = calculate_score(failing_submission, questions)
    assert score == 0.0, f"Expected 0.0, got {score}"
    assert passed is False, "Expected passed to be False"
    print("Jenkins CI: All automated unit tests passed successfully!")

if __name__ == "__main__":
    test_scoring_system()
