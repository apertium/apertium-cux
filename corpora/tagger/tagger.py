import sys, re


# Palabra	Lema	POS	Feats	Significado	Glosa	
#gea				subida		
#géche				ala		

class Tagger:

	def __init__(self, lexfn, corrfn):
		self.lexicon = self.load_lexicon(lexfn)
		self.corrections = self.load_corrections(corrfn)
	
	def load_lexicon(self, fn):
		lexicon = {}
		for line in open(fn).readlines():
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
		return lexicon
	
	def load_corrections(self,fn):
		corrections = {}
		for line in open(fn).readlines():
			if line.strip() == '':
				continue
			if line[0] == '#':
				continue
			orig, repl = line.strip().split('\t')	
			if orig in self.lexicon:
				print('WARNING:', orig,'→', self.lexicon[orig], file=sys.stderr)
			corrections[orig.strip()] = repl.strip()
		return corrections
	
	def add_featval(self,exist, feat, val):
		if val.strip() == '':
			return exist
		if exist == '' or exist == '_':
			return '%s=%s' % (feat, val) 
	
		return exist + '|' + '%s=%s' % (feat, val)
	
	def disambiguate(self,form, analyses, cux, spa):
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
	
		def choose_or_remove_list(analyses, words, trad):
			new_analyses = analyses
			found = True 
			spa_lower = [i.lower() for i in spa]
			res = [i.lower() in spa_lower for i in words.split(' ')]
			print('@@@', res, file=sys.stderr)
			for r in res:
				if r == False: 
					found = False
					break
			if found:
				new_analyses = [i for i in analyses if i[3] == trad]
			else:
				new_analyses = [i for i in analyses if i[3] != trad]
			print('###', analyses, '|||', new_analyses, file=sys.stderr)
	
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
	
		if form.lower() == 'a': 
			new_analyses = choose_or_remove(analyses, 'ya', 'ya')
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
		elif form == 'díi':
			new_analyses = choose_or_remove(analyses, 'caspa', 'caspa')
		elif form == 'yába':
			new_analyses = choose_or_remove(analyses, 'memela', 'memela')
		elif form == 'yaʼa':
			new_analyses = choose_or_remove(analyses, 'duele', 'duele')
			new_analyses = choose_or_remove(new_analyses, 'amo', 'amo')
		elif form == 'jíku':
			new_analyses = choose_or_remove(analyses, 'río', 'río')
		elif form == 'yata':
			new_analyses = choose_or_remove(analyses, 'hierba', 'hierba')
			if len(new_analyses) > 1:
				new_analyses = choose_or_remove(new_analyses, 'pichón', 'pichón')
		elif form == 'yoo':
			new_analyses = choose_or_remove(analyses, 'brazadas?', 'brazada')
		elif form == 'dü':
			new_analyses = choose_or_remove(analyses, 'manteca', 'manteca')
		elif form == 'dinuu':
			new_analyses = choose_or_remove(analyses, 'talón', 'talón')
			if len(new_analyses) > 1:
				new_analyses = choose_or_remove_list(new_analyses, 'mi hermano', 'mi hermano')
		elif form == 'biʼi':
			new_analyses = choose_or_remove(analyses, 'fruta', 'fruta')
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
		elif form == 'chikuu' or form == 'chikuʼu':
			new_analyses = choose_if_not_trad(analyses, r'(mi|mí)', 'abuela')
		elif form == 'jeakuy':
			new_analyses = choose_if_not_trad(analyses, 'llor[^ ]+', 'tapar')
		elif form == 'deabea':
			new_analyses = choose_if_not_trad(analyses, 'alumbrado', 'limpio')
		elif form == 'koon':
			new_analyses = choose_if_not_trad(analyses, 'señora', 'ese')
		elif form == 'yeabean':
			new_analyses = choose_if_not_trad(analyses, 'mucho', 'muy')
	
		if new_analyses == analyses:
			print('\tremaining:', form, '|', analyses,'|', '|', cux, spa, file=sys.stderr)
		else:	
			print('\tselected:', form, '|', new_analyses,'|', file=sys.stderr)
	
		return new_analyses

	def tag(self, token, ufeat):
		analyses = []

		# first look up the token, if not lower case, if not the correction 
		k = token
		if k in self.lexicon:
			analyses = self.lexicon[k]	
		elif k.lower() in self.lexicon:
			analyses = self.lexicon[k.lower()]	
			k = k.lower()
		elif k in self.corrections:	
			ufeat = self.add_featval(ufeat, 'Typo', 'Yes')
			k = self.corrections[k]
			analyses = self.lexicon[k]	
		elif k.lower() in self.corrections:	
			ufeat = self.add_featval(ufeat, 'Typo', 'Yes')
			k = self.corrections[k.lower()]
			analyses = self.lexicon[k.lower()]	
		return analyses, ufeat

