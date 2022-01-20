import sqlite3
import time
import numpy as np
from datetime import datetime

con = sqlite3.connect('FlightLeg.db')
cur = con.cursor()
cur.execute('''CREATE TABLE FlightLeg
               (id, tailNumber, sourceAirportCode, destinationAirportCode, sourceCountryCode, destinationCountryCode, departureTimeUtc, landingTimeUtc)''')

tailNumber, source_airport_code, source_country_code, destination_airport_code, destination_country_code, departure_time, landing_time = np.genfromtxt('flightlegs.csv', dtype=str, delimiter=";", skip_header=1, unpack=True)
for i in range(len(tailNumber)):
  cur.execute("INSERT INTO FlightLeg values (?, ?, ?, ?, ?, ?, ?, ?)", (i, tailNumber[i], source_airport_code[i], destination_airport_code[i], source_country_code[i], destination_country_code[i], departure_time[i], landing_time[i]))

#for row in cur.execute("SELECT * FROM FlightLeg"):
#  print(row)

###calculating values for 2 new columns
cur.execute("SELECT * FROM FlightLeg")
fmt = '%Y-%m-%d %H:%M:%S'
table = cur.fetchall()
full_table = np.empty([len(table), 10], dtype=object)
for i in range(len(table)):
  row = table[i]

  #calculating flight duration
  flight_duration = round((time.mktime(datetime.strptime(row[7], fmt).timetuple())-time.mktime(datetime.strptime(row[6], fmt).timetuple()))/60)
  
  #checking for flight crossing borders 'D' for domestic and 'I' for International
  if row[4] == row[5]:
    flightType = 'D'
  else:
    flightType = 'I'
  
  #constructing new table from rows of the old one and determined values for 2 new columns
  for j in range(10):
    if j < 8:
      full_table[i,j] = row[j]
    elif j == 8:
      full_table[i,j] = flight_duration
    else:
      full_table[i,j] = flightType

###cell for checking db
#for row in cur.execute("SELECT * FROM FlightLeg"):
#  print(row)

#adding two new columns
cur.execute("ALTER TABLE FlightLeg ADD COLUMN flightDuration INTEGER")
cur.execute("ALTER TABLE FlightLeg ADD COLUMN flightType TEXT")

#insering all data back to the db
cur.execute("DELETE FROM FlightLeg WHERE id != -1")
for i in range(1000):
  cur.execute("INSERT INTO FlightLeg values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (full_table[i,0], full_table[i,1], full_table[i,2], full_table[i,3], full_table[i,4], full_table[i,5], full_table[i,6], full_table[i,7], full_table[i,8], full_table[i,9]))

###another cell to see the db
#for row in cur.execute("SELECT * FROM FlightLeg"):
#  print(row)

# 1.     Który samolot wykonał najwięcej lotów? 
for top_number_of_flights in cur.execute("SELECT tailNumber, COUNT(1) FROM FlightLeg GROUP BY tailNumber ORDER BY COUNT(*) DESC LIMIT 1"):
  print("Airplane that took most flights has tail number %s and took %i flights." % (top_number_of_flights[0], top_number_of_flights[1]))
  
# 2.     Który samolot przeleciał najwięcej minut? 
for time_flying in cur.execute("SELECT tailNumber, SUM(flightDuration) FROM FlightLeg GROUP BY tailNumber ORDER BY SUM(flightDuration) DESC LIMIT 1"):
  print("Airplane that spent most time airborne is %s and was flying for %i minutes." % (time_flying[0], time_flying[1]))
  
# 3.     Który lot, w podziale na krajowe i zagraniczne, był najkrótszy, a który najdłuższy? 

#najdłuższy miedzynarodowy lot
for time_flying in cur.execute("SELECT * FROM FlightLeg WHERE flightType LIKE 'i' ORDER BY flightDuration DESC LIMIT 1"):
  print("Longest international flight took %i minutes. It was taken by plane with tail number of %s, departed from %s %s on %s and landed at %s %s on %s." % 
        (time_flying[8], time_flying[1], time_flying[2], time_flying[4], time_flying[6], time_flying[3], time_flying[5], time_flying[7]))

#najkrotszy miedzynarodowy lot
for time_flying in cur.execute("SELECT * FROM FlightLeg WHERE flightType LIKE 'i' ORDER BY flightDuration LIMIT 1"):
  print("Shortest international flight took %i minutes. It was taken by plane with tail number of %s, departed from %s %s on %s and landed at %s %s on %s." % 
        (time_flying[8], time_flying[1], time_flying[2], time_flying[4], time_flying[6], time_flying[3], time_flying[5], time_flying[7]))

#najdłuższy domowy lot
for time_flying in cur.execute("SELECT * FROM FlightLeg WHERE flightType LIKE 'd' ORDER BY flightDuration DESC LIMIT 1"):
  print("Longest domestic flight took %i minutes. It was taken by plane with tail number of %s, departed from %s %s on %s and landed at %s %s on %s." % 
        (time_flying[8], time_flying[1], time_flying[2], time_flying[4], time_flying[6], time_flying[3], time_flying[5], time_flying[7]))

#najkrotszy domowy lot
for time_flying in cur.execute("SELECT * FROM FlightLeg WHERE flightType LIKE 'd' ORDER BY flightDuration LIMIT 1"):
  print("Shortest domestic flight took %i minutes. It was taken by plane with tail number of %s, departed from %s %s on %s and landed at %s %s on %s." % 
        (time_flying[8], time_flying[1], time_flying[2], time_flying[4], time_flying[6], time_flying[3], time_flying[5], time_flying[7]))

  
