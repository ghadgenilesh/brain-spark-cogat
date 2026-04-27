#!/usr/bin/env python3
"""
Generate unique CoGAT-style questions.
  - Quantitative: programmatic (no text reuse)
  - Verbal / Non-verbal: large hand-crafted template banks
Output: questions.json (plain array, zero duplicate text)
"""

import json, random
from collections import Counter

random.seed(42)

BATTERY_MAP = {
    "verbal-analogies":      "verbal",
    "verbal-classification": "verbal",
    "sentence-completion":   "verbal",
    "number-series":         "quantitative",
    "number-analogies":      "quantitative",
    "number-puzzles":        "quantitative",
    "figure-matrices":       "non-verbal",
    "paper-folding":         "non-verbal",
    "figure-classification": "non-verbal",
}

questions = []
seen_texts = set()
_qid = [1]

def make_options(opts):
    return [{"label": l, "text": str(o), "svg": None}
            for l, o in zip(["A","B","C","D"], opts)]

def add(grade, qtype, diff, text, opts, ai, expl):
    t = text.strip()
    if t in seen_texts:
        return
    seen_texts.add(t)
    questions.append({
        "id": f"Q{_qid[0]:05d}", "grade": grade,
        "battery": BATTERY_MAP[qtype], "type": qtype,
        "difficulty": diff, "text": t, "svg": None,
        "options": make_options(opts), "answer": ai,
        "explanation": expl,
        "tags": [qtype.split("-")[0], grade, diff],
    })
    _qid[0] += 1

def distract(correct, extras, min_val=0):
    seen = {correct}; out = []
    for v in extras:
        v = int(v)
        if v not in seen and v > min_val:
            seen.add(v); out.append(v)
        if len(out) == 3: break
    i = 1
    while len(out) < 3:
        v = correct + i
        if v not in seen: seen.add(v); out.append(v)
        i += 1
    return out

def sw4(correct, wrongs):
    opts = [correct] + list(wrongs)[:3]
    random.shuffle(opts)
    return opts, opts.index(correct)

# ─── NUMBER SERIES ────────────────────────────────────────────────
# ascending arithmetic
for start in range(1, 55, 2):
    for step in range(1, 22, 1):
        seq = [start + step*i for i in range(5)]
        nxt = seq[-1] + step
        if nxt > 500: continue
        s = ", ".join(str(x) for x in seq)
        opts, ai = sw4(nxt, distract(nxt, [step, -step, step*2, 1, -1]))
        if step<=3 and start<=15: d,g = "easy",   random.choice(["K","1","2"])
        elif step<=8 and start<=30: d,g = "medium",random.choice(["2","3","4"])
        else:                       d,g = "hard",  random.choice(["4","5","6","7"])
        add(g,"number-series",d,f"What comes next?  {s}, ___",opts,ai,
            f"Add {step} each time. {seq[-1]}+{step}={nxt}.")

# descending arithmetic
for start in range(100,8,-5):
    for step in range(2,18,2):
        seq = [start-step*i for i in range(5)]
        if seq[-1]<1: continue
        nxt = seq[-1]-step
        if nxt<0: continue
        s = ", ".join(str(x) for x in seq)
        opts,ai = sw4(nxt, distract(nxt,[step,-step,step*2,1,-1]))
        if step<=4 and start<=30: d,g = "easy",  random.choice(["1","2","3"])
        elif step<=8:             d,g = "medium",random.choice(["3","4","5"])
        else:                     d,g = "hard",  random.choice(["5","6","7"])
        add(g,"number-series",d,f"What comes next?  {s}, ___",opts,ai,
            f"Subtract {step} each time. {seq[-1]}-{step}={nxt}.")

