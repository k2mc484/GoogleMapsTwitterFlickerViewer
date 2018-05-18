import oauth2 as oauth
import tkinter
from tkinter import END
import math
import ssl
from urllib.request import urlopen, urlretrieve
from urllib.parse import urlencode, quote_plus
import json
import urllib 
import io
from io import BytesIO
from PIL import Image, ImageTk

# To run the program, call the last function in this file: startGUI().


# The Globals class demonstrates a better style of managing "global variables"
# than simply scattering the globals around the code and using "global x" within
# functions to identify a variable as global.
#
# We make all of the variables that we wish to access from various places in the
# program properties of this Globals class.  They get initial values here
# and then can be referenced and set anywhere in the program via code like
# e.g. Globals.zoomLevel = Globals.zoomLevel + 1
#
class Globals:
   
   rootWindow = None
   mapLabel = None

   defaultLocation = "Mauna Kea, Hawaii"
   mapLocation = defaultLocation
   mapFileName = 'googlemap.gif'
   mapSize = 400
   zoomLevel = 9

   mapType = "satellite"
   
   lat = 19.8206105
   lng = -155.4680936
   
   listOfCoordinates =[]
   
   listOfTweets = []
   listOfTweetsIndex = 0
   listOfTweetsURL = []

   listOfCoordinatesFlickr = []
   listOfPhotos = []
   listOfPhotosIndex = 0
# Given a string representing a location, return 2-element tuple
# (latitude, longitude) for that location 
#
# See https://developers.google.com/maps/documentation/geocoding/
# for details
#
def geocodeAddress(addressString):
   urlbase = "https://maps.googleapis.com/maps/api/geocode/json?address="
   url = urlbase + quote_plus(addressString)
   #
   # Google's documentation says that should provide an API key with
   # the URL, and tells you how to register for and obtain a free API key
   # I strongly recommend you get one you and then uncomment the line below and replace
   # YOUR-API-KEY with your key.
   # Get one here:
   #   https://developers.google.com/maps/documentation/geocoding/get-api-key
   # IF YOU DO NOT get an API KEY, this code often still works but sometimes
   # you will get "OVER_QUERY_LIMIT" errors from Google.
   #
   url = url + "&key=" + "AIzaSyAJp8i2y7KO8ksdFPUCpi1TYtTeuAt5ZOM"

   ctx = ssl.create_default_context()
   ctx.check_hostname = False
   ctx.verify_mode = ssl.CERT_NONE
   
   stringResultFromGoogle = urlopen(url, context=ctx).read().decode('utf8')
   jsonResult = json.loads(stringResultFromGoogle)
   if (jsonResult['status'] != "OK"):
      print("Status returned from Google geocoder *not* OK: {}".format(jsonResult['status']))
      return (0.0, 0.0) # this prevents crash in retrieveMapFromGoogle - yields maps with lat/lon center at 0.0, 0.0
   loc = jsonResult['results'][0]['geometry']['location']
   return (float(loc['lat']),float(loc['lng']))


# Contruct a Google Static Maps API URL that specifies a map that is:
# - width-by-height in size (in pixels)
# - is centered at latitude lat and longitude long
# - is "zoomed" to the give Google Maps zoom level
#
# See https://developers.google.com/maps/documentation/static-maps/
#
# YOU WILL NEED TO MODIFY THIS TO BE ABLE TO
# 1) DISPLAY A PIN ON THE MAP
# 2) SPECIFY MAP TYPE - terrain vs road vs ...
#
def getMapUrl(width, height, lat, lng, zoom,mapType):
   markers  = placeMarkers()
   urlbase = "http://maps.google.com/maps/api/staticmap?"
   args = "center={},{}&zoom={}&size={}x{}&format=gif{}".format(lat,lng,zoom,width,height,markers)
   mapType = "&maptype={}".format(mapType)
   return  urlbase+args+mapType

# Retrieve a map image via Google Static Maps API:
# - centered at the location specified by global propery mapLocation
# - zoomed according to global property zoomLevel (Google's zoom levels range from 0 to 21)
# - width and height equal to global property mapSize
# Store the returned image in file name specified by global variable mapFileName
#
def retrieveMapFromGoogle():
   lat, lng = geocodeAddress(Globals.mapLocation)

   Globals.lat = lat
   Globals.lng = lng
   url = getMapUrl(Globals.mapSize, Globals.mapSize, lat, lng, Globals.zoomLevel,Globals.mapType)
   urlretrieve(url, Globals.mapFileName)

