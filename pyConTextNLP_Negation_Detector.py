import pyConTextNLP.pyConText as pyConText
import pyConTextNLP.itemData as itemData
import networkx as nx
import pandas as pd
import spacy
import urllib


def negations_pycontextnlp(clinical_text_df):
    # using scispacy only because we need its sentencizer
    scispacy_model = spacy.load('en_core_sci_lg')
    scispacy_model.add_pipe(scispacy_model.create_pipe('sentencizer'), before="parser")

    total_neg_concepts_detected = 0
    total_neg_concepts_passed = 0

    total_sum_frac_float = 0.
    total_transcripts_passed = 0.

    for index, row in clinical_text_df.iterrows():
        # if the row has a NaN value in the transcripts column, skip it
        if(pd.isna(clinical_text_df.iloc[index, 0])):
            continue

        print("Transcript " + str(index) + ":")

        # print("Detected negated edges:")
        list_detected_negated_edges = negations_pycontextnlp_individual_transcript(scispacy_model, row[0])

        print("Detected negated concepts:")
        set_detected_negated_concepts = set()
        for edge in list_detected_negated_edges:
            set_detected_negated_concepts.add("".join(edge[1].getCategory()[0].split('_')))
        print(set_detected_negated_concepts)

        print("Expected negated concepts:")
        expected_concepts = "".join(row[1].split())
        if(len(expected_concepts) == 0):
            continue
        expected_concepts = expected_concepts[1:-1].split(')(')
        expected_negated_concepts = []
        for concept in expected_concepts:
            if('false' in concept or 'False' in concept):

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

        num_neg_concepts_passed = 0
        num_neg_concepts_detected = 0
        for concept in expected_negated_concepts:
            if(concept in set_detected_negated_concepts):
                num_neg_concepts_detected += 1
            num_neg_concepts_passed += 1

        print("Number of negated concepts detected / Total negated concepts: " + str(num_neg_concepts_detected) + '/' + str(num_neg_concepts_passed))

        total_neg_concepts_detected += num_neg_concepts_detected
        total_neg_concepts_passed += num_neg_concepts_passed

        if(num_neg_concepts_passed != 0):
            total_sum_frac_float += (num_neg_concepts_detected / num_neg_concepts_passed)
            total_transcripts_passed += 1.

        print('\n\n')

    print('###################################################')
    print('Total number of negated concepts detected / All negated concepts: ' + str(total_neg_concepts_detected) + '/' + str(total_neg_concepts_passed))
    print('Average recall: ' + str(total_sum_frac_float / total_transcripts_passed))


def negations_pycontextnlp_individual_transcript(nlp, clinical_text):
    PYCONTEXTNLP_MODIFIERS = r'/C:/Users/mchlt/Downloads/School/Research/PyContextNLP/pyConTextNLP-Negation-Detection/data/pycontextnlp_modifiers.yml'
    PYCONTEXTNLP_TARGETS = r'/C:/Users/mchlt/Downloads/School/Research/PyContextNLP/pyConTextNLP-Negation-Detection/data/pycontextnlp_targets.yml'

    modifiers = itemData.get_items(PYCONTEXTNLP_MODIFIERS)
    targets = itemData.get_items(PYCONTEXTNLP_TARGETS)

    sentences = nlp(clinical_text)
    sentences = [sent.string.strip() for sent in sentences.sents]

    list_negated_edges = []

    for sentence in sentences:
        list_negated_edges.extend(pycontextnlp_markup_sentence(sentence.lower(), modifiers, targets))

    return list_negated_edges


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
        modifier_category = edge[0].getCategory()
        if('neg' in modifier_category[0]):
            # print(edge)
            list_negated_edges.append(edge)

    return list_negated_edges


def main():
    clinical_text_df = pd.read_excel("data/ConceptExtracEval_ODEMSA.xls")

    # pycontextnlp method
    negations_pycontextnlp(clinical_text_df)


if __name__ == "__main__":
    main()