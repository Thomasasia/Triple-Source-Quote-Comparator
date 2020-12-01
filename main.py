from statistics import mean, fmean, median, median_grouped,mode
import csv


# import the datasets
trumpstats = []
initial = True # To not read the first line, which has extra information
with open("trumptweets.csv", encoding='utf8') as file:
    reader = csv.reader(file,delimiter=',')
    for row in reader:
        if(initial):
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
with open("southpark.csv", encoding='utf8') as file:
    reader = csv.reader(file,delimiter=',')
    line = 1
    for row in reader:
        if(line%2==1): # only read even lines, as odd ones contain junk.
            line+=1
            continue
        else:
            park.append(row[3].lower())
            line+=1

# These are the words to be ignored, due to the high frequency in our language
cullwords = "the of and to a in for is on that by this with i you it not or be are from at as your all have new more an was we will home can us about if page my rt @ me do you too like get but they just did didn't what that that's".split()

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




# Obtain cool statistics
meanhate = 0
meanpark = 0
maxhate = 0
maxhatetweet = "test"
maxpark = 0
maxparktweet = "test"
for stat in trumpstats:
    try:
        if maxhate < stat[1]:
            maxhate = stat[1]
            maxhatetweet = stat[0]
        if maxpark < stat[2]:
            maxpark = stat[2]
            maxparktweet=stat[0]
        meanhate += stat[1]
        meanpark += stat[2]
    except UnicodeEncodeError:
        pass
meanhate = meanhate/len(trumpstats)
meanpark = meanpark/len(trumpstats)



print("Stats:")
print("\tHate Mean: ",meanhate)
print("\tHate Max: ",maxhate)
print("\tPark Mean: ",meanpark)
print("\tPark Max: ",maxpark)

print(maxhatetweet)
print(maxparktweet)

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
