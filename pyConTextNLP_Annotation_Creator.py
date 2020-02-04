import pyConTextNLP.pyConText as pyConText
import pyConTextNLP.itemData as itemData
import networkx as nx
import pandas as pd
import spacy
import urllib
import os


def negations_pycontextnlp(clinical_text_df):
    # using scispacy only because we need its sentencizer
    scispacy_model = spacy.load('en_core_sci_lg')
    scispacy_model.add_pipe(scispacy_model.create_pipe('sentencizer'), before="parser")

    for index, row in clinical_text_df.iterrows():
        # if the row has a NaN value in the transcripts column, skip it
        if (pd.isna(clinical_text_df.iloc[index, 0])):
            continue

        print("Transcript " + str(index) + ", row " + str(index + 2) + ":")

        # print("Detected negated edges:")
        list_detected_negated_edges, list_positions = negations_pycontextnlp_individual_transcript(scispacy_model,
                                                                                                   row[0])

        print("Detected negated concepts:\n")
        for idx in range(len(list_detected_negated_edges)):

            # handle opposite case
            if 'opposite' in list_detected_negated_edges[idx][1].getCategory()[0]:

                list_positions_together = []
                for i in range(2):
                    for j in range(2):
                        list_positions_together.append(list_positions[idx][i][j])

                # print sentence being analyzed
                print("..." + row[0][min(list_positions_together):max(list_positions_together)] + "...")
                print("--------------------")
                print("..." + row[0][(0 if min(list_positions_together) - 100 < 0 else min(list_positions_together) - 100) : min(list_positions_together)]
                    + '|||||'
                    + row[0][min(list_positions_together):max(list_positions_together)]
                    + '|||||'
                    + row[0][max(list_positions_together) : (len(row[0]) if max(list_positions_together) + 100 > len(row[0]) else max(list_positions_together) + 100)] + "...")

                to_add = "".join(list_detected_negated_edges[idx][1].getCategory()[0].split('_opposite'))
                print("\nnegated concept '" + to_add + "' detected at position ("
                      + str(list_positions[idx][0][0]) + ", " + str(list_positions[idx][0][1])
                      + ") (" + row[0][list_positions[idx][0][0]:list_positions[idx][0][1]] + "), ("
                      + str(list_positions[idx][1][0]) + ", " + str(list_positions[idx][1][1]) + ") ("
                      + row[0][list_positions[idx][1][0]:list_positions[idx][1][1]] + ")\n")

                correct = input("Is this annotation correct? [y]es [n]o: ")
                if correct == 'y':
                    annotation_string = '(' \
                                        + "".join(list_detected_negated_edges[idx][1].getCategory()[0]) \
                                        + ',False,' + row[0][list_positions[idx][1][0]:list_positions[idx][1][1]] \
                                        + ',' + row[0][list_positions[idx][0][0]:list_positions[idx][0][1]] \
                                        + ',' + str(min(list_positions_together)) \
                                        + ',' + str(max(list_positions_together)) \
                                        + ',' + row[0][min(list_positions_together):max(list_positions_together)] \
                                        + ')'
                    clinical_text_df.iat[index, 1] = str(row[1]) + '\n' + annotation_string
                print('\n')

            # handle negative edge case
            elif 'neg' in list_detected_negated_edges[idx][0].getCategory()[0]:

                list_positions_together = []
                for i in range(2):
                    for j in range(2):
                        list_positions_together.append(list_positions[idx][i][j])

                # print sentence being analyzed
                print("..." + row[0][min(list_positions_together):max(list_positions_together)] + "...")
                print("--------------------")
                print("..." + row[0][(0 if min(list_positions_together) - 100 < 0 else min(list_positions_together) - 100) : min(list_positions_together)]
                    + '|||||'
                    + row[0][min(list_positions_together):max(list_positions_together)]
                    + '|||||'
                    + row[0][max(list_positions_together) : (len(row[0]) if max(list_positions_together) + 100 > len(row[0]) else max(list_positions_together) + 100)] + "...")

                to_add = "".join(list_detected_negated_edges[idx][1].getCategory()[0].split('_'))
                print("\nnegated concept '" + to_add + "' detected at position ("
                      + str(list_positions[idx][0][0]) + ", " + str(list_positions[idx][0][1]) + ") ("
                      + row[0][list_positions[idx][0][0]:list_positions[idx][0][1]] + "), ("
                      + str(list_positions[idx][1][0]) + ", " + str(list_positions[idx][1][1]) + ") ("
                      + row[0][list_positions[idx][1][0]:list_positions[idx][1][1]] + ")\n")

                correct = input("Is this annotation correct? [y]es [n]o: ")
                if correct == 'y':
                    annotation_string = '(' \
                                        + "".join(list_detected_negated_edges[idx][1].getCategory()[0]) \
                                        + ',False,' + row[0][list_positions[idx][1][0]:list_positions[idx][1][1]] \
                                        + ',' + row[0][list_positions[idx][0][0]:list_positions[idx][0][1]] \
                                        + ',' + str(min(list_positions_together)) \
                                        + ',' + str(max(list_positions_together)) \
                                        + ',' + row[0][min(list_positions_together):max(list_positions_together)] \
                                        + ')'
                    clinical_text_df.iat[index, 1] = str(row[1]) + '\n' + annotation_string
                print('\n')

    clinical_text_df.to_csv('data/exported_generated_annotations.csv')


