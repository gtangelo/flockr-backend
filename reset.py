import pickle
import os
from glob import glob
from src.globals import DATA_FILE
from src.classes.Data import Data

data = Data()
for image in glob('src/static/*'):
    os.remove(image)
with open(DATA_FILE, 'wb') as FILE:
    pickle.dump(data, FILE)