########## 
#  basic GUI code

def displayMap():
   retrieveMapFromGoogle()    
   mapImage = tkinter.PhotoImage(file=Globals.mapFileName)
   Globals.mapLabel.configure(image=mapImage)
   # next line necessary to "prevent (image) from being garbage collected" - http://effbot.org/tkinterbook/label.htm
   Globals.mapLabel.mapImage = mapImage

def readEntriesSearchTwitterAndDisplayMap():
   loc = str(locationEntry.get())
   if(loc != ""):
       locationEntry.delete(0,END)
       Globals.mapLocation = loc
       displayMap()

        
   authTwitter()
   Globals.listOfTweetsIndex = 0
   Globals.listOfPhotosIndex =0
   
   
   
   searchString = str(searchEntry.get())
   if(searchString != ""):
       twitterString,coordinates,URL = searchTwitter(searchString, latlngcenter=[Globals.lat, Globals.lng])
       Globals.listOfTweets = twitterString
       Globals.listOfCoordinates = coordinates
       Globals.listOfTweetsURL = URL
       #print(Globals.listOfCoordinates)
       if(len(Globals.listOfTweets)>=1):
           num = Globals.listOfTweetsIndex 
           twitterLine = str(num + 1)+": "+ Globals.listOfTweets[Globals.listOfTweetsIndex]
           twitterText.delete(1.0,END)
           twitterText.insert(END,twitterLine)
           
       #Show Flickr image
       flickrString = searchFlickr(searchString, geo=(Globals.lat, Globals.lng))
       Globals.listOfPhotos = flickrString
      #The image URL
      
       if(len(Globals.listOfPhotos)>=1):
           url = photoURL(Globals.listOfPhotos[Globals.listOfPhotosIndex])
           #print(url)
           my_page = urlopen(url)
           my_picture = io.BytesIO(my_page.read())
           pil_img = Image.open(my_picture)
           tk_img = ImageTk.PhotoImage(pil_img)
      
           flickrText.image =tk_img
           flickrText.image_create(END, image=tk_img)
           flickrText.pack()
       displayMap()
       searchEntry.delete(0,END)

def placeMarkers():
    count = 0
    markerString = ""
    coordinates = Globals.listOfCoordinates
    for x in coordinates:
        if x != None:
            cords = x["coordinates"]
            lat = cords[1]
            lng = cords[0]
            if(count == Globals.listOfTweetsIndex):
                markerString = markerString + "&markers=color:red|size:mid|label:T|{},{}".format(lat,lng)
            else:
                markerString = markerString + "&markers=color:blue|size:mid|label:T|{},{}".format(lat,lng)
            count = count +1
    count2 = 0        
    flickrCoordinates = Globals.listOfCoordinatesFlickr     
    for y in flickrCoordinates:
            lat = y[1]
            lng = y[0]
            
            if(count2 == Globals.listOfPhotosIndex):
                markerString = markerString + "&markers=color:yellow|size:mid|label:F|{},{}".format(lat,lng)
            else:
                markerString = markerString + "&markers=color:green|size:mid|label:F|{},{}".format(lat,lng)
            count2 = count2 +1
    #######################
    #Flickr photo markers

    return markerString
    
