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

seen = set()

n_toks = 0
n_sents = 0

sent_id = 1
for line in sys.stdin.readlines():

	row = line.split('\t')
	author = row[0].strip()
	cux = row[1].strip()
	spa = row[2].strip()

	if cux in seen:
		continue
	seen.add(cux)

	tokens = re.sub('([,:?¿!¡;.])', ' \g<1> ', cux).strip().split(' ')

	print('# sent_id = ejemplos:%s' % (str(sent_id).zfill(4)))
	print('# text = %s' % (cux))
	print('# text[orig] = %s' % (cux))
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
		k = token.lower()
		if k not in lexicon and k in corrections:
			ufeat = add_featval(ufeat, 'Typo', 'Yes')
			k = corrections[k]
		if k in lexicon:
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

		print('%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (token_id, token, ulem, upos, '_', ufeat, '_', '_', '_', misc))
		token_id += 1
		n_toks += 1


	print()

	n_sents += 1

	sent_id += 1


print('%d\t%d' % (n_sents, n_toks), file=sys.stderr)
