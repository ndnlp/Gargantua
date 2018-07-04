import itertools
import operator
import xml.etree.ElementTree as et
import os
import sys

source_lang, target_lang = sys.argv[1:]

files = {}
for line in open("files.txt"):
    s, t = line.split()
    sl, sid = s.split(":", 1)
    tl, tid = t.split(":", 1)
    files[sid] = (sl, sid, tl, tid)

def reader(file):
    for line in file:
        doc_id, source_ids, target_ids = line.split("\t")
        source_ids = map(int, source_ids.split())
        target_ids = map(int, target_ids.split())
        yield doc_id, source_ids, target_ids

os.mkdir("sentence_alignment")

info_file = open("corpus_to_align/output_data_aligned/info.txt")
for doc_id, group in itertools.groupby(reader(info_file),
                                       operator.itemgetter(0)):
    assert doc_id.endswith(".txt")
    doc_id = doc_id[:-4]
    root = et.Element("alignments")
    root.attrib['source_id'] = doc_id
    try:
        root.attrib['translation_id'] = files[doc_id][3]
    except KeyError:
        sys.stderr.write("warning: skipping {}\n".format(doc_id))
        continue
    tree = et.ElementTree(root)
    for _, source_ids, target_ids in group:
        alignment = et.Element("alignment")

        if (files[doc_id][0], files[doc_id][2]) == (source_lang, target_lang):
            pass
        elif (files[doc_id][0], files[doc_id][2]) == (target_lang, source_lang):
            source_ids, target_ids = target_ids, source_ids

        source = et.Element("source")
        source.attrib['segments'] = " ".join("segment-{}".format(i-1) for i in source_ids)
        trans = et.Element("translation")
        trans.attrib['segments'] = " ".join("segment-{}".format(i-1) for i in target_ids)
        alignment.append(source)
        alignment.append(trans)
        root.append(alignment)
    tree.write("sentence_alignment/{}.align.xml".format(doc_id))
