import json
from nltk import tokenize
import re


class AutomaticSub:
    def __init__(self, text, time):
        self.text = text
        self.time = time


class Match:
    def __init__(self, start, end, confidence):
        self.start = start
        self.end = end
        self.confidence = confidence


class Sentence:
    def __init__(self, text, matches, index):
        self.text = text
        self.matches = matches
        self.index = index


class Caption:
    def __init__(self, start, end, text, confidence, index):
        self.start = start
        self.end = end
        self.text = text
        self.confidence = confidence
        self.index = index


def toTimestamp(ms):
    """ Converts milliseconds to a WebVTT time stamp. """
    s = (ms // 1000) % 60
    m = (ms // (1000 * 60)) % 60
    h = (ms // (1000 * 60 * 60))
    ms = ms % 1000
    return "{:02}:{:02}:{:02}.{:03}".format(h, m, s, ms)


def clip(n):
    """ Clips a number in [0, 1]. """
    if n < 0:
        return 0
    if n > 1:
        return 1
    return n


def writeCaptions(captions, file):
    """ Writes a list of Captions to a WebVTT file. """
    output = "WEBVTT"
    for caption in captions:
        output += "\n\n"
        output += "{} --> {}\n".format(toTimestamp(caption.start),
                                       toTimestamp(caption.end))
        output += caption.text

    with open(file, "w") as f:
        f.write(output)


def loadAutomaticSubs(file):
    """ Loads Youtube automatically generated subtitles from file. """
    subtitles = []
    with open(file, "r", encoding="utf-8") as f:
        for caption in json.load(f)["events"]:
            if "segs" not in caption:
                continue
            caption_start = caption["tStartMs"]
            for segment in caption["segs"]:
                text = segment["utf8"].strip().lower()
                if not len(text) or text == "[ __ ]":
                    continue
                start = caption_start
                if "tOffsetMs" in segment:
                    start += segment["tOffsetMs"]
                subtitles.append(AutomaticSub(text, start))
    return subtitles


def loadTranscript(file):
    transcript = []
    with open(file, "r", encoding="utf-8") as f:
        transcript = f.read().split("\n")
    return transcript


def loadTranscriptNLTK(file):
    """ Loads transcript from file. """
    transcript = []
    with open(file, "r", encoding="utf-8") as f:
        raw = re.sub("\n+", "\n", f.read()).split("\n")
        for paragraph in raw:
            transcript += tokenize.sent_tokenize(paragraph)
    return transcript


def toWords(s):
    """ Turn a sentence into a list of words. """
    s = re.sub("\[.+?\]", "", s).lower()
    s = tokenize.word_tokenize(s)
    words = []
    for word in s:
        if re.search("[a-z0-9]", word):
            if "'" in word:
                words[-1] += word
            else:
                words.append(word)
    return words
