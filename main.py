print("Program Started")
from statistics import mean, fmean, median, median_grouped,mode
import csv
import matplotlib.pyplot as plt
from tqdm import tqdm
import sys
import time
import pickle
import random


USEPICKLE = False # Set this to true if you want to use saved data
PICKLENAME = "clusters.p" # name of file to save/load from
print("""
             ,,,,,,,,
           ,|||````||||
     ,,,,|||||       ||,
  ,||||```````       `||
,|||`                 |||,
||`     ....,          `|||
||     ::::::::          |||,
||     :::::::'     ||    ``|||,
||,     :::::'               `|||
`||,                           |||
 `|||,       ||          ||    ,||
   `||                        |||`
    ||                   ,,,||||
    ||              ,||||||```
   ,||         ,,|||||`
  ,||`   ||   |||`
 |||`         ||
,||           ||
||`           ||
|||,         |||
 `|||,,    ,|||
   ``||||||||`

    Let's go!!
""")

def progressbar(current,max, clusters, prefix="", size=60, file=sys.stdout): # Stolen and modified from Stack Overflow. This is used to display a progress bar. Only works in a proper terminal.
    count = max
    j = current

    x = int(size*j/count)
    file.write("%s[%s%s] %i/%i Nodes Processed, %i Clusters Discovered\r" % (prefix, "#"*x, "."*(size-x), j, count, clusters))
    file.flush()


def dbscan(points, e, min_pnts): # Performs DBSCAN on the set of points. 99% accurate. Still messes up sometimes, and I'm not sure why.
    print("========== Performing DBSCAN ==========")
    clusters = []
    total = len(points)
    visited = 0
    progressbar(visited, total,len(clusters)," ", 60)
    for point in points:
        if not point.visited:
            point.visit()
            visited += 1
            progressbar(visited, total,len(clusters)," ", 60)
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
                            progressbar(visited, total,len(clusters)+1," ", 60)
                            if p.clusterId == -1:
                                p.clusterId = cluster.id
                                cluster.add(p)
                                pn = get_neighborhood(p,points,e)
                                if len(pn) >= min_pnts:
                                    for i in pn:
                                        if i not in N:
                                            N.append(i)
                    clusters.append(cluster)
                else:
                    print("Something messed up!")
            else:
                point.noise = True
    return clusters

def plot_clusters(clusters,points): # Plots each cluster given to it, then the left over noise points.

    #print("\nNumber of clusters: ",len(clusters))
    for cluster in clusters:
        #print("Plotting cluster ", cluster.id)
        #print("\tCluster size: ",len(cluster.points))
        x = []
        y = []
        for point in cluster.points:
            x.append(point.x)
            y.append(point.y)
        plt.scatter(x, y, s=3)
        #print("\tX:%i\n\tY:%i" % (len(x),len(y)))

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


def get_neighborhood(point, points, e): # Returns the points surrounding a point.
    neighborhood = []
    x = point.x
    y = point.y
    for q in points:
        if dist(x,y,q.x,q.y) <= e:
            neighborhood.append(q)

    return neighborhood

def dist(x1,y1,x2,y2): # returns the euclidean distance between two points.
    return ((x1-x2)**2 + (y1-y2)**2)**0.5

class Point: # Point class to hold all of the information of a point
    def __init__(self, x, y):
        self.density = 0
        self.x = x
        self.y = y
        self.core = False
        self.visited = False
        self.noise = False
        self.clusterId = -1
    def visit(self):
        self.visited = True


class Cluster: # Cluster class, postly to hold the points
    def __init__(self):
        self.points = []
        self.id = -1
    def add(self, point):
        self.points.append(point)


# import the datasets
MINLEN = 30 # minimum length of a tweet
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
        if hatefreq.get(word) != None: # incriments the value if the key exists
            count = hatefreq.get(word) + 1
            hatefreq.update({word : count})
        elif(word not in cullwords): # otherwise create the key and set the value to 1
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
    # I do this by getting the mean, because I think thats probably the best way to go about it.
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
print("\tAmzn Mean: ",meanpark)
print("\tAmzn Max: ",maxpark)

print("Most hateful tweet:")
print(maxhatetweet)
print()
print("Most Amazon tweet:")
print(maxparktweet)

from collections import Counter

hatescores = Counter(hatefreq)
parkscores = Counter(parkfreq)
# Print the most common words to add to the cull list if needed. Debug tool.
#print(hatescores.most_common(30))
#print(parkscores.most_common(10))


# renormalzie the data, to make it %100-y

mh = max([max(hates), max(parks)])

#mh = max(hates)
for i in range(len(hates)):
    if hates[i] != 0:
        hates[i] = (hates[i]/mh)*100
#mh = max(parks)
for i in range(len(parks)):
    if parks[i] != 0:
        parks[i] = (parks[i]/mh)*100
del mh

points = []
flipper = 0
for i in range(len(hates)):
    d = (parks[i]**2 + hates[i]**2)**0.5
    if ( d <= 100):
        if  random.randrange(0,int(d*2+1)-int(d*2/100)) == 0:#flipper % 20: # flip to decrease the size of the dataset, to stop my computer from dying. 6 might be fine
            points.append(Point(parks[i],hates[i]))
            flipper = 0
        flipper +=1
    else:
        points.append(Point(parks[i],hates[i]))


# Load old data. Sorta doesn't work.
if USEPICKLE:
    try:
        infile = open(PICKLENAME, 'rb')
        load = pickle.load(infile)
        points = load[0]
        clusters = load[1]
        infile.close()
    except FileNotFoundError:
        print("No clusters file found, making a new one!")
        clusters = dbscan(points, 1,6)#3, 3)
else:
    clusters = dbscan(points, 1.5, 6)

# Save data
outfile = open(PICKLENAME,'wb')
pickle.dump([points, clusters], outfile)
outfile.close
plot_clusters(clusters,points)


#for point in points:
#    print(point.clusterId)
