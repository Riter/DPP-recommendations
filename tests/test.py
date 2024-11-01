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
            "person_skills": ["Python", "Docker", "Kubernetes", "Linux", "Machine Learning"],
            "teams": [
                {
                    "team_id": 1,
                    "name": "Система контроля качества продуктов АО Медитек",
                    "skills": {
                        "Member 1": ["C#", "Back-end разработка", "Git", "SQL", "Построение Rest API", "Docker"],
                        "Member 2": ["C#", "Back-end разработка", "Docker", "Git", "СУБД PostgreSQL", "Linux"],
                        "Member 3": ["HTML", "CSS", "React", "Git", "Next", "Tailwind", "JavaScript"],
                        "Member 4": ["DevOps", "Docker", "Kubernetes", "K8S", "Linux", "Helm", "Nginx", "Graphana"],
                        "Member 5": ["Умение работать с API", "PostgreSQL", "Python", "Atlassian stack [Jira, Confluence]", "Linux"],
                        "Member 6": ["Data Science", "SQL", "Pandas", "Математическая статистика", "Управление проектами"],
                        "Member 7": ["Canva", "Figma", "CSS", "UI/UX", "Adobe XD", "Photoshop"]
                    },
                    "required_roles": ["C# Backend", "Тестировщик", "Аналитик"]
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
                }
            ],
            "threshold": 0.5,
            "unfilled_role_weight": 1.5
        }
    )
    assert response.status_code == 200
    assert "recommended_team_id" in response.json()
    assert "recommended_team_name" in response.json()

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
                "required_roles": ["C# Backend", "Тестировщик", "Аналитик"]
            },
            "cases": [
                {
                    "id": 1,
                    "title": "Система контроля качества",
                    "description": "Система для контроля качества продукции",
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
            "beta": 0.4
        }
    )
    assert response.status_code == 200
    assert "id" in response.json()
    assert "title" in response.json()

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
            "beta": 0.4
        }
    )
    assert response.status_code == 200
    assert "team_id" in response.json()
    assert "team_name" in response.json()
    assert "hybrid_similarity" in response.json()
