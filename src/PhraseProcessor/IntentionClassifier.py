""""""

from re import IGNORECASE, escape, sub
from sklearn.calibration import LinearSVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from termcolor import colored

from src import State
from src.Interfaces import PhraseProcessorInterface


class IntentionClassifier(PhraseProcessorInterface):
    """"""

    vectorizer: TfidfVectorizer
    classifier_proba: LogisticRegression
    classifier: LinearSVC
    state: State | None
    _loaded_modules: list[int]

    def __init__(self) -> None:
        self.vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(2, 3))
        self.classifier_proba = LogisticRegression()
        self.classifier = LinearSVC()
        self._loaded_modules = []
        self.state = None
        return

    def process(self, phrase: str) -> str:
        if self.state is None:
            raise RuntimeError(
                "Intention classifier process was called without before start handler"
            )
        cleared = sub(
            rf'\b{escape(self.state["settings"]["assistant_name"])}\b',
            "",
            phrase,
            flags=IGNORECASE,
        ).strip()
        if cleared == "" or cleared.isspace():
            return phrase
        predicted_intention = self.classifier.predict(  # type: ignore
            self.vectorizer.transform([cleared])  # type: ignore
        )[0]
        predict_index = list(self.classifier_proba.classes_).index(  # type: ignore
            predicted_intention  # type: ignore
        )
        probabilities = self.classifier_proba.predict_proba(  # type: ignore
            self.vectorizer.transform([cleared])  # type: ignore
        )[0]
        highest_probability = probabilities[predict_index]
        print(colored(f"Probability: {highest_probability}", "yellow"))
        return (
            f"{predicted_intention} {cleared}"
            if highest_probability
            > float(self.state["settings"]["intention_best_proba"])
            else phrase
        )

    def before_start(self, state: State) -> None:
        self.state = state
        if self._loaded_modules != (
            actual_modules := [id(module) for module in state["actions-modules"]]
        ):
            self._loaded_modules = actual_modules
            corpus: list[str] = []
            target_vector: list[str] = []
            for action in [
                x
                for module in state["actions-modules"]
                for x in module.get_actions(state)
            ]:
                for option in action.keys:
                    corpus.append(option)
                    target_vector.append(action.uid)
            # All the type ignores further are because parts of ndarrays are Unknown
            # Due to the heck non working type hints in numpy
            training_vector = self.vectorizer.fit_transform(corpus)  # type: ignore
            self.classifier_proba.fit(training_vector, target_vector)  # type: ignore
            self.classifier.fit(training_vector, target_vector)  # type: ignore
        return
