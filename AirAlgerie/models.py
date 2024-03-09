from django.db import models
import math
from datetime import timedelta
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
# Create your models here.


class aviion(models.Model):
    num_avion = models.IntegerField(primary_key=True)  
    nom_avion = models.CharField(max_length=100)
    autonomie_avion = models.FloatField()
    capacite_economique = models.IntegerField(default=1)
    capacite_affaire = models.IntegerField(default=1)
    capacite_1er_classe = models.IntegerField(default=1)
    prix_km_economique = models.FloatField(default=1)
    prix_km_affaire = models.FloatField(default=1)
    prix_km_1er_classe = models.FloatField(default=1)
   
    class Meta :
        db_table = "avion"


class categoriee(models.Model):
    id_categorie = models.AutoField(primary_key=True)
    type = models.CharField(max_length=100)
    prix = models.FloatField()    
   
    class Meta :
        db_table = "categorie"


class passsager(models.Model):
    ID_passager = models.AutoField(primary_key=True)
    Nom_passager = models.CharField(max_length=100)
    prenom_passager = models.CharField(max_length=100)
    email_passager = models.EmailField(max_length=100)
    num_telephone_passager = models.IntegerField()
    fk_idcategorie = models.ForeignKey(categoriee, on_delete=models.CASCADE ,default=1)      


    class Meta :
        db_table = "passager"

class vool(models.Model):
    num_vol = models.IntegerField(primary_key=True)
    date_vol = models.DateField()
    heure_depart = models.TimeField()

    def calculer_arrivee(self, duree_trajet):
        heure_depart = datetime.combine(datetime.today(), self.heure_depart)
        
        # Convert duree_trajet to float (or int) if it's a string
        if isinstance(duree_trajet, str):
            duree_trajet = float(duree_trajet)
        
        duree = timedelta(hours=duree_trajet)
        heure_arrivee = heure_depart + duree
        
        # Format the time part only
        heure_arrivee_time_only = heure_arrivee.strftime('%H:%M:%S')
        
        return heure_arrivee_time_only
   
    class Meta:
        db_table = "vol"


class trajeet(models.Model):
    id_trajet = models.AutoField(primary_key=True)
    ville_depart = models.CharField(max_length=100)
    ville_arrive = models.CharField(max_length=100)
    prix_trajet_economique = models.FloatField(default=1)
    prix_trajet_affaire = models.FloatField(default=1)
    prix_trajet_1er_classe = models.FloatField(default=1)
    duree_trajet = models.CharField(max_length=100)
    distance = models.FloatField()
    latitude_depart = models.FloatField(null=True)
    longitude_depart = models.FloatField(null=True)
    latitude_arrive = models.FloatField(null=True)
    longitude_arrive = models.FloatField(null=True)
    fk_idavion = models.ForeignKey(aviion, on_delete=models.CASCADE)
    fk_idvol = models.ForeignKey(vool, on_delete=models.CASCADE)
    def save(self, *args, **kwargs):
        if self.latitude_depart and self.longitude_depart and self.latitude_arrive and self.longitude_arrive:
            # Calculate distance using Haversine formula
            distance = self.calculer_distance(
                self.latitude_depart, self.longitude_depart,
                self.latitude_arrive, self.longitude_arrive
            )
            self.distance = distance
            if self.fk_idavion:
                vitesse_avion = 700  # Exemple de vitesse de croisière pour un avion commercial de ligne moyenne
                # Calculer la durée du trajet
                duree_trajet = self.calculer_duree_trajet(distance, vitesse_avion)
                self.duree_trajet = duree_trajet
                heures, reste = divmod(int(duree_trajet * 3600), 3600)
                minutes, secondes = divmod(reste, 60)
                formatted_duree = f"{heures} heures {minutes} minutes {secondes} secondes"
            # Vérification de l'autonomie de l'avion
            if self.fk_idavion:
                if self.fk_idavion.autonomie_avion < distance:
                    raise ValidationError("L'autonomie de l'avion est insuffisante pour ce trajet.")


            # Vérification de la disponibilité de l'avion au moment du départ prévu
            if self.fk_idvol:
                existing_trajets = trajeet.objects.filter(fk_idvol=self.fk_idvol)
                for trajet in existing_trajets:
                    if self.date_vol == trajet.date_vol:
                        raise ValidationError("L'avion est déjà en vol au moment prévu du départ.")
                # Enregistrement de la durée formattée dans le champ
                self.duree_trajet = formatted_duree
                prix_km_economique = self.fk_idavion.prix_km_economique
                self.prix_trajet_economique = round(prix_km_economique * distance, 2)
                prix_km_affaire = self.fk_idavion.prix_km_affaire
                self.prix_trajet_affaire = round(prix_km_affaire * distance, 2)
                prix_km_1er_classe = self.fk_idavion.prix_km_1er_classe
                self.prix_trajet_1er_classe = round(prix_km_1er_classe * distance, 2)
        super().save(*args, **kwargs)


    def calculer_distance(self, lat1, lon1, lat2, lon2):
        rayon_terre = 6371.0
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        d_lat = lat2_rad - lat1_rad
        d_lon = lon2_rad - lon1_rad
        a = math.sin(d_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(d_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = round(rayon_terre * c, 2)
        return distance
   
    def calculer_duree_trajet(self, distance, vitesse_avion):
        # Fonction de calcul de la durée du trajet
        duree_trajet = distance / vitesse_avion
        return duree_trajet


    class Meta :
        db_table = "trajet"




class reservatiion(models.Model):
    num_reservation = models.AutoField(primary_key=True)
    prix_totale = models.FloatField()
    date_reservation = models.DateField()
    heure_reservation = models.TimeField()
    nbr_passager = models.IntegerField()
    fk_nvol = models.ForeignKey(vool, on_delete=models.CASCADE)
    fk_passager = models.ForeignKey(passsager, on_delete=models.CASCADE)


    class Meta :
        db_table = "reservation"

