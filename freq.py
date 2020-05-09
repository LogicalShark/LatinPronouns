import re
import math
import numpy as np
import pandas as pd

pronouns = ["ego", "tu", "is", "id", "eae", "ea", "nos", "vos", "ei"]
# stopw = stopwords.words('english')
with open("stopwords.txt", 'r') as swf:
    stopw = [x[0:-1] for x in swf.readlines()]

freqs = {}
totalFreqs = {}
totalCount = 0
diffDict = {"total": {}}
for p in pronouns:
    diffDict[p] = {}

def resetGlobals():
    global freqs, totalFreqs, totalCount, diffDict
    pronouns = ["ego", "tu"]  # , "is", "id", "eae", "ea", "nos", "vos", "ei"]
    # stopw = stopwords.words('english')
    with open("stopwords.txt", 'r') as swf:
        stopw = [x[0:-1] for x in swf.readlines()]

    freqs = {}
    totalFreqs = {}
    totalCount = 0
    diffDict = {"total": {}}
    for p in pronouns:
        diffDict[p] = {}


def getWordFrequencies(pro, removeStop):
    global totalCount, totalFreqs
    proFreqs = {}
    totalWords = 0
    f = open("Text/text_" + pro + ".txt", 'r')
    for line in f.readlines():
        for word in line.split(' '):
            if removeStop and (word in stopw or not re.match(r"[a-z][a-z]+", word)):
                continue
            if word in proFreqs.keys():
                proFreqs[word] += 1
            else:
                proFreqs[word] = 1
            if word in totalFreqs.keys():
                totalFreqs[word] += 1
            else:
                totalFreqs[word] = 1
            totalWords += 1
            totalCount += 1
    for w in proFreqs.keys():
        proFreqs[w] = math.log(proFreqs[w] / totalWords)
    freqs[pro] = proFreqs
    f.close()

def analyzeWordFreqs(restricted):
    for pro in pronouns:
        print(pro)
        getWordFrequencies(pro, restricted)
    for pro in pronouns:
        f = open("Freqs/freqs_" + pro + ".txt", 'w')
        for w in {k: v for k, v in sorted(freqs[pro].items(), key=lambda item: -item[1])}.keys():
            f.write(w + ", " + str(freqs[pro][w]) + "\n")
    for w in totalFreqs.keys():
        totalFreqs[w] = math.log(totalFreqs[w] / totalCount)
    f = open("Analysis/freqs_total.txt", 'w')
    for w in {k: v for k, v in sorted(totalFreqs.items(), key=lambda item: -item[1])}.keys():
        f.write(w + ", " + str(totalFreqs[w]) + "\n")

    freqF = open("Analysis/freq_words_" + ("un" if not restricted else "") +
                 "restricted.txt", 'w')
    data = pd.read_csv("words_" + ("un" if not restricted else "") + "restricted.csv", sep=",",
                       usecols=["Word", "Count"])
    total = sum(data["Count"])
    for n in range(len(data["Word"])):
        word = data["Word"][n]
        freq = math.log(data["Count"][n]/total)
        freqF.write(word + ", " + str(freq) + "\n")
        if not word in totalFreqs.keys():
            diffDict["total"][word] = 10000 + freq
        else:
            diffDict["total"][word] = freq - totalFreqs[word]
    freqF.close()
    for word in {k: v for k, v in sorted(totalFreqs.items(), key=lambda item: -item[1])}.keys():
        if not word in diffDict["total"].keys():
            diffDict["total"][word] = -10000 - totalFreqs[word]
    diffF = open("Analysis/freq_diff" + ("_un" if not restricted else "") + ".txt", 'w')
    for w in {k: v for k, v in sorted(diffDict["total"].items(), key=lambda item: item[1])}.keys():
        diffF.write(w + ", " + str(diffDict["total"][w]) + "\n")
    diffF.close()


def getLemmaFrequencies(pro, removeStop):
    global totalCount, totalFreqs
    proFreqs = {}
    totalWords = 0
    data = pd.read_csv("Lemma/lemma_" + pro + ".csv", usecols=["Total", "Ambiguous", "Word", "POS"])
    for n in range(len(data["Total"])):
        words = data["Word"][n].split("/")
        lemma = words[0].replace("j","i")
        if data["Total"][n] == "<1":
            continue
        else:
            count = int(data["Total"][n])
        if removeStop and (any([w == lemma for w in stopw]) or not re.match(r"[a-z][a-z]+", lemma)):
            continue
        if lemma in proFreqs.keys():
            proFreqs[lemma] += count
        else:
            proFreqs[lemma] = count
        if lemma in totalFreqs.keys():
            totalFreqs[lemma] += count
        else:
            totalFreqs[lemma] = count
        totalWords += count
        totalCount += count
    for w in proFreqs.keys():
        proFreqs[w] = math.log(proFreqs[w] / totalWords)
    freqs[pro] = proFreqs
    
