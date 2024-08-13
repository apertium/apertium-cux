import sys, re, os, inspect, hashlib
import unicodedata


currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir +'/tagger')

from tagger import Tagger

def clean(s):
	o = s
	o = o.replace('´', 'ʼ')
	o = o.replace('’', 'ʼ')
	o = o.replace('`', 'ʼ')
	o = o.replace("'", 'ʼ')
	o = o.replace('?.','?')
	o = o.replace('.?','?')
	o = o.replace(' ?', '?')
	o = o.replace('¿ ', '¿')
	o = re.sub('  *', ' ', o)
	return unicodedata.normalize('NFKC', o)

def clean_sent(s):
	o = s
	if o[0] == o[0].lower():
		o = o[0].upper() + o[1:]
	return o


n_toks = 0
n_toks_nopunct = 0
n_sents = 0
n_tagged_sents = 0
n_tagged_tokens = 0
tokens_lex = 0

last_sent_id = ''

tagger = Tagger('../tagger/lexicon.tsv', '../tagger/corrections.tsv', '../tagger/verbs.tsv')

for line in open(sys.argv[1]):

	if line.count('ORACION EN CUICATECO') > 0:
		continue

	row = line.split('\t')

	cux = row[3].strip()
	if cux == '':
		continue
	sent_id = row[0].strip().replace('.','')
	if sent_id == '':
		sent_id = last_sent_id

	if '/' in cux or '*' in cux:
		print('[%s] WARNING: Non-standard characters in translation.' % (sent_id),file=sys.stderr)
		continue

# 0       1         2                 3                     4                      5
#ID	PALABRA	SIGNIFICADO	ORACION EN CUICATECO	ORACION EN ESPAÑOL	TRANSCRIPCIÓN		
#	Úu	yo	úu ne chidi	Yo estornudé	ˀuntʃidi		


	spa = row[4].strip()
	transcr = row[5].strip()

	if cux[-1] not in '.?!':
		cux = cux + '.'

	orig_cux = cux
	cux = clean(cux)
	cux = clean_sent(cux)
	tokens = re.sub('([,:?¿!¡;.])', ' \g<1> ', cux).strip().split(' ')
	tokens_spa = re.sub('([,:?¿!¡;.])', ' \g<1> ', spa).strip().split(' ')


#	print('# sent_id = gina:%s' % (str(sent_id)), file=sys.stderr)


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

		analyses, ufeat, new_misc = tagger.tag(token, ufeat)
		analyses = tagger.disambiguate(token, analyses, tokens, tokens_spa)

		misc += new_misc

		if len(analyses) == 1:
			ulem = analyses[0][0]
			upos = analyses[0][1]
			for fv in analyses[0][2].split('|'):
				if '=' not in fv:
					continue
				f, v = fv.split('=')
				ufeat = tagger.add_featval(ufeat, f, v)
			misc = tagger.add_featval(misc, 'Trad', analyses[0][3].replace(' ', '.'))
			misc = tagger.add_featval(misc, 'Gloss',  analyses[0][4])
			misc = tagger.add_featval(misc, 'UPOS',  analyses[0][5]) 
		elif len(analyses) > 1:
			ltrads = [] # make sure list of translations is in stable order
			for a in analyses:
				ltrads.append(a[3].replace(' ', '.'))
			ltrads.sort()
			trads = ','.join(ltrads)
			misc = tagger.add_featval(misc, 'Ambiguous', 'Yes')
			misc = tagger.add_featval(misc, 'Trad', trads)

		if len(analyses) > 0:
			tokens_lex += 1


		if upos != '_':
			n_found_pos += 1

		if upos != 'PUNCT':
			n_toks_nopunct += 1

		if misc == '': misc = '_'
		misc = misc.strip()

		token_lines.append('%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (token_id, token, ulem, upos, '_', ufeat, '_', '_', '_', misc))
		token_id += 1
		n_toks += 1


	fully_tagged = False
	if n_found_pos == (token_id - 1): 
		n_tagged_tokens += token_id - 1
		n_tagged_sents += 1	
		fully_tagged = True

	print('# sent_id = gina:%s' % (sent_id))
	print('# text = %s' % (cux))
	print('# text[orig] = %s' % (orig_cux))
	print('# text[spa] = %s' % (spa))
	print('# text[ipa] = %s' % (transcr))
	print('# tagged = %s' % (str(fully_tagged).lower()))

	for token_line in token_lines:
		print(token_line)
	print()

	last_sent_id = sent_id

	n_sents += 1

print('%d\t%d\t%d\t%d (%.2f%%)' % (n_sents, n_toks, n_toks_nopunct, tokens_lex, (tokens_lex/n_toks_nopunct)*100), file=sys.stderr)
print('%d (%.2f%%)\t\t%d (%.2f%%)' % (n_tagged_sents, (n_tagged_sents/n_sents)*100, n_tagged_tokens, (n_tagged_tokens/n_toks)*100), file=sys.stderr)

