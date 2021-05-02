import numpy as np
import emetrics
from data_handler import save_predictions
# from lifelines.utils import concordance_index

def calc_accuracy(y_test, predictions):
    counter = 0
    for i in range(y_test.shape[0]):
        if y_test[i] == predictions[i]:
            counter += 1
    return round(counter * 100 / y_test.shape[0], 3), counter

def calc_mean_squared_error(y_test, predictions):
    sum = 0
    for i in range(y_test.shape[0]):
        sum += pow((y_test[i] - predictions[i]), 2)
    return round(sum / y_test.shape[0], 3)

def finalize_results(dataset_name, y_test, predictions):
    f = open(f'./data/{dataset_name}-y_test.txt', 'w')
    for y in y_test:
        f.write(f'{y}\n')
    f.close()
    temp_y_test = []
    temp_predictions = []
    for i in range(y_test.shape[0]):
        temp_predictions.append(np.argmax(predictions[i]))
        temp_y_test.append(np.argmax(y_test[i]))
    f = open(f'./data/{dataset_name}-temp_y_test.txt', 'w')
    for y in temp_y_test:
        f.write(f'{y}\n')
    f.close()
    return np.array(temp_y_test), np.array(temp_predictions)

def measure_and_print_performance(dataset_name, y_test, predictions):
    # y_test, predictions = finalize_results(dataset_name, y_test, predictions)
    # acc, counter = calc_accuracy(y_test, predictions)
    ci = emetrics.get_cindex(y_test, predictions)
    mse = emetrics.get_k(y_test, predictions)
    r2m = emetrics.get_rm2(y_test, predictions)
    aupr = emetrics.get_aupr(y_test, predictions)

    save_predictions(dataset_name, y_test, predictions)

    print(f'{dataset_name} dataset:')
    # print(f'\tAccuracy: {acc}%, predicted {counter} out of {y_test.shape[0]}')
    print(f'\tConcordance Index: {ci}')
    print(f'\tMean Squared Error: {mse}')
    print(f'\tr2m: {r2m}')
    print(f'\tAUPR: {aupr}')