def initializeGUIetc():
   global locationEntry
   global searchEntry
   global twitterText
   global flickrText
   global flickrTitle
   global twitterAlert
    

   Globals.rootWindow = tkinter.Tk()
   Globals.rootWindow.title("HW9 Q2")

   mainFrame = tkinter.Frame(Globals.rootWindow) 
   mainFrame.pack()

   leftFrame = tkinter.Frame(mainFrame)
   leftFrame.pack()

   rightFrame = tkinter.Frame(leftFrame)
   rightFrame.pack(side = tkinter.RIGHT)

   locationLabel = tkinter.Label(leftFrame,text = "Type in a location to see it on the map")
   locationLabel.pack()

   locationEntry = tkinter.Entry(leftFrame)
   locationEntry.pack()

   ##Search entry for tweet key word
   searchLabel = tkinter.Label(leftFrame,text = "Key word to find relevent tweets in the area")
   searchLabel.pack()

   searchEntry = tkinter.Entry(leftFrame)
   searchEntry.pack()

   readEntryAndDisplayMapButton = tkinter.Button(leftFrame, text="Show me the map!", command=readEntriesSearchTwitterAndDisplayMap)
   readEntryAndDisplayMapButton.pack()

   # we use a tkinter Label to display the map image
   Globals.mapLabel = tkinter.Label(leftFrame, width=Globals.mapSize, bd=2, relief=tkinter.FLAT)
   Globals.mapLabel.pack()

   #Twitter tweets frames and widgets
   twitterFrame = tkinter.Frame(rightFrame)
   twitterFrame.pack()
   
   twitterTitle = tkinter.Label(twitterFrame,text = "Tweets")
   twitterTitle.pack()
   
   twitterText = tkinter.Text(twitterFrame, height=5, width=90)
   twitterText.pack()

   twitterButtonFrame = tkinter.Frame(twitterFrame)
   twitterButtonFrame.pack()
   
   twitterButton = tkinter.Button(twitterButtonFrame, text="Show next tweet", command=showNextTweet)
   twitterButton.pack()
   
   twitterURLButton = tkinter.Button(twitterButtonFrame, text="Open current tweet in browser", command=openURL)
   twitterURLButton.pack(side = tkinter.LEFT)
   

   #Flickr images frames and widges
   flickrFrame = tkinter.Frame(rightFrame)
   flickrFrame.pack()
   
   flickrTitle = tkinter.Label(twitterFrame,text = "Flicker Images")
   flickrTitle.pack()
   
   flickrText = tkinter.Text(twitterFrame, height=30, width=90)
   flickrText.pack()

   flickrButton = tkinter.Button(twitterFrame, text="Show next image", command= showNextPhoto)
   flickrButton.pack()

   #Map fram
   mapTypeFrame = tkinter.Frame(leftFrame)
   mapTypeFrame.pack()

   
   roadMapButton = tkinter.Button(mapTypeFrame, text="Road Map", command=roadMap)
   roadMapButton.pack(side = tkinter.LEFT)
   satelliteMapButton = tkinter.Button(mapTypeFrame, text="Satellite Map", command=satelliteMap)
   satelliteMapButton.pack(side = tkinter.LEFT)
   hybridMapButton = tkinter.Button(mapTypeFrame, text="Hybrid Map", command=hybridMap)
   hybridMapButton.pack(side = tkinter.LEFT)
   terrainMapButton = tkinter.Button(mapTypeFrame, text="Terrain Map", command=terrainMap)
   terrainMapButton.pack()
   
   zoomFrame = tkinter.Frame(leftFrame)
   zoomFrame.pack()
   
   zoomInButton = tkinter.Button(zoomFrame, text="Zoom in", command=zoomIn)
   zoomInButton.pack(side = tkinter.LEFT)
   zoomOutButton = tkinter.Button(zoomFrame, text="Zoom out", command=zoomOut)
   zoomOutButton.pack()
   

def zoomOut():
   if(Globals.zoomLevel != 0):
       Globals.zoomLevel = Globals.zoomLevel - 1
       displayMap()
    
def zoomIn():
   if(Globals.zoomLevel != 18):
       Globals.zoomLevel = Globals.zoomLevel + 1
       displayMap()
    
def roadMap():
    Globals.mapType = "roadmap"
    displayMap()
    
def satelliteMap():
    Globals.mapType = "satellite"
    displayMap()

def hybridMap():
    Globals.mapType = "hybrid"
    displayMap()

def terrainMap():
    Globals.mapType = "terrain"
    displayMap()

def startGUI():
    initializeGUIetc()
    displayMap()
    Globals.rootWindow.mainloop()
def openURL():
    if(len(Globals.listOfTweetsURL)>=1):
        webbrowser.open(Globals.listOfTweetsURL[Globals.listOfTweetsIndex]["url"])


############### Twitter related functions#########
 
# The code in this file won't work until you set up your Twitter "app"
# at https://dev.twitter.com/apps
# After you set up the app, copy the four long messy strings and put them here.
#

CONSUMER_KEY = "Yf1xejhSXu1BizE9rfDmAvS7t"
CONSUMER_SECRET = "sueXh6m8MYewqjxVbivUrWuxQDaeFcJumVi0ioQW9fJNLVYRHr"
ACCESS_KEY = "992138241930391552-E8EGBOVWnSYYpn8TY0EyQCMZLB5xf21"
ACCESS_SECRET = "E8egJIfz6ci1gIN2Qv9kajZm7U8cXjLKVMQpCDw7CKY7U"

