from statistics import mean, fmean, median, median_grouped,mode
import csv
import matplotlib.pyplot as plt
from tqdm import tqdm
import sys
import time
import pickle


USEPICKLE = True
PICKLENAME = "clusters.p"


def progressbar(current,max, prefix="", size=60, file=sys.stdout): # From stack overflow
    count = max
    j = current

    x = int(size*j/count)
    file.write("%s[%s%s] %i/%i\r" % (prefix, "#"*x, "."*(size-x), j, count))
    file.flush()


def dbscan(points, e, min_pnts):
    clusters = []
    total = len(points)
    visited = 0
    progressbar(visited, total,"Computing Nodes: ", 60)
    for point in points:
        if not point.visited:
            point.visit()
            visited += 1
            progressbar(visited, total,"Computing Nodes: ", 60)
            N = get_neighborhood(point, points, e)
            point.density = len(N)
            if len(N) >= min_pnts:
                point.core = True
                if point.clusterId == -1: # Should always be true
                    cluster = Cluster()
                    cluster.id = len(clusters)
                    cluster.add(point)
                    for p in N:
                        if not p.visited:
                            p.visit()
                            visited += 1
                            progressbar(visited, total,"Computing Nodes: ", 60)
                            if p.clusterId == -1:
                                p.clusterId = cluster.id
                                pn = get_neighborhood(p,points,e)
                                if len(pn) >= min_pnts:
                                    for i in pn:
                                        if i not in N:
                                            N.append(i)
                                            #print(len(N))
                    clusters.append(cluster)
                    print(clusters)

                else:
                    print("Something messed up!")
            else:
                point.noise = True
    return clusters

def plot_clusters(clusters,points):


    for cluster in clusters:
        x = []
        y = []
        for point in cluster.points:
            x.append(point.x)
            y.append(point.y)
            plt.scatter(x, y, s=3)

    x = []
    y = []
    for point in points:
        if point.clusterId == -1:
            x.append(point.x)
            y.append(point.y)
    plt.scatter(x,y,s=3)

    plt.ylabel("1-Star Amazon Video Game Review Similarity")
    plt.xlabel("Hate Speech Score")
    plt.show()


def get_neighborhood(point, points, e):
    neighborhood = []
    x = point.x
    y = point.y
    for q in points:
        if dist(x,y,q.x,q.y) >= e:
            neighborhood.append(q)

    return neighborhood

def dist(x1,y1,x2,y2):
    return ((x1-x2)**2 + (y1-y2)**2)**0.5

class Point:
    x = 0
    y = 0
    def __init__(self, x, y):
        self.x = x
        self.y = y
    density = 0
    core = False
    def visit(self):
        self.visited = True
    visited = False
    noise = False
    clusterId = -1

class Cluster:
    points = []
    id = -1
    def __init__(self,points):
        self.points = points
    def __init__(self):
        pass
    def add(self, point):
        self.points.append(point)


# import the datasets
MINLEN = 30
trumpstats = []
initial = True # To not read the first line, which has extra information
with open("trumptweets.csv", encoding='utf8') as file:
    reader = csv.reader(file,delimiter=',')
    for row in reader:
        if(initial or len(row[2]) <= 30): # Filter the first line which is garbage, as well as anything that is really short (to save my poor computer from this np problem)
            initial = False
            continue
        else:
            trumpstats.append([row[2].lower(),0,0]) # append the text, but leave room for the scoring

hate = []
initial = True
with open("hatespeech.csv", encoding='utf8') as file:
    reader = csv.reader(file,delimiter=',')
    for row in reader:
        if(initial):
            initial = False
            continue
        if(int(row[2]) + int(row[3]) >= int(row[4])): # only count if the tweet is sufficiently hateful
            hate.append(row[6].lower())

park = []
with open("reviews.csv", encoding='utf8') as file:
    reader = csv.reader(file,delimiter=',')
    #line = 1
    for row in reader:
        #if(line%2==1): # only read even lines, as odd ones contain junk.
        #    line+=1
        #    continue
        #else:
        park.append(row[0].lower()) # 3 for southpark
        #line+=1

# These are the words to be ignored, due to the high frequency in our language
cullwords = "the of and to a in for is on that by this with i you it not or be are from at game play games game. any much ever am had buy very after first don't as lol &amp tell said being never bad them why im say your it's no i'll right, yeah. now, okay, you, &amp; u where time were him because when yeah, even real girl . man girl he's still good look only y'all , could over back what's there's let been would there it. well who has one take ain't aint he's mr. been would there going her here his no, right need let's then want really make people well, going some well, she can't see now  its than 2 other going i've way think we're well you're got up these so oh gonna he our out come know how oh, all thank you! keep at have new more an was we will home can us about if page my rt @ me do you too like get but they i'm work just did didn't what that that's go".split()

