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

    total_neg_concepts_detected = 0
    total_expected_negated_concepts = 0

    precision_sum = 0.
    recall_sum = 0.
    f1_sum = 0.
    total_transcripts_passed = 0.

    for index, row in clinical_text_df.iterrows():
        # if the row has a NaN value in the transcripts column, skip it
        if (pd.isna(clinical_text_df.iloc[index, 0])):
            continue

        print("Transcript " + str(index) + ", row " + str(index + 2) + ":")

        # print("Detected negated edges:")
        list_detected_negated_edges, list_positions = negations_pycontextnlp_individual_transcript(scispacy_model,
                                                                                                   row[0])

        print("Detected negated concepts:")
        set_detected_negated_concepts = set()
        for idx in range(len(list_detected_negated_edges)):
            # handle opposite case
            if 'opposite' in list_detected_negated_edges[idx][1].getCategory()[0]:
                to_add = "".join(list_detected_negated_edges[idx][1].getCategory()[0].split('_opposite'))
                set_detected_negated_concepts.add(to_add)
                print("negated concept '" + to_add + "' detected at position ("
                      + str(list_positions[idx][0][0]) + ", " + str(list_positions[idx][0][1])
                      + ") (" + row[0][list_positions[idx][0][0]:list_positions[idx][0][1]] + "), ("
                      + str(list_positions[idx][1][0]) + ", " + str(list_positions[idx][1][1]) + ") ("
                      + row[0][list_positions[idx][1][0]:list_positions[idx][1][1]] + ")")
            # handle negative edge case
            elif 'neg' in list_detected_negated_edges[idx][0].getCategory()[0]:
                to_add = "".join(list_detected_negated_edges[idx][1].getCategory()[0].split('_'))
                set_detected_negated_concepts.add(to_add)
                print("negated concept '" + to_add + "' detected at position ("
                      + str(list_positions[idx][0][0]) + ", " + str(list_positions[idx][0][1]) + ") ("
                      + row[0][list_positions[idx][0][0]:list_positions[idx][0][1]] + "), ("
                      + str(list_positions[idx][1][0]) + ", " + str(list_positions[idx][1][1]) + ") ("
                      + row[0][list_positions[idx][1][0]:list_positions[idx][1][1]] + ")")
        print(set_detected_negated_concepts)

        print("Expected negated concepts:")
        if pd.isnull(row[1]):
            expected_negated_concepts = []
        else:
            expected_concepts = "".join(row[1].split())
            expected_concepts = expected_concepts[1:-1].split(')(')
            expected_negated_concepts = []
            for concept in expected_concepts:
                if ('false' in concept or 'False' in concept):
                    # TEMPORARY: ignore corner cases of related concepts
                    # if(
                    #     'breath' not in concept
                    #     and 'shortnessofbreath' not in concept
                    #
                    #     and 'lightheadedness' not in concept
                    #     and 'dizziness' not in concept
                    #
                    #     and 'hyperthermia' not in concept
                    #     and 'fever' not in concept
                    # ):

                    expected_negated_concepts.append(concept.split(',')[0])
        print(expected_negated_concepts)

        true_positives = 0.
        false_positives = 0.
        for concept in set_detected_negated_concepts:
            if concept in expected_negated_concepts:
                true_positives += 1.
            else:
                false_positives += 1.
        false_negatives = len(expected_negated_concepts) - true_positives

        if true_positives == 0 and false_positives == 0 and false_negatives == 0:
            transcript_precision = 1.
            transcript_recall = 1.
            transcript_f1 = 1.
        elif true_positives == 0 and (false_positives > 0 or false_negatives > 0):
            transcript_precision = 0.
            transcript_recall = 0.
            transcript_f1 = 0.
        else:
            transcript_precision = true_positives / (true_positives + false_positives)
            transcript_recall = true_positives / (true_positives + false_negatives)
            transcript_f1 = 2 * (
                        (transcript_precision * transcript_recall) / (transcript_precision + transcript_recall))

        print("Precision for this transcript: " + str(transcript_precision))
        print("Recall for this transcript: " + str(transcript_recall))
        print("F1 for this transcript: " + str(transcript_f1))

        total_neg_concepts_detected += true_positives
        total_expected_negated_concepts += len(expected_negated_concepts)
        precision_sum += transcript_precision
        recall_sum += transcript_recall
        f1_sum += transcript_f1
        total_transcripts_passed += 1.

        print('\n\n')

    print('###################################################')
    print('Total number of negated concepts detected / All negated concepts: ' + str(
        total_neg_concepts_detected) + '/' + str(total_expected_negated_concepts))
    print('Average precision: ' + str(precision_sum / total_transcripts_passed))
    print('Average recall: ' + str(recall_sum / total_transcripts_passed))
    print('Average F1: ' + str(f1_sum / total_transcripts_passed))


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