# Call this function after starting Python.  It creates a Twitter client object (in variable client)
# that is authorized (based on your account credentials and the keys above) to talk
# to the Twitter API. You won't be able to use the other functions in this file until you've
# called authTwitter()
#
def authTwitter():
    
    global client   
    consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
    access_token = oauth.Token(key=ACCESS_KEY, secret=ACCESS_SECRET)
    client = oauth.Client(consumer, access_token)


# Study the documenation at https://dev.twitter.com/rest/public/search
# to learn about construction Twitter queries and the format of the results
# returned by Twitter
#

# Try:
#       searchTwitter("finals")
#
# Iowa City's lat/lng is [41.6611277, -91.5301683] so also try:
#      searchTwitter("finals", latlngcenter=[41.6611277, -91.5301683])
#
def searchTwitter(searchString, count = 20, radius = 2, latlngcenter = None):
    global query
    global response
    global data
    global resultDict
    global tweets

    posts =[]
    cords = []
    URL = []
    query = "https://api.twitter.com/1.1/search/tweets.json?q=" + quote_plus(searchString) + "&count=" + str(count)

    if latlngcenter != None:
        query = query + "&geocode=" + str(latlngcenter[0]) + "," + str(latlngcenter[1]) + "," + str(radius) + "km"

    response, data = client.request(query)
    data = data.decode('utf8')
    resultDict = json.loads(data)
    # The key information in resultDict is the value associated with key 'statuses' (Twitter refers to
    # tweets as 'statuses'
    tweets = resultDict['statuses']
    gCount = 0

    for tweet in tweets:
        URL.append(tweet["entities"]["urls"][0])
        if tweet['coordinates'] != None:
            gCount = gCount + 1
            posts.append(printable(tweet['text']))
            cords.append(tweet['coordinates'])
        else:
            posts.append(printable(tweet['text']))
            cords.append(tweet['coordinates'])
            
            
    return posts, cords, URL
    

def whoIsFollowedBy(screenName):
    global response
    global resultDict
    
    query = "https://api.twitter.com/1.1/friends/list.json?&count=50"
    query = query + "&screen_name={}".format(screenName)
    response, data = client.request(query)
    data = data.decode('utf8')
    resultDict = json.loads(data)
    for person in resultDict['users']:
        print(person['screen_name'])
    
def getMyRecentTweets():
    global response
    global data
    global statusList 
    query = "https://api.twitter.com/1.1/statuses/user_timeline.json"
    response, data = client.request(query)
    data = data.decode('utf8')
    statusList = json.loads(data)
    for tweet in statusList:
        print(printable(tweet['text']))
        print()

def printable(s):
    result = ''
    for c in s:
        result = result + (c if c <= '\uffff' else '?')
    return result

def showNextTweet():
   if(len(Globals.listOfTweets)>=1):
      maxLength = len(Globals.listOfTweets) 
      if(Globals.listOfTweetsIndex != maxLength -1):
         Globals.listOfTweetsIndex = Globals.listOfTweetsIndex + 1
         line = str(Globals.listOfTweetsIndex+ 1)+": "+ Globals.listOfTweets[Globals.listOfTweetsIndex]
         twitterText.delete(1.0,END)
         twitterText.insert(END,line)
         
      else:
         Globals.listOfTweetsIndex = 0
         line = str(Globals.listOfTweetsIndex + 1)+": "+ Globals.listOfTweets[Globals.listOfTweetsIndex]
         twitterText.delete(1.0,END)
         twitterText.insert(END,line)
         
         
      displayMap()
         
         
def showNextPhoto():
    flickrText.delete(1.0,END)

    if(len(Globals.listOfPhotos)>=1):
        maxLength = len(Globals.listOfPhotos) 
        if(Globals.listOfPhotosIndex != maxLength -1):
            Globals.listOfPhotosIndex = Globals.listOfPhotosIndex + 1
            url = photoURL(Globals.listOfPhotos[Globals.listOfPhotosIndex])
            my_page = urlopen(url)
            my_picture = io.BytesIO(my_page.read())
            pil_img = Image.open(my_picture)
            tk_img = ImageTk.PhotoImage(pil_img)
            flickrText.image = tk_img
            flickrText.image_create(END, image=tk_img)
            flickrText.pack()
        else:
            Globals.listOfTweetsIndex = 0
            url = photoURL(Globals.listOfPhotos[Globals.listOfPhotosIndex])
            my_page = urlopen(url)
            my_picture = io.BytesIO(my_page.read())
            pil_img = Image.open(my_picture)
            tk_img = ImageTk.PhotoImage(pil_img)
            flickrText.image =tk_img
            flickrText.image_create(END, image=tk_img)
            flickrText.pack()
        displayMap()
