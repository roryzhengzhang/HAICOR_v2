# build variables
CONCEPTNET_SOURCE = "https://s3.amazonaws.com/conceptnet/downloads/2019/edges/conceptnet-assertions-5.7.0.csv.gz"
CONCEPTNET_TARGET = data/conceptnet-assertions-5.7.0.csv.gz

ENGLISHNET_TARGET = data/englishnet-assertions-5.7.0.csv.gz

# build rules
.PHONY: all

all: $(ENGLISHNET_TARGET)

$(CONCEPTNET_TARGET): makefile
	rm -f $(CONCEPTNET_TARGET)
	wget -P data $(CONCEPTNET_SOURCE)

$(ENGLISHNET_TARGET): $(CONCEPTNET_TARGET) makefile
	gunzip -c $(CONCEPTNET_TARGET) \
	| pv -petl -s `gunzip -c $(CONCEPTNET_TARGET) | wc -l` \
	| grep -E '^/a/\[/r/.+,/c/en/.+,(/c/en/|/[^c]).+\]\t' \
	| gzip > $(ENGLISHNET_TARGET)
