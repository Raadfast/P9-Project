import base_model
import dcnn_model

from data_loader import load_dataset
from keras.callbacks import ModelCheckpoint
from sklearn.model_selection import train_test_split

def checkpoint_path(model_name, model_version=1):
    return f'./data/models/{model_name}/model_{model_version}.ckpt'

def checkpoint(checkpoint_path):
    return ModelCheckpoint(
        filepath=checkpoint_path,
        save_weights_only=True,
        verbose=1
    )

def get_dataset_split(dataset_name, X, Y):
    x_train, x_test, y_train, y_test = train_test_split(X, Y, train_size=0.8, random_state=0)
    return {
        'name': dataset_name,
        'x_train': x_train,
        'x_test': x_test,
        'y_train': y_train,
        'y_test': y_test
    }

def run_train_session(model_name, dataset_name, threshold, batch_size):
    X, Y = load_dataset(dataset_name)
    dataset = get_dataset_split(dataset_name, X, Y)
    checkpoint_callback = checkpoint(checkpoint_path('base_' + model_name))
    base_model.train(dataset, batch_size, 128, [checkpoint_callback])
    checkpoint_callback = checkpoint(checkpoint_path('dcnn_' + model_name))
    dcnn_model.train(dataset, batch_size, 100, [checkpoint_callback])

def run_test_session():
    kiba_X, kiba_Y = load_dataset('kiba')
    davis_X, davis_Y = load_dataset('davis')
    datasets = [{
        'name': 'kiba',
        'x_test': kiba_X,
        'y_test': kiba_Y
    }, {
        'name': 'davis',
        'x_test': davis_X,
        'y_test': davis_Y
    }]
    base_model.test(datasets, checkpoint_path('base_model'))
    dcnn_model.test(datasets, checkpoint_path('dcnn_model'))

def run_small_test_session():
    kiba_X, kiba_Y = load_dataset('kiba')
    davis_X, davis_Y = load_dataset('davis')
    kiba_x_train, kiba_x_test, kiba_y_train, kiba_y_test = train_test_split(kiba_X, kiba_Y, train_size=0.84, random_state=0)
    davis_x_train, davis_x_test, davis_y_train, davis_y_test = train_test_split(davis_X, davis_Y, train_size=0.84, random_state=0)
    datasets = [{
        'name': 'kiba',
        'x_test': kiba_x_test,
        'y_test': kiba_y_test
    # }, {
    #     'name': 'davis',
    #     'x_test': davis_x_test,
    #     'y_test': davis_y_test
    }]
    base_model.test(datasets, checkpoint_path('base_model_ba_kiba'))
    dcnn_model.test(datasets, checkpoint_path('dcnn_model_ba_kiba'))

# run_train_session('model_ba_kiba', 'kiba', 12.1, 256)
# run_train_session('model_ba_davis', 'davis', 7.0, 256)

run_small_test_session()