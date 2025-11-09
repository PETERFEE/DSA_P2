import predict
import random
import alg1
from predict import conf
from alg1 import *

stressFile = open("dataset/stress.txt", "r")
totalTime = 0.0
counter = 1
classifier = SpamDecisionTree()

while True:
    try:
        line = stressFile.readline()
    except:
        continue
    if not line and counter > 100000:
        break
    confidence = random.uniform(0, 1)
    verdict, probability, time = classifier.classify(line.strip(), confidence)
    totalTime += time
    counter += 1
    if counter % 10000 == 0:
        print(f"Parsed {counter} lines")

print(f"The total time for the decision-tree algorithm was {(totalTime / 1000):.2f} seconds.")