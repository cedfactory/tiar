from . import classifier,analysis
from sklearn.model_selection import GridSearchCV

class HPTGridSearch(classifier.Classifier):
    """
    reference : https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html
    """

    def __init__(self, model, data_splitter, params=None):
        super().__init__(model, data_splitter, params)

        self.param_grid = None
        self.scoring = 'roc_auc' # \in {'roc_auc', ''}
        if params:
            self.param_grid = params.get("param_grid", self.param_grid)
            self.scoring = params.get("scoring", self.scoring)

        self.data_splitter = data_splitter
        self.model = model
        self.param_grid = self.model.get_param_grid()

    def build(self):
        self.tuner = GridSearchCV(estimator=self.model.get_model(), param_grid=self.param_grid, scoring=self.scoring)

    def fit(self):
        self.build()
        self.tuner.fit(self.data_splitter.X_train, self.data_splitter.y_train)
        return self.tuner.best_params_

    def get_analysis(self):
        y_test_pred, y_test_prob = classifier.get_pred_and_prob_with_predict_pred_and_predict_proba(self.tuner, self.data_splitter)
        return analysis.classification_analysis(self.data_splitter.X_test, self.data_splitter.y_test, y_test_pred, y_test_prob)

    def save(self, filename):
        print("HPTGridSearch.save() is not implemented")

    def load(self, filename):
        print("HPTGridSearch.load() is not implemented")