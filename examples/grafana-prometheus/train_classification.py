import pickle

from boxkite.monitoring.service import ModelMonitoringService
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split


def main():
    bunch = load_iris()
    X_train, X_test, Y_train, Y_test = train_test_split(
        bunch.data,
        [bunch.target_names[y] for y in bunch.target],
        test_size=61,
    )
    model = LogisticRegression()
    model.fit(X_train, Y_train)

    Y_pred = model.predict(X_test)
    print("Score: %.2f" % f1_score(Y_test, Y_pred, average="weighted"))
    with open("./model.pkl", "wb") as f:
        pickle.dump(model, f)

    features = zip(*[bunch.feature_names, X_train.T])
    # features = [("age", [33, 23, 54, ...]), ("sex", [0, 1, 0]), ...]
    inference = list(Y_pred)
    # inference = ['setosa', 'virginica', 'setosa', ...]
    ModelMonitoringService.export_text(
        features=features,
        inference=inference,
        path="./histogram.prom",
    )


if __name__ == "__main__":
    main()