# Create dictionaries of word frequencies
hatefreq = {}
parkfreq = {}

for line in hate:
    for word in line.split():
        if hatefreq.get(word) != None:
            count = hatefreq.get(word) + 1
            hatefreq.update({word : count})
        elif(word not in cullwords):
            hatefreq.update({word : 1})

for line in park:
    for word in line.split():
        if parkfreq.get(word) != None:
            count = parkfreq.get(word) + 1
            parkfreq.update({word : count})
        elif(word not in cullwords):
            parkfreq.update({word : 1})

# Compare each line to the dictionaries, to create a score for each word in the tweet

for tweet in trumpstats:
    sentence = tweet[0].split()
    for word in sentence: # cull the words
        if word in cullwords:
            sentence.remove(word)
            continue

    # hate calculation:
    hatred = []
    for word in sentence:
        if hatefreq.get(word) != None:
            hatred.append(hatefreq.get(word))
        else:
            hatred.append(0)

    # southpark calculation:
    parkery = []
    for word in sentence:
        if parkfreq.get(word) != None:
            parkery.append(parkfreq.get(word))
        else:
            parkery.append(0)

    # Set the new hate and park scores for the trump tweet
    tweet[1] = mean(hatred)
    tweet[2] = mean(parkery)




# Obtain cool statistics and also create the list of points for our plot
meanhate = 0
meanpark = 0
maxhate = 0
maxhatetweet = "test"
maxpark = 0
maxparktweet = "test"
# Here is where my variable naming reached its limit.
hates = []
parks = []
for stat in trumpstats:
    if maxhate < stat[1]:
        maxhate = stat[1]
        maxhatetweet = stat[0]
    if maxpark < stat[2]:
        maxpark = stat[2]
        maxparktweet=stat[0]
    meanhate += stat[1]
    meanpark += stat[2]
    hates.append(stat[1])
    parks.append(stat[2])
meanhate = meanhate/len(trumpstats)
meanpark = meanpark/len(trumpstats)



print("Stats:")
print("\tHate Mean: ",meanhate)
print("\tHate Max: ",maxhate)
print("\tPark Mean: ",meanpark)
print("\tPark Max: ",maxpark)

print("Most hateful tweet:")
print(maxhatetweet)
print()
print("Most Amazon tweet:")
print(maxparktweet)

from collections import Counter

hatescores = Counter(hatefreq)
parkscores = Counter(parkfreq)
#print(hatescores.most_common(30))
#print(parkscores.most_common(10))

# renormalzie the data, to make it %100-y

mh = max([max(hates), max(parks)])

for i in range(len(hates)):
    if hates[i] != 0:
        hates[i] = (hates[i]/mh)*100

for i in range(len(parks)):
    if parks[i] != 0:
        parks[i] = (parks[i]/mh)*100
del mh

points = []
flipper = 0
for i in range(len(hates)):
    if ((parks[i]**2 + hates[i]**2)**0.5) <= 45:
        if flipper > 20: # flip to decrease the size of the dataset, to stop my computer from dying. 6 might be fine
            points.append(Point(parks[i],hates[i]))
            flipper = 0
        flipper +=1
    else:
        points.append(Point(parks[i],hates[i]))

print("yeet")


if USEPICKLE:
    try:
        infile = open(PICKLENAME, 'rb')
        clusters = pickle.load(infile)
        infile.close()
    except FileNotFoundError:
        print("No clusters file found, making a new one!")
        clusters = dbscan(points, 3, 3)
else:
    clusters = dbscan(points, 3, 3)
print("yeet")
print(clusters)
outfile = open(PICKLENAME,wb)
pickle.dump(clusters, outfile)
outfile.close
plot_clusters(clusters,points)
print("yeet")

"""
sentences = [text.split() for text in sentences]

dictionary = corpora.Dictionary(sentences)

feat_c=len(dictionary.token2id)
corpus=[dictionary.doc2bow(text) for text in sentences]

model = models.TfidfModel(corpus)

for trump in trumpsen:
    tweet = trump[0].split()
    for t in tweet:
        if t in cullwords:
            tweet.remove(t)

    vec = dictionary.doc2bow(tweet)
    index = similarities.SparseMatrixSimilarity(model[corpus],num_features=feat_c)

    sim = index[model[vec]]

    trump[1] = max(sim)


print(trumpsen)
"""
