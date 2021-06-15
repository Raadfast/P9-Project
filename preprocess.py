import math
import numpy as np
import json
import pickle

from numpy.lib.function_base import append
from utils import load_json_obj_from_file
from collections import OrderedDict
from utils import read_fastas_from_file

FASTA_DICTIONARY = {
    "A": 1, "C": 2, "B": 3, "E": 4, "D": 5, "G": 6,
	"F": 7, "I": 8, "H": 9, "K": 10, "M": 11, "L": 12,
    "O": 13, "N": 14, "Q": 15, "P": 16, "S": 17, "R": 18,
    "U": 19, "T": 20, "W": 21,
    "V": 22, "Y": 23, "X": 24,
    "Z": 25
}

FASTA_DICTIONARY_LENGTH = len(FASTA_DICTIONARY) # 25

CANONICAL_SMILES_DICTIONARY = {
    "#": 1, "%": 2, ")": 3, "(": 4, "+": 5, "-": 6,
    ".": 7, "1": 8, "0": 9, "3": 10, "2": 11, "5": 12,
    "4": 13, "7": 14, "6": 15, "9": 16, "8": 17, "=": 18,
    "A": 19, "C": 20, "B": 21, "E": 22, "D": 23, "G": 24,
    "F": 25, "I": 26, "H": 27, "K": 28, "M": 29, "L": 30,
    "O": 31, "N": 32, "P": 33, "S": 34, "R": 35, "U": 36,
    "T": 37, "W": 38, "V": 39, "Y": 40, "[": 41, "Z": 42,
    "]": 43, "_": 44, "a": 45, "c": 46, "b": 47, "e": 48,
    "d": 49, "g": 50, "f": 51, "i": 52, "h": 53, "m": 54,
    "l": 55, "o": 56, "n": 57, "s": 58, "r": 59, "u": 60,
    "t": 61, "y": 62
}

CANONICAL_SMILES_DICTIONARY_LENGTH = len(CANONICAL_SMILES_DICTIONARY) # 62

ISOMETRIC_SMILES_DICTIONARY = {
    "#": 29, "%": 30, ")": 31, "(": 1, "+": 32, "-": 33, "/": 34, ".": 2,
    "1": 35, "0": 3, "3": 36, "2": 4, "5": 37, "4": 5, "7": 38, "6": 6,
    "9": 39, "8": 7, "=": 40, "A": 41, "@": 8, "C": 42, "B": 9, "E": 43,
    "D": 10, "G": 44, "F": 11, "I": 45, "H": 12, "K": 46, "M": 47, "L": 13,
    "O": 48, "N": 14, "P": 15, "S": 49, "R": 16, "U": 50, "T": 17, "W": 51,
    "V": 18, "Y": 52, "[": 53, "Z": 19, "]": 54, "\\": 20, "a": 55, "c": 56,
    "b": 21, "e": 57, "d": 22, "g": 58, "f": 23, "i": 59, "h": 24, "m": 60,
    "l": 25, "o": 61, "n": 26, "s": 62, "r": 27, "u": 63, "t": 28, "y": 64
}

ISOMETRIC_SMILES_DICTIONARY_LENGTH = len(ISOMETRIC_SMILES_DICTIONARY) # 64

def tokenize_smiles(smiles):
    res = []
    for char in smiles:
        res.append(ISOMETRIC_SMILES_DICTIONARY(char))
    return res

def tokenize_sequence(sequence):
    res = []
    for char in sequence:
        res.append(FASTA_DICTIONARY(char))
    return res

def one_hot_smiles(smiles_string, MAX_SMI_LEN, dictionary):
	X = np.zeros((MAX_SMI_LEN, len(dictionary)), np.uint8)

	for i, ch in enumerate(smiles_string[:MAX_SMI_LEN]):
		X[i, (dictionary[ch]-1)] = 1

	return X

def one_hot_sequence(line, MAX_SEQ_LEN, dictionary):
	X = np.zeros((MAX_SEQ_LEN, len(dictionary)), np.uint8)
	for i, ch in enumerate(line[:MAX_SEQ_LEN]):
		X[i, (dictionary[ch])-1] = 1

	return X


