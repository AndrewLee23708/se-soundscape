import random 

def generateState(len):
    characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    return ''.join(random.choice(characters) for _ in range(len))

def extractDevice(devices):
    for device in devices:
        if device['name'] == 'Soundscapes':
            return device['id']
    return -1