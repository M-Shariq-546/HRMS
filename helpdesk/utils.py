from helpdesk.models import Ticket
from datetime import datetime, timedelta
from horilla.utils.logger import HorillaLogger
from django.db import transaction
from croniter import croniter

logger = HorillaLogger("horilla.helpdesk.utils")

def CreateTicket(ticket):
    logger.info(f"======= Execution of create ticket utility function started =======")
    
    # Calculate next deadline based on frequency
    if ticket.frequency == "custom" and ticket.cron_expression:
        try:
            # Use croniter to calculate next execution time
            cron = croniter(ticket.cron_expression, datetime.now())
            next_execution = cron.get_next(datetime)
            deadline = next_execution.date()
        except Exception as e:
            logger.error(f"Error calculating next execution time: {e}")
            # Fallback to next day if CRON calculation fails
            deadline = datetime.now().date() + timedelta(days=1)
    else:
        # Handle regular frequency-based scheduling
        if ticket.frequency == "daily":
            deadline = datetime.now().date() + timedelta(days=1)
        elif ticket.frequency == "weekly":
            deadline = datetime.now().date() + timedelta(days=7)
        elif ticket.frequency == "monthly":
            deadline = datetime.now().date() + timedelta(days=30)
        else:
            deadline = datetime.now().date() + timedelta(days=1)

    with transaction.atomic():
        new_ticket = Ticket.objects.create(
            title=ticket.title,
            employee_id=ticket.employee_id,
            ticket_type=ticket.ticket_type,
            description=ticket.description,
            priority=ticket.priority,
            assigning_type=ticket.assigning_type,
            raised_on=ticket.raised_on,
            deadline=deadline,
            status="new",
            frequency=ticket.frequency,
            cron_expression=ticket.cron_expression,
            last_executed_at=datetime.now(),
            next_execution_at=deadline,
            created_by=ticket.created_by
        )
        # Copy assigned_to and tags
        new_ticket.assigned_to.set(ticket.assigned_to.all())
        new_ticket.tags.set(ticket.tags.all())
        new_ticket.save()
        logger.info(f"======= Execution of create ticket utility function completed successfully =======")


HOUR_CHOICES = [(i, f"{i:02d}") for i in range(24)]
MINUTE_CHOICES = [(i, f"{i:02d}") for i in range(60)]