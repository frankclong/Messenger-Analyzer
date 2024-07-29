from enum import Enum 

class GeneralAnalysisType(Enum):
    TOP = 'Top 10 Most Messaged'
    MESSAGES_OVER_TIME = 'Messages over Time'
    MESSAGES_SENT_BY_HOUR = 'Messages Sent by Hour'

class ContactAnalysisType(Enum):
    MESSAGES_OVER_TIME = 'Messages over Time'
    WORD_SPECTRUM = 'Word Spectrum'