"""
This is a program for review sentiment tagging and keywords mining
"""
import csv
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.sentiment.util import *
from rake_nltk import Rake
from PyQt5.QtWidgets import QPushButton, QWidget, QLabel, QPlainTextEdit, QTextEdit, QGridLayout,QApplication
from PyQt5 import QtGui
from PyQt5.QtCore import Qt


class ReviewAnalyzer(QWidget):

    # Here we define the vocabulary to better extract the keywords from the reviews
    __pos_adj__ = 'good|great|nice|wonderful|amazing|comfortable|clean|polite|lovely|outstanding|fantastic|beautiful|large|cozy|big|accommodated|pleasant|consistent|reliable|welcoming|gracious|friendly|delightful|fresh|excellent|reasonable|helpful|favorite|ideal|decent|safe'
    __neg_adj__ = 'bad|worse|worst|terrible|horrible|noisy|awful|poor|disappointing|cheap|stained|indifferent|rude|inadequate|out of date|slow|small|loud|noisy|chilly|stiff|moldy|weak|unacceptable|dirty|moldy|rusted|incompetent'
    __noun__ = 'place|room|pool|remodel|staff|location|furniture|bathroom|TV|TV reception|hot water|shower|lobby|bar|elevator|front desk|views|view|noises|front desk staff|housekeeping|smell|service|carpet|narrow|waiters|food|price|restaurant|internet|stay|bed|sofa|branch'
    __adverb__ = 'pretty|very|so|too|already|apparently|really|just|extraordinary|extremely'
    __be__ = 'be|is|isn\'t|is not|are|are not|aren\'t|was|wasn\'t|was not|were|were not|weren\'t'
    __junct__ = 'and|but'
    __slang__ = ''

    __pos_adj__ = __pos_adj__.split('|')
    __neg_adj__ = __neg_adj__.split('|')
    __noun__ = __noun__.split('|')
    __be__ = __be__.split('|')
    __adverb__ = __adverb__.split('|')
    __junct__ = __junct__.split('|')

    # Here we get the file from https://www.cs.uic.edu/~liub/FBS/sentiment-analysis.html#datasets for deep analyse
    # get the positive adj
    with open('pos.csv') as csvfile:
        positive_reader = csv.reader(csvfile, delimiter=',')
        __full_pos_adj__ = []
        for word in positive_reader:
            pos = "".join(word)
            __full_pos_adj__.append(pos)

    # get the negative adj
    with open('neg.csv') as csvfile:
        negative_reader = csv.reader(csvfile, delimiter=',')
        __full_neg_adj__ = []
        for word in negative_reader:
            neg = "".join(word)
            __full_neg_adj__.append(pos)

    def __init__(self):
        super().__init__()
        self.initUI()

    def word_count(self, review):
        """
        This function count the positive words and negative words in the each review
        :param review: string
        :return: list
        """
        pos_count = 0
        neg_count = 0
        for word in review.split():
            if word.lower() in self.__pos_adj__:
                pos_count = pos_count + 1
            elif word.lower() in self.__neg_adj__:
                neg_count = neg_count + 1
        return [pos_count, neg_count]


    def sentiment_tag(self, review):
        """
        This function makes sentiment tag for the review, we get the weight from experiment.
        The constant c is used to avoid the neg_score to be zero.
        :param review: string
        :return: string
        """
        c = 0.01
        adj_count = self.word_count(review)
        if adj_count[1] != 0 or adj_count[0] != 0:
            pos_score = adj_count[0] / (adj_count[0] + adj_count[1])
            neg_score = adj_count[1] / (adj_count[0] + adj_count[1])
            if 8 * neg_score > 2 * pos_score:
                sen_tag = 'This is a Negative Review'
            else:
                sen_tag = 'This is a Positive Review'
        else:
            # when we cannot figure out, we use the nltk package
            sid = SentimentIntensityAnalyzer()
            scores = sid.polarity_scores(review)
            neg_score = scores['neg']
            pos_score = scores['pos']
            if pos_score / (neg_score + c) < 10:
                sen_tag = 'This is a Negative Review'
            else:
                sen_tag = 'This is a Positive Review'
        return sen_tag

    def quick_keyword_mining(self, review):
        """
        We use the rake_nltk to extract some keywords that not include in our self-defined list.
        :param review: string
        :return: list
        """
        r = Rake()
        r.extract_keywords_from_text(review)

        results = r.get_ranked_phrases()
        results_range = len(results) // 2
        for i in range(results_range):
            results[i] = results[i].lower()
        return results[:results_range]

    def keyword_mining(self, review):
        """
        This is the major function we use to do the keyword mining.
        :param review: string
        :return: list
        """
        # extract keywords from the review
        pat_list = list()
        keywords = list()
        # Example : nice room
        for i in self.__pos_adj__:
            for j in self.__noun__:
                pat_list.append(i + ' ' + j)

        # Example : terrible room
        for i in self.__neg_adj__:
            for j in self.__noun__:
                pat_list.append(i + ' ' + j)

        # Example : room was noisy
        for n in self.__noun__:
            for b in self.__be__:
                for pa in self.__pos_adj__:
                    pat_list.append(n + ' ' + b + ' ' + pa)
                for na in self.__neg_adj__:
                    pat_list.append(n + ' ' + b + ' ' + na)

        # Example : room was pretty bad
        for n in self.__noun__:
            for b in self.__be__:
                for adv in self.__adverb__:
                    for pa in self.__pos_adj__:
                        pat_list.append(n + ' ' + b + ' ' + adv + ' ' + pa)
                    for na in self.__neg_adj__:
                        pat_list.append(n + ' ' + b + ' ' + adv + ' ' + na)

        pattern = re.compile('|'.join(pat_list), re.IGNORECASE)
        matches = pattern.findall(review)
        for match in matches:
            keywords.append(match.lower())
        return keywords

    def analyzer(self, review):
        """
        This function is used to combine the sentiment tagging and keywords mining and return the analysing results.
        :param review: string
        :return: dictionary
        """
        analyzer_result = {}
        analyzer_result['review_tag'] = self.sentiment_tag(review)
        analyzer_result['review_keywords'] = self.keyword_mining(review)
        other_keywords = self.quick_keyword_mining(review)
        other_keywords = other_keywords[:5]
        analyzer_result['other_keywords'] = []
        for word in other_keywords:
            if word not in analyzer_result['review_keywords']:
                if len(word.split()) > 1:
                    analyzer_result['other_keywords'].append(word.lower())
        return analyzer_result

    def initUI(self):
        """
        Include the GUI to get input and display the results.
        :return:
        """
        # set the background color
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)

        # set the UI
        hint_label1 = QLabel("Please enter the review below:")
        hint_label1.setFixedHeight(40)
        hint_label2 = QLabel("Analysing results: ")
        hint_label2.setFixedHeight(40)
        label_font = QtGui.QFont("Times", 18, QtGui.QFont.Bold)
        hint_label1.setFont(label_font)
        hint_label2.setFont(label_font)

        input_review = QPlainTextEdit()
        input_review.setFixedHeight(60)
        btn1 = QPushButton("Start", self)
        btn2 = QPushButton("Clear", self)
        button_font = QtGui.QFont("Times", 13, QtGui.QFont.Bold)
        btn1.setFont(button_font)
        btn2.setFont(button_font)

        analyze_result = QTextEdit()
        grid = QGridLayout()
        grid.setSpacing(6)
        grid.addWidget(hint_label1, 1, 0)
        grid.addWidget(input_review, 2, 0, 3, 0)
        grid.addWidget(btn1, 4, 0)
        grid.addWidget(btn2, 4, 1)
        grid.addWidget(hint_label2, 5, 0)
        grid.addWidget(analyze_result, 6, 0, 7, 0)
        self.setLayout(grid)

        def analysing():
            """
            Define the analyzer and display the results.
            :return:
            """
            result = self.analyzer(input_review.toPlainText())
            display_tag = str(result['review_tag'])
            display_other = result['other_keywords']
            display_keywords = ""
            for index, keyword in enumerate(result['review_keywords']):
                display_index = 'Keyword ' + str(index) + ':'
                display_keywords = display_keywords + display_index + ' ' + keyword + '\n'
            for other_index, other_word in enumerate(display_other):
                display_index = 'Keyword ' + str(other_index + len(result['review_keywords'])) + ':'
                display_keywords = display_keywords + display_index + ' ' + other_word + '\n'

            display_words = display_tag + '\n' + display_keywords
            analyze_result.setText(display_words)
        btn1.clicked.connect(analysing)

        def clear():
            """
            clear the results and inputs.
            :return:
            """
            analyze_result.setText("")
            input_review.setPlainText("")
        btn2.clicked.connect(clear)

        self.setGeometry(400, 150, 600, 500)
        self.setWindowTitle("Review Analyzer")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    analyzer = ReviewAnalyzer()
    analyzer.show()
    sys.exit(app.exec_())