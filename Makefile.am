###############################################################################
## Makefile for apertium-cux
###############################################################################

LANG1=cux
BASENAME=apertium-$(LANG1)

TARGETS_COMMON =			\
	$(LANG1).automorf.hfst		\
	$(LANG1).automorf.bin		\
	$(LANG1).automorf.att.gz	\
	$(LANG1).autogen.hfst		\
	$(LANG1).autogen.bin		\
	$(LANG1).autogen.att.gz		\
	$(LANG1).autoseg.hfst		\
	$(LANG1).autoseg.bin		\
	$(LANG1).prob		\
	$(LANG1).rlx.bin

TARGETS_INTERMEDIATE = $(LANG1).mor.hfst $(LANG1).seg.hfst $(LANG1).gen.hfst $(LANG1).phon.hfst

# This include defines goals for install-modes, .deps/.d and .mode files:
@ap_include@

###############################################################################

# nimahtlapaltzin:<s_sg1>mahtlapal<n><dim>
.deps/cux.mor.hfst: .deps/cux.LR.gen.hfst .deps/cux.mor.twol.hfst
	hfst-compose-intersect -1 .deps/cux.LR.gen.hfst -2 .deps/cux.mor.twol.hfst | hfst-minimise | hfst-invert -o $@

# amatl<n><dim><pl>:ama>tzi>tzin
.deps/cux.gen.hfst: .deps/cux.RL.lexc.hfst .deps/cux.twol.hfst
	hfst-compose-intersect -1 .deps/cux.RL.lexc.hfst -2 .deps/cux.twol.hfst | hfst-minimise  -o $@

.deps/cux.LR.gen.hfst: .deps/cux.lexc.hfst .deps/cux.twol.hfst
	hfst-compose-intersect -1 .deps/cux.lexc.hfst -2 .deps/cux.twol.hfst | hfst-minimise  -o $@

.deps/cux.twol.hfst: apertium-cux.cux.twol
	hfst-twolc $< -o $@

# <px2sg>metztli<n><pl>:m{o}>metz>huan
.deps/cux.lexc.hfst: apertium-cux.cux.lexc .deps/.d
	hfst-lexc -A --Werror $< -o $@

.deps/cux.RL.lexc: apertium-cux.cux.lexc .deps/.d
	cat $< | grep -v "Dir/LR" > $@

.deps/cux.RL.lexc.hfst: .deps/cux.RL.lexc .deps/.d
	hfst-lexc -A --Werror $< -o $@

.deps/cux.mor.twol.hfst: apertium-cux.cux.mor.twol
	hfst-twolc apertium-cux.cux.mor.twol -o .deps/cux.mor.twol.hfst

# notipehuan:no>tipe>huan
.deps/cux.seg.hfst: .deps/cux.mor.hfst .deps/cux.gen.hfst
	hfst-compose -F -1 .deps/cux.mor.hfst -2 .deps/cux.gen.hfst -o .deps/cux.seg.hfst 

.deps/cux.phon.hfst: apertium-cux.cux.phon
	hfst-lexc apertium-cux.cux.phon -o $@

.deps/cux.spellrelax.hfst: apertium-cux.cux.spellrelax 
	hfst-regexp2fst -S -o $@ < $<

$(LANG1).autophon.hfst: .deps/cux.phon.hfst
	hfst-fst2fst -w $< -o $@

$(LANG1).automorf.hfst: .deps/cux.mor.hfst .deps/cux.spellrelax.hfst
	hfst-invert $< |  hfst-compose -F -1 - -2 .deps/cux.spellrelax.hfst  | hfst-invert | hfst-fst2fst -w -o $@

$(LANG1).autogen.hfst: .deps/cux.gen.hfst
	hfst-compose-intersect -1 .deps/cux.gen.hfst -2 .deps/cux.mor.twol.hfst | hfst-fst2fst -w -o $@

$(LANG1).autoseg.hfst: .deps/cux.seg.hfst 
	hfst-fst2fst -w $< -o $@

$(LANG1).rlx.bin: apertium-cux.cux.rlx
	cg-comp $< $@

$(LANG1).autogen.att.gz: .deps/$(LANG1).gen.hfst
	hfst-compose-intersect -1 .deps/cux.gen.hfst -2 .deps/cux.mor.twol.hfst | hfst-eliminate-flags  | hfst-fst2txt | gzip -9 -c > $@ 

$(LANG1).automorf.att.gz: .deps/$(LANG1).mor.hfst .deps/cux.spellrelax.hfst
	hfst-invert $< |  hfst-compose -F -1 - -2 .deps/cux.spellrelax.hfst  | hfst-eliminate-flags | hfst-invert | hfst-fst2txt | gzip -9 -c > $@

$(LANG1).autoseg.att.gz: .deps/$(LANG1).seg.hfst
	hfst-fst2txt $< | gzip -9 -c > $@

$(LANG1).autogen.bin: $(LANG1).autogen.att.gz .deps/.d
	zcat < $< > .deps/$(LANG1).autogen.att
	lt-comp lr .deps/$(LANG1).autogen.att $@

$(LANG1).automorf.bin: $(LANG1).automorf.att.gz .deps/.d
	zcat < $< > .deps/$(LANG1).automorf.att
	lt-comp lr .deps/$(LANG1).automorf.att $@

$(LANG1).autoseg.bin: $(LANG1).autoseg.att.gz .deps/.d
	zcat < $< > .deps/$(LANG1).autoseg.att
	lt-comp lr .deps/$(LANG1).autoseg.att $@

$(LANG1).prob: $(BASENAME).$(LANG1).tagged $(LANG1).rlx.bin
	cat $< | cg-proc $(LANG1).rlx.bin | apertium-tagger -s 0 -u 2 $@ /dev/stdin

###############################################################################
## Distribution
###############################################################################

EXTRA_DIST=$(BASENAME).$(LANG1).lexc		\
		$(BASENAME).$(LANG1).twol	\
		$(BASENAME).$(LANG1).phon \
		$(BASENAME).$(LANG1).spellrelax \
		$(BASENAME).$(LANG1).rlx	\
		modes.xml

###############################################################################
## Installation stuff
###############################################################################
#
#   apertium_cux_dir: This is where the compiled binaries go
#   apertium_cux_srcdir: This is where the source files go

apertium_cuxdir=$(prefix)/share/apertium/$(BASENAME)/
apertium_cux_srcdir=$(prefix)/share/apertium/$(BASENAME)/

EXTRA_TARGETS=

if HAVE_HFSTOSPELL
EXTRA_TARGETS += $(LANG1).zhfst
endif # HAVE_HFSTOSPELL

apertium_cux_DATA=$(TARGETS_COMMON) $(EXTRA_TARGETS) 

pkgconfigdir = $(prefix)/share/pkgconfig
pkgconfig_DATA = $(BASENAME).pc

noinst_DATA=modes/$(LANG1)-morph.mode

install-data-local: install-modes
	$(INSTALL_DATA) $(BASENAME).$(LANG1).lexc $(DESTDIR)$(apertium_cux_srcdir)
	$(INSTALL_DATA) $(BASENAME).$(LANG1).twol $(DESTDIR)$(apertium_cux_srcdir)
	$(INSTALL_DATA) $(BASENAME).$(LANG1).rlx $(DESTDIR)$(apertium_cux_srcdir)


###############################################################################
## Cleanup
###############################################################################

CLEANFILES = $(TARGETS_COMMON) $(TARGETS_INTERMEDIATE)
clean-local:
	-rm -rf .deps modes

###############################################################################

test: all
	apertium-regtest test
