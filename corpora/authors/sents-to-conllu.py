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

	if pos == '_' and spa == '' and glosa == '':
		print('WARNING: Empty token', token, 'in lexicon', file=sys.stderr)
		continue

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

	print('disambiguate:', form, '|', analyses,'|', cux, spa, file=sys.stderr)
	new_analyses = analyses

	def choose_if_else(analyses, wordre, pos1, pos2):
		new_analyses = analyses
		found = False
		for token in spa:
			if re.findall(wordre, token.lower()):
				found = True

		if found:
			new_analyses = [i for i in analyses if i[1] == pos1]	
		else:
			new_analyses = [i for i in analyses if i[1] == pos2]	

		#print('\t!!!:', form, '|', found,'|', analyses,'||', new_analyses, file=sys.stderr)

		return new_analyses

	def choose_if(analyses, wordre, pos1):
		new_analyses = analyses
		found = False
		for token in spa:
			if re.findall(wordre, token.lower()):
				found = True
		if found:
			new_analyses = [i for i in analyses if i[1] == pos1]	
		#print('\t!!!:', wordre, '|', found,'|', analyses,'||', new_analyses, file=sys.stderr)

		return new_analyses

	def choose_if_not(analyses, wordre, pos1):
		new_analyses = analyses
		found = False
		for token in spa:
			if re.findall(wordre, token.lower()):
				found = True
		if not found:
			new_analyses = [i for i in analyses if i[1] == pos1]	
		#print('\t!!!:', wordre, '|', found,'|', analyses,'||', new_analyses, file=sys.stderr)

		return new_analyses

	def choose_or_remove(analyses, wordre, trad):
		new_analyses = analyses
		found = False
		for token in spa:
			if re.findall(wordre, token.lower()):
				found = True
		if found:
			new_analyses = [i for i in analyses if i[3] == trad]
		else:
			new_analyses = [i for i in analyses if i[3] != trad]

		return new_analyses

	def choose_if_not_trad(analyses, wordre, trad):
		new_analyses = analyses
		found = False
		for token in spa:
			if re.findall(wordre, token.lower()):
				found = True
		if not found:
			new_analyses = [i for i in analyses if i[3] == trad]
		else:
			new_analyses = [i for i in analyses if i[3] != trad]

		return new_analyses

	if form == 'a': # Choose 'a' as an ADV if we find "ya" in the translation, otherwise PART
		new_analyses = choose_if_else(analyses, 'ya', 'ADV', 'PART')
	elif form == 'nichi': # Choose 'nichi' as NUM if we find "diez" otherwise VERB
		new_analyses = choose_if_else(analyses, 'diez', 'NUM', 'VERB')
	elif form == 'tii':
		new_analyses = choose_if_else(analyses, 'dónde', 'ADV', 'NOUN')
	elif form == 'koʼo':
		new_analyses = choose_if_else(analyses, 'pie', 'NOUN', 'VERB')
	elif form == 'kuʼu':
		new_analyses = choose_if_else(analyses, 'plato', 'NOUN', 'VERB')
	elif form == 'cheanu':
		new_analyses = choose_if_else(analyses, 'cuñada', 'NOUN', 'VERB')
	elif form == 'kuaa':
		new_analyses = choose_if_else(analyses, r'rel[aá]mpago', 'NOUN', 'VERB')
	elif form == 'kaaka':
		new_analyses = choose_if_else(analyses, 'papel', 'NOUN', 'VERB')
	elif form == 'kueta':
		new_analyses = choose_if_else(analyses, 'cohete', 'NOUN', 'VERB')
	elif form == 'bea':
		new_analyses = choose_if_not(analyses, r'sentad[oa]', 'VERB')
	elif form == 'iyu':
		new_analyses = choose_if_not_trad(analyses, 'luna', 'mes')
	elif form == 'ñoʼö':
		new_analyses = choose_if_not_trad(analyses, r'(árbol|árboles)', 'pueblo')
	elif form == 'cheʼed':
		new_analyses = choose_if_not_trad(analyses, 'come', 'fuiste')
	elif form == 'dii':
		new_analyses = choose_or_remove(analyses, 'resistente', 'resistente')
		if len(new_analyses) > 1:
			new_analyses = choose_if(new_analyses, r'^(tú|ti|te)$', 'PRON')
		if len(new_analyses) > 1:
			new_analyses = choose_if_else(new_analyses, r'trabaj.*', 'VERB', 'PRON')
	elif form == 'yada':
		new_analyses = choose_if_not_trad(analyses, r'pájaros?', 'vestido')
	elif form == 'yuduu':
		new_analyses = choose_if_not_trad(analyses, 'plano', 'caballo')
	elif form == 'deabea':
		new_analyses = choose_if_not_trad(analyses, 'alumbrado', 'limpio')
	elif form == 'koon':
		new_analyses = choose_if_not_trad(analyses, 'señora', 'ese')

	if new_analyses == analyses:
		print('\tremaining:', form, '|', analyses,'|', '|', cux, spa, file=sys.stderr)
	else:	
		print('\tselected:', form, '|', new_analyses,'|', file=sys.stderr)

	return new_analyses

seen = set()

n_toks = 0
n_sents = 0
n_tagged_sents = 0
n_tagged_tokens = 0
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

	print('# sent_id = ejemplos:%s' % (str(sent_id).zfill(4)), file=sys.stderr)

	token_id = 1
	n_found_pos = 0
	token_lines = []
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
		print('!!!', analyses, file=sys.stderr)

		if len(analyses) == 1:
			ulem = analyses[0][0]
			upos = analyses[0][1]
			for fv in analyses[0][2].split('|'):
				if '=' not in fv:
					continue
				f, v = fv.split('=')
				ufeat = add_featval(ufeat, f, v)
			misc = add_featval(misc, 'Trad', analyses[0][3].replace(' ', '.'))
			misc = add_featval(misc, 'Gloss',  analyses[0][4])
		elif len(analyses) > 1:
			ltrads = [] # make sure list of translations is in stable order
			for a in analyses:
				ltrads.append(a[3].replace(' ', '.'))
			ltrads.sort()
			trads = ','.join(ltrads)
			misc = add_featval(misc, 'Ambiguous', 'Yes')
			misc = add_featval(misc, 'Trad', trads)

		if len(analyses) > 0:
			tokens_lex += 1

		if upos != '_':
			n_found_pos += 1

		token_lines.append('%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (token_id, token, ulem, upos, '_', ufeat, '_', '_', '_', misc))
		token_id += 1
		n_toks += 1

	#print('!!', token_id, n_found_pos)
	fully_tagged = False
	if n_found_pos == (token_id - 1): 
		n_tagged_tokens += token_id - 1
		n_tagged_sents += 1	
		fully_tagged = True

	print('# sent_id = ejemplos:%s' % (str(sent_id).zfill(4)))
	print('# text = %s' % (cux))
	print('# text[orig] = %s' % (orig_cux))
	print('# text[spa] = %s' % (spa))
	print('# tagged = %s' % (str(fully_tagged).lower()))
	print('# author = %s' % (author))
	for token_line in token_lines:
		print(token_line)
	print()

	n_sents += 1

	sent_id += 1


print('%d\t%d\t%d (%.2f%%)' % (n_sents, n_toks, tokens_lex, (tokens_lex/n_toks)*100), file=sys.stderr)
print('%d (%.2f%%)\t%d (%.2f%%)' % (n_tagged_sents, (n_tagged_sents/n_sents)*100, n_tagged_tokens, (n_tagged_tokens/n_toks)*100), file=sys.stderr)
