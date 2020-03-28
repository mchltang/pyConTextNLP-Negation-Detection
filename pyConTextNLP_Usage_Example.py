import pyConTextNLP.pyConText as pyConText
import pyConTextNLP.itemData as itemData
import networkx as nx
import os

PYCONTEXTNLP_MODIFIERS = r'/' + os.getcwd() + '/data/pycontextnlp_modifiers.yml'
PYCONTEXTNLP_TARGETS = r'/' + os.getcwd() + '/data/pycontextnlp_targets.yml'

test_str = "Patient denied n/v/d."

modifiers = itemData.get_items(PYCONTEXTNLP_MODIFIERS)
targets = itemData.get_items(PYCONTEXTNLP_TARGETS)

markup = pyConText.ConTextMarkup()

print(test_str.lower())

markup.setRawText(test_str.lower())

# print(markup)
# print(len(markup.getRawText()))

markup.cleanText()

# print(markup)
# print(len(markup.getText()))

markup.markItems(modifiers, mode="modifier")
markup.markItems(targets, mode="target")

# for node in markup.nodes(data=True):
#     print(node)

markup.pruneMarks()

# for node in markup.nodes(data=True):
#     print(node)

markup.applyModifiers()

for edge in markup.edges():
    print(edge)