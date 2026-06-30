# Archivo: recordatorio_metas.py
import pywhatkit
from datetime import datetime
import sys


def enviar_recordatorio():
    phone_no = "+51984161890"
    now = datetime.now()
    hora = now.hour
    minuto = now.minute

    if hora == 9 and minuto < 45:
        mensaje = (
            "Buenos días Santiago. Me podrías compartir por favor, respecto a este mes vigente, la siguiente información para cada agencia:\n"
            "- la cantidad de colocaciones meta\n"
            "- el monto de colocaciones meta\n"
            "- el número de asesores de crédito"
        )
    elif hora == 12 and minuto <= 45:
        mensaje = (
            "No te olvides por favor de compartir *respecto a este mes vigente*, la siguiente información para cada agencia:\n"
            "- la cantidad de colocaciones meta\n"
            "- el monto de colocaciones meta\n"
            "- el número de asesores de crédito"
        )
    else:
        print("[INFO] No es hora programada para ningún mensaje. Saliendo...")
        sys.exit(0)

    print(f"[INFO] Enviando WhatsApp al {phone_no}...")
    pywhatkit.sendwhatmsg_instantly(
        phone_no=phone_no, message=mensaje, wait_time=15, tab_close=True, close_time=3
    )
    print("[INFO] Mensaje enviado correctamente.")


if __name__ == "__main__":
    enviar_recordatorio()
