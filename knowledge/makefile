# build variables
CONCEPTNET_TARGET = $(DATA_DIRECTORY)/conceptnet-assertions-5.7.0.csv.gz
CONCEPTNET_SOURCE = 'https://s3.amazonaws.com/conceptnet/downloads/2019/edges/conceptnet-assertions-5.7.0.csv.gz'

ENGLISHNET_TARGET = $(DATA_DIRECTORY)/englishnet-assertions-5.7.0.csv.gz

DATABASE_TARGET = $(DATA_DIRECTORY)/database.sqlite $(DATA_DIRECTORY)/directed-graph.pkl
DATABASE_SOURCE = $(ENGLISHNET_TARGET)
DATABASE_DEPEND = knowledge/app.py knowledge/models/* knowledge/views/commands.py

# build rules
.PHONY: all clean

all: $(DATABASE_TARGET)

clean:
	rm -f $(CONCEPTNET_TARGET) $(ENGLISHNET_TARGET) $(DATABASE_TARGET)

$(CONCEPTNET_TARGET):
	wget --quiet --timestamping --show-progress --directory-prefix $(@D) \
	$(CONCEPTNET_SOURCE)

$(ENGLISHNET_TARGET): $(CONCEPTNET_TARGET)
	gunzip -c $(CONCEPTNET_TARGET) \
	| pv -perl --size `gunzip -c $(CONCEPTNET_TARGET) | wc -l` \
	| grep -P '^/a/\[/r/.+,/c/en/.+,(/c/en/|/[^c]).+\]\t' \
	| gzip > $(ENGLISHNET_TARGET)

$(DATABASE_TARGET): $(DATABASE_SOURCE) $(DATABASE_DEPEND)
	flask init $(ENGLISHNET_TARGET)
