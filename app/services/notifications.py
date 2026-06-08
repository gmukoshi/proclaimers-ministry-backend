import os
import requests
from datetime import datetime
from app import db

class NotificationService:
    @staticmethod
    def send_whatsapp(to_number, message, auto_send=False):
        """
        Implementation for WhatsApp Cloud API or Twilio.
        Supports both direct background sending and link generation.
        """
        clean_number = to_number.strip().replace(" ", "").replace("-", "")
        if clean_number.startswith("0"):
            clean_number = "254" + clean_number[1:]
        elif not clean_number.startswith("254") and len(clean_number) == 9:
            clean_number = "254" + clean_number
            
        if auto_send:
            print(f"🚀 [AUTO-SENDER] Initiating background delivery to {clean_number}...")
            print(f"Message: {message}")
            print(f"Status: DELIVERED (Mocked API Call Success)")
            return True, "Background delivery initiated"
            
        print(f"--- WHATSAPP API OUTBOUND ---")
        print(f"To: {clean_number}")
        print(f"Message: {message}")
        print(f"Status: SENT (Mocked Link Generation)")
        print(f"-----------------------------")
        
        return True, f"https://wa.me/{clean_number}?text={requests.utils.quote(message)}"

    @staticmethod
    def notify_proclaimer_of_assignment(assignment, auto_send=False):
        """
        Logic to notify a proclaimer about a new assignment.
        """
        if not assignment.proclaimer or not assignment.proclaimer.phone_number:
            return False, "Proclaimer or phone number missing"
            
        proclaimer_name = assignment.proclaimer.name
        mass_date = assignment.mass.date.strftime("%B %d, %Y")
        mass_time = assignment.mass.time.strftime("%I:%M %p")
        language = assignment.mass.language
        
        # Determine reading position (1st or 2nd)
        mass_assignments = sorted(assignment.mass.assignments, key=lambda a: a.id)
        reading_pos = "1st Reading" if mass_assignments[0].id == assignment.id else "2nd Reading"
        
        message = (
            f"*SMACC Proclaimers Ministry* 📖\n"
            f"--------------------------\n"
            f"Hello *{proclaimer_name}*, you have been assigned as a proclaimer for the upcoming mass:\n\n"
            f"📅 *Date*: {mass_date}\n"
            f"⏰ *Time*: {mass_time} ({language})\n"
            f"📜 *Part*: {reading_pos}\n\n"
            f"Please reply with 'CONFIRM' or 'DECLINE'. Thank you and God bless!"
        )
        
        success, result = NotificationService.send_whatsapp(assignment.proclaimer.phone_number, message, auto_send=auto_send)
        
        if success:
            assignment.notification_sent = True
            assignment.notification_date = datetime.utcnow()
            db.session.commit()
            
        return success, result




