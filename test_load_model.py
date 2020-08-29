import torch

MODEL_PATH ="../d53865dd121f47b4af481c070ae2c62b_of_models_15_0.5_0_epochs10000_best_weight.h5"

checkpoint = torch.load(MODEL_PATH, map_location=torch.device('cpu'))
