import string
import time

import openai
from nltk.tokenize import wordpunct_tokenize
from seqeval.metrics import classification_report


def compute_scores(true_labels, pred_labels):
    new_true_labels = []
    new_pred_labels = []
    for t_lbls, p_lbls in zip(true_labels, pred_labels):
        new_true_labels.append([
            t_lbl for t_lbl, p_lbl in zip(t_lbls, p_lbls)
        ])

        new_pred_labels.append([
            p_lbl for t_lbl, p_lbl in zip(t_lbls, p_lbls)
        ])

    return classification_report(new_true_labels, new_pred_labels, output_dict=True)


def remove_punctuation(text):
    """
    Remove punctuation from text
    :param text: text to remove punctuation from
    :return:  text without punctuation
    """
    text = [word.lower() for word in wordpunct_tokenize(text)
            if word not in string.punctuation]
    return " ".join(text)


def text2labels(sentence):
    """
    Convert text to labels
    :param sentence: text to convert
    :return:  list of labels
    """
    tokens = wordpunct_tokenize(sentence.lower())

    labels = []
    for i, token in enumerate(tokens):
        try:
            if token not in string.punctuation:
                labels.append('O')
            elif token in ['.', '?', '!', ';']:
                labels[-1] = 'I-PERIOD'
            elif token == ',':
                labels[-1] = 'I-COMMA'

        except IndexError:

            print(f"Sentence can't start with punctuation {token}")
            continue
    return labels


def compute_scores(true_labels, pred_labels):
    new_true_labels = []
    new_pred_labels = []
    for t_lbls, p_lbls in zip(true_labels, pred_labels):
        new_true_labels.append([
            t_lbl for t_lbl, p_lbl in zip(t_lbls, p_lbls)
        ])

        new_pred_labels.append([
            p_lbl for t_lbl, p_lbl in zip(t_lbls, p_lbls)
        ])

    return classification_report(new_true_labels, new_pred_labels, output_dict=True)


def prepare_prompt(sent_text):
    return {"role": "user", "content": sent_text}


def chat_gpt_predict(prompt, api_key, model="gpt-3.5-turbo"):
    openai.api_key = api_key
    messages = [prepare_prompt(prompt)]
    while True:
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages
            )

        except openai.error.RateLimitError:

            time.sleep(60)
            continue
        break
    pred_text = response.choices[0].message.content.replace("\"", "")
    return pred_text
