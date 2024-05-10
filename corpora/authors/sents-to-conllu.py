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
	token, lema, pos, feats, spa, glosa, _, _, _ = row

	if pos == '': pos = '_'
	if lema == '': lema = '_'

	if token not in lexicon:
		lexicon[token] = []

	lexicon[token].append((lema, pos, feats, spa, glosa))
	lexicon[token] = list(set(lexicon[token]))

for line in open('corrections.tsv').readlines():
	if line.strip() == '':
		continue
	if line[0] == '#':
		continue
	orig, repl = line.strip().split('\t')	
	if orig in lexicon:
		print('WARNING:', orig,'→', lexicon[orig], file=sys.stderr)
	corrections[orig.strip()] = repl.strip()

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

def disambiguate(form, analyses, cux, spa):
	if len(analyses) < 2:
		return analyses	

	#print('disambiguate:', form, '|', analyses,'|', cux, spa, file=sys.stderr)
	new_analyses = []

	# Choose 'a' as an ADV if we find "ya" in the translation, otherwise PART
	if form == 'a':
		foundYa = False
		if 'ya' in [i.lower() for i in spa]:
			foundYa = True

		if foundYa:
			new_analyses = [i for i in analyses if i[1] == 'ADV']	
		else:
			new_analyses = [i for i in analyses if i[1] == 'PART']	

		#print('!!!:', form, '|', foundYa,'|', analyses,'||', new_analyses, file=sys.stderr)

		return new_analyses
	# Choose 'nichi' as NUM if we find "diez" otherwise VERB
	elif form == 'nichi':
		foundDiez = False
		if 'diez' in [i.lower() for i in spa]:
			foundDiez = True

		if foundDiez:
			new_analyses = [i for i in analyses if i[1] == 'NUM']	
		else:
			new_analyses = [i for i in analyses if i[1] == 'VERB']	

		return new_analyses

	elif form == 'koʼo':
		foundPie = False
		if 'pie' in [i.lower() for i in spa] or 'pies' in [i.lower() for i in spa]:
			foundPie = True

		if foundPie:
			new_analyses = [i for i in analyses if i[1] == 'NOUN']	
		else:
			new_analyses = [i for i in analyses if i[1] == 'VERB']	

		return new_analyses

	elif form == 'bea':
		foundSentado = False
		if 'sentado' in [i.lower() for i in spa] or 'sentada' in [i.lower() for i in spa]:
			foundSentado = True

		if not foundSentado:
			new_analyses = [i for i in analyses if i[1] == 'VERB']	
			return new_analyses
						
	return analyses

seen = set()

n_toks = 0
n_sents = 0
n_tagged_sents = 0
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
	tokens_spa = re.sub('([,:?¿!¡;.])', ' \g<1> ', spa).strip().split(' ')

	print('# sent_id = ejemplos:%s' % (str(sent_id).zfill(4)))
	print('# text = %s' % (cux))
	print('# text[orig] = %s' % (orig_cux))
	print('# text[spa] = %s' % (spa))
	print('# author = %s' % (author))
	token_id = 1
	n_found_pos = 0
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
		elif k.lower() in corrections:	
			ufeat = add_featval(ufeat, 'Typo', 'Yes')
			k = corrections[k.lower()]
			analyses = lexicon[k.lower()]	

		analyses = disambiguate(k, analyses, tokens, tokens_spa)

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
		elif len(analyses) > 1:
			trads = ''
			for a in analyses:
				trads += a[3].replace(' ', '.') + ','
			trads = trads.strip(',')
			misc = add_featval(misc, 'Ambiguous', 'Yes')
			misc = add_featval(misc, 'Trad', trads)

		if len(analyses) > 0:
			tokens_lex += 1

		if upos != '_':
			n_found_pos += 1

		print('%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (token_id, token, ulem, upos, '_', ufeat, '_', '_', '_', misc))
		token_id += 1
		n_toks += 1

	#print('!!', token_id, n_found_pos)
	if n_found_pos == (token_id - 1): 
		n_tagged_sents += 1	

	print()

	n_sents += 1

	sent_id += 1


print('%d\t%d\t%d (%.2f%%)\t%d (%.2f%%)' % (n_sents, n_toks, tokens_lex, (tokens_lex/n_toks)*100, n_tagged_sents, (n_tagged_sents/n_sents)*100), file=sys.stderr)
