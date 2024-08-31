from typing import TYPE_CHECKING

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from termcolor import colored

from translations import translations

if TYPE_CHECKING:
    from appstate import AppState


class IntentionClassifier:
    state: "AppState"
    vectorizer: TfidfVectorizer
    classifier_proba: LogisticRegression
    classifier: LinearSVC

    def __init__(self, state: "AppState") -> None:
        self.state = state
        self.vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(2, 3))
        self.classifier_proba = LogisticRegression()
        self.classifier = LinearSVC()
        corpus: list[str] = []
        target_vector: list[str] = []
        for capability, function in state.assistant.capabilities.items():
            for option in function.keys:
                corpus.append(option)
                target_vector.append(capability)
        # All the type ignores further are because parts of ndarrays are Unknown
        # Due to the heck non working type hints in numpy
        training_vector = self.vectorizer.fit_transform(corpus)  # type: ignore
        self.classifier_proba.fit(training_vector, target_vector)  # type: ignore
        self.classifier.fit(training_vector, target_vector)  # type: ignore

    def classify(self, request: str) -> str | None:
        predicted_intention = self.classifier.predict(  # type: ignore
            self.vectorizer.transform([request])  # type: ignore
        )[0]
        predict_index = list(self.classifier_proba.classes_).index(  # type: ignore
            predicted_intention
        )
        probabilities = self.classifier_proba.predict_proba(  # type: ignore
            self.vectorizer.transform([request])  # type: ignore
        )[0]
        highest_probability = probabilities[predict_index]
        print(
            colored(f'{translations["Probability:"]} {highest_probability}', "yellow")
        )
        return (
            predicted_intention
            if highest_probability > self.state.settings.intention_best_proba
            else None
        )
