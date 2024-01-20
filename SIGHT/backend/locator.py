import google.generativeai as palm
import googlemaps
import os
from datetime import datetime
import psycopg2
from dotenv import load_dotenv

# setup section
a='AIzaSyCOnOQkks'
b='_tDZEubzMLfkTr'
c='a9E1R5oC7-4'
gmaps = googlemaps.Client(key=a+b+c)

palm.configure(api_key='AIzaSyC7A1ZN0ALCKhka49NSWF0nBtXKLIT_19w')

connection_string = 'postgresql://cgaswin:4fE2RHFeQnpC@ep-cold-morning-42359364.us-east-2.aws.neon.tech/cryptcode?sslmode=require'

conn = psycopg2.connect(connection_string)

cur = conn.cursor()



#==========

def get_popular_places(cords, place_type, place_name='', radius=1500, rankby='prominence'):
    """
    Function to get popular places with their details based on coordinates.

    Args:
        lat (float): Latitude of the location.
        lng (float): Longitude of the location.
        radius (int, optional): Search radius in meters. Defaults to 1500 meters.
        place_type (str, optional): Type of place to search for. Defaults to 'restaurant'.
        rankby (str, optional): Specifies the ranking method. Defaults to 'prominence'.

    Returns:
        list: List of dictionaries containing place details.
    """
    places = gmaps.places_nearby(location=cords, radius=radius, type=place_type, rank_by=rankby)

    places_details = []

    for place in places['results']:
        place_id = place['place_id']
        details = gmaps.place(place_id, fields=['name', 'rating', 'user_ratings_total', 'geometry'])
        distance = gmaps.distance_matrix(origins=cords, destinations=(details['result']['geometry']['location']['lat'], details['result']['geometry']['location']['lng']))['rows'][0]['elements'][0]['distance']['value']
        try:
          place_details = {
              'name': details['result']['name'],
              'rating': details['result']['rating'],
              'user_ratings_total': details['result']['user_ratings_total'],
              'coordinates': details['result']['geometry']['location'],
              'distance': 1 if distance==0 else distance
          }
        except:
          place_details = {
            'name': details['result']['name'],
            'rating': 0.1,
            'user_ratings_total': 0.1,
            'coordinates': details['result']['geometry']['location'],
            'distance': 1 if distance==0 else distance
        }
        places_details.append(place_details)

    # Rank places based on rating and number of reviews
    places_details.sort(key=lambda x: (x['rating'], x['user_ratings_total']), reverse=True)

    return places_details
    
    
# to get the validator data from PALM LLM
def validator(uid,type_, description):
	model_id="models/text-bison-001"
	prompt='''I am trying to start a Bicycle selling business in India. {{description}}. I want to know the market value and amount of customers of my business. what are some of my strong competitors. what is the per customer value? What are the potential risks and challenges my business may face? When can I expect to be profitable? what are some suggestions for me, give me an update about the current market? keep the answer small and don't repeat this questions, don't provide any links. answer in two paragraph.'''

	completion=palm.generate_text(
		model=model_id,
		prompt=prompt,
		temperature=0.99,
		max_output_tokens=400,
	)
	result=completion.result
	result=result.replace('**','')
	result=result.replace('*','')
	history(uid,type_,description,result)
	return result
	
def dist(a):
	if a>0:return a
	return 1


ranks=[]

def get_rank(coordinates,type_,size):
	error=[]

	if size=='large':
		size=2000
	elif size=='medium':
		size=1000
	elif size=='small':
		size=500
	ranks=[]
	compsd=[]
	compsr=[]
	comp_details={}
	for c in coordinates:

		rank=0
		weight=0
		compd=0
		compr=0
		try:
			competitors=get_popular_places(c, place_type=type_, radius=size)
		except Exception as e:
			print(e)
			error.append(c)
			continue
	  
		#to get few compepitors to put in map we find competitors above average weight
		avg_weight=sum([b['rating']*b['user_ratings_total']/dist(b['distance']) for b in competitors])/len(competitors)

		for b in competitors:
			#print(b)
			weight = b['rating']*b['user_ratings_total']/b['distance']
			if weight>avg_weight*.9:
				comp_details[b['name']]=[b['coordinates'],weight]
			compd+=b['distance']
			compr+=b['rating']*b['user_ratings_total']
		
			rank=rank+weight
		ranks.append(rank)
		compsd.append(compd)
		compsr.append(compr)
		#print(ranks)


	l = len(ranks)
	newl = ranks.copy()
	newl.sort()
	ranks = [newl.index(i)+1 for i in ranks]
	ranks=[l+1-i for i in ranks]

	#print(ranks)
	print(compsd)
	print(compsr)
	if len(compsd)!=0:
		compsd_avg=sum(compsd)/len(compsd)
	else:
		compsd_avg=1
	for i in range(len(compsd)):
		if compsd[i]<(compsd_avg*80/100):
			compsd[i]='relatively more competitors closely'
		elif compsd[i]==0:
			compsd[i]='make sure place got enough population density'
		else:
			compsd[i]=''
	compsr_avg=sum(compsr)/len(compsr)
	for i in range(len(compsr)):
		if compsr[i]>(compsr_avg*120/100):
			compsr[i]='comparatively good competitors in this area'
		elif compsr[i]==0:
			compsr[i]='make sure place got enough population density'
		else:
			compsr[i]=''
	#print(compsd)
	#print(compsr)
	for i in error:
		ind=call.index(c)
		ranks.insert(ind,'error')
		compsd.insert(ind,'error')
		compsr.insert(ind,'error')

	return {'rank':ranks,'observation1':compsd,'observation2':compsr,'competitors':comp_details}


# to store the user interaction
def history(uid,industry,des,res):
	

	#cur.execute("INSERT INTO History (uid, des, sol, date, time) VALUES (%S,%s,%s,%s,%s)", (uid, industry+'-'+des, res,datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime("%H:%M"));
    #conn.commit()
	return	    
	

