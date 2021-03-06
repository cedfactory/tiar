import pandas as pd
import numpy as np
from tiase.fimport import synthetic,fimport
from tiase.findicators import findicators
from tiase.fdatapreprocessing import fdataprep
from tiase.ml import data_splitter,classifiers_factory
from tiase import alfred
import pytest

def compare_dataframes(df1, df2):
    if len(df1.columns) != len(df2.columns):
        print("{} vs {}".format(len(df1.columns), len(df2.columns)))
        return False
    for column in df1.columns:
        array1 = df1[column].to_numpy()
        array2 = df2[column].to_numpy()
        if np.allclose(array1, array2) == False:
            return False
    return True

class TestMlClassifier:

    def get_dataframe(self):
        y = synthetic.get_sinusoid(length=1000, amplitude=1, frequency=.1, phi=0, height = 0)
        df = synthetic.create_dataframe(y, 0.)
        df = findicators.add_technical_indicators(df, ["target"])
        df = findicators.remove_features(df, ["open","adj_close","low","high","volume"])
        df.dropna(inplace = True)
        return df

    def get_data_splitter(self):
        df = self.get_dataframe()
        ds = data_splitter.DataSplitterTrainTestSimple(df, target="target", seq_len=21)
        ds.split(0.7)
        return ds
 
    def test_classifier_evaluate_cross_validation(self):
        df = fimport.get_dataframe_from_csv("./tiase/data/test/google_stocks_data.csv")
        df = findicators.add_technical_indicators(df, ["target"])
        findicators.remove_features(df, ["open", "high", "low", "adj_close", "volume", "dividends", "stock_splits"])
        df = fdataprep.process_technical_indicators(df, ['missing_values'])
        print(df.head())

        model = classifiers_factory.ClassifiersFactory.get_classifier("lstm1", {'epochs': 10})
        ds = data_splitter.DataSplitterForCrossValidation(df.copy(), nb_splits=5)
        results = model.evaluate_cross_validation(ds, "target", True)
        print(results)

        equal = np.array_equal(results["accuracies"], [0.45, 0.525, 0.5125, 0.45, 0.6])
        assert(equal)
        assert(results["average_accuracy"] == pytest.approx(0.5075, 0.0001))

        df_generated = pd.read_csv("./tmp/cross_validation_analysis.csv")
        df_expected = pd.read_csv("./tiase/data/test/cross_validation_analysis_ref.csv")
        assert(compare_dataframes(df_generated, df_expected))

        df_generated = pd.read_csv("./tmp/cross_validation_results.csv")
        df_expected = pd.read_csv("./tiase/data/test/cross_validation_results_ref.csv")
        assert(compare_dataframes(df_generated, df_expected))

    def test_alfred_classifier_evaluate_cross_validation(self):
        alfred.execute("./tiase/data/test/alfred_cross_validation.xml")

        # expectations
        df_generated = pd.read_csv("./tmp/cross_validation_analysis.csv")
        df_expected = pd.read_csv("./tiase/data/test/cross_validation_analysis_ref.csv")
        assert(compare_dataframes(df_generated, df_expected))

        df_generated = pd.read_csv("./tmp/cross_validation_results.csv")
        df_expected = pd.read_csv("./tiase/data/test/cross_validation_results_ref.csv")
        assert(compare_dataframes(df_generated, df_expected))

    def _test_classifier_common(self, model, expected_results, epsilon):
        ds = self.get_data_splitter()
        model.fit(ds)
        model_analysis = model.get_analysis()

        assert(model_analysis["precision"] == pytest.approx(expected_results["precision"], epsilon))
        assert(model_analysis["recall"] == pytest.approx(expected_results["recall"], epsilon))
        assert(model_analysis["f1_score"] == pytest.approx(expected_results["f1_score"], epsilon))

    def test_classifier_alwayssameclass(self):
        model = classifiers_factory.ClassifiersFactory.get_classifier("same class")
        self._test_classifier_common(model, {"precision":0.482142, "recall":1., "f1_score":0.650602}, 0.00001)

    def test_classifier_alwaysasprevious(self):
        model = classifiers_factory.ClassifiersFactory.get_classifier("as previous")
        self._test_classifier_common(model, {"precision":0.962962, "recall":0.962962, "f1_score":0.962962}, 0.00001)

    def test_classifier_lstm1(self):
        model = classifiers_factory.ClassifiersFactory.get_classifier("lstm1", {'epochs': 20})
        self._test_classifier_common(model, {"precision":0.992647, "recall":1., "f1_score":0.996309}, 0.00001)

    def test_classifier_lstm2(self):
        model = classifiers_factory.ClassifiersFactory.get_classifier("lstm2", {'epochs': 20})
        self._test_classifier_common(model, {"precision":1., "recall":0.985185, "f1_score":0.992537}, 0.00001)

    def test_classifier_lstm3(self):
        model = classifiers_factory.ClassifiersFactory.get_classifier("lstm3", {'epochs': 20})
        self._test_classifier_common(model, {"precision":1., "recall":0.955555, "f1_score":0.977272}, 0.00001)

    def test_classifier_lstm_hao2020(self):
        model = classifiers_factory.ClassifiersFactory.get_classifier("lstmhao2020", {'epochs': 20})
        self._test_classifier_common(model, {"precision":1., "recall":0.985185, "f1_score":0.992537}, 0.1)

    def test_classifier_bilstm(self):
        model = classifiers_factory.ClassifiersFactory.get_classifier("bilstm")
        self._test_classifier_common(model, {"precision":0.9851852, "recall":0.985185, "f1_score":0.985185}, 0.1)

    def test_classifier_cnnbilstm(self):
        model = classifiers_factory.ClassifiersFactory.get_classifier("cnnbilstm")
        self._test_classifier_common(model, {"precision":0.984732, "recall":0.955555, "f1_score":0.969924}, 0.1)

    def test_classifier_svc(self):
        model = classifiers_factory.ClassifiersFactory.get_classifier("svc", {'kernel': 'linear', 'c': 0.025})
        self._test_classifier_common(model, {"precision":0.985185, "recall":0.985185, "f1_score":0.985185}, 0.00001)

    def test_classifier_xgboost(self):
        model = classifiers_factory.ClassifiersFactory.get_classifier("xgboost", {"n_estimators":100})
        self._test_classifier_common(model, {"precision":1., "recall":1., "f1_score":1.}, 0.00001)

    def test_classifier_decision_tree(self):
        model = classifiers_factory.ClassifiersFactory.get_classifier("decision tree")
        self._test_classifier_common(model, {"precision":1., "recall":1., "f1_score":1.}, 0.00001)

    def test_classifier_mlp(self):
        model = classifiers_factory.ClassifiersFactory.get_classifier("mlp", {'hidden_layer_sizes': 80, 'random_state': 1})
        self._test_classifier_common(model, {"precision":1., "recall":0.992592, "f1_score":0.996282}, 0.00001)

    def test_classifier_gaussian_naive_bayes(self):
        model = classifiers_factory.ClassifiersFactory.get_classifier("gaussian naive bayes")
        self._test_classifier_common(model, {"precision":0.948529, "recall":0.955555, "f1_score":0.952029}, 0.00001)

    def test_classifier_gaussian_process(self):
        model = classifiers_factory.ClassifiersFactory.get_classifier("gaussian process")
        self._test_classifier_common(model, {"precision":1., "recall":0.992592, "f1_score":0.996282}, 0.00001)
