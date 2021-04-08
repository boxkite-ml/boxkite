import pickle

from boxkite.monitoring.service import ModelMonitoringService
from sklearn.datasets import load_diabetes
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split


def main():
    bunch = load_diabetes()
    X_train, X_test, Y_train, Y_test = train_test_split(bunch.data, bunch.target)
    model = LinearRegression()
    model.fit(X_train, Y_train)

    Y_pred = model.predict(X_test)
    print(f"Score: {r2_score(Y_test, Y_pred):.2f}")
    with open("./model.pkl", "wb") as f:
        pickle.dump(model, f)

    features = zip(*[bunch.feature_names, X_train.T])
    # features = [("age", [33, 23, 54, ...]), ("sex", [0, 1, 0]), ...]
    inference = list(Y_pred)
    # inference = [235.01351432, 211.79644624, 121.54947698, ...]
    ModelMonitoringService.export_text(
        features=features,
        inference=inference,
        path="./histogram.prom",
    )


if __name__ == "__main__":
    main()