##########################
#Flickr functions
#
#
#
#
#
#
#


flickrAPIKey = "eaf2f649cc81b88421a45ffd80b38958"

# Try things like:
#
# resultList = searchFlickr("kitten")
# showFlickrPhoto(resultList[0])
# showFlickrPhotoPage(resultList[0])
#
# resultList = searchFlickr("herky", geo=(41.6611277, -91.5301683))
# showFlickrPhoto(resultList[0])
# showFlickrPhotoPage(resultList[0])
# photoLoc(resultList[0])

def searchFlickr(topic, geo=None, maxNum = 20, radius=2):
    global url, resultFromFlickr, jsonresult, flickrPhotos, flickrAPIKey
    flickrCoordinates =[]
    base="https://api.flickr.com/services/rest/?"
    args = "method=flickr.photos.search&format=json&per_page={}&nojsoncallback=1".format(maxNum)
    topicPart = "&text=" + quote_plus(topic)

    noVerifyContext = ssl.create_default_context()
    noVerifyContext.check_hostname = False
    noVerifyContext.verify_mode = ssl.CERT_NONE
    
    url = base + args + topicPart + "&api_key=" + flickrAPIKey
    if geo != None:
        geoPart = "&lat={}&lon={}&radius={}".format(geo[0], geo[1], radius)
        url = url + geoPart
        
    resultFromFlickr= urlopen(url, context=noVerifyContext).read().decode('utf8')
    jsonresult = json.loads(resultFromFlickr)
    if jsonresult['stat'] == 'ok':
        flickrPhotos = jsonresult['photos']['photo']
        for x in flickrPhotos:
            lat,lng = photoLoc(x)
            flickrCoordinates.append([lng,lat])
        #print()
       # print(flickrCoordinates)
        print("{} photos found".format(len(flickrPhotos)))
        Globals.listOfCoordinatesFlickr = flickrCoordinates
        return flickrPhotos
    
    else:
        print("status returned from Flickr not ok")

def photoURL(photoListItem):
    farmId = photoListItem['farm']
    serverId = photoListItem['server']
    photoId = photoListItem['id']
    secret = photoListItem['secret']
    url = "https://farm{}.staticflickr.com/{}/{}_{}.jpg".format(farmId,serverId,photoId, secret)
    return url

def photoLoc(photoListItem):
    global photoI,flickrAPIKey
    base="https://api.flickr.com/services/rest/?"
    args = "method=flickr.photos.getInfo&format=json&nojsoncallback=1"
    idPart = "&photo_id=" + photoListItem['id']
    url = base + args + idPart + "&api_key=" + flickrAPIKey
    noVerifyContext = ssl.create_default_context()
    noVerifyContext.check_hostname = False
    noVerifyContext.verify_mode = ssl.CERT_NONE
    resultFromFlickr= urlopen(url, context=noVerifyContext).read().decode('utf8')
    photoI = json.loads(resultFromFlickr)
    photoI = photoI['photo']
    loc = photoI['location']
    lat = float(loc['latitude'])
    lon = float(loc['longitude'])
    return (lat, lon)

def photoInfo(photoListItem):
    global photoI,flickrAPIKey
    base="https://api.flickr.com/services/rest/?"
    args = "method=flickr.photos.getInfo&format=json&nojsoncallback=1"
    idPart = "&photo_id=" + photoListItem['id']
    url = base + args + idPart + "&api_key=" + flickrAPIKey
    noVerifyContext = ssl.create_default_context()
    noVerifyContext.check_hostname = False
    noVerifyContext.verify_mode = ssl.CERT_NONE
    resultFromFlickr= urlopen(url,context=noVerifyContext).read().decode('utf8')
    photoI = json.loads(resultFromFlickr)
    return photoI

import webbrowser
def showFlickrPhoto(photoListItem):
    webbrowser.open(photoURL(photoListItem))

def showFlickrPhotoPage(photoListItem):
    pI = photoInfo(photoListItem)
    pageURL = pI['photo']['urls']['url'][0]['_content']
    print(pageURL)
    webbrowser.open(pageURL)
