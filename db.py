import dataset
db = dataset.connect('sqlite:///storage.db')
settings = db['settings']
chats = db['chats']
conversations = db['conversations']