def label_smiles(line, MAX_SMI_LEN, dictionary):
	X = np.zeros(MAX_SMI_LEN, np.float32)
	for i, ch in enumerate(line[:MAX_SMI_LEN]):
		X[i] = dictionary[ch] / 10

	return X

def label_sequence(line, MAX_SEQ_LEN, dictionary):
	X = np.zeros(MAX_SEQ_LEN, np.float32)

	for i, ch in enumerate(line[:MAX_SEQ_LEN]):
		X[i] = dictionary[ch] / 10

	return X

DATASETS_TO_PREPROCESS = ['davis']

def converter(y, convert):
    return -1 * math.log10(y/pow(10, 9)) if convert else y

def binarize_score(y, threshold):
    return [0, 1] if y >= threshold else [1, 0]

def process_score(y, threshold=None, convert=False):
    y = converter(y, convert)
    return binarize_score(y, threshold) if threshold else y

def process_Y(Y, threshold=None):
    processed_Y = []
    for y in Y:
        processed_Y.append(process_score(y, threshold, convert=True))
    return processed_Y

def molecule_protein_positions(dataset_name):
    return (1, 0) if dataset_name == 'kiba' else (0, 1)

class DataSet(object):
    def __init__(self, dataset_name):
        self.dataset_name = dataset_name
        self.json_dataset_path = f'./data/{dataset_name}.json'
        self.dataset_folder_path =  f'./data/{dataset_name}/'
        self.MAX_SMI_LEN = 100 # self.SEQLEN = seqlen
        self.MAX_SEQ_LEN = 1000 # self.SMILEN = smilen

        self.smiles_dictionary = ISOMETRIC_SMILES_DICTIONARY
        self.smiles_dictionary_size = ISOMETRIC_SMILES_DICTIONARY_LENGTH

        self.fasta_dictionary = FASTA_DICTIONARY
        self.fasta_dictionary_length = FASTA_DICTIONARY_LENGTH

    # TODO: Redo this function
    def load_embedded_dataset(self):
        molecules = load_json_obj_from_file(self.dataset_folder_path + 'molecules.json') #Changed to json fom npy
        proteins = load_json_obj_from_file(self.dataset_folder_path + 'proteins.json')
        Y = load_json_obj_from_file(self.dataset_folder_path + 'binding_affinities.json')
        if self.dataset_name in DATASETS_TO_PREPROCESS:
            Y = process_Y(Y)
        return np.asarray(molecules), np.asarray(proteins), np.asarray(Y)

    def parse_data(self, with_label=False):
        json_dataset = load_json_obj_from_file(self.json_dataset_path)
        molecule_idx, protein_idx = molecule_protein_positions(self.dataset_name)
        convert = True if self.dataset_name in DATASETS_TO_PREPROCESS else False
        print(f'Dataset conversion: {convert}')

        embedded_molecules = []
        embedded_proteins = []
        Y = []

        if with_label:
            for pair in json_dataset:
                embedded_molecules.append(label_smiles(pair[molecule_idx], self.MAX_SMI_LEN, self.smiles_dictionary))
                embedded_proteins.append(label_sequence(pair[protein_idx], self.MAX_SEQ_LEN, self.fasta_dictionary))
                Y.append(process_score(pair[2], convert=convert))
        else:
            for pair in json_dataset:
                embedded_molecules.append(one_hot_smiles(pair[molecule_idx], self.MAX_SMI_LEN, self.smiles_dictionary))
                embedded_proteins.append(one_hot_sequence(pair[protein_idx], self.MAX_SEQ_LEN, self.fasta_dictionary))
                Y.append(process_score(pair[2], convert=convert))
        return np.asarray(embedded_molecules), np.asarray(embedded_proteins), np.asarray(Y)

    def parse_flattened_data(self):
        json_dataset = load_json_obj_from_file(self.json_dataset_path)
        molecule_idx, protein_idx = molecule_protein_positions(self.dataset_name)
        convert = True if self.dataset_name in DATASETS_TO_PREPROCESS else False
        print(f'Dataset conversion: {convert}')

        embedded_flattened_pairs = []
        Y = []

        for pair in json_dataset:
            embedded_flattened_pairs.append(
                np.concatenate(
                    (
                        one_hot_smiles(pair[molecule_idx], self.MAX_SMI_LEN, self.smiles_dictionary).flatten(),
                        one_hot_sequence(pair[protein_idx], self.MAX_SEQ_LEN, self.fasta_dictionary).flatten()
                    )
                )
            )
            Y.append(process_score(pair[2], convert=convert))
        return np.asarray(embedded_flattened_pairs), np.asarray(Y)

    def load_folds(self):
        json_dataset = load_json_obj_from_file(self.json_dataset_path)
        test_fold = json.load(open(self.dataset_folder_path + 'folds/test_fold_setting1.txt'))
        train_folds = json.load(open(self.dataset_folder_path + 'folds/train_fold_setting1.txt'))
        molecule_idx, protein_idx = molecule_protein_positions(self.dataset_name)
        convert = True if self.dataset_name in DATASETS_TO_PREPROCESS else False

        train_molecules = []
        train_proteins = []
        train_Y = []

        test_molecules = []
        test_proteins = []
        test_Y = []

        # for fold in train_folds:
        #     for index in fold:
        #         train_molecules.append(one_hot_sequence(json_dataset[index][molecule_idx], self.MAX_SMI_LEN, self.smiles_dictionary))
        #         train_proteins.append(one_hot_sequence(json_dataset[index][protein_idx], self.MAX_SEQ_LEN, self.fasta_dictionary))
        #         train_Y.append(process_score(json_dataset[index][2], convert=convert))
        # return train_molecules, train_proteins, train_Y

        for index in test_fold:
            test_molecules.append(one_hot_smiles(json_dataset[index][molecule_idx], self.MAX_SMI_LEN, self.smiles_dictionary))
            test_proteins.append(one_hot_sequence(json_dataset[index][protein_idx], self.MAX_SEQ_LEN, self.fasta_dictionary))
            test_Y.append(process_score(json_dataset[index][2], convert=convert))
        return np.asarray(test_molecules), np.asarray(test_proteins), np.asarray(test_Y)

