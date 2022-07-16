import os,openai, requests, random, base64
from concurrent.futures import ProcessPoolExecutor

'''OpenAI Key goes within the quotes'''
openai_key = 'Key Here'

# WP
wordpress_domain = '' ##DO NOT INCLUDE HTTPS OR WWW OR ANY TRAILING SLASHES. ONLY ENTER domainname.tld
wordpress_username = ''
wordpress_application_password = ''

wordpress_post_status = 'draft'

# OpenAI Tweaks
aiTemperature = 0.7
maxTokens = 100

'''Paths. Change these only if you know wtf you're doing'''
generated_content = 'new_content_files/'
uploaded_content = 'content_uploaded_to_wp/'

# Menu Items
singleq = ('''OpenAI is a bitch. Please format your questions clearly. 
        Sample Question: Tell me about guitar strings in 200 words
        Sample Answer below has only 199 words... OpenAI is a bitch

        Guitar strings are one of the most important aspects of the instrument, and the type of string you use can have 
        a big impact on your sound. There are a variety of different types of strings available, each with their own 
        unique properties.

        The most common type of string is the steel string, which is most often used on acoustic guitars. Steel strings 
        are known for their bright, clear tone and are a good choice for most styles of music.

        If you're looking for a warmer, more mellow sound, you might want to try a set of nylon strings. Nylon strings 
        are typically used on classical and flamenco guitars, and they offer a softer, more delicate sound.

        If you're looking for the ultimate in shredding capabilities, you'll want to check out a set of stainless steel 
        strings. These strings are incredibly durable and can stand up to serious abuse, making them a good choice for 
        metal and hard rock players.

        No matter what type of music you play, there's a set of guitar strings that's perfect for you. With so many 
        different types available, there's no reason not to experiment until you find the perfect set for your sound.

        So, type in your question accordingly: ''')

mainmenu = '''
    Howdy!

        Hit 
            1: Generate Articles and write them to file
            2: Generate Articles and post them to Wordpress
            3: Read Articles from file and post them to Wordpress
            4: Quit

        Wachawannado? : '''

a2menu = '''
        1: Imput single question here
        2: Read list of questions from file (One question per line)
        3: Go back to previous menu

        Wachawannadonow? : '''


def post2wp(q, i, flag, content):
    if flag:
        openai.api_key = openai_key
        content = openai.Completion.create(model="text-davinci-002", prompt=q, temperature=aiTemperature,
                                           max_tokens=maxTokens)["choices"][0]["text"]

    cred = f'{wordpress_username}:{wordpress_application_password}'
    tkn = base64.b64encode(cred.encode())
    wpheader = {'Authorization': 'Basic ' + tkn.decode('utf-8')}
    api_url = f'https://{wordpress_domain}/wp-json/wp/v2/posts'
    data = {
    'title' : q.capitalize(),
    'status': wordpress_post_status,
    'content': content,
    }
    print(content)
    wp_response = requests.post(url=api_url,headers=wpheader, json=data)
    print(f'Item no. {i+1} posted, with title{q} and post content \n\n {content} \n\n {wp_response})


def article2file(q,i):
    openai.api_key = openai_key
    response = openai.Completion.create(model="text-davinci-002", prompt=q, temperature=aiTemperature,
                                        max_tokens=maxTokens)["choices"][0]["text"]
    fname = q.replace(' ', '_') + '.txt'
    if os.path.exists(generated_content+fname):
        print('File with title already exists, renaming it with a random number prefix')
        os.replace(generated_content+fname,generated_content+str(random.randint(1000,9999))+fname)
    with open(generated_content+fname, 'w') as f:
        f.write(response)
        print(f'Item: {i} in list done.\nQuery string: {q}\nArticle:\n{response}\n\nSaved to {fname}')





if __name__ == '__main__':
    if not os.path.exists(generated_content):
        os.mkdir(generated_content)
    if not os.path.exists(uploaded_content):
        os.mkdir(uploaded_content)
    try:
        while True:
            try:
                wachawannado = int(input(mainmenu))
            except ValueError:
                print('\nPlease enter a number')
                continue
            if wachawannado == 1: #Article to file
                try:
                    wachawannadonow = int(input(a2menu))
                except ValueError:
                    print('\nPlease enter a number')
                    continue
                if wachawannadonow == 1: #a2f single
                    article2file(q=input(singleq), i=1)

                elif wachawannadonow == 2: #a2f file
                    if os.path.exists('q.txt'):
                        if not os.stat("file").st_size == 0:
                            with open('q.txt', 'r') as f:
                                with ProcessPoolExecutor(max_workers=16) as executor:
                                    for i, line in enumerate(f):
                                        executor.submit(article2file, i=i, q=line)
                        else:
                            print('\nq.txt is empty')
                            continue
                    else:
                        print("Can't find q.txt")
                        continue
                else:
                    continue

            elif wachawannado == 2: #Article to Wordpress
                try:
                    wachawannadonow = int(input(a2menu))
                except ValueError:
                    print('\nPlease enter a number')
                    continue
                if wachawannadonow == 1: #a2wp single
                    post2wp(q=input(singleq), i=1, flag = True, content = '')
                elif wachawannadonow == 2: #a2wp file
                    if os.path.exists('q.txt'):
                        if not os.stat("file").st_size == 0:
                            with open('q.txt', 'r') as f:
                                with ProcessPoolExecutor(max_workers=16) as executor:
                                    for i, line in enumerate(f):
                                        executor.submit(post2wp, q=line, i=i, flag = True, content = '')
                        else:
                            print('\nq.txt is empty')
                            continue
                    else:
                        print("Can't find q.txt")
                        continue
                else:
                    continue
            elif wachawannado == 3: #Files to WP
                contentfiles = os.listdir(generated_content)
                if contentfiles:
                    with ProcessPoolExecutor(max_workers=16) as executor:
                        for i, file in enumerate(contentfiles):
                            if file.endswith('.txt'):
                                print('Posting from file:', file)
                                with open(generated_content+file,'r') as f:
                                    executor.submit(post2wp, flag = False, content = f.read(), q = file.replace('_', '').replace('.txt',''), i=i)
                                os.replace(generated_content+file, uploaded_content+file)
                else:
                    print('Generated Content folder is empty')
            elif wachawannado == 4:
                print('Bye!')
                break
            else:
                print('Invalid Choice, try that again')
    except KeyboardInterrupt:
        print('Bye!')
