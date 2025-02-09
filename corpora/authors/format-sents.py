import sys, re

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
	return o

sents = {}
toks = {}
pp = set()
for i, line in enumerate(sys.stdin.readlines()):
	line = line.strip('\n')
	if line.strip() == '' or line.count('ORACION') > 0 or line.strip().count('\t') == 0:
		continue
	row = line.split('\t')

	if len(row) != 3:
		print(i,':', line, file=sys.stderr)
		continue

	p = row[0].strip()
	cux = clean(row[1].strip())

	if cux == '_':
		continue

	if cux[-1] not in '.:?!' and cux[0] not in '¿¡':
		cux += '.'
	spa = row[2].strip()
	if len(spa) == 0:
		print('INVALID', i,':', line, file=sys.stderr)
		continue
		
	if spa[-1] not in '.:?!' and spa[0] not in '¿¡':
		spa += '.'

	if p not in sents:
		sents[p] = 0
	if p not in toks:
		toks[p] = 0

	sents[p] += 1
	toks[p] += cux.count(' ')

	pp.add(p)

	if cux == '' or spa == '':
		print(i,':', line, file=sys.stderr)
		continue

	print('%s\t%s\t%s' % (p, cux, spa))

for p in pp:
	print(p, sents[p], toks[p], file=sys.stderr)
