import nltk

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
from nltk.tokenize import sent_tokenize
from summarizer import TransformerSummarizer


class TextProcessingUnit:
    # max text length supported by BERT.
    BERT_MAX = 512

    def __init__(self):
        # Load text summarization model
        self.summary_model = TransformerSummarizer(transformer_type="XLNet", transformer_model_key="xlnet-base-cased")

    # function to shorten the text
    def shorten_text(self, mysqldb_text, mongodb_text):
        def cut_text(text_sum):
            """
            function to cut text and remove repeated sentences on the text
            """
            total_sum = 0
            total_sent = []
            for s in sent_tokenize(text_sum):
                if total_sum <= 512:
                    total_sum = total_sum + len(s.split())
                    total_sent.append(s)
                else:
                    break
            sent = ' '.join(total_sent)
            return sent

        # reduce MongoDB text to new text of 1000 letters.
        mongodb_sum = self.summary_model(mongodb_text[:10000], ratio=0.2, num_sentences=20, max_length=1000)
        # append mongoDB text to MySql text
        final_text = mysqldb_text + " " + mongodb_sum
        # take the first 512 words of the total text
        final_text = cut_text(final_text)

        return final_text
