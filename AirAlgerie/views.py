from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse 
from AirAlgerie.models import aviion, categoriee, vool, passsager, trajeet, reservatiion
from django.db.models import Q
from datetime import datetime, timedelta

def home(request):
    # Fetch all trajet objects from the database
    trajets = trajeet.objects.all()
    return render(request, 'home.html', {'trajets': trajets})

@csrf_exempt
def search_flights(request):
    if request.method == 'POST':
        checkInDate = request.POST.get('checkInDate')
        departureHour = request.POST.get('DepartureHour')
        destination = request.POST.get('destination')
        numberAdults = int(request.POST.get('numberadults', 0))
        numberChildren = int(request.POST.get('numberchildren', 0))
        flight_class = request.POST.get('class')
        print("checkInDate:", checkInDate)
        print("departureHour:", departureHour) 
        print("destination:", destination) 
        print("numberAdults:", numberAdults) 
        print("numberChildren:", numberChildren) 
        print("flight_class:", flight_class) 
        try:
            departureDateTime = datetime.strptime(f"{checkInDate} {departureHour}", "%Y-%m-%d %H:%M")
        except ValueError:
            return HttpResponse("Invalid date or time format")

        four_hours_delta = timedelta(hours=4)
        departure_time_lower = departureDateTime - four_hours_delta
        departure_time_upper = departureDateTime + four_hours_delta

        flights = vool.objects.filter(
            (Q(date_vol=checkInDate) & 
             Q(heure_depart__range=(departure_time_lower.time(), departure_time_upper.time())) &
             Q(trajeet__ville_arrive=destination)) |
            ((Q(date_vol=departureDateTime.date() - timedelta(days=1)) |
              Q(date_vol=departureDateTime.date() + timedelta(days=1)) |
              Q(date_vol=departureDateTime.date() + timedelta(days=2))) &
             Q(heure_depart__range=(departure_time_lower.time(), departure_time_upper.time())) &
             Q(trajeet__ville_arrive=destination))
        )
        

    trajets = []
    for flight in flights:
      trajets.extend(trajeet.objects.filter(fk_idvol=flight))
      
    arrivals=[]
    for flight in flights:
        trajet = flight.trajeet_set.first()  # Assuming one trajeet per flight
        duree_trajet = trajet.duree_trajet
       
        arrivals.append(flight.calculer_arrivee(duree_trajet))
    passagers=numberAdults+numberChildren
    
    prices = []
    for flight in flights:
    # Determine the price per passenger based on the selected class
        if flight_class == "Economic class":
            prix_par_passager = flight.trajeet_set.first().prix_trajet_economique
        elif flight_class == "Business class":
            prix_par_passager = flight.trajeet_set.first().prix_trajet_affaire
        elif flight_class == "first classe":
            prix_par_passager = flight.trajeet_set.first().prix_trajet_1er_classe
        trajet = flight.trajeet_set.first()
        distance = trajet.distance
        reduction_adult=(categoriee.objects.filter(type="adult").first().prix)/100
        prix_adult=(1-reduction_adult)*prix_par_passager*numberAdults*distance
        reduction_child=(categoriee.objects.filter(type="child").first().prix)/100
        prix_child=(1-reduction_child)*prix_par_passager*numberChildren*distance
        
        prices.append(prix_adult + prix_child)

    trajets_prices_arrivals = list(zip(trajets, prices ,arrivals))


    return render(request, 'search_vol_result.html', {
            'flights': flights,
            'trajets': trajets,
            'class': flight_class,
            'destination':destination,
            'checkInDate' :checkInDate,
            'departureHour':departureHour,
            'numberAdults': numberAdults,
            'numberChildren':numberChildren,
            'trajets_prices_arrivals':trajets_prices_arrivals,
            'prices':prices,
            'passagers': passagers
        })