class AeDataSet(object):
    def __init__(self):
        self.MAX_SMI_LEN = 100
        self.MAX_SEQ_LEN = 1000

        self.smiles_dictionary = ISOMETRIC_SMILES_DICTIONARY
        self.smiles_dictionary_size = ISOMETRIC_SMILES_DICTIONARY_LENGTH

        self.fasta_dictionary = FASTA_DICTIONARY
        self.fasta_dictionary_length = FASTA_DICTIONARY_LENGTH

        self.kiba_molecules = set(load_json_obj_from_file('./data/kiba/ligands_iso.txt').values())
        self.kiba_proteins = set(load_json_obj_from_file('./data/kiba/proteins.txt').values())
        self.davis_molecules = set(load_json_obj_from_file('./data/davis/ligands_iso.txt').values())
        self.davis_proteins = set(load_json_obj_from_file('./data/davis/proteins.txt').values())

    def davis_kiba_molecules(self):
        molecules = self.kiba_molecules.union(self.davis_molecules)
        embedded_molecules = []
        for molecule in molecules:
            embedded_molecules.append(one_hot_sequence(molecule, self.MAX_SMI_LEN, self.smiles_dictionary))
        return np.asarray(embedded_molecules)

    def davis_kiba_proteins(self):
        proteins = self.kiba_proteins.union(self.davis_proteins)
        embedded_proteins = []
        for protein in proteins:
            embedded_proteins.append(one_hot_sequence(protein, self.MAX_SEQ_LEN, self.fasta_dictionary))
        return np.asarray(embedded_proteins)

    def load_external_data(self):
        molecules = load_json_obj_from_file('./data/drugbank-molecules.json')
        proteins = load_json_obj_from_file('./data/drugbank-proteins.json')
        embedded_molecules = []
        for molecule in molecules:
            if 'X' in molecule or 'x' in molecule or 'k' in molecule:
                continue
            embedded_molecules.append(one_hot_sequence(molecule, self.MAX_SMI_LEN, self.smiles_dictionary))
        del molecules
        embedded_proteins = []
        for protein in proteins:
            embedded_proteins.append(one_hot_sequence(protein, self.MAX_SEQ_LEN, self.fasta_dictionary))
        del proteins
        return np.asarray(embedded_molecules), np.asarray(embedded_proteins)
