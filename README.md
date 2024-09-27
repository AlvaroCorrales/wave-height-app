# wave-height-app
 
 Datos necesarios:
 - Datos de Puertos del Estado:
    - Histórico de altura de oleaje, periodo, dirección de olas, etc. - Descarga única
    - Tiempo real: Hace falta crear un script para scrapear los datos
- Datos AEMET:
    - Histórico de predicciones para el mismo periodo que los datos de oleaje - (Dev API)[https://opendata.aemet.es/centrodedescargas/inicio]?
    - Tiempo real: hace falta scrapear el xml de las predicciones diarias. En teoría no debería ser complicado. 

Arquitectura:
- Feature pipeline
- Training (model updating) pipeline
- Inference pipeline