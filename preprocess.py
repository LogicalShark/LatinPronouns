import re
import numpy as np
import pandas as pd

corpusDir = "Corpora/"
textDir = "Text/"
verbDir = "Verbs/"
pronouns = ["ego","tu","is","ea","id","nos","vos","ei","eae"]
endings = [r"([a-z]+[om])\b", r"([a-z]+s)\b", r"([a-z]+t)\b", r"([a-z]+t)\b",
           r"([a-z]+t)\b", r"([a-z]+mus)\b", r"([a-z]+tis)\b", r"([a-z]+nt)\b", r"([a-z]+nt)\b"]
cols = ["Source","Pre","Pro","Post"]

def extractText():
    for pro in pronouns:
        data = pd.read_csv(corpusDir+"corpus_"+pro+".csv",usecols=cols)
        open(textDir + "text_" + pro + ".txt", 'w').close()
        outf = open(textDir + "text_" + pro + ".txt", 'a')
        print(pro, len(data["Pro"]))
        for n in range(len(data["Pro"])):
            line = data["Pre"][n] + " " + data["Pro"][n] + \
                " " + data["Post"][n]
            line = line.replace("</s><s>", " ")
            line = line.replace("\n", " ")
            line = re.sub(r"[^a-zA-Z ]", "", line).lower()
            outf.write(line)
        outf.close()

def extractVerbs():
    for n in range(len(pronouns)):
        textf = open(textDir + "text_" + pronouns[n] + ".txt", 'r')
        open(verbDir + "verbs_" + pronouns[n], 'w').close()
        outf = open(verbDir + "verbs_" + pronouns[n], 'a')
        for line in textf.readlines():
            search = re.findall(endings[n], line)
            # print(search)
            if len(search) == 0:
                outf.write("NONE FOUND\n")
            else:
                for s in search:
                    outf.write(s + " ")
                outf.write("\n")
        outf.close()

if __name__ == "__main__":
    print("Text")
    extractText()
    print("Verbs")
    extractVerbs()
    print("Done")
