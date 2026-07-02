import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from nonogram.api.main import app
from nonogram.api.routers import generator_router
from nonogram.api.schemas import GenerateRequest, DifficultyLevel
from nonogram.core.exceptions import GenerationTimeoutError

client = TestClient(app)


class TestGenerateEndpoint:
    def test_generation_timeout_becomes_a_422(self, monkeypatch):
        # In-tree RandomPatternSource rarely fails uniqueness on the first
        # try, so a genuine timeout is hard to hit through the real random
        # source in a fast, deterministic test — inject the failure directly.
        def fake_generate_puzzle(*args, **kwargs):
            raise GenerationTimeoutError("no valid puzzle found")

        monkeypatch.setattr(generator_router, "generate_puzzle", fake_generate_puzzle)

        request = GenerateRequest(
            num_rows=5, num_cols=5, difficulty=DifficultyLevel.EASY, max_attempts=1
        )
        with pytest.raises(HTTPException) as exc_info:
            generator_router.generate(request)
        assert exc_info.value.status_code == 422

    def test_generate_returns_a_puzzle_matching_the_requested_difficulty(self):
        response = client.post(
            "/puzzles/generate",
            json={"num_rows": 5, "num_cols": 5, "difficulty": "EASY", "max_attempts": 20, "seed": 42},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["difficulty"]["category"] == "EASY"
        assert body["exact_match"] is True
        assert len(body["row_clues"]) == 5
        assert len(body["col_clues"]) == 5
        assert "solution" not in body

    def test_generate_is_deterministic_for_a_given_seed(self):
        payload = {"num_rows": 5, "num_cols": 5, "difficulty": "EASY", "max_attempts": 20, "seed": 7}
        first = client.post("/puzzles/generate", json=payload).json()
        second = client.post("/puzzles/generate", json=payload).json()
        assert first == second

    def test_generate_rejects_non_positive_dimensions(self):
        response = client.post(
            "/puzzles/generate",
            json={"num_rows": 0, "num_cols": 5, "difficulty": "EASY", "max_attempts": 20},
        )
        assert response.status_code == 422

    def test_generate_rejects_invalid_difficulty_level(self):
        response = client.post(
            "/puzzles/generate",
            json={"num_rows": 5, "num_cols": 5, "difficulty": "IMPOSSIBLE", "max_attempts": 20},
        )
        assert response.status_code == 422


class TestSolveEndpoint:
    def test_solve_returns_a_valid_solution(self):
        generated = client.post(
            "/puzzles/generate",
            json={"num_rows": 5, "num_cols": 5, "difficulty": "EASY", "max_attempts": 20, "seed": 42},
        ).json()

        response = client.post(
            "/puzzles/solve",
            json={"row_clues": generated["row_clues"], "col_clues": generated["col_clues"]},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "SOLVED"
        assert len(body["solution"]) == 5
        assert len(body["solution"][0]) == 5

    def test_solve_reports_contradiction_for_impossible_clues(self):
        response = client.post(
            "/puzzles/solve",
            json={"row_clues": [[2], [2]], "col_clues": [[1], [2]]},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "CONTRADICTION"
        assert body["solution"] is None

    def test_solve_rejects_an_invalid_clue(self):
        response = client.post(
            "/puzzles/solve",
            json={"row_clues": [[-1]], "col_clues": [[1]]},
        )
        assert response.status_code == 422

    def test_solve_respects_max_backtrack_depth(self):
        response = client.post(
            "/puzzles/solve",
            json={
                "row_clues": [[1, 1], [1, 1], [1, 1], [1, 1]],
                "col_clues": [[1, 1], [1, 1], [1, 1], [1, 1]],
                "max_backtrack_depth": 0,
            },
        )
        assert response.status_code == 200
        assert response.json()["status"] == "MAX_DEPTH_EXCEEDED"


def test_docs_are_available():
    response = client.get("/docs")
    assert response.status_code == 200


@pytest.mark.parametrize("path", ["/openapi.json"])
def test_openapi_schema_is_available(path):
    response = client.get(path)
    assert response.status_code == 200
    assert "/puzzles/generate" in response.json()["paths"]
    assert "/puzzles/solve" in response.json()["paths"]
