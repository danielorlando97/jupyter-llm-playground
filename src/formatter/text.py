def print_texts(text):
    for sent in text.split('.'):
        print(sent.strip() + '.')
    
def print_list(l):
    for item in l:
        print(item.strip())