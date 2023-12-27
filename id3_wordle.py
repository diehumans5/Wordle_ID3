from math import log2
import re
from flask import Flask, render_template, request, redirect, url_for, session
from flask import flash
import random
 
words = []
read_file = open('word_l_2.txt','r')
content = read_file.read()
words = re.findall(r'[a-z]{5}',content)

def out_put(a,b):
    used = [0,0,0,0,0]
    b_used = [0,0,0,0,0]
    res = 0
    for i in range(5):
        if a[i] == b[i]:
            used[i] = 1
            b_used[i] = 1
            res+=2*(3**(4-i))
    for i in range(5):
        if b[i] in a and b_used[i] == 0:
            ind = a.index(b[i])
            if used[ind] != 1:
                used[ind] = 1
                res+=1*(3**(4-i))
    return res

def match(word,pat,words):
    pattern = ''
    pres = []
    not_pres = []
    res = []
    used = [0,0,0,0,0]
    let = ['-','-','-','-','-']
    for i in range(5):
        curr = pat%3
        if curr == 2:
            pattern = f"[{word[4-i]}]"+pattern
            used[4-i] = 1
        elif curr == 1:
            pres.append(word[4-i])
            let[4-i] = word[4-i]
            pattern = '[a-z]'+pattern
        else:
            pattern = '[a-z]'+pattern
            if word[4-i] not in pres and word[4-i] not in not_pres:
                not_pres.append(word[4-i])
        pat = pat//3

    for i in pres:
        if i in not_pres:
            not_pres.pop(not_pres.index(i))
    pattern = re.compile(pattern)
    res = re.findall(pattern,str(words))
    new_res = []
    count = 0
    oth_count = 0
    for i in res:
        new_s = ''
        count = 0
        oth_count = 0
        for n in range(5):
            if used[n] == 0:
                new_s = new_s+i[n]
            if i[n] == let[n]:
                #print(i,let)
                oth_count+=1
        for k in pres:
            if k in new_s:
                count+=1
        for k in not_pres:
            if k in new_s:
                oth_count+=1
        if count == len(pres) and oth_count==0:
            new_res.append(i)

    return new_res

app = Flask(__name__)
app.secret_key = '97531'
pres_words = []
for i in range(241):
    pres_words.append(0)

to_be_guessed = ''
possible_words = words
guesses = []
colours = []
@app.route("/",methods=['GET','POST'])
def main():
    global pres_words,words,possible_words,to_be_guessed,colours,guesses
    print(to_be_guessed)
    if request.method == 'GET':
        to_be_guessed = random.choice(words)
        possible_words = words
        guesses = []
        colours = []
        res = []
        for i in words:
            tot = 0
            for n in range(241):
                pres_words[n] = 0
            for k in words:
                if i!=k:
                    pres_words[out_put(i,k)]+=1
            for n in range(241):
                if pres_words[n]!=0:
                    tot+=pres_words[n]*log2(1/pres_words[n])
            tot = tot/len(words)
            res.append([i,tot])
        res.sort(key=lambda x:x[1],reverse=True)
        return render_template('id3_front.html',bestwords = res)
    else:
        res = []
        new_word = request.form['new_word']
        '''if new_word == to_be_guessed:
            flash('Correct!')
            to_be_guessed = random.choice(words)
            guesses = []
            colours = []
            possible_words = words
            return redirect(url_for('main'))'''
        guesses.append(new_word)
        pat = out_put(to_be_guessed,new_word)
        possible_words = match(new_word,pat,possible_words)
        for i in words:
            tot = 0
            for n in range(241):
                pres_words[n] = 0
            for k in possible_words:
                if i!=k:
                    pres_words[out_put(i,k)]+=1
            for n in range(241):
                if pres_words[n]!=0:
                    tot+=pres_words[n]*log2(1/pres_words[n])
            if len(possible_words)>0:
                tot = tot/len(possible_words)
            res.append([i,tot])
        res.sort(key=lambda x:x[1],reverse=True)
        colour = []
        for i in range(5):
            col = pat%3
            if col == 2:
                colour.insert(0,'lime')
            elif col == 1:
                colour.insert(0,'gold')
            else:
                colour.insert(0,'silver')
            pat = pat//3
        colours.append(colour)
        random.shuffle(possible_words)
        return render_template('id3_front.html',bestwords = res,posswords = possible_words,guesses = guesses,lent = len(guesses),colours = colours)

    
if __name__ == '__main__':
    app.run(debug=True)
