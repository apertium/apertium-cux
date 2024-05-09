import sys, re

lexicon = {}
corrections = {}

# Palabra	Lema	POS	Feats	Significado	Glosa	
#gea				subida		
#géche				ala		

for line in open('lexicon.tsv').readlines():
	if line.strip() == '':
		continue
	#['géche', '', '', 'ala', '', '\n']
	row = line.strip('\n').split('\t')
	token, lema, pos, feats, spa, glosa, _ = row

	if pos == '': pos = '_'
	if lema == '': lema = '_'

	if token not in lexicon:
		lexicon[token] = []

	lexicon[token].append((lema, pos, feats, spa, glosa))
	lexicon[token] = list(set(lexicon[token]))

for line in open('corrections.tsv').readlines():
	if line.strip() == '':
		continue
	orig, repl = line.strip().split('\t')	
	corrections[orig] = repl

def add_featval(exist, feat, val):
	if val.strip() == '':
		return exist
	if exist == '' or exist == '_':
		return '%s=%s' % (feat, val) 

	return exist + '|' + '%s=%s' % (feat, val)

def clean_sent(s):
	o = s
	if o[0] == o[0].lower():
		o = o[0].upper() + o[1:]
	return o

seen = set()

n_toks = 0
n_sents = 0
tokens_lex = 0

sent_id = 1
for line in sys.stdin.readlines():

	row = line.split('\t')
	author = row[0].strip()
	cux = row[1].strip()
	spa = row[2].strip()

	if cux in seen:
		continue
	seen.add(cux)

	orig_cux = cux
	cux = clean_sent(cux)
	tokens = re.sub('([,:?¿!¡;.])', ' \g<1> ', cux).strip().split(' ')

	print('# sent_id = ejemplos:%s' % (str(sent_id).zfill(4)))
	print('# text = %s' % (cux))
	print('# text[orig] = %s' % (orig_cux))
	print('# text[spa] = %s' % (spa))
	print('# author = %s' % (author))
	token_id = 1
	for token in tokens:
		if token.strip() == '':
			continue
		upos = '_'
		ulem = '_'
		ufeat = '_'
		misc = ''
		if token in ',:?¿!¡;.':
			ulem = token
			upos = 'PUNCT'
		analyses = []

		# first look up the token, if not lower case, if not the correction 
		k = token
		if k in lexicon:
			analyses = lexicon[k]	
		elif k.lower() in lexicon:
			analyses = lexicon[k.lower()]	
			k = k.lower()
		elif k in corrections:	
			ufeat = add_featval(ufeat, 'Typo', 'Yes')
			k = corrections[k]
			analyses = lexicon[k]	

		if len(analyses) == 1:
			ulem = lexicon[k][0][0]
			upos = lexicon[k][0][1]
			for fv in lexicon[k][0][2].split('|'):
				if '=' not in fv:
					continue
				f, v = fv.split('=')
				ufeat = add_featval(ufeat, f, v)
			misc = add_featval(misc, 'Trad', lexicon[k][0][3].replace(' ', '.'))
			misc = add_featval(misc, 'Gloss',  lexicon[k][0][4])
			tokens_lex += 1
		elif len(analyses) > 0:
			misc = add_featval(misc, 'Ambiguous', 'Yes')
			tokens_lex += 1

		print('%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (token_id, token, ulem, upos, '_', ufeat, '_', '_', '_', misc))
		token_id += 1
		n_toks += 1


	print()

	n_sents += 1

	sent_id += 1


print('%d\t%d\t%d (%.2f)' % (n_sents, n_toks, tokens_lex, (tokens_lex/n_toks)*100), file=sys.stderr)
