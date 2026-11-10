import random
from collections import Counter,defaultdict
from pathlib import Path
BOOKS={"alice":"books/alice.txt","sherlock":"books/sherlock.txt"}
USE_TRIGRAMS=True
def load_words(path):
    text=(Path(__file__).parent/path).read_text(encoding="utf-8").lower()
    text=text.replace("\u2019","'").replace("\u2018","'")
    chars=[ch if ch.isalpha() or ch=="'" else " " for ch in text]
    words=[]
    for word in "".join(chars).split():
        word=word.strip("'")
        if word:
            words.append(word)
    return words
def build_bigrams(words):
    model=defaultdict(Counter)
    for current,following in zip(words,words[1:]):
        model[current][following]+=1
    return model
def build_trigrams(words):
    model=defaultdict(Counter)
    for a,b,c in zip(words,words[1:],words[2:]):
        model[(a,b)][c]+=1
    return model
def build_model(words):
    return{"unigrams":Counter(words),"bigrams":build_bigrams(words),"trigrams":build_trigrams(words)}
def top_k(counter,k):
    total=sum(counter.values())
    return [(word,count/total) for word,count in counter.most_common(k)]
def suggest(model,typed,k=3):
    if USE_TRIGRAMS and len(typed)>=2:
        key=(typed[-2],typed[-1])
        if key in model["trigrams"]:
            return top_k(model["trigrams"][key],k)
    if typed and typed[-1] in model["bigrams"]:
        return top_k(model["bigrams"][typed[-1]],k)
    return top_k(model["unigrams"],k)
def generate(model,start,length=15,mode="random"):
    typed=start.lower().split()
    for _ in range(length):
        options=suggest(model,typed,k=10)
        if not options:
            break
        if mode=="greedy":
            next_word=options[0][0]
        else:
            words=[w for w,_ in options]
            weights=[p for _,p in options]
            next_word=random.choices(words,weights=weights)[0]
        typed.append(next_word)
    return " ".join(typed)
def keyboard(model):
    print("\nType a word, or 1/2/3 to tap a suggestion. Enter on its own to finish.")
    typed=[]
    while True:
        chips=[w for w,_ in suggest(model,typed)]
        print("\n "+(" ".join(typed) or "(empty)"))
        print(" "+" ".join(f"[{i}] {w}" for i,w in enumerate(chips,1)))
        choice=input(" > ").strip().lower()
        if choice=="":
            break
        if choice in ("1","2","3") and int(choice)<=len(chips):
            typed.append(chips[int(choice)-1])
        else:
            typed.extend(choice.split())
    print("\nYour sentence:"," ".join(typed))
if __name__=="__main__":
    models={}
    for author,path in BOOKS.items():
        words=load_words(path)
        models[author]=build_model(words)
        print(f"{author:<9} {len(words):>7} words, {len(set(words)):>6} different words")
    print("\nSame start, different author:")
    for start in ["the","i am","said the"]:
        for author,model in models.items():
            options=", ".join(f"{w} ({p:.0%})" for w,p in suggest(model,start.split()))
            print(f" {start!r:<11} {author:<9} -> {options}")
    print("\nGreedy vs random writing (Alice):")
    print(" greedy:",generate(models["alice"],"alice was",mode="greedy"))
    print(" random:",generate(models["alice"],"alice was",mode="random"))
    author=input("\nPick your keyboard's author (alice / sherlock): ").strip().lower()
    keyboard(models.get(author,models["alice"]))