from sklearn.cluster import KMeans
from sklearn.metrics import confusion_matrix,classification_report,accuracy_score
from sklearn.metrics import adjusted_rand_score
import matplotlib.pyplot as plt
import pandas as pd

#Cluster contains 4 centers generated with sklearn.dataset make blob
df = pd.read_csv("testScripts/cluster.csv")
X = df.drop('label', axis=1)
Y = df.label
scores = []
f = open("testScripts/results.txt", 'w')
#obviously doesn't work well if you assume only 3
for i in range(1, 6):
    kmeans = KMeans(i,init='k-means++')
    kmeans.fit(X)
    score = adjusted_rand_score(Y, kmeans.labels_)
    scores.append(score)
    print(str(i) + " : " + str(score))
    f.write(str(score) + "\n")

plt.plot(scores)
plt.savefig("testScripts/rand_scores.png")

f.close()



