# PYTHONPATH=. pytest tests/test.py

import pytest
from fastapi.testclient import TestClient
from main import app  # Импортируем FastAPI приложение

client = TestClient(app)

def test_recommend_team_to_person():
    # Пример запроса для "Человек - команда"
    response = client.post(
        "/recommend_team_to_person",
        json={
        "person_skills": ["Python", "Docker", "Kubernetes", "Linux", "Machine Learning", "SQL", "Matplotlib", "Seaborn"],
        "teams": [
            {
                "team_id": 1,
                "name": "Команда анализа данных",
                "skills": {
                    "Member 1": ["Data Science", "Python", "Pandas", "SQL", "Scikit-Learn"],
                    "Member 2": ["Python", "Machine Learning", "TensorFlow", "Keras", "Pandas"],
                    "Member 3": ["SQL", "Data Engineering", "Pandas", "Matplotlib"],
                    "Member 4": ["Linux", "Docker", "Kubernetes", "DevOps"],
                    "Member 5": ["Python", "Matplotlib", "Seaborn", "Data Visualization"]
                },
                "required_roles": ["Аналитик", "ML engineer", "DevOps"]
            },
            {
                "team_id": 2,
                "name": "Разработка системы ECM для авиационного двигателя",
                "skills": {
                    "Member 1": ["Python", "Back-end разработка", "Django", "Docker", "Git", "SQL", "Построение Rest API"],
                    "Member 2": ["Python", "Back-end разработка", "Docker", "Git", "СУБД PostgreSQL", "Linux"],
                    "Member 3": ["Machine Learning", "Data Science", "Python", "Pandas", "NumPy", "Scikit-Learn", "TensorFlow"],
                    "Member 4": ["DevOps", "Docker", "Kubernetes", "K8S", "Linux", "Helm", "Nginx", "Graphana"],
                    "Member 5": ["Python", "PostgreSQL", "Умение работать с API", "Atlassian stack [Jira, Confluence]", "Linux"],
                    "Member 6": ["Data Science", "SQL", "Математическая статистика", "Pandas", "Scikit-Learn"],
                    "Member 7": ["DevOps", "Machine Learning", "AirFlow", "Docker", "Kubernetes", "ONNX Runtime"]
                },
                "required_roles": ["ML engineer", "Аналитик", "Python Backend", "DevOps", "ML Ops Engineer"]
            },
            {
                "team_id": 3,
                "name": "Команда разработки на C++",
                "skills": {
                    "Member 1": ["C++", "Back-end разработка", "Git", "Linux", "Docker"],
                    "Member 2": ["Python", "Machine Learning", "SQL", "Scikit-Learn", "TensorFlow"],
                    "Member 3": ["Linux", "DevOps", "Docker", "Kubernetes"],
                    "Member 4": ["Machine Learning", "Data Science", "Python", "Pandas"],
                    "Member 5": ["Computer Vision", "OpenCV", "Python", "TensorFlow"]
                },
                "required_roles": ["C++ Backend", "ML engineer", "DevOps", "CV engineer"]
            },
            {
                "team_id": 4,
                "name": "Команда Frontend разработки",
                "skills": {
                    "Member 1": ["HTML", "CSS", "JavaScript", "React", "Git"],
                    "Member 2": ["JavaScript", "Vue", "Frontend разработка", "CSS", "Git"],
                    "Member 3": ["UI/UX", "Figma", "Adobe XD", "Frontend разработка"],
                    "Member 4": ["JavaScript", "HTML", "CSS", "React", "Next"]
                },
                "required_roles": ["Frontend", "Дизайнер"]
            },
            {
                "team_id": 5,
                "name": "Тестировщики ПО",
                "skills": {
                    "Member 1": ["Python", "Automated Testing", "Selenium", "Git"],
                    "Member 2": ["Testing", "Manual Testing", "API Testing", "SQL"],
                    "Member 3": ["Load Testing", "Performance Testing", "JMeter", "Linux"],
                    "Member 4": ["Python", "Test Automation", "PyTest", "Selenium"],
                    "Member 5": ["Linux", "Shell Scripting", "Bash", "Docker"]
                },
                "required_roles": ["Тестировщик", "DevOps"]
            }
        ],
        "role_filled_threshold": 0.5,
        "unfilled_role_weight": 1.5,
        "confidence_percentile": 0.6
    }

    )
    assert response.status_code == 200
    assert "recommended_teams" in response.json()
    assert len(response.json()["recommended_teams"]) > 0
    for team in response.json()["recommended_teams"]:
        assert "team_id" in team
        assert "team_name" in team
        assert "similarity" in team