def rewriteLemmaFiles():
    for pro in pronouns:
        print(pro)
        file = open("LemmaRaw/lemma_"+pro+".txt", 'r')
        outFile = open("Lemma/lemma_"+pro+".csv", 'w')
        outFile.write("Total,Ambiguous,Word,POS\n")
        for line in file.readlines():
            line = line.strip()
            if len(line) == 0:
                continue
            suffix = ""
            if " a, um :" in line:
                line = line[:line.index(" a, um :")] + " adj."
            elif not ". : " in line and not " e : " in line:
                # print(line, "verb?")
                line = line[:line.index(" :")] + ", PossibleVerb."
            else:
                line = line[:line.index(" :")]
            newLine = line[:line.index(" (")].strip() + ","
            newLine += '/'.join(line[line.index("(")+1:line.index(")")].split(", ")).strip() + ","
            newLine +=  '/'.join(line[line.index(")")+1:line.rindex(",")].split(", ")).strip() + ","
            newLine += line[line.rindex(",")+1:].strip()
            outFile.write(newLine + "\n")


def analyzeLemmaFreqs(restricted):
    for pro in pronouns:
        print(pro)
        getLemmaFrequencies(pro, restricted)
    for pro in pronouns:
        f = open("LemmaFreqs/lemmafreqs_" + pro + ".txt", 'w')
        for w in {k: v for k, v in sorted(freqs[pro].items(), key=lambda item: -item[1])}.keys():
            f.write(w + ", " + str(freqs[pro][w]) + "\n")
    for w in totalFreqs.keys():
        totalFreqs[w] = math.log(totalFreqs[w] / totalCount)
    f = open("LemmaFreqs/lemmafreqs_total.txt", 'w')
    for w in {k: v for k, v in sorted(totalFreqs.items(), key=lambda item: -item[1])}.keys():
        f.write(w + ", " + str(totalFreqs[w]) + "\n")

    freqF = open("Analysis/freq_lemmas_" +
                 ("un" if not restricted else "") + "restricted.txt", 'w')
    data = pd.read_csv("lemmas_" + ("un" if not restricted else "") + "restricted.csv", sep=",",
                       usecols=["Word", "Count"])  
    total = sum(data["Count"])
    for n in range(len(data["Word"])):
        word = data["Word"][n]
        freq = math.log(data["Count"][n]/total)
        freqF.write(word + ", " + str(freq) + "\n")
        if not word in totalFreqs.keys():
            diffDict["total"][word] = 10000 + freq
        else:
            diffDict["total"][word] = freq - totalFreqs[word]
    freqF.close()
    for word in {k: v for k, v in sorted(totalFreqs.items(), key=lambda item: -item[1])}.keys():
        if not word in diffDict["total"].keys():
            diffDict["total"][word] = -10000 - totalFreqs[word]
    diffF = open("Analysis/freq_diff" + ("_un" if not restricted else "") + "_lemmas.txt", 'w')
    for w in {k: v for k, v in sorted(diffDict["total"].items(), key=lambda item: item[1])}.keys():
        diffF.write(w + ", " + str(diffDict["total"][w]) + "\n")
    diffF.close()

def extractVerbs():
    for pro in pronouns:
        print(pro)
        outf = open("Verbs/verbs_"+pro+".csv", 'w')
        outf.write("Frequency,Verb\n")
        for word in {k: v for k, v in sorted(freqs[pro].items(), key=lambda item: -item[1])}.keys():
            outf.write(str(freqs[pro][word]) + "," + word + "\n")
    outf = open("Analysis/verbs_total.csv", 'w')
    outf.write("Frequency,Verb\n")
    for word in {k: v for k, v in sorted(totalFreqs.items(), key=lambda item: -item[1])}.keys():
        outf.write(str(totalFreqs[word]) + "," + word + "\n")

if __name__ == "__main__":
    # analyzeWordFreqs(False)
    # resetGlobals()
    analyzeWordFreqs(True)
    # resetGlobals()
    # analyzeLemmaFreqs(False)
    # extractVerbs()
    # resetGlobals()
    # analyzeLemmaFreqs(True)
    # extractVerbs()
    # file = open("lemmas_alt.txt", 'r')
    # outFile = open("Lemma/lemma_alt.csv", 'w')
    # outFile.write("Total,Ambiguous,Word,POS\n")
    # for line in file.readlines():
    #     line = line.strip()
    #     if len(line) == 0:
    #         continue
    #     suffix = ""
    #     if " a, um :" in line:
    #         line = line[:line.index(" a, um :")] + " adj."
    #     elif not ". : " in line and not " e : " in line:
    #         # print(line, "verb?")
    #         line = line[:line.index(" :")] + ", PossibleVerb."
    #     else:
    #         line = line[:line.index(" :")]
    #     newLine = line[:line.index(" (")].strip() + ","
    #     newLine += '/'.join(line[line.index("(") +
    #                                 1:line.index(")")].split(", ")).strip() + ","
    #     newLine += '/'.join(line[line.index(")") +
    #                                 1:line.rindex(",")].split(", ")).strip() + ","
    #     newLine += line[line.rindex(",")+1:].strip()
    #     outFile.write(newLine + "\n")
