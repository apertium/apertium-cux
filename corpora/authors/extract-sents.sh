
# 1	A	Ya	A che'ë kuete # ¿ A nood?	Ya fui al campo # ¿Ya llegasté?	

lilia=$(mktemp /tmp/lilia.XXXX)
cat lilia.tsv | cut -f4 | sed 's/#/\n/g' > /tmp/cux
cat lilia.tsv | cut -f5 | sed 's/#/\n/g' > /tmp/spa
paste /tmp/cux /tmp/spa > ${lilia}

lucy=$(mktemp /tmp/lucy.XXXX)
cat lucy.tsv | cut -f4-5 > ${lucy}

mazali=$(mktemp /tmp/mazali.XXXX)
cat mazali.tsv  | cut -f3-4 > ${mazali}

paula=$(mktemp /tmp/paula.XXXX)
cat paula.tsv | cut -f3 | sed 's/#/\n/g' | sed 's/^ *//g'> /tmp/cux
cat paula.tsv | cut -f4 | sed 's/#/\n/g' > /tmp/spa
cat paula.tsv  | cut -f5-6 | grep -P -v '^[ \t]' | cut -f1 >> /tmp/cux
cat paula.tsv  | cut -f5-6 | grep -P -v '^[ \t]' | cut -f2 >> /tmp/spa
cat paula.tsv  | cut -f7-8 | grep -P -v '^[ \t]' | cut -f1 >> /tmp/cux
cat paula.tsv  | cut -f7-8 | grep -P -v '^[ \t]' | cut -f2 >> /tmp/spa
cat paula.tsv  | cut -f9-10 | grep -P -v '^[ \t]' | cut -f1 >> /tmp/cux
cat paula.tsv  | cut -f9-10 | grep -P -v '^[ \t]' | cut -f2 >> /tmp/spa
cat paula.tsv  | cut -f13-14 | grep -P -v '^[ \t]' | cut -f1 >> /tmp/cux
cat paula.tsv  | cut -f13-14 | grep -P -v '^[ \t]' | cut -f2 >> /tmp/spa
paste /tmp/cux /tmp/spa > ${paula}

#paula.tsv

wc -lw ${lilia} ${lucy} ${mazali} ${paula} >/dev/stderr

for p in ${lilia} ${lucy} ${mazali} ${paula}; do
	pp=$(basename ${p} | cut -f1 -d'.')
	cat ${p} | sed "s/^/${pp}\t/g"
done

#rm ${lilia} ${lucy} ${mazali} ${paula}
