# Example sentences

Sentence files from Google Sheets:

* `lilia.tsv`: Sentences from Lilia
* `lucy.tsv`: Sentences from Maestra Lucy
* `mazali.tsv`: Sentences from Mazali
* `paula.tsv`: Sentences from Paula

Linguistic data for processing the sentences:

* `lexicon.tsv`: A lexicon with UPOS, UFeats and glosses
* `corrections.tsv`: Corrections of typos

Scripts to process the sentences:

`extract-sents.sh`: Extract and merge sentences from the TSV files
`format-sents.py`: Clean and format the sentences as a TSV
`sents-to-conllu.py`: Convert the sentences to CoNLL-U format