def negations_pycontextnlp_individual_transcript(nlp, clinical_text):
    PYCONTEXTNLP_MODIFIERS = r'/' + os.getcwd() + '/data/pycontextnlp_modifiers.yml'
    PYCONTEXTNLP_TARGETS = r'/' + os.getcwd() + '/data/pycontextnlp_targets.yml'

    modifiers = itemData.get_items(PYCONTEXTNLP_MODIFIERS)
    targets = itemData.get_items(PYCONTEXTNLP_TARGETS)

    sentences = nlp(clinical_text)
    sentences = [sent.string for sent in sentences.sents]

    list_negated_edges = []
    list_positions = []
    curr_combined_length = 0

    for sentence in sentences:
        returned_negated_edges = pycontextnlp_markup_sentence(sentence.lower(), modifiers, targets)
        for edge in returned_negated_edges:
            list_positions.append(
                (
                    (curr_combined_length + edge[0].getSpan()[0], curr_combined_length + edge[0].getSpan()[1]),
                    (curr_combined_length + edge[1].getSpan()[0], curr_combined_length + edge[1].getSpan()[1])
                )
            )
        curr_combined_length += len(sentence)
        list_negated_edges.extend(returned_negated_edges)

    return (list_negated_edges, list_positions)


def pycontextnlp_markup_sentence(s, modifiers, targets, prune_inactive=True):
    markup = pyConText.ConTextMarkup()

    markup.setRawText(s)
    markup.cleanText()

    markup.markItems(modifiers, mode="modifier")
    markup.markItems(targets, mode="target")

    markup.pruneMarks()
    markup.dropMarks('Exclusion')

    markup.applyModifiers()

    markup.pruneSelfModifyingRelationships()
    if prune_inactive:
        markup.dropInactiveModifiers()

    list_negated_edges = []

    for edge in markup.edges():
        # modifier_category = edge[0].getCategory()
        # if('neg' in modifier_category[0]):
        #     # print(edge)
        #     list_negated_edges.append(edge)
        list_negated_edges.append(edge)

    return list_negated_edges


def main():
    clinical_text_df = pd.read_excel("data/eimara_annotations.xls")

    # file used for testing purposes
    # clinical_text_df = pd.read_excel("data/test_opposite_concepts.xls")

    # pycontextnlp method
    negations_pycontextnlp(clinical_text_df)


if __name__ == "__main__":
    main()
