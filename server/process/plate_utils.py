"""
plate.py

Modulo per la gestione delle targhe

funzione offerte:
- check_authorization
- log_access_to_db
- log_to_csv
- log_plate_result

"""

try:
    import server.config as config
    from server.control.context import get_context
    from server.database import DatabaseManager

except ImportError as e:
    print(f"Errore nel caricamento dei moduli in plate_utils.py: {e}")


def check_authorization(plate_text: str) -> bool:

    db_manager: DatabaseManager = get_context("db_manager")

    if db_manager:

        try:
            # Verifica che la targa sia autorizzata (presente nel DB)
            is_authorized, plate_info = db_manager.is_plate_authorized(plate_text)

            if is_authorized:
                return "authorized", plate_info

            if plate_info and plate_info.get("status") == "expired":
                return "expired", plate_info

            return "not_authorized", None

        except Exception as e:
            # Errore nel database
            if config.VERBOSE:
                print(f"⚠️  Errore database, uso fallback: {e}")
            # Fallback alla lista in memoria
            if plate_text in config.ALL_AUTHORIZED_PLATES:
                return "authorized", {
                    "plate_number": plate_text,
                    "first_name": "N/A",
                    "last_name": "N/A",
                    "role": "N/A",
                    "expiration_date": "N/A",
                }

            return "not_authorized", None

    else:
        # database non inizializzato o non disponibile
        # fallback
        if plate_text in config.ALL_AUTHORIZED_PLATES:
            return "authorized", {
                "plate_number": plate_text,
                "first_name": "N/A",
                "last_name": "N/A",
                "role": "N/A",
                "expiration_date": "N/A",
            }

        return "not_authorized", None


def log_access_to_db(
    plate_text: str, status: str, frame_number: int, confidence: float, track_id: int
):

    db_manager: DatabaseManager = get_context("db_manager")

    if db_manager:
        try:
            db_manager.log_access(
                plate_number=plate_text,
                frame_number=frame_number,
                confidence=confidence,
                status=status,
                track_id=track_id,
            )
        except Exception as e:
            print(f"❌ Errore nel logging al database: {e}")


def log_to_csv(
    plate_text: str, status: str, frame_number: int, confidence: float, track_id: int
):

    with open(config.OUTPUT_CSV, "a") as f:
        f.write(f"{plate_text},{status},{frame_number},{confidence},{track_id}\n")


def log_plate_result(plate_text: str, status: str, confidence: float, plate_info: dict):

    if not config.VERBOSE:
        return

    print(f"\n   📋 TARGA FINALE: {plate_text}")
    print(f"   🎯 Confidenza: {confidence:.2f}")

    if status == "authorized":
        print(f"   ✅ Targa AUTORIZZATA")
        if plate_info:
            print(
                f"Proprietario: {plate_info.get('first_name')} "
                f"{plate_info.get('last_name')} | "
                f"Ruolo: {plate_info.get('role')} | "
                f"Scadenza: {plate_info.get('expiration_date')}"
            )
    elif status == "expired":
        print(f"⚠️  Targa SCADUTA")
        if plate_info:
            print(f"scaduta il: {plate_info.get('expiration_date')}")
    else:
        print(f"❌ Targa NON AUTORIZZATA")
