from abc import abstractmethod

from ..context import PredictionContext


class LogExporter:
    """Defines the exporter interface for emitting prediction context as log statements.

    Users who wish to support other backend storage systems should inherit from this class.
    """

    @abstractmethod
    def emit(self, prediction: PredictionContext):
        """
        Saves the full prediction context to an external datastore.

        :param prediction: The completed prediction
        :type prediction: PredictionContext
        """
        raise NotImplementedError
