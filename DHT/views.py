from django.shortcuts import render
import csv
from django.http import JsonResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from django.http import HttpResponse
from reportlab.lib import colors
from django.utils import timezone
import datetime
from .models import Dht11

#fct pour afficher la dernière valeur et le temps écoulé
def table(request):
    derniere_ligne = Dht11.objects.last()
    derniere_date = Dht11.objects.last().dt
    delta_temps = timezone.now() - derniere_date
    difference_minutes = delta_temps.seconds // 60
    temps_ecoule = ' il y a ' + str(difference_minutes) + ' min'
    if difference_minutes > 60:
        temps_ecoule = 'il y ' + str(difference_minutes // 60) + 'h' + str(difference_minutes % 60) + 'min'
    valeurs = {'date': temps_ecoule, 'id': derniere_ligne.id, 'temp': derniere_ligne.temp, 'hum': derniere_ligne.hum}
    return render(request, 'value.html', {'valeurs': valeurs})

#fct pour télécharger les données au format CSV
def download_csv(request):
    model_values = Dht11.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="dht.csv"'
    writer = csv.writer(response)
    writer.writerow(['id', 'temp', 'hum', 'dt'])
    liste = model_values.values_list('id', 'temp', 'hum', 'dt')
    for row in liste:
        writer.writerow(row)
    return response

#fct pour afficher la page d'accueil
def index_view(request):
    return render(request, 'index.html')

#fct pour afficher le graphique
def graphique(request):
    return render(request, 'Chart.html')

#récupérer toutes les valeurs de température et d'humidité sous forme de fichier JSON
def chart_data(request):
    dht = Dht11.objects.all()
    data = {
        'temps': [Dt.dt for Dt in dht],
        'temperature': [Temp.temp for Temp in dht],
        'humidity': [Hum.hum for Hum in dht]
    }
    return JsonResponse(data)

# Récupérer les valeurs de température et d'humidité des dernières 24h JSON
def chart_data_jour(request):
    dht = Dht11.objects.all()
    now = timezone.now()
    last_24_hours = now - timezone.timedelta(hours=24)
    dht = Dht11.objects.filter(dt__range=(last_24_hours, now))
    data = {
        'temps': [Dt.dt for Dt in dht],
        'temperature': [Temp.temp for Temp in dht],
        'humidity': [Hum.hum for Hum in dht]
    }
    return JsonResponse(data)

#récupérer les valeurs de température et d'humidité de la dernière semaine JSON
def chart_data_semaine(request):
    dht = Dht11.objects.all()
    date_debut_semaine = timezone.now().date() - datetime.timedelta(days=7)
    dht = Dht11.objects.filter(dt__gte=date_debut_semaine)
    data = {
        'temps': [Dt.dt for Dt in dht],
        'temperature': [Temp.temp for Temp in dht],
        'humidity': [Hum.hum for Hum in dht]
    }
    return JsonResponse(data)

#récupérer les valeurs de température et d'humidité du dernier mois JSON
def chart_data_mois(request):
    dht = Dht11.objects.all()
    date_debut_semaine = timezone.now().date() - datetime.timedelta(days=30)
    dht = Dht11.objects.filter(dt__gte=date_debut_semaine)
    data = {
        'temps': [Dt.dt for Dt in dht],
        'temperature': [Temp.temp for Temp in dht],
        'humidity': [Hum.hum for Hum in dht]
    }
    return JsonResponse(data)


def download_pdf(request):

    period = request.GET.get('period')

    #définir la plage de dates
    if period == '24h':
        start_date = timezone.now() - datetime.timedelta(hours=24)
    elif period == 'semaine':
        start_date = timezone.now() - datetime.timedelta(weeks=1)
    elif period == 'mois':
        start_date = timezone.now() - datetime.timedelta(days=30)
    else:
        return HttpResponse("Période invalide. Les options valides sont: 24h, semaine, mois", status=400)

    data = Dht11.objects.filter(dt__gte=start_date)

    if not data.exists():
        return HttpResponse("Aucune donnée disponible pour cette période", status=404)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="dht_data_{period}.pdf"'

    buffer = BytesIO()

    p = canvas.Canvas(buffer, pagesize=letter)

    #définir les styles de texte
    title_font = "Helvetica-Bold"
    content_font = "Helvetica"

  
    p.setFillColor(colors.HexColor("#4CAF50"))
    p.rect(0, 740, 600, 40, fill=1) 
    p.setFont(title_font, 18)
    p.setFillColor(colors.white)
    p.drawString(200, 755, "Données du Capteur DHT11")

    #ajouter un sous-titre
    p.setFont(content_font, 12)
    p.setFillColor(colors.white)
    p.drawString(200, 730, f"Période: {period.capitalize()}")

    #ajouter un séparateur (ligne)
    p.setStrokeColor(colors.black)
    p.setLineWidth(1)
    p.line(30, 710, 580, 710)

    #ajouter les en-têtes de colonnes
    p.setFont(title_font, 12)
    p.setFillColor(colors.white)
    col_width = 150
    p.drawString(50, 690, "Date")
    p.drawString(200, 690, "Température (°C)")
    p.drawString(350, 690, "Humidité (%)")

    #fct pour ajouter une nouvelle page seulement si nécessaire
    def add_page_if_needed():
        nonlocal y_position
        if y_position < 50: 
            p.showPage() 
            p.setFont(title_font, 12) 
            p.setFillColor(colors.white)
            p.drawString(50, 690, "Date")
            p.drawString(200, 690, "Température (°C)")
            p.drawString(350, 690, "Humidité (%)")
            y_position = 670

    #ajouter les données dans le PDF
    y_position = 670  # Position de départ pour les données
    p.setFont(content_font, 10)
    p.setFillColor(colors.black)

    for entry in data:
        add_page_if_needed()
        p.drawString(50, y_position, entry.dt.strftime("%Y-%m-%d %H:%M:%S"))
        p.drawString(200, y_position, f"{entry.temp:.2f}")
        p.drawString(350, y_position, f"{entry.hum:.2f}")
        y_position -= 20 

    #ajouter une note de bas de page
    p.setFont(content_font, 8)
    p.setFillColor(colors.gray)
    p.drawString(50, 30, "DHT11 Sensor Data Report - Generated with Django and ReportLab")

    #sauvegarde du PDF dans le buffer
    p.showPage()
    p.save()

    #renvoyer le fichier PDF
    buffer.seek(0)
    response.write(buffer.getvalue())
    buffer.close()
    return response
