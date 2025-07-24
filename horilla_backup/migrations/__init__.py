# import atexit
# import sys

# def shutdown_function():
#     if 'makemigratios' in sys.argv or 'migrate' in sys.argv:
#         return
     
#     from horilla_backup.models import GoogleDriveBackup, LocalBackup

#     if GoogleDriveBackup.objects.exists():
#         google_drive_backup = GoogleDriveBackup.objects.first()
#         google_drive_backup.active = False
#         google_drive_backup.save()
#     if LocalBackup.objects.exists():
#         local_backup = LocalBackup.objects.first()
#         local_backup.active = False
#         local_backup.save()


# try:
#     atexit.register(shutdown_function)
# except:
#     pass
