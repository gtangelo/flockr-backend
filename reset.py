import pickle
from src.classes.Data import Data

data = Data()
with open('data.p', 'wb') as FILE:
    pickle.dump(data, FILE)