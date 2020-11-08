import pickle
from src.globals import DATA_FILE
from src.classes.Data import Data

data = Data()
with open(DATA_FILE, 'wb') as FILE:
    pickle.dump(data, FILE)