import pickle

from sklearn.datasets import load_diabetes
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from boxkite.monitoring.service import ModelMonitoringService


def main():
    bunch = load_diabetes()
    X_train, X_test, Y_train, Y_test = train_test_split(
        bunch.data, bunch.target
    )
    model = LinearRegression()
    model.fit(X_train, Y_train)

    print("Score: %.2f" % model.score(X_test, Y_test))
    with open("./model.pkl", "wb") as f:
        pickle.dump(model, f)

    features = zip(*[bunch.feature_names, X_train.T])
    # features = [("age", [33, 23, 54, ...]), ("sex", [0, 1, 0]), ...]
    ModelMonitoringService.export_text(
        features=features, path="./histogram.prom",
    )


if __name__ == "__main__":
    main()