def test_recommend_case_to_team():
    # Пример запроса для "Команда - кейс"
    response = client.post(
        "/recommend_case_to_team",
        json={
            "team": {
                "team_id": 1,
                "name": "Team 1",
                "skills": {
                    "Member 1": ["C#", "Back-end разработка", "Git", "SQL", "Построение Rest API", "Docker"],
                    "Member 2": ["C#", "Back-end разработка", "Docker", "Git", "СУБД PostgreSQL", "Linux"],
                    "Member 3": ["HTML", "CSS", "React", "Git", "Next", "Tailwind", "JavaScript"],
                    "Member 4": ["DevOps", "Docker", "Kubernetes", "K8S", "Linux", "Helm", "Nginx", "Graphana"],
                    "Member 5": ["Умение работать с API", "PostgreSQL", "Python", "Atlassian stack [Jira, Confluence]", "Linux"],
                    "Member 6": ["Data Science", "SQL", "Pandas", "Математическая статистика", "Управление проектами"],
                    "Member 7": ["Canva", "Figma", "CSS", "UI/UX", "Adobe XD", "Photoshop"]
                },
            },
            "cases": [
                {
                    "id": 1,
                    "title": "Система контроля качества",
                    "description": "Система контроля качества продуктов АО 'Медитек' требуется для контроля качества и технических параметров различных приборов проектируемых компанией.",
                    "required_roles": "C# Backend, Тестировщик, Аналитик"
                },
                {
                    "id": 2,
                    "title": "Разработка ECM для авиации",
                    "description": "Моделирование авиационного двигателя",
                    "required_roles": "ML engineer, Аналитик, Python Backend, DevOps"
                }
            ],
            "alpha": 0.6,
            "beta": 0.4,
            "confidence_percentile": 0.8
        }
    )
    assert response.status_code == 200
    assert "recommended_cases" in response.json()
    assert len(response.json()["recommended_cases"]) > 0
    for case in response.json()["recommended_cases"]:
        assert "id" in case
        assert "title" in case
        assert "hybrid_similarity" in case

def test_recommend_team_to_case():
    # Пример запроса для "Кейс - команда"
    response = client.post(
        "/recommend_team_to_case",
        json={
            "case": {
                "id": 1,
                "title": "Система контроля качества продуктов АО 'Медитек'",
                "description": "Система контроля качества продуктов требуется для контроля качества и технических параметров приборов.",
                "required_roles": "C# Backend, Тестировщик, Аналитик"
            },
            "teams": [
                {
                    "team_id": 1,
                    "name": "Team 1",
                    "skills": {
                        "Member 1": ["C#", "Back-end разработка", "Git", "SQL", "Построение Rest API", "Docker"],
                        "Member 2": ["C#", "Back-end разработка", "Docker", "Git", "СУБД PostgreSQL", "Linux"],
                        "Member 3": ["HTML", "CSS", "React", "Git", "Next", "Tailwind", "JavaScript"],
                        "Member 4": ["DevOps", "Docker", "Kubernetes", "K8S", "Linux", "Helm", "Nginx", "Graphana"],
                        "Member 5": ["Умение работать с API", "PostgreSQL", "Python", "Atlassian stack [Jira, Confluence]", "Linux"],
                        "Member 6": ["Data Science", "SQL", "Pandas", "Математическая статистика", "Управление проектами"],
                        "Member 7": ["Canva", "Figma", "CSS", "UI/UX", "Adobe XD", "Photoshop"]
                    }
                },
                {
                    "team_id": 2,  
                    "name": "Team 2",
                    "skills": {
                        "Member 1": ["Python", "Back-end разработка", "Django", "Docker", "Git", "SQL", "Построение Rest API"],
                        "Member 2": ["Python", "Back-end разработка", "Docker", "Git", "СУБД PostgreSQL", "Linux"],
                        "Member 3": ["Machine Learning", "Data Science", "Python", "Pandas", "NumPy", "Scikit-Learn", "TensorFlow"],
                        "Member 4": ["DevOps", "Docker", "Kubernetes", "K8S", "Linux", "Helm", "Nginx", "Graphana"],
                        "Member 5": ["Python", "PostgreSQL", "Умение работать с API", "Atlassian stack [Jira, Confluence]", "Linux"],
                        "Member 6": ["Data Science", "SQL", "Математическая статистика", "Pandas", "Scikit-Learn"],
                        "Member 7": ["DevOps", "Machine Learning", "AirFlow", "Docker", "Kubernetes", "ONNX Runtime"]
                    }
                }
            ],
            "alpha": 0.6,
            "beta": 0.4,
            "confidence_percentile": 0.8
        }
    )
    assert response.status_code == 200
    assert "recommended_teams" in response.json()
    assert len(response.json()["recommended_teams"]) > 0
    for team in response.json()["recommended_teams"]:
        assert "team_id" in team
        assert "team_name" in team
        assert "hybrid_similarity" in team

def test_receive_new_data():
    # Test data following the NewDataRequest model structure
    response = client.post(
        "/new_data",
        json={
            "team_id": 1,
            "team_title": "Test Team",
            "case_title": "Test Case",
            "case_description": "This is a test case description",
            "user_fio": "John Doe",
            "person_skills": ["Python", "Data Science", "DevOps"],
            "case_required_roles": ["Backend Developer", "Тестировщик"]
        }
    )

    # Check response status code
    assert response.status_code == 200

    # Check response structure
    response_data = response.json()
    assert "message" in response_data
    assert "data" in response_data

    # Check response message
    assert response_data["message"] == "Новые данные успешно получены"

    # Check returned data matches input
    returned_data = response_data["data"]
    assert returned_data["team_id"] == 1
    assert returned_data["team_title"] == "Test Team"
    assert returned_data["case_title"] == "Test Case"
    assert returned_data["case_description"] == "This is a test case description"
    assert returned_data["user_fio"] == "John Doe"
    assert returned_data["person_skills"] == ["Python", "Data Science", "DevOps"]
    assert returned_data["case_required_roles"] == ["Backend Developer", "Тестировщик"]