# geometric
for base in range(1,7):
    for ratio in [2,3,4,5]:
        seq = [base*(ratio**i) for i in range(5)]
        nxt = base*(ratio**5)
        if nxt>200000: continue
        s = ", ".join(str(x) for x in seq)
        opts,ai = sw4(nxt, distract(nxt,[base,-base,seq[-1],nxt//ratio,nxt+ratio]))
        if ratio==2 and base<=3: d,g = "medium",random.choice(["2","3","4"])
        elif ratio<=3:           d,g = "hard",  random.choice(["4","5","6"])
        else:                    d,g = "hard",  random.choice(["6","7","8"])
        add(g,"number-series",d,f"What comes next?  {s}, ___",opts,ai,
            f"Multiply by {ratio} each time. {seq[-1]}x{ratio}={nxt}.")

# perfect squares
for offset in range(0,5):
    sq = [(n+offset)**2 for n in range(1,6)]
    nxt = (6+offset)**2
    s = ", ".join(str(x) for x in sq)
    opts,ai = sw4(nxt, distract(nxt,[nxt//4,-10,10,5,-5,8]))
    d = "easy" if offset==0 else ("medium" if offset<=2 else "hard")
    g = random.choice(["3","4","5"] if offset<=2 else ["5","6","7"])
    add(g,"number-series",d,f"What comes next?  {s}, ___",opts,ai,
        f"Perfect squares. Next is {6+offset}^2={nxt}.")

# perfect cubes
for offset in range(0,4):
    cu = [(n+offset)**3 for n in range(1,5)]
    nxt = (5+offset)**3
    s = ", ".join(str(x) for x in cu)
    opts,ai = sw4(nxt, distract(nxt,[25,-25,50,-50,100]))
    add(random.choice(["6","7","8"]),"number-series","hard",
        f"What comes next?  {s}, ___",opts,ai, f"Perfect cubes. {5+offset}^3={nxt}.")

# fibonacci variants
for seq, nxt, d, gs, expl in [
    ([1,1,2,3,5],8,"medium",["3","4","5"],"Fibonacci: 3+5=8."),
    ([1,2,3,5,8],13,"medium",["4","5","6"],"Fibonacci: 5+8=13."),
    ([2,3,5,8,13],21,"hard",["5","6","7"],"Fibonacci-like: 8+13=21."),
    ([1,3,4,7,11],18,"hard",["6","7","8"],"Add two before: 7+11=18."),
    ([0,1,1,2,3],5,"easy",["3","4"],"Fibonacci starting 0. 2+3=5."),
    ([3,5,8,13,21],34,"hard",["7","8"],"Fibonacci-like: 13+21=34."),
    ([2,4,6,10,16],26,"hard",["7","8"],"Fibonacci-like: 10+16=26."),
    ([1,4,5,9,14],23,"hard",["6","7"],"Add two before: 9+14=23."),
]:
    s = ", ".join(str(x) for x in seq)
    opts,ai = sw4(nxt, distract(nxt,[1,-1,2,3]))
    add(random.choice(gs),"number-series",d,f"What comes next?  {s}, ___",opts,ai,expl)

# alternating step
for seq, nxt, d, gs, expl in [
    ([1,2,4,5,7],8,"medium",["3","4"],"+1,+2,+1,+2... 7+1=8."),
    ([2,5,4,7,6],9,"hard",["5","6"],"+3,-1,+3,-1... 6+3=9."),
    ([10,12,9,11,8],10,"hard",["6","7"],"+2,-3,+2,-3... 8+2=10."),
    ([1,3,2,4,3],5,"medium",["3","4","5"],"+2,-1,+2,-1... 3+2=5."),
    ([5,10,8,16,14],28,"hard",["7","8"],"x2,-2,x2,-2... 14x2=28."),
    ([3,6,4,8,6],12,"hard",["6","7"],"x2,-2,x2,-2... 6x2=12."),
    ([2,4,3,6,5],10,"medium",["4","5"],"Pattern: +2,-1,+3,-1... 5x2=10."),
]:
    s = ", ".join(str(x) for x in seq)
    opts,ai = sw4(nxt, distract(nxt,[1,-1,2,seq[-1]]))
    add(random.choice(gs),"number-series",d,f"What comes next?  {s}, ___",opts,ai,expl)

# primes
PRIMES=[2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71]
for si in range(0, len(PRIMES)-5):
    seq = PRIMES[si:si+5]; nxt = PRIMES[si+5]
    s = ", ".join(str(x) for x in seq)
    opts,ai = sw4(nxt, distract(nxt,[1,-1,2,4]))
    d = "easy" if si==0 else ("medium" if si<=3 else "hard")
    g = random.choice(["5","6"] if si<=4 else ["6","7","8"])
    add(g,"number-series",d,
        f"What comes next in this sequence of prime numbers?  {s}, ___",opts,ai,
        f"Consecutive primes. The next prime after {seq[-1]} is {nxt}.")

# increasing differences
for a0 in [0,1,2,3,5,10]:
    seq=[a0]
    for dd in range(1,5): seq.append(seq[-1]+dd)
    nxt=seq[-1]+5; s=", ".join(str(x) for x in seq)
    opts,ai=sw4(nxt, distract(nxt,[1,-1,4,6]))
    diff="medium" if a0<=3 else "hard"
    g=random.choice(["4","5"] if a0<=3 else ["5","6","7"])
    add(g,"number-series",diff,f"What comes next?  {s}, ___",opts,ai,
        f"Differences: 1,2,3,4 — next gap=5. {seq[-1]}+5={nxt}.")

# ─── NUMBER ANALOGIES ─────────────────────────────────────────────
def na_text(a,b,c,d): return f"{a} is to {b} as {c} is to ___."

# multiply by k
for k in range(2,9):
    used=set()
    for a in range(2,20):
        b=a*k
        if b>900: continue
        for c in range(2,20):
            if c==a or (a,c) in used: continue
            d=c*k; used.add((a,c))
            opts,ai=sw4(d, distract(d,[k,-k,c,b-a,d+k]))
            if k<=3 and a<=5: diff,gr="easy",  random.choice(["1","2","3"])
            elif k<=5:        diff,gr="medium",random.choice(["3","4","5"])
            else:             diff,gr="hard",  random.choice(["5","6","7"])
            add(gr,"number-analogies",diff,na_text(a,b,c,d),opts,ai,
                f"Rule: x{k}. {a}x{k}={b}, so {c}x{k}={d}.")
            break

# add k
for k in range(2,25,2):
    for a in range(1,18,3):
        b=a+k; c=a+random.randint(2,12); d=c+k
        opts,ai=sw4(d, distract(d,[1,-1,k,-k,2]))
        if k<=5:  diff,gr="easy",  random.choice(["K","1","2"])
        elif k<=12: diff,gr="medium",random.choice(["2","3","4"])
        else:       diff,gr="hard",  random.choice(["4","5","6"])
        add(gr,"number-analogies",diff,na_text(a,b,c,d),opts,ai,
            f"Rule: +{k}. {a}+{k}={b}, so {c}+{k}={d}.")

# square
for a in range(2,14):
    b=a*a; c=a+random.randint(1,6); d=c*c
    opts,ai=sw4(d, distract(d,[c,d//2,c*2,b]))
    diff="medium" if a<=5 else "hard"
    gr=random.choice(["3","4","5"] if a<=5 else ["5","6","7","8"])
    add(gr,"number-analogies",diff,na_text(a,b,c,d),opts,ai,
        f"Rule: square. {a}^2={b}, so {c}^2={d}.")

# cube
for a in range(2,7):
    b=a**3; c=a+1; d=c**3
    opts,ai=sw4(d, distract(d,[20,-20,b+10,d+5]))
    add(random.choice(["6","7","8"]),"number-analogies","hard",
        na_text(a,b,c,d),opts,ai, f"Rule: cube. {a}^3={b}, so {c}^3={d}.")

# divide by k
for k in [2,3,4,5]:
    for a in range(k*2, k*15, k):
        b=a//k; c=((a+k*random.randint(2,6))//k)*k; d=c//k
        if c==a: continue
        opts,ai=sw4(d, distract(d,[1,-1,k,d+k//2]))
        diff="easy" if k==2 else ("medium" if k<=3 else "hard")
        gr=random.choice(["2","3"] if k==2 else (["3","4","5"] if k==3 else ["5","6","7"]))
        add(gr,"number-analogies",diff,na_text(a,b,c,d),opts,ai,
            f"Rule: /{k}. {a}/{k}={b}, so {c}/{k}={d}.")

# square root
sq_pairs=[(4,2),(9,3),(16,4),(25,5),(36,6),(49,7),(64,8),(81,9),(100,10),(121,11),(144,12)]
for i in range(len(sq_pairs)-1):
    a,b=sq_pairs[i]; c,d=sq_pairs[i+1]
    opts,ai=sw4(d, distract(d,[1,-1,2,b]))
    diff="medium" if i<=4 else "hard"
    gr=random.choice(["4","5"] if i<=4 else ["5","6","7"])
    add(gr,"number-analogies",diff,na_text(a,b,c,d),opts,ai,
        f"Rule: square root. sqrt({a})={b}, so sqrt({c})={d}.")

# factorial
fact={1:1,2:2,3:6,4:24,5:120,6:720}
for a in range(1,5):
    b=fact[a]; c=a+1; d=fact[c]
    opts,ai=sw4(d, distract(d,[b,d//2,d+10,c*b]))
    add(random.choice(["7","8"]),"number-analogies","hard",
        na_text(a,b,c,d),opts,ai, f"Rule: factorial. {a}!={b}, so {c}!={d}.")

# ─── NUMBER PUZZLES ────────────────────────────────────────────────
# missing addend
for total in range(3,20):
    for part in range(1,total):
        missing=total-part
        if missing<=0 or missing==part: continue
        opts,ai=sw4(missing, distract(missing,[1,-1,part,total]))
        if total<=8:   d,g="easy",  random.choice(["K","1"])
        elif total<=13: d,g="medium",random.choice(["1","2"])
        else:           d,g="hard",  random.choice(["2","3"])
        add(g,"number-puzzles",d,f"___ + {part} = {total}. What is the missing number?",
            opts,ai, f"{total}-{part}={missing}.")

# subtraction missing
for total in range(4,20):
    for part in range(1,total-1):
        missing=total-part
        opts,ai=sw4(missing, distract(missing,[1,-1,part,total]))
        if total<=10: d,g="easy",  random.choice(["1","2"])
        else:         d,g="medium",random.choice(["2","3"])
        add(g,"number-puzzles",d,f"{total} - ___ = {part}. What is the missing number?",
            opts,ai, f"{total}-{missing}={part}.")

# linear equations
for a in range(2,9):
    for xv in range(2,16):
        for b in range(0,20,3):
            c=a*xv+b
            if c>120: continue
            opts,ai=sw4(xv, distract(xv,[1,-1,a,b,c-b]))
            if c<=20 and a<=3: d,g="easy",  random.choice(["3","4"])
            elif c<=60:        d,g="medium",random.choice(["4","5","6"])
            else:              d,g="hard",  random.choice(["6","7","8"])
            add(g,"number-puzzles",d,f"Solve for n:  {a}n + {b} = {c}",opts,ai,
                f"{a}n={c}-{b}={c-b}, n={xv}.")

# rectangle area / perimeter
for l,w in [(2,3),(3,4),(4,5),(5,6),(6,7),(7,8),(8,9),(3,7),(4,8),(5,9),
            (6,10),(10,12),(8,11),(9,13),(2,9),(3,11),(5,12),(7,10)]:
    area=l*w; perim=2*(l+w)
    for what,tgt,formula in [("area",area,f"{l}x{w}={area}"),
                              ("perimeter",perim,f"2x({l}+{w})={perim}")]:
        opts,ai=sw4(tgt, distract(tgt,[l,w,l+w,tgt+l,tgt-w]))
        if l<=5:   d,g="easy",  random.choice(["3","4"])
        elif l<=8: d,g="medium",random.choice(["4","5","6"])
        else:      d,g="hard",  random.choice(["6","7","8"])
        add(g,"number-puzzles",d,
            f"A rectangle has length {l} and width {w}. What is its {what}?",
            opts,ai, f"{what.capitalize()} = {formula}.")

# percentages
for pct in [10,15,20,25,30,40,50,60,75,80]:
    for base in [20,40,50,60,80,100,120,150,200,250]:
        result=pct*base//100
        if result==0 or (pct*base)%100!=0: continue
        opts,ai=sw4(result, distract(result,[5,-5,result//2,result*2]))
        if pct in [10,50] and base<=100: d,g="easy",  random.choice(["4","5"])
        elif pct in [25,20]:             d,g="medium",random.choice(["5","6"])
        else:                            d,g="hard",  random.choice(["6","7","8"])
        add(g,"number-puzzles",d,f"What is {pct}% of {base}?",opts,ai,
            f"{pct}% of {base} = {pct}/100 x {base} = {result}.")

# multiplication word problems
for bags in range(2,10):
    for each in range(2,12):
        total=bags*each
        if total>100: continue
        opts,ai=sw4(total, distract(total,[bags,each,bags+each,total+bags]))
        d,g=("easy",random.choice(["1","2"])) if total<=30 else ("medium",random.choice(["2","3","4"]))
        add(g,"number-puzzles",d,
            f"There are {bags} bags with {each} items in each. How many items in total?",
            opts,ai, f"{bags}x{each}={total}.")

# speed/distance/time
for speed in [30,40,50,60,70,80,100]:
    for time in [1,1.5,2,2.5,3,4]:
        dist=int(speed*time); t_str=str(int(time)) if time==int(time) else str(time)
        opts,ai=sw4(dist, distract(dist,[speed,int(time),dist+speed,dist-speed//2]))
        d="medium" if speed<=60 and time<=2 else "hard"
        g=random.choice(["4","5"] if d=="medium" else ["6","7","8"])
        add(g,"number-puzzles",d,
            f"A car travels at {speed} mph for {t_str} hours. How far does it travel?",
            opts,ai, f"Distance = {speed}x{t_str}={dist} miles.")

# consecutive integers
for n in range(2,20):
    total=n+(n+1)
    opts,ai=sw4(n, distract(n,[1,-1,2,total//3]))
    d="easy" if total<=10 else ("medium" if total<=20 else "hard")
    g=random.choice(["2","3"] if d=="easy" else (["4","5"] if d=="medium" else ["6","7"]))
    add(g,"number-puzzles",d,
        f"Two consecutive integers add up to {total}. What is the smaller integer?",
        opts,ai, f"n+(n+1)={total} => 2n+1={total} => n={n}.")

# hand-crafted coin/money
for gr,diff,text,correct,wrongs,expl in [
    ("K","easy","You have 2 pennies and 1 nickel. How many cents do you have?",
     7,[6,8,5,9],"2+5=7 cents."),
    ("1","easy","You buy a sticker for 20 cents and pay with 50 cents. How much change?",
     30,[20,25,35,40],"50-20=30 cents change."),
    ("2","medium","You have 3 dimes and 4 nickels. How many cents?",
     50,[40,60,55,45],"30+20=50 cents."),
    ("3","medium","A toy costs $3.75. You pay $5. What is your change (in cents)?",
     125,[100,150,75,130],"500-375=125 cents."),
    ("4","hard","You need $8.50. You have 3 two-dollar bills and 6 quarters. How many more cents do you need?",
     100,[50,75,125,150],"3x200+6x25=750 cents. 850-750=100 cents more."),
]:
    opts,ai=sw4(correct, wrongs[:3])
    add(gr,"number-puzzles",diff,text,opts,ai,expl)

# ─── VERBAL ANALOGIES ─────────────────────────────────────────────
VA=[
 ("K","easy","Dog is to bark as cat is to ___.",["purr","run","swim","hop"],0,"Dogs bark; cats purr."),
 ("K","easy","Sun is to day as moon is to ___.",["night","cloud","rain","wind"],0,"Sun→day; moon→night."),
 ("K","easy","Bird is to nest as fish is to ___.",["pond","sky","leaf","rock"],0,"A bird lives in a nest; a fish in a pond."),
 ("K","easy","Shoe is to foot as hat is to ___.",["head","hand","leg","finger"],0,"A shoe covers the foot; a hat the head."),
 ("K","easy","Crayon is to draw as scissors is to ___.",["cut","glue","write","paint"],0,"You draw with a crayon; cut with scissors."),
 ("K","easy","Car is to road as boat is to ___.",["water","sky","sand","mud"],0,"A car travels on a road; a boat on water."),
 ("K","medium","Hand is to glove as foot is to ___.",["shoe","hat","sock","mitten"],0,"Glove→hand; shoe→foot."),
 ("K","medium","Big is to small as hot is to ___.",["cold","warm","cool","icy"],0,"Opposites: big/small, hot/cold."),
 ("K","medium","Happy is to sad as fast is to ___.",["slow","quick","funny","loud"],0,"Opposites: happy/sad, fast/slow."),
 ("K","medium","Pencil is to write as brush is to ___.",["paint","cut","read","eat"],0,"Pencil→write; brush→paint."),
 ("K","hard","Puppy is to dog as kitten is to ___.",["cat","bird","rabbit","hamster"],0,"Puppy grows into dog; kitten into cat."),
 ("K","hard","Finger is to hand as toe is to ___.",["foot","arm","knee","ankle"],0,"Fingers are part of a hand; toes of a foot."),
 ("1","easy","Apple is to fruit as rose is to ___.",["flower","tree","vegetable","animal"],0,"Apple is a fruit; rose is a flower."),
 ("1","easy","Teacher is to school as doctor is to ___.",["hospital","library","store","park"],0,"Teacher→school; doctor→hospital."),
 ("1","easy","Fish is to swim as bird is to ___.",["fly","run","hop","bark"],0,"A fish swims; a bird flies."),
 ("1","easy","Rain is to wet as fire is to ___.",["hot","cold","soft","loud"],0,"Rain→wet; fire→hot."),
 ("1","easy","Night is to dark as day is to ___.",["bright","cold","short","quiet"],0,"Night is dark; day is bright."),
 ("1","medium","Book is to read as song is to ___.",["sing","draw","eat","jump"],0,"You read a book; sing a song."),
 ("1","medium","Cold is to coat as hot is to ___.",["swimsuit","boots","scarf","gloves"],0,"Coat→cold weather; swimsuit→hot weather."),
 ("1","medium","Bee is to hive as bird is to ___.",["nest","branch","leaf","flower"],0,"Bee lives in hive; bird in nest."),
 ("1","hard","Painter is to brush as writer is to ___.",["pen","canvas","easel","frame"],0,"Painter→brush; writer→pen."),
 ("1","hard","Kitten is to cat as cub is to ___.",["bear","dog","deer","fox"],0,"Kitten→cat; cub→bear."),
 ("2","easy","Knife is to cut as broom is to ___.",["sweep","cook","wash","fold"],0,"Knife cuts; broom sweeps."),
 ("2","easy","Ear is to hear as eye is to ___.",["see","taste","smell","touch"],0,"Ears hear; eyes see."),
 ("2","easy","Rain is to umbrella as sun is to ___.",["sunscreen","coat","boots","scarf"],0,"Rain→umbrella; sun→sunscreen."),
 ("2","easy","Hammer is to nail as saw is to ___.",["wood","screw","brick","wire"],0,"Hammer→nail; saw→wood."),
 ("2","medium","Library is to books as museum is to ___.",["artifacts","pencils","desks","rulers"],0,"Library→books; museum→artifacts."),
 ("2","medium","Hungry is to eat as tired is to ___.",["sleep","run","talk","think"],0,"Hungry→eat; tired→sleep."),
 ("2","medium","Sailor is to ship as pilot is to ___.",["airplane","car","train","bus"],0,"Sailor→ship; pilot→airplane."),
 ("2","hard","Author is to novel as composer is to ___.",["symphony","painting","sculpture","poem"],0,"Author→novel; composer→symphony."),
 ("2","hard","Scales are to fish as feathers are to ___.",["bird","frog","whale","snake"],0,"Fish have scales; birds have feathers."),
 ("2","hard","Caterpillar is to butterfly as tadpole is to ___.",["frog","fish","snake","lizard"],0,"Caterpillar→butterfly; tadpole→frog."),
 ("3","easy","Carpenter is to hammer as surgeon is to ___.",["scalpel","paintbrush","wrench","needle"],0,"Carpenter→hammer; surgeon→scalpel."),
 ("3","easy","Chapter is to book as verse is to ___.",["poem","song","story","letter"],0,"Chapter is part of a book; verse of a poem."),
 ("3","easy","Evaporate is to liquid as melt is to ___.",["solid","gas","liquid","plasma"],0,"Evaporation converts liquid; melting converts solid."),
 ("3","medium","Peninsula is to land as island is to ___.",["water","sand","rock","mud"],0,"Peninsula=land mostly surrounded by water; island=entirely."),
 ("3","medium","Accelerate is to speed up as decelerate is to ___.",["slow down","stop","turn","park"],0,"Accelerate=speed up; decelerate=slow down."),
 ("3","medium","Herbivore is to plants as carnivore is to ___.",["meat","grass","fruit","seeds"],0,"Herbivores eat plants; carnivores eat meat."),
 ("3","hard","Architect is to blueprint as choreographer is to ___.",["routine","canvas","script","score"],0,"Architect→blueprint; choreographer→routine."),
 ("3","hard","Synonym is to similar as antonym is to ___.",["opposite","same","bigger","related"],0,"Synonyms=similar; antonyms=opposite."),
 ("3","hard","Democracy is to citizens as monarchy is to ___.",["king","president","governor","senator"],0,"Democracy=rule by citizens; monarchy=rule by king."),
 ("4","easy","Astronaut is to space as marine biologist is to ___.",["ocean","desert","forest","mountain"],0,"Astronauts→space; marine biologists→ocean."),
 ("4","easy","Latitude is to horizontal as longitude is to ___.",["vertical","diagonal","curved","parallel"],0,"Latitude=horizontal lines; longitude=vertical."),
 ("4","easy","Evaporation is to liquid as condensation is to ___.",["gas","solid","plasma","mixture"],0,"Evaporation: liquid→gas; condensation: gas→liquid."),
 ("4","medium","Orbit is to planet as rotate is to ___.",["axis","sun","moon","comet"],0,"Planet orbits sun; rotates on its axis."),
 ("4","medium","Microscope is to small as telescope is to ___.",["distant","large","fast","bright"],0,"Microscope sees small things; telescope sees distant things."),
 ("4","medium","Legislative is to laws as executive is to ___.",["enforce","debate","interpret","create"],0,"Legislative makes laws; executive enforces them."),
 ("4","hard","Metamorphosis is to butterfly as germination is to ___.",["plant","seed","flower","root"],0,"Metamorphosis=butterfly's change; germination=seed becoming a plant."),
 ("4","hard","Photosynthesis is to chlorophyll as combustion is to ___.",["oxygen","nitrogen","hydrogen","carbon"],0,"Photosynthesis uses chlorophyll; combustion requires oxygen."),
 ("5","easy","Democracy is to vote as monarchy is to ___.",["inherit","elect","appoint","campaign"],0,"Democracy: vote in leaders; monarchy: inherit power."),
 ("5","easy","Novel is to fiction as biography is to ___.",["nonfiction","fantasy","mystery","drama"],0,"Novel=fiction; biography=nonfiction."),
 ("5","medium","Osmosis is to water as diffusion is to ___.",["particles","light","heat","electricity"],0,"Osmosis=water movement; diffusion=particle movement."),
 ("5","medium","Alliteration is to consonants as assonance is to ___.",["vowels","rhymes","syllables","stresses"],0,"Alliteration repeats consonants; assonance repeats vowels."),
 ("5","medium","Precipitation is to water cycle as erosion is to ___.",["rock cycle","carbon cycle","nitrogen cycle","oxygen cycle"],0,"Precipitation→water cycle; erosion→rock cycle."),
 ("5","hard","Inertia is to mass as resistance is to ___.",["friction","velocity","force","momentum"],0,"Greater mass=greater inertia; friction creates resistance."),
 ("5","hard","Connotation is to implied meaning as denotation is to ___.",["literal meaning","figurative meaning","emotional tone","cultural context"],0,"Connotation=implied; denotation=literal."),
 ("6","easy","Photon is to light as electron is to ___.",["electricity","sound","heat","gravity"],0,"Photons=light particles; electrons carry charge."),
 ("6","easy","Hypothesis is to experiment as theory is to ___.",["evidence","guess","data","claim"],0,"Hypothesis→experiment; theory→evidence."),
 ("6","medium","Mitosis is to growth as meiosis is to ___.",["reproduction","repair","digestion","respiration"],0,"Mitosis=growth; meiosis=reproduction."),
 ("6","medium","Tectonic plates is to earthquakes as atmospheric pressure is to ___.",["weather","tides","seasons","gravity"],0,"Moving plates→earthquakes; pressure changes→weather."),
 ("6","hard","Isotope is to neutrons as ion is to ___.",["electrons","protons","neutrons","atoms"],0,"Isotopes differ in neutrons; ions differ in electrons."),
 ("6","hard","Baroque is to ornate as minimalism is to ___.",["sparse","colorful","complex","abstract"],0,"Baroque=ornate; minimalism=sparse."),
 ("7","easy","Congress is to legislation as judiciary is to ___.",["interpretation","taxation","enforcement","declaration"],0,"Congress→legislation; judiciary→interpretation."),
 ("7","easy","Acceleration is to force as resistance is to ___.",["friction","velocity","mass","momentum"],0,"Force causes acceleration; friction causes resistance."),
 ("7","medium","Empiricism is to experience as rationalism is to ___.",["reason","faith","emotion","instinct"],0,"Empiricism: knowledge via experience; rationalism: via reason."),
 ("7","medium","Literal is to denotation as figurative is to ___.",["connotation","diction","syntax","tone"],0,"Literal=denotation; figurative=connotation."),
 ("7","hard","Genotype is to alleles as phenotype is to ___.",["traits","chromosomes","genes","proteins"],0,"Genotype=alleles; phenotype=observable traits."),
 ("7","hard","Natural selection is to Darwin as relativity is to ___.",["Einstein","Newton","Curie","Bohr"],0,"Darwin→natural selection; Einstein→relativity."),
 ("8","easy","Covalent bond is to sharing as ionic bond is to ___.",["transfer","repulsion","attraction","fusion"],0,"Covalent=sharing electrons; ionic=transferring."),
 ("8","easy","Inflation is to purchasing power as deflation is to ___.",["prices","wages","supply","demand"],0,"Inflation erodes purchasing power; deflation lowers prices."),
 ("8","medium","Totalitarianism is to control as libertarianism is to ___.",["freedom","equality","justice","order"],0,"Totalitarianism=state control; libertarianism=individual freedom."),
 ("8","medium","Concave is to inward as convex is to ___.",["outward","flat","curved","hollow"],0,"Concave curves inward; convex outward."),
 ("8","hard","Entropy is to disorder as enthalpy is to ___.",["heat content","disorder","pressure","volume"],0,"Entropy=disorder; enthalpy=heat content."),
 ("8","hard","Allegory is to extended metaphor as satire is to ___.",["ridicule","praise","describe","narrate"],0,"Allegory=extended metaphor; satire=ridicule through humor."),
 ("8","hard","Mitochondria is to eukaryote as ribosome is to ___.",["both prokaryote and eukaryote","only eukaryote","only prokaryote","neither"],0,"Mitochondria only in eukaryotes; ribosomes in both."),
]
for gr,diff,text,opts,ai,expl in VA:
    add(gr,"verbal-analogies",diff,text,opts,ai,expl)

# ─── VERBAL CLASSIFICATION ────────────────────────────────────────
VC=[
 ("K","easy","Which does NOT belong? Cat, Dog, Bird, Chair",["Cat","Dog","Bird","Chair"],3,"Animals vs furniture."),
 ("K","easy","Which does NOT belong? Apple, Banana, Orange, Carrot",["Apple","Banana","Orange","Carrot"],3,"Fruits vs vegetable."),
 ("K","easy","Which does NOT belong? Red, Blue, Green, Loud",["Red","Blue","Green","Loud"],3,"Colors vs a sound description."),
 ("K","medium","Which does NOT belong? Happy, Sad, Angry, Running",["Happy","Sad","Angry","Running"],3,"Emotions vs an action."),
 ("K","medium","Which does NOT belong? Circle, Square, Triangle, Heavy",["Circle","Square","Triangle","Heavy"],3,"Shapes vs a weight."),
 ("K","hard","Which does NOT belong? Monday, Tuesday, Sunday, January",["Monday","Tuesday","Sunday","January"],3,"Days vs a month."),
 ("1","easy","Which does NOT belong? Square, Triangle, Rectangle, Yellow",["Square","Triangle","Rectangle","Yellow"],3,"Shapes vs a color."),
 ("1","easy","Which does NOT belong? Milk, Juice, Water, Bread",["Milk","Juice","Water","Bread"],3,"Drinks vs a food."),
 ("1","medium","Which does NOT belong? January, March, Monday, July",["January","March","Monday","July"],2,"Months vs a day."),
 ("1","medium","Which does NOT belong? Robin, Eagle, Salmon, Parrot",["Robin","Eagle","Salmon","Parrot"],2,"Birds vs a fish."),
 ("1","hard","Which does NOT belong? Run, Jump, Skip, Tall",["Run","Jump","Skip","Tall"],3,"Actions vs a description."),
 ("2","easy","Which does NOT belong? Piano, Guitar, Drum, Paintbrush",["Piano","Guitar","Drum","Paintbrush"],3,"Instruments vs an art tool."),
 ("2","medium","Which does NOT belong? Whisper, Shout, Murmur, Sprint",["Whisper","Shout","Murmur","Sprint"],3,"Speaking vs running."),
 ("2","medium","Which does NOT belong? Rose, Tulip, Lily, Oak",["Rose","Tulip","Lily","Oak"],3,"Flowers vs a tree."),
 ("2","hard","Which does NOT belong? Autobiography, Biography, Memoir, Fable",["Autobiography","Biography","Memoir","Fable"],3,"Nonfiction vs fiction."),
 ("3","easy","Which does NOT belong? Noun, Verb, Adverb, Sentence",["Noun","Verb","Adverb","Sentence"],3,"Parts of speech vs a grammatical structure."),
 ("3","medium","Which does NOT belong? Erosion, Weathering, Deposition, Photosynthesis",["Erosion","Weathering","Deposition","Photosynthesis"],3,"Geological vs biological process."),
 ("3","medium","Which does NOT belong? Simile, Metaphor, Hyperbole, Synonym",["Simile","Metaphor","Hyperbole","Synonym"],3,"Figurative language vs vocabulary term."),
 ("3","hard","Which does NOT belong? Reptile, Mammal, Amphibian, Photosynthesis",["Reptile","Mammal","Amphibian","Photosynthesis"],3,"Animal classes vs a process."),
 ("4","easy","Which does NOT belong? Mercury, Venus, Earth, Sun",["Mercury","Venus","Earth","Sun"],3,"Planets vs a star."),
 ("4","medium","Which does NOT belong? Herbivore, Carnivore, Omnivore, Predator",["Herbivore","Carnivore","Omnivore","Predator"],3,"Diet types vs hunting role."),
 ("4","hard","Which does NOT belong? Legislature, Executive, Judiciary, Municipality",["Legislature","Executive","Judiciary","Municipality"],3,"Branches of national government vs a local government unit."),
 ("4","hard","Which does NOT belong? Photosynthesis, Respiration, Fermentation, Erosion",["Photosynthesis","Respiration","Fermentation","Erosion"],3,"Biological vs geological process."),
 ("5","easy","Which does NOT belong? Mitochondria, Chloroplast, Nucleus, Bacteria",["Mitochondria","Chloroplast","Nucleus","Bacteria"],3,"Organelles vs organisms."),
 ("5","medium","Which does NOT belong? Iambic, Trochaic, Spondaic, Haiku",["Iambic","Trochaic","Spondaic","Haiku"],3,"Metrical feet vs a poem form."),
 ("5","hard","Which does NOT belong? Feudalism, Mercantilism, Capitalism, Democracy",["Feudalism","Mercantilism","Capitalism","Democracy"],3,"Economic vs political system."),
 ("6","easy","Which does NOT belong? Proton, Neutron, Electron, Molecule",["Proton","Neutron","Electron","Molecule"],3,"Subatomic particles vs a molecule."),
 ("6","medium","Which does NOT belong? Sonata, Symphony, Concerto, Limerick",["Sonata","Symphony","Concerto","Limerick"],3,"Musical compositions vs a poem form."),
 ("6","hard","Which does NOT belong? Mitosis, Meiosis, Binary Fission, Osmosis",["Mitosis","Meiosis","Binary Fission","Osmosis"],3,"Cell division vs water transport."),
 ("7","easy","Which does NOT belong? Tragedy, Comedy, Satire, Sonnet",["Tragedy","Comedy","Satire","Sonnet"],3,"Literary genres vs a poem form."),
 ("7","medium","Which does NOT belong? Deductive, Inductive, Abductive, Empirical",["Deductive","Inductive","Abductive","Empirical"],3,"Reasoning types vs an epistemological term."),
 ("7","hard","Which does NOT belong? Covalent, Ionic, Metallic, Gravitational",["Covalent","Ionic","Metallic","Gravitational"],3,"Chemical bonds vs a physical force."),
 ("8","easy","Which does NOT belong? Acid, Base, Salt, Catalyst",["Acid","Base","Salt","Catalyst"],3,"Chemical compound types vs a reaction helper."),
 ("8","medium","Which does NOT belong? Totalitarianism, Oligarchy, Theocracy, Federalism",["Totalitarianism","Oligarchy","Theocracy","Federalism"],3,"Government types vs a power structure."),
 ("8","hard","Which does NOT belong? Entropy, Enthalpy, Momentum, Gibbs Free Energy",["Entropy","Enthalpy","Momentum","Gibbs Free Energy"],2,"Thermodynamic quantities vs a mechanics quantity."),
]
for gr,diff,text,opts,ai,expl in VC:
    add(gr,"verbal-classification",diff,text,opts,ai,expl)

# ─── SENTENCE COMPLETION ──────────────────────────────────────────
SC=[
 ("K","easy","The dog ___ at the mailman.",["barked","swam","flew","sang"],0,"Dogs bark."),
 ("K","easy","I eat breakfast in the ___.",["morning","night","winter","school"],0,"Breakfast is eaten in the morning."),
 ("K","medium","It was raining, so she opened her ___.",["umbrella","kite","snowglobe","bicycle"],0,"Umbrella keeps you dry in rain."),
 ("K","medium","The baby ___ when she was hungry.",["cried","laughed","slept","ran"],0,"Babies cry when hungry."),
 ("K","hard","We ___ our hands before eating dinner.",["wash","paint","shake","fold"],0,"Washing hands keeps us healthy."),
 ("1","easy","We use our eyes to ___.",["see","hear","smell","taste"],0,"Eyes let us see."),
 ("1","easy","The sun rises in the ___ every morning.",["east","west","north","south"],0,"The sun always rises in the east."),
 ("1","medium","The story was so funny that everyone began to ___.",["laugh","cry","sleep","yell"],0,"Funny things make people laugh."),
 ("1","medium","She ran so fast that she was ___ at the finish line.",["breathless","bored","cold","clumsy"],0,"Running fast makes you breathless."),
 ("1","hard","She practiced every day and ___ improved.",["gradually","never","rarely","suddenly"],0,"Daily practice leads to gradual improvement."),
 ("2","easy","The library is a place where you can ___ books.",["borrow","sell","cook","build"],0,"Libraries let you borrow books."),
 ("2","medium","Because it was very cold outside, he put on his ___.",["coat","swimsuit","sandals","shorts"],0,"A coat keeps you warm in cold weather."),
 ("2","medium","After running for an hour, she was ___ and needed water.",["thirsty","bored","sleepy","angry"],0,"Exercise makes you thirsty."),
 ("2","hard","The scientist made careful ___ before writing her conclusion.",["observations","guesses","stories","paintings"],0,"Scientists observe before concluding."),
 ("3","easy","The author used vivid ___ to help readers picture the scene.",["description","numbers","titles","chapters"],0,"Vivid description helps readers imagine."),
 ("3","medium","Although she was nervous, she spoke with great ___.",["confidence","sadness","confusion","silence"],0,"Confidence means sounding sure of yourself."),
 ("3","medium","The town was ___ after the storm knocked out the power.",["dark","colorful","noisy","warm"],0,"Without power there are no lights — dark."),
 ("3","hard","The expedition was ___ because the team had planned every detail.",["successful","dangerous","boring","impossible"],0,"Careful planning leads to success."),
 ("4","easy","Plants convert sunlight into food through ___.",["photosynthesis","respiration","digestion","transpiration"],0,"Photosynthesis turns sunlight into food."),
 ("4","medium","The ___ government system divides power between national and state levels.",["federal","monarchy","tribal","parliamentary"],0,"Federal system shares power between national and state."),
 ("4","medium","Her argument was ___ because she supported every claim with strong evidence.",["compelling","vague","irrelevant","misleading"],0,"Evidence-backed arguments are compelling."),
 ("4","hard","The speaker used ___ to emphasize his point by greatly exaggerating the problem.",["hyperbole","simile","metaphor","alliteration"],0,"Hyperbole uses extreme exaggeration."),
 ("5","easy","The ___ of a wave is the distance from one crest to the next.",["wavelength","amplitude","frequency","velocity"],0,"Wavelength = distance between crests."),
 ("5","medium","The historian argued that economic factors were the primary ___ of the war.",["cause","effect","solution","outcome"],0,"Economic problems caused the war."),
 ("5","medium","Despite the setback, the team remained ___ and continued their research.",["resilient","defeated","indifferent","hesitant"],0,"Resilient = bouncing back from difficulties."),
 ("5","hard","The novel's ___ shifts from hope to despair as the protagonist loses everything.",["tone","plot","setting","theme"],0,"Tone is the emotional quality of the writing."),
 ("6","easy","An element's ___ number equals the number of protons in its nucleus.",["atomic","mass","neutron","electron"],0,"Atomic number = protons."),
 ("6","medium","The ___ perspective reveals only the narrator's thoughts and feelings.",["first-person","third-person omniscient","second-person","third-person limited"],0,"First-person: uses 'I', only what the narrator knows."),
 ("6","hard","The treaty was ___ because both nations refused to compromise.",["deadlocked","ratified","signed","enacted"],0,"Deadlock = no side can agree, no progress."),
 ("7","easy","Newton's second law: force equals mass times ___.",["acceleration","velocity","distance","momentum"],0,"F=ma."),
 ("7","medium","The author employed ___ to hint at events later in the story.",["foreshadowing","flashback","irony","allegory"],0,"Foreshadowing: early hints of future events."),
 ("7","hard","The philosopher contended that morality is ___, varying across cultures.",["relative","absolute","innate","universal"],0,"Moral relativism: right/wrong depends on culture."),
 ("8","easy","In an exothermic reaction, energy is ___ to the surroundings.",["released","absorbed","stored","converted"],0,"Exothermic reactions release heat."),
 ("8","medium","The author's ___ critique exposed hypocrisy through irony.",["satirical","literal","emotional","factual"],0,"Satire uses irony to criticize."),
 ("8","hard","Quantum mechanics ___ the deterministic view of classical physics.",["challenged","confirmed","ignored","replaced"],0,"Quantum mechanics introduced probability, challenging determinism."),
]
for gr,diff,text,opts,ai,expl in SC:
    add(gr,"sentence-completion",diff,text,opts,ai,expl)

# ─── FIGURE MATRICES ─────────────────────────────────────────────
FM=[
 ("K","easy","2x2 grid: top-left=small circle, top-right=large circle, bottom-left=small square. Bottom-right=?",["Large square","Small circle","Large circle","Small triangle"],0,"Pattern: shapes grow larger left→right."),
 ("K","easy","Top row: white star, black star. Bottom row: white heart, ___.",["Black heart","White heart","White star","Black circle"],0,"White→black in each row. White heart→black heart."),
 ("K","medium","Top row: 1 dot, 2 dots. Bottom row: 1 triangle, ___.",["Two triangles","Three triangles","One triangle","One circle"],0,"Count increases by 1. 1 triangle→2 triangles."),
 ("K","hard","Top row: circle inside square; circle inside triangle. Bottom row: star inside square, ___.",["Star inside triangle","Circle inside triangle","Star inside circle","Triangle inside star"],0,"Inner=star (same row); outer follows top pattern→triangle."),
 ("1","easy","Row 1: small red square→big red square. Row 2: small blue circle→___.",["Big blue circle","Small blue circle","Big red circle","Big blue square"],0,"Shape grows; color stays. Small blue circle→big blue circle."),
 ("1","medium","Row 1: triangle→upside-down triangle→triangle. Row 2: arrow up→arrow down→___.",["Arrow up","Arrow down","Arrow left","Arrow right"],0,"Flips then flips back. Up→down→up."),
 ("1","hard","3x3 grid, shapes rotate 90° clockwise each column. Col 1: arrow right. Col 2: arrow down. Col 3: ___.",["Arrow pointing left","Arrow pointing up","Arrow pointing right","Arrow pointing down"],0,"90° clockwise: right→down→left."),
 ("2","easy","Row 1: circle,circle,circle. Row 2: square,square,square. Row 3: triangle,triangle,___.",["Triangle","Square","Circle","Star"],0,"Each row repeats the same shape. Row 3: triangle."),
 ("2","medium","Row 1: 1 circle. Row 2: 2 circles. Row 3: ___.",["3 circles","4 circles","2 circles","1 circle"],0,"Pattern +1 per row. Row 3: 3 circles."),
 ("2","hard","Top-left=dark large circle. Top-right=light large circle. Bottom-left=dark small circle. Bottom-right=___.",["Light small circle","Dark small circle","Light large circle","Dark large circle"],0,"Left=dark, right=light; top=large, bottom=small → light small circle."),
 ("3","easy","Shapes gain a side each row: triangle(3)→square(4)→___.",["Pentagon","Hexagon","Circle","Oval"],0,"3→4→5 sides. Next=pentagon."),
 ("3","medium","Outer shape rotates 90° per column; inner shape is always a square. Missing inner shape=___.",["Square","Circle","Triangle","Star"],0,"Inner shape constant=square."),
 ("3","hard","3x3: each row has circle,square,triangle once. Row 3: triangle, circle, ___.",["Square","Circle","Triangle","Star"],0,"Latin square pattern — missing=square."),
 ("4","easy","Row 3 all solid shapes: solid circle, solid triangle, ___.",["Solid square","Dotted square","Striped square","Solid star"],0,"Row 3=all solid. Missing=solid square."),
 ("4","medium","Each step right adds one diagonal stripe. (2,1)=0, (2,2)=1, (2,3)=___.",["2 stripes","3 stripes","1 stripe","No stripes"],0,"+1 stripe per step → 2."),
 ("4","hard","Rows/cols each have black, gray, white. Row 3: white square, black triangle, ___.",["Gray circle","White circle","Black circle","Gray triangle"],0,"Col 3 and row 3 both need gray. Gray circle."),
 ("5","easy","Each figure adds one inner rectangle. Figure 1=1, 2=2, 3=3, 4=___.",["4 inner rectangles","3","5","2"],0,"Pattern +1 per figure. Figure 4=4."),
 ("5","medium","Shapes reflected across vertical axis. Col 1: right arrow. Col 2: left arrow. Col 3: ___.",["Right-facing arrow","Left-facing arrow","Up-facing arrow","Down-facing arrow"],0,"Right→left→right."),
 ("5","hard","Shape 1 rotates 45° per row; shape 2=circle. Row 3 shape 1 is 90° from start (diamond). What is shown?",["Diamond overlapping circle","Square overlapping circle","Triangle overlapping circle","Circle overlapping circle"],0,"Square rotated 45°=diamond; overlapping circle."),
 ("6","easy","Dark region grows +1 per row. Row 1=1, Row 2=2, Row 3=___.",["3 dark segments","4","2","1"],0,"Pattern +1. Row 3=3."),
 ("6","medium","Dots = row×col. Cell(3,2)=6. Cell(3,3)=___.",["9","6","8","12"],0,"3x3=9."),
 ("6","hard","Numbered cells: odd=solid, even=outline. Cell 9 is ___.",["Solid","Outline","Both","Neither"],0,"9 is odd → solid."),
 ("7","easy","Rows/cols have pentagon(P), hexagon(H), heptagon(Hp) once. Row 3: Hp, P, ___.",["Hexagon","Pentagon","Heptagon","Octagon"],0,"Row 3 has Hp and P; missing=hexagon."),
 ("7","medium","Shapes grow larger left→right; lighter top→bottom. Top-left=large dark circle. Bottom-right=___.",["Small light circle","Large light circle","Small dark circle","Large dark circle"],0,"Right=smaller; down=lighter → small light circle."),
 ("7","hard","Binary dots: Row 1=101=5, Row 2=110=6, Row 3=011=___.",["3","6","5","7"],0,"011=0x4+1x2+1x1=3."),
 ("8","easy","Row 1=translation, Row 2=reflection, Row 3=___.",["Rotation","Translation","Reflection","Dilation"],0,"Three rigid transformations in sequence."),
 ("8","medium","Row product=24. Row 3: 3, 2, ___.",["4","3","8","6"],0,"3x2x?=24 → ?=4."),
 ("8","hard","f(1)=2, f(2)=5, f(3)=10, f(4)=___.",["17","14","16","20"],0,"f(n)=n^2+1. f(4)=17."),
]
for gr,diff,text,opts,ai,expl in FM:
    add(gr,"figure-matrices",diff,text,opts,ai,expl)

# ─── PAPER FOLDING ───────────────────────────────────────────────
PF=[
 ("K","easy","Square folded in half; 1 hole punched in the middle. Unfolded: how many holes?",["2","1","3","4"],0,"1 fold doubles. 1 punch → 2 holes."),
 ("K","easy","Square folded top-to-bottom; hole near top. Where is the second hole?",["Near the bottom","Near the top","In the center","In the corner"],0,"Fold mirrors top to bottom → hole appears near the bottom."),
 ("K","medium","Paper folded vertically; 1 hole in top-left corner. Holes when unfolded?",["2","1","3","4"],0,"1 fold=2 layers. 1 punch → 2 holes."),
 ("K","hard","Square folded in half twice; 1 hole in center. Holes when unfolded?",["4","2","3","1"],0,"2 folds=4 layers. 1 punch → 4 holes."),
 ("1","easy","Rectangular paper folded left-to-right; 2 holes punched side by side. Holes when unfolded?",["4","3","2","5"],0,"1 fold doubles. 2 holes → 4 holes."),
 ("1","medium","Paper folded diagonally; 1 hole near fold. What appears when unfolded?",["Holes symmetrically on both sides of the diagonal","Center hole","Corner hole","Edge holes"],0,"Diagonal fold → mirror image holes."),
 ("1","hard","Square folded vertically then top half folded down; 1 hole in center. Holes when unfolded?",["4","2","3","8"],0,"2 folds=4 layers → 4 holes."),
 ("2","easy","Paper folded into quarters; 1 hole in center. Holes when fully unfolded?",["4","8","2","1"],0,"2 folds=4 layers → 4 holes."),
 ("2","medium","Square folded diagonally; 1 hole near each corner. Holes when unfolded?",["4","2","3","6"],0,"2 punches x 2 layers = 4 holes."),
 ("2","hard","Strip accordion-folded 3 times (8 layers); 1 hole punched. Holes when unfolded?",["8","4","6","3"],0,"8 layers → 8 holes."),
 ("3","easy","Paper folded in half twice (4 layers); 2 holes punched. Holes when unfolded?",["8","4","6","10"],0,"4 layers x 2 holes = 8."),
 ("3","medium","Square folded twice; notch cut from folded corner. Result when unfolded?",["A hole in the center","Holes in every corner","Notch on each edge","Hole near one edge"],0,"Center-corner cut → hole in very center."),
 ("3","hard","Paper folded along both diagonals; 1 hole near edge. Holes when unfolded?",["4","2","3","8"],0,"2 diagonal folds → 4 quadrants → 4 holes."),
 ("4","easy","Square folded in thirds (3 layers); 1 hole. Holes when unfolded?",["3","2","4","6"],0,"3 layers → 3 holes."),
 ("4","medium","Paper folded in half, then top-right corner folded down; hole in double-folded area. Holes when unfolded?",["4","3","2","5"],0,"Double-folded area=4 layers → 4 holes."),
 ("4","hard","Square folded into eighths (3 folds); 1 hole. Holes when unfolded?",["8","6","4","16"],0,"3 folds=8 layers → 8 holes."),
 ("5","easy","Paper with 3 folds (8 layers); 2 holes punched. Holes when unfolded?",["16","8","12","4"],0,"8 layers x 2 = 16."),
 ("5","medium","Square folded diagonally twice (4 layers); hole at hypotenuse. Pattern when unfolded?",["Symmetrically along both diagonals","In each corner","In the center","Along one edge"],0,"Reflected across both diagonals → symmetric pattern."),
 ("5","hard","Accordion paper with 6 folds (64 layers); 1 hole. Holes when unfolded?",["64","32","128","16"],0,"2^6=64 layers → 64 holes."),
 ("6","easy","Square folded in half then thirds (6 layers); 1 hole. Holes when unfolded?",["6","12","3","8"],0,"6 layers → 6 holes."),
 ("6","medium","Paper folded n times has 2^n holes from 1 punch. 32 holes → how many folds?",["5","4","6","3"],0,"2^5=32 → 5 folds."),
 ("6","hard","Strip folded into eighths; triangular corner removed. Notches when fully unfolded?",["8","4","16","6"],0,"8 layers → 8 notches."),
 ("7","easy","Paper folded 4 times (16 layers); 2 holes. Holes when unfolded?",["32","16","8","64"],0,"16 x 2 = 32 holes."),
 ("7","medium","Square folded corner-to-corner; punch at fold line. Result when unfolded?",["Two symmetric holes on either side of the crease","No hole","One center hole","Torn edge"],0,"Punch at fold → 2 holes when opened."),
 ("7","hard","Paper folded into 2^n layers; 128 holes result from 1 punch. What is n?",["7","6","8","5"],0,"2^7=128 → n=7."),
 ("8","easy","4x4 grid of squares, every other shaded; folded in half; holes punched through shaded squares. Unique holes when unfolded?",["8","4","16","6"],0,"8 shaded squares visible; 2 layers coincide → 8 unique holes."),
 ("8","medium","12-layer fold; 3 holes punched. Holes when unfolded?",["36","12","24","9"],0,"12 x 3 = 36."),
 ("8","hard","Square folded into 32 equal triangles; 1 hole through all. The holes form a regular polygon with how many sides?",["32","16","64","8"],0,"32-fold symmetry → 32-gon."),
]
for gr,diff,text,opts,ai,expl in PF:
    add(gr,"paper-folding",diff,text,opts,ai,expl)

# ─── FIGURE CLASSIFICATION ───────────────────────────────────────
FC=[
 ("K","easy","Group: cat, dog, rabbit. Which also belongs?",["Flower","Fish","Rock","Book"],1,"Fish is also an animal."),
 ("K","easy","Group: circle, oval, sphere (round shapes). Which fits?",["Square","Triangle","Button","Rectangle"],2,"Button is round."),
 ("K","medium","Group: apple, lemon, orange (round fruits). Which fits?",["Banana","Grape","Pear","Cucumber"],1,"Grape is a round fruit."),
 ("K","hard","Group: whistle, trumpet, flute (wind instruments). Which fits?",["Drum","Violin","Recorder","Piano"],2,"Recorder is a wind instrument."),
 ("1","easy","Group: equilateral, right, isosceles triangle. Which shape fits?",["Square","Scalene triangle","Oval","Hexagon"],1,"Scalene triangle is also a triangle."),
 ("1","medium","Group: robin, eagle, penguin (all birds). Which fits?",["Bat","Dragonfly","Ostrich","Butterfly"],2,"Ostrich is also a bird."),
 ("1","hard","Group: 4, 9, 16 (perfect squares). Which fits?",["12","18","25","20"],2,"25=5^2 — also a perfect square."),
 ("2","easy","Group: whisper, murmur, hum (quiet sounds). Which fits?",["Shout","Roar","Rustle","Scream"],2,"Rustle is also a soft sound."),
 ("2","medium","Group: square, rectangle, rhombus (4-sided shapes). Which fits?",["Triangle","Pentagon","Trapezoid","Hexagon"],2,"Trapezoid also has 4 sides."),
 ("2","hard","Group: 2, 3, 5, 7 (primes). Which fits?",["9","15","11","21"],2,"11 is prime."),
 ("3","easy","Group: autobiography, diary, memoir (first-person nonfiction). Which fits?",["Novel","Fable","Personal essay","Myth"],2,"Personal essay is also first-person nonfiction."),
 ("3","medium","Group: erosion, weathering, deposition (geological processes). Which fits?",["Photosynthesis","Digestion","Landslide","Evaporation"],2,"Landslide is also geological."),
 ("3","hard","Group: scalene, right, equilateral (all triangles). Which fits?",["Rhombus","Isosceles triangle","Parallelogram","Pentagon"],1,"Isosceles triangle is also a triangle."),
 ("4","easy","Group: Mercury, Venus, Mars (inner rocky planets). Which fits?",["Jupiter","Saturn","Earth","Neptune"],2,"Earth is also an inner rocky planet."),
 ("4","medium","Group: iamb, trochee, spondee (2-syllable feet). Which fits?",["Dactyl","Anapest","Pyrrhic","Amphibrach"],2,"Pyrrhic has 2 syllables."),
 ("4","hard","Group: 6, 28, 496 (perfect numbers). Which fits?",["12","8128","100","64"],1,"8128 is the next perfect number."),
 ("5","easy","Group: mitochondria, chloroplast, nucleus (organelles). Which fits?",["Ribosome","Cell wall","Vacuole","Flagellum"],2,"Vacuole is also a membrane-bound organelle."),
 ("5","medium","Group: haiku, tanka, renga (Japanese poetry forms). Which fits?",["Sonnet","Limerick","Haibun","Ode"],2,"Haibun is also Japanese."),
 ("5","hard","Group: 1, 3, 6, 10 (triangular numbers). Which fits?",["14","15","16","20"],1,"T5=15."),
 ("6","easy","Group: proton, neutron, electron (subatomic particles). Which fits?",["Atom","Quark","Molecule","Ion"],1,"Quarks are sub-particles making up protons/neutrons."),
 ("6","medium","Group: iambic pentameter, haiku, sonnet (fixed forms). Which fits?",["Free verse","Prose","Villanelle","Stream of consciousness"],2,"Villanelle is a fixed form."),
 ("6","hard","Group: 1, 8, 27, 64 (perfect cubes). Which fits?",["100","121","125","144"],2,"5^3=125."),
 ("7","easy","Group: mitosis, meiosis, binary fission (cell division). Which fits?",["Osmosis","Photosynthesis","Budding","Transpiration"],2,"Budding is also a reproductive process."),
 ("7","medium","Group: allegory, parable, fable (moral stories). Which fits?",["Sonnet","Elegy","Myth","Haiku"],2,"Myths also convey moral/cultural lessons."),
 ("7","hard","Which number belongs to prime, Fibonacci, AND triangular groups?",["5","13","3","21"],2,"3 is prime, Fibonacci (1,1,2,3), and triangular (T2=3)."),
 ("8","easy","Group: enthalpy, entropy, Gibbs free energy (thermodynamic state functions). Which fits?",["Velocity","Momentum","Internal energy","Acceleration"],2,"Internal energy is also a thermodynamic state function."),
 ("8","medium","Group: covalent, ionic, metallic bonds. Which fits?",["Hydrogen bond","Van der Waals force","Polar covalent","Ionic dipole"],2,"Polar covalent is a subtype of covalent bond."),
 ("8","hard","Group: logarithmic, exponential, polynomial (growth types). Which fits?",["Linear","Quadratic","Constant","Sinusoidal"],1,"Quadratic (x^2) is polynomial."),
]
for gr,diff,text,opts,ai,expl in FC:
    add(gr,"figure-classification",diff,text,opts,ai,expl)

# ─── WRITE OUTPUT ─────────────────────────────────────────────────
random.shuffle(questions)
for i,q in enumerate(questions,1):
    q["id"] = f"Q{i:05d}"

out = "/Users/nilesh/Projects/brainspark/questions.json"
with open(out,"w",encoding="utf-8") as f:
    json.dump(questions, f, indent=2)

combos = Counter((q["grade"],q["battery"],q["difficulty"]) for q in questions)
print(f"\n✓ Written {len(questions)} unique questions → {out}\n")
types_count = Counter(q["type"] for q in questions)
for t in sorted(types_count):
    print(f"  {t:<35} {types_count[t]}")
print(f"\n  Sessions before any repeat (9/session): ~{len(questions)//9}")
