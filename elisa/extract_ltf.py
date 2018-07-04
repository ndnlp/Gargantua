import xml.etree.ElementTree as et
import sys
import os

srcdir = sys.argv[1]
dstdir = sys.argv[2]
alignment_path = os.path.join(srcdir, "sentence_alignment")
langs = sys.argv[3:]

files = {}
for filename in os.listdir(alignment_path):
    if filename.endswith(".xml"):
        tree = et.parse(os.path.join(alignment_path, filename))
        root = tree.getroot()
        assert root.tag == "alignments"
        f = {}
        l = {}
        for attr in ["source_id", "translation_id"]:
            doc_id = root.attrib[attr]
            for lang in langs:
                filename = "{}/{}/ltf/{}.ltf.xml".format(srcdir, lang, doc_id)
                if os.path.isfile(filename):
                    f[lang] = doc_id
                    l[attr] = lang
                    break
        files[f[l["source_id"]]] = f
        print("{}:{}\t{}:{}".format(l["source_id"], f[l["source_id"]],
                                    l["translation_id"], f[l["translation_id"]]))

try:
    os.makedirs(dstdir)
except OSError:
    pass
for lang in ["source", "target"]:
    for name in ["untokenized", "tokenized", "prepared"]:
        os.makedirs("{}/{}_language_corpus_{}".format(dstdir, lang, name))

def process(xmlfilename, lang, doc_id):
    tree = et.parse(xmlfilename)
    root = tree.getroot()

    assert root.tag == "LCTL_TEXT"
    assert len(root) == 1
    doc = root[0]
    assert doc.tag == "DOC"
    assert len(doc) == 1
    text = doc[0]
    assert text.tag == "TEXT"

    files = {}
    for name in ["untokenized", "tokenized", "prepared"]:
        files[name] = open("{}/{}_language_corpus_{}/{}.txt".format(dstdir, lang, name, doc_id), "w")

    for seg in text:
        seg_id = seg.attrib['id']
        #print(doc_id, seg_id)
        original_text = [child for child in seg if child.tag == "ORIGINAL_TEXT"]
        assert len(original_text) == 1
        original_text = original_text[0].text
        files["untokenized"].write(" ".join(original_text.split()) + "\n")
        tokenized = [child.text.strip() for child in seg if child.tag == "TOKEN"]
        tokenized = " ".join(tokenized)
        assert "\n" not in tokenized
        files["tokenized"].write(tokenized + "\n")
        files["prepared"].write(tokenized.lower() + "\n")

for doc_id, f in files.items():
    sl, tl = langs
    process("{}/{}/ltf/{}.ltf.xml".format(srcdir, sl, f[sl]), "source", doc_id)
    process("{}/{}/ltf/{}.ltf.xml".format(srcdir, tl, f[tl]), "target", doc_id)

