import re,sys
t=open(sys.argv[1],encoding='utf-8').read()
# cut at \selfcheck (body only, exclude questions)
i=t.find('\\selfcheck'); 
if i>0: t=t[:i]
# remove comments
t=re.sub(r'(?m)(?<!\\)%.*$','',t)
# remove tikzpicture blocks entirely
t=re.sub(r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}','',t,flags=re.S)
# remove equation/align/display math contents (count as some chars? critic likely excluded markup but kept visible). We'll drop math blocks.
t=re.sub(r'\\begin\{(equation|align|center|tabularx|tabular|tikzfig)\}.*?\\end\{\1\}',' ',t,flags=re.S)
t=re.sub(r'\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^{}]*\})?',' ',t)  # strip commands w/ simple args
t=re.sub(r'[{}$~\\]',' ',t)
t=re.sub(r'\s+',' ',t)
print(len(t.strip()))
