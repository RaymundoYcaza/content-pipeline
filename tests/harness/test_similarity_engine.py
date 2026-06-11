from pipeline.core.similarity_engine import SimilarityEngine


def test_cosine_similarity_identical_vectors():
    engine = SimilarityEngine()
    score = engine.cosine_similarity([1, 0, 0], [1, 0, 0])
    assert round(score, 5) == 1.0


def test_max_similarity():
    engine = SimilarityEngine()
    score = engine.max_similarity([1, 0], [[1, 0], [0, 1]])
    assert round(score, 5) == 1.0


def test_classify_review():
    engine = SimilarityEngine()
    result = engine.classify(0.8, review_threshold=0.72, reject_threshold=0.84)
    assert result == "review"
